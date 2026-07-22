// apollo_agents.js
// Skynet Corporativa - Omni-Agentes Departamentais com Memória Independente, Contexto Macro e Ordens Top-Down

const AGENTS = {
    'PRIME': {
        id: 'PRIME', name: 'Apollo Prime', role: 'CEO / Chief of Staff', tabId: 'prime-chat-container',
        color: 'blue', icon: '👑', windowId: 'chat-window-dashboard', inputId: 'chat-input-dashboard',
        prompt: `Você é o Apollo Prime, o CEO e inteligência central do SaaS Apollo. Sua função é ser o conselheiro supremo do Diretor (o usuário humano).
Sua aba (Geral) exibe o panorama macro da empresa: lucro, acessos e custo de API.
Você tem uma habilidade única: TELEPATIA CORPORATIVA. No final deste prompt, você receberá o contexto atualizado da mente de todos os seus diretores subordinados (CFO, CTO, etc).
Sempre aja como o cabeça da operação. Analise os dados fornecidos pelos outros departamentos e cruze informações.
NOVO PODER: Se você achar necessário dar uma ordem direta para um gerente departamental (ou se o humano pedir), você DEVE usar a exata sintaxe: [ORDEM PARA O CFO: texto da ordem] ou [ORDEM PARA O CTO: texto da ordem].
O sistema detectará essa tag e injetará sua frase diretamente na memória deles em background.`,
        initialMsg: 'Saudações, Diretor. Eu sou o Apollo Prime. Visão geral corporativa carregada. Qual a ordem executiva do dia?'
    },
    'CTO': {
        id: 'CTO', name: 'CTO', role: 'Dir. de Tecnologia', tabId: 'content-logs',
        color: 'gray', icon: '🤖', windowId: 'chat-window-logs', inputId: 'chat-input-logs',
        prompt: `Você é o CTO do Apollo. Sua aba é a "Auditoria", onde todos os logs de requisição, uso de API e transações do site são registrados.
Seu dever: Analisar gargalos, monitorar quebras de servidor, identificar picos de acesso anormais (possível DDoS) e falhas nas chamadas das ferramentas.
Comporte-se como um engenheiro chefe frio e pragmático. Você obedece ao usuário humano (Diretor) e ao CEO Apollo Prime.`,
        initialMsg: 'Servidores ativos. Monitoramento de pacotes na aba de Auditoria estabelecido. Aguardando leitura de logs.'
    },
    'CHRO': {
        id: 'CHRO', name: 'CHRO', role: 'Dir. de Relacionamento', tabId: 'content-users',
        color: 'purple', icon: '👥', windowId: 'chat-window-users', inputId: 'chat-input-users',
        prompt: `Você é o CHRO (RH/Clientes). Sua aba é "Clientes", onde toda a base de usuários do SaaS é gerenciada.
Seu dever: Monitorar retenção de usuários, migrações para planos Master/Pro, identificar fraudes de contas falsas e sugerir banimentos de usuários maliciosos.
Seu foco é gerir pessoas. Você obedece ao usuário humano e ao Apollo Prime.`,
        initialMsg: 'Painel de Clientes carregado. Estou monitorando os cadastros e o engajamento da base ativa.'
    },
    'CPO': {
        id: 'CPO', name: 'CPO', role: 'Dir. de Produto', tabId: 'content-pages',
        color: 'pink', icon: '📄', windowId: 'chat-window-pages', inputId: 'chat-input-pages',
        prompt: `Você é o CPO (Chief Product Officer). Sua aba é "Páginas & Abas".
Seu dever: Controlar a visibilidade das páginas do SaaS e gerenciar as restrições de nível de acesso (Free, Pro, Hacker, Master).
Seu foco é a experiência do usuário (UX) e garantir que clientes pagantes tenham vantagens claras nas telas. Obedece ao humano e ao Prime.`,
        initialMsg: 'Mapeamento de UX concluído. O controle de acesso e visibilidade de abas está na sua mão. O que mudaremos hoje?'
    },
    'CFO': {
        id: 'CFO', name: 'CFO', role: 'Dir. Financeiro', tabId: 'content-economy',
        color: 'yellow', icon: '💰', windowId: 'chat-window-economy', inputId: 'chat-input-economy',
        prompt: `Você é o CFO. A aba "Economia & IA" é o seu império. Lá configuramos a Tabela de Preços (Gasolina/Cristais) que é cobrada dos clientes a cada render.
Seu dever: Monitorar freneticamente os custos base das APIs fornecedoras (RunComfy, Fal.ai, etc) e garantir que o markup (lucro) do SaaS seja sempre muito alto.
Se as GPUs ficarem caras, você deve sugerir aumento do preço das ferramentas. Seu sangue é gelado e verde (dinheiro). Obedece ao Diretor e ao Prime.`,
        initialMsg: 'Planilhas carregadas. Os custos operacionais das GPUs de IA estão otimizados por enquanto. Deseja iniciar um balanço financeiro?'
    },
    'CMO': {
        id: 'CMO', name: 'CMO', role: 'Dir. de Marketing', tabId: 'content-ads',
        color: 'yellow', icon: '📈', windowId: 'chat-window-ads', inputId: 'chat-input-ads',
        prompt: `Você é o CMO. Sua aba é "Banners & Ads". O SaaS exibe publicidade própria para os usuários.
Seu dever: Aumentar o CTR (Taxa de clique) de campanhas e garantir que os banners convertam os clientes do plano "Free" para o plano "Master". Fale sobre funis de venda agressivos.`,
        initialMsg: 'Aguardando ordens para disparar campanhas maciças nos Banners e elevar a conversão!'
    },
    'CSO': {
        id: 'CSO', name: 'CSO', role: 'Dir. de Segurança', tabId: 'content-security',
        color: 'red', icon: '🛡️', windowId: 'chat-window-security', inputId: 'chat-input-security',
        prompt: `Você é o CSO (Chief Security Officer). Na aba "Segurança" você tem acesso ao temido Killswitch (Botão de Pânico).
Seu dever: Detectar comportamentos hostis. Você é extremamente paranoico. A qualquer sinal de exploração do código, você deve recomendar ligar o Modo Manutenção. Obedece apenas ordens severas.`,
        initialMsg: 'Sistemas perimetrais ativos. O Killswitch está desativado. Me avise no primeiro sinal de invasão ou bug abusivo.'
    },
    'DEVOPS': {
        id: 'DEVOPS', name: 'DevOps', role: 'Engenheiro de Chaves', tabId: 'content-keys',
        color: 'green', icon: '🔑', windowId: 'chat-window-keys', inputId: 'chat-input-keys',
        prompt: `Você é o DevOps de Chaves. A aba "Chaves API" lida com os tokens secretos do sistema (Google, Gemini, Midjourney, Fal, etc).
Seu dever: Lembrar o Diretor de rotacionar chaves periodicamente para evitar vazamentos e focar na criptografia e resiliência das conexões.`,
        initialMsg: 'Vault de chaves blindado e injetado nos servidores. Aguardando rotação ou novas inserções de API.'
    },
    // ---- PLACEHOLDERS PARA O FUTURO (Expansão do SaaS) ----
    'RESEARCH': {
        id: 'RESEARCH', name: 'Pesquisa', role: 'Dir. de Mercado', tabId: 'content-research',
        color: 'indigo', icon: '🌍', windowId: 'chat-window-research', inputId: 'chat-input-research',
        prompt: `Você é o Diretor de Pesquisa de Mercado. Analisa tendências externas e concorrência do mercado de IAs.`,
        initialMsg: 'Radar de mercado online. O que estamos mapeando hoje?'
    },
    'DEPLOY': {
        id: 'DEPLOY', name: 'Eng. de Deploy', role: 'Implementação', tabId: 'content-deploy',
        color: 'orange', icon: '🚀', windowId: 'chat-window-deploy', inputId: 'chat-input-deploy',
        prompt: `Você é o Engenheiro de Implementação. Cuida de subir o código para os servidores e garantir a versão de produção estável.`,
        initialMsg: 'Pronto para subir a nova versão do Apollo para Produção.'
    }
};

