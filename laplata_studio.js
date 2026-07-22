/**
 * Apollo La Plata - Image Studio Logic
 * Gerencia a lógica de laplata_studio.html
 */

document.addEventListener('DOMContentLoaded', async () => {
    // --- ELEMENTOS UI ---
    // Painel Esquerdo
    const aspectRatioSelect = document.getElementById('aspect-ratio');
    const globalContextInput = document.getElementById('global-context');
    const negativePromptInput = document.getElementById('negative-prompt');
    const rosterMini = document.getElementById('roster-mini');
    
    const refDropzone = document.getElementById('ref-dropzone');
    const refPlaceholder = document.getElementById('ref-placeholder');
    const refPreview = document.getElementById('ref-preview');
    const btnRemoveRef = document.getElementById('btn-remove-ref');
    const refFileInput = document.getElementById('ref-file');
    
    const mainPrompt = document.getElementById('main-prompt');
    const btnEnhance = document.getElementById('btn-enhance');
    const btnGenerate = document.getElementById('btn-generate');

    // Painel Direito
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const viewerPlaceholder = document.getElementById('viewer-placeholder');
    const resultWrapper = document.getElementById('result-wrapper');
    const resultImage = document.getElementById('result-image');
    
    const toolDownload = document.getElementById('tool-download');
    const toolReroll = document.getElementById('tool-reroll');

    // --- ESTADO LOCAL ---
    let referenceImageBase64 = null;
    let generatedImageBase64 = null;
    let isGenerating = false;
    let cachedCharacters = [];

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
        btnEnhance.disabled = isGenerating || text.length === 0;
    };

    mainPrompt.addEventListener('input', updateGenerateBtnState);

    // --- CARREGAR ROSTER MINI ---
    async function loadRosterMini() {
        try {
            cachedCharacters = await window.laplataDB.characters.getAll();
            rosterMini.innerHTML = '';
            
            if (cachedCharacters.length === 0) {
                rosterMini.innerHTML = '<div style="color: #64748b; font-size: 0.8rem;">Sem personagens. Crie no Laboratório primeiro.</div>';
                return;
            }

            cachedCharacters.forEach(char => {
                const btn = document.createElement('button');
                btn.className = 'char-tag-btn';
                
                let imgHtml = '';
                if (char.previewUrl) {
                    imgHtml = `<img src="${char.previewUrl}" alt="Ref">`;
                }
                
                btn.innerHTML = `${imgHtml} ${char.name}`;
                btn.title = char.description || 'Sem descrição visual';
                
                btn.addEventListener('click', () => {
                    playClick();
                    // Adiciona a tag no final ou onde o cursor estiver (simplificando: no final)
                    if (!mainPrompt.value.includes(char.name)) {
                        mainPrompt.value = mainPrompt.value ? `${mainPrompt.value} ${char.name}` : char.name;
                        updateGenerateBtnState();
                    }
                });
                
                rosterMini.appendChild(btn);
            });
        } catch (e) {
            console.error("Erro ao carregar roster", e);
            rosterMini.innerHTML = '<div style="color: #ef4444;">Erro ao carregar</div>';
        }
    }

    // --- UPLOAD DE REFERÊNCIA ---
    refDropzone.addEventListener('click', (e) => {
        if (e.target !== btnRemoveRef && !isGenerating) refFileInput.click();
    });

    refFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            if (!file.type.startsWith('image/')) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    let width = img.width;
                    let height = img.height;
                    const maxDim = 1024;
                    if (width > height && width > maxDim) { height *= maxDim / width; width = maxDim; } 
                    else if (height > maxDim) { width *= maxDim / height; height = maxDim; }
                    canvas.width = width; canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    
                    referenceImageBase64 = canvas.toDataURL('image/jpeg', 0.8);
                    refPlaceholder.style.display = 'none';
                    refPreview.src = referenceImageBase64;
                    refPreview.style.display = 'block';
                    btnRemoveRef.style.display = 'block';
                    playClick();
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    btnRemoveRef.addEventListener('click', (e) => {
        e.stopPropagation();
        referenceImageBase64 = null;
        refPlaceholder.style.display = 'block';
        refPreview.style.display = 'none';
        refPreview.src = '';
        btnRemoveRef.style.display = 'none';
        refFileInput.value = '';
        playClick();
    });

    // --- IA: MELHORAR PROMPT ---
    btnEnhance.addEventListener('click', async () => {
        const text = mainPrompt.value.trim();
        if (!text || isGenerating) return;

        playClick();
        isGenerating = true;
        btnEnhance.innerHTML = "⏳";
        updateGenerateBtnState();

        try {
            const sysInstruction = "You are an expert prompt engineer. Enhance the following prompt for image generation, adding details about lighting, composition, and mood. Keep character names intact.";
            const expanded = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                // laplata_ai tem a função genérica generateText
                return await window.laplataAI.generateText(apiKey, `Original: ${text}\nGlobal Context: ${globalContextInput.value}\n\nEnhance:`, {}, sysInstruction);
            });

            mainPrompt.value = expanded;
            showToast('Sucesso', 'Prompt mágico aplicado!', 'success');
            playSuccess();
        } catch (e) {
            console.error(e);
            showToast('Erro', 'Falha ao melhorar prompt.', 'system');
            playError();
        } finally {
            isGenerating = false;
            btnEnhance.innerHTML = "✨ Melhorar";
            updateGenerateBtnState();
        }
    });

    // --- IA: GERAR IMAGEM ---
    btnGenerate.addEventListener('click', async () => {
        const text = mainPrompt.value.trim();
        if (!text || isGenerating) return;

        playClick();
        await startGenerationLogic(text, "Luz, Câmera... Ação!");
    });

    async function startGenerationLogic(promptText, loadingMsg) {
        const db = await window.laplataDB.openDB();
        const currencies = await window.laplataDB.getCurrencies(db);
        if (currencies.gasolina < 1) {
            if (window.apolloNotifications) window.apolloNotifications.add("Sem Combustível", "Você precisa de Gasolina para gerar imagens no Laboratório.", "error");
            if (window.apolloSFX) window.apolloSFX.play('error');
            if (window.apolloCopilot) window.apolloCopilot.react("low_gas");
            return;
        }

        isGenerating = true;
        updateGenerateBtnState();
        loadingText.innerText = loadingMsg;
        loadingOverlay.style.display = 'flex';
        
        viewerPlaceholder.style.display = 'flex';
        resultWrapper.style.display = 'none';

        try {
            const settings = await window.laplataSettings.getSettings();
            
            // Injeta configurações específicas da tela
            let finalSettings = { 
                ...settings,
                aspectRatio: aspectRatioSelect.value,
                globalContext: globalContextInput.value.trim(),
                sceneContext: "",
                negativePrompt: negativePromptInput.value.trim()
            };

            const resultBase64 = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.generateImage(apiKey, promptText, cachedCharacters, finalSettings, referenceImageBase64);
            });

            generatedImageBase64 = resultBase64;
            
            // Mostra na Tela
            viewerPlaceholder.style.display = 'none';
            resultImage.src = generatedImageBase64;
            resultWrapper.style.display = 'inline-block';
            
            // Ajusta CSS do wrapper
            const ratio = finalSettings.aspectRatio.split(':');
            resultWrapper.style.aspectRatio = `${ratio[0]}/${ratio[1]}`;
            resultWrapper.style.width = ratio[0] > ratio[1] ? '100%' : 'auto';
            resultWrapper.style.height = ratio[0] > ratio[1] ? 'auto' : '100%';

            playSuccess();
            showToast('Corte!', 'Cena renderizada com perfeição.', 'quest');

            // Salvar na Galeria
            const finalSavePrompt = `[Estúdio] ${promptText}`;
            await window.laplataDB.gallery.save({
                id: crypto.randomUUID(),
                prompt: finalSavePrompt,
                imageUrl: generatedImageBase64,
                timestamp: Date.now(),
                aspectRatio: finalSettings.aspectRatio
            });

            // Deduzir 1 Gasolina e Atualizar Navbar
            await window.laplataDB.updateCurrency(db, 'gasolina', -1);
            window.laplataDB.updateTopNav(db);

            if (window.apolloQuests) window.apolloQuests.addProgress('image');
            if (window.apolloCopilot && Math.random() > 0.5) window.apolloCopilot.react("generate_success");

        } catch (e) {
            console.error("Geração falhou:", e);
            showToast('Erro', e.message, 'system');
            playError();
        } finally {
            isGenerating = false;
            updateGenerateBtnState();
            loadingOverlay.style.display = 'none';
        }
    }

    // --- FERRAMENTAS RESULTADO ---
    toolDownload.addEventListener('click', () => {
        if (!generatedImageBase64) return;
        playClick();
        const link = document.createElement('a');
        link.href = generatedImageBase64;
        link.download = `apollo_scene_${Date.now()}.jpg`;
        link.click();
    });

    toolReroll.addEventListener('click', async () => {
        playClick();
        await startGenerationLogic(mainPrompt.value, "Gravando Take 2...");
    });

    // Inicia a Tela
    loadRosterMini();
    updateGenerateBtnState();
});
