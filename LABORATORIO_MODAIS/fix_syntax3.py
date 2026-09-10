with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the literal newline inside the split string
import re
code = re.sub(r'lyrics_block\.split\(\'' + '\n' + r'\'\)', r"lyrics_block.split('\\n')", code)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
