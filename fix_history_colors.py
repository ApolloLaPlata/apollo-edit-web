import re

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias_core.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# Replace iconColor for long videos
content = content.replace("script.type === 'shorts' ? '#ea580c' : '#4f46e5'", "script.type === 'shorts' ? '#ea580c' : '#8b5cf6'")
# Replace iconBg for long videos
content = content.replace("script.type === 'shorts' ? '#ffedd5' : '#e0e7ff'", "script.type === 'shorts' ? '#ffedd5' : '#ede9fe'")
# Replace btnPlay styles
content = content.replace("background: #e0e7ff; color: #4338ca; border: 1px solid #c7d2fe;", "background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe;")

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)
print('Fixed history colors in noticias_core.js!')
