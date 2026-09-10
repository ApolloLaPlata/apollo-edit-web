import re
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/vercel.json', 'r') as f:
    text = f.read()

text = re.sub(r'"http://163\.176\.135\.59/media/"', r'"http://163.176.135.59/media/"', text)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/vercel.json', 'w') as f:
    f.write(text)
