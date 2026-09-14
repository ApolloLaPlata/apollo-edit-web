import re
with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the inner setTimeout of downloadAllBatchFiles
start_marker = "window.batchGeneratedFiles.forEach((url, index) => {"
if start_marker in html:
    start_idx = html.find(start_marker) + len(start_marker)
    end_idx = html.find("delay += 800", start_idx)
    
    new_inner = '''
                setTimeout(() => {
                    let finalUrl = url;
                    if (url.includes("apolloedit.com/media")) {
                        finalUrl = "https://www.apolloedit.com/api/download?url=" + encodeURIComponent(url);
                    }
                    const iframe = document.createElement("iframe");
                    iframe.style.display = "none";
                    iframe.src = finalUrl;
                    document.body.appendChild(iframe);
                    setTimeout(() => document.body.removeChild(iframe), 10000);
                    logMusicMaster("Baixando arquivo " + (index + 1) + "...");
                }, delay);
                '''
    html = html[:start_idx] + new_inner + html[end_idx:]

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
