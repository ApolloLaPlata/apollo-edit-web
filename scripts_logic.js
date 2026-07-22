
window.ApolloAlert = function(msg) {
    if (typeof showToast === 'function') {
        showToast(msg, 'info');
    } else {
        alert(msg);
    }
};
// scripts_logic.js - Lógica para a Aba de Roteiros

let scriptsProfiles = [];
let activeScriptsProfileId = '';

document.addEventListener('DOMContentLoaded', () => {
    loadScriptsProfiles();
    updateScriptsGenerateBtn();
    loadAIModels();

    // Check for cross-page prefill data
    const prefill = window.readPrefill ? window.readPrefill('scripts_prefill') : null;
    if (prefill) {
        if (prefill.text) {
            const topicEl = document.getElementById('scripts-topic');
            if (topicEl) {
                topicEl.value = prefill.text;
                if (typeof updateScriptsGenerateBtn === 'function') updateScriptsGenerateBtn();
            }
        }
        if (prefill.profileId) {
            const profileSelect = document.getElementById('scripts-profile-select');
            if (profileSelect) {
                profileSelect.value = prefill.profileId;
                if (typeof switchScriptsProfile === 'function') {
                    switchScriptsProfile(prefill.profileId);
                } else {
                    activeScriptsProfileId = prefill.profileId;
                }
            } else {
                activeScriptsProfileId = prefill.profileId;
            }
        }
    }
});

function loadScriptsProfiles() {
    const saved = localStorage.getItem('channel_profiles');
    if (saved) {
        try {
            scriptsProfiles = JSON.parse(saved);
            if (scriptsProfiles.length > 0 && !activeScriptsProfileId) {
                activeScriptsProfileId = scriptsProfiles[0].id;
            }
        } catch (e) {
            console.error('Error parsing profiles', e);
            scriptsProfiles = [];
        }
    }
    renderScriptsProfiles();
    renderScriptsProfileSelect();
}

async function loadAIModels() {
    try {
        const res = await fetch('https://api.apolloedit.com/api/public/models_pricing');
        const data = await res.json();
        if(data.success) {
            const select = document.getElementById('scripts-ai-engine');
            if(!select) return;
            
            // Keep the first default option
            const defaultOpt = select.options[0];
            select.innerHTML = '';
            select.appendChild(defaultOpt);
            
            data.models.forEach(m => {
                if(m.tier === 'Premium') {
                    const opt = document.createElement('option');
                    opt.value = m.model_id;
                    const estimatedCost = ((m.input_price_per_1m * 0.002) + (m.output_price_per_1m * 0.002)).toFixed(4); // Rough estimate for a script in $
                    const marginCost = (parseFloat(estimatedCost) * 1.3).toFixed(4); // 30% margin
                    const gasCost = Math.ceil(parseFloat(marginCost) * 100); // converting cents to gas
                    opt.textContent = `🧠 ${m.provider} - ${m.model_id} (Est. Custo: ~${gasCost || 1} Gas)`;
                    select.appendChild(opt);
                }
            });
        }
    } catch(e) { console.error('Error loading AI models:', e); }
}

function saveScriptsProfiles() {
    localStorage.setItem('channel_profiles', JSON.stringify(scriptsProfiles));
    renderScriptsProfiles();
    renderScriptsProfileSelect();
}

function renderScriptsProfileSelect() {
    const select = document.getElementById('scripts-profile-select');
    if (!select) return;
    
    select.innerHTML = '<option value="">Sem perfil específico (Genérico)</option>';
    
    scriptsProfiles.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.textContent = p.name;
        if (p.id === activeScriptsProfileId) {
            option.selected = true;
        }
        select.appendChild(option);
    });
    
    select.onchange = (e) => {
        activeScriptsProfileId = e.target.value;
    };
}

function toggleScriptsProfileForm(show) {
    const form = document.getElementById('scripts-profile-form');
    if (form) {
        form.style.display = show ? 'flex' : 'none';
        if (show) {
            document.getElementById('scripts-profile-name').value = '';
            document.getElementById('scripts-profile-desc').value = '';
            document.getElementById('scripts-profile-files-list').innerHTML = '';
            document.getElementById('scripts-profile-files').value = '';
        }
    }
}

let pendingProfileFiles = [];

