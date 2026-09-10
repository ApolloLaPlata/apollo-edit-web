with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'preview.innerHTML =' in line:
        lines[i+1] = lines[i+1].replace('<div', '<div', 1)
    if '</div>' in line and ';' in lines[i+1] and 'preview.innerHTML' in lines[i-11]:
        lines[i] = lines[i].replace('</div>', '</div>')
        
    if 'const trackHtml =' in line:
        lines[i+1] = lines[i+1].replace('<div', '<div', 1)
    if '</a>' in line and '</div>' in lines[i+1] and ';' in lines[i+2] and 'const trackHtml =' in lines[i-10]:
        lines[i+1] = lines[i+1].replace('</div>', '</div>')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)
