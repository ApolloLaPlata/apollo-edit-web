// State para a tab de imagens
let imagesState = {
    script: '',
    imageCount: 8,
    autoSelect: true,
    allowedTypes: {
        photo: true,
        headline: true,
        object: true,
        comic: true,
        graph: true,
        illustration: false,
        ai_generated: false,
        screenshot: true
    },
    isAnalyzing: false,
    assets: [],
    error: null,
    seoResult: '',
    isOptimizingSEO: false,
    refreshingIndex: null,
    hoveredPreview: null
};

const IMAGES_TYPES_CONFIG = [
    { id: 'photo', label: 'Foto Real', icon: 'fa-camera' },
    { id: 'headline', label: 'Manchete', icon: 'fa-newspaper' },
    { id: 'object', label: 'Objeto/Lugar', icon: 'fa-image' },
    { id: 'comic', label: 'Cômico/Meme', icon: 'fa-smile' },
    { id: 'graph', label: 'Gráfico/Dado', icon: 'fa-chart-line' },
    { id: 'illustration', label: 'Desenho/Ilustração', icon: 'fa-palette' },
    { id: 'ai_generated', label: 'Gerado por IA', icon: 'fa-robot' },
    { id: 'screenshot', label: 'Print/Rede Social', icon: 'fa-desktop' }
];

function initImagesTab() {
    console.log("Inicializando tab-images");
    
    // Bind inputs
    const scriptInput = document.getElementById('images-script-input');
    if (scriptInput) {
        scriptInput.addEventListener('input', (e) => {
            imagesState.script = e.target.value;
            updateImagesButtons();
        });
    }

    const countInput = document.getElementById('images-count');
    if (countInput) {
        countInput.addEventListener('input', (e) => {
            imagesState.imageCount = parseInt(e.target.value) || 8;
        });
    }

    const autoSelectInput = document.getElementById('images-auto-select');
    if (autoSelectInput) {
        autoSelectInput.addEventListener('change', (e) => {
            imagesState.autoSelect = e.target.checked;
            renderImagesAutoSelectToggle();
        });
    }

    renderImagesTypes();
    updateImagesButtons();
}

function renderImagesAutoSelectToggle() {
    const slider = document.getElementById('images-auto-select-slider');
    const knob = document.getElementById('images-auto-select-knob');
    if (slider && knob) {
        if (imagesState.autoSelect) {
            slider.style.backgroundColor = '#4f46e5';
            knob.style.left = '22px';
        } else {
            slider.style.backgroundColor = '#2a2a2a';
            knob.style.left = '2px';
        }
    }
}

function renderImagesTypes() {
    const container = document.getElementById('images-types-container');
    if (!container) return;

    container.innerHTML = '';
    IMAGES_TYPES_CONFIG.forEach(type => {
        const isChecked = imagesState.allowedTypes[type.id];
        const html = `
            <label style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; border: 1px solid ${isChecked ? '#818cf8' : '#444'}; background: ${isChecked ? 'rgba(139,92,246,0.15)' : '#1e1e1e'}; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                <input type="checkbox" style="accent-color: #4f46e5; width: 16px; height: 16px;" 
                    ${isChecked ? 'checked' : ''} 
                    onchange="toggleImagesType('${type.id}', this.checked)">
                <i class="fas ${type.icon}" style="color: ${isChecked ? '#4f46e5' : '#71717a'}; font-size: 14px;"></i>
                <span style="font-size: 12px; font-weight: 500; color: ${isChecked ? '#a78bfa' : '#94a3b8'};">${type.label}</span>
            </label>
        `;
        container.innerHTML += html;
    });
}

function toggleImagesType(id, checked) {
    imagesState.allowedTypes[id] = checked;
    renderImagesTypes();
}

function imagesImportScript() {
    const historyManager = window.historyManager;
    if (historyManager) {
        historyManager.loadHistory();
        const history = historyManager.getHistory();
        if (history && history.length > 0) {
            imagesState.script = history[0].script;
            const input = document.getElementById('images-script-input');
            if (input) input.value = imagesState.script;
            updateImagesButtons();
            
            // Show toast
            const container = document.getElementById('toast-container');
            if (container) {
                const toast = document.createElement('div');
                toast.className = 'toast success';
                toast.innerHTML = `<i class="fas fa-check-circle"></i> Roteiro mais recente puxado do histórico!`;
                container.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
            }
        } else {
            imagesSetError("Nenhum roteiro encontrado no histórico.");
        }
    } else {
        imagesSetError("Histórico não disponível.");
    }
}

