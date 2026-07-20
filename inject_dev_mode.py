import os
import glob

html_files = glob.glob(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\*.html")

links_html = []
for file_path in sorted(html_files):
    filename = os.path.basename(file_path)
    name_clean = filename.replace('.html', '').replace('_', ' ').title()
    link = f"""
                <a href="#" onclick="window.parent.openAppTab('{filename}', '📄 {name_clean}', true)" 
                   style="background: rgba(20, 15, 30, 0.8); border: 1px solid #4a2b6e; color: #cbd5e1; padding: 12px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: bold; transition: 0.2s; display: flex; align-items: center; gap: 8px;">
                    <span style="color: #9B59B6;">📄</span> {filename}
                </a>"""
    links_html.append(link)

grid_html = f"""
            <div id="dev-mode-pages" class="section-title" style="margin-top: 50px; border-top: 2px solid #4a2b6e; padding-top: 20px;">
                🗄️ TODAS AS PÁGINAS (DEV MODE)
            </div>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px;">Acesso rápido a todos os arquivos HTML para o planejamento de design (Basta clicar para abrir na aba).</p>
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin-bottom: 50px;">
{"".join(links_html)}
            </div>
"""

hub_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\hub.html"
with open(hub_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "dev-mode-pages" not in content:
    content = content.replace('</main>', grid_html + '        </main>')
    with open(hub_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected successfully into hub.html")
else:
    print("dev-mode-pages already in hub.html")
