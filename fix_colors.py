import json
import os

base_dir = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\Workspaces"
for ws in ["DESCARGA NEWS", "MACACO DRIVER", "HISTORIAS DE 7 DIAS"]:
    cfg_path = os.path.join(base_dir, ws, "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        if "theme_colors" in cfg:
            del cfg["theme_colors"]
        with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4)
print("Removed custom theme_colors from workspaces.")
