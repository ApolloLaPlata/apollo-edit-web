import os
import glob

def reverse_dotnet_ansi(text):
    b = bytearray()
    for c in text:
        try:
            b.append(c.encode('cp1252')[0])
        except UnicodeEncodeError:
            if ord(c) < 256:
                b.append(ord(c))
            else:
                # If it's a real unicode character that got appended later (like emojis in new code), 
                # we just encode it directly as utf-8 bytes
                b.extend(c.encode('utf-8'))
    
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        # If it fails to decode as utf-8, it means our assumption is wrong, return original
        return text

def fix_all():
    files = glob.glob('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\web_ui\\*.html')
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Only fix if we detect typical mojibake patterns (like Ã£ for ã)
        if 'Ã' in text or '' in text or 'DŸ' in text or 'Â' in text:
            fixed = reverse_dotnet_ansi(text)
            if fixed != text:
                with open(f, 'w', encoding='utf-8-sig') as file:
                    file.write(fixed)
                print(f"Fixed: {os.path.basename(f)}")

fix_all()
