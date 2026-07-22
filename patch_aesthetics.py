import os
import re

html_files = [
    'midia.html', 'volume.html', 'dublagem.html', 'tts.html', 
    'legendas.html', 'narrador.html', 'montador.html', 'musica.html', 
    'podcast.html', 'timeline.html', 'dashboard.html', 'fila.html', 
    'config.html', 'tanque.html'
]

# Mapa de Ícones e Descrições para cada página
page_info = {
    'midia.html': ('Resize Crop', 'Redimensione e ajuste mídias com blur.', '✂️'),
    'volume.html': ('Audio Normalizer', 'Padronize o volume de seus vídeos.', '🔊'),
    'dublagem.html': ('Dublagem RVC', 'Clone vozes e duble automaticamente.', '🎙️'),
    'tts.html': ('Motor Voz IA', 'Geração de voz neural de alta qualidade.', '🗣️'),
    'legendas.html': ('Auto Legendas', 'Gere legendas animadas estilo TikTok.', '📝'),
    'narrador.html': ('Avatar Mágico', 'Avatar falante movido a IA.', '🧙‍♂️'),
    'montador.html': ('Montador Dark', 'Cortes secos e edição automatizada.', '🎬'),
    'musica.html': ('Fábrica Musical', 'Trilhas sonoras geradas por IA.', '🎵'),
    'podcast.html': ('Cast Creator', 'Crie conversas entre duas vozes.', '🎧'),
    'timeline.html': ('Timeline Master', 'Edição avançada multi-faixas.', '🎞️'),
    'dashboard.html': ('DEXboard', 'Estatísticas, custos e armazenamento.', '📊'),
    'fila.html': ('Fila de Render', 'Gerencie seus trabalhos no Render Farm.', '⏱️'),
    'config.html': ('Chaves API', 'Configure suas chaves BYOK.', '🔑'),
    'tanque.html': ('O Tanque', 'Compre Gasolina e abasteça seu estúdio.', '⛽')
}

def inject_aesthetics(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, not found.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(filepath)
    if filename not in page_info:
        return

    title, desc, icon = page_info[filename]

    header_html = f"""
        <div class="single-tool-header" style="margin-bottom: 30px; display: flex; align-items: center; gap: 20px; background: linear-gradient(145deg, #2a164d 0%, #170d2b 100%); padding: 30px; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 2px solid var(--btn-purple); position: relative; overflow: hidden;">
            <!-- Decorativo fundo -->
            <div style="position:absolute; top:-30px; right:-20px; font-size: 150px; opacity: 0.05; transform: rotate(15deg); pointer-events: none;">🏎️</div>
            
            <div style="font-size: 3.5rem; background: var(--btn-purple); border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; border: var(--border-thick); box-shadow: 0 8px 0 var(--border-dark); z-index: 2;">{icon}</div>
            <div style="z-index: 2;">
                <h3 style="font-family: 'Bangers', cursive; font-size: 3.5rem; color: var(--btn-yellow); text-shadow: 4px 4px 0 var(--border-dark); margin: 0; letter-spacing: 3px;">
                    {title.upper()}
                </h3>
                <p style="font-family: 'Nunito', sans-serif; font-size: 1.4rem; color: #cbd5e1; margin: 0; font-weight: 800; text-shadow: 1px 1px 0 #000;">
                    {desc}
                </p>
            </div>
        </div>
"""

    bottom_ad_html = """
        <div class="ad-slot" style="margin-top: 30px; min-height: 90px; padding: 10px; background: repeating-linear-gradient(45deg, #1e1e1e, #1e1e1e 10px, #2a2a2a 10px, #2a2a2a 20px); border: 2px dashed #444;">
            <span style="font-family: 'Bangers', cursive; font-size: 1.5rem; color: #666; letter-spacing: 2px;">[ESPAÇO PUBLICITÁRIO - 728x90 INFERIOR]</span>
        </div>
"""

    # Add header
    if 'class="single-tool-header"' not in content:
        if '<div class="main-container">' in content:
            content = content.replace('<div class="main-container">', f'<div class="main-container">\n{header_html}', 1)
        elif '<div class="container">' in content:
             content = content.replace('<div class="container">', f'<div class="container">\n{header_html}', 1)
        elif '<div class="workspace">' in content:
             content = content.replace('<div class="workspace">', f'<div class="workspace" style="flex-direction: column;">\n{header_html}\n<div style="display: flex; flex-grow: 1; height: 100%;">', 1)
             content = content.replace('<!-- Bottom: Timeline Editor -->', '</div>\n    <!-- Bottom: Timeline Editor -->', 1)

    # Add bottom ad
    if '[ESPAÇO PUBLICITÁRIO - 728x90 INFERIOR]' not in content:
        # Encontrar fechamento do main-container. Um pouco dificil com regex simples, 
        # vamos injetar antes do fechamento do main-container.
        # Uma forma fácil é colocar antes do <script> que normalmente fica no fim.
        if '<script>' in content:
            # We'll split by the first <script> that is NOT from cdn or auth
            # Wait, easier to use regex or string manipulation.
            content = content.replace('    <script>', f'{bottom_ad_html}\n    <script>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {filename}")

for f in html_files:
    inject_aesthetics(f)

print("All aesthetic patches applied!")
