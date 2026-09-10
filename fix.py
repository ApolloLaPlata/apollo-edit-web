import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace("throw new Error( + '' + r'HTTP : ' + '' + r);", "throw new Error(`HTTP ${res.status}: ${errText}`);")
html = html.replace("log( + '' + r'📦 Job enfileirado no backend (ID: ...). Iniciando polling...' + '' + r, 'info');", "log(`📦 Job enfileirado no backend (ID: ${jobId}). Iniciando polling...`, 'info');")
html = html.replace("log( + '' + r'💓 Consultando status... (s)' + '' + r, 'info');", "log(`💓 Consultando status... (${now}s)`, 'info');")
html = html.replace("document.getElementById('spinnerLabel').textContent =  + '' + r'Gerando Vídeo... s' + '' + r;", "document.getElementById('spinnerLabel').textContent = `Gerando Vídeo... ${now}s`;")
html = html.replace("const statusRes = await fetch( + '' + r'/api/studio/modal/status/' + '' + r);", "const statusRes = await fetch(`/api/studio/modal/status/${jobId}`);")
html = html.replace("throw new Error( + '' + r'Erro ao consultar status: HTTP ' + '' + r);", "throw new Error(`Erro ao consultar status: HTTP ${statusRes.status}`);")

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(html)
