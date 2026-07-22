import os

def fix_mojibake(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            text = f.read()
        
        # Reverse the cp1252 decoding
        # Encode back to cp1252 to get the original bytes, then decode as utf-8
        try:
            original_bytes = text.encode('cp1252')
            fixed_text = original_bytes.decode('utf-8')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_text)
            return True
        except Exception as e:
            print(f"Encoding error for {filepath}: {e}")
            return False
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

print(fix_mojibake('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\web_ui\\hub.html'))
