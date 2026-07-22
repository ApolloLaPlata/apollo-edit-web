/**
 * APOLLO TRANSFER OS (Micro-Windows Explorer)
 * Unifica a Área de Transferência e o Bagageiro num mesmo HUD flutuante.
 */

window.apolloTransferOS = {
    currentFolder: 'transfer', // 'transfer', 'bagageiro', ou 'ias'
    clipboard: null, // { action: 'copy'|'cut', item: object }
    history: [], // Pilha de ações para o Undo (Ctrl+Z)
    selectedId: null,

    // Keys para o LocalStorage
    keys: {
        'transfer': 'apollo_transfer_v3',
        'bagageiro': 'apollo_bagageiro_v3',
        'ias': 'apollo_ias_v3',
        'fx': 'apollo_fx_v3',
        'configs': 'apollo_configs_v3'
    },

    getItems: function(folder = this.currentFolder) {
        try {
            const data = localStorage.getItem(this.keys[folder]);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            return [];
        }
    },

    saveItems: function(items, skipHistory = false) {
        if (!skipHistory) {
            this.history.push({
                folder: this.currentFolder,
                data: JSON.stringify(this.getItems())
            });
            if (this.history.length > 20) this.history.shift();
        }
        localStorage.setItem(this.keys[this.currentFolder], JSON.stringify(items));
        this.render();
    },

    // --- COMANDOS DO SISTEMA ---
    copyAction: function() {
        if (this.selectedId) {
            const items = this.getItems();
            const item = items.find(i => i.id === this.selectedId);
            if (item) {
                this.clipboard = { action: 'copy', item: JSON.parse(JSON.stringify(item)) };
                if (window.showToast) window.showToast('Copiado para a prancheta', 'info');
            }
        }
    },

    cutAction: function() {
        if (this.selectedId) {
            const items = this.getItems();
            const item = items.find(i => i.id === this.selectedId);
            if (item) {
                this.clipboard = { action: 'cut', item: JSON.parse(JSON.stringify(item)), sourceFolder: this.currentFolder };
                if (window.showToast) window.showToast('Recortado', 'info');
            }
        }
    },

    pasteAction: function() {
        if (this.clipboard && this.clipboard.item) {
            let items = this.getItems();
            const newItem = JSON.parse(JSON.stringify(this.clipboard.item));
            newItem.id = 'item_' + Date.now() + '_' + Math.floor(Math.random()*1000);
            
            items.unshift(newItem);
            this.saveItems(items);

            // Se foi Cut, remove da pasta original
            if (this.clipboard.action === 'cut') {
                const sourceKey = this.keys[this.clipboard.sourceFolder];
                let sourceItems = [];
                try { sourceItems = JSON.parse(localStorage.getItem(sourceKey)) || []; } catch(e){}
                sourceItems = sourceItems.filter(i => i.id !== this.clipboard.item.id);
                localStorage.setItem(sourceKey, JSON.stringify(sourceItems));
                
                this.clipboard = null; // Cut só cola uma vez
            }

            if (window.showToast) window.showToast('Colado', 'success');
            // Re-render caso estejamos vendo a pasta de destino
            this.render();
        }
    },

    deleteAction: function() {
        if (this.selectedId) {
            let items = this.getItems();
            items = items.filter(i => i.id !== this.selectedId);
            this.selectedId = null;
            this.saveItems(items);
            if (window.showToast) window.showToast('Deletado', 'info');
        }
    },

    downloadAction: function() {
        if (this.selectedId) {
            const items = this.getItems();
            const item = items.find(i => i.id === this.selectedId);
            if (item) {
                let content = '';
                let filename = item.title || 'apollo_export';
                let mimeType = 'text/plain';

                if (item.data && item.data.url) {
                    const a = document.createElement('a');
                    a.href = item.data.url;
                    a.download = filename;
                    a.click();
                    return;
                }

                if (item.type === 'text') {
                    content = item.data || item.title;
                    filename += '.txt';
                } else {
                    content = JSON.stringify(item, null, 2);
                    filename += '.json';
                    mimeType = 'application/json';
                }

                const blob = new Blob([content], { type: mimeType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
                if (window.showToast) window.showToast('Download iniciado', 'success');
            }
        } else {
            if (window.showToast) window.showToast('Selecione um item para baixar', 'error');
        }
    },

    undoAction: function() {
        if (this.history.length > 0) {
            const lastState = this.history.pop();
            localStorage.setItem(this.keys[lastState.folder], lastState.data);
            this.selectedId = null;
            this.render();
            if (window.showToast) window.showToast('Desfeito (Ctrl+Z)', 'info');
        } else {
            if (window.showToast) window.showToast('Nada para desfazer', 'error');
        }
    },

    newTextAction: function() {
        const text = prompt("Digite um texto ou anotação rápida:");
        if (text && text.trim() !== '') {
            this.addItem('text', 'Anotação', 'Texto', null, text);
        }
    },

    addItem: function(type, title, subtitle, thumbnail, dataPayload = null) {
        const items = this.getItems();
        const newItem = {
            id: 'item_' + Date.now() + '_' + Math.floor(Math.random()*1000),
            type: type,
            title: title,
            subtitle: subtitle,
            thumbnail: thumbnail,
            data: dataPayload,
            timestamp: Date.now()
        };
        items.unshift(newItem);
        this.saveItems(items);
    },

    toggleFolder: function(targetFolder) {
        if (targetFolder) {
            this.currentFolder = targetFolder;
        }
        this.selectedId = null;
        this.render();
    },

    // --- NOVA API PARA FERRAMENTAS NATIVAS ---
    receiveFile: function(blobOrFile, filename) {
        let type = 'file';
        if (blobOrFile.type.startsWith('image/')) type = 'image';
        else if (blobOrFile.type.startsWith('video/')) type = 'video';
        else if (blobOrFile.type.startsWith('audio/')) type = 'audio';
        else if (blobOrFile.type.startsWith('text/')) type = 'text';

        const fileUrl = URL.createObjectURL(blobOrFile);
        
        // Pula pro Bagageiro pra salvar (ou mantém na currentFolder se preferir)
        // O usuário pediu pra cair no bagageiro. Mas a Área de Transferência (transfer) é a HUD padrão.
        this.addItem(type, filename, (blobOrFile.size / (1024*1024)).toFixed(2) + ' MB', type === 'image' ? fileUrl : null, { originalFileObj: true, url: fileUrl });
        
        if (window.showToast) window.showToast('📥 ' + filename + ' salvo na Área de Transferência!', 'success');
        else alert(filename + ' salvo na Área de Transferência!');
    },

    toggleMinimize: function() {
        const hud = document.getElementById('apollo-transfer-hud');
        let minIcon = document.getElementById('hud-minimized-icon');
        
        if (!minIcon) {
            minIcon = document.createElement('div');
            minIcon.id = 'hud-minimized-icon';
            minIcon.innerHTML = '🎒';
            minIcon.title = 'Abrir Área de Transferência';
            minIcon.style.cssText = 'position: fixed; bottom: 20px; right: 20px; width: 100px; height: 100px; background: rgba(15,23,42,0.95); border: 3px solid var(--btn-purple, #8b5cf6); border-radius: 50%; display: none; align-items: center; justify-content: center; font-size: 50px; cursor: pointer; box-shadow: 0 0 20px rgba(139,92,246,0.5); z-index: 9999; transition: transform 0.2s, box-shadow 0.2s; backdrop-filter: blur(5px);';
            
            minIcon.onmouseover = () => { minIcon.style.transform = 'scale(1.1)'; minIcon.style.boxShadow = '0 0 30px rgba(139,92,246,0.8)'; };
            minIcon.onmouseout = () => { minIcon.style.transform = 'scale(1)'; minIcon.style.boxShadow = '0 0 20px rgba(139,92,246,0.5)'; };
            
            let isDragging = false;
            let didDrag = false;
            let startX, startY, initialLeft, initialTop;

            minIcon.onmousedown = (e) => {
                isDragging = true;
                didDrag = false;
                startX = e.clientX;
                startY = e.clientY;
                const rect = minIcon.getBoundingClientRect();
                initialLeft = rect.left;
                initialTop = rect.top;
                document.body.style.userSelect = 'none';
                document.querySelectorAll('iframe').forEach(f => f.style.pointerEvents = 'none');
            };

            document.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                const dx = e.clientX - startX;
                const dy = e.clientY - startY;
                if (Math.abs(dx) > 3 || Math.abs(dy) > 3) didDrag = true;
                if (didDrag) {
                    let newLeft = initialLeft + dx;
                    let newTop = initialTop + dy;
                    
                    const maxLeft = window.innerWidth - minIcon.offsetWidth;
                    const maxTop = window.innerHeight - minIcon.offsetHeight;
                    
                    newLeft = Math.max(0, Math.min(newLeft, maxLeft));
                    newTop = Math.max(0, Math.min(newTop, maxTop));
                    
                    minIcon.style.left = `${newLeft}px`;
                    minIcon.style.top = `${newTop}px`;
                    minIcon.style.bottom = 'auto';
                    minIcon.style.right = 'auto';
                }
            });

            document.addEventListener('mouseup', () => {
                if (isDragging && didDrag) {
                    localStorage.setItem('apollo_transfer_pos', JSON.stringify({ left: minIcon.style.left, top: minIcon.style.top }));
                }
                isDragging = false;
                document.body.style.userSelect = '';
                document.querySelectorAll('iframe').forEach(f => f.style.pointerEvents = 'auto');
            });

            minIcon.onclick = () => {
                if (didDrag) return; // Não clica se apenas arrastou
                this.toggleMinimize();
            };
            document.body.appendChild(minIcon);
        }

        if (hud.style.display !== 'none') {
            // Minimize
            hud.style.display = 'none';
            minIcon.style.display = 'flex';
        } else {
            // Restore
            hud.style.display = 'flex';
            minIcon.style.display = 'none';
        }
    },

    // --- RENDERIZAÇÃO DA UI ---
    render: function() {
        const hud = document.getElementById('apollo-transfer-hud');
        if (!hud) return;

        const titleEl = document.getElementById('hud-os-title');
        const countEl = document.getElementById('hud-os-count');
        const toggleBtn = document.getElementById('hud-toggle-folder-btn');
        const container = document.getElementById('hud-item-container');

        const items = this.getItems();

        // Atualiza Labels baseados na pasta atual
        if (this.currentFolder === 'transfer') {
            titleEl.innerHTML = '🎒 ÁREA DE BAGAGEM';
            hud.style.borderColor = 'var(--btn-purple, #8b5cf6)';
        } else if (this.currentFolder === 'bagageiro') {
            titleEl.innerHTML = '🚘 GARAGEM (ESTOQUE)';
            hud.style.borderColor = 'var(--btn-yellow, #FFD32A)';
        } else if (this.currentFolder === 'ias') {
            titleEl.innerHTML = '🚀 NITRO IA (MECÂNICOS)';
            hud.style.borderColor = '#ef4444';
        } else if (this.currentFolder === 'fx') {
            titleEl.innerHTML = '🔧 PEÇAS (ASSETS)';
            hud.style.borderColor = '#10b981';
        } else if (this.currentFolder === 'configs') {
            titleEl.innerHTML = '🏎️ CHASSI (TEMPLATES)';
            hud.style.borderColor = '#3b82f6';
        }
        
        // Update active states and texts
        const btnTransfer = document.getElementById('btn-folder-transfer');
        const btnBagageiro = document.getElementById('btn-folder-bagageiro');
        const btnIas = document.getElementById('btn-folder-ias');
        const btnFx = document.getElementById('btn-folder-fx');
        const btnConfigs = document.getElementById('btn-folder-configs');
        
        [btnTransfer, btnBagageiro, btnIas, btnFx, btnConfigs].forEach(btn => {
            if(btn) btn.classList.remove('active');
        });

        if (this.currentFolder === 'transfer' && btnTransfer) btnTransfer.classList.add('active');
        if (this.currentFolder === 'bagageiro' && btnBagageiro) btnBagageiro.classList.add('active');
        if (this.currentFolder === 'ias' && btnIas) btnIas.classList.add('active');
        if (this.currentFolder === 'fx' && btnFx) btnFx.classList.add('active');
        if (this.currentFolder === 'configs' && btnConfigs) btnConfigs.classList.add('active');

        countEl.innerText = items.length;
        container.innerHTML = '';

        if (items.length === 0) {
            container.innerHTML = '<div style="width:100%; text-align:center; padding: 20px; color: #64748b; font-family: Nunito;">Esta pasta está vazia.</div>';
            return;
        }

        // Renderiza itens
        items.forEach(item => {
            const isSelected = this.selectedId === item.id;
            
            let iconHtml = '<div class="hud-item-icon">📝</div>';
            if (item.thumbnail) {
                iconHtml = `<div class="hud-item-icon" style="background: url('${item.thumbnail}') center/cover;"></div>`;
            } else if (item.type === 'video') {
                iconHtml = '<div class="hud-item-icon">🎥</div>';
            } else if (item.type === 'audio') {
                iconHtml = '<div class="hud-item-icon">🎵</div>';
            } else if (item.type === 'text') {
                iconHtml = '<div class="hud-item-icon">📰</div>';
            } else if (item.type === 'ai') {
                const aiIcon = (item.data && item.data.icon) ? item.data.icon : '🤖';
                const badge = (item.data && item.data.badge) ? `<div style="position:absolute; top:-5px; right:-5px; background:#0ea5e9; color:white; font-size:0.6rem; padding:2px 4px; border-radius:10px; font-weight:bold;">${item.data.badge}</div>` : '';
                iconHtml = `<div class="hud-item-icon" style="position:relative;">${aiIcon}${badge}</div>`;
            } else if (item.type === 'projeto') {
                iconHtml = '<div class="hud-item-icon">🎬</div>';
            }

            const itemDiv = document.createElement('div');
            itemDiv.className = `hud-item ${isSelected ? 'selected' : ''}`;
            itemDiv.style.border = isSelected ? '2px solid var(--btn-green)' : '';
            itemDiv.setAttribute('draggable', 'true');
            itemDiv.innerHTML = `
                ${iconHtml}
                <div class="hud-item-info">
                    <strong>${item.title}</strong>
                    <span>${item.subtitle}</span>
                </div>
            `;

            // Configurar Drag from HUD
            itemDiv.addEventListener('dragstart', (e) => {
                const payload = {
                    source: 'hud',
                    id: item.id,
                    type: item.type === 'ai' ? (item.data.type || item.type) : item.type,
                    name: item.title,
                    icon: item.data && item.data.icon ? item.data.icon : '📝',
                    badge: item.data && item.data.badge ? item.data.badge : '',
                    isProject: item.type === 'projeto',
                    folder: this.currentFolder,
                    originalItem: item
                };
                e.dataTransfer.setData('application/json', JSON.stringify(payload));
                e.dataTransfer.setData('text/plain', item.id);
                itemDiv.style.opacity = '0.5';
            });
            itemDiv.addEventListener('dragend', () => {
                itemDiv.style.opacity = '1';
                document.querySelectorAll('.drop-zone-slot').forEach(sz => sz.classList.remove('drag-over'));
            });

            // Evento de seleção (Click)
            itemDiv.onclick = (e) => {
                this.selectedId = item.id;
                this.render();
            };

            // Evento de abertura dupla (Double Click)
            itemDiv.ondblclick = (e) => {
                if (item.type === 'image' || (item.type === 'file' && item.title.match(/\.(png|jpg|jpeg|webp)$/i))) {
                    const url = `photopea_wrapper.html?item_id=${item.id}`;
                    const tabTitle = `🎨 ${item.title.substring(0, 10)}...`;
                    if (window.parent && window.parent.openAppTab) {
                        window.parent.openAppTab(url, tabTitle, true);
                    } else if (window.openAppTab) {
                        window.openAppTab(url, tabTitle, true);
                    }
                }
            };


            container.appendChild(itemDiv);
        });
    },

    // --- INICIALIZAÇÃO E INJEÇÃO DO HTML ---
    init: function() {
        if (document.getElementById('apollo-transfer-hud')) return;

        const style = document.createElement('style');
        style.innerHTML = `
            #apollo-transfer-hud { position: fixed; bottom: 20px; right: 20px; width: 380px; background: rgba(15, 23, 42, 0.95); border: 2px solid var(--btn-purple, #8b5cf6); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); z-index: 9999; display: flex; flex-direction: column; overflow: hidden; backdrop-filter: blur(10px); transition: border-color 0.3s; }
            #hud-header { background: rgba(0,0,0,0.3); padding: 15px; display: flex; flex-direction: column; gap: 10px; border-bottom: 2px solid #334155; cursor: grab; }
            .hud-header-top { display: flex; justify-content: space-between; align-items: center; width: 100%; }
            .hud-header-tabs { display: flex; gap: 6px; width: 100%; justify-content: space-between; }
            #hud-header:active { cursor: grabbing; }
            #hud-os-title { margin: 0; color: #fff; font-size: 1.2rem; font-family: 'Bangers', cursive; display: flex; align-items: center; gap: 8px; letter-spacing: 1px; }
            .hud-count { background: var(--btn-purple, #8b5cf6); color: white; border-radius: 12px; padding: 2px 8px; font-size: 0.8rem; font-family: 'Nunito', sans-serif; font-weight: bold; }
            .hud-controls { display: flex; gap: 5px; }
            .hud-control-btn { background: none; border: none; color: #cbd5e1; cursor: pointer; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 4px; transition: 0.2s; }
            .hud-control-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }
            
            /* OS TOOLBAR */
            .os-toolbar { display: flex; gap: 5px; padding: 8px 15px; background: rgba(0,0,0,0.2); border-bottom: 1px solid #334155; }
            .os-tool-btn { background: #334155; color: #cbd5e1; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; transition: 0.2s; flex: 1; display:flex; justify-content:center; align-items:center; }
            .os-tool-btn:hover { background: #3b82f6; color: white; }
            .os-tool-btn.upload { background: var(--btn-green); color: white; font-weight: bold; }
            .os-tool-btn.upload:hover { background: #059669; }

            .hud-folder-btn { flex: 1; background: linear-gradient(180deg, #1e293b, #0f172a); color: #94a3b8; border: 1px solid #334155; padding: 6px 0; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 6px rgba(0,0,0,0.3); }
            .hud-folder-btn div { font-size: 1.1rem; filter: grayscale(0.5) opacity(0.8); transition: 0.3s; }
            .hud-folder-btn span { font-family: 'Nunito', sans-serif; font-size: 0.55rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0.5px; }
            .hud-folder-btn:hover { background: linear-gradient(180deg, #334155, #1e293b); color: #e2e8f0; transform: translateY(-2px); }
            .hud-folder-btn:hover div { filter: grayscale(0) opacity(1); }
            .hud-folder-btn:active { transform: translateY(1px); box-shadow: 0 1px 0 rgba(0,0,0,0.5); }
            .hud-folder-btn.active { background: #0f172a; border-color: var(--theme-color); color: #fff; box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 0 12px var(--theme-color); }
            .hud-folder-btn.active div { filter: grayscale(0) opacity(1); transform: scale(1.1); }
            .hud-folder-btn.active span { color: var(--theme-color); text-shadow: 0 0 5px var(--theme-color); }
            
            .hud-body { padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; flex-grow: 1; }
            .hud-body::-webkit-scrollbar { width: 6px; }
            .hud-body::-webkit-scrollbar-thumb { background: #475569; border-radius: 6px; }
            
            .hud-item { display: flex; align-items: center; gap: 12px; background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; border: 1px solid #334155; cursor: pointer; transition: all 0.2s; user-select: none; }
            .hud-item:hover { background: rgba(255,255,255,0.1); transform: translateY(-2px); }
            .hud-item.selected { background: rgba(59, 130, 246, 0.2); }
            .hud-item-icon { width: 40px; height: 40px; border-radius: 8px; background: #1e293b; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
            .hud-item-info { display: flex; flex-direction: column; overflow: hidden; }
            .hud-item-info strong { color: #fff; font-size: 0.9rem; font-family: 'Nunito', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .hud-item-info span { color: #94a3b8; font-size: 0.75rem; font-family: 'Nunito', sans-serif; }
        `;
        document.head.appendChild(style);

        const hudHTML = `
        <div id="apollo-transfer-hud" style="resize: both; min-width: 300px; min-height: 200px; height: 450px;">
            <div id="hud-header">
                <div class="hud-header-top">
                    <h3 id="hud-os-title">🎒 ÁREA DE TRANSFERÊNCIA <span class="hud-count" id="hud-os-count">0</span></h3>
                    <button onclick="apolloTransferOS.toggleMinimize()" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color:#fff; width:30px; height:30px; border-radius:6px; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:0.2s;" title="Minimizar">➖</button>
                </div>
                <div class="hud-header-tabs">
                    <button id="btn-folder-transfer" onclick="apolloTransferOS.toggleFolder('transfer')" class="hud-folder-btn" style="--theme-color: #8b5cf6;">
                        <div>🎒</div><span>BAGAGEM</span>
                    </button>
                    <button id="btn-folder-bagageiro" onclick="apolloTransferOS.toggleFolder('bagageiro')" class="hud-folder-btn" style="--theme-color: #f59e0b;">
                        <div>🚘</div><span>GARAGEM</span>
                    </button>
                    <button id="btn-folder-ias" onclick="apolloTransferOS.toggleFolder('ias')" class="hud-folder-btn" style="--theme-color: #ef4444;">
                        <div>🚀</div><span>NITRO IA</span>
                    </button>
                    <button id="btn-folder-fx" onclick="apolloTransferOS.toggleFolder('fx')" class="hud-folder-btn" style="--theme-color: #10b981;">
                        <div>🔧</div><span>PEÇAS</span>
                    </button>
                    <button id="btn-folder-configs" onclick="apolloTransferOS.toggleFolder('configs')" class="hud-folder-btn" style="--theme-color: #3b82f6;">
                        <div>🏎️</div><span>CHASSI</span>
                    </button>
                </div>
            </div>

            <!-- OS TOOLBAR -->
            <div class="os-toolbar">
                <button id="hud-text-btn" class="os-tool-btn" title="Novo Texto" onclick="apolloTransferOS.newTextAction()">➕</button>
                <button id="hud-cut-btn" class="os-tool-btn" title="Arraste ou clique para Cortar (Ctrl+X)" onclick="apolloTransferOS.cutAction()">✂</button>
                <button id="hud-copy-btn" class="os-tool-btn" title="Arraste ou clique para Copiar (Ctrl+C)" onclick="apolloTransferOS.copyAction()">📄</button>
                <button id="hud-paste-btn" class="os-tool-btn" title="Colar (Ctrl+V)" onclick="apolloTransferOS.pasteAction()">📋</button>
                <button id="hud-trash-btn" class="os-tool-btn" title="Arraste itens aqui ou clique para Deletar (Del)" onclick="apolloTransferOS.deleteAction()">🗑️</button>
                <button id="hud-undo-btn" class="os-tool-btn" title="Desfazer (Ctrl+Z)" onclick="apolloTransferOS.undoAction()">↩</button>
                <button id="hud-download-btn" class="os-tool-btn" title="Arraste ou clique para Download" onclick="apolloTransferOS.downloadAction()">⬇️</button>
                <button id="hud-upload-btn" class="os-tool-btn upload" title="Upload de Arquivo" onclick="window.openUploadModal()">⬆️ UPLOAD</button>
            </div>
            
            <div class="hud-body" id="hud-item-container">
                <!-- Render via JS -->
            </div>
            
            <!-- Indicador de Resize -->
            <div style="position: absolute; bottom: 4px; right: 4px; font-size: 16px; color: rgba(255,255,255,0.4); pointer-events: none; transform: rotate(-45deg);">⇲</div>
        </div>

        <!-- Modal Global de Upload -->
        <div id="upload-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 9999; justify-content: center; align-items: center; backdrop-filter: blur(5px);">
            <div style="background: #1e1e1e; padding: 40px; border-radius: 16px; border: 2px solid #444; width: 500px; max-width: 90%; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.8); position: relative;">
                <button onclick="window.closeUploadModal()" style="position: absolute; top: -15px; right: -15px; background: var(--btn-red); border: var(--border-thick); width: 40px; height: 40px; border-radius: 50%; color: #fff; font-family: 'Bangers'; font-size: 1.5rem; cursor: pointer; box-shadow: 0 4px 0 var(--border-dark);">X</button>
                <h3 style="margin-bottom:15px; color: var(--btn-yellow); font-family: 'Bangers'; font-size:2.5rem; text-shadow: 2px 2px 0 var(--border-dark);">Upload p/ Nuvem</h3>
                <p style="font-size:1rem; color: #fff; font-weight:800; margin-bottom: 25px;">Envio direto pelo navegador.</p>
                <input type="file" id="file-input" accept=".png,.jpg,.jpeg,.mp4,.mp3,.wav,.txt,.json,.md" style="margin-bottom: 20px; width:100%; border:var(--border-thick); border-radius:12px; padding:15px; font-weight: 800; font-family: 'Nunito';" />
                <div id="upload-progress" style="display:none; width:100%; background:#e2e8f0; height:16px; border-radius:8px; margin-bottom: 15px; border: 2px solid var(--border-dark);">
                    <div id="upload-bar" style="width:0%; height:100%; background:var(--btn-green); border-radius:6px; transition:width 0.2s;"></div>
                </div>
                <p id="upload-status" style="font-size:1rem; font-weight:800; color:var(--btn-yellow); margin-bottom: 25px;"></p>
                <button class="btn yellow" style="width:100%; font-size:1.5rem;" onclick="window.startS3Upload()">INICIAR UPLOAD</button>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', hudHTML);

        this.render();
        this.makeDraggable();
        this.attachGlobalEvents();
    },

    makeDraggable: function() {
        const hud = document.getElementById('apollo-transfer-hud');
        const header = document.getElementById('hud-header');
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        // Restore position on init
        try {
            const savedPos = JSON.parse(localStorage.getItem('apollo_transfer_pos'));
            if (savedPos && savedPos.left) {
                let leftNum = parseFloat(savedPos.left);
                let topNum = parseFloat(savedPos.top);
                
                // Prevent bleeding completely off-screen
                leftNum = Math.max(-200, Math.min(leftNum, window.innerWidth - 50));
                topNum = Math.max(0, Math.min(topNum, window.innerHeight - 50));
                
                hud.style.left = `${leftNum}px`;
                hud.style.top = `${topNum}px`;
                hud.style.bottom = 'auto';
                hud.style.right = 'auto';
            }
        } catch(e) {}

        header.addEventListener('mousedown', (e) => {
            if(e.target.closest('button')) return;
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            const rect = hud.getBoundingClientRect();
            initialLeft = rect.left;
            initialTop = rect.top;
            document.body.style.userSelect = 'none';
            document.querySelectorAll('iframe').forEach(f => f.style.pointerEvents = 'none');
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            
            let newLeft = initialLeft + dx;
            let newTop = initialTop + dy;
            
            // Relaxed constraints to allow dragging slightly off-screen like a real OS window
            newLeft = Math.max(-hud.offsetWidth + 50, Math.min(newLeft, window.innerWidth - 50));
            newTop = Math.max(0, Math.min(newTop, window.innerHeight - 50));
            
            hud.style.left = `${newLeft}px`;
            hud.style.top = `${newTop}px`;
            hud.style.bottom = 'auto';
            hud.style.right = 'auto';
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                localStorage.setItem('apollo_transfer_pos', JSON.stringify({ left: hud.style.left, top: hud.style.top }));
            }
            isDragging = false;
            document.body.style.userSelect = '';
            document.querySelectorAll('iframe').forEach(f => f.style.pointerEvents = 'auto');
        });
    },

    attachGlobalEvents: function() {
        const hud = document.getElementById('apollo-transfer-hud');
        
        // DRAG AND DROP OS FILES
        hud.addEventListener('dragover', (e) => {
            e.preventDefault();
            hud.style.boxShadow = '0 0 20px var(--btn-green)';
        });
        hud.addEventListener('dragleave', (e) => {
            hud.style.boxShadow = '0 10px 30px rgba(0,0,0,0.8)';
        });
        hud.addEventListener('drop', (e) => {
            e.preventDefault();
            hud.style.boxShadow = '0 10px 30px rgba(0,0,0,0.8)';
            
            // Files drag
            if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                window.processDroppedFiles(e.dataTransfer.files);
                return;
            }

            // Drag from chat_ia sidebar
            const payloadStr = e.dataTransfer.getData('application/json');
            if (payloadStr) {
                try {
                    const payload = JSON.parse(payloadStr);
                    if (payload.source === 'sidebar') {
                        // Switch folder if dropping AI
                        if (payload.isProject) {
                            apolloTransferOS.toggleFolder('transfer');
                        } else {
                            apolloTransferOS.toggleFolder('ias');
                        }
                        
                        // Add to HUD
                        apolloTransferOS.addItem(
                            payload.isProject ? 'projeto' : 'ai',
                            payload.name,
                            payload.isProject ? 'Save State' : payload.type,
                            null,
                            payload
                        );

                        // Remove from sidebar
                        const el = document.getElementById(payload.id);
                        if(el) el.remove();
                        if (window.showToast) window.showToast('Item movido para Área de Transferência', 'success');
                    }
                } catch(err) {}
            }
        });

        // GLOBAL OS PASTE
        document.addEventListener('paste', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            if (e.clipboardData && e.clipboardData.files && e.clipboardData.files.length > 0) {
                window.processDroppedFiles(e.clipboardData.files);
            }
        });

        // DRAG TO ACTIONS (Trash, Copy, Cut, Download)
        const setupActionDrop = (btnId, actionFn) => {
            const btn = document.getElementById(btnId);
            if (!btn) return;
            btn.addEventListener('dragover', (e) => {
                e.preventDefault();
                btn.style.background = '#ef4444'; // Red highlight for action
                btn.style.color = '#fff';
                btn.style.transform = 'scale(1.1)';
            });
            btn.addEventListener('dragleave', (e) => {
                btn.style.background = '';
                btn.style.color = '';
                btn.style.transform = 'scale(1)';
            });
            btn.addEventListener('drop', (e) => {
                e.preventDefault();
                btn.style.background = '';
                btn.style.color = '';
                btn.style.transform = 'scale(1)';
                
                const id = e.dataTransfer.getData('text/plain');
                if (id && id.startsWith('item_')) {
                    apolloTransferOS.selectedId = id;
                    actionFn.call(apolloTransferOS);
                }
            });
        };
        
        setupActionDrop('hud-trash-btn', apolloTransferOS.deleteAction);
        setupActionDrop('hud-copy-btn', apolloTransferOS.copyAction);
        setupActionDrop('hud-cut-btn', apolloTransferOS.cutAction);
        setupActionDrop('hud-download-btn', apolloTransferOS.downloadAction);

        // DRAG TO TABS (Move items between folders)
        const folderIds = ['btn-folder-transfer', 'btn-folder-bagageiro', 'btn-folder-ias', 'btn-folder-fx', 'btn-folder-configs'];
        const folderKeys = ['transfer', 'bagageiro', 'ias', 'fx', 'configs'];
        
        folderIds.forEach((btnId, index) => {
            const btn = document.getElementById(btnId);
            const targetFolder = folderKeys[index];
            if (!btn) return;

            btn.addEventListener('dragover', (e) => {
                e.preventDefault();
                btn.style.boxShadow = 'inset 0 1px 0 rgba(255,255,255,0.1), 0 0 15px var(--theme-color)';
                btn.style.transform = 'scale(1.05)';
            });
            btn.addEventListener('dragleave', (e) => {
                btn.style.boxShadow = '';
                btn.style.transform = '';
            });
            btn.addEventListener('drop', (e) => {
                e.preventDefault();
                btn.style.boxShadow = '';
                btn.style.transform = '';

                const id = e.dataTransfer.getData('text/plain');
                if (id && id.startsWith('item_')) {
                    const sourceItems = apolloTransferOS.getItems();
                    const itemIndex = sourceItems.findIndex(i => i.id === id);
                    if (itemIndex > -1) {
                        // Remove from source
                        const item = sourceItems.splice(itemIndex, 1)[0];
                        apolloTransferOS.saveItems(sourceItems, true); // save source without history
                        
                        // Add to destination
                        let targetItems = [];
                        try {
                            const data = localStorage.getItem(apolloTransferOS.keys[targetFolder]);
                            targetItems = data ? JSON.parse(data) : [];
                        } catch(err) {}
                        targetItems.unshift(item);
                        localStorage.setItem(apolloTransferOS.keys[targetFolder], JSON.stringify(targetItems));
                        
                        if (window.showToast) window.showToast('Item movido para ' + btn.querySelector('span').innerText, 'success');
                        apolloTransferOS.render(); // Re-render current folder
                    }
                }
            });
        });

        // KEYBOARD SHORTCUTS
        document.addEventListener('keydown', (e) => {
            // Se o foco não está em inputs
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                if (e.ctrlKey && e.key.toLowerCase() === 'c') { e.preventDefault(); this.copyAction(); }
                if (e.ctrlKey && e.key.toLowerCase() === 'x') { e.preventDefault(); this.cutAction(); }
                if (e.ctrlKey && e.key.toLowerCase() === 'v') { e.preventDefault(); this.pasteAction(); }
                if (e.ctrlKey && e.key.toLowerCase() === 'z') { e.preventDefault(); this.undoAction(); }
                if (e.key === 'Delete') { e.preventDefault(); this.deleteAction(); }
            }
        });
    }
};

window.processDroppedFiles = function(files) {
    // Usar URL.createObjectURL em vez de FileReader para suportar arquivos gigantes
    Array.from(files).forEach(file => {
        const fileUrl = URL.createObjectURL(file); // Permite referenciar arquivos de gigabytes sem crashear a RAM
        let type = 'file';
        if (file.type.startsWith('image/')) type = 'image';
        else if (file.type.startsWith('video/')) type = 'video';
        else if (file.type.startsWith('audio/')) type = 'audio';
        else if (file.type.startsWith('text/')) type = 'text';

        apolloTransferOS.addItem(type, file.name, (file.size / (1024*1024)).toFixed(2) + ' MB', type === 'image' ? fileUrl : null, { originalFileObj: true, url: fileUrl });
    });
}

// UPLOAD MODAL LOGIC
window.openUploadModal = function() {
    document.getElementById('upload-modal').style.display = 'flex';
}
window.closeUploadModal = function() {
    document.getElementById('upload-modal').style.display = 'none';
}
window.startS3Upload = function() {
    const fileInput = document.getElementById('file-input');
    const bar = document.getElementById('upload-bar');
    const prog = document.getElementById('upload-progress');
    const stat = document.getElementById('upload-status');

    if (!fileInput.files || fileInput.files.length === 0) {
        stat.innerText = "Selecione um arquivo primeiro!";
        return;
    }

    const file = fileInput.files[0];
    prog.style.display = 'block';
    stat.innerText = "Iniciando upload...";
    bar.style.width = '0%';

    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        bar.style.width = progress + '%';
        stat.innerText = `Enviando... \${progress}%`;

        if (progress >= 100) {
            clearInterval(interval);
            stat.innerText = "Upload Concluído!";
            stat.style.color = "var(--btn-green)";
            
            let type = 'file';
            if (file.type.startsWith('image')) type = 'image';
            if (file.type.startsWith('video')) type = 'video';
            if (file.type.startsWith('audio')) type = 'audio';
            
            // ADICIONA NO HUD ATUAL NATIVAMENTE
            apolloTransferOS.addItem(type, file.name, 'S3 Upload', null);

            setTimeout(() => {
                window.closeUploadModal();
                stat.innerText = "";
                stat.style.color = "var(--btn-yellow)";
                prog.style.display = 'none';
                bar.style.width = '0%';
                fileInput.value = '';
            }, 1000);
        }
    }, 100);
}

// Inicializa no fim do load
document.addEventListener('DOMContentLoaded', () => {
    if (window.self !== window.top) return; // Do not render Bagageiro UI inside iframes
    if (window.apolloTransferOS) {
        window.apolloTransferOS.init();
    }
});

// --- DELEGATE IFRAME APIS TO PARENT ---
const originalAddItem = window.apolloTransferOS.addItem;
window.apolloTransferOS.addItem = function(type, name, size, img, metadata) {
    if (window.self !== window.top && window.parent.apolloTransferOS) {
        return window.parent.apolloTransferOS.addItem(type, name, size, img, metadata);
    }
    return originalAddItem.call(this, type, name, size, img, metadata);
};

const originalReceiveFile = window.apolloTransferOS.receiveFile;
window.apolloTransferOS.receiveFile = function(file, filename) {
    if (window.self !== window.top && window.parent.apolloTransferOS) {
        return window.parent.apolloTransferOS.receiveFile(file, filename);
    }
    return originalReceiveFile ? originalReceiveFile.call(this, file, filename) : null;
};

// --- INTERCOMUNICAÇÃO COM ENGINES EXTERNAS (Iframes) ---
window.addEventListener('message', function(event) {
    const data = event.data;
    if (data && data.action === 'export_to_bagageiro') {
        const fileContent = data.content; // Uint8Array, Blob ou String
        const fileName = data.filename || `Export_${Date.now()}`;
        const mimeType = data.mimeType || 'application/octet-stream';
        
        let file;
        if (fileContent instanceof Blob) {
            file = new File([fileContent], fileName, { type: mimeType });
        } else if (fileContent instanceof Uint8Array || fileContent instanceof ArrayBuffer) {
            file = new File([fileContent], fileName, { type: mimeType });
        } else {
            file = new File([fileContent], fileName, { type: mimeType });
        }
        
        if (window.self !== window.top && window.parent.processDroppedFiles) {
             window.parent.processDroppedFiles([file]);
        } else if (window.processDroppedFiles) {
             window.processDroppedFiles([file]);
        }
        
        if (window.showToast) window.showToast("Exportado do App Externo para o Bagageiro!", "#059669");
        else if (window.parent.showToast) window.parent.showToast("Exportado do App Externo para o Bagageiro!", "#059669");
    }
});
