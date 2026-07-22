import sys
import codecs

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\editor_audiomass.html'
with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

target = """    <div id="audiomass-wrapper" style="flex: 1; width: 100%; position: relative; overflow: hidden;">
        <!-- Engine Open Source Local (AudioMass) -->
        <iframe id="audiomass-container" src="engines/audiomass/src/index.html" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"></iframe>
    </div>

    <!-- Bruxelinha AI Assistant -->"""

replacement = """    <div id="audiomass-wrapper" style="flex: 1; width: 100%; position: relative; overflow: hidden;">
        <!-- Engine Open Source Local (AudioMass) -->
        <iframe id="audiomass-container" src="engines/audiomass/src/index.html" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"></iframe>
    </div>

    <!-- Interceptor de Downloads do iFrame -->
    <script>
        document.getElementById('audiomass-container').addEventListener('load', function() {
            try {
                const iframeWin = this.contentWindow;
                
                // Sequestra o clique em links de download gerados via Blob
                const originalClick = iframeWin.HTMLAnchorElement.prototype.click;
                iframeWin.HTMLAnchorElement.prototype.click = function() {
                    if (this.download && this.href && this.href.startsWith('blob:')) {
                        // O iFrame quer baixar um arquivo gerado localmente! Vamos copiar.
                        fetch(this.href).then(r => r.blob()).then(blob => {
                            if (window.apolloTransferOS) {
                                window.apolloTransferOS.receiveFile(blob, this.download || 'audio_exportado.wav');
                            }
                        }).catch(e => console.error("Erro ao sequestrar Blob do AudioMass:", e));
                    }
                    // Mantem o comportamento original
                    return originalClick.apply(this, arguments);
                };

                console.log("Ninja: Interceptador do Bagageiro injetado no AudioMass!");
            } catch(e) {
                console.warn("Falha ao injetar interceptador no AudioMass (CORS ou restricao):", e);
            }
        });
    </script>

    <!-- Bruxelinha AI Assistant -->"""

if target in content:
    content = content.replace(target, replacement)
    with codecs.open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Successfully patched editor_audiomass.html')
else:
    print('Target not found in editor_audiomass.html')
