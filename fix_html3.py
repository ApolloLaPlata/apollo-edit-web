import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Modificar o HTML da Letra e adicionar o Controle de Tempo
if 'id="lyricsContainer"' in content:
    # Substituir o bloco do lyrics
    old_lyrics = '''<div id="lyricsContainer" style="display:none; margin-top: 15px;">
                    <div class="field-label">Letra da Música (Obrigatório para ACE-Step)</div>
                    <textarea id="musicLyrics" placeholder="[Verse 1]\\nAcordei cedo pra vencer..."></textarea>
                </div>'''
    
    new_lyrics = '''<div id="lyricsContainer" style="margin-top: 15px;">
                    <div class="field-label">Letra da Música (ACE-Step / Outros)</div>
                    <textarea id="musicLyrics" placeholder="[Verse 1]\nAcordei cedo pra vencer..."></textarea>
                </div>
                
                <div id="timeContainer" style="margin-top: 15px;">
                    <div class="field-label">Duração (Segundos)</div>
                    <input type="number" id="musicDuration" value="30" min="1" max="180" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">
                </div>'''
    
    content = content.replace(old_lyrics, new_lyrics)

# 2. Remover a lógica que esconde o lyricsContainer do JS
if "lyricsContainer.style.display = 'none';" in content:
    content = content.replace("lyricsContainer.style.display = 'none';", "lyricsContainer.style.display = 'block';")

# 3. Adicionar o parametro de duração no fetch (JS)
if "formData.append('ref_audio', refFile);" in content and "musicDuration" not in content:
    # Append the duration parameter to formData
    js_form_append = '''            if (refFile) formData.append('ref_audio', refFile);
            
            const duration = document.getElementById('musicDuration').value;
            formData.append('duration', duration);'''
    content = content.replace("            if (refFile) formData.append('ref_audio', refFile);", js_form_append)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Atualizado HTML e JS com Letra Sempre Visível e Controle de Tempo.")
