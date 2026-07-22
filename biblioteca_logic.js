/**
 * Biblioteca Apollo (Asset Library Logic)
 */

// Mock Database (Simulando os arquivos do HD H:\ que irão pro GitHub/R2)
const mockAssets = [
    { id: 'sfx_swoosh_01', type: 'sfx', title: 'Cinematic Swoosh Deep', category: 'Efeito Sonoro', duration: '0:02', url: 'mock_audio.mp3' },
    { id: 'sfx_impact_02', type: 'sfx', title: 'Impacto Épico Bass Drop', category: 'Efeito Sonoro', duration: '0:04', url: 'mock_audio.mp3' },
    { id: 'sfx_glitch_01', type: 'sfx', title: 'Digital Glitch Horror', category: 'Efeito Sonoro', duration: '0:01', url: 'mock_audio.mp3' },
    { id: 'bgm_cyber_01', type: 'bgm', title: 'Cyberpunk Chase 120BPM', category: 'Trilha Sonora', duration: '2:15', url: 'mock_audio.mp3' },
    
    { id: 'vid_overlay_glitch', type: 'overlay', title: 'Glitch Tela Quebrada (Alpha)', category: 'Overlay Vídeo', thumb: 'https://picsum.photos/400/200?random=1' },
    { id: 'vid_overlay_rain', type: 'overlay', title: 'Chuva Cinematográfica', category: 'Overlay Vídeo', thumb: 'https://picsum.photos/400/200?random=2' },
    { id: 'vid_trans_burn', type: 'transition', title: 'Transição Filme Queimado', category: 'Transição', thumb: 'https://picsum.photos/400/200?random=3' },
    { id: 'vid_bg_neon', type: 'background', title: 'Túnel Neon Infinito (Loop)', category: 'Background', thumb: 'https://picsum.photos/400/200?random=4' },
    
    { id: 'gfx_lower_third', type: 'template', title: 'Lower Third Notícias Vermelho', category: 'Template Gráfico', thumb: 'https://picsum.photos/400/200?random=5' }
];

document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('asset-grid');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const searchInput = document.getElementById('search-input');
    const titleLabel = document.getElementById('current-category-title');
    
    let currentFilter = 'sfx'; // default tab

    // Initialize
    loadUserGarage();
    renderAssets(currentFilter);

    // Filters
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterBtns.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            
            currentFilter = e.currentTarget.getAttribute('data-filter');
            titleLabel.textContent = e.currentTarget.textContent.trim();
            searchInput.value = ''; // clear search
            renderAssets(currentFilter);
        });
    });

    // Search
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        renderAssets(currentFilter, query);
    });

    // Render Grid
    function renderAssets(filterType, searchQuery = '') {
        grid.innerHTML = '';
        
        let filtered = mockAssets;
        if (filterType !== 'all') {
            filtered = filtered.filter(a => a.type === filterType);
        }
        if (searchQuery) {
            filtered = filtered.filter(a => a.title.toLowerCase().includes(searchQuery));
        }

        if (filtered.length === 0) {
            grid.innerHTML = `<div style="color: #666; grid-column: 1/-1; text-align: center; padding: 40px;">Nenhum asset encontrado para esta categoria.</div>`;
            return;
        }

        filtered.forEach(asset => {
            const isAdded = checkUserGarage(asset.id);
            const btnClass = isAdded ? 'btn-add added' : 'btn-add';
            const btnText = isAdded ? '<i class="fas fa-check"></i> Na Garagem' : '<i class="fas fa-plus"></i> Adicionar às Peças';

            let previewHTML = '';
            
            if (asset.type === 'sfx' || asset.type === 'bgm') {
                // Audio Preview
                previewHTML = `
                    <div class="asset-preview" style="background: #111;">
                        <div class="play-overlay" onclick="playMockAudio(this)"><i class="fas fa-play"></i></div>
                        <div class="waveform" style="display:none;">
                            <div class="bar" style="animation-delay: 0s"></div>
                            <div class="bar" style="animation-delay: 0.2s"></div>
                            <div class="bar" style="animation-delay: 0.4s"></div>
                            <div class="bar" style="animation-delay: 0.1s"></div>
                            <div class="bar" style="animation-delay: 0.5s"></div>
                        </div>
                    </div>
                `;
            } else {
                // Video/Image Preview
                previewHTML = `
                    <div class="asset-preview">
                        <img src="${asset.thumb}" alt="thumb">
                        <div class="play-overlay"><i class="fas fa-eye"></i></div>
                    </div>
                `;
            }

            const card = document.createElement('div');
            card.className = 'asset-card';
            card.innerHTML = `
                ${previewHTML}
                <div class="asset-info">
                    <h4 class="asset-title" title="${asset.title}">${asset.title}</h4>
                    <div class="asset-meta">
                        <span>${asset.category}</span>
                        ${asset.duration ? `<span>${asset.duration}</span>` : ''}
                    </div>
                    <button class="${btnClass}" onclick="toggleGarage('${asset.id}', this)">${btnText}</button>
                </div>
            `;
            grid.appendChild(card);
        });
    }

});

// Audio Playback Mock
let isPlaying = false;
function playMockAudio(btn) {
    const icon = btn.querySelector('i');
    const waveform = btn.nextElementSibling;
    
    if (isPlaying) {
        icon.className = 'fas fa-play';
        waveform.style.display = 'none';
        isPlaying = false;
    } else {
        // Stop all others
        document.querySelectorAll('.play-overlay i').forEach(i => i.className = 'fas fa-play');
        document.querySelectorAll('.waveform').forEach(w => w.style.display = 'none');
        
        icon.className = 'fas fa-pause';
        waveform.style.display = 'flex';
        isPlaying = true;
        
        // Auto pause after 3 seconds for demo
        setTimeout(() => {
            if(isPlaying && icon.className === 'fas fa-pause') {
                icon.className = 'fas fa-play';
                waveform.style.display = 'none';
                isPlaying = false;
            }
        }, 3000);
    }
}

// LocalStorage Garage Mock
let userGarage = [];
function loadUserGarage() {
    const saved = localStorage.getItem('apollo_user_assets');
    if (saved) {
        userGarage = JSON.parse(saved);
    }
}

function checkUserGarage(id) {
    return userGarage.includes(id);
}

function toggleGarage(id, btnElement) {
    if (userGarage.includes(id)) {
        // Remove
        userGarage = userGarage.filter(i => i !== id);
        btnElement.className = 'btn-add';
        btnElement.innerHTML = '<i class="fas fa-plus"></i> Adicionar às Peças';
    } else {
        // Add
        userGarage.push(id);
        btnElement.className = 'btn-add added';
        btnElement.innerHTML = '<i class="fas fa-check"></i> Na Garagem';
        
        // Show subtle notification
        console.log(`[Banco de Dados] Link salvo na conta do usuário: ${id} (0 Bytes consumidos)`);
    }
    localStorage.setItem('apollo_user_assets', JSON.stringify(userGarage));
}
