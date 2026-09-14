with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

old_func = r'''async function forceDownloadAudio\(url, filename\) \{
    try \{
        const response = await fetch\(url\);
        const blob = await response\.blob\(\);
        const blobUrl = URL\.createObjectURL\(blob\);
        const a = document\.createElement\("a"\);
        a\.href = blobUrl;
        a\.download = filename || url\.split\('/'\)\.pop\(\);
        document\.body\.appendChild\(a\);
        a\.click\(\);
        document\.body\.removeChild\(a\);
        setTimeout\(\(\) => URL\.revokeObjectURL\(blobUrl\), 1000\);
    \} catch \(e\) \{
        window\.open\(url, '_blank'\);
    \}
\}'''

new_func = r'''async function forceDownloadAudio(url, filename) {
    const downloadUrl = "https://www.apolloedit.com/api/download?url=" + encodeURIComponent(url);
    const iframe = document.createElement("iframe");
    iframe.style.display = "none";
    iframe.src = downloadUrl;
    document.body.appendChild(iframe);
    setTimeout(() => document.body.removeChild(iframe), 10000);
}'''

html = re.sub(old_func, new_func, html)

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
