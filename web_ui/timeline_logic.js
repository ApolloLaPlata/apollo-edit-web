// timeline_logic.js - Motor da Timeline de 4 Camadas

document.addEventListener('DOMContentLoaded', () => {
    
    const PIXELS_PER_SECOND = 20; // 20px = 1 segundo visual
    const MAX_SECONDS = 300; // 5 minutos de timeline

    let draggedBlock = null;
    let resizingBlock = null;
    let resizeDirection = null; // 'left' or 'right'
    let startX = 0;
    let startLeft = 0;
    let startWidth = 0;

    initRuler();
    setupToolbar();
    setupSaveButton();

    function initRuler() {
        const ruler = document.getElementById('timeline-ruler');
        if (!ruler) return;
        
        for (let i = 0; i <= MAX_SECONDS; i++) {
            const tick = document.createElement('div');
            tick.className = 'ruler-tick ' + (i % 5 === 0 ? 'major' : '');
            tick.style.left = (i * PIXELS_PER_SECOND) + 'px';
            
            if (i % 5 === 0) {
                // Format MM:SS
                const mins = Math.floor(i / 60);
                const secs = i % 60;
                tick.innerText = `${mins}:${secs.toString().padStart(2, '0')}`;
            }
            ruler.appendChild(tick);
        }
    }

    function setupToolbar() {
        document.querySelectorAll('.add-block-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const trackType = e.target.closest('button').dataset.track;
                addBlock(trackType);
                if(window.apolloSfx) window.apolloSfx.play('click');
            });
        });
    }

    let blockCounter = 1;

    function addBlock(trackType) {
        const trackContent = document.getElementById(`track-${trackType}`);
        if (!trackContent) return;

        const block = document.createElement('div');
        block.className = 'timeline-block';
        block.dataset.type = trackType;
        block.dataset.id = `block_${blockCounter++}`;
        
        // Default size = 5 seconds (100px)
        const defaultWidth = 5 * PIXELS_PER_SECOND;
        block.style.width = defaultWidth + 'px';
        
        // Find end of last block to snap (mostly for video)
        let maxLeft = 0;
        const existingBlocks = trackContent.querySelectorAll('.timeline-block');
        existingBlocks.forEach(b => {
            const rightEdge = parseFloat(b.style.left || 0) + parseFloat(b.style.width || 0);
            if (rightEdge > maxLeft) maxLeft = rightEdge;
        });

        block.style.left = maxLeft + 'px';

        // Content
        let title = "Bloco";
        if(trackType === 'video') title = "Cena Base";
        if(trackType === 'template') title = "Template Padrão";
        if(trackType === 'config') title = "LUT Dark";
        if(trackType === 'audio') title = "Voz Narrador";

        block.innerHTML = `
            <div class="resize-handle left"></div>
            <span>${title}</span>
            <div class="resize-handle right"></div>
        `;

        // Event listeners
        block.addEventListener('mousedown', onBlockMouseDown);
        
        trackContent.appendChild(block);
    }

    function onBlockMouseDown(e) {
        if (e.target.classList.contains('resize-handle')) {
            // Resizing
            resizingBlock = e.currentTarget;
            resizeDirection = e.target.classList.contains('left') ? 'left' : 'right';
        } else {
            // Dragging
            draggedBlock = e.currentTarget;
        }

        startX = e.clientX;
        startLeft = parseFloat(e.currentTarget.style.left || 0);
        startWidth = parseFloat(e.currentTarget.style.width || 0);

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        
        // Prevent text selection
        e.preventDefault(); 
    }

    function onMouseMove(e) {
        const deltaX = e.clientX - startX;

        if (draggedBlock) {
            let newLeft = startLeft + deltaX;
            if (newLeft < 0) newLeft = 0; // Don't go before 0
            draggedBlock.style.left = newLeft + 'px';
        } 
        else if (resizingBlock) {
            if (resizeDirection === 'right') {
                let newWidth = startWidth + deltaX;
                if (newWidth < 20) newWidth = 20; // Minimum size 1 sec
                resizingBlock.style.width = newWidth + 'px';
            } else if (resizeDirection === 'left') {
                let newLeft = startLeft + deltaX;
                let newWidth = startWidth - deltaX;
                
                if (newWidth < 20) {
                    newWidth = 20;
                    newLeft = startLeft + (startWidth - 20);
                }
                if (newLeft < 0) {
                    newLeft = 0;
                    newWidth = startWidth + startLeft;
                }
                
                resizingBlock.style.left = newLeft + 'px';
                resizingBlock.style.width = newWidth + 'px';
            }
        }
    }

    function onMouseUp() {
        draggedBlock = null;
        resizingBlock = null;
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);
        if(window.apolloSfx) window.apolloSfx.play('drop');
    }

    function setupSaveButton() {
        const btn = document.getElementById('btn-save-timeline');
        if (!btn) return;
        btn.addEventListener('click', () => {
            const timelineData = exportTimelineJSON();
            if (window.laplataInventory) {
                // Send to Inventory V2 Area de Transferência
                window.laplataInventory.copy(JSON.stringify(timelineData, null, 2), 'mapping');
                if (window.showToast) window.showToast('Mapeamento salvo na Área de Transferência!', 'success');
                if (window.apolloSfx) window.apolloSfx.play('success');
            } else {
                console.error("laplataInventory não encontrado.");
                alert("Mapeamento (JSON):\n" + JSON.stringify(timelineData, null, 2));
            }
        });
    }

    function exportTimelineJSON() {
        const data = {
            version: "1.0",
            total_duration_seconds: 0,
            tracks: {
                video: [],
                template: [],
                config: [],
                audio: []
            }
        };

        const tracks = ['video', 'template', 'config', 'audio'];
        
        tracks.forEach(t => {
            const trackEl = document.getElementById(`track-${t}`);
            const blocks = trackEl.querySelectorAll('.timeline-block');
            
            blocks.forEach(b => {
                const left = parseFloat(b.style.left || 0);
                const width = parseFloat(b.style.width || 0);
                const startSec = left / PIXELS_PER_SECOND;
                const endSec = (left + width) / PIXELS_PER_SECOND;
                
                if (endSec > data.total_duration_seconds) {
                    data.total_duration_seconds = endSec;
                }

                data.tracks[t].push({
                    id: b.dataset.id,
                    name: b.querySelector('span').innerText,
                    start_time: parseFloat(startSec.toFixed(2)),
                    end_time: parseFloat(endSec.toFixed(2)),
                    duration: parseFloat((endSec - startSec).toFixed(2))
                });
            });
            
            // Sort by start_time
            data.tracks[t].sort((a, b) => a.start_time - b.start_time);
        });

        return data;
    }
});
