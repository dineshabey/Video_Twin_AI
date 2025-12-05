import yt_dlp
import json

url = "https://www.youtube.com/watch?v=XEzRZ35urlk"

ydl_opts = {
    'writesubtitles': True,
    'writeautomaticsub': True,
    'skip_download': True,
    'quiet': True,
    'no_warnings': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        subtitles = info.get('subtitles') or info.get('automatic_captions')
        
        if subtitles:
            # Prefer English
            lang = 'en'
            if lang not in subtitles and 'en-orig' in subtitles:
                lang = 'en-orig'
            
            if lang in subtitles:
                subs = subtitles[lang]
                # Look for json3 format
                json3_sub = next((s for s in subs if s['ext'] == 'json3'), None)
                if json3_sub:
                    print(f"JSON3 URL: {json3_sub['url']}")
                else:
                    print("No JSON3 subtitle found.")
            else:
                print("No English subtitles found.")
        else:
            print("No subtitles found.")
except Exception as e:
    print(f"Error: {e}")
