import os
import json
import shutil

BASE_DIR = r"E:\MEUS PROGRAMAS"
APOLLO_DIR = os.path.join(BASE_DIR, "APOLLO_STUDIO")
WORKSPACES_DIR = os.path.join(APOLLO_DIR, "Workspaces")

canais_map = {
    "TUTORIAL DAS COISAS CODIGOS": "Tutorial das Coisas",
    "MACACO DRIVER CODIGOS": "MACACO DRIVER",
    "HISTORIAS DE 7 DIAS CODIGOS": "HISTORIAS DE 7 DIAS",
    "DESCARGA NEWS CODIGOS": "DESCARGA NEWS"
}

KEYS_TO_MIGRATE = [
    "personagens",
    "backgrounds",
    "paths",
    "video_settings",
    "use_compressor",
    "use_smart_pacing",
    "use_ducking",
    "tratamento_audio",
    "estetica_canal"
]

def migrar():
    for old_dir_name, new_ws_name in canais_map.items():
        old_dir = os.path.join(BASE_DIR, old_dir_name)
        new_dir = os.path.join(WORKSPACES_DIR, new_ws_name)
        
        if not os.path.exists(old_dir):
            print(f"DIRETÓRIO ANTIGO NÃO ENCONTRADO: {old_dir}")
            continue
            
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            print(f"NOVO WORKSPACE CRIADO: {new_dir}")
            
        old_config_path = os.path.join(old_dir, "config.json")
        new_config_path = os.path.join(new_dir, "config.json")
        
        old_cfg = {}
        if os.path.exists(old_config_path):
            try:
                with open(old_config_path, 'r', encoding='utf-8') as f:
                    old_cfg = json.load(f)
            except Exception as e:
                print(f"Erro ao ler config antigo {old_config_path}: {e}")
                
        new_cfg = {}
        if os.path.exists(new_config_path):
            try:
                with open(new_config_path, 'r', encoding='utf-8') as f:
                    new_cfg = json.load(f)
            except Exception as e:
                print(f"Erro ao ler config novo {new_config_path}: {e}")
                
        # Preservar chaves novas (colors, logo, etc)
        tema = new_cfg.get("theme_colors")
        app_logo = new_cfg.get("app_logo_path")
        app_icon = new_cfg.get("app_icon_path")
        
        # Migrar dados principais
        for key in KEYS_TO_MIGRATE:
            if key in old_cfg:
                new_cfg[key] = old_cfg[key]
                
        # Procurar logos na pasta antiga
        icon_found = None
        img_found = None
        for file in os.listdir(old_dir):
            if file.lower().endswith('.ico'):
                if not icon_found or 'logo' in file.lower():
                    icon_found = file
            if file.lower().endswith('.png'):
                if not img_found or 'logo' in file.lower():
                    img_found = file
                
        # Copiar logos
        if img_found and not app_logo:
            src = os.path.join(old_dir, img_found)
            dst = os.path.join(new_dir, img_found)
            shutil.copy2(src, dst)
            new_cfg["app_logo_path"] = dst
            print(f"Copiado logo: {img_found}")
            
        if icon_found and not app_icon:
            src = os.path.join(old_dir, icon_found)
            dst = os.path.join(new_dir, icon_found)
            shutil.copy2(src, dst)
            new_cfg["app_icon_path"] = dst
            print(f"Copiado ícone: {icon_found}")
            
        # Manter cores se já tiverem sido setadas
        if tema:
            new_cfg["theme_colors"] = tema
            
        # Salvar config novo
        try:
            with open(new_config_path, 'w', encoding='utf-8') as f:
                json.dump(new_cfg, f, indent=4, ensure_ascii=False)
            print(f"SUCESSO: Configurações de '{old_dir_name}' migradas para '{new_ws_name}'")
        except Exception as e:
            print(f"Erro ao salvar novo config {new_config_path}: {e}")

if __name__ == "__main__":
    migrar()
