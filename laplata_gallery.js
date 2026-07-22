/**
 * Apollo La Plata - Gallery Logic
 * Gerencia a galeria de imagens e vídeos usando o laplata_db.js
 */

document.addEventListener('DOMContentLoaded', async () => {
    const grid = document.getElementById('gallery-grid');
    const galleryCount = document.getElementById('gallery-count');
    
    // Paginação
    const btnPrevPage = document.getElementById('btn-prev-page');
    const btnNextPage = document.getElementById('btn-next-page');
    const pageIndicator = document.getElementById('page-indicator');
    
    // Barra de Ferramentas
    const btnClearGallery = document.getElementById('btn-clear-gallery');
    const btnExportCSV = document.getElementById('btn-export-csv');
    const btnExportZipImg = document.getElementById('btn-export-zip-img');
    const btnExportZipFull = document.getElementById('btn-export-zip-full');
    const btnCopyScript = document.getElementById('btn-copy-script');
    
    // Lightbox
    const lightboxModal = document.getElementById('lightbox-modal');
    const btnCloseLightbox = document.getElementById('btn-close-lightbox');
    const lightboxMediaContainer = document.getElementById('lightbox-media-container');
    const lbPrompt = document.getElementById('lb-prompt');
    const lbVideoBlock = document.getElementById('lb-video-block');
    const lbVideoPrompt = document.getElementById('lb-video-prompt');
    const lbDate = document.getElementById('lb-date');
    const lbRatio = document.getElementById('lb-ratio');
    
    const btnCopyPrompt = document.getElementById('btn-copy-prompt');
    const btnDownloadMedia = document.getElementById('btn-download-media');
    const btnDeleteItem = document.getElementById('btn-delete-item');

    let allMedia = [];
    let currentPage = 1;
    const ITEMS_PER_PAGE = 20;
    let currentLightboxItem = null;

    // SFX Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playSuccess = () => { if (window.apolloSFX) window.apolloSFX.play('success'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };

    const showToast = (title, message, type = 'system') => {
        if (window.apolloNotifications) {
            window.apolloNotifications.add(title, message, type);
        } else {
            console.log(`[${title}] ${message}`);
        }
    };

    // Formatação
    const padNumber = (num) => num.toString().padStart(3, '0');

    // --- CARREGAMENTO INICIAL ---
    async function loadGallery() {
        try {
            const rawMedia = await window.laplataDB.gallery.getAll();
            // Ordena cronologicamente inverso (mais novo primeiro) para exibição
            allMedia = rawMedia.sort((a, b) => b.timestamp - a.timestamp);
            galleryCount.innerText = `${allMedia.length} itens`;
            
            // Corrige página se deletou o último item da página atual
            const maxPages = Math.ceil(allMedia.length / ITEMS_PER_PAGE) || 1;
            if (currentPage > maxPages) currentPage = maxPages;

            renderGrid();
        } catch (e) {
            console.error("Erro ao carregar galeria:", e);
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:50px; color:#ef4444;">Falha ao ler o banco de dados.</div>`;
        }
    }

    function renderGrid() {
        if (allMedia.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:50px; color:#94a3b8;">A galeria está vazia. Gere imagens no Laboratório!</div>`;
            updatePagination();
            return;
        }

        const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
        const endIndex = startIndex + ITEMS_PER_PAGE;
        const pageItems = allMedia.slice(startIndex, endIndex);

        grid.innerHTML = pageItems.map(item => {
            const isVideo = !!item.videoUrl;
            const previewUrl = isVideo ? item.videoUrl : item.imageUrl;
            
            // Detecta tipo para renderizar a tag correta
            let mediaHtml = '';
            if (previewUrl.startsWith('data:video')) {
                mediaHtml = `<video src="${previewUrl}" autoplay loop muted playsinline></video>`;
            } else {
                mediaHtml = `<img src="${previewUrl}" alt="Media">`;
            }

            const dateStr = new Date(item.timestamp).toLocaleDateString() + ' ' + new Date(item.timestamp).toLocaleTimeString();

            return `
            <div class="gallery-card" onclick="window.openLightbox('${item.id}')">
                <div class="gallery-img-wrapper" style="aspect-ratio: ${item.aspectRatio === '1:1' ? '1/1' : '16/9'};">
                    ${mediaHtml}
                    ${isVideo ? '<div class="video-badge">🎬 VÍDEO</div>' : ''}
                </div>
                <div class="gallery-card-content">
                    <div class="prompt-text">${item.prompt}</div>
                    <div class="timestamp">${dateStr}</div>
                </div>
            </div>`;
        }).join('');

        updatePagination();
    }

    function updatePagination() {
        const totalPages = Math.ceil(allMedia.length / ITEMS_PER_PAGE) || 1;
        pageIndicator.innerText = `Página ${currentPage} de ${totalPages}`;
        
        btnPrevPage.disabled = currentPage === 1;
        btnNextPage.disabled = currentPage === totalPages;
    }

    btnPrevPage.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            playClick();
            renderGrid();
        }
    });

    btnNextPage.addEventListener('click', () => {
        const totalPages = Math.ceil(allMedia.length / ITEMS_PER_PAGE);
        if (currentPage < totalPages) {
            currentPage++;
            playClick();
            renderGrid();
        }
    });

    // --- LIGHTBOX ---
    window.openLightbox = (id) => {
        const item = allMedia.find(m => m.id === id);
        if (!item) return;
        
        currentLightboxItem = item;
        playClick();
        lightboxModal.style.display = 'flex';

        // Mídia
        const isVideo = !!item.videoUrl;
        const mainUrl = isVideo ? item.videoUrl : item.imageUrl;
        
        if (mainUrl.startsWith('data:video')) {
            lightboxMediaContainer.innerHTML = `<video src="${mainUrl}" controls autoplay loop style="width:100%; height:100%; object-fit:contain;"></video>`;
        } else {
            lightboxMediaContainer.innerHTML = `<img src="${mainUrl}" style="width:100%; height:100%; object-fit:contain;">`;
        }

        // Metadados
        lbPrompt.innerText = item.prompt;
        
        if (isVideo && item.videoPrompt) {
            lbVideoBlock.style.display = 'block';
            lbVideoPrompt.innerText = item.videoPrompt;
        } else {
            lbVideoBlock.style.display = 'none';
        }

        lbDate.innerText = new Date(item.timestamp).toLocaleString();
        lbRatio.innerText = item.aspectRatio || '16:9';
    };

    function closeLightbox() {
        lightboxModal.style.display = 'none';
        lightboxMediaContainer.innerHTML = '';
        currentLightboxItem = null;
        playClick();
    }

    btnCloseLightbox.addEventListener('click', closeLightbox);
    
    // Fechar ao clicar fora da área
    lightboxModal.addEventListener('click', (e) => {
        if (e.target === lightboxModal) closeLightbox();
    });

    // Ações do Lightbox
    btnCopyPrompt.addEventListener('click', () => {
        if (!currentLightboxItem) return;
        navigator.clipboard.writeText(currentLightboxItem.prompt);
        showToast('Copiado!', 'Prompt copiado para a área de transferência.', 'system');
        playClick();
    });

    btnDownloadMedia.addEventListener('click', () => {
        if (!currentLightboxItem) return;
        playClick();
        
        const isVideo = !!currentLightboxItem.videoUrl;
        const mainUrl = isVideo ? currentLightboxItem.videoUrl : currentLightboxItem.imageUrl;
        
        let ext = isVideo ? 'mp4' : 'png';
        if (mainUrl.startsWith('data:image/gif')) ext = 'gif';
        else if (mainUrl.startsWith('data:video/webm')) ext = 'webm';
        else if (mainUrl.startsWith('data:image/jpeg')) ext = 'jpg';

        const filename = `apollo_render_${currentLightboxItem.timestamp}.${ext}`;
        
        const link = document.createElement('a');
        link.href = mainUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    const btnCopyToInventory = document.createElement('button');
    btnCopyToInventory.className = 'btn-action btn-secondary';
    btnCopyToInventory.style.padding = '12px';
    btnCopyToInventory.style.marginTop = '10px';
    btnCopyToInventory.innerHTML = '🎒 Copiar para Área de Transferência';
    btnCopyToInventory.onclick = () => {
        if (!currentLightboxItem) return;
        const mainUrl = currentLightboxItem.imageUrl; // Inventory mostly uses images
        window.laplataInventory.copy(mainUrl);
        closeLightbox();
    };
    btnDownloadMedia.parentNode.insertBefore(btnCopyToInventory, btnDownloadMedia.nextSibling);

    btnDeleteItem.addEventListener('click', async () => {
        if (!currentLightboxItem) return;
        
        if (confirm("Deseja EXCLUIR permanentemente esta cena?")) {
            try {
                await window.laplataDB.gallery.delete(currentLightboxItem.id);
                showToast('Excluído', 'Mídia deletada com sucesso.', 'system');
                playSuccess();
                closeLightbox();
                loadGallery();
            } catch (e) {
                console.error(e);
                showToast('Erro', 'Falha ao deletar.', 'system');
                playError();
            }
        }
    });

    // --- FERRAMENTAS EM LOTE ---
    
    // Deletar Tudo
    btnClearGallery.addEventListener('click', async () => {
        if (allMedia.length === 0) return;
        
        const answer = prompt('ATENÇÃO! Digite "DELETAR" para apagar todas as mídias permanentemente:');
        if (answer === 'DELETAR') {
            try {
                await window.laplataDB.gallery.clear();
                showToast('Apocalipse', 'Galeria completamente esvaziada.', 'system');
                if (window.apolloCopilot) window.apolloCopilot.react("clear_gallery");
                playSuccess();
                loadGallery();
            } catch (e) {
                console.error(e);
                showToast('Erro', 'Falha ao esvaziar galeria.', 'system');
                playError();
            }
        }
    });

    // Geração de Script Mestre
    function generateMasterScript(sortedArray) {
        let text = "PROJETO: APOLLO STORY BATCH\n";
        text += "===================================\n\n";

        sortedArray.forEach((img, idx) => {
            const sceneNum = padNumber(idx + 1);
            text += `CENA ${sceneNum}\n`;
            text += `-----------------------------------\n`;
            text += `Arquivo: Cena_${sceneNum}.png\n`;
            text += `Prompt Imagem : ${img.prompt}\n`;
            text += `Prompt Vídeo  : ${img.videoPrompt || '[Nenhum]'}\n\n`;
        });
        return text;
    }

    btnCopyScript.addEventListener('click', () => {
        if (allMedia.length === 0) return;
        playClick();
        
        // Ordem cronológica real (do mais antigo pro mais novo)
        const sorted = [...allMedia].sort((a,b) => a.timestamp - b.timestamp);
        const scriptText = generateMasterScript(sorted);
        
        navigator.clipboard.writeText(scriptText);
        showToast('Sucesso', 'Roteiro Mestre copiado!', 'system');
    });

    // CSV
    btnExportCSV.addEventListener('click', () => {
        if (allMedia.length === 0) return;
        playClick();

        const sorted = [...allMedia].sort((a,b) => a.timestamp - b.timestamp);
        let csv = "Cena,Prompt de Imagem,Prompt de Vídeo,Proporção,Data\n";
        
        sorted.forEach((img, idx) => {
            const sceneNum = padNumber(idx + 1);
            const pImg = `"${(img.prompt || '').replace(/"/g, '""')}"`;
            const pVid = `"${(img.videoPrompt || '').replace(/"/g, '""')}"`;
            const date = new Date(img.timestamp).toLocaleString();
            
            csv += `${sceneNum},${pImg},${pVid},${img.aspectRatio || '16:9'},"${date}"\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Apollo_Roteiro_${Date.now()}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    });

    // ZIP Download (Usando JSZip)
    async function doZipExport(includeTextFiles) {
        if (allMedia.length === 0) return;
        playClick();
        showToast('Compactando', 'Criando arquivo ZIP, aguarde...', 'system');
        
        try {
            const zip = new window.JSZip();
            const dateStr = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            const folderName = `Apollo_Batch_${dateStr}`;
            const folder = zip.folder(folderName);

            const sorted = [...allMedia].sort((a,b) => a.timestamp - b.timestamp);

            if (includeTextFiles) {
                folder.file("_ROTEIRO_MESTRE.txt", generateMasterScript(sorted));
            }

            sorted.forEach((img, index) => {
                const sceneNum = padNumber(index + 1);
                
                // Extrai base64 da Imagem
                if (img.imageUrl && img.imageUrl.includes(',')) {
                    const b64 = img.imageUrl.split(',')[1];
                    folder.file(`Cena_${sceneNum}.png`, b64, { base64: true });
                }

                // Extrai base64 do Vídeo (se houver)
                if (img.videoUrl && img.videoUrl.includes(',')) {
                    const vB64 = img.videoUrl.split(',')[1];
                    let ext = 'mp4';
                    if (img.videoUrl.startsWith('data:image/gif')) ext = 'gif';
                    else if (img.videoUrl.startsWith('data:video/webm')) ext = 'webm';
                    folder.file(`Cena_${sceneNum}.${ext}`, vB64, { base64: true });
                }
            });

            const content = await zip.generateAsync({ type: "blob" });
            const url = URL.createObjectURL(content);
            const link = document.createElement('a');
            link.href = url;
            link.download = `${folderName}.zip`;
            link.click();
            URL.revokeObjectURL(url);

            showToast('Sucesso', 'Download ZIP concluído!', 'success');
            playSuccess();
            
            // Dispara quest se existir
            if (window.apolloQuests) window.apolloQuests.checkAction('export_project');

        } catch (e) {
            console.error("Erro ao gerar ZIP:", e);
            showToast('Erro', 'Falha ao compactar os arquivos. Mídias pesadas?', 'system');
            playError();
        }
    }

    btnExportZipImg.addEventListener('click', () => doZipExport(false));
    btnExportZipFull.addEventListener('click', () => doZipExport(true));

    // INICIAR
    loadGallery();
});
