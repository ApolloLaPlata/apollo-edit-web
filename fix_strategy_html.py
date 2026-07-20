import sys
import re

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add strategy_logic.js if missing
if 'strategy_logic.js' not in content:
    content = content.replace(
        '<script src="scripts_logic.js"></script>',
        '<script src="scripts_logic.js"></script>\n    <script src="strategy_logic.js"></script>'
    )

def replacer(match):
    block = match.group(0)
    block = block.replace('#4f46e5', '#8b5cf6') # indigo-600 -> violet-500
    block = block.replace('#312e81', '#4c1d95') # indigo-900 -> violet-900
    block = block.replace('#3730a3', '#5b21b6') # indigo-800 -> violet-800
    block = block.replace('#c7d2fe', '#ddd6fe') # indigo-200 -> violet-200
    return block

content = re.sub(r'<div id="tab-strategy" class="tab-pane active">.*?(?=<div id="tab-)', replacer, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