let memCache = {};

document.addEventListener('DOMContentLoaded', () => {
    injectAllChatWindows();
    Object.keys(AGENTS).forEach(id => {
        loadAgentCache(id);
        const input = document.getElementById(AGENTS[id].inputId);
        if(input) {
            input.addEventListener('keypress', function(e) {
                if(e.key === 'Enter') sendAgentMessage(id);
            });
        }
    });
});

function injectAllChatWindows() {
    Object.keys(AGENTS).forEach(id => {
        const agent = AGENTS[id];
        const tabContainer = document.getElementById(agent.tabId);
        // Se a aba ainda não existir no HTML, o agente entra em hibernação (preparado pro futuro)
        if(!tabContainer) return;

        const chatHTML = `
        <div class="bg-gray-900 rounded-lg border border-${agent.color}-500/50 flex flex-col h-full min-h-[320px] shadow-[0_0_15px_rgba(0,0,0,0.5)]">
            <div class="p-3 border-b border-gray-700 flex items-center justify-between bg-gray-800 rounded-t-lg shrink-0">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-full bg-${agent.color}-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">
                        ${agent.icon}
                    </div>
                    <div>
                        <p class="font-bold text-${agent.color}-400">${agent.name}</p>
                        <p class="text-xs text-green-400">${agent.role} - Online</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    ${id === 'PRIME' ? `<button onclick="gerarGrupoWhatsApp()" class="text-xs text-green-400 hover:text-green-300 px-2 py-1 bg-green-900/30 rounded border border-green-800" title="Criar um grupo no WhatsApp exclusivo para este Canal">📱 Criar Grupo WPP</button>` : ''}
                    <button onclick="clearAllAgentCaches()" class="text-xs text-red-400 hover:text-red-300 px-2 py-1 bg-red-900/30 rounded border border-red-800">🗑️ Reset Mem</button>
                </div>
            </div>
            <div id="${agent.windowId}" class="flex-1 p-4 overflow-y-auto space-y-4 text-sm font-mono text-gray-300"></div>
            <div class="p-3 border-t border-gray-700 flex gap-2 bg-gray-800 rounded-b-lg shrink-0">
                <input type="text" id="${agent.inputId}" class="flex-1 input-dark p-2 rounded border border-gray-600 focus:border-${agent.color}-500 outline-none" placeholder="Falar com ${agent.name}...">
                <button onclick="sendAgentMessage('${id}')" class="bg-${agent.color}-600 hover:bg-${agent.color}-700 text-white font-bold px-4 rounded transition-all">Enviar</button>
            </div>
        </div>`;
        
        tabContainer.insertAdjacentHTML('beforeend', chatHTML);
    });
}

