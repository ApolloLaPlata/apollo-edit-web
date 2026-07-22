import os
import glob

html_files = glob.glob("*.html")

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False

    if 'background-color: #121212;' in content:
        content = content.replace('background-color: #121212;', '/* background removed for 3d */')
        modified = True
        
    if 'background: #1e1e1e;' in content and 'body {' in content:
        # Some might have 1e1e1e. But let's just stick to what we know is in body.
        pass

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed background in {filepath}")

print("Backgrounds fixed!")
