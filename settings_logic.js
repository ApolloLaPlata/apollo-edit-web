// settings_logic.js - Lógica para a Aba de Configurações (API Keys & Preferences)

const SETTINGS_AI_KEYS = [
    { key: 'api_key_grok',       label: 'Grok (xAI)',         icon: 'fa-bolt',       color: '#E67E22', testable: true },
    { key: 'openrouter_api_key', label: 'OpenRouter',         icon: 'fa-route',      color: '#9B59B6', testable: false, alias: 'api_key_openrouter' },
    { key: 'api_key_gemini',     label: 'Google Gemini',      icon: 'fa-gem',        color: '#3498DB', testable: false, multi: true },
    { key: 'api_key_pixabay',    label: 'Pixabay',            icon: 'fa-image',      color: '#2ECC71', testable: true },
    { key: 'api_key_pexels',     label: 'Pexels',             icon: 'fa-camera',     color: '#E74C3C', testable: true },
    { key: 'api_key_apify',      label: 'Apify',              icon: 'fa-spider',     color: '#F1C40F', testable: false }
];

const SETTINGS_SOCIAL_KEYS = [
    { key: 'api_key_twitter',    label: 'Twitter/X',          icon: 'fa-twitter',    color: '#1DA1F2' },
    { key: 'api_key_youtube',    label: 'YouTube',            icon: 'fa-youtube',    color: '#FF0000' },
    { key: 'api_key_instagram',  label: 'Instagram',          icon: 'fa-instagram',  color: '#E1306C' },
    { key: 'api_key_facebook',   label: 'Facebook',           icon: 'fa-facebook',   color: '#1877F2' },
    { key: 'api_key_tiktok',     label: 'TikTok',             icon: 'fa-music',      color: '#000000' },
    { key: 'api_key_kwai',       label: 'Kwai',               icon: 'fa-video',      color: '#FF7E29' }
];

const SETTINGS_TONES = [
    { value: 'serio',        label: 'Sério / Jornalístico' },
    { value: 'descontraido', label: 'Descontraído / Bate-papo' },
    { value: 'sarcastico',   label: 'Sarcástico / Irônico' },
    { value: 'comedia',      label: 'Humor / Comédia' },
    { value: 'agressivo',    label: 'Agressivo / Polêmico' },
    { value: 'inspirador',   label: 'Inspirador / Motivacional' }
];

const SETTINGS_ENGINES = [
    { value: 'gemini',     label: 'Google Gemini' },
    { value: 'grok',       label: 'Grok (xAI)' },
    { value: 'openrouter', label: 'OpenRouter' }
];

document.addEventListener('DOMContentLoaded', () => {
    initSettingsTab();
});

function initSettingsTab() {
    renderSettings();
}

function renderSettings() {
    const container = document.getElementById('settings-container');
    if (!container) return;

    container.innerHTML = `
        <!-- AI Models Section -->
        <div class="news-card">
            <h2 style="font-family:'Bangers',cursive; font-size:1.6rem; color:#9B59B6; margin:0 0 6px 0; letter-spacing:2px;">
                <i class="fas fa-robot"></i> Modelos de IA & Imagens
            </h2>
            <p style="color:#64748b; font-family:'Nunito',sans-serif; font-size:13px; margin:0 0 20px 0;">
                Configure suas chaves de API para os serviços de inteligência artificial e busca de imagens.
            </p>
            <div style="display:flex; flex-direction:column; gap:16px;">
                ${SETTINGS_AI_KEYS.map(k => renderKeyRow(k)).join('')}
            </div>
        </div>

        <!-- Social Networks Section -->
        <div class="news-card">
            <h2 style="font-family:'Bangers',cursive; font-size:1.6rem; color:#3498DB; margin:0 0 6px 0; letter-spacing:2px;">
                <i class="fas fa-share-alt"></i> Redes Sociais
            </h2>
            <p style="color:#64748b; font-family:'Nunito',sans-serif; font-size:13px; margin:0 0 20px 0;">
                Chaves de API para integração com redes sociais (scraping, postagem, análise).
            </p>
            <div style="display:flex; flex-direction:column; gap:16px;">
                ${SETTINGS_SOCIAL_KEYS.map(k => renderKeyRow(k)).join('')}
            </div>
        </div>

        <!-- Preferences Section -->
        <div class="news-card">
            <h2 style="font-family:'Bangers',cursive; font-size:1.6rem; color:#2ECC71; margin:0 0 6px 0; letter-spacing:2px;">
                <i class="fas fa-sliders-h"></i> Preferências
            </h2>
            <p style="color:#64748b; font-family:'Nunito',sans-serif; font-size:13px; margin:0 0 20px 0;">
                Personalize o comportamento padrão da Central de Notícias.
            </p>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap:20px;">
                ${renderPreferenceTone()}
                ${renderPreferenceEngine()}
                ${renderPreferenceLanguage()}
                ${renderPreferenceTheme()}
                ${renderPreferenceAutoSave()}
            </div>
        </div>
    `;
}

