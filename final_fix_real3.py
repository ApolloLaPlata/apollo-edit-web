import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Just do regex with re.DOTALL between "preview.innerHTML =" and "for (let i = 0;"
    pattern = re.compile(r'preview\.innerHTML = `.*?;\n            \}\n.*?(?=for \(let i = 0)', re.DOTALL)
    
    good_block = """preview.innerHTML = `
                    <div style="padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 style="color: white;">🎧 Histórico de Áudios (Bagagem)</h3>
                            <button id="batchDownloadAllContainer" class="btn btn-primary" onclick="downloadAllBatchFiles()" style="display:none; font-weight: bold; background: #00d2ff; color: black; border: none; box-shadow: 0 0 10px rgba(0, 210, 255, 0.5);">
                                ⬇️ Baixar Todas as Músicas
                            </button>
                        </div>
                        <div id="batchTracksList" style="display:flex; flex-direction:column; gap:15px;"></div>
                    </div>
                `;
            }
            
            """
    
    content = re.sub(pattern, good_block, content)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {fpath}")
