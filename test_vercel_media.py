import httpx
url = "https://www.apolloedit.com.br/media/audio_688f83e3506e46e2bb31891c7cc72568.wav"
resp = httpx.get(url)
print(f"Status from Vercel: {resp.status_code}")
