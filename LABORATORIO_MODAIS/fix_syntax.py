with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip() == ');' and 'const result = await response.json();' in lines[i+2]:
        skip = True
    
    if not skip:
        new_lines.append(line)
        
    if skip and line.strip() == '}' and 'function copyLogs()' in lines[i+2]:
        skip = False

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
