import os
import json

base_dir = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\Workspaces"

workspaces = {
    "MACACO DRIVER": {
        "theme_colors": {"bg": "#FFE135", "fg": "#1A1A1A", "accent": "#1A1A1A"},
        "app_logo_path": r"E:\MEUS PROGRAMAS\MACACO DRIVER CODIGOS\macaco_logo.ico"
    },
    "HISTORIAS DE 7 DIAS": {
        "theme_colors": {"bg": "#2D0A5E", "fg": "#FFD700", "accent": "#4B1088"},
        "app_logo_path": r"E:\MEUS PROGRAMAS\HISTORIAS DE 7 DIAS CODIGOS\logohistoriasde7dias.ico"
    },
    "DESCARGA NEWS": {
        "theme_colors": {"bg": "#87CEEB", "fg": "#1E3A8A", "accent": "#FFD700"},
        "app_logo_path": r"E:\MEUS PROGRAMAS\DESCARGA NEWS CODIGOS\logo-descarga-noticias-sem-fundo-horizontal.ico"
    }
}

for ws, data in workspaces.items():
    cfg_path = os.path.join(base_dir, ws, "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r', encoding='utf-8') as f:
            try:
                cfg = json.load(f)
            except:
                cfg = {}
    else:
        cfg = {}
        
    cfg["theme_colors"] = data["theme_colors"]
    # Change to PNG if available, but ICO works too
    png_logo = data["app_logo_path"].replace(".ico", ".png")
    if os.path.exists(png_logo):
        cfg["app_logo_path"] = png_logo
    else:
        cfg["app_logo_path"] = data["app_logo_path"]
        
    with open(cfg_path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4)
        
print("Cores e logos atualizados com sucesso!")
