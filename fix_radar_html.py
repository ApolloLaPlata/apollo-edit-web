import re

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

def replacer(match):
    block = match.group(0)
    # Replace #dc2626 (red) to #8b5cf6 (violet)
    block = block.replace('#dc2626', '#8b5cf6')
    # Replace #fee2e2 (red bg) to #ede9fe (violet bg)
    block = block.replace('#fee2e2', '#ede9fe')
    # Replace #ef4444 to #8b5cf6
    block = block.replace('#ef4444', '#8b5cf6')
    return block

content = re.sub(r'<div id="tab-radar" class="tab-pane">.*?(?=<div id="tab-)', replacer, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
