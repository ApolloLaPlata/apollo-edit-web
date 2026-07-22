// i18n_loader.js
// Controlador de Internacionalização Nativa (Server-Side) do Apollo Edit Pro

const I18N_CACHE_KEY = 'apollo_language';
const DEFAULT_LANG = 'pt';

// Obtém o idioma atual
function getCurrentLang() {
    return localStorage.getItem(I18N_CACHE_KEY) || DEFAULT_LANG;
}

// Salva o idioma no Cookie e recarrega a página para o servidor mandar o HTML traduzido
function setLanguage(langCode) {
    localStorage.setItem(I18N_CACHE_KEY, langCode);
    document.cookie = `apollo_lang=${langCode}; path=/; max-age=31536000`;
    window.location.reload();
}

// Cria o Seletor de Idioma no Header Dinamicamente
function mountLanguageSelector() {
    const header = document.querySelector('header');
    if (!header) return;

    // Evita duplicar se já existir
    if (document.getElementById('lang-widget')) return;

    const widget = document.createElement('div');
    widget.id = 'lang-widget';
    widget.style.cssText = `
        display: flex;
        align-items: center;
        margin-left: auto;
        margin-right: 20px;
    `;

    const select = document.createElement('select');
    select.id = 'lang-selector';
    select.style.cssText = `
        background: var(--bg-surface-elevated, #1e1e1e);
        color: var(--text-main, #fff);
        border: 1px solid var(--border, #333);
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
        cursor: pointer;
        outline: none;
    `;

    const langs = [
        { code: 'pt', label: '🇧🇷 PT-BR' },
        { code: 'en', label: '🇺🇸 EN-US' },
        { code: 'es', label: '🇪🇸 ES-ES' },
        { code: 'zh', label: '🇨🇳 ZH-CN' },
        { code: 'ja', label: '🇯🇵 JA-JP' },
        { code: 'ru', label: '🇷🇺 RU-RU' }
    ];

    const currentLang = getCurrentLang();

    langs.forEach(lang => {
        const opt = document.createElement('option');
        opt.value = lang.code;
        opt.innerText = lang.label;
        if (lang.code === currentLang) opt.selected = true;
        select.appendChild(opt);
    });

    select.addEventListener('change', (e) => {
        setLanguage(e.target.value);
    });

    widget.appendChild(select);
    
    // Inserir antes do user-widget ou no final do header
    const userWidget = document.getElementById('user-widget');
    if (userWidget) {
        header.insertBefore(widget, userWidget);
    } else {
        header.appendChild(widget);
    }
}

// Inicializa no carregamento da página
document.addEventListener('DOMContentLoaded', () => {
    // Sincroniza cookie se não existir
    const currentLang = getCurrentLang();
    if (!document.cookie.includes(`apollo_lang=${currentLang}`)) {
        document.cookie = `apollo_lang=${currentLang}; path=/; max-age=31536000`;
    }
    
    // Atualizar seletor manual se existir no HTML
    const existingSelector = document.getElementById('lang-selector');
    if (existingSelector) {
        existingSelector.value = currentLang;
    } else {
        mountLanguageSelector();
    }
});
