/**
 * Apollo La Plata - Social Posts & Carrossel Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    // --- ELEMENTOS UI ---
    // Controls
    const btnToggles = document.querySelectorAll('.toggle-btn');
    const panelSingle = document.getElementById('panel-single');
    const panelCarousel = document.getElementById('panel-carousel');
    const rosterMini = document.getElementById('roster-mini');
    const inStyle = document.getElementById('s-style');

    // Single Inputs
    const sContext = document.getElementById('s-context');
    const sOverlay = document.getElementById('s-overlay');
    const btnGenerateSingle = document.getElementById('btn-generate-single');

    // Carousel Inputs
    const cTopic = document.getElementById('c-topic');
    const cSlideCount = document.getElementById('c-slide-count');
    const cSlideVal = document.getElementById('c-slide-val');
    const btnGenerateScript = document.getElementById('btn-generate-script');

    // Caption
    const btnGenerateCaption = document.getElementById('btn-generate-caption');
    const captionArea = document.getElementById('caption-area');
    const captionText = document.getElementById('caption-text');
    const btnCopyCaption = document.getElementById('btn-copy-caption');

    // Viewers
    const viewerSingle = document.getElementById('viewer-single');
    const viewerCarousel = document.getElementById('viewer-carousel');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');

    // Single Preview
    const placeholderSingle = document.getElementById('placeholder-single');
    const resultSingle = document.getElementById('result-single');
    const imgSingle = document.getElementById('img-single');
    const btnDownloadSingle = document.getElementById('btn-download-single');

    // Carousel Editor
    const slideList = document.getElementById('slide-list');
    const btnAddSlide = document.getElementById('btn-add-slide');
    const btnGenerateAll = document.getElementById('btn-generate-all');
    const slideTemplate = document.getElementById('slide-template');

    // --- ESTADO LOCAL ---
    let mode = 'single';
    let layout = '1:1';
    let cachedCharacters = [];
    let selectedCharacters = [];
    let isGenerating = false;
    
    // Carousel State
    let slides = []; // { id, prompt, overlay, status, imageUrl, element }

    // Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playSuccess = () => { if (window.apolloSFX) window.apolloSFX.play('success'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };
    const showToast = (title, message, type = 'system') => { if (window.apolloNotifications) window.apolloNotifications.add(title, message, type); };

    // Update range value display
    cSlideCount.addEventListener('input', () => { cSlideVal.innerText = cSlideCount.value; });

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
                
                panelSingle.style.display = mode === 'single' ? 'flex' : 'none';
                panelCarousel.style.display = mode === 'carousel' ? 'flex' : 'none';
                viewerSingle.style.display = mode === 'single' ? 'flex' : 'none';
                viewerCarousel.style.display = mode === 'carousel' ? 'flex' : 'none';
            }
            if (btn.hasAttribute('data-layout')) {
                document.querySelectorAll('[data-layout]').forEach(b => {
                    b.style.background = 'transparent'; b.style.color = '#94a3b8';
                });
                btn.style.background = '#10b981'; btn.style.color = 'white';
                layout = btn.getAttribute('data-layout');
                
                // Adjust Single viewer aspect ratio if visible
                if (mode === 'single') {
                    let ratio = layout.replace(':', '/');
                    resultSingle.style.aspectRatio = ratio;
                    const isHoriz = layout === '16:9';
                    resultSingle.style.width = isHoriz ? '100%' : 'auto';
                    resultSingle.style.height = isHoriz ? 'auto' : '100%';
                }
            }
        });
    });

    // --- FUNÇÕES COMPARTILHADAS ---
    
    // Constrói o prompt forte para postagem social
    function buildSocialPrompt(basePrompt, overlayText, style) {
        let p = `You are a world-class Social Media Content Creator and Graphic Designer.
Create a highly engaging, visually striking image for a social media post.
Aspect Ratio: ${layout}
Visual Style: ${style || 'Professional, high quality'}

SCENE DESCRIPTION:
${basePrompt}
`;
        if (overlayText) {
            p += `
CRITICAL TEXT REQUIREMENT:
The image MUST boldly feature the following exact text written on it:
"${overlayText}"
Make the text huge, readable, and well integrated into the design. Language: Portuguese (PT-BR).`;
        }
        return p;
    }

    // --- MODO SINGLE POST ---
    
    btnGenerateSingle.addEventListener('click', async () => {
        const context = sContext.value.trim();
        if (!context) { showToast('Erro', 'Preencha o contexto da postagem.', 'system'); return; }
        
        playClick();
        isGenerating = true;
        btnGenerateSingle.disabled = true;
        
        viewerSingle.style.display = 'flex';
        placeholderSingle.style.display = 'none';
        resultSingle.style.display = 'block';
        
        loadingOverlay.style.display = 'flex';
        loadingText.innerText = "Criando Postagem...";

        try {
            const settings = await window.laplataSettings.getSettings();
            const finalPrompt = buildSocialPrompt(context, sOverlay.value.trim(), inStyle.value.trim());
            const finalSettings = { ...settings, aspectRatio: layout, sceneContext: "" };

            const resultBase64 = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.generateImage(apiKey, finalPrompt, selectedCharacters, finalSettings, null);
            });

            imgSingle.src = resultBase64;
            playSuccess();
            showToast('Postagem Concluída', 'Imagem gerada com sucesso!', 'success');

            // Salva na Galeria
            await window.laplataDB.gallery.save({
                id: crypto.randomUUID(),
                prompt: `[Social] ${context.substring(0,30)}`,
                imageUrl: resultBase64,
                timestamp: Date.now(),
                aspectRatio: layout
            });

        } catch (e) {
            console.error(e);
            showToast('Erro', e.message, 'system');
            playError();
            resultSingle.style.display = 'none';
            placeholderSingle.style.display = 'flex';
        } finally {
            isGenerating = false;
            btnGenerateSingle.disabled = false;
            loadingOverlay.style.display = 'none';
        }
    });

    btnDownloadSingle.addEventListener('click', () => {
        if (!imgSingle.src) return;
        playClick();
        const link = document.createElement('a');
        link.href = imgSingle.src;
        link.download = `apollo_social_${Date.now()}.png`;
        link.click();
    });

    // --- MODO CARROSSEL ---

    function renderSlides() {
        slideList.innerHTML = '';
        if (slides.length === 0) {
            slideList.innerHTML = `<div class="placeholder-text" style="margin-top: 50px;">
                <div style="font-size: 4rem; opacity: 0.5;">📚</div>
                <div>Descreva um tópico e clique em "Gerar Roteiro".</div>
            </div>`;
            return;
        }

        slides.forEach((slide, index) => {
            const clone = slideTemplate.content.cloneNode(true);
            const el = clone.querySelector('.slide-item');
            el.dataset.id = slide.id;
            
            el.querySelector('.idx').innerText = index + 1;
            
            const inOverlay = el.querySelector('.sl-overlay');
            inOverlay.value = slide.overlay;
            inOverlay.addEventListener('input', (e) => { slide.overlay = e.target.value; });

            const inPrompt = el.querySelector('.sl-prompt');
            inPrompt.value = slide.prompt;
            inPrompt.addEventListener('input', (e) => { slide.prompt = e.target.value; });

            if (slide.status === 'done' && slide.imageUrl) {
                el.classList.add('done');
                const img = el.querySelector('.sl-img');
                img.src = slide.imageUrl;
                img.style.display = 'block';
                el.querySelector('.sl-icon').style.display = 'none';
            } else if (slide.status === 'generating') {
                el.classList.add('generating');
                el.querySelector('.sl-icon').style.display = 'none';
                el.querySelector('.sl-spinner').style.display = 'block';
            } else if (slide.status === 'error') {
                el.classList.add('error');
                el.querySelector('.sl-error').style.display = 'block';
                el.querySelector('.sl-error').innerText = "Erro na geração.";
            }

            el.querySelector('.btn-remove-slide').addEventListener('click', () => {
                playClick();
                slides = slides.filter(s => s.id !== slide.id);
                renderSlides();
            });

            slideList.appendChild(el);
            slide.element = slideList.lastElementChild;
        });
    }

    btnGenerateScript.addEventListener('click', async () => {
        const topic = cTopic.value.trim();
        const count = parseInt(cSlideCount.value);
        if (!topic) { showToast('Erro', 'Insira o tópico do carrossel.', 'system'); return; }

        playClick();
        isGenerating = true;
        btnGenerateScript.disabled = true;
        loadingOverlay.style.display = 'flex';
        loadingText.innerText = "Criando Roteiro...";

        try {
            const prompt = `Crie um roteiro para um carrossel de Instagram/LinkedIn com exatamente ${count} slides sobre o tópico: "${topic}".
Retorne APENAS um array JSON válido. Cada objeto deve conter:
"prompt": Descrição visual detalhada da imagem (Cena de fundo).
"overlayText": O texto curto e chamativo que será escrito por cima da imagem.
Exemplo: [{"prompt": "Homem de terno sorrindo...", "overlayText": "Como dobrar vendas"}]`;

            const resultStr = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.generateText(apiKey, prompt, {}, "You are a Social Media Content Strategist. Output valid JSON only, without markdown tags.");
            });

            let parsed;
            try {
                const clean = resultStr.replace(/```json/gi, '').replace(/```/gi, '').trim();
                parsed = JSON.parse(clean);
            } catch (e) { throw new Error("A IA não retornou um JSON válido."); }

            slides = parsed.map(s => ({
                id: crypto.randomUUID(),
                prompt: s.prompt || "",
                overlay: s.overlayText || "",
                status: 'idle',
                imageUrl: null
            }));

            renderSlides();
            playSuccess();
            showToast('Roteiro Gerado', 'Edite os slides e clique em Gerar Todas as Imagens.', 'success');

        } catch (e) {
            console.error(e);
            showToast('Erro', e.message, 'system');
            playError();
        } finally {
            isGenerating = false;
            btnGenerateScript.disabled = false;
            loadingOverlay.style.display = 'none';
        }
    });

    btnAddSlide.addEventListener('click', () => {
        playClick();
        slides.push({
            id: crypto.randomUUID(),
            prompt: "", overlay: "", status: 'idle', imageUrl: null
        });
        renderSlides();
    });

    btnGenerateAll.addEventListener('click', async () => {
        if (slides.length === 0) return;
        playClick();
        isGenerating = true;
        btnGenerateAll.disabled = true;

        const settings = await window.laplataSettings.getSettings();
        const finalSettings = { ...settings, aspectRatio: '1:1', sceneContext: "" };

        // Forçamos o layout para 1:1 para carrossel (padrão Instagram) no state
        layout = '1:1';

        for (let i = 0; i < slides.length; i++) {
            const slide = slides[i];
            if (slide.status === 'done' && slide.imageUrl) continue; // Pula os já gerados

            slide.status = 'generating';
            renderSlides(); // Atualiza UI para loading deste slide

            try {
                const finalPrompt = buildSocialPrompt(slide.prompt, slide.overlay, inStyle.value.trim());
                
                const resultBase64 = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                    return await window.laplataAI.generateImage(apiKey, finalPrompt, selectedCharacters, finalSettings, null);
                });

                slide.imageUrl = resultBase64;
                slide.status = 'done';

                // Salva na Galeria
                await window.laplataDB.gallery.save({
                    id: crypto.randomUUID(),
                    prompt: `[Carrossel S${i+1}] ${slide.overlay}`,
                    imageUrl: resultBase64,
                    timestamp: Date.now(),
                    aspectRatio: '1:1'
                });

            } catch (e) {
                console.error(e);
                slide.status = 'error';
            }
            renderSlides(); // Atualiza UI do slide (Done ou Error)
        }

        isGenerating = false;
        btnGenerateAll.disabled = false;
        playSuccess();
        showToast('Carrossel Finalizado', 'Todas as imagens foram geradas.', 'success');
    });

    // --- LEGENDA COPY ---
    btnGenerateCaption.addEventListener('click', async () => {
        let contextText = "";
        if (mode === 'single') {
            contextText = sContext.value.trim();
            if (!contextText) { showToast('Erro', 'Preencha o contexto da postagem primeiro.', 'system'); return; }
            contextText += `\nTexto na imagem: ${sOverlay.value}`;
        } else {
            contextText = cTopic.value.trim();
            if (!contextText || slides.length === 0) { showToast('Erro', 'Gere o roteiro do carrossel primeiro.', 'system'); return; }
            contextText += `\nEste é um carrossel de ${slides.length} slides.\nTópicos abordados: ${slides.map(s => s.overlay).join(', ')}`;
        }

        playClick();
        btnGenerateCaption.disabled = true;
        btnGenerateCaption.innerText = "⏳ Gerando...";

        try {
            const prompt = `Crie uma legenda (copy) persuasiva para um post de Instagram/LinkedIn.
Contexto: ${contextText}
A legenda deve ser engajadora, ter uma chamada para ação (CTA) no final e incluir de 3 a 5 hashtags relevantes. Não coloque aspas em volta da legenda.`;

            const resultStr = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.generateText(apiKey, prompt, {}, "You are an expert Social Media Copywriter.");
            });

            captionText.value = resultStr;
            captionArea.style.display = 'block';
            playSuccess();
            showToast('Legenda Gerada', 'Sua copy está pronta!', 'success');

        } catch (e) {
            console.error(e);
            showToast('Erro', 'Falha ao gerar legenda', 'system');
            playError();
        } finally {
            btnGenerateCaption.disabled = false;
            btnGenerateCaption.innerText = "💬 Gerar Legenda (Copy)";
        }
    });

    btnCopyCaption.addEventListener('click', () => {
        if (!captionText.value) return;
        playClick();
        navigator.clipboard.writeText(captionText.value);
        showToast('Copiado', 'Legenda copiada para a área de transferência', 'system');
    });

});
