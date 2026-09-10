import re
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Change video and image generation to use relative Vercel paths
text = re.sub(r'const url\s*=\s*"http://163\.176\.135\.59/api/studio/modal/generate_video";', r'const url = "/api/studio/modal/generate_video";', text)
text = re.sub(r'const url\s*=\s*"http://163\.176\.135\.59/api/studio/modal/generate";', r'const url = "/api/studio/modal/generate";', text)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
