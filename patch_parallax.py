import os

html_files = [
    'midia.html', 'volume.html', 'dublagem.html', 'tts.html', 
    'legendas.html', 'narrador.html', 'montador.html', 'musica.html', 
    'podcast.html', 'timeline.html', 'dashboard.html', 'fila.html', 
    'config.html', 'tanque.html', 'ferramentas.html', 'hub.html'
]

bg_html = '<div id="global-3d-bg"></div>'
script_html = '<script src="bg_parallax.js"></script>'

def patch_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, not found.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # Inject background div right after <body>
    if bg_html not in content and '<body>' in content:
        content = content.replace('<body>', f'<body>\n    {bg_html}', 1)
        modified = True

    # Inject parallax script before </body>
    if script_html not in content and '</body>' in content:
        content = content.replace('</body>', f'    {script_html}\n</body>', 1)
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")

for f in html_files:
    patch_file(f)

print("Parallax Patching complete!")
