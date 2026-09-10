import urllib.request
from bs4 import BeautifulSoup
url = 'https://modal.com/docs/guide/memory-snapshot'
req = urllib.request.Request(url)
try:
    resp = urllib.request.urlopen(req)
    soup = BeautifulSoup(resp.read(), 'html.parser')
    print(soup.get_text()[:3000])
except Exception as e:
    print('Error:', e)