function renderKeyRow(config) {
    const savedValue = localStorage.getItem(config.key) || '';
    const hasValue = savedValue.length > 0;
    const maskedValue = hasValue ? '•'.repeat(Math.min(savedValue.length, 24)) + savedValue.slice(-4) : '';

    return `
        <div style="display:flex; align-items:center; gap:12px; padding:14px 16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid ${hasValue ? 'rgba(46,204,113,0.3)' : 'rgba(255,255,255,0.1)'}; flex-wrap:wrap;">
            <div style="width:40px; height:40px; border-radius:10px; background:${config.color}22; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                <i class="fab ${config.icon}" style="color:${config.color}; font-size:18px;"></i>
            </div>
            <div style="flex:1; min-width:140px;">
                <label style="display:block; font-family:'Nunito',sans-serif; font-weight:700; font-size:14px; color:#fff; margin-bottom:2px;">
                    ${config.label}
                    ${hasValue ? '<i class="fas fa-check-circle" style="color:#2ECC71; font-size:12px; margin-left:4px;"></i>' : ''}
                </label>
                <span style="font-size:11px; color:#64748b; font-family:'Nunito',sans-serif;">
                    ${hasValue ? maskedValue : 'Não configurada'}
                </span>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <input type="password" id="settings-input-${config.key}" 
                    placeholder="Cole sua chave aqui..." 
                    value="${savedValue}"
                    style="width:220px; padding:8px 12px; background:#2a2a2a; color:#fff; border:1px solid #444; border-radius:6px; font-family:'Nunito',sans-serif; font-size:13px;">
                <button onclick="settingsSaveKey('${config.key}'${config.alias ? ",'" + config.alias + "'" : ''})" 
                    style="padding:8px 14px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:700; font-family:'Nunito',sans-serif; background:#2ECC71; color:#fff; transition:0.2s; white-space:nowrap;">
                    <i class="fas fa-save"></i> Salvar
                </button>
                ${config.testable ? `
                    <button onclick="settingsTestKey('${config.key}')" id="settings-test-${config.key}"
                        style="padding:8px 14px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:700; font-family:'Nunito',sans-serif; background:rgba(52,152,219,0.15); color:#3498DB; transition:0.2s; white-space:nowrap;">
                        <i class="fas fa-vial"></i> Testar
                    </button>
                ` : ''}
            </div>
        </div>
    `;
}

function renderPreferenceTone() {
    const current = localStorage.getItem('setting_tone') || 'serio';
    const options = SETTINGS_TONES.map(t => 
        `<option value="${t.value}" ${current === t.value ? 'selected' : ''}>${t.label}</option>`
    ).join('');

    return `
        <div style="padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.1);">
            <label style="display:block; font-family:'Nunito',sans-serif; font-weight:700; font-size:14px; color:#FFD32A; margin-bottom:8px;">
                <i class="fas fa-microphone-alt"></i> Tom de Voz Padrão
            </label>
            <select onchange="settingsSavePref('setting_tone', this.value)"
                style="width:100%; padding:10px; background:#2a2a2a; color:#fff; border:1px solid #444; border-radius:6px; font-family:'Nunito',sans-serif; font-size:14px;">
                ${options}
            </select>
        </div>
    `;
}

function renderPreferenceEngine() {
    const current = localStorage.getItem('default_engine') || 'gemini';
    const options = SETTINGS_ENGINES.map(e => 
        `<option value="${e.value}" ${current === e.value ? 'selected' : ''}>${e.label}</option>`
    ).join('');

    return `
        <div style="padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.1);">
            <label style="display:block; font-family:'Nunito',sans-serif; font-weight:700; font-size:14px; color:#FFD32A; margin-bottom:8px;">
                <i class="fas fa-brain"></i> Motor de IA Padrão
            </label>
            <select onchange="settingsSavePref('default_engine', this.value)"
                style="width:100%; padding:10px; background:#2a2a2a; color:#fff; border:1px solid #444; border-radius:6px; font-family:'Nunito',sans-serif; font-size:14px;">
                ${options}
            </select>
        </div>
    `;
}

function renderPreferenceLanguage() {
    const current = localStorage.getItem('setting_language') || 'pt-BR';
    return `
        <div style="padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.1);">
            <label style="display:block; font-family:'Nunito',sans-serif; font-weight:700; font-size:14px; color:#FFD32A; margin-bottom:8px;">
                <i class="fas fa-globe"></i> Idioma
            </label>
            <select onchange="settingsSavePref('setting_language', this.value)"
                style="width:100%; padding:10px; background:#2a2a2a; color:#fff; border:1px solid #444; border-radius:6px; font-family:'Nunito',sans-serif; font-size:14px;">
                <option value="pt-BR" ${current === 'pt-BR' ? 'selected' : ''}>Português (Brasil)</option>
                <option value="en" ${current === 'en' ? 'selected' : ''}>English</option>
                <option value="es" ${current === 'es' ? 'selected' : ''}>Español</option>
            </select>
        </div>
    `;
}

