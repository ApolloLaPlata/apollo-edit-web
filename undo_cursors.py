import glob

for filename in glob.glob('*.py'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = content.replace("", "")
    content = content.replace("", "")
    content = content.replace("", "")
    content = content.replace("", "")
    
    if content != original:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Removed from {filename}")
