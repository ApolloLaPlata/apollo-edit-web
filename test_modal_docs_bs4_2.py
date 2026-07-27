import urllib.request
from bs4 import BeautifulSoup
url = 'https://modal.com/docs/guide/memory-snapshot'
req = urllib.request.Request(url)
try:
    resp = urllib.request.urlopen(req)
    soup = BeautifulSoup(resp.read(), 'html.parser')
    text = soup.get_text()
    import re
    if "245" in text:
        print("FOUND 245 in docs:", text[text.find("245")-100:text.find("245")+100])
    if "H100" in text:
        print("FOUND H100 in docs:", text[text.find("H100")-100:text.find("H100")+100])
    print(text[3000:5000])
except Exception as e:
    print('Error:', e)
