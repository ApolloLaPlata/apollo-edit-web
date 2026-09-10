with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html", "r", encoding="utf-8") as f:
    text = f.read()

# Add button
btn_wav = """<button class="btn btn-primary btn-sm" id="btnDownloadPreview" onclick="downloadCurrentMedia()" style="display:none; font-weight:bold;">⬇️ Baixar Resultado</button>"""
btn_mp3 = btn_wav + """\n                <button class="btn btn-secondary btn-sm" id="btnDownloadMp3" onclick="convertAndDownloadMp3()" style="display:none; font-weight:bold; background: #6c5ce7; color: white; border: none; padding: 4px 12px; border-radius: 4px; cursor: pointer;">🎵 Baixar MP3</button>"""
text = text.replace(btn_wav, btn_mp3)

# Clear button visibility
clear1 = "document.getElementById('btnDownloadPreview').style.display = 'none';"
clear2 = clear1 + "\n    const btnMp3 = document.getElementById('btnDownloadMp3');\n    if(btnMp3) btnMp3.style.display = 'none';"
text = text.replace(clear1, clear2)

# Show MP3 button on audio success (first occurrence in music test)
sh1 = "currentAudioData = data.audio_base64 || data.audio_url || \"\";\n                  document.getElementById('btnDownloadPreview').style.display = 'block';"
sh2 = sh1 + "\n                  document.getElementById('btnDownloadMp3').style.display = 'block';"
text = text.replace(sh1, sh2)

# Show MP3 button on audio success (second occurrence in transcribe)
sh3 = "currentAudioData = data.audio_base64 || data.audio_url || \"\";\n                    document.getElementById('btnDownloadPreview').style.display = 'block';"
sh4 = sh3 + "\n                    document.getElementById('btnDownloadMp3').style.display = 'block';"
text = text.replace(sh3, sh4)

# Add convert function
convert_func = """
async function convertAndDownloadMp3() {
    if (!currentAudioData) return;
    
    // We already have the base64, send to backend to convert
    log('⏳ Convertendo WAV para MP3 na nuvem...', 'info');
    const oldText = document.getElementById('btnDownloadMp3').innerHTML;
    document.getElementById('btnDownloadMp3').innerHTML = '⏳ Convertendo...';
    document.getElementById('btnDownloadMp3').disabled = true;
    
    try {
        let b64 = currentAudioData;
        if (b64.includes(',')) {
            b64 = b64.split(',')[1];
        }
        
        const url = '/api/studio/modal/convert_mp3';
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026' },
            body: JSON.stringify({ audio_base64: b64 })
        });
        
        if (!response.ok) {
            throw new Error('Erro na conversão HTTP ' + response.status);
        }
        
        const data = await response.json();
        if (data.status === 'success' && data.audio_base64) {
            const a = document.createElement('a');
            a.href = 'data:audio/mp3;base64,' + data.audio_base64;
            a.download = `apollo_audio_converted_${Date.now()}.mp3`;
            a.click();
            log('💾 Download MP3 concluído.', 'ok');
        } else {
            throw new Error(data.message || 'Erro desconhecido na conversão.');
        }
    } catch(err) {
        log('❌ Falha na conversão para MP3: ' + err.message, 'error');
        alert("Falha na conversão para MP3!");
    } finally {
        document.getElementById('btnDownloadMp3').innerHTML = oldText;
        document.getElementById('btnDownloadMp3').disabled = false;
    }
}
</script>
"""
text = text.replace("</script>", convert_func, 1)

with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html", "w", encoding="utf-8") as f:
    f.write(text)
