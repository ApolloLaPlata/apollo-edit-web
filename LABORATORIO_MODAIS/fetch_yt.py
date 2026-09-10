import urllib.request
import re

urls = ["https://www.youtube.com/watch?v=mV5-kuUFsAo", "https://www.youtube.com/watch?v=VXKMz6lIgX4"]
for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        title = re.search(r'<title>(.*?)</title>', html)
        if title:
            print(f"{url} -> {title.group(1).replace(' - YouTube', '')}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
