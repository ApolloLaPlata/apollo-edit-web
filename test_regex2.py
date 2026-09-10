
import urllib.request
import re

url = "https://raw.githubusercontent.com/lldacing/ComfyUI_PuLID_Flux_ll/main/pulidflux.py"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    c2 = urllib.request.urlopen(req).read().decode("utf-8")
    matches = re.findall(r".*pulid_forward.*", c2)
    print("Matches for pulid_forward:")
    for m in matches:
        print(m.strip())
except Exception as e:
    print(e)

