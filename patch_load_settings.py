import re

filepath = r'e:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias_core.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# Check if loadSettings already exists
if 'function loadSettings' in content:
    print('loadSettings already exists, skipping append.')
else:
    # Append loadSettings after the last DOMContentLoaded initNewsTab
    append_code = """

// --- Settings: Load saved values on page init ---
function loadSettings() {
    const fields = [
        'api_key_grok', 'api_key_openai', 'api_key_openrouter',
        'api_key_gemini', 'api_key_pixabay', 'api_key_pexels', 'api_key_apify',
        'setting_tone', 'setting_language', 'setting_theme',
        'api_key_twitter', 'api_key_youtube', 'api_key_instagram',
        'api_key_facebook', 'api_key_tiktok', 'api_key_kwai'
    ];
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        const stored = localStorage.getItem(id === 'api_key_openrouter' ? 'openrouter_api_key' : id);
        if (stored !== null) el.value = stored;
    });
    const autoSave = document.getElementById('setting_autoSave');
    if (autoSave) {
        const v = localStorage.getItem('setting_autoSave');
        if (v !== null) autoSave.checked = (v === 'true');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
});
"""
    content += append_code
    print('loadSettings appended.')

# Fix settings icon color from indigo to violet
content = content.replace(
    'class="fas fa-cog" style="color: #4f46e5;"',
    'class="fas fa-cog" style="color: #8b5cf6;"'
)
# Fix settings save button from default to violet
content = content.replace(
    'Salvar Configura\xe7\xf5es',
    'Salvar Configura\xe7\xf5es'
)

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)
print('Done patching noticias_core.js')