function handleScriptsProfileFiles(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    pendingProfileFiles = [];
    const list = document.getElementById('scripts-profile-files-list');
    list.innerHTML = '';
    
    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            pendingProfileFiles.push({
                name: file.name,
                content: e.target.result
            });
            
            const li = document.createElement('li');
            li.style.cssText = 'display: flex; align-items: center; justify-content: space-between; background: #2a2a2a; padding: 6px 10px; border-radius: 6px; border: 1px solid #444; font-size: 12px;';
            li.innerHTML = `
                <span style="display: flex; align-items: center; gap: 6px; color: #cbd5e1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    <i class="fas fa-file-alt" style="color: #4f46e5;"></i> ${file.name}
                </span>
                <i class="fas fa-check-circle" style="color: #10b981;"></i>
            `;
            list.appendChild(li);
        };
        reader.readAsText(file);
    });
}

function saveScriptsProfile() {
    const nameInput = document.getElementById('scripts-profile-name');
    const descInput = document.getElementById('scripts-profile-desc');
    
    const name = nameInput.value.trim();
    if (!name) {
        window.ApolloAlert("O nome do perfil é obrigatório.");
        return;
    }
    
    const newProfile = {
        id: 'prof_' + Date.now().toString(),
        name: name,
        description: descInput.value.trim(),
        files: pendingProfileFiles
    };
    
    scriptsProfiles.push(newProfile);
    activeScriptsProfileId = newProfile.id;
    saveScriptsProfiles();
    toggleScriptsProfileForm(false);
}

function deleteScriptsProfile(id) {
    if(confirm("Tem certeza que deseja excluir este perfil?")) {
        scriptsProfiles = scriptsProfiles.filter(p => p.id !== id);
        if (activeScriptsProfileId === id) {
            activeScriptsProfileId = scriptsProfiles.length > 0 ? scriptsProfiles[0].id : '';
        }
        saveScriptsProfiles();
    }
}

