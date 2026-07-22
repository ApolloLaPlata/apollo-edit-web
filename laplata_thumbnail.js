/**
 * Apollo La Plata - Thumbnail Studio Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    // --- ESTILOS ---
    const THUMBNAIL_STYLES = [
        { id: 'mrbeast', label: 'Alto Contraste / Viral (Estilo MrBeast)', prompt: 'High saturation, expressive face close-up, bright background, bold outcome' },
        { id: 'tech_review', label: 'Review Tech (MKBHD/The Verge)', prompt: 'Clean, minimalist, product focus, matte background, professional lighting' },
        { id: 'gaming', label: 'Gaming / Gameplay', prompt: 'Action packed, vibrant neon colors, game assets, dramatic lighting, 3D text' },
        { id: 'vlog', label: 'Vlog Lifestyle', prompt: 'Natural lighting, bright, warm tones, authentic expression, blurred background' },
        { id: 'educational', label: 'Educacional / Explainer', prompt: 'Vector illustrations, flat design, clean typography, split screen comparison' },
        { id: 'podcast', label: 'Podcast / Entrevista', prompt: 'Professional studio lighting, dark elegant background, subject focus' },
        { id: 'horror_story', label: 'Terror / True Crime', prompt: 'Dark, vignette, high contrast, red highlights, mysterious atmosphere' },
    ];

    // --- ELEMENTOS UI ---
    // Controls
    const btnToggles = document.querySelectorAll('.toggle-btn');
    const panelStructured = document.getElementById('panel-structured');
    const panelCustom = document.getElementById('panel-custom');
    
    // Inputs Structured
    const inTitle = document.getElementById('t-title');
    const inHook = document.getElementById('t-hook');
    const inColor = document.getElementById('t-color');
    const inPosition = document.getElementById('t-position');
    const inStyle = document.getElementById('t-style');
    const inBg = document.getElementById('t-bg');
    
    // Input Custom
    const inCustom = document.getElementById('t-custom');

    // Roster & Refs
    const rosterMini = document.getElementById('roster-mini');
    const refGallery = document.getElementById('ref-gallery');
    const btnAddRef = document.getElementById('btn-add-ref');
    const refFileInput = document.getElementById('ref-file');

    // Buttons & Result
    const btnGenerate = document.getElementById('btn-generate');
    const viewerPlaceholder = document.getElementById('viewer-placeholder');
    const resultWrapper = document.getElementById('result-wrapper');
    const resultImage = document.getElementById('result-image');
    const crossFormatBar = document.getElementById('cross-format-bar');
    const btnCrossFormat = document.getElementById('btn-cross-format');

    // Overlays
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const editOverlay = document.getElementById('edit-overlay');
    const editInstruction = document.getElementById('edit-instruction');
    const btnCancelEdit = document.getElementById('btn-cancel-edit');
    const btnApplyEdit = document.getElementById('btn-apply-edit');
    const overlayTools = document.getElementById('overlay-tools');

    // Hover Tools
    const toolDownload = document.getElementById('tool-download');
    const toolReroll = document.getElementById('tool-reroll');
    const toolEdit = document.getElementById('tool-edit');
    const toolPrompt = document.getElementById('tool-prompt');

    // --- ESTADO LOCAL ---
    let mode = 'structured';
    let layout = '16:9';
    let referenceImages = []; // Array of base64
    let cachedCharacters = [];
    let selectedCharacters = [];
    let isGenerating = false;
    let generatedResult = null; // { imageUrl, prompt }

    // Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playSuccess = () => { if (window.apolloSFX) window.apolloSFX.play('success'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };
    const showToast = (title, message, type = 'system') => { if (window.apolloNotifications) window.apolloNotifications.add(title, message, type); };

    // Init Styles
    THUMBNAIL_STYLES.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id; opt.innerText = s.label;
        inStyle.appendChild(opt);
    });

    // --- CARREGAR ROSTER ---
    try {
        cachedCharacters = await window.laplataDB.characters.getAll();
        rosterMini.innerHTML = '';
        if (cachedCharacters.length === 0) rosterMini.innerHTML = '<div style="color: #64748b; font-size: 0.8rem;">Sem personagens cadastrados.</div>';
        
        cachedCharacters.forEach(char => {
            const btn = document.createElement('button');
            btn.className = 'char-tag-btn';
            btn.innerHTML = (char.previewUrl ? `<img src="${char.previewUrl}"> ` : '') + char.name;
            btn.addEventListener('click', () => {
                playClick();
                btn.classList.toggle('selected');
                if (btn.classList.contains('selected')) selectedCharacters.push(char);
                else selectedCharacters = selectedCharacters.filter(c => c.id !== char.id);
            });
            rosterMini.appendChild(btn);
        });
    } catch (e) { console.error(e); }

    // --- TOGGLES (MODO & LAYOUT) ---
    btnToggles.forEach(btn => {
        btn.addEventListener('click', () => {
            if (isGenerating) return;
            playClick();
            if (btn.hasAttribute('data-mode')) {
                document.querySelectorAll('[data-mode]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                mode = btn.getAttribute('data-mode');
                panelStructured.style.display = mode === 'structured' ? 'flex' : 'none';
                panelCustom.style.display = mode === 'custom' ? 'flex' : 'none';
            }
            if (btn.hasAttribute('data-layout')) {
                document.querySelectorAll('[data-layout]').forEach(b => {
                    b.style.background = 'transparent'; b.style.color = '#94a3b8'; b.style.border = 'none';
                });
                btn.style.background = '#334155'; btn.style.color = 'white'; btn.style.border = '1px solid #475569';
                layout = btn.getAttribute('data-layout');
                updateCrossFormatBar();
            }
        });
    });

    // --- REFERÊNCIAS ---
    btnAddRef.addEventListener('click', () => { if (!isGenerating) refFileInput.click(); });

    refFileInput.addEventListener('change', (e) => {
        if (!e.target.files) return;
        Array.from(e.target.files).forEach(file => {
            if (!file.type.startsWith('image/')) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    let width = img.width, height = img.height;
                    const maxDim = 800; // Otimizado
                    if (width > height && width > maxDim) { height *= maxDim / width; width = maxDim; } 
                    else if (height > maxDim) { width *= maxDim / height; height = maxDim; }
                    canvas.width = width; canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    
                    const base64 = canvas.toDataURL('image/jpeg', 0.8);
                    referenceImages.push(base64);
                    renderRefs();
                    playClick();
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        });
        refFileInput.value = '';
    });

    const btnPasteRef = document.getElementById('btn-paste-ref');
    if (btnPasteRef) {
        btnPasteRef.addEventListener('click', () => {
            const b64 = window.laplataInventory.paste();
            if (b64) {
                referenceImages.push(b64);
                renderRefs();
                playClick();
                showToast('Colado', 'Imagem carregada do Inventário!', 'success');
            } else {
                playError();
                showToast('Aviso', 'O inventário está vazio!', 'system');
            }
        });
    }

    function renderRefs() {
        // Remove todos os items criados (mantém só o botão de add)
        document.querySelectorAll('.ref-gallery .ref-item:not(.ref-add)').forEach(el => el.remove());
        
        referenceImages.forEach((img64, idx) => {
            const div = document.createElement('div');
            div.className = 'ref-item';
            div.innerHTML = `
                <img src="${img64}">
                <button class="btn-remove-ref">X</button>
            `;
            div.querySelector('.btn-remove-ref').addEventListener('click', (e) => {
                e.stopPropagation();
                referenceImages.splice(idx, 1);
                renderRefs();
                playClick();
            });
            refGallery.insertBefore(div, btnAddRef);
        });
        if (btnPasteRef) {
            refGallery.appendChild(btnPasteRef);
        }
    }

    // --- CROSS FORMAT ---
    function updateCrossFormatBar() {
        if (!generatedResult) {
            crossFormatBar.style.display = 'none';
            return;
        }
        crossFormatBar.style.display = 'flex';
        const target = layout === '16:9' ? '9:16' : '16:9';
        const label = target === '16:9' ? 'Horizontal (16:9)' : 'Vertical (9:16)';
        btnCrossFormat.innerText = `Gerar Versão ${label}`;
    }

    btnCrossFormat.addEventListener('click', async () => {
        playClick();
        // Troca o layout na UI e clica gerar
        const target = layout === '16:9' ? '9:16' : '16:9';
        const btn = document.querySelector(`[data-layout="${target}"]`);
        if (btn) btn.click();
        await startGenerationLogic("Convertendo Formato...");
    });

    // --- GERAÇÃO CORE ---
    btnGenerate.addEventListener('click', async () => {
        playClick();
        await startGenerationLogic("Renderizando Design...");
    });

    async function startGenerationLogic(loadingMsg) {
        if (mode === 'structured') {
            if (!inTitle.value.trim() && !inBg.value.trim()) {
                showToast('Erro', 'Preencha o Título ou Fundo.', 'system'); return;
            }
        } else {
            if (!inCustom.value.trim()) {
                showToast('Erro', 'Insira um prompt.', 'system'); return;
            }
        }

        const db = await window.laplataDB.openDB();
        const currencies = await window.laplataDB.getCurrencies(db);
        if (currencies.gasolina < 1) {
            if (window.apolloNotifications) window.apolloNotifications.add("Sem Combustível", "Você precisa de Gasolina para gerar imagens.", "error");
            if (window.apolloSFX) window.apolloSFX.play('error');
            if (window.apolloCopilot) window.apolloCopilot.react("low_gas");
            return;
        }

        isGenerating = true;
        btnGenerate.disabled = true;
        
        viewerPlaceholder.style.display = 'none';
        resultWrapper.style.display = 'block';
        loadingOverlay.style.display = 'flex';
        loadingText.innerText = loadingMsg;
        editOverlay.style.display = 'none';
        overlayTools.style.display = 'none'; // Esconde ferramentas durante geração

        // CSS Ajuste
        const isHoriz = layout === '16:9';
        resultWrapper.style.aspectRatio = layout.replace(':', '/');
        resultWrapper.style.width = isHoriz ? '100%' : 'auto';
        resultWrapper.style.height = isHoriz ? 'auto' : '100%';

        try {
            const settings = await window.laplataSettings.getSettings();
            
            let finalPrompt = "";
            let promptLabel = "";

            if (mode === 'structured') {
                const styleObj = THUMBNAIL_STYLES.find(s => s.id === inStyle.value);
                const stylePrompt = styleObj ? styleObj.prompt : "";
                
                finalPrompt = `You are a professional YouTube Thumbnail Designer.
Create a highly engaging thumbnail image with the following requirements:
- Aspect Ratio: ${layout}
- Subject Position: ${inPosition.value}
- Background: ${inBg.value || 'dynamic and eye-catching'}
- Style: ${stylePrompt}
- Text Color Theme: ${inColor.value}

IMPORTANT TEXT TO RENDER IN THE IMAGE (Make it HUGE, bold, readable, and 3D if possible):
Main Text: "${inTitle.value}"
Secondary Text: "${inHook.value}"

Ensure the text is extremely clear and placed where it does not obscure the main subject.`;
                promptLabel = `[Thumbnail] ${inTitle.value}`;
            } else {
                finalPrompt = inCustom.value;
                promptLabel = `[Thumb Custom] ${inCustom.value.substring(0, 20)}`;
            }

            // Vamos usar o motor base `laplata_ai.js` `generateImage`
            // Note: O laplata_ai original aceita apenas a primeira imagem de referência base64
            const refBase64 = referenceImages.length > 0 ? referenceImages[0] : null;
            
            const finalSettings = {
                ...settings,
                aspectRatio: layout,
                sceneContext: "" // Zera para não conflitar
            };

            const resultBase64 = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.generateImage(apiKey, finalPrompt, selectedCharacters, finalSettings, refBase64);
            });

            resultImage.src = resultBase64;
            generatedResult = {
                imageUrl: resultBase64,
                prompt: promptLabel
            };

            // Deduzir 1 Gasolina e Atualizar Navbar
            await window.laplataDB.updateCurrency(db, 'gasolina', -1);
            window.laplataDB.updateTopNav(db);

            // Adicionar progresso à missão
            if (window.apolloQuests) window.apolloQuests.addProgress('image');
            if (window.apolloCopilot && Math.random() > 0.5) window.apolloCopilot.react("generate_success");

            playSuccess();
            showToast('Design Concluído', 'Sua miniatura está pronta!', 'success');
            
            // Salva na Galeria
            await window.laplataDB.gallery.save({
                id: crypto.randomUUID(),
                prompt: `${promptLabel} (${layout})`,
                imageUrl: resultBase64,
                timestamp: Date.now(),
                aspectRatio: layout
            });

        } catch (e) {
            console.error(e);
            showToast('Erro', e.message, 'system');
            playError();
            resultWrapper.style.display = 'none';
            viewerPlaceholder.style.display = 'flex';
        } finally {
            isGenerating = false;
            btnGenerate.disabled = false;
            loadingOverlay.style.display = 'none';
            overlayTools.style.display = 'flex'; // Volta as ferramentas
            updateCrossFormatBar();
        }
    }

    // --- HOVER TOOLS ---
    toolDownload.addEventListener('click', () => {
        if (!generatedResult) return;
        playClick();
        const link = document.createElement('a');
        link.href = generatedResult.imageUrl;
        link.download = `apollo_thumb_${layout.replace(':','_')}_${Date.now()}.png`;
        link.click();
    });

    toolReroll.addEventListener('click', async () => {
        playClick();
        await startGenerationLogic("Tentando outra ideia...");
    });

    toolEdit.addEventListener('click', () => {
        playClick();
        editOverlay.style.display = 'flex';
        overlayTools.style.display = 'none';
        editInstruction.focus();
    });

    btnCancelEdit.addEventListener('click', () => {
        playClick();
        editOverlay.style.display = 'none';
        overlayTools.style.display = 'flex';
        editInstruction.value = '';
    });

    // Edição via Inpainting / Edit Prompt
    btnApplyEdit.addEventListener('click', async () => {
        const text = editInstruction.value.trim();
        if (!text || !generatedResult) return;

        playClick();
        editOverlay.style.display = 'none';
        loadingText.innerText = "Aplicando magia de edição...";
        loadingOverlay.style.display = 'flex';
        isGenerating = true;

        try {
            // Em laplata_ai.js temos a função `editImage` que recebe base64 + instrução
            const resultBase64 = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.editImage(apiKey, generatedResult.imageUrl, text);
            });

            resultImage.src = resultBase64;
            generatedResult.imageUrl = resultBase64;

            playSuccess();
            showToast('Editado!', 'Modificações aplicadas.', 'success');

            // Salva na galeria a versão editada
            await window.laplataDB.gallery.save({
                id: crypto.randomUUID(),
                prompt: `[Editado Thumb: ${text}]`,
                imageUrl: resultBase64,
                timestamp: Date.now(),
                aspectRatio: layout
            });

        } catch (e) {
            console.error(e);
            showToast('Falha na Edição', e.message, 'system');
            playError();
        } finally {
            isGenerating = false;
            loadingOverlay.style.display = 'none';
            overlayTools.style.display = 'flex';
            editInstruction.value = '';
        }
    });

    toolPrompt.addEventListener('click', async () => {
        if (!generatedResult) return;
        playClick();
        loadingText.innerText = "Lendo imagem...";
        loadingOverlay.style.display = 'flex';
        isGenerating = true;

        try {
            // Analisador de Visão para extrair o prompt
            const result = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                const { GoogleGenAI } = await import('https://esm.sh/@google/genai@0.1.2');
                const ai = new GoogleGenAI({ apiKey });
                const mime = generatedResult.imageUrl.match(/^data:(image\/\w+);base64,/)[1];
                const base64Data = generatedResult.imageUrl.replace(/^data:image\/\w+;base64,/, "");

                const sysInstruction = "Describe this image in extreme detail as an image generation prompt. Include texts, layouts, lighting, background, and character positions.";

                const response = await ai.models.generateContent({
                    model: 'gemini-2.5-flash',
                    contents: [{ role: "user", parts: [
                        { text: "Describe." },
                        { inlineData: { data: base64Data, mimeType: mime } }
                    ]}],
                    config: { systemInstruction: { parts: [{ text: sysInstruction }] } }
                });

                return response.text || "";
            });

            // Vai para a aba Custom e preenche
            document.querySelector('[data-mode="custom"]').click();
            inCustom.value = result;
            showToast('Prompt Extraído', 'Prompt copiado para a aba Livre!', 'success');
            playSuccess();

        } catch (e) {
            console.error(e);
            showToast('Erro', 'Falha ao ler imagem', 'system');
            playError();
        } finally {
            isGenerating = false;
            loadingOverlay.style.display = 'none';
            overlayTools.style.display = 'flex';
        }
    });

});