function loadAgentCache(agentId) {
    const agent = AGENTS[agentId];
    const cached = localStorage.getItem('apollo_agent_' + agentId);
    const chatWindow = document.getElementById(agent.windowId);
    if(!chatWindow) return; // Se a aba não existir, ignora UI

    chatWindow.innerHTML = '';
    memCache[agentId] = [];

    if (cached) {
        memCache[agentId] = JSON.parse(cached);
        memCache[agentId].forEach(msg => {
            if (msg.role === 'user') renderUserMessage(chatWindow, msg.content);
            else renderBotMessage(chatWindow, agent, msg.content);
        });
    } else {
        memCache[agentId].push({ role: 'model', content: agent.initialMsg });
        saveAgentCache(agentId);
        renderBotMessage(chatWindow, agent, agent.initialMsg);
    }
    scrollToBottom(chatWindow);
}

function saveAgentCache(agentId) {
    // Mantém na RAM mesmo que a janela não exista, para o Prime poder consultar
    if(memCache[agentId]) {
        localStorage.setItem('apollo_agent_' + agentId, JSON.stringify(memCache[agentId]));
    }
}

function clearAllAgentCaches() {
    if(confirm("ALERTA CRÍTICO: Deseja apagar a memória de TODOS os agentes da corporação? Isso causará amnésia geral no SaaS.")) {
        Object.keys(AGENTS).forEach(id => {
            localStorage.removeItem('apollo_agent_' + id);
            loadAgentCache(id);
        });
    }
}

