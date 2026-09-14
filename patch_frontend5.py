with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

# For batch download
batch_old = '''window.batchGeneratedFiles.forEach((url, index) => {
                  setTimeout(() => {
                      forceDownloadAudio(url);
                      logMusicMaster("Baixando arquivo " + (index + 1) + "...");
                  }, delay);'''
batch_new = '''window.batchGeneratedFiles.forEach((url, index) => {
                  setTimeout(() => {
                      const dlUrl = `https://www.apolloedit.com/api/download?url=${encodeURIComponent(url)}`;
                      window.open(dlUrl, '_blank');
                      logMusicMaster("Baixando arquivo " + (index + 1) + "...");
                  }, delay);'''
html = html.replace(batch_old, batch_new)

# For single download
html = html.replace('<button onclick="forceDownloadAudio(`${fileUrlAbs}`)" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</button>', '<a href="https://www.apolloedit.com/api/download?url=${encodeURIComponent(fileUrlAbs)}" target="_blank" class="btn btn-primary" style="white-space: nowrap; height: fit-content;">⬇️ Baixar</a>')

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
