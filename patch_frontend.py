import re

with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add the forceDownloadAudio function
if 'function forceDownloadAudio' not in html:
    func_code = '''
async function forceDownloadAudio(url, filename) {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = filename || url.split('/').pop();
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
    } catch (e) {
        window.open(url, '_blank');
    }
}
'''
    html = html.replace('function downloadImage() {', func_code + '\nfunction downloadImage() {')

# Fix batch download all
batch_old = '''const a = document.createElement("a");
                    a.href = url;
                    a.download = url.split("/").pop(); // extrai o nome final do arquivo
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);'''
batch_new = '''forceDownloadAudio(url);'''
html = html.replace(batch_old, batch_new)

# Fix individual download button
btn_old = '''<a href="" download class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</a>'''
btn_new = '''<button onclick="forceDownloadAudio('')" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</button>'''
html = html.replace(btn_old, btn_new)

# fallback if there are weird encoding issues in my exact string match:
import re
html = re.sub(r'<a href="\$\{fileUrlAbs\}" download class="btn btn-primary"[^>]*>.*?Baixar.*?</a>', 
              r'<button onclick="forceDownloadAudio(\'\')" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</button>', 
              html, flags=re.DOTALL)

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
