import yt_dlp
import requests
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from typing import List, Optional
import os

class IngestionService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extracts the video ID from a YouTube URL.
        """
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    def get_transcript(self, url: str) -> str:
        """
        Fetches the transcript for a given video URL using yt-dlp with cookies.
        """
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True,
            'quiet': False,
            'no_warnings': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'nocheckcertificate': True,
        }

        # PRODUCTION SOLUTION: Load cookies from environment variable
        # This allows updating cookies without redeployment
        youtube_cookies = os.getenv('YOUTUBE_COOKIES_BASE64')
        
        if youtube_cookies:
            try:
                import base64
                # Decode base64 cookies and write to /tmp (writable in Cloud Run)
                cookies_content = base64.b64decode(youtube_cookies).decode('utf-8')
                cookie_file = '/tmp/cookies.txt'
                
                with open(cookie_file, 'w') as f:
                    f.write(cookies_content)
                
                ydl_opts['cookiefile'] = cookie_file
                print(f"✓ Loaded cookies from environment variable to {cookie_file}")
            except Exception as e:
                print(f"⚠ Error loading cookies from env: {e}")
        else:
            # Fallback: try to find cookies.txt in various locations
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
                
                # Get subtitles (manual or auto)
                subtitles = info.get('subtitles') or info.get('automatic_captions')
                if not subtitles:
                    raise Exception("No subtitles found for this video.")

                # Prefer English
                lang = 'en'
                if lang not in subtitles:
                    # Try to find any english variant
                    lang = next((l for l in subtitles if l.startswith('en')), None)
                
                if not lang:
                    # Fallback to first available
                    lang = list(subtitles.keys())[0]

                subs = subtitles[lang]
                json3_sub = next((s for s in subs if s['ext'] == 'json3'), None)
                
                if json3_sub:
                    response = requests.get(json3_sub['url'])
                    response.raise_for_status()
                    data = response.json()

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
        Orchestrates the ingestion process.
        """
        if not self._extract_video_id(url):
             raise ValueError("Invalid YouTube URL")

        transcript = self.get_transcript(url)
        chunks = self.text_splitter.split_text(transcript)
        return chunks