function renderScriptsProfiles() {
    const container = document.getElementById('scripts-profiles-list');
    if (!container) return;
    
    if (scriptsProfiles.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 24px 16px; border: 2px dashed #444; border-radius: 8px; color: #94a3b8;">
                <i class="fas fa-users fa-2x" style="margin-bottom: 8px; opacity: 0.5;"></i>
                <p style="font-size: 14px; margin: 0;">Nenhum perfil cadastrado.</p>
                <p style="font-size: 12px; margin: 4px 0 0 0;">Crie um perfil para gerar roteiros mais autênticos.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    scriptsProfiles.forEach(p => {
        const div = document.createElement('div');
        div.style.cssText = `background: ${p.id === activeScriptsProfileId ? 'rgba(79,70,229,0.15)' : '#1e1e1e'}; border: 1px solid ${p.id === activeScriptsProfileId ? '#6366f1' : '#333'}; border-radius: 8px; padding: 12px; transition: all 0.2s;`;
        div.innerHTML = `
            <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px;">
                <div>
                    <h4 style="font-size: 14px; font-weight: 600; color: #fff; margin: 0 0 2px 0;">${p.name}</h4>
                    ${p.description ? `<p style="font-size: 12px; color: #94a3b8; margin: 0;">${p.description}</p>` : ''}
                </div>
                <button onclick="deleteScriptsProfile('${p.id}')" style="background: none; border: none; color: #a1a1aa; cursor: pointer; padding: 4px; border-radius: 4px;" onmouseover="this.style.color='#ef4444'; this.style.background='#fee2e2';" onmouseout="this.style.color='#a1a1aa'; this.style.background='none';">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
            <div style="font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 4px;">
                <i class="fas fa-database" style="color: #4f46e5;"></i> ${p.files ? p.files.length : 0} arquivos de base
            </div>
        `;
        container.appendChild(div);
    });
}

function updateScriptsGenerateBtn() {
    const topic = document.getElementById('scripts-topic').value.trim();
    const btn = document.getElementById('scripts-generate-btn');
    const btnShorts = document.getElementById('scripts-generate-shorts-btn');
    const btnThumb = document.getElementById('scripts-generate-thumb-btn');
    const clearBtn = document.getElementById('scripts-clear-topic-btn');
    
    if (clearBtn) clearBtn.style.display = topic ? 'block' : 'none';
    
    const setBtnState = (b, enabled) => {
        if (b) {
            b.disabled = !enabled;
            b.style.opacity = enabled ? '1' : '0.5';
            b.style.cursor = enabled ? 'pointer' : 'not-allowed';
        }
    };
    
    setBtnState(btn, !!topic);
    setBtnState(btnShorts, !!topic);
    setBtnState(btnThumb, !!topic);
}

async function handleGenerateScriptCustom() {
    const topic = document.getElementById('scripts-topic').value.trim();
    const modality = document.getElementById('scripts-modality').value;
    const tone = document.getElementById('scripts-tone').value;
    const profileId = document.getElementById('scripts-profile-select').value;
    
    if (!topic) return;
    
    const btn = document.getElementById('scripts-generate-btn');
    const originalBtnHTML = btn.innerHTML;
    
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando Roteiro...';
    btn.style.opacity = '0.7';
    
    const resultContainer = document.getElementById('scripts-result-container');
    const outputDiv = document.getElementById('scripts-output');
    
    resultContainer.style.display = 'block';
    outputDiv.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;padding:40px;color:#8b5cf6;"><i class="fas fa-circle-notch fa-spin fa-2x"></i></div>';
    outputDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    let profileContext = '';
    if (profileId) {
        const p = scriptsProfiles.find(x => x.id === profileId);
        if (p) {
            profileContext = `Perfil: ${p.name}\nDescrição: ${p.description || ''}\n`;
            if (p.files && p.files.length > 0) {
                profileContext += `\n--- MATERIAIS DE REFERÊNCIA (Para clonar o estilo) ---\n`;
                p.files.forEach(f => {
                    profileContext += `\nArquivo: ${f.name}\n${f.content}\n`;
                });
            }
        }
    }
    
    let tonePrompt = '';
    if (tone === 'perfil') {
        tonePrompt = profileId ? 'Use EXATAMENTE o tom de voz e estilo demonstrados nos textos de referência do perfil.' : 'Use um tom natural e engajador.';
    } else {
        const tones = {
            'sarcastico': 'Use um tom Sarcástico e Irônico: Faça piadas ácidas, deboche da situação (quando apropriado), use humor inteligente e não tenha medo de ser um pouco cínico.',
            'comedia': 'Use um tom de Humor e Comédia: Faça o espectador rir, use analogias engraçadas, exagere nas reações e mantenha a energia lá em cima.',
            'agressivo': 'Use um tom Agressivo e Polêmico: Seja incisivo, direto, critique sem dó, mostre indignação e não tenha papas na língua. Fale verdades duras.',
            'serio': 'Use um tom Sério e Jornalístico: Focado nos fatos, imparcial, com linguagem formal, credibilidade e análise profunda.',
            'descontraido': 'Use um tom Descontraído e Bate-papo: Como se estivesse conversando com um amigo no bar. Use gírias leves, seja muito próximo do público e relaxado.',
            'inspirador': 'Use um tom Inspirador e Motivacional: Focado em superação, lições de vida, energia positiva e em fazer o espectador se sentir capaz de tudo.'
        };
        tonePrompt = tones[tone] || tones['serio'];
    }
    
    let modalityPrompt = '';
    const modalities = {
        'longo': 'Formato: Vídeo Longo Padrão (8 a 12 minutos). Estrutura: Gancho forte inicial, introdução do tema, desenvolvimento aprofundado com exemplos, e chamada para ação (CTA) no final.',
        'curto': 'Formato: Vídeo Curto (3 a 5 minutos). Estrutura: Gancho rápido, direto ao ponto, sem enrolação, desenvolvimento focado no essencial, e CTA rápido.',
        'shorts': 'Formato: Shorts/TikTok/Reels (até 60 segundos). Estrutura: Gancho ABSURDO nos primeiros 3 segundos, ritmo frenético, sem enrolação, frases curtas, e CTA rápido no final.',
        'corte': 'Formato: Corte Estilo Podcast (1 a 3 minutos). Estrutura: Inicia no meio de um raciocínio forte ou polêmico, desenvolve o argumento principal, e termina com uma reflexão ou punchline.',
        'documentario': 'Formato: Documentário/Ensaio de Vídeo. Estrutura: Tom investigativo, narrativa envolvente, contexto histórico ou aprofundado, divisão em capítulos ou atos, e conclusão reflexiva.',
        'noticias': 'Formato: Notícias/Jornalismo. Estrutura: Manchete impactante, resumo do fato (o que, quem, quando, onde, por que), desdobramentos, e encerramento.',
        'review': 'Formato: Review de Produto. Estrutura: Gancho sobre o produto, unboxing ou primeiras impressões, prós e contras detalhados, veredito final e CTA de compra.',
        'tutorial': 'Formato: Tutorial / Passo a Passo. Estrutura: Explicação do problema, os passos lógicos e claros para resolver, dicas extras e CTA.',
        'storytelling': 'Formato: Storytelling / Relato Pessoal. Estrutura: O estado inicial (situação problema), o evento incitante, a jornada/luta, o clímax e a resolução/lição aprendida.'
    };
    modalityPrompt = modalities[modality] || modalities['longo'];
    
    const finalInstructions = `Tema/Instruções Gerais: ${topic}\n\nREGRAS DE FORMATAÇÃO E TOM DE VOZ:\n- ${modalityPrompt}\n- ${tonePrompt}\n\nCrie o roteiro baseando-se estritamente nestas diretrizes. Inclua rubricas visuais (ex: [Corta para B-roll de...]) se apropriado.`;

    try {
        const engineSelect = document.getElementById('scripts-ai-engine');
        const engineValue = engineSelect ? engineSelect.value : 'auto';

        const response = await fetch('https://api.apolloedit.com/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(buildNoticiasBody({
                prompt_type: 'gerar-roteiro',
                input_text: finalInstructions,
                profile_context: profileContext,
                model_choice: engineValue
            }))
        });

        if (!response.ok) {
            throw new Error(`Erro: ${response.status}`);
        }

        const data = await response.json();
        
        // Remove simple markdown markers
        let cleanText = data.text.replace(/```markdown\n?/g, '').replace(/```\n?/g, '').trim();
        
        outputDiv.innerHTML = window.marked ? marked.parse(cleanText) : `<pre style="white-space: pre-wrap; font-family: inherit;">${cleanText}</pre>`;
        outputDiv.setAttribute('data-raw', cleanText);
    } catch (err) {
        outputDiv.innerHTML = `<div style="color: #ef4444;"><i class="fas fa-exclamation-triangle"></i> Falha ao gerar roteiro: ${err.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalBtnHTML;
        btn.style.opacity = '1';
    }
}

async function handleGenerateShortsScript() {
    await runSimpleScriptPrompt('gerar-shorts', 'scripts-generate-shorts-btn', '<i class="fas fa-mobile-alt"></i> Shorts');
}

async function handleGenerateThumbnails() {
    await runSimpleScriptPrompt('ideias-thumbnails', 'scripts-generate-thumb-btn', '<i class="fas fa-image"></i> Thumbnails');
}

async function runSimpleScriptPrompt(promptType, btnId, originalHtml) {
    const topic = document.getElementById('scripts-topic').value.trim();
    if (!topic) return;
    
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        btn.style.opacity = '0.7';
    }
    
    const resultContainer = document.getElementById('scripts-result-container');
    const outputDiv = document.getElementById('scripts-output');
    
    resultContainer.style.display = 'block';
    outputDiv.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;padding:40px;color:#8b5cf6;"><i class="fas fa-circle-notch fa-spin fa-2x"></i></div>';
    outputDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    try {
        const response = await fetch('https://api.apolloedit.com/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt_type: promptType,
                input_text: topic,
                engine: localStorage.getItem('default_engine') || 'gemini',
                api_key_or: localStorage.getItem('openrouter_api_key') || '',
                api_key_grok: localStorage.getItem('api_key_grok') || ''
            })
        });

        if (!response.ok) throw new Error(`Erro: ${response.status}`);
        
        const data = await response.json();
        let cleanText = (data.content || data.text || '').replace(/```markdown\n?/g, '').replace(/```\n?/g, '').trim();
        
        outputDiv.innerHTML = window.marked ? marked.parse(cleanText) : `<pre style="white-space: pre-wrap; font-family: inherit;">${cleanText}</pre>`;
        outputDiv.setAttribute('data-raw', cleanText);
    } catch (err) {
        outputDiv.innerHTML = `<div style="color: #ef4444;"><i class="fas fa-exclamation-triangle"></i> Falha: ${err.message}</div>`;
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
            btn.style.opacity = '1';
        }
    }
}

function copyCustomScript() {
    const outputDiv = document.getElementById('scripts-output');
    const text = outputDiv.getAttribute('data-raw') || outputDiv.innerText;
    
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('scripts-copy-btn');
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check" style="color:#10b981;"></i> Copiado!';
        setTimeout(() => {
            btn.innerHTML = originalHtml;
        }, 2000);
    });
}

function downloadCustomScriptTXT() {
    const outputDiv = document.getElementById('scripts-output');
    const text = outputDiv.getAttribute('data-raw') || outputDiv.innerText;
    if (!text) return;
    
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `roteiro_${new Date().getTime()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}
