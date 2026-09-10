with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 1: logTerminal to log
text = text.replace("logTerminal", "log")

# Fix 2: Streaming support for generateMusicTest()
new_fetch = '''const response = await fetch(url, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json', 'x-apollo-lock': 'apollo-beta-key-2026' },
                  body: JSON.stringify({ prompt, lyrics, model, duration, reference_audio_base64: refBase64 })
              });
                                
                if (!response.ok) {
                    const errText = await response.text();
                    throw new Error(HTTP : );
                }
                
                let data = null;
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n');
                    
                    buffer = lines.pop();
                    
                    for (const line of lines) {
                        if (line.trim() === '') continue;
                        try {
                            const parsed = JSON.parse(line);
                            if (parsed.status === 'processing') {
                                log(⚡ [Modal] , 'info');
                            } else if (parsed.status === 'success' || parsed.status === 'error') {
                                data = parsed;
                            }
                        } catch(e) {
                            console.error("Erro no parse JSON do chunk:", e, line);
                        }
                    }
                }
                
                if (buffer.trim() !== '') {
                    try {
                        const parsed = JSON.parse(buffer);
                        if (parsed.status === 'success' || parsed.status === 'error') {
                            data = parsed;
                        }
                    } catch(e) {}
                }
                
                if (!data) {
                    throw new Error(Nenhum dado valido retornado no stream.);
                }
                
                document.getElementById('musicLoading').style.display = 'none';
              
                if (data.status === 'success') {
                  log('🚀 Áudio gerado com sucesso! ' + (data.message || ''), 'ok');
                  
                  document.getElementById('previewPlaceholder').style.display = 'none';
                  hideSpinner();

                  const audioSrc = data.audio_base64 ? 'data:audio/wav;base64,' + data.audio_base64 : data.audio_url;
                  const audNode = document.getElementById('previewAudio');
                  audNode.src = audioSrc;
                  audNode.style.display = 'block';
                  
                  currentImageData = data.audio_base64 || data.audio_url || "";
                  document.getElementById('btnDownloadPreview').style.display = 'block';
              } else {
                  log('❌ ERRO MODAL: ' + (data.message || JSON.stringify(data)), 'error');
                  document.getElementById('musicLoading').style.display = 'none';
                  hideSpinner();
              }
          } catch (err) {
                log('❌ CRASH FETCH: ' + err.message, 'error');
                document.getElementById('musicLoading').style.display = 'none';
                hideSpinner();
            }'''

idx_start = text.find("const response = await fetch(url, {")
idx_end = text.find("          } catch (err) {")
idx_end_catch = text.find("            }", idx_end) + 13

if idx_start != -1 and idx_end != -1:
    text = text[:idx_start] + new_fetch + text[idx_end_catch:]
    with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Sucesso na substituicao.")
else:
    print("Falha na substituicao. Revertendo.")
