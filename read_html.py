import sys

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'async function generateMusicTest()' in line:
        out = ''.join(lines[i:i+70])
        print(out.encode('ascii', 'ignore').decode('ascii'))
        break
