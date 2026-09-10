import sys

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1:
text = text.replace('throw new Error(HTTP : );', 'throw new Error(HTTP : );')

# Fix 2: (the split with actual newline)
bad_split = '''const lines = rawText.trim().split('
  ');'''
good_split = '''const lines = rawText.trim().split('\\n');'''
text = text.replace(bad_split, good_split)

# Fix 3:
text = text.replace('throw new Error(Nenhum dado valido retornado: );', 'throw new Error(Nenhum dado valido retornado: );')

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
