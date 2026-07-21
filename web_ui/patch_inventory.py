import os

new_code = '''/**
 * Apollo La Plata - Ponte de Inventário V2 (Packs e Magic Squares)
 * Permite copiar mídias isoladas ou agrupar várias mídias em "Packs" dinâmicos.
 */

window.laplataInventory = {
    KEY: 'laplata_inventory_clip_v2', // Nova chave para evitar crash com V1
    
    state: {
        currentFolder: null // null = root, senao = ID do pack aberto
    },

    // Retorna todos os itens do inventário
    getItems: function() {
        try {
            const data = localStorage.getItem(this.KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            return [];
        }
    },

    // Salva itens no inventário
    saveItems: function(items) {
        localStorage.setItem(this.KEY, JSON.stringify(items));
        this.updateUI();
    },

    // API Retrocompatível com V1
    // copy(base64Image) -> Adiciona como single image
    copy: function(payload, type = 'image', metadata = {}) {
        const items = this.getItems();
        
        let newItem = {
            id: 'item_' + Date.now() + '_' + Math.floor(Math.random()*1000),
            type: type, // 'image', 'pack', 'prompt', etc
            data: payload,
            metadata: metadata,
            timestamp: Date.now()
        };

        // Se estivermos dentro de um pack, tentar adicionar dentro do pack (Opcional)
        // Por padrão, sempre copia pro root
        items.unshift(newItem); 
        
        this.saveItems(items);

        if (window.apolloNotifications) {
            window.apolloNotifications.add("Copiado!", "Item enviado para a Área de Transferência 🎒", "system");
        }
        if (window.apolloCopilot) window.apolloCopilot.react("copy_inventory");
        if (window.apolloSFX) window.apolloSFX.play('click');
    },

    // Novo: Adicionar um Pack inteiro de uma vez
    addPack: function(title, itemsArray, metadata = {}) {
        const items = this.getItems();
        
        // Thumbnail do pack será o primeiro item de imagem, ou um ícone padrão
        let thumb = '';
        if (itemsArray.length > 0 && itemsArray[0].type === 'image') {
            thumb = itemsArray[0].data;
        }

        const newPack = {
            id: 'pack_' + Date.now(),
            type: 'pack',
            title: title,
            thumbnail: thumb,
            count: itemsArray.length,
            items: itemsArray,
            metadata: metadata,
            timestamp: Date.now()
        };

        items.unshift(newPack);
        this.saveItems(items);
        
        if (window.apolloNotifications) {
            window.apolloNotifications.add("Pack Salvo!", title + " enviado para a Área 🎒", "system");
        }
        if (window.apolloSFX) window.apolloSFX.play('success');
    },

    clear: function() {
        localStorage.removeItem(this.KEY);
        this.state.currentFolder = null;
        this.updateUI();
        if (window.apolloSFX) window.apolloSFX.play('click');
    },

    removeItem: function(id) {
        let items = this.getItems();
        items = items.filter(i => i.id !== id);
        this.saveItems(items);
    },

    // UI
    initUI: function() {
        if (document.getElementById('laplata-inventory-widget')) return;

        const style = document.createElement('style');
        style.innerHTML = 
            #laplata-inventory-widget {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                gap: 10px;
                font-family: 'Inter', sans-serif;
            }

            #laplata-inventory-btn {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background: linear-gradient(135deg, #f59e0b, #d97706);
                border: 2px solid #fff;
                box-shadow: 0 5px 15px rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                cursor: pointer;
                transition: all 0.2s;
                position: relative;
            }
            #laplata-inventory-btn:hover { transform: scale(1.1); }
            
            #laplata-inventory-badge {
                position: absolute; top: -5px; right: -5px;
                background: #ef4444; color: white; font-size: 0.6rem; font-weight: bold;
                width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
                border: 2px solid #0f172a; display: none;
            }

            #laplata-inventory-panel {
                background: rgba(15, 23, 42, 0.95);
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 15px;
                width: 320px; /* Mais largo para caber a grade */
                max-height: 400px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.8);
                backdrop-filter: blur(10px);
                display: none;
                flex-direction: column;
                transform-origin: bottom right;
                animation: inventoryPop 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            }
            
            #laplata-inventory-header {
                display: flex; justify-content: space-between; align-items: center;
                border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 10px;
            }

            #laplata-inventory-header h4 { margin: 0; color: white; font-size: 0.9rem; display: flex; align-items: center; gap: 8px;}
            
            .inv-btn-back {
                background: #3b82f6; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; cursor: pointer; display: none;
            }

            .inv-btn-clear {
                background: #334155; color: #cbd5e1; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; cursor: pointer; transition: 0.2s;
            }
            .inv-btn-clear:hover { background: #ef4444; color: white; }

            /* Grid de Magic Squares */
            #laplata-inventory-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                overflow-y: auto;
                padding-right: 5px;
                min-height: 100px;
            }
            
            /* Scrollbar */
            #laplata-inventory-grid::-webkit-scrollbar { width: 5px; }
            #laplata-inventory-grid::-webkit-scrollbar-thumb { background: #475569; border-radius: 5px; }

            /* O Quadradinho Mágico */
            .magic-square {
                aspect-ratio: 1;
                background: #1e293b;
                border-radius: 8px;
                border: 1px solid #475569;
                position: relative;
                cursor: pointer;
                transition: all 0.2s;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .magic-square:hover {
                border-color: #f59e0b;
                transform: translateY(-2px);
                box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2);
            }
            
            /* Hover lateral expansivo (Dica visual ao passar mouse) */
            .magic-square .tooltip {
                position: absolute;
                bottom: -100%;
                left: 0; width: 100%;
                background: rgba(0,0,0,0.8);
                color: white; font-size: 0.6rem;
                padding: 4px; text-align: center;
                transition: 0.2s;
            }
            .magic-square:hover .tooltip { bottom: 0; }

            .magic-square img {
                width: 100%; height: 100%; object-fit: cover;
            }

            .magic-square .pack-badge {
                position: absolute;
                top: 5px; right: 5px;
                background: rgba(59, 130, 246, 0.9);
                color: white; font-size: 0.65rem; font-weight: bold;
                padding: 2px 5px; border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            }
            
            .magic-square .pack-icon {
                font-size: 2rem; opacity: 0.5;
            }

            .inv-empty-msg { font-size: 0.8rem; color: #64748b; text-align: center; padding: 20px 0; grid-column: span 3; }
        ;
        document.head.appendChild(style);

        const widget = document.createElement('div');
        widget.id = 'laplata-inventory-widget';
        
        const panel = document.createElement('div');
        panel.id = 'laplata-inventory-panel';
        panel.innerHTML = 
            <div id="laplata-inventory-header">
                <h4><button class="inv-btn-back" id="inv-back-btn">⬅</button> 🎒 <span id="inv-title">Transferência</span></h4>
                <button class="inv-btn-clear" id="laplata-inventory-clear">Limpar</button>
            </div>
            <div id="laplata-inventory-grid"></div>
            <div style="font-size:0.65rem; color:#475569; text-align:center; margin-top:10px;">Dica: Duplo-clique para abrir Packs.</div>
        ;

        const btn = document.createElement('div');
        btn.id = 'laplata-inventory-btn';
        btn.innerHTML = 📋<div class="badge" id="laplata-inventory-badge">0</div>;
        btn.onclick = () => {
            const isVisible = panel.style.display === 'flex';
            panel.style.display = isVisible ? 'none' : 'flex';
            if (!isVisible) this.updateUI();
        };

        widget.appendChild(panel);
        widget.appendChild(btn);
        document.body.appendChild(widget);

        panel.querySelector('#laplata-inventory-clear').onclick = () => this.clear();
        panel.querySelector('#inv-back-btn').onclick = () => {
            this.state.currentFolder = null;
            this.updateUI();
        };

        this.updateUI();
    },

    updateUI: function() {
        const grid = document.getElementById('laplata-inventory-grid');
        const badge = document.getElementById('laplata-inventory-badge');
        const titleSpan = document.getElementById('inv-title');
        const backBtn = document.getElementById('inv-back-btn');
        
        if (!grid) return;

        let items = this.getItems();
        
        // Se estivermos dentro de uma pasta (Pack)
        if (this.state.currentFolder) {
            const pack = items.find(i => i.id === this.state.currentFolder && i.type === 'pack');
            if (pack) {
                items = pack.items;
                titleSpan.innerText = pack.title || "Pack";
                backBtn.style.display = 'inline-block';
            } else {
                this.state.currentFolder = null; // Falha de segurança
            }
        } 
        
        if (!this.state.currentFolder) {
            titleSpan.innerText = "Transferência";
            backBtn.style.display = 'none';
        }

        badge.innerText = this.getItems().length;
        badge.style.display = this.getItems().length > 0 ? 'flex' : 'none';

        grid.innerHTML = '';

        if (items.length === 0) {
            grid.innerHTML = '<div class="inv-empty-msg">Vazio. Colete ou gere arquivos.</div>';
            return;
        }

        items.forEach(item => {
            const square = document.createElement('div');
            square.className = 'magic-square';
            square.title = "Item"; // nativo

            if (item.type === 'image') {
                square.innerHTML = <img src="\"> <div class="tooltip">IMG</div>;
                // Clique simples na imagem = copiar para clipboard (Ação retrocompativel)
                square.onclick = () => {
                    // Para futuro: arrastar e soltar (Drag and Drop nativo)
                    // Por enquanto só toca som
                    if(window.apolloSFX) window.apolloSFX.play('click');
                };
            } 
            else if (item.type === 'pack') {
                let inner = '';
                if (item.thumbnail) {
                    inner = <img src="\" style="opacity: 0.6;">;
                } else {
                    inner = <div class="pack-icon">📁</div>;
                }
                
                square.innerHTML = 
                    \
                    <div class="pack-badge">\</div>
                    <div class="tooltip">\</div>
                ;
                
                // Duplo-Clique = Abre a pasta
                square.ondblclick = () => {
                    if(window.apolloSFX) window.apolloSFX.play('success');
                    this.state.currentFolder = item.id;
                    this.updateUI();
                };
            }

            grid.appendChild(square);
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.laplataInventory.initUI();
});
'''

with open('laplata_inventory.js', 'w', encoding='utf-8') as f:
    f.write(new_code)
