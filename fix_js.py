import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

js_logic = '''
        function updateMusicUI() {
            const model = document.getElementById('musicModel').value;
            const modelText = document.getElementById('musicModel').options[document.getElementById('musicModel').selectedIndex].text;
            document.getElementById('musicBadgeModel').textContent = modelText;
            
            const lyricsContainer = document.getElementById('lyricsContainer');
            const refAudioContainer = document.getElementById('refAudioContainer');
            
            if (model === 'ace-step') {
                lyricsContainer.style.display = 'block';
                refAudioContainer.style.display = 'block';
            } else if (model === 'minimax') {
                lyricsContainer.style.display = 'none';
                refAudioContainer.style.display = 'none';
            } else {
                lyricsContainer.style.display = 'none';
                refAudioContainer.style.display = 'block';
            }
        }

        async function generateMusicTest() {
            const model = document.getElementById('musicModel').value;
            const prompt = document.getElementById('musicPrompt').value;
            const lyrics = document.getElementById('musicLyrics').value;
            const refFile = document.getElementById('musicRefFile').files[0];
            
            if (!prompt.trim()) {
                alert("Por favor, digite um prompt para gerar o áudio.");
                return;
            }
            if (model === 'ace-step' && !lyrics.trim()) {
                alert("O modelo ACE-Step exige uma letra (Lyrics).");
                return;
            }

            document.getElementById('musicResultCard').style.display = 'block';
            document.getElementById('musicLoading').style.display = 'block';
            document.getElementById('musicOutput').style.display = 'none';
            document.getElementById('musicError').style.display = 'none';
            
            const formData = new FormData();
            formData.append('model', model);
            formData.append('prompt', prompt);
            if (lyrics) formData.append('lyrics', lyrics);
            if (refFile) formData.append('ref_audio', refFile);

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
                    document.getElementById('musicError').textContent = data.error || 'Erro desconhecido na geração.';
                }
            } catch (err) {
                document.getElementById('musicLoading').style.display = 'none';
                document.getElementById('musicError').style.display = 'block';
                document.getElementById('musicError').textContent = 'Erro de rede: ' + err.message;
            }
        }
'''

if "updateMusicUI()" not in content:
    content = content.replace("function showTab(name) {", js_logic + "\n        function showTab(name) {")

# Update tabs array inside showTab
if "['img','vid','audio','music']" not in content:
    content = content.replace("['img','vid','audio']", "['img','vid','audio','music']")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("JS inserido com sucesso!")
