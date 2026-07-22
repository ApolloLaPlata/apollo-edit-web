import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['index.html', 'login.html', 'hub.html', 'tanque.html', 'dashboard.html']]

new_header_content = """
        <!-- Logo e Créditos -->
        <div class="top-nav" style="flex-grow: 1; display: flex; align-items: center; justify-content: flex-start; gap: 20px;">
            <a href="hub.html" style="text-decoration: none;">
                <div class="main-logo"><span>APOLLO</span> EDIT WEB</div>
            </a>
            <span class="badge" style="background: rgba(124,58,237,.2); color: #9B59B6; padding: 4px 8px; border-radius: 4px;" data-i18n="{BADGE_KEY}">{BADGE_TEXT}</span>
            <div class="credits-badge" style="margin-left: 20px; display: flex; align-items: center;">
                <span class="gas-icon"></span>
                <strong id="user-credits" data-i18n="common.loading">Carregando...</strong>&nbsp;<span data-i18n="common.gasoline">Gasolina</span>
            </div>
        </div>

        <div class="user-widget" id="user-widget" style="display: flex; gap: 10px; align-items: center; margin-left: auto;">
            <div class="user-info" style="text-align: right; display: flex; flex-direction: column;">
                <span class="user-name" id="user-name" data-i18n="header.user_pro" style="font-size: 14px; font-weight: bold; color: #fff;">Usuário Pro</span>
            </div>
            <div class="avatar" style="width: 40px; height: 40px; border-radius: 50%; background: #333; border: 2px solid #FFD32A;"></div>
        </div>
"""

ad_block = """
    <div class="ad-slot" style="margin-bottom: 20px; min-height: 90px; padding: 10px;">
        <span data-i18n="common.ad_space_728">[BANNER 728x90 ADSENSE]</span>
    </div>
"""

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract badge info if exists
    badge_match = re.search(r'<span class=".*badge".*?data-i18n="([^"]+)".*?>(.*?)</span>', content)
    badge_key = badge_match.group(1) if badge_match else "common.loading"
    badge_text = badge_match.group(2) if badge_match else "Ferramenta"
    
    # Replace header inner content
    custom_header = new_header_content.replace("{BADGE_KEY}", badge_key).replace("{BADGE_TEXT}", badge_text)
    
    # Find header block
    header_pattern = r'(<header[^>]*>).*?(</header>)'
    
    def repl(m):
        return m.group(1) + custom_header + m.group(2)
        
    content = re.sub(header_pattern, repl, content, flags=re.DOTALL)
    
    # Insert ad block right after </header> if not timeline.html
    if f != 'timeline.html':
        if 'ad-slot' not in content:
            content = content.replace('</header>', '</header>\n' + ad_block)
            
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
        
print("Done patching HTMLs")
