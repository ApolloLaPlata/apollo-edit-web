import re

with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix max limits
html = re.sub(r'id="musicDurationFixed"(.*?max=")120(")', r'id="musicDurationFixed"\g<1>300\g<2>', html)
html = re.sub(r'id="musicDurationMin"(.*?max=")120(")', r'id="musicDurationMin"\g<1>300\g<2>', html)
html = re.sub(r'id="musicDurationMax"(.*?max=")120(")', r'id="musicDurationMax"\g<1>300\g<2>', html)

# Rename SA3
html = html.replace('>Stable Audio 3 (Melhor para Efeitos Sonoros)<', '>Stable Audio 3 Medium<')
html = html.replace('>Stable Audio 3 (Curto)<', '>Stable Audio 3 Medium<')

# Fix forceDownloadAudio manually with basic split/replace to avoid regex loops
start_idx = html.find('async function forceDownloadAudio(url, filename)')
if start_idx != -1:
    end_idx = html.find('}', html.find('window.open(url, \'_blank\');', start_idx)) + 1
    old_func = html[start_idx:end_idx]
    new_func = '''async function forceDownloadAudio(url, filename) {
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
    html = html.replace(old_func, new_func)

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
