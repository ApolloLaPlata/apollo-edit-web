import re
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the specific malformed split
text = re.sub(r"split\('\n\s+'\);", r"split('\n');", text)
text = text.replace("split('\n  ');", "split('\\n');")

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
