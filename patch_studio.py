import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix the payload sent to backend
old_payload = 'body: JSON.stringify({ prompt: p, engine, duration: finalDuration })'
new_payload = 'body: JSON.stringify({ prompt: p, engine, lyrics: lyrics[i] || "", duration: finalDuration })'
html = html.replace(old_payload, new_payload)

# 2. Fix fileUrlAbs bug
old_file_url = 'const fileUrlAbs = result.file_url.startsWith(\\'http\\') ? result.file_url : ${result.file_url};'
new_file_url = 'const fileUrlAbs = result.file_url;'
html = html.replace(old_file_url, new_file_url)

# 3. Add forceDownload script right before </body>
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
html = html.replace('</body>', force_download_script)

# 4. Replace the download button in trackHtml
html = re.sub(r'<a href="\$\{fileUrlAbs\}" download class="btn btn-primary".*?Baixar</a>', 
              r'<button onclick="forceDownloadFile(\\\'\\\', \\\'musica_.mp3\\\')" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">\u2B07\uFE0F Baixar</button>', html)

with open('web_ui/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("modal_ai_studio.html patched!")
