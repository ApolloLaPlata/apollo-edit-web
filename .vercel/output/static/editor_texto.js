// editor_texto.js
document.addEventListener('DOMContentLoaded', () => {
    const LOCAL_STORAGE_KEY = 'apollo_editor_texto_editorjs';

    // Inicialização do Editor.js
    const editor = new EditorJS({
        holder: 'word-editor',
        tools: {
            header: Header,
            list: List,
            paragraph: {
                class: Paragraph,
                inlineToolbar: true,
            }
        },
        placeholder: 'Comece a digitar seu roteiro aqui... (Pressione / para comandos de IA)',
        data: JSON.parse(localStorage.getItem(LOCAL_STORAGE_KEY) || '{}'),
        onChange: () => {
            editor.save().then((outputData) => {
                localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(outputData));
            });
        }
    });

    // Botão Salvar Rascunho Manual (Topbar)
    document.getElementById('btn-save-draft')?.addEventListener('click', async () => {
        const outputData = await editor.save();
        localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(outputData));
        if (window.showToast) window.showToast("Rascunho salvo no LocalStorage!", "#00ffcc");
    });

    // Botão Salvar Projeto na Garagem (Banco de Dados)
    document.getElementById('btn-save-garagem')?.addEventListener('click', async () => {
        try {
            const outputData = await editor.save();
            if (!outputData.blocks.length) {
                alert("O texto está vazio. Escreva algo antes de salvar.");
                return;
            }

            let title = "Documento Sem Título";
            const firstHeader = outputData.blocks.find(b => b.type === 'header');
            if (firstHeader && firstHeader.data.text) {
                title = firstHeader.data.text.replace(/&nbsp;/g, ' ').trim();
            } else {
                const firstPara = outputData.blocks.find(b => b.type === 'paragraph');
                if (firstPara && firstPara.data.text) {
                    title = firstPara.data.text.replace(/&nbsp;/g, ' ').substring(0, 30);
                }
            }

            const project = {
                id: 'proj_text_' + Date.now().toString(),
                type: 'roteiro_texto',
                title: title,
                content: JSON.stringify(outputData),
                timestamp: Date.now()
            };

            await window.laplataDB.projects.save(project);
            if (window.showToast) window.showToast(`Projeto salvo na Garagem!`, "#00ffcc");
        } catch(e) {
            console.error("Erro ao salvar projeto:", e);
            alert("Falha ao salvar na Garagem.");
        }
    });

    // Função de Exportar
    window.exportToBagageiro = async function() {
        try {
            const outputData = await editor.save();
            if (!outputData.blocks.length) {
                alert("O texto está vazio. Escreva algo antes de exportar.");
                return;
            }

            // Converter blocos para HTML básico para exportação
            let htmlContent = outputData.blocks.map(block => {
                switch (block.type) {
                    case 'header': return `<h${block.data.level}>${block.data.text}</h${block.data.level}>`;
                    case 'paragraph': return `<p>${block.data.text}</p>`;
                    case 'list': return `<ul>${block.data.items.map(i => `<li>${i}</li>`).join('')}</ul>`;
                    default: return '';
                }
            }).join('\n');

            const blob = new Blob([htmlContent], { type: 'text/html' });
            const file = new File([blob], `Documento_${new Date().getTime()}.html`, { type: 'text/html' });

            if (window.apolloTransferOS) {
                window.apolloTransferOS.receiveFile(file, file.name);
            } else if (typeof window.processDroppedFiles === 'function') {
                window.processDroppedFiles([file]);
                if (window.showToast) window.showToast("Exportado para o Apollo OS (Bagageiro)!", "#6b21a8");
            } else {
                console.warn("Transfer HUD global não carregado. Simulando download direto.");
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = file.name;
                a.click();
            }
        } catch(e) {
            console.error("Erro na exportação: ", e);
        }
    };

    // Lógica de IA do Roteirista
    const btnContinue = document.getElementById('btn-ia-continue');
    const btnRewrite = document.getElementById('btn-ia-rewrite');
    const btnGrammar = document.getElementById('btn-ia-grammar');
    const aiTone = document.getElementById('ai-tone');

    async function callAITextEdit(action, textContext, tone) {
        document.body.style.cursor = 'wait';
        try {
            if (!window.laplataAI || !window.laplataApiKeys) {
                throw new Error("Módulo de IA não carregado.");
            }
            let systemInstruction = "Você é um assistente de escrita avançado.";
            let prompt = "";
            if (action === 'continue') {
                systemInstruction = `Você deve continuar o texto de forma fluida (Tom: ${tone}). Não coloque explicações.`;
                prompt = `Continue este texto:\n\n${textContext}`;
            } else if (action === 'rewrite') {
                systemInstruction = `Reescreva o texto melhorando a qualidade (Tom: ${tone}). Sem introduções.`;
                prompt = `Reescreva este texto:\n\n${textContext}`;
            } else if (action === 'grammar') {
                systemInstruction = `Corrija o texto fornecido. Se já estiver correto, responda "[Revisão OK]".`;
                prompt = `Revise este texto:\n\n${textContext}`;
            }

            return await window.laplataApiKeys.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.generateText(apiKey, prompt, {}, systemInstruction);
            });
        } catch (error) {
            console.error(error);
            if (window.showToast) window.showToast("Erro na IA: " + error.message, "#ff0000");
            return "";
        } finally {
            document.body.style.cursor = 'default';
        }
    }

    btnContinue?.addEventListener('click', async () => {
        btnContinue.innerText = "Pensando...";
        const outputData = await editor.save();
        const fullText = outputData.blocks.map(b => b.data.text || '').join('\n');
        const newText = await callAITextEdit('continue', fullText, aiTone.value);
        
        if (newText) {
            editor.blocks.insert('paragraph', { text: newText });
            if (window.showToast) window.showToast("IA: Texto continuado!", "#ff00ff");
        }
        btnContinue.innerText = "Continuar Texto Mágico";
    });

    btnRewrite?.addEventListener('click', async () => {
        alert("Com Editor.js, o recurso de reescrita focada requer seleção avançada. Em breve!");
    });

    btnGrammar?.addEventListener('click', async () => {
        btnGrammar.innerText = "Revisando...";
        const outputData = await editor.save();
        const fullText = outputData.blocks.map(b => b.data.text || '').join('\n');
        const result = await callAITextEdit('grammar', fullText, aiTone.value);
        
        if (window.showToast) window.showToast("IA: " + result, "#00ffcc");
        btnGrammar.innerText = "Corrigir e Revisar";
    });
});
