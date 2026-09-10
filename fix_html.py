import sys
import re

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add previewAudio to the right panel
if 'id="previewAudio"' not in text:
    text = text.replace(
        '<video id="previewVideo" controls></video>',
        '<video id="previewVideo" controls></video>\n            <!-- Resultado: Audio -->\n            <audio id="previewAudio" controls style="display: none; width: 80%; box-shadow: 0 8px 40px #00d2ff22; border-radius: 12px;"></audio>'
    )

# 2. Update clearPreview
if "document.getElementById('previewAudio').style.display = 'none';" not in text:
    text = text.replace(
        "vidNode.src = '';",
        "vidNode.src = '';\n\n    const audNode = document.getElementById('previewAudio');\n    if (audNode) { audNode.style.display = 'none'; audNode.src = ''; }"
    )

# 3. Update showSpinner
if "document.getElementById('previewAudio').style.display = 'none';" not in text:
    text = text.replace(
        "document.getElementById('previewVideo').style.display = 'none';",
        "document.getElementById('previewVideo').style.display = 'none';\n    if(document.getElementById('previewAudio')) document.getElementById('previewAudio').style.display = 'none';"
    )

# 4. Update generateMusicTest to use the right panel for audio, and left panel for logs
# Remove the old musicOutput logic
text = re.sub(
    r"if \(data\.status === 'success'\) \{[\s\S]*?\} else \{",
    """if (data.status === 'success') {
                    // Manda log pro lado esquerdo
                    document.getElementById('musicOutput').style.display = 'block';
                    document.getElementById('musicOutput').innerHTML = '<div style="color: #00d2ff; font-family: monospace; font-size: 0.9rem;">[OK] Áudio gerado com sucesso!<br><br>Status: ' + data.message + '</div>';
                    
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
                } else {""",
    text
)

# 5. Make generateMusicTest trigger the right-panel spinner
if "showSpinner('Gerando áudio..." not in text:
    text = text.replace(
        "document.getElementById('musicError').style.display = 'none';",
        "document.getElementById('musicError').style.display = 'none';\n            showSpinner('Gerando áudio. Isso pode levar até 90 segundos...');"
    )

# 6. Make generateMusicTest stop the spinner on error
text = text.replace(
    "document.getElementById('musicError').textContent = 'CRASH FETCH: ' + err.message;",
    "document.getElementById('musicError').textContent = 'CRASH FETCH: ' + err.message;\n                hideSpinner();"
)
text = text.replace(
    "document.getElementById('musicError').textContent = JSON.stringify(data, null, 2);",
    "document.getElementById('musicError').textContent = JSON.stringify(data, null, 2);\n                    hideSpinner();"
)

# 7. Remove the old musicPlayer from musicOutput
text = re.sub(
    r'<audio id="musicPlayer" controls.*?></audio>',
    '<!-- Log Text vai aqui -->',
    text
)

with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(text)
