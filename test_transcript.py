from youtube_transcript_api import YouTubeTranscriptApi

video_id = "9gGnTQTYNaE"

try:
    print(f"Testing video: {video_id}")
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
    # Try to get the manual english one
    try:
        transcript = transcript_list.find_transcript(['en'])
        print(f"Found transcript: {transcript.language_code}")
        print("Fetching...")
        data = transcript.fetch()
        print("Success!")
        print(str(data)[:100])
    except Exception as e:
        print(f"Failed to fetch specific transcript: {e}")
        
except Exception as e:
    print(f"Error: {e}")
