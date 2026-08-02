import os
import re
path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\apollo_modal_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'@web_app\.post\("/generate/multipass"\)\s*\ndef api_generate_multipass[\s\S]*?return \{"status": "error", "message": f"Erro de roteamento Multipass: \{str\(e\)\}"\}', text)

if match:
    original_block = match.group(0)
    autoblog_block = original_block.replace(
        '@web_app.post("/generate/multipass")',
        '@web_app.post("/generate/autoblog/multipass")'
    ).replace(
        'def api_generate_multipass(req: MultiPassRequest):',
        'def api_generate_autoblog_multipass(req: MultiPassRequest):'
    ).replace(
        'UniversalComfyEngine',
        'BlogUniversalComfyEngine'
    )
    new_text = text[:match.end()] + "\n\n" + autoblog_block + text[match.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("apollo_modal_engine.py updated with autoblog multipass route!")
else:
    print("Could not find multipass block")
