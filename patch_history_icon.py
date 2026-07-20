filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# Fix history archive icon color to violet
content = content.replace(
    'class="fas fa-archive" style="color: #4f46e5;"',
    'class="fas fa-archive" style="color: #8b5cf6;"'
)

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)
print('Done patching history icon to violet!')
