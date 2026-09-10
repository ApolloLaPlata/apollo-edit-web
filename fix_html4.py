import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Ache a div do lyricsContainer
if 'id="lyricsContainer"' in content:
    idx_start = content.find('<div id="lyricsContainer"')
    idx_end = content.find('</div>', idx_start) + 6
    
    new_html = '''<div id="lyricsContainer" style="margin-top: 15px;">
                    <div class="field-label">Letra da Música (Opcional)</div>
                    <textarea id="musicLyrics" placeholder="[Verse 1]\nAcordei cedo pra vencer..."></textarea>
                </div>
                
                <div id="timeContainer" style="margin-top: 15px;">
                    <div class="field-label">Duração (Segundos)</div>
                    <input type="number" id="musicDuration" value="30" min="1" max="180" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                </div>'''
    
    content = content[:idx_start] + new_html + content[idx_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("HTML corrigido com precisão!")