function renderPreferenceTheme() {
    const current = localStorage.getItem('setting_theme') || 'dark';
    return `
        <div style="padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.1);">
            <label style="display:block; font-family:'Nunito',sans-serif; font-weight:700; font-size:14px; color:#FFD32A; margin-bottom:8px;">
                <i class="fas fa-palette"></i> Tema Visual
            </label>
            <select onchange="settingsSavePref('setting_theme', this.value)"
                style="width:100%; padding:10px; background:#2a2a2a; color:#fff; border:1px solid #444; border-radius:6px; font-family:'Nunito',sans-serif; font-size:14px;">
                <option value="dark" ${current === 'dark' ? 'selected' : ''}>🌙 Escuro</option>
                <option value="light" ${current === 'light' ? 'selected' : ''}>☀️ Claro</option>
                <option value="auto" ${current === 'auto' ? 'selected' : ''}>🔄 Automático</option>
            </select>
        </div>
    `;
}

function renderPreferenceAutoSave() {
    const current = localStorage.getItem('setting_autoSave') !== 'false'; // default true
    return `
        <div style="padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.1);">
            <label style="display:block; font-family:'Nunito',sans-serif; font-weight:700; font-size:14px; color:#FFD32A; margin-bottom:8px;">
                <i class="fas fa-save"></i> Auto-salvar Roteiros
            </label>
            <div style="display:flex; align-items:center; gap:12px;">
                <button onclick="settingsToggleAutoSave()" id="settings-autosave-btn"
                    style="padding:10px 20px; border:none; border-radius:6px; cursor:pointer; font-size:14px; font-weight:700; font-family:'Nunito',sans-serif; transition:0.2s; background:${current ? '#2ECC71' : 'rgba(255,255,255,0.1)'}; color:${current ? '#fff' : '#94a3b8'};">
                    ${current ? '<i class="fas fa-toggle-on"></i> Ativado' : '<i class="fas fa-toggle-off"></i> Desativado'}
                </button>
                <span style="font-size:12px; color:#64748b; font-family:'Nunito',sans-serif;">
                    Salva roteiros automaticamente no histórico ao gerar
                </span>
            </div>
        </div>
    `;
}

function settingsSaveKey(key, alias) {
    const input = document.getElementById(`settings-input-${key}`);
    if (!input) return;

    const value = input.value.trim();
    if (!value) {
        localStorage.removeItem(key);
        if (alias) localStorage.removeItem(alias);
        showToast(`🗑️ Chave ${key} removida`, 'info');
    } else {
        localStorage.setItem(key, value);
        if (alias) localStorage.setItem(alias, value);
        showToast(`✅ Chave salva com sucesso!`, 'success');
    }
    renderSettings();
}

function settingsSavePref(key, value) {
    localStorage.setItem(key, value);
    showToast('✅ Preferência salva!', 'success');
}

function settingsToggleAutoSave() {
    const current = localStorage.getItem('setting_autoSave') !== 'false';
    localStorage.setItem('setting_autoSave', (!current).toString());
    renderSettings();
    showToast(current ? 'Auto-salvar desativado' : 'Auto-salvar ativado', 'info');
}

async function settingsTestKey(key) {
    const btn = document.getElementById(`settings-test-${key}`);
    const value = localStorage.getItem(key) || '';

    if (!value) {
        showToast('⚠️ Salve a chave primeiro', 'error');
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }

    try {
        let ok = false;

        if (key === 'api_key_grok') {
            const res = await fetch('/api/grok/models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: value })
            });
            ok = res.ok;
        } else if (key === 'api_key_pixabay') {
            const res = await fetch(`https://pixabay.com/api/?key=${value}&q=test&per_page=3`);
            const data = await res.json();
            ok = !data.error && data.totalHits !== undefined;
        } else if (key === 'api_key_pexels') {
            const res = await fetch('https://api.pexels.com/v1/search?query=test&per_page=1', {
                headers: { 'Authorization': value }
            });
            ok = res.ok;
        }

        if (ok) {
            showToast('✅ Chave válida! Conexão OK.', 'success');
            if (btn) btn.innerHTML = '<i class="fas fa-check" style="color:#2ECC71;"></i> OK';
        } else {
            showToast('❌ Chave inválida ou sem permissão.', 'error');
            if (btn) btn.innerHTML = '<i class="fas fa-times" style="color:#E74C3C;"></i> Falhou';
        }
    } catch (err) {
        showToast('❌ Erro ao testar: ' + err.message, 'error');
        if (btn) btn.innerHTML = '<i class="fas fa-times" style="color:#E74C3C;"></i> Erro';
    }

    setTimeout(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-vial"></i> Testar';
        }
    }, 3000);
}
