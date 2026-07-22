/**
 * Apollo La Plata - Video Director Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- UI ELEMENTS ---
    const scriptInput = document.getElementById('director-script');
    const imgUpload = document.getElementById('img-upload');
    const imgGrid = document.getElementById('img-grid');
    const btnAddImg = document.getElementById('btn-add-img');
    const imgStatus = document.getElementById('img-status');
    const btnExecute = document.getElementById('btn-execute');
    const cueList = document.getElementById('cue-list');
    const cueTemplate = document.getElementById('cue-template');

    // --- STATE ---
    let cues = [];
    let images = []; // { id, base64 }
    let isProcessing = false;

    // Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playSuccess = () => { if (window.apolloSFX) window.apolloSFX.play('success'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };
    const showToast = (title, message, type = 'system') => { if (window.apolloNotifications) window.apolloNotifications.add(title, message, type); };

    // --- PARSE SCRIPT ---
    function parseScript() {
        const lines = scriptInput.value.split('\n').filter(l => l.trim().length > 0);
        cues = lines.map(line => {
            const isCut = line.toUpperCase().includes('[CORTA]');
            return {
                id: crypto.randomUUID(),
                type: isCut ? 'CORTA' : 'CONTINUA',
                text: line.replace(/.*?\[(CORTA|CONTINUA)\]/i, '').trim(),
                originalText: line,
                status: 'pending', // pending, processing, completed, error
                thumbnailUrl: null,
                videoUrl: null
            };
        });
        updateStatus();
    }

    function updateStatus() {
        const totalCorta = cues.filter(c => c.type === 'CORTA').length;
        if (images.length < totalCorta) {
            imgStatus.innerText = `${images.length}/${totalCorta} Necessárias`;
            imgStatus.style.color = '#f59e0b'; // amber
        } else {
            imgStatus.innerText = `${images.length}/${totalCorta} Preenchidas`;
            imgStatus.style.color = '#10b981'; // emerald
        }
    }

    scriptInput.addEventListener('input', parseScript);

    // --- IMAGE UPLOAD ---
    btnAddImg.addEventListener('click', () => {
        if (isProcessing) return;
        playClick();
        imgUpload.click();
    });

    imgUpload.addEventListener('change', (e) => {
        const files = Array.from(e.target.files || []);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onloadend = () => {
                images.push({ id: crypto.randomUUID(), base64: reader.result });
                renderImages();
                updateStatus();
            };
            if (file) reader.readAsDataURL(file);
        });
        e.target.value = '';
    });

    const btnPasteImg = document.getElementById('btn-paste-img');
    if (btnPasteImg) {
        btnPasteImg.addEventListener('click', () => {
            if (isProcessing) return;
            const b64 = window.laplataInventory.paste();
            if (b64) {
                images.push({ id: crypto.randomUUID(), base64: b64 });
                renderImages();
                updateStatus();
                playClick();
                showToast('Colado', 'Imagem carregada do Inventário!', 'success');
            } else {
                playError();
                showToast('Aviso', 'O inventário está vazio!', 'system');
            }
        });
    }

    function renderImages() {
        // Keep only the Add Button
        imgGrid.innerHTML = '';
        images.forEach((img, index) => {
            const slot = document.createElement('div');
            slot.className = 'img-slot';
            slot.innerHTML = `
                <img src="${img.base64}">
                <div class="scene-tag">Cena ${index + 1}</div>
                <div class="btn-remove-img" title="Remover"><span style="font-size:1.2rem; margin:0;">🗑️</span></div>
            `;
            
            const btnRemove = slot.querySelector('.btn-remove-img');
            slot.addEventListener('mouseenter', () => { if(!isProcessing) btnRemove.classList.add('active'); });
            slot.addEventListener('mouseleave', () => btnRemove.classList.remove('active'));
            
            btnRemove.addEventListener('click', (e) => {
                e.stopPropagation();
                if (isProcessing) return;
                playClick();
                images = images.filter(i => i.id !== img.id);
                renderImages();
                updateStatus();
            });

            imgGrid.appendChild(slot);
        });
        imgGrid.appendChild(btnAddImg);
        if (btnPasteImg) imgGrid.appendChild(btnPasteImg);
    }

    // --- EXECUTE DIRECTOR ---
    
    // MOCK: Extrai último frame do vídeo
    async function extractLastFrameMock(videoUrl) {
        return new Promise(resolve => {
            // Em um sistema real, leríamos o video via Canvas.
            // Aqui, vamos simular que extraímos um frame usando uma imagem base64 de placeholder
            setTimeout(() => {
                // Return a generic grey placeholder as the "extracted frame"
                const canvas = document.createElement('canvas');
                canvas.width = 640; canvas.height = 360;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#475569';
                ctx.fillRect(0,0,640,360);
                ctx.fillStyle = '#94a3b8';
                ctx.font = '20px Arial';
                ctx.fillText('Frame Extraído MOCK', 200, 180);
                resolve(canvas.toDataURL('image/png'));
            }, 500);
        });
    }

    // MOCK: Gera Vídeo
    async function generateVideoMock(prompt, imageBase64) {
        return new Promise(resolve => {
            setTimeout(() => {
                // Simula retorno de vídeo do ComfyUI
                // Usando um placeholder genérico da W3Schools ou um local se existir
                resolve("https://www.w3schools.com/html/mov_bbb.mp4");
            }, 3000); // 3 segundos simulando geração
        });
    }

    function renderCues() {
        cueList.innerHTML = '';
        if (cues.length === 0) {
            cueList.innerHTML = `
                <div class="placeholder-text" style="text-align: center; margin-top: 50px; color: #475569;">
                    <div style="font-size: 4rem; opacity: 0.5;">🎞️</div>
                    <div style="margin-top: 10px;">Nenhum script processado.</div>
                </div>`;
            return;
        }

        cues.forEach((cue, index) => {
            const clone = cueTemplate.content.cloneNode(true);
            const el = clone.querySelector('.cue-item');
            
            // Classes e cores
            el.classList.add(cue.status);
            
            const typeBadge = el.querySelector('.cue-type');
            typeBadge.innerText = cue.type;
            typeBadge.classList.add(cue.type.toLowerCase());
            
            el.querySelector('.cue-title').innerText = `Cena ${index + 1}`;
            el.querySelector('.cue-text').innerText = cue.text;

            // Status Icon
            const iconDiv = el.querySelector('.cue-status-icon');
            if (cue.status === 'processing') iconDiv.innerHTML = '<div class="spinner"></div>';
            else if (cue.status === 'completed') iconDiv.innerHTML = '✅';
            else if (cue.status === 'error') iconDiv.innerHTML = '❌';
            else iconDiv.innerHTML = '<span style="color:#475569;">⏳</span>'; // pending

            // Media Preview
            if (cue.thumbnailUrl || cue.videoUrl) {
                const mediaArea = el.querySelector('.cue-media');
                mediaArea.style.display = 'flex';

                if (cue.thumbnailUrl) {
                    el.querySelector('.input-media img').src = cue.thumbnailUrl;
                } else {
                    el.querySelector('.input-media').style.display = 'none';
                }

                if (cue.videoUrl) {
                    el.querySelector('.output-media video').src = cue.videoUrl;
                } else {
                    el.querySelector('.output-media').style.display = 'none';
                    el.querySelector('.media-arrow').style.display = 'none';
                }
            }

            cueList.appendChild(el);
        });
    }

    btnExecute.addEventListener('click', async () => {
        parseScript();
        
        if (cues.length === 0) {
            showToast('Erro', 'Insira o roteiro antes de iniciar.', 'system');
            return;
        }

        const totalCorta = cues.filter(c => c.type === 'CORTA').length;
        if (images.length < totalCorta) {
            showToast('Falta de Imagens', `Você tem ${images.length} imagens, mas o roteiro pede ${totalCorta} cenas de [CORTA].`, 'error');
            playError();
            return;
        }

        playClick();
        isProcessing = true;
        btnExecute.disabled = true;
        btnExecute.innerText = "🎬 Gravando Cenas (MOCK)...";
        scriptInput.disabled = true;

        let cortaIndex = 0;
        let lastGeneratedFrame = null;

        // Reset Status
        cues.forEach(c => { c.status = 'pending'; c.thumbnailUrl = null; c.videoUrl = null; });
        renderCues();

        try {
            for (let i = 0; i < cues.length; i++) {
                const cue = cues[i];
                cue.status = 'processing';
                
                let sourceBase64 = "";

                if (cue.type === 'CORTA') {
                    sourceBase64 = images[cortaIndex].base64;
                    cortaIndex++;
                } else {
                    if (!lastGeneratedFrame) {
                        throw new Error(`Falha no [CONTINUA] da Cena ${i+1}. Falta o quadro da cena anterior.`);
                    }
                    sourceBase64 = lastGeneratedFrame;
                }

                cue.thumbnailUrl = sourceBase64;
                renderCues();

                // Simula Geração de Vídeo
                const videoUrl = await generateVideoMock(cue.text, sourceBase64);
                
                if (!videoUrl) throw new Error("Erro ao gerar vídeo (MOCK).");

                cue.videoUrl = videoUrl;
                cue.status = 'completed';
                renderCues();

                // Extrai último frame para o próximo CONTINUA
                if (i < cues.length - 1 && cues[i+1].type === 'CONTINUA') {
                    lastGeneratedFrame = await extractLastFrameMock(videoUrl);
                }
            }

            playSuccess();
            showToast('Sucesso', 'Gravação do Diretor finalizada!', 'success');

        } catch (e) {
            console.error(e);
            showToast('Erro na Gravação', e.message, 'error');
            playError();
            // Marca o que estiver processando como erro
            cues.forEach(c => { if (c.status === 'processing') c.status = 'error'; });
            renderCues();
        } finally {
            isProcessing = false;
            btnExecute.disabled = false;
            btnExecute.innerHTML = "🎬 Iniciar GRAVAÇÃO EM CADEIA";
            scriptInput.disabled = false;
        }
    });

    // Init
    parseScript();
});
