import sys
import re

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Revert the URL to use relative /api/
text = text.replace(
    "const url = 'http://163.176.135.59/api/studio/modal/generate/audio_lab';",
    "const url = '/api/studio/modal/generate/audio_lab';"
)

# 2. Hide musicResultCard by default and remove it from being shown
text = text.replace("document.getElementById('musicResultCard').style.display = 'block';", "")

# 3. On success, just show the right panel (already doing that), and log to the terminal
success_block = """if (data.status === 'success') {
                    // Log to terminal
                    logTerminal('🚀 Áudio gerado com sucesso! ' + (data.message || ''));
                    
                    // Esconde placeholder e spinner do lado direito
                    document.getElementById('previewPlaceholder').style.display = 'none';
                    hideSpinner();

                    // Toca o audio no lado direito
                    const audioSrc = data.audio_base64 ? 'data:audio/wav;base64,' + data.audio_base64 : data.audio_url;
                    const audNode = document.getElementById('previewAudio');
                    audNode.src = audioSrc;
                    audNode.style.display = 'block';
                    
                    // Permite download
                    currentImageData = data.audio_base64 || data.audio_url || "";
                    document.getElementById('btnDownloadPreview').style.display = 'block';
                } else {
                    logTerminal('❌ ERRO MODAL: ' + JSON.stringify(data));
                    hideSpinner();
                }"""

text = re.sub(r"if \(data\.status === 'success'\) \{[\s\S]*?\} else \{[\s\S]*?\}", success_block, text)

# 4. On catch error, log to terminal instead of musicError
error_block = """} catch (err) {
                  logTerminal('❌ CRASH FETCH: ' + err.message);
                  hideSpinner();
              }"""
text = re.sub(r"\} catch \(err\) \{[\s\S]*?\}", error_block, text)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
