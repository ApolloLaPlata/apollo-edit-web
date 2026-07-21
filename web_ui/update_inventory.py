import os

new_js = '''/**
 * Apollo La Plata - Ponte de Inventário V2 (Packs e Magic Squares)
 * Permite copiar mídias isoladas ou agrupar várias mídias em "Packs" dinâmicos.
 * V3: Suporte a comandos OS (Copiar, Colar, Recortar, Deletar, Ctrl+Z, Novo Texto)
 */

window.laplataInventory = {
    KEY: 'laplata_inventory_clip_v2',
    
    state: {
        currentFolder: null,
        selectedId: null,
        clipboardItem: null,
        history: [] // Para o Ctrl+Z
    },

    getItems: function() {
        try {
            const data = localStorage.getItem(this.KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            return [];
        }
    },

    saveItems: function(items, skipHistory = false) {
        if (!skipHistory) {
            const current = localStorage.getItem(this.KEY);
            if (current) {
                this.state.history.push(current);
                if (this.state.history.length > 20) this.state.history.shift();
            }
        }
        localStorage.setItem(this.KEY, JSON.stringify(items));
        this.updateUI();
    },

    undo: function() {
        if (this.state.history.length > 0) {
            const previousState = this.state.history.pop();
            localStorage.setItem(this.KEY, previousState);
            this.state.selectedId = null;
            this.updateUI();
            if (window.showToast) window.showToast('Ação desfeita (Ctrl+Z)', 'info');
        } else {
            if (window.showToast) window.showToast('Nada para desfazer', 'error');
        }
    },

    copyAction: function() {
        if (this.state.selectedId) {
            const items = this.getItems();
            const item = items.find(i => i.id === this.state.selectedId);
            if (item) {
                this.state.clipboardItem = { action: 'copy', item: JSON.parse(JSON.stringify(item)) };
                if (window.showToast) window.showToast('Copiado para a prancheta do Apollo', 'info');
            }
        }
    },

    cutAction: function() {
        if (this.state.selectedId) {
            const items = this.getItems();
            const item = items.find(i => i.id === this.state.selectedId);
            if (item) {
                this.state.clipboardItem = { action: 'cut', item: JSON.parse(JSON.stringify(item)) };
                if (window.showToast) window.showToast('Recortado', 'info');
            }
        }
    },

    pasteAction: function() {
        if (this.state.clipboardItem) {
            let items = this.getItems();
            const newItem = JSON.parse(JSON.stringify(this.state.clipboardItem.item));
            newItem.id = 'item_' + Date.now() + '_' + Math.floor(Math.random()*1000);
            newItem.timestamp = Date.now();
            
            items.unshift(newItem);
            
            if (this.state.clipboardItem.action === 'cut') {
                items = items.filter(i => i.id !== this.state.clipboardItem.item.id);
                this.state.clipboardItem = null;
            }
            
            this.saveItems(items);
            if (window.showToast) window.showToast('Colado', 'success');
        }
    },

    deleteAction: function() {
        if (this.state.selectedId) {
            this.removeItem(this.state.selectedId);
            this.state.selectedId = null;
            if (window.showToast) window.showToast('Item apagado', 'info');
        }
    },

    newTextAction: function() {
        const text = prompt("Digite o texto ou prompt para salvar:");
        if (text && text.trim() !== '') {
            this.copy(text, 'text');
        }
    },

    copy: function(payload, type = 'image', metadata = {}) {
        const items = this.getItems();
        let newItem = {
            id: 'item_' + Date.now() + '_' + Math.floor(Math.random()*1000),
            type: type,
            data: payload,
            metadata: metadata,
            timestamp: Date.now()
        };
        items.unshift(newItem); 
        this.saveItems(items);
        if (window.apolloNotifications) window.apolloNotifications.add("Copiado!", "Item salvo 🎒", "system");
        if (window.apolloSFX) window.apolloSFX.play('click');
    },

    addPack: function(title, itemsArray, metadata = {}) {
        const items = this.getItems();
        let thumb = '';
        if (itemsArray.length > 0 && itemsArray[0].type === 'image') thumb = itemsArray[0].data;
        const newPack = {
            id: 'pack_' + Date.now(), type: 'pack', title: title, thumbnail: thumb, count: itemsArray.length,
            items: itemsArray, metadata: metadata, timestamp: Date.now()
        };
        items.unshift(newPack);
        this.saveItems(items);
        if (window.apolloSFX) window.apolloSFX.play('success');
    },

    clear: function() {
        this.saveItems([]); // Uses saveItems to allow undo
        this.state.currentFolder = null;
        if (window.apolloSFX) window.apolloSFX.play('click');
    },

    removeItem: function(id) {
        let items = this.getItems();
        items = items.filter(i => i.id !== id);
        this.saveItems(items);
    },

    initUI: function() {
        if (document.getElementById('laplata-inventory-widget')) return;

        const style = document.createElement('style');
        style.innerHTML = 
            #laplata-inventory-widget { position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; align-items: flex-end; gap: 10px; font-family: 'Inter', sans-serif; }
            #laplata-inventory-btn { width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #f59e0b, #d97706); border: 2px solid #fff; box-shadow: 0 5px 15px rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; cursor: pointer; transition: all 0.2s; position: relative; }
            #laplata-inventory-btn:hover { transform: scale(1.1); }
            #laplata-inventory-badge { position: absolute; top: -5px; right: -5px; background: #ef4444; color: white; font-size: 0.6rem; font-weight: bold; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid #0f172a; display: none; }
            #laplata-inventory-panel { background: rgba(15, 23, 42, 0.95); border: 1px solid #334155; border-radius: 12px; padding: 15px; width: 340px; max-height: 450px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); backdrop-filter: blur(10px); display: none; flex-direction: column; transform-origin: bottom right; animation: inventoryPop 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
            #laplata-inventory-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 10px; }
            #laplata-inventory-header h4 { margin: 0; color: white; font-size: 0.9rem; display: flex; align-items: center; gap: 8px;}
            .inv-toolbar { display: flex; gap: 5px; margin-bottom: 10px; background: rgba(0,0,0,0.3); padding: 5px; border-radius: 6px; }
            .inv-toolbar-btn { background: #334155; color: #cbd5e1; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: 0.2s; flex: 1; display:flex; justify-content:center; align-items:center; }
            .inv-toolbar-btn:hover { background: #3b82f6; color: white; }
            #laplata-inventory-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; overflow-y: auto; padding-right: 5px; min-height: 100px; }
            #laplata-inventory-grid::-webkit-scrollbar { width: 5px; }
            #laplata-inventory-grid::-webkit-scrollbar-thumb { background: #475569; border-radius: 5px; }
            .magic-square { aspect-ratio: 1; background: #1e293b; border-radius: 8px; border: 1px solid #475569; position: relative; cursor: pointer; transition: all 0.2s; overflow: hidden; display: flex; align-items: center; justify-content: center; }
            .magic-square:hover { border-color: #f59e0b; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(245, 158, 11, 0.2); }
            .magic-square.selected { border-color: #3b82f6; border-width: 3px; box-shadow: 0 0 15px rgba(59, 130, 246, 0.5); transform: scale(0.95); }
            .magic-square .tooltip { position: absolute; bottom: -100%; left: 0; width: 100%; background: rgba(0,0,0,0.8); color: white; font-size: 0.6rem; padding: 4px; text-align: center; transition: 0.2s; }
            .magic-square:hover .tooltip { bottom: 0; }
            .magic-square img { width: 100%; height: 100%; object-fit: cover; }
            .magic-square .pack-badge { position: absolute; top: 5px; right: 5px; background: rgba(59, 130, 246, 0.9); color: white; font-size: 0.65rem; font-weight: bold; padding: 2px 5px; border-radius: 10px; }
            .magic-square .pack-icon { font-size: 2rem; opacity: 0.5; }
            .inv-empty-msg { font-size: 0.8rem; color: #64748b; text-align: center; padding: 20px 0; grid-column: span 3; }
        ;
        document.head.appendChild(style);

        const widget = document.createElement('div');
        widget.id = 'laplata-inventory-widget';
        
        const panel = document.createElement('div');
        panel.id = 'laplata-inventory-panel';
        panel.innerHTML = 
            <div id="laplata-inventory-header">
                <h4><button class="inv-toolbar-btn" style="flex:0; margin-right:5px; display:none;" id="inv-back-btn">⬅</button> 🎒 <span id="inv-title">Transferência</span></h4>
                <button class="inv-toolbar-btn" style="flex:0; background:#ef4444;" id="laplata-inventory-clear">Limpar</button>
            </div>
            <div class="inv-toolbar">
                <button class="inv-toolbar-btn" id="inv-btn-new" title="Novo Texto"><i class="fas fa-plus"></i></button>
                <button class="inv-toolbar-btn" id="inv-btn-cut" title="Recortar (Ctrl+X)"><i class="fas fa-cut"></i></button>
                <button class="inv-toolbar-btn" id="inv-btn-copy" title="Copiar (Ctrl+C)"><i class="fas fa-copy"></i></button>
                <button class="inv-toolbar-btn" id="inv-btn-paste" title="Colar (Ctrl+V)"><i class="fas fa-paste"></i></button>
                <button class="inv-toolbar-btn" id="inv-btn-del" title="Deletar (Del)"><i class="fas fa-trash"></i></button>
                <button class="inv-toolbar-btn" id="inv-btn-undo" title="Desfazer (Ctrl+Z)"><i class="fas fa-undo"></i></button>
            </div>
            <div id="laplata-inventory-grid"></div>
            <div style="font-size:0.65rem; color:#475569; text-align:center; margin-top:10px;">Atalhos OS ativados. Clique duplo para abrir Packs.</div>
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

        // Bind toolbar events
        panel.querySelector('#laplata-inventory-clear').onclick = () => { if(confirm('Limpar tudo?')) this.clear(); };
        panel.querySelector('#inv-back-btn').onclick = () => { this.state.currentFolder = null; this.updateUI(); };
        panel.querySelector('#inv-btn-new').onclick = () => this.newTextAction();
        panel.querySelector('#inv-btn-cut').onclick = () => this.cutAction();
        panel.querySelector('#inv-btn-copy').onclick = () => this.copyAction();
        panel.querySelector('#inv-btn-paste').onclick = () => this.pasteAction();
        panel.querySelector('#inv-btn-del').onclick = () => this.deleteAction();
        panel.querySelector('#inv-btn-undo').onclick = () => this.undo();

        // Bind Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (panel.style.display === 'flex') {
                if (e.ctrlKey && e.key.toLowerCase() === 'z') { e.preventDefault(); this.undo(); }
                if (e.ctrlKey && e.key.toLowerCase() === 'c') { e.preventDefault(); this.copyAction(); }
                if (e.ctrlKey && e.key.toLowerCase() === 'x') { e.preventDefault(); this.cutAction(); }
                if (e.ctrlKey && e.key.toLowerCase() === 'v') { e.preventDefault(); this.pasteAction(); }
                if (e.key === 'Delete') { e.preventDefault(); this.deleteAction(); }
            }
        });

        this.updateUI();
    },

    updateUI: function() {
        const grid = document.getElementById('laplata-inventory-grid');
        const badge = document.getElementById('laplata-inventory-badge');
        const titleSpan = document.getElementById('inv-title');
        const backBtn = document.getElementById('inv-back-btn');
        
        if (!grid) return;

        let items = this.getItems();
        
        if (this.state.currentFolder) {
            const pack = items.find(i => i.id === this.state.currentFolder && i.type === 'pack');
            if (pack) {
                items = pack.items;
                titleSpan.innerText = pack.title || "Pack";
                backBtn.style.display = 'flex';
            } else {
                this.state.currentFolder = null; 
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
            if (this.state.selectedId === item.id) square.classList.add('selected');
            
            square.title = item.type; 

            if (item.type === 'image') {
                square.innerHTML = <img src="\"><div class="tooltip">IMG</div>;
            } else if (item.type === 'text' || item.type === 'mapping') {
                square.innerHTML = <div class="pack-icon">📄</div><div class="tooltip">\</div>;
            } else if (item.type === 'pack') {
                let inner = item.thumbnail ? <img src="\" style="opacity: 0.6;"> : <div class="pack-icon">📁</div>;
                square.innerHTML = \<div class="pack-badge">\</div><div class="tooltip">\</div>;
                square.ondblclick = () => {
                    if(window.apolloSFX) window.apolloSFX.play('success');
                    this.state.currentFolder = item.id;
                    this.state.selectedId = null;
                    this.updateUI();
                };
            } else {
                square.innerHTML = <div class="pack-icon">📦</div><div class="tooltip">\</div>;
            }

            // Click selects item
            square.onclick = (e) => {
                this.state.selectedId = item.id;
                this.updateUI();
                if(window.apolloSFX) window.apolloSFX.play('click');
            };

            grid.appendChild(square);
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.laplataInventory.initUI();
});
'''

try:
    with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\laplata_inventory.js', 'w', encoding='utf-8') as f:
        f.write(new_js)
    print("Sucesso!")
except Exception as e:
    print(f"Erro: {e}")
