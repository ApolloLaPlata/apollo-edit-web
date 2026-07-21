/**
 * Apollo La Plata - Script Room Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    // --- ELEMENTOS UI ---
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Outputs
    const resultBox = document.getElementById('result-box');
    const resultPlaceholderText = document.getElementById('result-placeholder-text');
    const outputLoading = document.getElementById('output-loading');
    const outputProgress = document.getElementById('output-progress');
    const btnCopy = document.getElementById('btn-copy');

    // Tab: Enhancer
    const enhancerPrompt = document.getElementById('enhancer-prompt');
    const enhancerStyle = document.getElementById('enhancer-style');
    const btnRunEnhancer = document.getElementById('btn-run-enhancer');

    // Tab: Script
    const scriptText = document.getElementById('script-text');
    const scriptStyle = document.getElementById('script-style');
    const btnRunScript = document.getElementById('btn-run-script');

    // Tab: Style
    const styleDropzone = document.getElementById('style-dropzone');
    const styleFileInput = document.getElementById('style-file');
    const stylePreview = document.getElementById('style-preview');
    const stylePlaceholder = document.getElementById('style-placeholder');
    const btnRemoveStyle = document.getElementById('btn-remove-style');
    const btnRunStyle = document.getElementById('btn-run-style');

    // Tab: Motion
    const motionPrompts = document.getElementById('motion-prompts');
    const btnRunMotion = document.getElementById('btn-run-motion');

    // Tab: VEO
    const veoText = document.getElementById('veo-text');
    const checkVeoVideo = document.getElementById('check-veo-video');
    const btnRunVeo = document.getElementById('btn-run-veo');

    let currentTab = 'tab-enhancer';
    let isProcessing = false;
    let styleBase64 = null;
    let characters = []; // Cache dos personagens

    // Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playSuccess = () => { if (window.apolloSFX) window.apolloSFX.play('success'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };
    const showToast = (title, message, type = 'system') => { if (window.apolloNotifications) window.apolloNotifications.add(title, message, type); };

    // Set Output
    function setOutput(text) {
        if (!text) {
            resultBox.innerHTML = `<div style="opacity: 0.3; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 15px;">
                        <span style="font-size: 3rem;">🤖</span>
                        <span>Aguardando instruções...</span>
                    </div>`;
            btnCopy.style.display = 'none';
        } else {
            resultBox.textContent = text;
            btnCopy.style.display = 'block';
            btnCopy.classList.remove('copied');
            btnCopy.innerText = 'Copiar';
        }
    }

    // Navegação de Abas
    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            if (isProcessing) return;
            playClick();
            tabs.forEach(t => { t.classList.remove('active'); t.classList.remove('active-veo'); });
            tabContents.forEach(c => c.classList.remove('active'));
            
            const target = btn.getAttribute('data-target');
            if (target === 'tab-veo') btn.classList.add('active-veo');
            else btn.classList.add('active');
            
            document.getElementById(target).classList.add('active');
            currentTab = target;
            setOutput('');
        });
    });

    // Checkbox customizado
    checkVeoVideo.addEventListener('click', () => {
        if (isProcessing) return;
        playClick();
        checkVeoVideo.classList.toggle('checked');
    });

    // --- CARREGAMENTO DB ---
    try {
        characters = await window.laplataDB.characters.getAll();
    } catch(e) { console.error(e); }

    // --- UPLOAD IMAGEM (ESTILOS) ---
    styleDropzone.addEventListener('click', (e) => {
        if (e.target !== btnRemoveStyle && !isProcessing) styleFileInput.click();
    });

    styleFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            if (!file.type.startsWith('image/')) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    let width = img.width, height = img.height;
                    const maxDim = 1024;
                    if (width > height && width > maxDim) { height *= maxDim / width; width = maxDim; } 
                    else if (height > maxDim) { width *= maxDim / height; height = maxDim; }
                    canvas.width = width; canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    
                    styleBase64 = canvas.toDataURL('image/jpeg', 0.8);
                    stylePlaceholder.style.display = 'none';
                    styleDropzone.querySelector('span:nth-of-type(2)').style.display = 'none';
                    stylePreview.src = styleBase64;
                    stylePreview.style.display = 'block';
                    btnRemoveStyle.style.display = 'block';
                    btnRunStyle.disabled = false;
                    playClick();
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    btnRemoveStyle.addEventListener('click', (e) => {
        e.stopPropagation();
        styleBase64 = null;
        stylePlaceholder.style.display = 'inline';
        styleDropzone.querySelector('span:nth-of-type(2)').style.display = 'inline';
        stylePreview.style.display = 'none';
        stylePreview.src = '';
        btnRemoveStyle.style.display = 'none';
        btnRunStyle.disabled = true;
        styleFileInput.value = '';
        playClick();
    });

    // --- CÓPIA ---
    btnCopy.addEventListener('click', () => {
        playClick();
        navigator.clipboard.writeText(resultBox.textContent);
        btnCopy.classList.add('copied');
        btnCopy.innerText = 'Copiado!';
        setTimeout(() => {
            btnCopy.classList.remove('copied');
            btnCopy.innerText = 'Copiar';
        }, 2000);
    });

    // --- FUNÇÕES CORE ---
    async function executeTabLogic(btnElement, loadingTextMsg, logicFn) {
        if (isProcessing) return;
        playClick();
        isProcessing = true;
        btnElement.disabled = true;
        outputLoading.style.display = 'flex';
        outputProgress.innerText = '';
        setOutput('');
        
        try {
            const settings = await window.laplataSettings.getSettings();
            const result = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await logicFn(apiKey, settings);
            });
            setOutput(result);
            playSuccess();
        } catch(e) {
            console.error(e);
            setOutput(`ERRO: ${e.message}`);
            playError();
            showToast('Erro na IA', e.message, 'system');
        } finally {
            isProcessing = false;
            btnElement.disabled = false;
            outputLoading.style.display = 'none';
        }
    }

    // 1. Refinador
    btnRunEnhancer.addEventListener('click', () => {
        const text = enhancerPrompt.value.trim();
        if (!text) return;
        executeTabLogic(btnRunEnhancer, "Refinando...", async (apiKey, settings) => {
            const sys = "You are an expert prompt engineer. You will receive a simple concept and a visual style. Rewrite the concept into a highly detailed text-to-image prompt. Return ONLY the final prompt.";
            return await window.laplataAI.generateText(apiKey, `Concept: ${text}\nStyle: ${enhancerStyle.value}\n`, settings, sys);
        });
    });

    // 2. Roteiro
    btnRunScript.addEventListener('click', () => {
        const text = scriptText.value.trim();
        if (!text) return;
        executeTabLogic(btnRunScript, "Quebrando Cenas...", async (apiKey, settings) => {
            const sys = "You are a storyboard artist and prompt engineer. Read the narrative text and break it down into sequential image generation prompts. Each scene should be one line. Include the Visual Style provided in every prompt. Return a clean list of prompts, no conversational text.";
            return await window.laplataAI.generateText(apiKey, `Narrative: ${text}\nVisual Style: ${scriptStyle.value}\n`, settings, sys);
        });
    });

    // 3. Estilos
    btnRunStyle.addEventListener('click', async () => {
        if (!styleBase64) return;
        // Precisamos importar o SDK diretamente pois a laplata_ai.js só previu gerar imagem e gerar texto simples, não Image-to-Text puro (vision)
        // Então faremos o fetch da IA manualmente usando ESM como no laplata_ai.
        
        playClick();
        isProcessing = true;
        btnRunStyle.disabled = true;
        outputLoading.style.display = 'flex';
        setOutput('');
        
        try {
            const result = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                const { GoogleGenAI } = await import('https://esm.sh/@google/genai@0.1.2');
                const ai = new GoogleGenAI({ apiKey });
                
                const mime = styleBase64.match(/^data:(image\/\w+);base64,/)[1];
                const base64Data = styleBase64.replace(/^data:image\/\w+;base64,/, "");

                const sysInstruction = "You are an expert Art Director and prompt engineer. Analyze the attached image and describe ITS VISUAL STYLE ONLY in extreme detail. DO NOT describe the subject (the person, animal, or specific object). Describe ONLY the lighting, color grading, art medium, brushstrokes, camera lens, aesthetics, and mood. Provide the output as a clean prompt fragment.";

                const response = await ai.models.generateContent({
                    model: 'gemini-2.5-flash',
                    contents: [{ role: "user", parts: [
                        { text: "Extract the style from this image." },
                        { inlineData: { data: base64Data, mimeType: mime } }
                    ]}],
                    config: { systemInstruction: { parts: [{ text: sysInstruction }] } }
                });

                let txt = response.text || "";
                return txt.replace(/```\w*\n?/g, '').replace(/```/g, '').trim();
            });
            setOutput(result);
            playSuccess();
        } catch(e) {
            console.error(e);
            setOutput(`ERRO: ${e.message}`);
            playError();
            showToast('Erro', 'Falha ao analisar imagem.', 'system');
        } finally {
            isProcessing = false;
            btnRunStyle.disabled = false;
            outputLoading.style.display = 'none';
        }
    });

    // 4. Motion Animador
    btnRunMotion.addEventListener('click', async () => {
        const text = motionPrompts.value.trim();
        if (!text) return;
        
        const lines = text.split('\n').filter(l => l.trim());
        if (lines.length === 0) return;

        playClick();
        isProcessing = true;
        btnRunMotion.disabled = true;
        outputLoading.style.display = 'flex';
        setOutput('');
        
        let finalOutput = [];
        
        try {
            for (let i = 0; i < lines.length; i++) {
                outputProgress.innerText = `(${i+1}/${lines.length})`;
                const result = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                    const sys = "You are a Prompt Engineer for AI Video Generators (Runway, Kling, Veo). Rewrite the provided image prompt into a VIDEO MOTION PROMPT. Describe the movement, camera action (pan, tilt, tracking), and dynamic lighting. Keep it under 2 sentences. No prefixes.";
                    return await window.laplataAI.generateText(apiKey, `Original Image Prompt: ${lines[i]}\n\nVideo Prompt:`, {}, sys);
                });
                finalOutput.push(result);
            }
            setOutput(finalOutput.join('\n\n'));
            playSuccess();
            showToast('Animações', 'Prompts convertidos para vídeo.', 'success');
        } catch(e) {
            console.error(e);
            setOutput(finalOutput.join('\n\n') + `\n\n[ERRO NO PROCESSAMENTO DO RESTANTE: ${e.message}]`);
            playError();
        } finally {
            isProcessing = false;
            btnRunMotion.disabled = false;
            outputLoading.style.display = 'none';
            outputProgress.innerText = '';
        }
    });

    // 5. VEO Export
    btnRunVeo.addEventListener('click', async () => {
        const text = veoText.value.trim();
        if (!text) return;

        playClick();
        isProcessing = true;
        btnRunVeo.disabled = true;
        outputLoading.style.display = 'flex';
        setOutput('');
        outputProgress.innerText = "Preparando ZIP...";

        try {
            // 1. Encontrar tags
            const matchHashtags = (text.match(/#[\p{L}\p{N}_-]+/gu) || []).map(t => t.toLowerCase().replace('#', ''));
            const uniqueTags = [...new Set(matchHashtags)];
            
            const matchedChars = characters.filter(c => {
                const cNameSanitized = c.name.toLowerCase().replace(/[^\p{L}\p{N}_-]/gu, '');
                const cNameRaw = c.name.toLowerCase().replace('#', '');
                return uniqueTags.includes(cNameSanitized) || uniqueTags.includes(cNameRaw) || text.toLowerCase().includes(cNameRaw);
            });

            const zip = new JSZip();
            let aliasedInputForAI = text;

            // 2. Add as capas no ZIP
            matchedChars.forEach((char, idx) => {
                const alias = `#Personagem${idx+1}`;
                const escapedTag = char.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                const regex = new RegExp(`(#${escapedTag}|\\b${escapedTag}\\b)`, 'gi');
                aliasedInputForAI = aliasedInputForAI.replace(regex, alias);

                if (char.previewUrl) {
                    const mimeMatch = char.previewUrl.match(/^data:image\/(\w+);base64,/);
                    const ext = mimeMatch ? mimeMatch[1] : 'png';
                    const base64Data = char.previewUrl.replace(/^data:image\/\w+;base64,/, "");
                    zip.file(`imagens_referencia/${alias.replace('#','')}.${ext}`, base64Data, {base64: true});
                }
            });

            outputProgress.innerText = "Reescrevendo...";

            // 3. IA rescreve o contexto sem censura
            const sys = "You are a prompt editor. You will receive a list of prompts. Your job is to rewrite them to remove any potentially censored themes, political figures, or explicit violence, replacing them with generic movie descriptions. Keep the exact character tags (like #Personagem1) intact. Keep one prompt per line.";
            
            let finalText = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                return await window.laplataAI.generateText(apiKey, `Original Prompts:\n${aliasedInputForAI}`, {}, sys);
            });

            zip.file('prompts.txt', finalText.split('\n').filter(l=>l.trim()).join('\n\n'));

            // 4. Video extra
            if (checkVeoVideo.classList.contains('checked')) {
                const lines = finalText.split('\n').filter(l => l.trim().length > 0);
                const videoPrompts = [];
                for (let i = 0; i < lines.length; i++) {
                    outputProgress.innerText = `Vídeo (${i+1}/${lines.length})...`;
                    const result = await window.laplataSettings.executeWithKeyRotation(async (apiKey) => {
                        const mSys = "You are a Prompt Engineer for AI Video Generators (Veo). Rewrite the provided image prompt into a VIDEO MOTION PROMPT. Describe the movement and camera action. Keep it under 2 sentences. No prefixes.";
                        return await window.laplataAI.generateText(apiKey, `Original: ${lines[i]}`, {}, mSys);
                    });
                    videoPrompts.push(result);
                }
                zip.file('prompts_animacao.txt', videoPrompts.join('\n\n'));
            }

            // Baixar ZIP
            const content = await zip.generateAsync({ type: 'blob' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(content);
            a.download = `VEO_Export_${Date.now()}.zip`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);

            setOutput(finalText);
            playSuccess();
            showToast('Download Pronto', 'ZIP com Imagens e Prompts exportado.', 'success');

        } catch(e) {
            console.error(e);
            setOutput(`ERRO VEO: ${e.message}`);
            playError();
        } finally {
            isProcessing = false;
            btnRunVeo.disabled = false;
            outputLoading.style.display = 'none';
            outputProgress.innerText = "";
        }
    });

});
