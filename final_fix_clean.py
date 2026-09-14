import re

with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix max limits
html = re.sub(r'(id="musicDurationFixed".*?max=")120(")', r'\g<1>300\g<2>', html)
html = re.sub(r'(id="musicDurationMin".*?max=")120(")', r'\g<1>300\g<2>', html)
html = re.sub(r'(id="musicDurationMax".*?max=")120(")', r'\g<1>300\g<2>', html)

# 2. Rename SA3
html = html.replace('>Stable Audio 3 (Melhor para Efeitos Sonoros)<', '>Stable Audio 3 Medium<')
html = html.replace('>Stable Audio 3 (Curto)<', '>Stable Audio 3 Medium<') # Just in case

# 3. Fix forceDownloadAudio to use iframe
old_func = r'''async function forceDownloadAudio(url, filename) {
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
}'''

new_func = r'''async function forceDownloadAudio(url, filename) {
    let finalUrl = url;
    if (url.includes("apolloedit.com/media")) {
        finalUrl = "https://www.apolloedit.com/api/download?url=" + encodeURIComponent(url);
    }
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = finalUrl;
    document.body.appendChild(iframe);
    setTimeout(() => document.body.removeChild(iframe), 10000);
}'''

if old_func in html:
    html = html.replace(old_func, new_func)
else:
    print("Warning: old_func not found exactly. Manual patch needed.")

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
