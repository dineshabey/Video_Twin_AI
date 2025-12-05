from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional
import re

class YouTubeService:
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extracts the video ID from a YouTube URL.
        """
        # Regex for extracting YouTube Video ID
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def get_transcript(video_id: str) -> str:
        """
        Fetches the transcript for a given video ID.
        """
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            # Combine all text parts into a single string
            full_text = " ".join([item['text'] for item in transcript_list])
            return full_text
        except Exception as e:
            raise Exception(f"Failed to fetch transcript: {str(e)}")
