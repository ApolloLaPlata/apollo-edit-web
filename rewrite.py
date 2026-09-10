import re

html_path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\modal_ai_studio.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix double textarea
html = re.sub(
    r'<div id="timeContainer".*?</div>\s*<textarea id="musicLyrics" placeholder="\[Verse 1\]\s*Acordei cedo pra vencer\.\.\."></textarea>\s*</div>',
    r'<div id="timeContainer" style="margin-top: 15px;">\n                    <div class="field-label">Duração (Segundos)</div>\n                    <input type="number" id="musicDuration" value="30" min="1" max="180" style="width:100%; background:#0d0d15; border:1px solid var(--border); color:var(--text); padding:8px; border-radius:8px;">\n                </div>\n',
    html,
    flags=re.DOTALL
)

# 2. Fix generateMusicTest
js_old = '''        async function generateMusicTest() {
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
                const url = '/api/studio/modal/generate/audio_lab';
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026' },
                    body: JSON.stringify({ prompt, lyrics, model, duration })
                });
                const data = await response.json();
                document.getElementById('musicLoading').style.display = 'none';
                
                if (data.success || data.status === 'success') {
                    document.getElementById('musicOutput').style.display = 'block';
                    if (data.audio_base64) {
                        document.getElementById('musicPlayer').src = 'data:audio/wav;base64,' + data.audio_base64;
                    } else if (data.audio_url) {
                        document.getElementById('musicPlayer').src = data.audio_url;
                    }
                } else {
                    document.getElementById('musicError').style.display = 'block';
                    document.getElementById('musicError').innerHTML = <code>Erro: \</code>;
                }
            } catch (err) {
                document.getElementById('musicLoading').style.display = 'none';
                document.getElementById('musicError').style.display = 'block';
                document.getElementById('musicError').innerHTML = <code>CRASH FETCH: \</code>;
            }
        }'''

js_new = '''        async function generateMusicTest() {
            const model = document.getElementById('musicModel').value;
            const prompt = document.getElementById('musicPrompt').value;
            const lyrics = document.getElementById('musicLyrics') ? document.getElementById('musicLyrics').value : '';
            const refFile = document.getElementById('musicRefFile').files[0];
            const duration = document.getElementById('musicDuration').value;
            
            if (!prompt.trim()) { alert("Digite o prompt!"); return; }
            
            document.getElementById('musicResultCard').style.display = 'block';
            document.getElementById('musicLoading').style.display = 'block';
            document.getElementById('musicOutput').style.display = 'none';
            document.getElementById('musicError').style.display = 'none';
            
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
                
                if (data.success || data.status === 'success') {
                    document.getElementById('musicOutput').style.display = 'block';
                    if (data.audio_base64) {
                        document.getElementById('musicPlayer').src = 'data:audio/wav;base64,' + data.audio_base64;
                    } else if (data.audio_url) {
                        document.getElementById('musicPlayer').src = data.audio_url;
                    }
                } else {
                    document.getElementById('musicError').style.display = 'block';
                    document.getElementById('musicError').innerHTML = <code>Erro: \</code>;
                }
            } catch (err) {
                document.getElementById('musicLoading').style.display = 'none';
                document.getElementById('musicError').style.display = 'block';
                document.getElementById('musicError').innerHTML = <code>CRASH FETCH: \</code>;
            }
        }'''

html = html.replace(js_old, js_new)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
with open('E:\\\\MEUS PROGRAMAS\\\\APOLLO_EDIT_WEB\\\\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
