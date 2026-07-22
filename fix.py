import sys
content = open('transfer_hud.js', 'r', encoding='utf-8').read()
content = content.replace('\\`', '`')
open('transfer_hud.js', 'w', encoding='utf-8').write(content)
