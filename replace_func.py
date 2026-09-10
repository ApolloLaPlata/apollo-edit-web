import re

html_path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\modal_ai_studio.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Primeiro: remover o textarea duplo
# O original tem:
# <div class="field-label">Duração (Segundos)</div>
# <input type="number" id="musicDuration" ...
# </div>
# <textarea id="musicLyrics" placeholder="[Verse 1]\nAcordei cedo pra vencer..."></textarea>
# </div>

double_lyrics_pattern = r'</div>\s*<textarea id="musicLyrics" placeholder="\[Verse 1\]\nAcordei cedo pra vencer\.\.\."></textarea>\s*</div>'
html = re.sub(double_lyrics_pattern, '</div>', html)

# Segundo: substituir TODA a função generateMusicTest
old_func = '''        async function generateMusicTest() {
            const model = document.getElementById('musicModel').value;
            const prompt = document.getElementById('musicPrompt').value;
            const lyrics = document.getElementById('musicLyrics').value;
            const refFile = document.getElementById('musicRefFile').files[0];
            
            if (!prompt.trim()) { alert("Digite o prompt!"); return; }
            
            document.getElementById('musicResultCard').style.display = 'block';
            document.getElementById('musicLoading').style.display = 'block';
            document.getElementById('musicOutput').style.display = 'none';
            document.getElementById('musicError').style.display = 'none';
            
            const formData = new FormData();
            formData.append('model', model);
            formData.append('prompt', prompt);
            if (lyrics) formData.append('lyrics', lyrics);
            if (refFile) formData.append('ref_audio', refFile);
            
            const duration = document.getElementById('musicDuration').value;
            formData.append('duration', duration);

            try {
                const response = await fetch('/api/audio/lab_test', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                document.getElementById('musicLoading').style.display = 'none';
                
                if (data.success) {
                    document.getElementById('musicOutput').style.display = 'block';
                    document.getElementById('musicPlayer').src = data.audio_url;
                } else {
                    document.getElementById('musicError').style.display = 'block';
                    document.getElementById('musicError').textContent = JSON.stringify(data, null, 2);
                }
            } catch (err) {
                document.getElementById('musicLoading').style.display = 'none';
                document.getElementById('musicError').style.display = 'block';
                document.getElementById('musicError').textContent = 'CRASH FETCH: ' + err.message;
            }
        }'''

new_func = '''        async function generateMusicTest() {
            const model = document.getElementById('musicModel').value;
            const prompt = document.getElementById('musicPrompt').value;
            const lyrics = document.getElementById('musicLyrics').value;
            const refFile = document.getElementById('musicRefFile').files[0];
            
            if (!prompt.trim()) { alert("Digite o prompt!"); return; }
            
            document.getElementById('musicResultCard').style.display = 'block';
            document.getElementById('musicLoading').style.display = 'block';
            document.getElementById('musicOutput').style.display = 'none';
            document.getElementById('musicError').style.display = 'none';
            
            const duration = parseInt(document.getElementById('musicDuration').value);
            
            try {
                let refBase64 = null;
                if (refFile) {
                    refBase64 = await fileToBase64(refFile);
                }
                const url = '/api/studio/modal/generate/audio_lab';
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026' },
                    body: JSON.stringify({ prompt, lyrics, model, duration, reference_audio_base64: refBase64 })
                });
                const rawText = await response.text();
                let data;
                try {
                    data = JSON.parse(rawText);
                } catch(e) {
                    throw new Error(rawText.substring(0, 100));
                }
                document.getElementById('musicLoading').style.display = 'none';
                
                if (data.status === 'success') {
                    document.getElementById('musicOutput').style.display = 'block';
                    document.getElementById('musicPlayer').src = data.audio_url;
                } else {
                    document.getElementById('musicError').style.display = 'block';
                    document.getElementById('musicError').textContent = JSON.stringify(data, null, 2);
                }
            } catch (err) {
                document.getElementById('musicLoading').style.display = 'none';
                document.getElementById('musicError').style.display = 'block';
                document.getElementById('musicError').textContent = 'CRASH FETCH: ' + err.message;
            }
        }'''

if old_func in html:
    html = html.replace(old_func, new_func)
    print("Function replaced successfully!")
else:
    print("Function not found, try regex...")
    html = re.sub(re.escape(old_func), new_func, html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
with open('E:\\\\MEUS PROGRAMAS\\\\APOLLO_EDIT_WEB\\\\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
