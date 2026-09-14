import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

func = """
function forceDownloadFile(url, filename) {
    fetch(url)
    .then(r => r.blob())
    .then(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(a.href);
    }).catch(e => {
        alert('Erro ao baixar: ' + e.message);
    });
}
"""
if 'function forceDownloadFile' not in html:
    html = html.replace('function b64toBlob(b64, mime) {', func + '\n        function b64toBlob(b64, mime) {')

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
