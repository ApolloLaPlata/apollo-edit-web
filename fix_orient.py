import re
import glob

for filename in glob.glob('*.py'):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'CTkScrollbar' in content:
        content = re.sub(r'orient=([\'"])vertical\1', r'orientation=\1vertical\1', content)
        content = re.sub(r'orient=([\'"])horizontal\1', r'orientation=\1horizontal\1', content)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
print("orient replaced by orientation")
