import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def replace_block():
    target = "img_smart.paste(img, (offset_x, offset_y))"
    replacement = '''img_smart.paste(img, (offset_x, offset_y))
                            
                            try:
                                draw = ImageDraw.Draw(img_smart)
                                label = f"Image {i+1}"
                                draw.rectangle([(10, 10), (100, 35)], fill=(0,0,0))
                                draw.text((20, 15), label, fill=(255,255,255))
                            except Exception as e:
                                print(f"Erro draw: {e}")'''
    return content.replace(target, replacement)

content = replace_block()

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Grid label atualizado no routes_studio.py (FORCED)")
