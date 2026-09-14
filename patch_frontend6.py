with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

batch_old = '''window.batchGeneratedFiles.forEach((url, index) => {
                  setTimeout(() => {
                      const dlUrl = `https://www.apolloedit.com/api/download?url=${encodeURIComponent(url)}`;
                      window.open(dlUrl, '_blank');
                      logMusicMaster("Baixando arquivo " + (index + 1) + "...");
                  }, delay);'''
batch_new = '''window.batchGeneratedFiles.forEach((url, index) => {
                  setTimeout(() => {
                      const dlUrl = `https://www.apolloedit.com/api/download?url=${encodeURIComponent(url)}`;
                      const iframe = document.createElement('iframe');
                      iframe.style.display = 'none';
                      iframe.src = dlUrl;
                      document.body.appendChild(iframe);
                      setTimeout(() => document.body.removeChild(iframe), 10000);
                      logMusicMaster("Baixando arquivo " + (index + 1) + "...");
                  }, delay);'''
html = html.replace(batch_old, batch_new)

with open('frontend/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
