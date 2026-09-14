import httpx
resp = httpx.get("https://www.apolloedit.com/modal_ai_studio.html?v=8")
for line in resp.text.split("\n"):
    if "durationWrapper" in line:
        print(line.strip().encode('ascii', 'ignore').decode('ascii'))
