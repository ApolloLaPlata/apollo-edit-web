path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/pocket_director.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('transform: translateX(100%);', 'transform: translateX(0%);')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
