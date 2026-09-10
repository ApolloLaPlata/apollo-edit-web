import sys

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
match = re.search(r'req = client\.build_request\("POST".*?return StreamingResponse[^)]*\)', text, re.DOTALL)
if match:
    print(match.group(0))
else:
    print("Not found")
