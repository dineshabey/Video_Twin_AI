import yt_dlp
import requests
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from typing import List, Optional
import os

class IngestionService:
    """
    Handles YouTube video transcript extraction and text chunking for RAG pipeline.
    
    Supports cookie-based authentication to bypass YouTube's bot detection
    and implements robust error handling for various video formats.
    """
    
    def __init__(self):
        """Initialize text splitter with optimized chunk parameters for semantic search."""
        # Chunk size balances context window and retrieval precision
        # 200-char overlap ensures semantic continuity across chunks
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract 11-character video ID from various YouTube URL formats.
        
        Supports:
            - youtube.com/watch?v=VIDEO_ID
            - youtu.be/VIDEO_ID
            - youtube.com/embed/VIDEO_ID
            
        Args:
            url: YouTube video URL
            
        Returns:
            11-character video ID or None if invalid format
        """
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def get_transcript(self, url: str) -> str:
        """
        Fetch video transcript using yt-dlp with cookie-based authentication.
        
        Strategy:
            1. Load cookies from environment (production) or filesystem (local)
            2. Use browser-like headers to avoid bot detection
            3. Extract JSON3 subtitle format for best quality
            4. Parse and concatenate all text segments
            
        Args:
            url: YouTube video URL
            
        Returns:
            Full transcript as concatenated string
            
        Raises:
            Exception: If no subtitles found or extraction fails
            
        Note:
            Cookies are required for videos that trigger YouTube's bot detection.
            In Cloud Run, cookies are loaded from YOUTUBE_COOKIES_BASE64 env var.
        """
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True,
            'quiet': False,
            'no_warnings': False,
            # Mimic Chrome browser to avoid bot detection
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'nocheckcertificate': True,
        }

        # Cookie authentication strategy for production deployment
        # Cookies stored as base64-encoded env var to avoid file system dependencies
        youtube_cookies = os.getenv('YOUTUBE_COOKIES_BASE64')
        
        if youtube_cookies:
            try:
                import base64
                # Decode and write to /tmp (only writable location in Cloud Run)
                cookies_content = base64.b64decode(youtube_cookies).decode('utf-8')
                cookie_file = '/tmp/cookies.txt'
                
                with open(cookie_file, 'w') as f:
                    f.write(cookies_content)
                
                ydl_opts['cookiefile'] = cookie_file
                print(f"✓ Loaded cookies from environment variable to {cookie_file}")
            except Exception as e:
                print(f"⚠ Error loading cookies from env: {e}")
        else:
            # Local development fallback - check multiple possible locations
            cookie_paths = [
                'cookies.txt',
                '/workspace/cookies.txt',
                os.path.join(os.path.dirname(__file__), '../../../../cookies.txt'),
            ]
            
            cookie_found = False
            for cookie_path in cookie_paths:
                abs_path = os.path.abspath(cookie_path)
                print(f"Checking for cookies at: {abs_path}")
                if os.path.exists(abs_path):
                    ydl_opts['cookiefile'] = abs_path
                    print(f"✓ Using cookies from: {abs_path}")
                    cookie_found = True
                    break
            
            if not cookie_found:
                print("⚠ WARNING: No cookies found! Set YOUTUBE_COOKIES_BASE64 env var or include cookies.txt")
                print(f"Current working directory: {os.getcwd()}")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Prefer manual subtitles over auto-generated for accuracy
                subtitles = info.get('subtitles') or info.get('automatic_captions')
                if not subtitles:
                    raise Exception("No subtitles found for this video.")

                # Language selection priority: English variants, then first available
                lang = 'en'
                if lang not in subtitles:
                    lang = next((l for l in subtitles if l.startswith('en')), None)
                
                if not lang:
                    lang = list(subtitles.keys())[0]

                subs = subtitles[lang]
                
                # JSON3 format provides best quality with proper timing and formatting
                json3_sub = next((s for s in subs if s['ext'] == 'json3'), None)
                
                if json3_sub:
                    response = requests.get(json3_sub['url'])
                    response.raise_for_status()
                    data = response.json()

                    # Parse JSON3 structure: events -> segs -> utf8 text
                    full_text = []
                    if 'events' in data:
                        for event in data['events']:
                            if 'segs' in event:
                                for seg in event['segs']:
                                    if 'utf8' in seg and seg['utf8'] != '\n':
                                        full_text.append(seg['utf8'])
                    return " ".join(full_text)
                
                raise Exception(f"No suitable subtitle format found for language {lang}")

        except Exception as e:
            raise Exception(f"Failed to fetch transcript: {str(e)}")

    def process_video(self, url: str) -> List[str]:
        """
        Orchestrate full ingestion pipeline: validate URL -> fetch transcript -> chunk text.
        
        Args:
            url: YouTube video URL
            
        Returns:
            List of text chunks ready for embedding
            
        Raises:
            ValueError: If URL format is invalid
            Exception: If transcript extraction fails
        """
        if not self._extract_video_id(url):
             raise ValueError("Invalid YouTube URL")

        transcript = self.get_transcript(url)
        chunks = self.text_splitter.split_text(transcript)
        return chunks
