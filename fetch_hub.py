import httpx
resp = httpx.get("https://www.apolloedit.com/hub.html")
for line in resp.text.split("\n"):
    if "modal_ai_studio" in line:
        print(line.strip())
