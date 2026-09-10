with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "lyrics_lines = [l.strip() for l in lyrics_block.split(" in line:
        lines[i] = "                lyrics_lines = [l.strip() for l in lyrics_block.split(chr(10)) if l.strip() and not l.strip().startswith('[')]\n"

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
