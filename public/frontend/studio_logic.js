// studio_logic.js - Lógica para o Estúdio de Capas (Canvas)

let studioCanvas;
let studioCtx;
let studioBgImage = null;
let studioTexts = [];

// Estado do drag & drop
let isDragging = false;
let dragTextIndex = -1;
let dragOffsetX = 0;
let dragOffsetY = 0;

document.addEventListener('DOMContentLoaded', () => {
    studioCanvas = document.getElementById('studio-canvas');
    if (!studioCanvas) return;
    
    studioCtx = studioCanvas.getContext('2d');
    
    // Set default size
    studioCanvas.width = 1280;
    studioCanvas.height = 720;
    
    // Add mouse events
    studioCanvas.addEventListener('mousedown', handleMouseDown);
    studioCanvas.addEventListener('mousemove', handleMouseMove);
    studioCanvas.addEventListener('mouseup', handleMouseUp);
    studioCanvas.addEventListener('mouseout', handleMouseUp);
    
    // Touch events for mobile
    studioCanvas.addEventListener('touchstart', handleTouchStart, {passive: false});
    studioCanvas.addEventListener('touchmove', handleTouchMove, {passive: false});
    studioCanvas.addEventListener('touchend', handleMouseUp);
    
    drawStudio();
});

function drawStudio() {
    if (!studioCanvas || !studioCtx) return;
    
    // Limpar
    studioCtx.clearRect(0, 0, studioCanvas.width, studioCanvas.height);
    
    // Fundo
    if (studioBgImage) {
        // Draw image covering the canvas (contain or cover)
        // We will do "cover"
        const imgRatio = studioBgImage.width / studioBgImage.height;
        const canvasRatio = studioCanvas.width / studioCanvas.height;
        
        let drawWidth, drawHeight, offsetX, offsetY;
        
        if (imgRatio > canvasRatio) {
            drawHeight = studioCanvas.height;
            drawWidth = studioBgImage.width * (studioCanvas.height / studioBgImage.height);
            offsetX = (studioCanvas.width - drawWidth) / 2;
            offsetY = 0;
        } else {
            drawWidth = studioCanvas.width;
            drawHeight = studioBgImage.height * (studioCanvas.width / studioBgImage.width);
            offsetX = 0;
            offsetY = (studioCanvas.height - drawHeight) / 2;
        }
        
        studioCtx.drawImage(studioBgImage, offsetX, offsetY, drawWidth, drawHeight);
    } else {
        studioCtx.fillStyle = '#1e293b'; // slate-800
        studioCtx.fillRect(0, 0, studioCanvas.width, studioCanvas.height);
        
        studioCtx.fillStyle = '#94a3b8'; // slate-400
        studioCtx.font = 'bold 40px Arial';
        studioCtx.textAlign = 'center';
        studioCtx.textBaseline = 'middle';
        studioCtx.fillText('Nenhuma imagem de fundo', studioCanvas.width / 2, studioCanvas.height / 2);
    }
    
    // Textos
    studioTexts.forEach(item => {
        studioCtx.font = `bold ${item.size}px Arial`;
        studioCtx.fillStyle = item.color;
        studioCtx.textAlign = 'center';
        studioCtx.textBaseline = 'middle';
        
        // Sombra / Borda preta grossa (estilo YouTube)
        studioCtx.strokeStyle = 'black';
        studioCtx.lineWidth = item.size / 8;
        studioCtx.lineJoin = 'round';
        studioCtx.strokeText(item.text, item.x, item.y);
        studioCtx.fillText(item.text, item.x, item.y);
    });
}

function loadStudioImage(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            studioBgImage = img;
            drawStudio();
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function addTextToStudio() {
    const input = document.getElementById('studio-text');
    const colorInput = document.getElementById('studio-color');
    const sizeInput = document.getElementById('studio-size');
    
    const text = input.value.trim();
    if (!text) return;
    
    studioTexts.push({
        text: text.toUpperCase(), // Estilo thumbnail sempre maiúsculo
        color: colorInput.value,
        size: parseInt(sizeInput.value) || 100,
        x: studioCanvas.width / 2,
        y: studioCanvas.height / 2 + (studioTexts.length * 50)
    });
    
    input.value = '';
    drawStudio();
}

function clearStudioTexts() {
    studioTexts = [];
    drawStudio();
}

function downloadStudioImage() {
    if (!studioCanvas) return;
    
    const dataUrl = studioCanvas.toDataURL('image/jpeg', 0.9);
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = `capa-youtube-${Date.now()}.jpg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// === Lógica de Drag & Drop ===

function getMousePos(evt) {
    const rect = studioCanvas.getBoundingClientRect();
    const scaleX = studioCanvas.width / rect.width;
    const scaleY = studioCanvas.height / rect.height;
    
    return {
        x: (evt.clientX - rect.left) * scaleX,
        y: (evt.clientY - rect.top) * scaleY
    };
}

function getTouchPos(evt) {
    const rect = studioCanvas.getBoundingClientRect();
    const scaleX = studioCanvas.width / rect.width;
    const scaleY = studioCanvas.height / rect.height;
    
    const touch = evt.touches[0];
    return {
        x: (touch.clientX - rect.left) * scaleX,
        y: (touch.clientY - rect.top) * scaleY
    };
}

function isMouseInText(x, y, item) {
    studioCtx.font = `bold ${item.size}px Arial`;
    const metrics = studioCtx.measureText(item.text);
    const width = metrics.width;
    const height = item.size; // aproximação da altura
    
    // textAlign='center', textBaseline='middle'
    const left = item.x - width / 2;
    const right = item.x + width / 2;
    const top = item.y - height / 2;
    const bottom = item.y + height / 2;
    
    return x >= left && x <= right && y >= top && y <= bottom;
}

function handleMouseDown(e) {
    const pos = getMousePos(e);
    startDrag(pos.x, pos.y);
}

function handleMouseMove(e) {
    if (!isDragging) return;
    const pos = getMousePos(e);
    doDrag(pos.x, pos.y);
}

function handleTouchStart(e) {
    const pos = getTouchPos(e);
    if (startDrag(pos.x, pos.y)) {
        e.preventDefault(); // Previne scroll se clicou no texto
    }
}

function handleTouchMove(e) {
    if (!isDragging) return;
    e.preventDefault();
    const pos = getTouchPos(e);
    doDrag(pos.x, pos.y);
}

function handleMouseUp() {
    isDragging = false;
    dragTextIndex = -1;
}

function startDrag(x, y) {
    // Percorre do último para o primeiro (os de cima primeiro)
    for (let i = studioTexts.length - 1; i >= 0; i--) {
        const item = studioTexts[i];
        if (isMouseInText(x, y, item)) {
            isDragging = true;
            dragTextIndex = i;
            dragOffsetX = x - item.x;
            dragOffsetY = y - item.y;
            return true;
        }
    }
    return false;
}

function doDrag(x, y) {
    if (dragTextIndex > -1) {
        studioTexts[dragTextIndex].x = x - dragOffsetX;
        studioTexts[dragTextIndex].y = y - dragOffsetY;
        drawStudio();
    }
}
