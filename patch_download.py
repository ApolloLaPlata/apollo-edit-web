import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

force_download_script = '''
<script>
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
    }).catch(e => {
        alert("Erro ao baixar: " + e.message);
    });
}
</script>
</body>
'''
if 'forceDownloadFile' not in html:
    html = html.replace('</body>', force_download_script)

html = re.sub(r'<a href="\$\{fileUrlAbs\}" download class="btn btn-primary" style="white-space: nowrap; height: fit-content;">.*?</a', 
              r'<button onclick="forceDownloadFile(\\'\\', \\'musica_.mp3\\')" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</button', html)

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
