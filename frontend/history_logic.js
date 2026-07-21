// history_logic.js - Lógica para a Aba de Histórico de Roteiros

let historyState = {
    scripts: [],
    expandedId: null,
    ttsPlaying: null,
    synth: window.speechSynthesis || null
};

document.addEventListener('DOMContentLoaded', () => {
    initHistoryTab();
});

function initHistoryTab() {
    loadHistory();
    renderHistory();

    const clearBtn = document.getElementById('history-clear-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', historyClearAll);
    }
}

function loadHistory() {
    try {
        historyState.scripts = JSON.parse(localStorage.getItem('scripts_history') || '[]');
    } catch(e) {
        historyState.scripts = [];
    }
    // Sort by date descending
    historyState.scripts.sort((a, b) => new Date(b.date) - new Date(a.date));
}

function saveHistory() {
    localStorage.setItem('scripts_history', JSON.stringify(historyState.scripts));
}

function estimateReadingTime(text) {
    if (!text) return '< 1 min';
    const wordCount = text.trim().split(/\s+/).length;
    const minutes = Math.ceil(wordCount / 180); // ~180 words/min spoken
    return `${minutes} min`;
}

function formatDate(dateStr) {
    if (!dateStr) return '—';
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch(e) {
        return dateStr;
    }
}

function getTypeBadge(type) {
    if (!type) return { label: 'Roteiro', color: '#9B59B6', icon: 'fa-pen-nib' };
    const t = type.toLowerCase();
    if (t.includes('short') || t.includes('curto') || t.includes('reels')) {
        return { label: 'Shorts', color: '#E74C3C', icon: 'fa-mobile-alt' };
    }
    if (t.includes('thumb')) {
        return { label: 'Thumbnail', color: '#E67E22', icon: 'fa-image' };
    }
    if (t.includes('longo') || t.includes('long')) {
        return { label: 'Longo', color: '#3498DB', icon: 'fa-film' };
    }
    return { label: 'Roteiro', color: '#9B59B6', icon: 'fa-pen-nib' };
}

function renderHistory() {
    const list = document.getElementById('history-list');
    const empty = document.getElementById('history-empty');
    const countEl = document.getElementById('history-count');

    if (countEl) {
        countEl.textContent = historyState.scripts.length;
    }

    if (historyState.scripts.length === 0) {
        if (empty) empty.style.display = 'flex';
        if (list) list.style.display = 'none';
        return;
    }

    if (empty) empty.style.display = 'none';
    if (!list) return;

    list.style.display = 'flex';
    list.innerHTML = '';

    historyState.scripts.forEach((script, idx) => {
        const badge = getTypeBadge(script.type);
        const isExpanded = historyState.expandedId === script.id;
        const readTime = estimateReadingTime(script.content);

        const card = document.createElement('div');
        card.className = 'news-card';
        card.style.cssText = 'cursor: pointer; transition: all 0.2s;';

        let contentHTML = '';
        if (isExpanded && script.content) {
            // Use marked.js if available
            const rendered = window.marked ? marked.parse(script.content) : `<pre style="white-space:pre-wrap; font-family:'Nunito',sans-serif; color:#cbd5e1; font-size:14px; line-height:1.7; margin:0;">${script.content}</pre>`;
            contentHTML = `
                <div style="margin-top:16px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.1);">
                    <div style="max-height:500px; overflow-y:auto; padding-right:8px; color:#cbd5e1; font-family:'Nunito',sans-serif; font-size:14px; line-height:1.7;">
                        ${rendered}
                    </div>
                </div>
            `;
        }

        card.innerHTML = `
            <div onclick="historyToggleExpand('${script.id}')" style="display:flex; align-items:flex-start; justify-content:space-between; gap:16px;">
                <div style="flex:1; min-width:0;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; flex-wrap:wrap;">
                        <span style="background:${badge.color}; color:#fff; padding:3px 10px; border-radius:12px; font-size:11px; font-weight:700; font-family:'Nunito',sans-serif; display:inline-flex; align-items:center; gap:4px;">
                            <i class="fas ${badge.icon}"></i> ${badge.label}
                        </span>
                        <span style="color:#64748b; font-size:12px; font-family:'Nunito',sans-serif;">
                            <i class="fas fa-calendar-alt" style="margin-right:4px;"></i>${formatDate(script.date)}
                        </span>
                        <span style="color:#64748b; font-size:12px; font-family:'Nunito',sans-serif;">
                            <i class="fas fa-clock" style="margin-right:4px;"></i>${readTime}
                        </span>
                    </div>
                    <h3 style="font-size:16px; font-weight:700; color:#fff; margin:0; font-family:'Nunito',sans-serif; line-height:1.4;">
                        ${script.title || 'Roteiro sem título'}
                    </h3>
                </div>
                <i class="fas fa-chevron-${isExpanded ? 'up' : 'down'}" style="color:#64748b; font-size:14px; margin-top:4px;"></i>
            </div>

            ${contentHTML}

            <div style="display:flex; gap:8px; margin-top:12px; flex-wrap:wrap;" onclick="event.stopPropagation();">
                <button onclick="historyPlayTTS(${idx})" id="history-tts-${idx}" style="padding:8px 14px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; font-family:'Nunito',sans-serif; background:rgba(46,204,113,0.15); color:#2ECC71; transition:0.2s;">
                    🔊 ${historyState.ttsPlaying === idx ? 'Parar' : 'Ouvir'}
                </button>
                <button onclick="historyCopy(${idx})" style="padding:8px 14px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; font-family:'Nunito',sans-serif; background:rgba(52,152,219,0.15); color:#3498DB; transition:0.2s;">
                    📋 Copiar
                </button>
                <button onclick="historyDelete(${idx})" style="padding:8px 14px; border:none; border-radius:6px; cursor:pointer; font-size:12px; font-weight:600; font-family:'Nunito',sans-serif; background:rgba(231,76,60,0.15); color:#E74C3C; transition:0.2s;">
                    🗑️ Excluir
                </button>
            </div>
        `;

        list.appendChild(card);
    });
}

