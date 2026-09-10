import re
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace ANY split with a newline inside it
text = re.sub(r"split\('\r?\n\s+'\);", r"split('\\n');", text)
text = re.sub(r"split\('[\r\n\s]+'\);", r"split('\\n');", text)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
