def fix_mojibake(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            text = f.read()
        
        # Reverse using latin-1 which is 1-to-1
        original_bytes = text.encode('latin-1')
        fixed_text = original_bytes.decode('utf-8')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        return True
    except Exception as e:
        print(f"Error for {filepath}: {e}")
        return False

print(fix_mojibake('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\web_ui\\hub.html'))
