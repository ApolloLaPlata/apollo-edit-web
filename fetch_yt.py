import sys
import os

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    os.system("pip install youtube-transcript-api")
    from youtube_transcript_api import YouTubeTranscriptApi

try:
    transcript = YouTubeTranscriptApi.get_transcript('4_vnvJqUwN8', languages=['pt', 'en'])
    text = " ".join([x['text'] for x in transcript])
    print(text)
except Exception as e:
    print("Error:", e)
    
    # fallback to yt-dlp to get title/description
    os.system("pip install yt-dlp")
    os.system("yt-dlp --print \"%(title)s - %(description)s\" https://www.youtube.com/watch?v=4_vnvJqUwN8")
