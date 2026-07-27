import urllib.request
url = 'https://modal.com/docs/guide/memory-snapshot'
req = urllib.request.Request(url)
try:
    resp = urllib.request.urlopen(req)
    content = resp.read().decode('utf-8')
    if "H100" in content:
        print("H100 mentioned!")
    else:
        print("H100 not mentioned.")
except Exception as e:
    print('Error:', e)
