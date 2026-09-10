import sys
import re

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace any occurrence of '/api/studio/modal/...' with 'http://163.176.135.59/api/studio/modal/...' inside Javascript fetch calls
text = re.sub(r"(['\"])/api/studio/modal/([^'\"]+)(['\"])", r"\1http://163.176.135.59/api/studio/modal/\2\3", text)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
