import sys

with open('web_ui/modal_ai_studio.html', 'rb') as f:
    raw = f.read()

# 1. Decode as UTF-8 (this gives us the string with weird characters like Ã§)
text = raw.decode('utf-8')

# Remove BOM if present
if text.startswith('\ufeff'):
    text = text[1:]

try:
    # 2. Encode to Windows-1252 (this gets back the original UTF-8 bytes)
    # Use 'cp1252' (Windows-1252)
    original_bytes = text.encode('cp1252')
    
    # 3. Decode as UTF-8
    fixed_text = original_bytes.decode('utf-8')
    
    with open('web_ui/modal_ai_studio_restored.html', 'w', encoding='utf-8') as f:
        f.write(fixed_text)
    print("Restore succeeded!")
except Exception as e:
    print("Restore failed:", e)
