import sys

with open('web_ui/modal_ai_studio.html', 'rb') as f:
    raw = f.read()

text = raw.decode('utf-8')
if text.startswith('\ufeff'):
    text = text[1:]

try:
    # Try to fix double encoding
    fixed = text.encode('windows-1252').decode('utf-8')
    with open('web_ui/modal_ai_studio_fixed.html', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print("Fix succeeded!")
except Exception as e:
    print("Fix failed:", e)
