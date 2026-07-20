import glob
import re

for filename in glob.glob('*.py'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = re.sub(r',\s*activebackground=[\'"].*?[\'"]', '', content)
    content = re.sub(r',\s*activeforeground=[\'"].*?[\'"]', '', content)
    
    if content != original:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {filename}')
