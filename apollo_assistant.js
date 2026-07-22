// apollo_assistant.js
// Injeta o "Assistente Apollo" como um widget flutuante

(function() {
    function injectAssistant() {
        if (window.self !== window.top) return;
        if (document.getElementById('apollo-assistant-widget')) return;

        // Container Flutuante
        const container = document.createElement('div');
        container.id = 'apollo-assistant-widget';
        container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 100000;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            font-family: 'Inter', sans-serif;
        `;

        // O Chat Panel (oculto por padrão)
        const chatPanel = document.createElement('div');
        chatPanel.id = 'apollo-assistant-panel';
        chatPanel.style.cssText = `
            width: 320px;
            height: 450px;
            background: #0f172a;
            border: 1px solid rgba(139, 92, 246, 0.4);
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.8);
            display: none;
            flex-direction: column;
            margin-bottom: 15px;
            overflow: hidden;
            backdrop-filter: blur(10px);
        `;

        chatPanel.innerHTML = `
            <div style="background: rgba(30, 41, 59, 0.8); padding: 12px 16px; color: #f8fafc; font-weight: bold; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(139, 92, 246, 0.3);">
                <span style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: linear-gradient(135deg, #8b5cf6, #3b82f6); -webkit-background-clip: text; color: transparent;">✨ Assistente Apollo</span>
                </span>
                <button id="btn-close-assistant" style="background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 16px; transition: color 0.2s;">✖</button>
            </div>
            <div id="assistant-chat-history" style="flex: 1; padding: 16px; overflow-y: auto; color: #e2e8f0; font-size: 14px; display: flex; flex-direction: column; gap: 12px;">
                <div style="background: #1e293b; padding: 12px; border-radius: 8px 8px 8px 2px; align-self: flex-start; max-width: 85%; border: 1px solid rgba(255,255,255,0.05); line-height: 1.5;">
                    Olá! Eu sou o Assistente Apollo. Como posso auxiliar em sua edição ou roteirização hoje?
                </div>
            </div>
            <div style="padding: 12px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; gap: 8px; background: rgba(15, 23, 42, 0.9);">
                <input type="text" id="assistant-chat-input" placeholder="Digite seu comando..." style="flex: 1; padding: 10px; border-radius: 6px; border: 1px solid #334155; background: #1e293b; color: white; outline: none; font-family: 'Inter', sans-serif;">
                <button id="btn-send-assistant" style="background: linear-gradient(135deg, #8b5cf6, #3b82f6); color: white; border: none; border-radius: 6px; padding: 0 16px; cursor: pointer; font-weight: bold; transition: opacity 0.2s;">Enviar</button>
            </div>
        `;

        // O Botão Flutuante (Assistente Apollo)
        const fab = document.createElement('button');
        fab.style.cssText = `
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            border: 2px solid rgba(255,255,255,0.1);
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.5);
            cursor: pointer;
            font-size: 24px;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: white;
        `;
        fab.innerHTML = '✨';
        fab.title = 'Abrir Assistente Apollo (IA)';

        fab.onmouseover = () => {
            fab.style.transform = 'scale(1.1) translateY(-4px)';
            fab.style.boxShadow = '0 10px 25px rgba(59, 130, 246, 0.6)';
        };
        fab.onmouseout = () => {
            fab.style.transform = 'scale(1) translateY(0)';
            fab.style.boxShadow = '0 4px 20px rgba(59, 130, 246, 0.5)';
        };

        fab.onclick = () => {
            const isHidden = chatPanel.style.display === 'none';
            chatPanel.style.display = isHidden ? 'flex' : 'none';
            if (isHidden) {
                document.getElementById('assistant-chat-input').focus();
            }
        };

        container.appendChild(chatPanel);
        container.appendChild(fab);
        document.body.appendChild(container);

        // Lógica de fechamento
        document.getElementById('btn-close-assistant').onclick = () => {
            chatPanel.style.display = 'none';
        };

        // Lógica de Envio
        const input = document.getElementById('assistant-chat-input');
        const btnSend = document.getElementById('btn-send-assistant');
        const history = document.getElementById('assistant-chat-history');

        const sendMessage = async () => {
            const text = input.value.trim();
            if (!text) return;

            // Adiciona mensagem do user
            const userMsg = document.createElement('div');
            userMsg.style.cssText = `background: #8b5cf6; padding: 12px; border-radius: 8px 8px 2px 8px; align-self: flex-end; max-width: 85%; color: white; line-height: 1.5;`;
            userMsg.textContent = text;
            history.appendChild(userMsg);
            input.value = '';
            history.scrollTop = history.scrollHeight;

            // Loading
            const loadingMsg = document.createElement('div');
            loadingMsg.style.cssText = `background: #1e293b; padding: 12px; border-radius: 8px 8px 8px 2px; align-self: flex-start; max-width: 85%; font-style: italic; color: #94a3b8; border: 1px solid rgba(255,255,255,0.05);`;
            loadingMsg.innerHTML = '<span style="animation: pulse 1.5s infinite;">Processando...</span>';
            history.appendChild(loadingMsg);
            history.scrollTop = history.scrollHeight;

            try {
                // Chama a API Laplata
                const apiKeysRef = window.laplataApiKeys || (window.parent && window.parent.laplataApiKeys);
                const aiRef = window.laplataAI || (window.parent && window.parent.laplataAI);

                if (apiKeysRef && aiRef) {
                    // Extract current tool name from URL
                    const pathParts = window.location.pathname.split('/');
                    const currentPage = pathParts[pathParts.length - 1] || 'hub.html';
                    
                    // Knowledge Base Dictionary
                    const toolKB = {
                        "editor_texto.html": "Você está no Editor de Texto Mágico. O usuário pode escrever roteiros. Diga a ele para usar a barra superior para formatar ou salvar na Garagem.",
                        "editor_imagem.html": "Você está no Photopea (Clone do Photoshop). Ensine atalhos do Photoshop, fale sobre camadas (layers), máscaras e filtros.",
                        "editor_audiomass.html": "Você está no AudioMass. Diga ao usuário que ele pode arrastar áudios, cortar partes, aplicar efeitos (reverb, compressão) no topo.",
                        "editor_daw.html": "Você está na DAW Profissional (BandLab/GarageBand style). Ensine sobre multipistas, arranjo, MIDI e plugins.",
                        "gerador_musica.html": "Você está no Gerador de Música IA. Diga ao usuário para inserir um prompt (ex: 'Bossa nova triste com saxofone') e gerar.",
                        "removedor_fundo.html": "Você está no Removedor de Fundo. Diga para o usuário colar ou upar uma imagem para extrair o fundo com IA.",
                        "estudio_dublagem.html": "Você está no Estúdio de Dublagem (RVC). O usuário pode upar um áudio original, escolher um modelo de voz (Personagem) e a IA vai clonar o timbre.",
                        "storyboard.html": "Você está no Mapa Mental (Excalidraw). Ensine que o usuário pode desenhar nós, caixas e setas para planejar vídeos.",
                        "teleprompter.html": "Você está no Teleprompter. Ensine o usuário a colar o texto, ajustar a velocidade e gravar a si mesmo lendo a tela.",
                        "editor_freecut.html": "Você está no Editor de Vídeo (Timeline). Ensine a arrastar clipes, cortar (Split), exportar o projeto, e usar transições.",
                        "tts.html": "Você está no Motor Voz IA (TTS). Ensine a colar roteiros, ajustar o Pitch e Speed e clicar em Gerar Áudio.",
                        "ferramenta_laplata.html": "Você está na La Plata IA. Ajude o usuário a interagir com os nós neurais profundos do Apollo.",
                        "hub.html": "Você está no Hub Central Apollo. Ensine o usuário a clicar nas ferramentas ao redor para entrar nos editores."
                    };
                    
                    const contextInfo = toolKB[currentPage] || "Você está no Apollo Edit Web.";
                    
                    const navMap = `
Mapeamento de Navegação Válido (Use com a tag [NAVIGATE: arquivo.html]):
- editor_texto.html (Editor de Texto / Roteiros)
- editor_imagem.html (Editor de Imagem / Photopea)
- editor_audiomass.html (Edição de Áudio / AudioMass)
- editor_daw.html (DAW de Música Avançada)
- gerador_musica.html (Gerador de Música IA)
- removedor_fundo.html (Removedor de Fundo de Imagens)
- estudio_dublagem.html (Dublagem e Clonagem RVC)
- storyboard.html (Mapa Mental / Excalidraw)
- teleprompter.html (Teleprompter para gravação)
- timeline.html (Editor de Vídeo)
- tts.html (Motor de Voz TTS)
- hub.html (Tela Inicial Central)`;

                    const promptText = `O usuário diz: ${text}`;
                    
                    // Extrai contexto do canal atual
                    let channelContext = "";
                    try {
                        const activeId = sessionStorage.getItem('apollo_active_channel_id') || localStorage.getItem('apollo_active_channel_id');
                        if (activeId) {
                            const channels = JSON.parse(localStorage.getItem('apollo_channels') || '[]');
                            const ch = channels.find(c => c.id === activeId);
                            if (ch) {
                                channelContext = `\n\n[CONTEXTO GLOBAL DO CANAL ATUAL]\nNome do Canal: ${ch.name}\nDescrição do Canal: ${ch.description || 'Não informada'}\nSua Personalidade/Tom de Voz para este canal: ${ch.personality || 'Aja profissionalmente.'}\nLinks de Pesquisa/Referências do Canal: ${ch.links && ch.links.length > 0 ? ch.links.map(l => l.title + ' - ' + l.url).join(', ') : 'Nenhum'}`;
                            }
                        }
                    } catch(e) {}

                    const systemMsg = `Você é o Assistente Apollo, uma IA poderosa, prestativa e integrada ao ecossistema Apollo OS.${channelContext}\n\n[CONTEXTO DA FERRAMENTA ATUAL ONDE O USUÁRIO ESTÁ]\n${contextInfo}\n\n${navMap}\n\nHABILIDADE DE NAVEGAÇÃO:\nSe o usuário pedir para ir para outra ferramenta, você DEVE usar a tag oculta [NAVIGATE: arquivo.html] no final da sua resposta consultando o mapa acima. Exemplo: "Entendido, abrindo o editor de áudio. [NAVIGATE: editor_audiomass.html]".\n\nSiga estritamente a "Sua Personalidade/Tom de Voz" se fornecida no contexto do canal.`;
                    
                    let resposta = await apiKeysRef.executeWithKeyRotation(async (apiKey) => {
                        return await aiRef.generateText(apiKey, promptText, {}, systemMsg);
                    });
                    
                    history.removeChild(loadingMsg);
                    
                    // Parse NAVIGATE tag
                    const navMatch = resposta.match(/\[NAVIGATE:\s*([^\]]+)\]/i);
                    let targetPage = null;
                    if (navMatch) {
                        targetPage = navMatch[1].trim();
                        // Remove the tag from the visible response
                        resposta = resposta.replace(/\[NAVIGATE:\s*([^\]]+)\]/i, '').trim();
                    }
                    
                    const botMsg = document.createElement('div');
                    botMsg.style.cssText = `background: #1e293b; padding: 12px; border-radius: 8px 8px 8px 2px; align-self: flex-start; max-width: 85%; white-space: pre-wrap; border: 1px solid rgba(255,255,255,0.05); line-height: 1.5;`;
                    botMsg.textContent = resposta;
                    history.appendChild(botMsg);
                    
                    // Execute Navigation if found
                    if (targetPage) {
                        setTimeout(() => {
                            if (window.openAppTab) {
                                window.openAppTab(targetPage, targetPage.replace('.html', ''));
                            } else if (window.parent && window.parent.openAppTab) {
                                window.parent.openAppTab(targetPage, targetPage.replace('.html', ''));
                            } else {
                                window.location.href = targetPage;
                            }
                        }, 1500); // Wait 1.5s so the user can read the message before jumping
                    }
                } else {
                    throw new Error("Laplata API não carregada no escopo global.");
                }
            } catch (err) {
                console.error(err);
                history.removeChild(loadingMsg);
                const errorMsg = document.createElement('div');
                errorMsg.style.cssText = `background: rgba(220, 38, 38, 0.2); border: 1px solid #dc2626; padding: 12px; border-radius: 8px 8px 8px 2px; align-self: flex-start; max-width: 85%; color: #fca5a5; line-height: 1.5;`;
                errorMsg.textContent = 'Erro de conexão. O subsistema de I.A. não está disponível no momento.';
                history.appendChild(errorMsg);
            }
            history.scrollTop = history.scrollHeight;
        };

        btnSend.onclick = sendMessage;
        input.onkeypress = (e) => {
            if (e.key === 'Enter') sendMessage();
        };

        // Inject pulse animation keyframes if not exists
        if (!document.getElementById('apollo-animations')) {
            const style = document.createElement('style');
            style.id = 'apollo-animations';
            style.innerHTML = `
                @keyframes pulse {
                    0% { opacity: 0.6; }
                    50% { opacity: 1; }
                    100% { opacity: 0.6; }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Tentar injetar assim que possível
    if (document.readyState === 'loading') {
        // document.addEventListener('DOMContentLoaded', injectAssistant);
    } else {
        // injectAssistant();
    }
})();