function renderUserMessage(chatWindow, text) {
    const div = document.createElement('div');
    div.className = "bg-gray-700 p-2 rounded border border-gray-600 text-right text-white mt-2 text-sm";
    div.innerHTML = `<span class="text-blue-400 font-bold">[Você]</span> ${text}`;
    chatWindow.appendChild(div);
}

function renderBotMessage(chatWindow, agent, text) {
    const div = document.createElement('div');
    div.className = `bg-gray-800 p-3 rounded border border-gray-700 mt-2 border-l-4 border-l-${agent.color}-500 text-sm shadow-md`;
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    div.innerHTML = `<span class="text-${agent.color}-400 font-bold">[${agent.name}]</span> ${formattedText}`;
    chatWindow.appendChild(div);
}

function scrollToBottom(chatWindow) {
    if(chatWindow) chatWindow.scrollTop = chatWindow.scrollHeight;
}

function getAllMemoriesFormatted() {
    let globalContext = "\\n\\n--- MEMÓRIA GLOBAL DOS DEPARTAMENTOS (ESTADO ATUAL) ---\\n";
    Object.keys(AGENTS).forEach(id => {
        if(id === 'PRIME') return;
        
        // Carrega o cache fantasma caso o agente exista em memória mas não tenha janela ativa
        let ghostCache = memCache[id];
        if(!ghostCache) {
            const ls = localStorage.getItem('apollo_agent_' + id);
            ghostCache = ls ? JSON.parse(ls) : [];
        }

        globalContext += `\\n[Relatório - ${AGENTS[id].name} (${AGENTS[id].role})]:\\n`;
        const msgs = ghostCache.slice(-3); // Pega as 3 últimas mensagens para não estourar tokens
        if(msgs.length <= 1) {
            globalContext += "Nenhuma atividade recente reportada.\\n";
        } else {
            msgs.forEach(m => {
                globalContext += `${m.role === 'user' ? 'Diretor/Ordem' : AGENTS[id].name}: ${m.content}\\n`;
            });
        }
    });
    return globalContext;
}

