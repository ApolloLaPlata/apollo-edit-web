# coding: utf-8
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = '''img_smart = ImageOps.fit(img, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.2))
                            grid.paste(img_smart, box=(i % cols * w, i // cols * h))'''

new_block = '''# Substituindo Smart Crop por "Pad Seguro" (Sem perda de dados)
                            img.thumbnail((w, h), Image.Resampling.LANCZOS)
                            img_smart = Image.new("RGB", (w, h), (255, 255, 255))
                            offset_x = (w - img.width) // 2
                            offset_y = (h - img.height) // 2
                            img_smart.paste(img, (offset_x, offset_y))
                            
                            grid.paste(img_smart, box=(i % cols * w, i // cols * h))'''

content = content.replace(old_block, new_block)
content = content.replace('[SMART CROP]', '[SMART GRID]')
content = content.replace('com Smart Cropping (centering)', 'com Smart Padding (Preservacao 100%)')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Crop fixado!")
