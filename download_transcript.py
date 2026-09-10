import sys
import subprocess

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "youtube-transcript-api"])
    from youtube_transcript_api import YouTubeTranscriptApi

import json

try:
    transcript = YouTubeTranscriptApi.get_transcript('uEKxxL7T7eA', languages=['pt', 'en'])
    text = " ".join([t['text'] for t in transcript])
    with open("transcript_video.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Sucesso. Tamanho do texto:", len(text))
except Exception as e:
    print("Erro:", str(e))
