import os

html_path = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
js_path = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias_core.js'

# Patch HTML
with open(html_path, 'r', encoding='latin-1') as f:
    html_content = f.read()

badge_target = """<span style="font-size: 12px; font-weight: 600; background: #d1fae5; color: #047857; padding: 4px 12px; border-radius: 9999px;">
                                            Dashboard em Breve
                                        </span>"""
badge_replace = """<span style="font-size: 12px; font-weight: 600; background: #d1fae5; color: #047857; padding: 4px 12px; border-radius: 9999px;">
                                            Status do Sistema
                                        </span>"""

html_content = html_content.replace(badge_target, badge_replace)

panel_target = """Dashboard.
                                    </p>

                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px;">"""
panel_replace = """Dashboard.
                                    </p>
                                    
                                    <!-- Mini Dashboard Status Panel -->
                                    <div id="social-status-panel" style="margin-bottom: 24px; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; display: flex; gap: 12px; flex-wrap: wrap;">
                                    </div>

                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px;">"""

html_content = html_content.replace(panel_target, panel_replace)

with open(html_path, 'w', encoding='latin-1') as f:
    f.write(html_content)


# Patch JS
with open(js_path, 'r', encoding='latin-1') as f:
    js_content = f.read()

js_patch = """
function renderSocialStatus() {
    const panel = document.getElementById('social-status-panel');
    if (!panel) return;
    
    const platforms = [
        { id: 'api_key_twitter', name: 'X (Twitter)', icon: 'fab fa-twitter', color: '#0ea5e9' },
        { id: 'api_key_youtube', name: 'YouTube', icon: 'fab fa-youtube', color: '#ef4444' },
        { id: 'api_key_instagram', name: 'Instagram', icon: 'fab fa-instagram', color: '#ec4899' },
        { id: 'api_key_facebook', name: 'Facebook', icon: 'fab fa-facebook', color: '#3b5998' },
        { id: 'api_key_tiktok', name: 'TikTok', icon: 'fab fa-tiktok', color: '#000000' },
        { id: 'api_key_kwai', name: 'Kwai', icon: 'fas fa-video', color: '#f97316' }
    ];
    
    let html = '';
    platforms.forEach(p => {
        const hasKey = !!localStorage.getItem(p.id);
        const statusColor = hasKey ? '#10b981' : '#9ca3af';
        const statusText = hasKey ? 'Conectado' : 'Pendente';
        const bgColor = hasKey ? '#ecfdf5' : '#f3f4f6';
        
        html += `
            <div style="display: flex; align-items: center; gap: 8px; padding: 6px 12px; background: ${bgColor}; border: 1px solid ${hasKey ? '#a7f3d0' : '#e5e7eb'}; border-radius: 999px; font-size: 12px; font-weight: 500; color: #374151;">
                <i class="${p.icon}" style="color: ${p.color};"></i> ${p.name}: <span style="color: ${statusColor};">${statusText}</span>
            </div>
        `;
    });
    
    panel.innerHTML = html;
}
"""

if "renderSocialStatus" not in js_content:
    js_content += js_patch
    
    # inject into loadSettings
    # Find the end of loadSettings block
    load_settings_target = """    if (autoSave) {
        const v = localStorage.getItem('setting_autoSave');
        if (v !== null) autoSave.checked = (v === 'true');
    }"""
    load_settings_replace = """    if (autoSave) {
        const v = localStorage.getItem('setting_autoSave');
        if (v !== null) autoSave.checked = (v === 'true');
    }
    
    if (typeof renderSocialStatus === 'function') {
        renderSocialStatus();
    }"""
    js_content = js_content.replace(load_settings_target, load_settings_replace)
    
    # inject into saveSettings
    save_settings_target = """    const statusDiv = document.getElementById('settings-save-status');
    statusDiv.style.display = 'block';"""
    save_settings_replace = """    const statusDiv = document.getElementById('settings-save-status');
    statusDiv.style.display = 'block';
    
    if (typeof renderSocialStatus === 'function') {
        renderSocialStatus();
    }"""
    js_content = js_content.replace(save_settings_target, save_settings_replace)

    with open(js_path, 'w', encoding='latin-1') as f:
        f.write(js_content)
    print("Social Dashboard patched successfully!")
else:
    print("Social Dashboard already patched.")

