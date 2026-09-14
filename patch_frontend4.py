with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

func_code = """
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
"""
html = html.replace('function downloadImage() {', func_code + '\nfunction downloadImage() {')

find_str = '<a href="${fileUrlAbs}" download class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</a>'
replace_str = '<button onclick="forceDownloadAudio(`${fileUrlAbs}`)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</button>'
html = html.replace(find_str, replace_str)

old_batch = """const a = document.createElement("a");
                    a.href = url;
                    a.download = url.split("/").pop(); // extrai o nome final do arquivo
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);"""
html = html.replace(old_batch, 'forceDownloadAudio(url);')

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
