import re

for fpath in ['frontend/modal_ai_studio.html', 'public/modal_ai_studio.html']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add debugging alerts or logs
    content = content.replace("musicRunning = true;", "musicRunning = true;\n            logMusicMaster('Iniciando script de geração...');")
    content = content.replace("logMusicMaster(\"[\" + (i+1) + \"/\" + prompts.length + \"] Solicitando gera", "logMusicMaster('Preparando fetch...');\n                  logMusicMaster(\"[\" + (i+1) + \"/\" + prompts.length + \"] Solicitando gera")
    content = content.replace("} catch(e) {", "} catch(e) {\n                    alert('Erro capturado: ' + e.message);\n                    console.error(e);")
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Patched {fpath}")
