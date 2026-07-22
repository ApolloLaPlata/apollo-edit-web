/**
 * Apollo La Plata - Character Creator Logic
 * Gerencia a lógica do laplata_creator.html
 */

document.addEventListener('DOMContentLoaded', async () => {
    // --- ELEMENTOS UI ---
    // Painel Esquerdo
    const modeBtns = document.querySelectorAll('.mode-btn');
    const refDropzone = document.getElementById('ref-dropzone');
    const refPlaceholder = document.getElementById('ref-placeholder');
    const refPreview = document.getElementById('ref-preview');
    const btnRemoveRef = document.getElementById('btn-remove-ref');
    const refFileInput = document.getElementById('ref-file');
    const btnDescribeImg = document.getElementById('btn-describe-img');
    const btnExpandPrompt = document.getElementById('btn-expand-prompt');
    const mainPrompt = document.getElementById('main-prompt');
    const btnGenerate = document.getElementById('btn-generate');

    // Painel Direito
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const viewerPlaceholder = document.getElementById('viewer-placeholder');
    const resultWrapper = document.getElementById('result-wrapper');
    const resultImage = document.getElementById('result-image');
    
    // Tools Overlay
    const toolDownload = document.getElementById('tool-download');
    const toolReroll = document.getElementById('tool-reroll');
    const toolEdit = document.getElementById('tool-edit');
    const toolGetPrompt = document.getElementById('tool-get-prompt');

    // Edit Overlay
    const editOverlay = document.getElementById('edit-overlay');
    const editPrompt = document.getElementById('edit-prompt');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');
    const btnApplyEdit = document.getElementById('btn-apply-edit');

    // Save Bar
    const saveBar = document.getElementById('save-bar');
    const saveName = document.getElementById('save-name');
    const saveDesc = document.getElementById('save-desc');
    const btnSaveRoster = document.getElementById('btn-save-roster');

    // --- ESTADO LOCAL ---
    let currentMode = 'turnaround';
    let referenceImageBase64 = null;
    let generatedImageBase64 = null;
    let isGenerating = false;

    // Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playSuccess = () => { if (window.apolloSFX) window.apolloSFX.play('success'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };

    const showToast = (title, message, type = 'system') => {
        if (window.apolloNotifications) window.apolloNotifications.add(title, message, type);
    };

    const updateGenerateBtnState = () => {
        const text = mainPrompt.value.trim();
        btnGenerate.disabled = isGenerating || text.length === 0;
        btnExpandPrompt.disabled = isGenerating || text.length === 0;
    };

    mainPrompt.addEventListener('input', updateGenerateBtnState);

    // --- SELEÇÃO DE MODO ---
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (isGenerating) return;
            playClick();
            modeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.getAttribute('data-mode');
            
            // Ajusta o placeholder dependendo do modo
            if (currentMode === 't-pose') {
                mainPrompt.placeholder = "Ex: Um ninja ciborgue, simetria, mãos abertas, rosto neutro...";
            } else if (currentMode === 'expression') {
                mainPrompt.placeholder = "Ex: Expressões de um elfo ladino. Rindo, Chorando, Com Raiva. Poses de ataque...";
            } else {
                mainPrompt.placeholder = "Ex: Um samurai cyberpunk com armadura verde neon, katana nas costas...";
            }
        });
    });

    // --- UPLOAD DE REFERÊNCIA ---
    refDropzone.addEventListener('click', (e) => {
        if (e.target !== btnRemoveRef && !isGenerating) refFileInput.click();
    });

    refDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        refDropzone.style.borderColor = '#2ECC71';
    });

    refDropzone.addEventListener('dragleave', () => {
        refDropzone.style.borderColor = '#475569';
    });

    refDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        refDropzone.style.borderColor = '#475569';
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            processFile(e.dataTransfer.files[0]);
        }
    });

    refFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            processFile(e.target.files[0]);
        }
    });

    function processFile(file) {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                const maxDim = 1024;

                if (width > height && width > maxDim) {
                    height *= maxDim / width;
                    width = maxDim;
                } else if (height > maxDim) {
                    width *= maxDim / height;
                    height = maxDim;
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                referenceImageBase64 = canvas.toDataURL('image/jpeg', 0.8);
                
                refPlaceholder.style.display = 'none';
                refPreview.src = referenceImageBase64;
                refPreview.style.display = 'block';
                btnRemoveRef.style.display = 'block';
                // btnDescribeImg.style.display = 'flex'; // Opcional, mantido escondido por padrão se não for usar a API de descrever
                
                playClick();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    btnRemoveRef.addEventListener('click', (e) => {
        e.stopPropagation();
        referenceImageBase64 = null;
        refPlaceholder.style.display = 'block';
        refPreview.style.display = 'none';
        refPreview.src = '';
        btnRemoveRef.style.display = 'none';
        btnDescribeImg.style.display = 'none';
        refFileInput.value = '';
        playClick();
    });

    // --- IA: EXPANDIR PROMPT ---
    btnExpandPrompt.addEventListener('click', async () => {
        const text = mainPrompt.value.trim();
        if (!text || isGenerating) return;

        playClick();
        isGenerating = true;
        btnExpandPrompt.innerHTML = "✨ Expandindo...";
        updateGenerateBtnState();

        try {
            const settings = await window.laplataSettings.getSettings();
            
            const expanded = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.expandDescription(apiKey, text, currentMode, settings);
            });

            mainPrompt.value = expanded;
            showToast('Expansão Concluída', 'O prompt foi detalhado com sucesso!', 'success');
            playSuccess();
        } catch (e) {
            console.error(e);
            showToast('Falha na IA', e.message, 'system');
            playError();
        } finally {
            isGenerating = false;
            btnExpandPrompt.innerHTML = "✨ Expandir com IA";
            updateGenerateBtnState();
        }
    });

    // --- IA: GERAR IMAGEM ---
    btnGenerate.addEventListener('click', async () => {
        const text = mainPrompt.value.trim();
        if (!text || isGenerating) return;

        playClick();
        await startGenerationLogic(text, "Sintetizando Concept Art...", false);
    });

    async function startGenerationLogic(promptText, loadingMsg, isEdit = false) {
        isGenerating = true;
        updateGenerateBtnState();
        loadingText.innerText = loadingMsg;
        loadingOverlay.style.display = 'flex';
        
        // Hide result temporary
        if (!isEdit) {
            viewerPlaceholder.style.display = 'flex';
            resultWrapper.style.display = 'none';
            saveBar.style.display = 'none';
        }

        try {
            // 1. Carrega configurações e DB de personagens
            const settings = await window.laplataSettings.getSettings();
            const characters = await window.laplataDB.characters.getAll();

            // Override do aspect ratio baseado no modo
            let finalSettings = { ...settings };
            finalSettings.aspectRatio = currentMode === 'turnaround' ? '16:9' : '1:1';

            // 2. Rotação de Chaves e Geração via ESM SDK (laplata_ai.js)
            let resultBase64;

            if (isEdit) {
                // A edição no Gemini 2.5/Flash geralmente envia a imagem atual como ref
                resultBase64 = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                    return await window.laplataAI.generateImage(apiKey, promptText, characters, finalSettings, generatedImageBase64);
                });
            } else {
                resultBase64 = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                    return await window.laplataAI.generateImage(apiKey, promptText, characters, finalSettings, referenceImageBase64);
                });
            }

            generatedImageBase64 = resultBase64;
            
            // 3. Mostra na Tela
            viewerPlaceholder.style.display = 'none';
            resultImage.src = generatedImageBase64;
            resultWrapper.style.display = 'inline-block';
            
            // Ajusta visual do wrapper de acordo com o ratio
            resultWrapper.style.aspectRatio = currentMode === 'turnaround' ? '16/9' : '1/1';
            resultWrapper.style.width = currentMode === 'turnaround' ? '100%' : 'auto';
            resultWrapper.style.height = currentMode === 'turnaround' ? 'auto' : '100%';

            saveBar.style.display = 'flex';

            playSuccess();
            showToast('Geração Concluída', 'Sua imagem está pronta!', 'quest');

            // 4. Salvar backup automático na Galeria
            let promptPrefix = currentMode === 't-pose' ? '[T-Pose]' : currentMode === 'expression' ? '[Expressions]' : '[Character Sheet]';
            const finalSavePrompt = isEdit ? `[Editado: ${editPrompt.value.trim()}] ${promptPrefix} ${mainPrompt.value}` : `${promptPrefix} ${promptText}`;

            await window.laplataDB.gallery.save({
                id: crypto.randomUUID(),
                prompt: finalSavePrompt,
                imageUrl: generatedImageBase64,
                timestamp: Date.now(),
                aspectRatio: finalSettings.aspectRatio
            });

            if (window.apolloQuests) window.apolloQuests.checkAction('generate_image');

        } catch (e) {
            console.error("Geração falhou:", e);
            showToast('Erro de Renderização', e.message, 'system');
            playError();
        } finally {
            isGenerating = false;
            updateGenerateBtnState();
            loadingOverlay.style.display = 'none';
        }
    }

    // --- OVERLAY TOOLS ---
    toolDownload.addEventListener('click', () => {
        if (!generatedImageBase64) return;
        playClick();
        const link = document.createElement('a');
        link.href = generatedImageBase64;
        link.download = `apollo_concept_${Date.now()}.jpg`;
        link.click();
    });

    toolReroll.addEventListener('click', async () => {
        playClick();
        await startGenerationLogic(mainPrompt.value, "Re-rolando pixels...", false);
    });

    toolEdit.addEventListener('click', () => {
        playClick();
        editPrompt.value = '';
        editOverlay.style.display = 'flex';
        editPrompt.focus();
    });

    toolGetPrompt.addEventListener('click', () => {
        // Se quisermos apenas copiar o prompt atual
        playClick();
        navigator.clipboard.writeText(mainPrompt.value);
        showToast('Copiado', 'Prompt original copiado!', 'system');
    });

    // --- EDIÇÃO (INPAINT/STYLE TRANSFER SIMULADO) ---
    btnCancelEdit.addEventListener('click', () => {
        playClick();
        editOverlay.style.display = 'none';
    });

    btnApplyEdit.addEventListener('click', async () => {
        const text = editPrompt.value.trim();
        if (!text) return;
        playClick();
        editOverlay.style.display = 'none';
        
        // Envia instrução de edição para o Gemini junto com a imagem original
        const fullEditPrompt = `Modify the provided image based on this instruction: ${text}. DO NOT change the overall structure drastically unless requested. Maintain the same character: ${mainPrompt.value}`;
        
        await startGenerationLogic(fullEditPrompt, "Aplicando Edição (Magia em processo)...", true);
    });

    // --- SALVAR NO ROSTER ---
    btnSaveRoster.addEventListener('click', async () => {
        if (!generatedImageBase64) return;
        
        let name = saveName.value.trim();
        if (!name) name = "#NovoPersonagem" + Math.floor(Math.random() * 1000);
        if (!name.startsWith('#')) name = '#' + name;

        const charObj = {
            id: crypto.randomUUID(),
            name: name,
            category: 'Conceito Gerado',
            description: saveDesc.value.trim() || mainPrompt.value.trim(),
            images: [generatedImageBase64],
            previewUrl: generatedImageBase64
        };

        try {
            await window.laplataDB.characters.save(charObj);
            showToast('Sucesso', `Personagem ${name} integrado ao Roster!`, 'success');
            playSuccess();
            
            saveName.value = '';
            saveDesc.value = '';
            saveBar.style.display = 'none';

            if (window.apolloQuests) window.apolloQuests.checkAction('create_character');

        } catch (e) {
            console.error(e);
            showToast('Erro', 'Falha ao salvar personagem.', 'system');
            playError();
        }
    });

    // Inicia UI update
    updateGenerateBtnState();
});
