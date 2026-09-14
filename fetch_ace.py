import urllib.request
import json
url = "https://raw.githubusercontent.com/ace-step/ACE-Step-1.5/main/acestep/inference.py"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        print(content[:3000])
except Exception as e:
    print(e)
