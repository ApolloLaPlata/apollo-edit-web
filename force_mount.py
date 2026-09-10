import sys

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
if 'app.mount("/media"' not in text:
    text = re.sub(
        r'(app\.mount\("/ext_apps".*?\n)',
        r'\g<1>\nimport os\nos.makedirs("/home/ubuntu/apollo_edit/media", exist_ok=True)\napp.mount("/media", StaticFiles(directory="/home/ubuntu/apollo_edit/media"), name="media")\n',
        text
    )

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