function updateImagesButtons() {
    const analyzeBtn = document.getElementById('images-analyze-btn');
    const clearBtn = document.getElementById('images-clear-btn');
    const hasScript = imagesState.script.trim().length > 0;
    
    if (analyzeBtn) {
        analyzeBtn.disabled = imagesState.isAnalyzing || !hasScript;
        analyzeBtn.style.opacity = analyzeBtn.disabled ? '0.5' : '1';
        analyzeBtn.style.cursor = analyzeBtn.disabled ? 'not-allowed' : 'pointer';
        
        if (imagesState.isAnalyzing) {
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';
        } else {
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Extrair e Buscar';
        }
    }
    
    if (clearBtn) {
        const canClear = hasScript || imagesState.assets.length > 0;
        clearBtn.disabled = imagesState.isAnalyzing || !canClear;
        clearBtn.style.opacity = clearBtn.disabled ? '0.5' : '1';
        clearBtn.style.cursor = clearBtn.disabled ? 'not-allowed' : 'pointer';
    }
}

function imagesSetError(msg) {
    imagesState.error = msg;
    const errorEl = document.getElementById('images-error');
    const textEl = document.getElementById('images-error-text');
    if (errorEl && textEl) {
        if (msg) {
            textEl.textContent = msg;
            errorEl.style.display = 'flex';
        } else {
            errorEl.style.display = 'none';
        }
    }
}

async function imagesAnalyze() {
    if (!imagesState.script.trim()) {
        imagesSetError("Por favor, insira um roteiro.");
        return;
    }
    
    const activeTypes = Object.entries(imagesState.allowedTypes)
        .filter(([_, allowed]) => allowed)
        .map(([type]) => type);
        
    if (activeTypes.length === 0) {
        imagesSetError("Selecione pelo menos um tipo de imagem.");
        return;
    }

    imagesSetError(null);
    imagesState.isAnalyzing = true;
    imagesState.assets = [];
    updateImagesUI();

    try {
        const response = await fetch('https://api.apolloedit.com/api/noticias/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(buildNoticiasBody({
                prompt_type: 'images',
                input_text: imagesState.script,
                images_count: imagesState.imageCount,
                allowed_types: activeTypes
            }))
        });

        if (!response.ok) {
            throw new Error('Falha na resposta do servidor.');
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            const rawAssets = data.assets || [];
            
            // Loop sequentially para buscar as imagens de cada ativo (como no original)
            imagesState.assets = [];
            const pixabayKey = localStorage.getItem('api_key_pixabay') || '';
            const pexelsKey = localStorage.getItem('api_key_pexels') || '';
            
            for (let i = 0; i < rawAssets.length; i++) {
                const asset = rawAssets[i];
                let autoImages = [];
                try {
                    const res = await fetch(`/api/search-images?q=${encodeURIComponent(asset.searchQuery)}&pixabay=${pixabayKey}&pexels=${pexelsKey}`);
                    if (res.ok) {
                        const imgData = await res.json();
                        autoImages = imgData.urls || [];
                    }
                } catch (e) {
                    console.error("Error fetching images for", asset.searchQuery, e);
                }
                
                asset.autoImages = autoImages;
                if (imagesState.autoSelect && autoImages.length > 0) {
                    asset.userImage = autoImages[0].url;
                    asset.selectedSourceUrl = autoImages[0].source;
                }
                imagesState.assets.push(asset);
                // Update UI incrementally if desired, but we'll do it at the end
            }
        } else {
            throw new Error(data.message || 'Erro desconhecido');
        }
    } catch (err) {
        imagesSetError("Erro ao extrair e buscar imagens: " + err.message);
    } finally {
        imagesState.isAnalyzing = false;
        updateImagesUI();
    }
}

function imagesClear() {
    imagesState.script = '';
    imagesState.assets = [];
    imagesState.error = null;
    imagesState.seoResult = '';
    
    const input = document.getElementById('images-script-input');
    if (input) input.value = '';
    
    imagesSetError(null);
    updateImagesUI();
}

function updateImagesUI() {
    updateImagesButtons();
    renderImagesOutput();
    renderImagesHeader();
}

