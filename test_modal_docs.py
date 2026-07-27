import urllib.request
url = 'https://modal.com/docs/guide/memory-snapshot'
req = urllib.request.Request(url)
try:
    resp = urllib.request.urlopen(req)
    print(resp.read().decode('utf-8')[:1000])
except Exception as e:
    print('Error:', e)
