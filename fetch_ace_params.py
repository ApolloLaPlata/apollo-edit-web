import urllib.request
url = "https://raw.githubusercontent.com/ace-step/ACE-Step-1.5/main/acestep/inference.py"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        import re
        params = re.search(r'class GenerationParams.*?:\n(.*?)\nclass', content, re.DOTALL)
        if params:
            print(params.group(1).encode('ascii', 'ignore').decode('ascii'))
        else:
            print("Not found")
except Exception as e:
    print(e)
