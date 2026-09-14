import re
import glob

bad_block = '''            if (!document.getElementById('batchTracksList')) {
                preview.innerHTML = 
                    <div style="padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 style="color: white;">🎧 Histórico de Áudios (Bagagem)</h3>
                            <button id="batchDownloadAllContainer" class="btn btn-primary" onclick="downloadAllBatchFiles()" style="display:none; font-weight: bold; background: #00d2ff; color: black; border: none; box-shadow: 0 0 10px rgba(0, 210, 255, 0.5);">
                                ⬇️ Baixar Todas as Músicas
                            </button>
                        </div>
                        <div id="batchTracksList" style="display:flex; flex-direction:column; gap:15px;"></div>
                    </div>
                ;
            }">
                    <h2 style="color: white; margin-bottom: 20px; text-align: center;">🚀 Resultados da Sessão</h2>
                    <div id="batchDownloadAllContainer" style="text-align:center; margin-bottom: 20px; display:none;">
                        <button class="btn btn-primary" onclick="downloadAllBatchFiles()" style="font-size: 1.2rem; padding: 15px 30px; font-weight: bold; background: #00d2ff; color: black; border: none; box-shadow: 0 0 15px rgba(0, 210, 255, 0.5);">
                            💾 Baixar Todas as Músicas
                        </button>
                    </div>
                    <div id="batchTracksList" style="display:flex; flex-direction:column; gap:15px;"></div>
                </div>
              ;'''

good_block = '''            if (!document.getElementById('batchTracksList')) {
                preview.innerHTML = 
                    <div style="padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h3 style="color: white;">🎧 Histórico de Áudios (Bagagem)</h3>
                            <button id="batchDownloadAllContainer" class="btn btn-primary" onclick="downloadAllBatchFiles()" style="display:none; font-weight: bold; background: #00d2ff; color: black; border: none; box-shadow: 0 0 10px rgba(0, 210, 255, 0.5);">
                                ⬇️ Baixar Todas as Músicas
                            </button>
                        </div>
                        <div id="batchTracksList" style="display:flex; flex-direction:column; gap:15px;"></div>
                    </div>
                ;
            }'''

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html', 'web_ui/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try replacing using regex because of potential encoding issues with emojis
    pattern = re.compile(r"if \(!document.getElementById\('batchTracksList'\)\) \{.*?</div>\s*;", re.DOTALL)
    new_content = re.sub(pattern, good_block.strip(), content)
    
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Patched {fpath}")
    else:
        print(f"Failed to patch {fpath}")

