import re

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

def replacer(match):
    block = match.group(0)
    # Replace #059669 (green-600) to #8b5cf6 (violet-500)
    block = block.replace('#059669', '#8b5cf6')
    # Replace #d1fae5 (green-100) to #ede9fe (violet-100)
    block = block.replace('#d1fae5', '#ede9fe')
    # Replace #047857 (green-700) to #6d28d9 (violet-700)
    block = block.replace('#047857', '#6d28d9')
    return block

content = re.sub(r'<div id="tab-monitor" class="tab-pane">.*?(?=<div id="tab-)', replacer, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed monitor colors!')
