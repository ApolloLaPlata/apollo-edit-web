import os

css_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\global_style.css'

css_to_append = """
/* =========================================================================
   HYBRID RPG AESTHETIC - CARDS & SIDEBAR
   ========================================================================= */

/* Modificando os itens da Sidebar e Grid de ferramentas para a estética roxa/neon */
.rpg-item, .tool-card {
    background: rgba(30, 20, 50, 0.7) !important;
    border: 1px solid rgba(155, 89, 182, 0.5) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    backdrop-filter: blur(5px) !important;
    transition: all 0.3s ease !important;
}

.rpg-item:hover, .tool-card:hover {
    border-color: #e0b0ff !important;
    box-shadow: 0 5px 25px rgba(155, 89, 182, 0.6) !important;
    transform: translateY(-5px) scale(1.02) !important;
    background: rgba(40, 25, 70, 0.9) !important;
}

.rpg-item-name, .tool-card h3 {
    color: #fff !important;
    text-shadow: 0 0 5px rgba(255,255,255,0.3) !important;
    font-weight: bold !important;
}

/* Modificando a sidebar para não ficar um cinza triste */
.side-panel {
    background: linear-gradient(180deg, rgba(15, 10, 25, 0.95), rgba(5, 5, 10, 0.95)) !important;
    border-right: 1px solid #4a2b6e !important;
}

.section-title {
    color: #e0b0ff !important;
    text-shadow: 0 0 10px rgba(155, 89, 182, 0.4) !important;
    border-bottom: 1px solid #4a2b6e !important;
}

/* Header mais vivo */
header {
    background: linear-gradient(90deg, #100b16, #211333) !important;
    border-bottom: 2px solid #4a2b6e !important;
}

.main-logo {
    color: #FFD32A !important;
    text-shadow: 0 0 10px rgba(255, 211, 42, 0.6) !important;
}
.main-logo span {
    color: #e0b0ff !important;
}

/* Esconder qualquer barra de scroll que fique feia com o blur */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #0b0510;
}
::-webkit-scrollbar-thumb {
    background: #4a2b6e;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #9B59B6;
}
"""

with open(css_path, 'r', encoding='utf-8') as f:
    current_css = f.read()

if "HYBRID RPG AESTHETIC - CARDS & SIDEBAR" not in current_css:
    with open(css_path, 'a', encoding='utf-8') as f:
        f.write("\n" + css_to_append)
    print("Cards CSS injected.")
else:
    print("Already injected.")