function historyToggleExpand(id) {
    historyState.expandedId = historyState.expandedId === id ? null : id;
    renderHistory();
}

function historyPlayTTS(idx) {
    const script = historyState.scripts[idx];
    if (!script || !script.content) return;

    if (!historyState.synth) {
        showToast('Seu navegador não suporta Text-to-Speech', 'error');
        return;
    }

    // If already playing this one, stop
    if (historyState.ttsPlaying === idx) {
        historyState.synth.cancel();
        historyState.ttsPlaying = null;
        renderHistory();
        return;
    }

    // Stop any existing
    historyState.synth.cancel();

    const utterance = new SpeechSynthesisUtterance(script.content);
    utterance.lang = 'pt-BR';
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    // Try to find a pt-BR voice
    const voices = historyState.synth.getVoices();
    const ptVoice = voices.find(v => v.lang === 'pt-BR') || voices.find(v => v.lang.startsWith('pt'));
    if (ptVoice) utterance.voice = ptVoice;

    utterance.onend = () => {
        historyState.ttsPlaying = null;
        renderHistory();
    };

    utterance.onerror = () => {
        historyState.ttsPlaying = null;
        renderHistory();
    };

    historyState.ttsPlaying = idx;
    historyState.synth.speak(utterance);
    renderHistory();
}

function historyCopy(idx) {
    const script = historyState.scripts[idx];
    if (!script) return;

    const text = script.content || '';
    navigator.clipboard.writeText(text).then(() => {
        showToast('📋 Roteiro copiado!', 'success');
    }).catch(() => {
        showToast('Falha ao copiar', 'error');
    });
}

function historyDelete(idx) {
    if (!confirm('Deseja realmente excluir este roteiro do histórico?')) return;

    // Stop TTS if playing this one
    if (historyState.ttsPlaying === idx && historyState.synth) {
        historyState.synth.cancel();
        historyState.ttsPlaying = null;
    }

    historyState.scripts.splice(idx, 1);
    saveHistory();
    renderHistory();
    showToast('🗑️ Roteiro excluído', 'info');
}

function historyClearAll() {
    if (!confirm('Tem certeza que deseja LIMPAR TODO o histórico? Esta ação não pode ser desfeita.')) return;

    if (historyState.synth) historyState.synth.cancel();
    historyState.scripts = [];
    historyState.ttsPlaying = null;
    historyState.expandedId = null;
    saveHistory();
    renderHistory();
    showToast('🗑️ Histórico limpo completamente', 'info');
}
