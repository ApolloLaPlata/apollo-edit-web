def fix_mojibake(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            text = f.read()
        
        # Reverse .NET's cp1252 decoding fallback
        byte_array = bytearray()
        for c in text:
            try:
                b = c.encode('cp1252')
                byte_array.extend(b)
            except UnicodeEncodeError:
                # Character couldn't be encoded by cp1252
                # This means it was an undefined byte in cp1252, which .NET mapped literally to U+00XX
                if ord(c) < 256:
                    byte_array.append(ord(c))
                else:
                    # If it's over 256 and not in cp1252, this is a real Unicode character that was NOT in the original file 
                    # before corruption? Or maybe it was already UTF-8 and survived?
                    # Let's just encode it as UTF-8 directly into the byte array, as a safe fallback
                    byte_array.extend(c.encode('utf-8'))
        
        fixed_text = byte_array.decode('utf-8')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        return True
    except Exception as e:
        print(f"Error for {filepath}: {e}")
        return False

print(fix_mojibake('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\web_ui\\hub.html'))
