with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = '''    acc = get_active_modal_account()
    if not acc:
        raise HTTPException(status_code=503, detail="Nenhuma conta Modal ativa configurada na Colmeia.")
        
    workspace = acc.get("workspace")
    if not workspace:
        raise HTTPException(status_code=500, detail="Workspace modal nao configurado.")

    remote_path = path
    if path == "generate_image":
        remote_path = "generate/image"
    elif path == "generate_video":
        remote_path = "generate/video"
    elif path == "generate_universal":
        remote_path = "generate/universal"
    elif path == "generate_tts":
        remote_path = "generate/tts"'''

new_block = '''    # Dual-routing system for Modalities
    workspace = "sitesviniciusmiranda" # fallback
    
    remote_path = path
    if path == "generate_image":
        remote_path = "generate/image"
        workspace = "canalobservadoreconomico" # Conta 7
    elif path == "generate_video":
        remote_path = "generate/video"
        workspace = "canalobservadoreconomico" # Conta 7
    elif path == "generate_universal":
        remote_path = "generate/universal"
        workspace = "canalobservadoreconomico" # Conta 7
    elif path == "generate_tts":
        remote_path = "generate/tts"
        workspace = "sitesviniciusmiranda" # Conta 10'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("PATCH ROUTES SUCCESS!")
else:
    print("ERRO: routes_studio old block not found")
