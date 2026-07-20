filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# Fix settings cog icon color to violet
content = content.replace(
    'class="fas fa-cog" style="color: #4f46e5;"',
    'class="fas fa-cog" style="color: #8b5cf6;"'
)

# Fix "Modelos de IA" robot icon to violet
content = content.replace(
    'class="fas fa-robot" style="color: #2563eb;"',
    'class="fas fa-robot" style="color: #8b5cf6;"'
)

# Fix Preferencias shield icon to violet
content = content.replace(
    'class="fas fa-shield-alt" style="color: #4b5563;"',
    'class="fas fa-shield-alt" style="color: #8b5cf6;"'
)

# Fix Integracoes Redes Sociais globe icon to violet
content = content.replace(
    'class="fas fa-globe" style="color: #10b981;"',
    'class="fas fa-globe" style="color: #8b5cf6;"'
)

# Fix save button color in settings
content = content.replace(
    '"news-btn primary" onclick="saveSettings()"',
    '"news-btn primary" onclick="saveSettings()" style="background: #8b5cf6; border-color: #8b5cf6;"'
)

# Fix Testar Chave button colors (indigo to violet)
content = content.replace(
    'color: #4f46e5; background: #eef2ff;',
    'color: #8b5cf6; background: #ede9fe;'
)

# Fix setting_autoSave checkbox accent to violet
content = content.replace(
    'accent-color: #4f46e5;',
    'accent-color: #8b5cf6;'
)

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)
print('Done patching noticias.html settings colors!')
