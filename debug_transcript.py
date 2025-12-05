from youtube_transcript_api import YouTubeTranscriptApi

video_id = "XEzRZ35urlk" # Google I/O 2024 Keynote
try:
    print(f"Attempting to fetch transcript for {video_id}...")
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("Success!")
    print(f"Transcript length: {len(transcript)}")
except Exception as e:
    print(f"Error: {e}")
