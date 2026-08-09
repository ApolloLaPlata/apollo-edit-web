import sys

filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\apollo_agents.js'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''    } else {
        // Lógica de Rotação de Chaves'''

if target not in content:
    print('ALVO NAO ENCONTRADO NO ARQUIVO')
    sys.exit(1)

# Achar onde fecha o bloco else
# O bloco do else começa em "    } else {" e tem um "catch (err) {" e termina em "continue; // Erro de rede"
end_marker = '                continue; // Erro de rede, tenta a próxima chave\n            }\n        }'

start_idx = content.find(target)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

replacement = '''    } else {
        try {
            const openAiHistory = geminiHistory.map(msg => ({
                role: msg.role === 'model' ? 'assistant' : 'user',
                content: msg.parts[0].text
            }));
            
            const response = await fetch('/api/lightning_proxy', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: 'nvidia-nemotron-3-ultra-550b-a55b',
                    system_prompt: finalPrompt,
                    messages: openAiHistory.length > 0 ? openAiHistory : [{role: 'user', content: 'Olá'}]
                })
            });

            const data = await response.json();

            if (response.status === 200 && !data.error) {
                document.getElementById(typingId).remove();
                let aiText = data.choices[0].message.content;
                
                // TELEPATIA CORPORATIVA
                const orderRegex = /\[ORDEM PARA O\s+([A-Z]+):\s*(.*?)\]/gi;
                let match;
                while ((match = orderRegex.exec(aiText)) !== null) {
                    const targetAgent = match[1].toUpperCase();
                    const orderText = match[2];
                    if (AGENTS[targetAgent] && targetAgent !== 'PRIME') {
                        let targetCache = memCache[targetAgent];
                        if(!targetCache) {
                            const ls = localStorage.getItem('apollo_agent_' + targetAgent);
                            targetCache = ls ? JSON.parse(ls) : [{role: 'assistant', content: AGENTS[targetAgent].initialMsg}];
                        }
                        targetCache.push({ role: 'user', content: [MENSAGEM DO CEO - APOLLO PRIME]:  });
                        localStorage.setItem('apollo_agent_' + targetAgent, JSON.stringify(targetCache));
                        if(memCache[targetAgent]) memCache[targetAgent] = targetCache;
                        
                        const tWindow = document.getElementById(AGENTS[targetAgent].windowId);
                        if(tWindow) {
                            const div = document.createElement('div');
                            div.className = "bg-blue-900/50 p-2 rounded border border-blue-500 text-left text-white mt-2 text-sm shadow-[0_0_10px_rgba(59,130,246,0.5)]";
                            div.innerHTML = <span class="text-blue-400 font-bold">⚡ [NOVA ORDEM DO CEO]:</span> ;
                            tWindow.appendChild(div);
                        }
                        aiText += \\n\\n*(📡 Telepatia: Ordem executiva repassada com sucesso para a mente do )*;
                    }
                }

                renderBotMessage(chatWindow, agent, aiText);
                memCache[agentId].push({ role: 'model', parts: [{text: aiText}] });
                success = true;
            } else {
                lastError = data.error ? data.error.message : HTTP ;
            }
        } catch (err) {
            lastError = err.message;
        }'''

new_content = content[:start_idx] + replacement + content[end_idx:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('SUBSTITUIDO COM SUCESSO')
