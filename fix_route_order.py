import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Encontrar o bloco da rota /api/audio/lab_test
start_idx = content.find('@app.post("/api/audio/lab_test")')
if start_idx != -1:
    # O bloco vai até o final do arquivo, já que inserimos lá. Mas cuidado se houver mais coisas.
    end_idx = len(content) # O bloco ia até o final.
    
    route_code = content[start_idx:end_idx].strip()
    
    # Remove a rota do final
    content = content[:start_idx].strip()
    
    # 2. Encontrar o app.mount("/", ...)
    mount_idx = content.find('app.mount("/", StaticFiles(directory=WEB_UI_DIR), name="static")')
    
    if mount_idx != -1:
        # Pular umas linhas acima do app.mount para inserir a rota
        insert_idx = content.rfind('# Todo o', 0, mount_idx)
        if insert_idx == -1:
            insert_idx = mount_idx
            
        new_content = content[:insert_idx] + "\n" + route_code + "\n\n" + content[insert_idx:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Rota movida para CIMA do app.mount!")
    else:
        print("Não achou o app.mount!")
else:
    print("Não achou a rota no final do arquivo!")
