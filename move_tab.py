import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Primeiro, encontrar a div tab-music e extraí-la.
if '<!-- TAB: AUDIO LAB (MUSIC & SFX) -->' in content:
    start_idx = content.find('<!-- TAB: AUDIO LAB (MUSIC & SFX) -->')
    end_idx = content.find('<script>', start_idx)
    
    # Extrai o HTML
    tab_music_html = content[start_idx:end_idx].strip()
    
    # Remove do local original
    content = content[:start_idx] + content[end_idx:]
    
    # Agora insere antes do </aside>
    if '</aside>' in content:
        content = content.replace('</aside>', tab_music_html + '\n\n    </aside>')
        
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Movido tab-music para dentro do painel lateral!")
