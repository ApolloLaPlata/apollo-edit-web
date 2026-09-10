import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'lyrics_block\.split\(\'[\\r\\n]+\'\)', r"lyrics_block.split('\\n')", code)
code = re.sub(r'lyrics_block\.split\(\'\\\n\'\)', r"lyrics_block.split('\\n')", code)
code = re.sub(r'lyrics_block\.split\(\'\\[\r\n]*\'\)', r"lyrics_block.split('\\n')", code)

# Just manually replace the line if regex fails
lines = code.split('\n')
for i, line in enumerate(lines):
    if 'lyrics_lines = [l.strip() for l in lyrics_block.split(' in line:
        lines[i] = "                lyrics_lines = [l.strip() for l in lyrics_block.split('\\n') if l.strip() and not l.strip().startswith('[')]"
        if i + 1 < len(lines) and lines[i+1].strip() == "') if l.strip() and not l.strip().startswith('[')]":
            lines[i+1] = ""

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
