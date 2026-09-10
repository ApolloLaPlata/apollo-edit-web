import httpx
url = "http://163.176.135.59/media/audio_688f83e3506e46e2bb31891c7cc72568.wav"
resp = httpx.get(url)
print(f"Status from Oracle: {resp.status_code}")
print(resp.text[:100])