function renderImagesHeader() {
    const topActions = document.getElementById('images-top-actions');
    if (!topActions) return;

    if (imagesState.assets.length > 0 && !imagesState.isAnalyzing) {
        const completed = imagesState.assets.filter(a => !!a.userImage).length;
        const total = imagesState.assets.length;
        const perc = Math.round((completed / total) * 100) || 0;
        
        topActions.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 14px; font-weight: 500; color: #94a3b8;">
                    Progresso: ${completed}/${total}
                </div>
                <div style="width: 128px; height: 8px; background: #2a2a2a; border-radius: 9999px; overflow: hidden;">
                    <div style="height: 100%; width: ${perc}%; background: #10b981; transition: width 0.5s;"></div>
                </div>
                <button onclick="imagesDownloadZIP()" style="display: flex; align-items: center; gap: 8px; background: #1e1e1e; border: 1px solid #444; border-radius: 6px; padding: 6px 12px; font-size: 14px; font-weight: 500; color: #fff; cursor: pointer; margin-left: 8px;">
                    <i class="fas fa-file-archive"></i> Baixar ZIP
                </button>
            </div>
        `;
    } else {
        topActions.innerHTML = '';
    }
}

function renderImagesOutput() {
    const emptyState = document.getElementById('images-empty-state');
    const loadingState = document.getElementById('images-loading-state');
    const container = document.getElementById('images-assets-container');
    
    if (imagesState.isAnalyzing) {
        if (emptyState) emptyState.style.display = 'none';
        if (container) container.style.display = 'none';
        if (loadingState) loadingState.style.display = 'flex';
        return;
    }
    
    if (imagesState.assets.length === 0) {
        if (loadingState) loadingState.style.display = 'none';
        if (container) container.style.display = 'none';
        if (emptyState) emptyState.style.display = 'flex';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    if (loadingState) loadingState.style.display = 'none';
    if (container) {
        container.style.display = 'flex';
        container.innerHTML = '';
        
        imagesState.assets.forEach((asset, idx) => {
            const isDone = !!asset.userImage;
            const typeConfig = IMAGES_TYPES_CONFIG.find(t => t.id === asset.type) || IMAGES_TYPES_CONFIG[2];
            
            let html = `
                <div style="background: #1e1e1e; border-radius: 12px; border: 1px solid ${isDone ? '#065f46' : '#333'}; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                    <div style="padding: 20px; border-bottom: 1px solid #333; display: flex; gap: 16px; flex-direction: row; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 250px;">
                            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                                <span style="font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 9999px; display: flex; align-items: center; gap: 6px; background: #e0e7ff; color: #4338ca;">
                                    <i class="fas ${typeConfig.icon}"></i> ${typeConfig.label.toUpperCase()}
                                </span>
                                <span style="font-size: 12px; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                                    Imagem ${idx + 1} de ${imagesState.assets.length}
                                </span>
                                ${isDone ? `<span style="margin-left: auto; display: flex; align-items: center; gap: 4px; color: #059669; font-size: 12px; font-weight: 500;"><i class="fas fa-check-circle"></i> Selecionada</span>` : ''}
                            </div>
                            
                            <h3 style="font-size: 18px; font-weight: 500; margin: 0 0 4px 0; color: ${isDone ? '#94a3b8' : '#fff'};">${asset.description}</h3>
                            <p style="font-size: 14px; color: #64748b; font-style: italic; margin: 0 0 16px 0; border-left: 2px solid #444; padding-left: 12px;">"${asset.context}"</p>
                        </div>
                        
                        ${isDone ? `
                            <div style="width: 192px; flex-shrink: 0; display: flex; flex-direction: column; gap: 8px;">
                                <div style="aspect-ratio: 16/9; background: #2a2a2a; position: relative; border-radius: 8px; overflow: hidden; border: 1px solid #333;">
                                    <img src="${asset.userImage}" style="width: 100%; height: 100%; object-fit: cover;">
                                    <div style="position: absolute; top: 8px; right: 8px; display: flex; flex-direction: column; gap: 8px;">
                                        <button onclick="imagesRemoveSelected(${idx})" style="background: rgba(0,0,0,0.5); color: white; border: none; width: 28px; height: 28px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                </div>
                                ${asset.selectedSourceUrl ? `
                                    <a href="${asset.selectedSourceUrl}" target="_blank" style="font-size: 11px; color: #4f46e5; text-decoration: none; font-weight: 500; display: flex; align-items: center; gap: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                                        <i class="fas fa-external-link-alt"></i> Ver fonte original
                                    </a>
                                ` : ''}
                            </div>
                        ` : ''}
                    </div>
                    
                    ${!isDone ? `
                         <div style="padding: 20px; background: #161616;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                                <p style="font-size: 14px; font-weight: 500; color: #cbd5e1; margin: 0;">Opções encontradas na internet:</p>
                            </div>
                            
                            ${asset.autoImages && asset.autoImages.length > 0 ? `
                                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 12px; margin-bottom: 16px;">
                                    ${asset.autoImages.map((img, imgIdx) => `
                                         <div style="aspect-ratio: 16/9; background: #2a2a2a; border-radius: 6px; overflow: hidden; position: relative; cursor: pointer; border: 2px solid transparent;" 
                                             onmouseover="this.querySelector('.overlay').style.opacity=1" 
                                             onmouseout="this.querySelector('.overlay').style.opacity=0">
                                            <img src="/api/proxy-image?url=${encodeURIComponent(img.thumbnail || img.url)}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='${img.thumbnail || img.url}'">
                                            <div class="overlay" style="position: absolute; inset: 0; background: rgba(0,0,0,0.4); opacity: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: opacity 0.2s;">
                                                <button onclick="imagesSelectAutoImage(${idx}, ${imgIdx})" style="background: rgba(255,255,255,0.15); color: #fff; border: 1px solid rgba(255,255,255,0.3); padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; cursor: pointer; backdrop-filter: blur(4px);">Usar esta</button>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : `<div style="font-size: 14px; color: #64748b; font-style: italic; margin-bottom: 16px;">Nenhuma imagem automática encontrada.</div>`}
                            
                            <div style="display: flex; align-items: center; gap: 12px; padding-top: 12px; border-top: 1px solid #333;">
                                <span style="font-size: 14px; color: #94a3b8;">Não gostou das opções?</span>
                                <a href="https://www.google.com/search?tbm=isch&q=${encodeURIComponent(asset.searchQuery)}" target="_blank" style="display: inline-flex; align-items: center; gap: 6px; background: #1e1e1e; border: 1px solid #444; color: #cbd5e1; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: 500; text-decoration: none; cursor: pointer;">
                                    <i class="fas fa-search"></i> Buscar no Google
                                </a>
                                <label style="display: inline-flex; align-items: center; gap: 6px; background: #1e1e1e; border: 1px solid #444; color: #cbd5e1; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer;">
                                    <i class="fas fa-upload"></i> Fazer Upload
                                    <input type="file" accept="image/*" style="display: none;" onchange="imagesHandleUpload(${idx}, event)">
                                </label>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
            container.innerHTML += html;
        });
    }
}

function imagesSelectAutoImage(assetIdx, imgIdx) {
    const asset = imagesState.assets[assetIdx];
    const img = asset.autoImages[imgIdx];
    asset.userImage = img.url;
    asset.selectedSourceUrl = img.source;
    updateImagesUI();
}

function imagesRemoveSelected(assetIdx) {
    const asset = imagesState.assets[assetIdx];
    asset.userImage = null;
    asset.selectedSourceUrl = null;
    updateImagesUI();
}

function imagesHandleUpload(assetIdx, event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagesState.assets[assetIdx].userImage = e.target.result;
            imagesState.assets[assetIdx].selectedSourceUrl = null;
            updateImagesUI();
        };
        reader.readAsDataURL(file);
    }
}

async function imagesDownloadZIP() {
    const assetsWithImages = imagesState.assets.filter(a => !!a.userImage);
    if (assetsWithImages.length === 0) return;
    
    // Na versão real a exportação vai depender do JSZip ou chamada ao server.
    // Aqui faremos um fallback para baixar uma a uma para o navegador
    try {
        const response = await fetch('https://api.apolloedit.com/api/download-zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ images: assetsWithImages })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `imagens_roteiro_${new Date().getTime()}.zip`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            throw new Error('Falha ao baixar zip');
        }
    } catch (err) {
        console.error("Zip indisponível, falhando graciosamente", err);
        // Fallback
        alert("Baixando imagens individualmente...");
        assetsWithImages.forEach((asset, idx) => {
            setTimeout(() => {
                const a = document.createElement('a');
                a.href = asset.userImage;
                a.download = `imagem_${idx+1}.jpg`;
                a.target = '_blank';
                document.body.appendChild(a);
                a.click();
                a.remove();
            }, idx * 1000);
        });
    }
}

// Inicializa quando as funções globais chamam (será mesclado via py)
// Para facilitar a fusão:
document.addEventListener('DOMContentLoaded', () => {
    initImagesTab();
});
