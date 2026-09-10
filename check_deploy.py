import httpx
url = "https://www.apolloedit.com.br/modal_ai_studio.html"
resp = httpx.get(url)
if "split('\\n');" in resp.text:
    print("DEPLOYED!")
else:
    print("NOT DEPLOYED YET")
