import glob
import re

for filename in glob.glob('*.py'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content

    # Find CTkButton and add cursor="hand2" if not already present
    # Using regex to insert into CTkButton instantiation if it doesn't exist
    
    # We can just do a regex replace on CTkButton(
    def add_cursor(match):
        inner = match.group(1)
        if 'cursor=' not in inner:
            return f"CTkButton({inner}"
        return match.group(0)

    content = re.sub(r'CTkButton\(([^)]+)', add_cursor, content)

    if content != original:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Added hand2 cursor to buttons in {filename}")
