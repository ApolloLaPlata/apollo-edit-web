import re

html_path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\modal_ai_studio.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the JSON parsing crash
old_try = '''            try {
                const url = '/api/studio/modal/generate/audio_lab';
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026' },
                    body: JSON.stringify({ prompt, lyrics, model, duration })
                });
                const data = await response.json();'''

new_try = '''            try {
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
                }'''

html = html.replace(old_try.replace('\\n', '\\r\\n'), new_try)
html = html.replace(old_try, new_try)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
with open('E:\\\\MEUS PROGRAMAS\\\\APOLLO_EDIT_WEB\\\\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
