
window.ApolloAlert = function(msg) {
    if (typeof showToast === 'function') {
        showToast(msg, 'info');
    } else {
        alert(msg);
    }
};
// strategy_logic.js - Lógica para a Aba de Estratégia do Canal

let activeStrategyProfileId = '';

document.addEventListener('DOMContentLoaded', () => {
    // Escuta evento customizado de quando os perfis são carregados/atualizados
    // Como os perfis vêm de scripts_logic.js, faremos um fallback com intervalo ou chamaremos init
    setTimeout(initStrategyTab, 500);
});

function initStrategyTab() {
    renderStrategyProfileSelect();
}

function renderStrategyProfileSelect() {
    const select = document.getElementById('strategy-profile-select');
    if (!select) return;
    
    select.innerHTML = '<option value="">-- Selecione um Canal --</option>';
    
    // scriptsProfiles vem do scripts_logic.js (compartilhado globalmente)
    if (typeof scriptsProfiles !== 'undefined') {
        scriptsProfiles.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = p.name;
            select.appendChild(option);
        });
    }
}

function getActiveStrategyProfile() {
    if (typeof scriptsProfiles === 'undefined') return null;
    return scriptsProfiles.find(p => p.id === activeStrategyProfileId);
}

function loadStrategyProfileContext() {
    const select = document.getElementById('strategy-profile-select');
    activeStrategyProfileId = select.value;
    
    const infoBox = document.getElementById('strategy-profile-info');
    const descSpan = document.getElementById('strategy-profile-desc');
    
    const profile = getActiveStrategyProfile();
    if (profile) {
        infoBox.style.display = 'block';
        descSpan.textContent = profile.description || 'Sem descrição.';
        renderStrategyCompetitors();
    } else {
        infoBox.style.display = 'none';
        document.getElementById('strategy-competitors-list').innerHTML = '';
    }
}

