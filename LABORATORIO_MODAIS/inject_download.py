with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8') as f:
    code = f.read()

download_fn = '''
        function downloadAllBatchFiles() {
            if (!window.batchGeneratedFiles || window.batchGeneratedFiles.length === 0) {
                alert("Nenhuma música foi gerada para baixar.");
                return;
            }
            logMusicMaster("Iniciando download em lote...");
            let delay = 0;
            window.batchGeneratedFiles.forEach((url, index) => {
                setTimeout(() => {
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = url.split("/").pop(); // extrai o nome final do arquivo
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    logMusicMaster("Baixando arquivo " + (index + 1) + "...");
                }, delay);
                delay += 800; // 800ms delay para não travar o navegador
            });
        }
'''

if 'function downloadAllBatchFiles' not in code:
    code = code.replace('async function generateMusicMaster()', download_fn + '\n        async function generateMusicMaster()')

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(code)
