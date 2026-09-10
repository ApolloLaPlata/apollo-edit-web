import subprocess
import sys

try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])

subprocess.run([sys.executable, "-m", "yt_dlp", "--write-auto-sub", "--sub-lang", "pt", "--skip-download", "https://www.youtube.com/watch?v=uEKxxL7T7eA"])
