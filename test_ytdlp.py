import yt_dlp

url = "https://www.youtube.com/watch?v=9gGnTQTYNaE"

ydl_opts = {
    'writesubtitles': True,
    'writeautomaticsub': True,
    'skip_download': True,
    'quiet': False,
    # Simulate a real browser
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'referer': 'https://www.youtube.com/',
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("Success!")
        print(f"Subtitles: {list(info.get('subtitles', {}).keys())}")
        print(f"Auto-subs: {list(info.get('automatic_captions', {}).keys())}")
except Exception as e:
    print(f"Error: {e}")