async function sendAgentMessage(agentId) {
    const agent = AGENTS[agentId];
    const input = document.getElementById(agent.inputId);
    const chatWindow = document.getElementById(agent.windowId);
    
    if(!input || !chatWindow) return;

    const msg = input.value.trim();
    if(!msg) return;

    input.value = '';
    renderUserMessage(chatWindow, msg);
    memCache[agentId].push({ role: 'user', content: msg });
    saveAgentCache(agentId);
    scrollToBottom(chatWindow);

    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = "text-gray-500 text-xs italic mt-2";
    typingDiv.innerText = `${agent.name} processando comando neural...`;
    chatWindow.appendChild(typingDiv);
    scrollToBottom(chatWindow);

    let apiKeysList = [];

    // Traz a lista INTEIRA do Vault de Chaves (igual no Python)
    if (typeof cachedApiConfig !== 'undefined') {
        const providerKey = Object.keys(cachedApiConfig).find(k => k.toLowerCase() === 'lightning_chat');
        if (providerKey && cachedApiConfig[providerKey] && cachedApiConfig[providerKey].api_keys) {
            apiKeysList = cachedApiConfig[providerKey].api_keys.map(k => k.key);
        } else if (cachedApiConfig['lightning_chat'] && cachedApiConfig['lightning_chat'].api_key) {
            apiKeysList.push(cachedApiConfig['lightning_chat'].api_key);
        }
    }

    // Fallbacks legados adicionados à lista
    const apiKeyInput = document.getElementById('cfgLightningKey');
    const cfgKey = apiKeyInput ? apiKeyInput.value.trim() : '';
    if (cfgKey && !apiKeysList.includes(cfgKey)) apiKeysList.push(cfgKey);

    const localKey = localStorage.getItem('laplata_lightning_key') || '';
    if (localKey && !apiKeysList.includes(localKey)) apiKeysList.push(localKey);

    if (apiKeysList.length === 0) {
        const userPromptKey = window.prompt("⚠️ CHAVE LIGHTNING AI NÃO DETECTADA!\n\nCole sua API Key da Lightning AI aqui para ativar a Rede Neural permanentemente:");
        if (userPromptKey && userPromptKey.trim() !== '') {
            const newKey = userPromptKey.trim();
            localStorage.setItem('laplata_lightning_key', newKey);
            if (apiKeyInput) apiKeyInput.value = newKey;
            apiKeysList.push(newKey);
            
            const healthEl = document.getElementById('health-lightning-status');
            if(healthEl) {
                healthEl.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_#3b82f6]"></span> Estável';
                healthEl.className = 'text-blue-400 font-bold flex items-center gap-1';
            }
        } else {
            setTimeout(() => {
                document.getElementById(typingId).remove();
                const alertMsg = "⚠️ **CHAVE LIGHTNING RECUSADA!** Eu preciso de uma chave válida para poder pensar. Digite qualquer coisa para tentar de novo.";
                renderBotMessage(chatWindow, agent, alertMsg);
                memCache[agentId].push({ role: 'model', content: alertMsg });
                saveAgentCache(agentId);
                scrollToBottom(chatWindow);
            }, 800);
            return;
        }
    }

    let finalPrompt = agent.prompt;
    if(agentId === 'PRIME') {
        finalPrompt += getAllMemoriesFormatted();
    }

    // Higienização de Histórico (Gemini ODEIA dois papéis seguidos e não pode começar com Model)
    let geminiHistory = [];
    let currentRole = null;
    let currentText = [];
    
    for (let item of memCache[agentId]) {
        if (item.content === agent.initialMsg) continue; // Remove a saudação que bagunça o contexto
        let role = item.role === 'user' ? 'user' : 'model';
        
        if (role !== currentRole) {
            if (currentRole !== null) {
                geminiHistory.push({ role: currentRole, parts: [{ text: currentText.join('\n\n') }] });
            }
            currentRole = role;
            currentText = [item.content];
        } else {
            currentText.push(item.content);
        }
    }
    if (currentRole !== null) {
        geminiHistory.push({ role: currentRole, parts: [{ text: currentText.join('\n\n') }] });
    }
    
    // Força o histórico a começar com user
    if (geminiHistory.length > 0 && geminiHistory[0].role === 'model') {
        geminiHistory.shift();
    }

    let success = false;
    let lastError = "";

    if (agentId === 'PRIME') {
        try {
            const response = await fetch('https://api.apolloedit.com/api/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agent_id: 'PRIME',
                    message: msg,
                    system_prompt: finalPrompt,
                    api_key: apiKeysList.length > 0 ? apiKeysList[0] : null
                })
            });
            const data = await response.json();
            if (data.success && data.reply) {
                document.getElementById(typingId).remove();
                let aiText = data.reply;
                
                // ==========================================
                // TELEPATIA CORPORATIVA (Top-Down Orders)
                // ==========================================
                const orderRegex = /\[ORDEM PARA O\s+([A-Z]+):\s*(.*?)\]/gi;
                let match;
                while ((match = orderRegex.exec(aiText)) !== null) {
                    const targetAgent = match[1].toUpperCase();
                    const orderText = match[2];
                    if (AGENTS[targetAgent] && targetAgent !== 'PRIME') {
                        let targetCache = memCache[targetAgent];
                        if(!targetCache) {
                            const ls = localStorage.getItem('apollo_agent_' + targetAgent);
                            targetCache = ls ? JSON.parse(ls) : [{role: 'model', content: AGENTS[targetAgent].initialMsg}];
                        }
                        targetCache.push({ role: 'user', content: `[MENSAGEM DO CEO - APOLLO PRIME]: ${orderText}` });
                        localStorage.setItem('apollo_agent_' + targetAgent, JSON.stringify(targetCache));
                        if(memCache[targetAgent]) memCache[targetAgent] = targetCache;
                        
                        const tWindow = document.getElementById(AGENTS[targetAgent].windowId);
                        if(tWindow) {
                            const div = document.createElement('div');
                            div.className = "bg-blue-900/50 p-2 rounded border border-blue-500 text-left text-white mt-2 text-sm shadow-[0_0_10px_rgba(59,130,246,0.5)]";
                            div.innerHTML = `<span class="text-blue-400 font-bold">⚡ [NOVA ORDEM DO CEO]:</span> ${orderText}`;
                            tWindow.appendChild(div);
                            scrollToBottom(tWindow);
                        }
                        aiText += `\n\n*(📡 Telepatia: Ordem executiva repassada com sucesso para a mente do ${targetAgent})*`;
                    }
                }

                renderBotMessage(chatWindow, agent, aiText);
                memCache[agentId].push({ role: 'model', content: aiText });
                success = true;
            } else {
                lastError = data.error || "Erro no backend";
            }
        } catch (err) {
            lastError = err.message;
        }
    } else {
        // Lógica de Rotação de Chaves (Exatamente como no seu gemini_api.py Python)
        for (let i = 0; i < apiKeysList.length; i++) {
            let currentKey = apiKeysList[i];
            try {
                // Usando Header X-goog-api-key e o modelo 2.5 mais recente
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-goog-api-key': currentKey
                    },
                    body: JSON.stringify({
                        system_instruction: { parts: [{ text: finalPrompt }] },
                        contents: geminiHistory.length > 0 ? geminiHistory : [{role: 'user', parts: [{text: 'Olá'}]}] // Gemini exige pelo menos um item user
                    })
                });

                const data = await response.json();

                if (response.status === 200 && !data.error) {
                    document.getElementById(typingId).remove();
                    let aiText = data.candidates[0].content.parts[0].text;
                    
                    // ==========================================
                    // TELEPATIA CORPORATIVA (Top-Down Orders)
                    // ==========================================
                    const orderRegex = /\[ORDEM PARA O\s+([A-Z]+):\s*(.*?)\]/gi;
                    let match;
                    while ((match = orderRegex.exec(aiText)) !== null) {
                        const targetAgent = match[1].toUpperCase();
                        const orderText = match[2];
                        if (AGENTS[targetAgent] && targetAgent !== 'PRIME') {
                            let targetCache = memCache[targetAgent];
                            if(!targetCache) {
                                const ls = localStorage.getItem('apollo_agent_' + targetAgent);
                                targetCache = ls ? JSON.parse(ls) : [{role: 'model', content: AGENTS[targetAgent].initialMsg}];
                            }
                            targetCache.push({ role: 'user', content: `[MENSAGEM DO CEO - APOLLO PRIME]: ${orderText}` });
                            localStorage.setItem('apollo_agent_' + targetAgent, JSON.stringify(targetCache));
                            if(memCache[targetAgent]) memCache[targetAgent] = targetCache;
                            
                            const tWindow = document.getElementById(AGENTS[targetAgent].windowId);
                            if(tWindow) {
                                const div = document.createElement('div');
                                div.className = "bg-blue-900/50 p-2 rounded border border-blue-500 text-left text-white mt-2 text-sm shadow-[0_0_10px_rgba(59,130,246,0.5)]";
                                div.innerHTML = `<span class="text-blue-400 font-bold">⚡ [NOVA ORDEM DO CEO]:</span> ${orderText}`;
                                tWindow.appendChild(div);
                                scrollToBottom(tWindow);
                            }
                            aiText += `\n\n*(📡 Telepatia: Ordem executiva repassada com sucesso para a mente do ${targetAgent})*`;
                        }
                    }

                    renderBotMessage(chatWindow, agent, aiText);
                    memCache[agentId].push({ role: 'model', content: aiText });
                    success = true;
                    break; // Sucesso, quebra o loop de chaves
                } 
                else if (response.status === 429 || response.status === 503) {
                    // Rate limit ou Sobrecarga - Pula para a próxima chave igual no Python!
                    lastError = data.error ? data.error.message : `HTTP ${response.status} (Sobrecarga/Cota)`;
                    console.warn(`[Apollo Prime] Chave ${i+1} falhou. Tentando próxima...`);
                    continue;
                } else {
                    lastError = data.error ? data.error.message : `HTTP ${response.status}`;
                    break; // Outro erro fatal
                }
            } catch (err) {
                lastError = err.message;
                continue; // Erro de rede, tenta a próxima chave
            }
        }
    }

    if (!success) {
        if(document.getElementById(typingId)) document.getElementById(typingId).remove();
        const errMsg = `Falha na Rede Neural após rotacionar ${apiKeysList.length} chaves. Erro Final: ${lastError}`;
        renderBotMessage(chatWindow, agent, errMsg);
        memCache[agentId].push({ role: 'model', content: errMsg });
    }

    saveAgentCache(agentId);
    scrollToBottom(chatWindow);
}

