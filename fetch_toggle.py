import httpx
resp = httpx.get("https://www.apolloedit.com/modal_ai_studio.html?v=8")
lines = resp.text.split("\n")
start = -1
for i, line in enumerate(lines):
    if "function toggleMusicUI" in line:
        start = i
        break
if start != -1:
    for i in range(start, start+30):
        print(lines[i].rstrip())