function renderStrategyCompetitors() {
    const list = document.getElementById('strategy-competitors-list');
    list.innerHTML = '';
    
    const profile = getActiveStrategyProfile();
    if (!profile) return;
    
    if (!profile.competitors) {
        profile.competitors = [];
    }
    
    if (profile.competitors.length === 0) {
        list.innerHTML = '<li style="font-size: 12px; color: #9ca3af; text-align: center; padding: 8px;">Nenhum concorrente adicionado.</li>';
        return;
    }
    
    profile.competitors.forEach((comp, idx) => {
        const li = document.createElement('li');
        li.style.cssText = 'display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; font-size: 14px;';
        li.innerHTML = `
            <span style="color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 80%;">${comp}</span>
            <button onclick="removeStrategyCompetitor(${idx})" style="background: none; border: none; color: #9ca3af; cursor: pointer; transition: color 0.2s;" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#9ca3af'">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;
        list.appendChild(li);
    });
}

function addStrategyCompetitor() {
    const input = document.getElementById('strategy-competitor-input');
    const val = input.value.trim();
    if (!val) return;
    
    const profile = getActiveStrategyProfile();
    if (!profile) {
        window.ApolloAlert("Selecione um canal primeiro.");
        return;
    }
    
    if (!profile.competitors) profile.competitors = [];
    profile.competitors.push(val);
    
    // Salvar globalmente
    if (typeof saveScriptsProfiles === 'function') saveScriptsProfiles();
    
    input.value = '';
    renderStrategyCompetitors();
}

function removeStrategyCompetitor(index) {
    const profile = getActiveStrategyProfile();
    if (!profile || !profile.competitors) return;
    
    profile.competitors.splice(index, 1);
    
    // Salvar globalmente
    if (typeof saveScriptsProfiles === 'function') saveScriptsProfiles();
    
    renderStrategyCompetitors();
}

async function generateStrategy() {
    const profile = getActiveStrategyProfile();
    if (!profile) {
        window.ApolloAlert("Selecione um canal primeiro!");
        return;
    }
    
    const btn = document.getElementById('btn-generate-strategy');
    const originalBtnHtml = btn.innerHTML;
    
    btn.disabled = true;
    btn.style.opacity = '0.7';
    btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Analisando Mercado...';
    
    const container = document.getElementById('strategy-results-container');
    const list = document.getElementById('strategy-ideas-list');
    
    container.style.display = 'flex';
    list.innerHTML = '<div style="text-align: center; padding: 40px; color: #8b5cf6;"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';
    
    const competitorsList = profile.competitors && profile.competitors.length > 0 
        ? profile.competitors.join(', ') 
        : 'Nenhum concorrente especificado';

    const inputContext = `Canal: ${profile.name}\nNicho: ${profile.description}\nConcorrentes: ${competitorsList}`;

    try {
        const response = await fetch('https://api.apolloedit.com/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(buildNoticiasBody({
                prompt_type: 'gerar-estrategia',
                input_text: inputContext
            }))
        });

        if (!response.ok) throw new Error(`Erro API: ${response.status}`);
        
        const data = await response.json();
        
        // Retira os delimitadores markdown se houver
        let cleanText = data.text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
        const ideas = JSON.parse(cleanText);
        
        list.innerHTML = '';
        
        ideas.forEach((idea, i) => {
            let urgencyColor = '#059669'; // Emerald
            let urgencyBg = '#ecfdf5';
            if (idea.urgency === 'Alta') {
                urgencyColor = '#b91c1c'; // Red
                urgencyBg = '#fef2f2';
            } else if (idea.urgency === 'Média' || idea.urgency === 'Media') {
                urgencyColor = '#b45309'; // Amber
                urgencyBg = '#fffbeb';
            }
            
            const card = document.createElement('div');
            card.style.cssText = 'background: #1e1e1e; border-radius: 12px; border: 1px solid #333; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: border-color 0.2s;';
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 12px;">
                    <h4 style="font-size: 18px; font-weight: 700; color: #fff; margin: 0; line-height: 1.3;">${idea.title}</h4>
                    <span style="background: ${urgencyBg}; color: ${urgencyColor}; font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; white-space: nowrap;">Urgência ${idea.urgency}</span>
                </div>
                
                <div style="display: flex; flex-direction: column; gap: 12px; font-size: 14px;">
                    <div style="display: flex; gap: 8px; align-items: flex-start;">
                        <i class="fas fa-exclamation-circle" style="color: #8b5cf6; margin-top: 4px;"></i>
                        <div>
                            <strong style="color: #fff; display: block;">Por que fazer agora?</strong>
                            <span style="color: #94a3b8;">${idea.whyNow}</span>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 8px; align-items: flex-start;">
                        <i class="fas fa-crosshairs" style="color: #059669; margin-top: 4px;"></i>
                        <div>
                            <strong style="color: #fff; display: block;">Seu ângulo único:</strong>
                            <span style="color: #94a3b8;">${idea.angle}</span>
                        </div>
                    </div>
                    
                    <div style="display: flex; gap: 8px; align-items: flex-start; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border: 1px solid #333;">
                        <i class="fas fa-eye" style="color: #ef4444; margin-top: 4px;"></i>
                        <div>
                            <strong style="color: #fff; display: block; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Contexto da Concorrência</strong>
                            <span style="color: #94a3b8; font-size: 13px;">${idea.competitorContext}</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #333; display: flex; justify-content: flex-end;">
                    <button onclick="sendToScriptsTab('${encodeURIComponent(idea.title)}')" style="background: none; border: none; color: #8b5cf6; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: color 0.2s;" onmouseover="this.style.color='#7c3aed'" onmouseout="this.style.color='#8b5cf6'">
                        Criar Roteiro para este Vídeo <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            `;
            list.appendChild(card);
        });

    } catch (err) {
        list.innerHTML = `<div style="background: #fef2f2; border: 1px solid #fee2e2; border-radius: 8px; padding: 16px; color: #b91c1c; font-size: 14px;"><i class="fas fa-exclamation-triangle"></i> Erro: ${err.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerHTML = originalBtnHtml;
    }
}

function sendToScriptsTab(encodedTitle) {
    const title = decodeURIComponent(encodedTitle);
    
    // We can also pass the profile id if needed, but the current prefill logic only reads 'text'.
    // We will expand it to also read 'profileId' if you want, but for now we just pass 'text'.
    localStorage.setItem('scripts_prefill', JSON.stringify({
        text: title,
        profileId: activeStrategyProfileId || null
    }));
    window.location.href = 'noticias_scripts.html';
}
