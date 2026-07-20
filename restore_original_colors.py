import json
import os

base_dir = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\Workspaces"

workspaces = {
    "MACACO DRIVER": {
        "theme_colors": {
            "bg": "#FFE135",
            "app_bg": "#FFE135",
            "app_fg": "#1A1A1A",
            "header_bg": "#0F172A",
            "header_fg": "#FFE135",
            "accent": "#0F172A",
            "btn_bg": "#0F172A",
            "btn_fg": "#FFFFFF",
            "btn_active_bg": "#1E3A8A",
            "btn_active_fg": "#FFFFFF",
            "tab_bg": "#0F172A",
            "tab_fg": "#FFFFFF",
            "tab_selected_bg": "#FFE135",
            "tab_selected_fg": "#1A1A1A",
            "tab_active_bg": "#FFC107",
            "tab_active_fg": "#1A1A1A",
            "section_bg": "#FFE135",
            "section_fg": "#1A1A1A",
            
            "style_configure_TLabel": {"background": "#FFE135", "foreground": "#1A1A1A"},
            "style_configure_TLabelframe": {"background": "#FFE135"},
            "style_configure_TLabelframe.Label": {"background": "#FFE135", "foreground": "#1A1A1A"},
            "style_configure_TCheckbutton": {"background": "#FFE135", "foreground": "#1A1A1A"},
            "style_configure_TRadiobutton": {"background": "#FFE135", "foreground": "#1A1A1A"}
        }
    },
    "HISTORIAS DE 7 DIAS": {
        "theme_colors": {
            "bg": "#2D0A5E",
            "app_bg": "#2D0A5E",
            "app_fg": "#EDE9FE",
            "header_bg": "#130026",
            "header_fg": "#FFD700",
            "accent": "#4B1088",
            "btn_bg": "#4B1088",
            "btn_fg": "#FFFFFF",
            "btn_active_bg": "#7C3AED",
            "btn_active_fg": "#FFFFFF",
            "tab_bg": "#130026",
            "tab_fg": "#EDE9FE",
            "tab_selected_bg": "#FFD700",
            "tab_selected_fg": "#000000",
            "tab_active_bg": "#4B1088",
            "tab_active_fg": "#FFFFFF",
            "section_bg": "#2D0A5E",
            "section_fg": "#FFFFFF",
            
            "style_configure_TLabel": {"background": "#2D0A5E", "foreground": "#FFD700"},
            "style_configure_TLabelframe": {"background": "#2D0A5E"},
            "style_configure_TLabelframe.Label": {"background": "#2D0A5E", "foreground": "#FFD700"},
            "style_configure_TCheckbutton": {"background": "#2D0A5E", "foreground": "#FFFFFF"},
            "style_configure_TRadiobutton": {"background": "#2D0A5E", "foreground": "#FFFFFF"}
        }
    },
    "DESCARGA NEWS": {
        "theme_colors": {
            "bg": "#87CEEB",
            "app_bg": "#87CEEB",
            "app_fg": "#1E3A8A",
            "header_bg": "#0F172A",
            "header_fg": "#FFD700",
            "accent": "#0F172A",
            "btn_bg": "#0F172A",
            "btn_fg": "#FFFFFF",
            "btn_active_bg": "#1E3A8A",
            "btn_active_fg": "#FFFFFF",
            "tab_bg": "#0F172A",
            "tab_fg": "#FFFFFF",
            "tab_selected_bg": "#87CEEB",
            "tab_selected_fg": "#1E3A8A",
            "tab_active_bg": "#BFDBFE",
            "tab_active_fg": "#1E3A8A",
            "section_bg": "#87CEEB",
            "section_fg": "#1E3A8A",
            
            "style_configure_TLabel": {"background": "#87CEEB", "foreground": "#1E3A8A"},
            "style_configure_TLabelframe": {"background": "#87CEEB"},
            "style_configure_TLabelframe.Label": {"background": "#87CEEB", "foreground": "#1E3A8A"},
            "style_configure_TCheckbutton": {"background": "#87CEEB", "foreground": "#1E3A8A"},
            "style_configure_TRadiobutton": {"background": "#87CEEB", "foreground": "#1E3A8A"},
            "style_configure_Subtitle.TLabel": {"background": "#87CEEB", "foreground": "#374151"},
            "style_configure_Title.TLabel": {"background": "#87CEEB", "foreground": "#1E3A8A"}
        }
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
        
    with open(cfg_path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4)
        
print("Themes restored matching exactly the provided screenshots!")
