// Apollo Image Studio Pro - independent browser image editor engine.

(function () {
    const els = {
        mainCanvas: document.getElementById('mainCanvas'),
        overlayCanvas: document.getElementById('overlayCanvas'),
        canvasFrame: document.getElementById('canvasFrame'),
        stageViewport: document.getElementById('stageViewport'),
        layersList: document.getElementById('layersList'),
        toast: document.getElementById('toast'),
        docMeta: document.getElementById('docMeta'),
        imageInput: document.getElementById('imageInput'),
        layerImageInput: document.getElementById('layerImageInput'),
        projectInput: document.getElementById('projectInput'),
        layerNameInput: document.getElementById('layerNameInput'),
        opacityRange: document.getElementById('opacityRange'),
        blendModeSelect: document.getElementById('blendModeSelect'),
        layerXInput: document.getElementById('layerXInput'),
        layerYInput: document.getElementById('layerYInput'),
        docWidthInput: document.getElementById('docWidthInput'),
        docHeightInput: document.getElementById('docHeightInput'),
        zoomRange: document.getElementById('zoomRange'),
        zoomLabel: document.getElementById('zoomLabel'),
        brushSize: document.getElementById('brushSize'),
        brushSizeLabel: document.getElementById('brushSizeLabel'),
        colorInput: document.getElementById('colorInput'),
        applyCropBtn: document.getElementById('applyCropBtn'),
        clearSelectionBtn: document.getElementById('clearSelectionBtn')
    };

    const ctx = els.mainCanvas.getContext('2d');
    const overlayCtx = els.overlayCanvas.getContext('2d');

    const state = {
        width: 1280,
        height: 720,
        zoom: 0.8,
        tool: 'move',
        layers: [],
        activeId: null,
        pointer: null,
        selection: null,
        history: [],
        future: [],
        nextId: 1,
        isRestoring: false
    };

    let toastTimer = null;

    function showToast(message, kind = 'ok') {
        clearTimeout(toastTimer);
        els.toast.textContent = message;
        els.toast.className = `toast visible ${kind}`;
        toastTimer = setTimeout(() => {
            els.toast.className = 'toast';
        }, kind === 'error' ? 4200 : 2400);
    }

    window.showToast = showToast;

    function makeCanvas(width, height) {
        const canvas = document.createElement('canvas');
        canvas.width = Math.max(1, Math.round(width));
        canvas.height = Math.max(1, Math.round(height));
        return canvas;
    }

    function cloneCanvas(source) {
        const canvas = makeCanvas(source.width, source.height);
        canvas.getContext('2d').drawImage(source, 0, 0);
        return canvas;
    }

    function uid() {
        return `layer_${state.nextId++}`;
    }

    function activeLayer() {
        return state.layers.find((layer) => layer.id === state.activeId) || null;
    }

    function rasterLayer(name, canvas, x = 0, y = 0) {
        return {
            id: uid(),
            type: 'raster',
            name,
            canvas,
            x,
            y,
            width: canvas.width,
            height: canvas.height,
            opacity: 1,
            blendMode: 'source-over',
            visible: true
        };
    }

    function textLayer(text, x, y) {
        return {
            id: uid(),
            type: 'text',
            name: `Text: ${text.slice(0, 18)}`,
            text,
            x,
            y,
            fontSize: 58,
            fontFamily: 'Impact, Arial Black, Arial',
            color: els.colorInput.value,
            stroke: '#000000',
            opacity: 1,
            blendMode: 'source-over',
            visible: true
        };
    }

    function resizeCanvases() {
        els.mainCanvas.width = state.width;
        els.mainCanvas.height = state.height;
        els.overlayCanvas.width = state.width;
        els.overlayCanvas.height = state.height;
        els.canvasFrame.style.width = `${state.width}px`;
        els.canvasFrame.style.height = `${state.height}px`;
        els.docMeta.textContent = `${state.width} x ${state.height}`;
        els.docWidthInput.value = state.width;
        els.docHeightInput.value = state.height;
    }

    function applyZoom() {
        els.canvasFrame.style.transform = `scale(${state.zoom})`;
        els.zoomRange.value = Math.round(state.zoom * 100);
        els.zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
    }

    function drawTextLayer(layer, targetCtx) {
        targetCtx.save();
        targetCtx.globalAlpha = layer.opacity;
        targetCtx.globalCompositeOperation = layer.blendMode;
        targetCtx.font = `${layer.fontSize}px ${layer.fontFamily}`;
        targetCtx.lineJoin = 'round';
        targetCtx.lineWidth = Math.max(2, Math.round(layer.fontSize * 0.08));
        targetCtx.strokeStyle = layer.stroke || '#000000';
        targetCtx.fillStyle = layer.color || '#ffffff';
        targetCtx.strokeText(layer.text, layer.x, layer.y);
        targetCtx.fillText(layer.text, layer.x, layer.y);
        targetCtx.restore();
    }

    function render() {
        ctx.clearRect(0, 0, state.width, state.height);

        for (const layer of state.layers) {
            if (!layer.visible) continue;
            ctx.save();
            ctx.globalAlpha = layer.opacity;
            ctx.globalCompositeOperation = layer.blendMode || 'source-over';

            if (layer.type === 'raster') {
                ctx.drawImage(layer.canvas, layer.x, layer.y, layer.width, layer.height);
            } else if (layer.type === 'text') {
                ctx.restore();
                drawTextLayer(layer, ctx);
                continue;
            }

            ctx.restore();
        }

        renderOverlay();
        renderLayersPanel();
        renderProperties();
        updateSelectionButtons();
    }

    function renderOverlay() {
        overlayCtx.clearRect(0, 0, state.width, state.height);

        const layer = activeLayer();
        if (layer) {
            overlayCtx.save();
            overlayCtx.strokeStyle = 'rgba(216, 180, 254, 0.75)';
            overlayCtx.lineWidth = 1;
            overlayCtx.setLineDash([6, 4]);
            if (layer.type === 'raster') {
                overlayCtx.strokeRect(layer.x, layer.y, layer.width, layer.height);
            } else {
                overlayCtx.font = `${layer.fontSize}px ${layer.fontFamily}`;
                const metrics = overlayCtx.measureText(layer.text);
                overlayCtx.strokeRect(layer.x, layer.y - layer.fontSize, metrics.width, layer.fontSize * 1.22);
            }
            overlayCtx.restore();
        }

        if (state.selection) {
            const rect = normalizedRect(state.selection);
            overlayCtx.save();
            overlayCtx.fillStyle = 'rgba(124, 58, 237, 0.12)';
            overlayCtx.strokeStyle = '#f0abfc';
            overlayCtx.lineWidth = 2;
            overlayCtx.setLineDash([9, 5]);
            overlayCtx.fillRect(rect.x, rect.y, rect.w, rect.h);
            overlayCtx.strokeRect(rect.x, rect.y, rect.w, rect.h);
            overlayCtx.restore();
        }
    }

    function renderLayersPanel() {
        els.layersList.innerHTML = '';

        [...state.layers].reverse().forEach((layer) => {
            const row = document.createElement('div');
            row.className = `layer-row${layer.id === state.activeId ? ' active' : ''}`;
            row.dataset.layerId = layer.id;

            const visible = document.createElement('button');
            visible.type = 'button';
            visible.className = 'layer-vis';
            visible.textContent = layer.visible ? 'On' : 'Off';
            visible.title = 'Alternar visibilidade';
            visible.addEventListener('click', (event) => {
                event.stopPropagation();
                layer.visible = !layer.visible;
                commit('Visibilidade');
                render();
            });

            const name = document.createElement('div');
            name.className = 'layer-name';
            name.textContent = layer.name;

            const type = document.createElement('div');
            type.className = 'layer-type';
            type.textContent = layer.type;

            row.append(visible, name, type);
            row.addEventListener('click', () => {
                state.activeId = layer.id;
                render();
            });
            els.layersList.appendChild(row);
        });
    }

    function renderProperties() {
        const layer = activeLayer();
        const disabled = !layer;

        for (const input of [els.layerNameInput, els.opacityRange, els.blendModeSelect, els.layerXInput, els.layerYInput]) {
            input.disabled = disabled;
        }

        if (!layer) {
            els.layerNameInput.value = '';
            els.opacityRange.value = 100;
            els.blendModeSelect.value = 'source-over';
            els.layerXInput.value = 0;
            els.layerYInput.value = 0;
            return;
        }

        els.layerNameInput.value = layer.name;
        els.opacityRange.value = Math.round(layer.opacity * 100);
        els.blendModeSelect.value = layer.blendMode || 'source-over';
        els.layerXInput.value = Math.round(layer.x);
        els.layerYInput.value = Math.round(layer.y);
    }

    function updateSelectionButtons() {
        const hasSelection = !!state.selection;
        els.applyCropBtn.disabled = !hasSelection;
        els.clearSelectionBtn.disabled = !hasSelection;
    }

    function normalizedRect(rect) {
        const x = Math.min(rect.x, rect.x + rect.w);
        const y = Math.min(rect.y, rect.y + rect.h);
        const w = Math.abs(rect.w);
        const h = Math.abs(rect.h);
        return { x, y, w, h };
    }

    function pointerToDoc(event) {
        const rect = els.overlayCanvas.getBoundingClientRect();
        return {
            x: clamp((event.clientX - rect.left) * (state.width / rect.width), 0, state.width),
            y: clamp((event.clientY - rect.top) * (state.height / rect.height), 0, state.height)
        };
    }

    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function createInitialDocument() {
        state.width = 1280;
        state.height = 720;
        resizeCanvases();

        const canvas = makeCanvas(state.width, state.height);
        const baseCtx = canvas.getContext('2d');
        baseCtx.fillStyle = '#ffffff';
        baseCtx.fillRect(0, 0, canvas.width, canvas.height);

        const layer = rasterLayer('Background', canvas);
        state.layers = [layer];
        state.activeId = layer.id;
        state.selection = null;
        state.history = [];
        state.future = [];
        commit('Novo documento');
        render();
    }

    function fitZoom() {
        const viewportRect = els.stageViewport.getBoundingClientRect();
        const scaleX = Math.max(0.05, (viewportRect.width - 96) / state.width);
        const scaleY = Math.max(0.05, (viewportRect.height - 96) / state.height);
        state.zoom = clamp(Math.min(scaleX, scaleY), 0.2, 2.2);
        applyZoom();
    }

    function setTool(tool) {
        state.tool = tool;
        document.querySelectorAll('.tool-btn[data-tool]').forEach((button) => {
            button.classList.toggle('active', button.dataset.tool === tool);
        });
    }

    function currentSnapshot() {
        return {
            width: state.width,
            height: state.height,
            activeId: state.activeId,
            nextId: state.nextId,
            layers: state.layers.map((layer) => {
                const common = {
                    id: layer.id,
                    type: layer.type,
                    name: layer.name,
                    x: layer.x,
                    y: layer.y,
                    opacity: layer.opacity,
                    blendMode: layer.blendMode,
                    visible: layer.visible
                };

                if (layer.type === 'raster') {
                    return {
                        ...common,
                        width: layer.width,
                        height: layer.height,
                        dataUrl: layer.canvas.toDataURL('image/png')
                    };
                }

                return {
                    ...common,
                    text: layer.text,
                    fontSize: layer.fontSize,
                    fontFamily: layer.fontFamily,
                    color: layer.color,
                    stroke: layer.stroke
                };
            })
        };
    }

    async function restoreSnapshot(snapshot) {
        state.isRestoring = true;
        state.width = snapshot.width;
        state.height = snapshot.height;
        state.activeId = snapshot.activeId;
        state.nextId = snapshot.nextId || state.nextId;
        state.selection = null;
        resizeCanvases();

        const restoredLayers = await Promise.all(snapshot.layers.map(async (layer) => {
            if (layer.type !== 'raster') return { ...layer };

            const image = await loadImage(layer.dataUrl);
            const canvas = makeCanvas(layer.width || image.width, layer.height || image.height);
            canvas.getContext('2d').drawImage(image, 0, 0, canvas.width, canvas.height);
            return {
                ...layer,
                canvas
            };
        }));

        state.layers = restoredLayers;
        state.isRestoring = false;
        render();
    }

    function commit() {
        if (state.isRestoring) return;
        state.history.push(currentSnapshot());
        if (state.history.length > 36) state.history.shift();
        state.future = [];
    }

    async function undo() {
        if (state.history.length <= 1) {
            showToast('Nada para desfazer.', 'error');
            return;
        }
        const current = state.history.pop();
        state.future.push(current);
        await restoreSnapshot(state.history[state.history.length - 1]);
        showToast('Desfeito.');
    }

    async function redo() {
        if (!state.future.length) {
            showToast('Nada para refazer.', 'error');
            return;
        }
        const snapshot = state.future.pop();
        state.history.push(snapshot);
        await restoreSnapshot(snapshot);
        showToast('Refeito.');
    }

    function loadImage(src) {
        return new Promise((resolve, reject) => {
            const image = new Image();
            image.onload = () => resolve(image);
            image.onerror = () => reject(new Error('Imagem nao carregou.'));
            image.src = src;
        });
    }

    function fileToDataUrl(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Arquivo nao carregou.'));
            reader.readAsDataURL(file);
        });
    }

    function scaleImageSize(width, height, maxSide = 4096) {
        const max = Math.max(width, height);
        if (max <= maxSide) return { width, height, scale: 1 };
        const scale = maxSide / max;
        return {
            width: Math.round(width * scale),
            height: Math.round(height * scale),
            scale
        };
    }

    async function openImageFile(file) {
        if (!file) return;
        const dataUrl = await fileToDataUrl(file);
        const image = await loadImage(dataUrl);
        const size = scaleImageSize(image.naturalWidth || image.width, image.naturalHeight || image.height);
        const canvas = makeCanvas(size.width, size.height);
        canvas.getContext('2d').drawImage(image, 0, 0, size.width, size.height);

        state.width = size.width;
        state.height = size.height;
        resizeCanvases();

        const layer = rasterLayer(file.name.replace(/\.[^.]+$/, '') || 'Imagem', canvas);
        state.layers = [layer];
        state.activeId = layer.id;
        state.selection = null;
        state.history = [];
        state.future = [];
        commit('Abrir imagem');
        fitZoom();
        render();
        showToast('Imagem aberta.');
    }

    async function importLayerFile(file) {
        if (!file) return;
        const dataUrl = await fileToDataUrl(file);
        const image = await loadImage(dataUrl);
        const size = scaleImageSize(image.naturalWidth || image.width, image.naturalHeight || image.height);
        const canvas = makeCanvas(size.width, size.height);
        canvas.getContext('2d').drawImage(image, 0, 0, size.width, size.height);

        const layer = rasterLayer(file.name.replace(/\.[^.]+$/, '') || 'Camada importada', canvas, 0, 0);
        state.layers.push(layer);
        state.activeId = layer.id;
        commit('Importar camada');
        render();
        showToast('Camada importada.');
    }

    function composeDocumentCanvas() {
        const canvas = makeCanvas(state.width, state.height);
        const out = canvas.getContext('2d');
        out.clearRect(0, 0, canvas.width, canvas.height);
        for (const layer of state.layers) {
            if (!layer.visible) continue;
            out.save();
            out.globalAlpha = layer.opacity;
            out.globalCompositeOperation = layer.blendMode || 'source-over';
            if (layer.type === 'raster') {
                out.drawImage(layer.canvas, layer.x, layer.y, layer.width, layer.height);
            } else {
                out.restore();
                drawTextLayer(layer, out);
                continue;
            }
            out.restore();
        }
        return canvas;
    }

    function exportPng() {
        const canvas = composeDocumentCanvas();
        canvas.toBlob((blob) => {
            if (!blob) {
                showToast('Falha ao exportar PNG.', 'error');
                return;
            }
            const fileName = `apollo_image_${Date.now()}.png`;
            const file = new File([blob], fileName, { type: 'image/png' });

            if (window.apolloTransferOS && typeof window.apolloTransferOS.toggleFolder === 'function') {
                window.apolloTransferOS.toggleFolder('bagageiro');
            }

            if (typeof window.processDroppedFiles === 'function') {
                window.processDroppedFiles([file]);
                showToast('PNG enviado para o Bagageiro.');
                return;
            }

            const url = URL.createObjectURL(blob);
            const anchor = document.createElement('a');
            anchor.href = url;
            anchor.download = fileName;
            anchor.click();
            URL.revokeObjectURL(url);
            showToast('PNG baixado.');
        }, 'image/png');
    }

    async function saveProject() {
        const title = prompt('Nome do projeto:', 'Apollo Image Studio');
        if (!title) return;
        const snapshot = currentSnapshot();
        const project = {
            id: `apollo_image_project_${Date.now()}`,
            type: 'imagem_json',
            engine: 'apollo-image-studio-pro',
            title,
            content: JSON.stringify(snapshot),
            timestamp: Date.now(),
            updatedAt: new Date().toISOString()
        };

        try {
            if (window.laplataDB && window.laplataDB.projects) {
                await window.laplataDB.projects.save(project);
            } else {
                const stored = JSON.parse(localStorage.getItem('apollo_image_projects') || '[]');
                stored.push(project);
                localStorage.setItem('apollo_image_projects', JSON.stringify(stored));
            }

            const blob = new Blob([project.content], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const anchor = document.createElement('a');
            anchor.href = url;
            anchor.download = `${title.replace(/[^\w-]+/g, '_')}.apollo-image.json`;
            anchor.click();
            URL.revokeObjectURL(url);
            showToast('Projeto salvo.');
        } catch (error) {
            showToast(error.message, 'error');
        }
    }

    async function loadProjectFile(file) {
        if (!file) return;
        const text = await file.text();
        let payload = JSON.parse(text);
        if (payload.content && typeof payload.content === 'string') {
            payload = JSON.parse(payload.content);
        }
        await restoreSnapshot(payload);
        state.history = [];
        state.future = [];
        commit('Carregar projeto');
        fitZoom();
        render();
        showToast('Projeto carregado.');
    }

    function addEmptyLayer() {
        const canvas = makeCanvas(state.width, state.height);
        const layer = rasterLayer(`Camada ${state.layers.length + 1}`, canvas);
        state.layers.push(layer);
        state.activeId = layer.id;
        commit('Nova camada');
        render();
    }

    function duplicateActiveLayer() {
        const layer = activeLayer();
        if (!layer) return;

        let copy;
        if (layer.type === 'raster') {
            copy = rasterLayer(`${layer.name} copia`, cloneCanvas(layer.canvas), layer.x + 16, layer.y + 16);
            copy.width = layer.width;
            copy.height = layer.height;
        } else {
            copy = {
                ...layer,
                id: uid(),
                name: `${layer.name} copia`,
                x: layer.x + 16,
                y: layer.y + 16
            };
        }
        copy.opacity = layer.opacity;
        copy.blendMode = layer.blendMode;
        copy.visible = layer.visible;
        state.layers.push(copy);
        state.activeId = copy.id;
        commit('Duplicar camada');
        render();
    }

    function deleteActiveLayer() {
        if (state.layers.length <= 1) {
            showToast('O documento precisa manter ao menos uma camada.', 'error');
            return;
        }
        const index = state.layers.findIndex((layer) => layer.id === state.activeId);
        if (index < 0) return;
        state.layers.splice(index, 1);
        state.activeId = state.layers[Math.max(0, index - 1)].id;
        commit('Excluir camada');
        render();
    }

    function ensureRasterLayer() {
        let layer = activeLayer();
        if (!layer) {
            addEmptyLayer();
            layer = activeLayer();
        }

        if (layer.type === 'raster') return layer;

        const canvas = makeCanvas(state.width, state.height);
        drawTextLayer(layer, canvas.getContext('2d'));
        const raster = rasterLayer(layer.name, canvas);
        raster.id = layer.id;
        raster.opacity = layer.opacity;
        raster.blendMode = layer.blendMode;
        raster.visible = layer.visible;
        const index = state.layers.findIndex((item) => item.id === layer.id);
        state.layers[index] = raster;
        return raster;
    }

    function addTextAt(x, y) {
        const text = prompt('Texto:', 'Apollo');
        if (!text) return;
        const layer = textLayer(text, x, y);
        state.layers.push(layer);
        state.activeId = layer.id;
        commit('Texto');
        render();
    }

    function startPointer(event) {
        const point = pointerToDoc(event);
        const layer = activeLayer();
        state.pointer = {
            startX: point.x,
            startY: point.y,
            lastX: point.x,
            lastY: point.y,
            layerX: layer ? layer.x : 0,
            layerY: layer ? layer.y : 0,
            drawing: true
        };

        if (state.tool === 'text') {
            addTextAt(point.x, point.y);
            state.pointer = null;
            return;
        }

        if (state.tool === 'crop' || state.tool === 'select') {
            state.selection = { x: point.x, y: point.y, w: 0, h: 0 };
            render();
            return;
        }

        if (state.tool === 'brush' || state.tool === 'eraser') {
            const raster = ensureRasterLayer();
            const layerCtx = raster.canvas.getContext('2d');
            layerCtx.save();
            layerCtx.lineCap = 'round';
            layerCtx.lineJoin = 'round';
            layerCtx.lineWidth = Number(els.brushSize.value);
            layerCtx.strokeStyle = els.colorInput.value;
            if (state.tool === 'eraser') layerCtx.globalCompositeOperation = 'destination-out';
            layerCtx.beginPath();
            layerCtx.moveTo(point.x - raster.x, point.y - raster.y);
            state.pointer.layerCtx = layerCtx;
            render();
        }
    }

    function movePointer(event) {
        if (!state.pointer || !state.pointer.drawing) return;
        const point = pointerToDoc(event);
        const dx = point.x - state.pointer.startX;
        const dy = point.y - state.pointer.startY;

        if (state.tool === 'move') {
            const layer = activeLayer();
            if (!layer) return;
            layer.x = state.pointer.layerX + dx;
            layer.y = state.pointer.layerY + dy;
            render();
        } else if (state.tool === 'brush' || state.tool === 'eraser') {
            const raster = activeLayer();
            if (!raster || raster.type !== 'raster') return;
            state.pointer.layerCtx.lineTo(point.x - raster.x, point.y - raster.y);
            state.pointer.layerCtx.stroke();
            render();
        } else if (state.tool === 'crop' || state.tool === 'select') {
            state.selection.w = point.x - state.selection.x;
            state.selection.h = point.y - state.selection.y;
            render();
        }

        state.pointer.lastX = point.x;
        state.pointer.lastY = point.y;
    }

    function endPointer() {
        if (!state.pointer) return;
        if (state.pointer.layerCtx) {
            state.pointer.layerCtx.closePath();
            state.pointer.layerCtx.restore();
        }

        const changed = Math.abs(state.pointer.lastX - state.pointer.startX) > 0.5 ||
            Math.abs(state.pointer.lastY - state.pointer.startY) > 0.5;

        state.pointer = null;

        if (state.selection) {
            const rect = normalizedRect(state.selection);
            if (rect.w < 4 || rect.h < 4) state.selection = null;
            render();
            return;
        }

        if (changed) commit('Editar');
        render();
    }

    function applyCrop() {
        if (!state.selection) return;
        const rect = normalizedRect(state.selection);
        if (rect.w < 8 || rect.h < 8) {
            state.selection = null;
            render();
            return;
        }

        for (const layer of state.layers) {
            layer.x -= rect.x;
            layer.y -= rect.y;
        }
        state.width = Math.round(rect.w);
        state.height = Math.round(rect.h);
        state.selection = null;
        resizeCanvases();
        commit('Crop');
        fitZoom();
        render();
        showToast('Crop aplicado.');
    }

    function resizeDocument() {
        const width = Number(els.docWidthInput.value);
        const height = Number(els.docHeightInput.value);
        if (!width || !height || width < 1 || height < 1) {
            showToast('Dimensoes invalidas.', 'error');
            return;
        }
        state.width = Math.round(width);
        state.height = Math.round(height);
        state.selection = null;
        resizeCanvases();
        commit('Redimensionar documento');
        fitZoom();
        render();
    }

    function applyImageDataFilter(filterName) {
        const layer = ensureRasterLayer();
        if (!layer || layer.type !== 'raster') return;

        const layerCtx = layer.canvas.getContext('2d');
        const imageData = layerCtx.getImageData(0, 0, layer.canvas.width, layer.canvas.height);
        const data = imageData.data;

        if (filterName === 'grayscale') {
            for (let i = 0; i < data.length; i += 4) {
                const gray = Math.round(data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114);
                data[i] = gray;
                data[i + 1] = gray;
                data[i + 2] = gray;
            }
        } else if (filterName === 'sepia') {
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                data[i] = clamp(0.393 * r + 0.769 * g + 0.189 * b, 0, 255);
                data[i + 1] = clamp(0.349 * r + 0.686 * g + 0.168 * b, 0, 255);
                data[i + 2] = clamp(0.272 * r + 0.534 * g + 0.131 * b, 0, 255);
            }
        } else if (filterName === 'invert') {
            for (let i = 0; i < data.length; i += 4) {
                data[i] = 255 - data[i];
                data[i + 1] = 255 - data[i + 1];
                data[i + 2] = 255 - data[i + 2];
            }
        } else if (filterName === 'brightness') {
            for (let i = 0; i < data.length; i += 4) {
                data[i] = clamp(data[i] + 22, 0, 255);
                data[i + 1] = clamp(data[i + 1] + 22, 0, 255);
                data[i + 2] = clamp(data[i + 2] + 22, 0, 255);
            }
        } else if (filterName === 'contrast') {
            const contrast = 28;
            const factor = (259 * (contrast + 255)) / (255 * (259 - contrast));
            for (let i = 0; i < data.length; i += 4) {
                data[i] = clamp(factor * (data[i] - 128) + 128, 0, 255);
                data[i + 1] = clamp(factor * (data[i + 1] - 128) + 128, 0, 255);
                data[i + 2] = clamp(factor * (data[i + 2] - 128) + 128, 0, 255);
            }
        }

        layerCtx.putImageData(imageData, 0, 0);
        commit(`Filtro ${filterName}`);
        render();
        showToast('Ajuste aplicado.');
    }

    function applyCanvasFilter(filterName) {
        const layer = ensureRasterLayer();
        if (!layer || layer.type !== 'raster') return;

        if (filterName === 'rasterize') {
            commit('Rasterizar');
            render();
            showToast('Camada rasterizada.');
            return;
        }

        if (['grayscale', 'sepia', 'invert', 'brightness', 'contrast'].includes(filterName)) {
            applyImageDataFilter(filterName);
            return;
        }

        if (filterName === 'blur') {
            const temp = cloneCanvas(layer.canvas);
            const layerCtx = layer.canvas.getContext('2d');
            layerCtx.clearRect(0, 0, layer.canvas.width, layer.canvas.height);
            layerCtx.filter = 'blur(4px)';
            layerCtx.drawImage(temp, 0, 0);
            layerCtx.filter = 'none';
            commit('Blur');
            render();
            showToast('Blur aplicado.');
            return;
        }

        if (filterName === 'sharpen') {
            convolveActiveLayer([
                0, -1, 0,
                -1, 5, -1,
                0, -1, 0
            ]);
            commit('Sharpen');
            render();
            showToast('Sharpen aplicado.');
        }
    }

    function convolveActiveLayer(kernel) {
        const layer = ensureRasterLayer();
        const layerCtx = layer.canvas.getContext('2d');
        const w = layer.canvas.width;
        const h = layer.canvas.height;
        const src = layerCtx.getImageData(0, 0, w, h);
        const out = layerCtx.createImageData(w, h);
        const side = Math.round(Math.sqrt(kernel.length));
        const half = Math.floor(side / 2);

        for (let y = 0; y < h; y++) {
            for (let x = 0; x < w; x++) {
                const dstOff = (y * w + x) * 4;
                let r = 0;
                let g = 0;
                let b = 0;
                for (let ky = 0; ky < side; ky++) {
                    for (let kx = 0; kx < side; kx++) {
                        const px = clamp(x + kx - half, 0, w - 1);
                        const py = clamp(y + ky - half, 0, h - 1);
                        const srcOff = (py * w + px) * 4;
                        const wt = kernel[ky * side + kx];
                        r += src.data[srcOff] * wt;
                        g += src.data[srcOff + 1] * wt;
                        b += src.data[srcOff + 2] * wt;
                    }
                }
                out.data[dstOff] = clamp(r, 0, 255);
                out.data[dstOff + 1] = clamp(g, 0, 255);
                out.data[dstOff + 2] = clamp(b, 0, 255);
                out.data[dstOff + 3] = src.data[dstOff + 3];
            }
        }
        layerCtx.putImageData(out, 0, 0);
    }

    function bindEvents() {
        document.querySelectorAll('.tool-btn[data-tool]').forEach((button) => {
            button.addEventListener('click', () => setTool(button.dataset.tool));
        });

        document.getElementById('newDocBtn').addEventListener('click', () => {
            createInitialDocument();
            fitZoom();
            showToast('Novo documento.');
        });
        document.getElementById('openImageBtn').addEventListener('click', () => els.imageInput.click());
        document.getElementById('importLayerBtn').addEventListener('click', () => els.layerImageInput.click());
        document.getElementById('saveProjectBtn').addEventListener('click', saveProject);
        document.getElementById('loadProjectBtn').addEventListener('click', () => els.projectInput.click());
        document.getElementById('exportPngBtn').addEventListener('click', exportPng);
        document.getElementById('undoBtn').addEventListener('click', undo);
        document.getElementById('redoBtn').addEventListener('click', redo);
        document.getElementById('addLayerBtn').addEventListener('click', addEmptyLayer);
        document.getElementById('duplicateLayerBtn').addEventListener('click', duplicateActiveLayer);
        document.getElementById('deleteLayerBtn').addEventListener('click', deleteActiveLayer);
        document.getElementById('resizeDocBtn').addEventListener('click', resizeDocument);
        document.getElementById('fitZoomBtn').addEventListener('click', fitZoom);
        els.applyCropBtn.addEventListener('click', applyCrop);
        els.clearSelectionBtn.addEventListener('click', () => {
            state.selection = null;
            render();
        });

        els.imageInput.addEventListener('change', (event) => openImageFile(event.target.files[0]));
        els.layerImageInput.addEventListener('change', (event) => importLayerFile(event.target.files[0]));
        els.projectInput.addEventListener('change', (event) => loadProjectFile(event.target.files[0]));

        els.zoomRange.addEventListener('input', () => {
            state.zoom = Number(els.zoomRange.value) / 100;
            applyZoom();
        });
        els.brushSize.addEventListener('input', () => {
            els.brushSizeLabel.textContent = els.brushSize.value;
        });

        els.layerNameInput.addEventListener('change', () => {
            const layer = activeLayer();
            if (!layer) return;
            layer.name = els.layerNameInput.value || layer.name;
            commit('Renomear camada');
            render();
        });
        els.opacityRange.addEventListener('input', () => {
            const layer = activeLayer();
            if (!layer) return;
            layer.opacity = Number(els.opacityRange.value) / 100;
            render();
        });
        els.opacityRange.addEventListener('change', () => commit('Opacidade'));
        els.blendModeSelect.addEventListener('change', () => {
            const layer = activeLayer();
            if (!layer) return;
            layer.blendMode = els.blendModeSelect.value;
            commit('Mesclagem');
            render();
        });
        els.layerXInput.addEventListener('change', () => updateLayerPosition());
        els.layerYInput.addEventListener('change', () => updateLayerPosition());

        document.querySelectorAll('.adjust-btn').forEach((button) => {
            button.addEventListener('click', () => applyCanvasFilter(button.dataset.filter));
        });

        els.overlayCanvas.addEventListener('pointerdown', (event) => {
            event.preventDefault();
            els.overlayCanvas.setPointerCapture(event.pointerId);
            startPointer(event);
        });
        els.overlayCanvas.addEventListener('pointermove', (event) => {
            event.preventDefault();
            movePointer(event);
        });
        els.overlayCanvas.addEventListener('pointerup', (event) => {
            event.preventDefault();
            endPointer(event);
        });
        els.overlayCanvas.addEventListener('pointercancel', endPointer);

        els.stageViewport.addEventListener('dragover', (event) => event.preventDefault());
        els.stageViewport.addEventListener('drop', (event) => {
            event.preventDefault();
            const file = event.dataTransfer.files[0];
            if (!file || !file.type.startsWith('image/')) return;
            if (state.layers.length <= 1 && state.layers[0].name === 'Background') {
                openImageFile(file);
            } else {
                importLayerFile(file);
            }
        });
    }

    function updateLayerPosition() {
        const layer = activeLayer();
        if (!layer) return;
        layer.x = Number(els.layerXInput.value) || 0;
        layer.y = Number(els.layerYInput.value) || 0;
        commit('Mover camada');
        render();
    }

    function init() {
        bindEvents();
        createInitialDocument();
        applyZoom();
        setTimeout(fitZoom, 80);
    }

    init();
})();
