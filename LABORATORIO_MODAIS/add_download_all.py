import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

download_all_fn = '''
        function downloadAllBatchFiles() {
            if (!window.batchGeneratedFiles || window.batchGeneratedFiles.length === 0) return;
            
            if (!confirm(Baixar \ arquivos simultaneamente? (O navegador pode pedir permissão))) return;

            window.batchGeneratedFiles.forEach((url, idx) => {
                setTimeout(() => {
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = url.split('/').pop() || ("Lote_Track_" + (idx + 1) + ".mp3");
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }, idx * 500);
            });
        }
'''

if 'function downloadAllBatchFiles' not in html:
    html = html.replace('window.addEventListener(\\\'DOMContentLoaded\\\', () => { if(typeof toggleMusicUI', download_all_fn + '\n        window.addEventListener(\\\'DOMContentLoaded\\\', () => { if(typeof toggleMusicUI')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