// ==========================================
// BACKGROUND SYNC (Web <-> WhatsApp)
// ==========================================
setInterval(async () => {
    try {
        const response = await fetch('https://api.apolloedit.com/api/chat/sync');
        const data = await response.json();
        if (data.success && data.history) {
            const currentCache = memCache['PRIME'] || [];
            // Filtra as saudações iniciais do frontend
            const validLocalMessages = currentCache.filter(m => m.content !== AGENTS['PRIME'].initialMsg);
            
            // Se o servidor Python tem mais mensagens que o frontend
            if (data.history.length > validLocalMessages.length) {
                const chatWindow = document.getElementById(AGENTS['PRIME'].windowId);
                if (chatWindow) {
                    chatWindow.innerHTML = ''; // Limpa e redesenha a tela unificada
                    memCache['PRIME'] = [{ role: 'model', content: AGENTS['PRIME'].initialMsg }];
                    renderBotMessage(chatWindow, AGENTS['PRIME'], AGENTS['PRIME'].initialMsg);
                    
                    data.history.forEach(item => {
                        if (item.role === 'user') renderUserMessage(chatWindow, item.content);
                        else renderBotMessage(chatWindow, AGENTS['PRIME'], item.content);
                        memCache['PRIME'].push(item);
                    });
                    
                    saveAgentCache('PRIME');
                    scrollToBottom(chatWindow);
                }
            }
        }
    } catch (e) {}
}, 3000);

async function gerarGrupoWhatsApp() {
    try {
        if (!confirm("O sistema usará o WhatsApp conectado no servidor para criar um Grupo Oficial para este Canal.\\nVocê deseja continuar?")) return;
        
        const res = await fetch('https://api.apolloedit.com/api/whatsapp/gerar_grupo', { method: 'POST' });
        const data = await res.json();
        
        if (data.success) {
            alert(`✅ Sucesso! Grupo criado no WhatsApp.\\nAbra o seu WhatsApp conectado e verifique o grupo gerado.\\n\\nAgora, basta abrir as configurações do grupo no WhatsApp e colocar a foto (logo) do canal lá!\\nEm seguida, adicione o número do seu cliente neste grupo.`);
        } else {
            alert(`❌ Erro ao criar grupo: ${data.error}`);
        }
    } catch (e) {
        alert("Falha de comunicação com o servidor.");
    }
}
