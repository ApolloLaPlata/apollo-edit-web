/**
 * Apollo La Plata - Character Roster Logic
 * Gerencia a lógica de CRUD da interface laplata_roster.html utilizando o laplata_db.js
 */

document.addEventListener('DOMContentLoaded', async () => {
    const grid = document.getElementById('roster-grid');
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter');
    
    // Elementos do Modal
    const modal = document.getElementById('character-modal');
    const btnOpenModal = document.getElementById('btn-open-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const btnCancelModal = document.getElementById('btn-cancel-modal');
    const btnSaveChar = document.getElementById('btn-save-char');
    const btnDeleteChar = document.getElementById('btn-delete-char');
    const modalTitle = document.getElementById('modal-title');
    
    // Inputs do form
    const inputId = document.getElementById('char-id');
    const inputName = document.getElementById('char-name');
    const inputCategory = document.getElementById('char-category');
    const inputDescription = document.getElementById('char-description');
    const imageDropzone = document.getElementById('image-dropzone');
    const imageInput = document.getElementById('image-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');

    let currentCharacters = [];
    let pendingImagesBase64 = []; // Guarda as imagens em base64 do personagem atual

    // SFX Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playSuccess = () => { if (window.apolloSFX) window.apolloSFX.play('success'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };

    // Notificações
    const showToast = (title, message, type = 'system') => {
        if (window.apolloNotifications) {
            window.apolloNotifications.add(title, message, type);
        } else {
            console.log(`[${title}] ${message}`);
        }
    };

    // --- CARREGAMENTO INICIAL ---
    async function loadCharacters() {
        try {
            currentCharacters = await window.laplataDB.characters.getAll();
            updateCategoryDropdown();
            renderGrid();
        } catch (error) {
            console.error("Erro ao carregar personagens:", error);
            showToast('Erro Crítico', 'Falha ao ler o banco de dados local.', 'system');
            playError();
        }
    }

    function updateCategoryDropdown() {
        const categories = new Set(currentCharacters.map(c => c.category || 'Sem Categoria'));
        const optionsHTML = ['<option value="all">Todas Categorias</option>'];
        categories.forEach(cat => {
            optionsHTML.push(`<option value="${cat}">${cat}</option>`);
        });
        categoryFilter.innerHTML = optionsHTML.join('');
    }

    function renderGrid() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedCat = categoryFilter.value;

        const filtered = currentCharacters.filter(c => {
            const matchesSearch = c.name.toLowerCase().includes(searchTerm) || (c.description && c.description.toLowerCase().includes(searchTerm));
            const cat = c.category || 'Sem Categoria';
            const matchesCat = selectedCat === 'all' || cat === selectedCat;
            return matchesSearch && matchesCat;
        });

        if (filtered.length === 0) {
            grid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:50px; color:#94a3b8;">Nenhum personagem encontrado.</div>`;
            return;
        }

        grid.innerHTML = filtered.map(c => `
            <div class="character-card" data-id="${c.id}" onclick="window.editCharacter('${c.id}')">
                <div class="character-img-wrapper">
                    <img src="${c.previewUrl || 'assets/bg_timeline.png'}" alt="${c.name}">
                </div>
                <div class="character-card-content">
                    <h4 class="character-tag">${c.name}</h4>
                    <span class="character-category">${c.category || 'Sem Categoria'}</span>
                    <p style="font-size: 0.8rem; color: #cbd5e1; margin-top:5px; flex-grow:1; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
                        ${c.description || 'Sem descrição'}
                    </p>
                </div>
            </div>
        `).join('');
    }

    // Filtros
    searchInput.addEventListener('input', renderGrid);
    categoryFilter.addEventListener('change', renderGrid);

    // --- LÓGICA DO MODAL ---
    function openModal(isEdit = false) {
        modal.style.display = 'flex';
        playClick();
        if (!isEdit) {
            modalTitle.innerText = "Adicionar Personagem";
            inputId.value = '';
            inputName.value = '';
            inputCategory.value = '';
            inputDescription.value = '';
            pendingImagesBase64 = [];
            renderImagePreviews();
            btnDeleteChar.style.display = 'none';
        }
    }

    function closeModal() {
        modal.style.display = 'none';
        playClick();
    }

    btnOpenModal.addEventListener('click', () => openModal(false));
    btnCloseModal.addEventListener('click', closeModal);
    btnCancelModal.addEventListener('click', closeModal);

    // Expor função global para ser chamada pelo onclick dos cards
    window.editCharacter = (id) => {
        const char = currentCharacters.find(c => c.id === id);
        if (!char) return;

        openModal(true);
        modalTitle.innerText = "Editar Personagem";
        inputId.value = char.id;
        inputName.value = char.name;
        inputCategory.value = char.category || '';
        inputDescription.value = char.description || '';
        pendingImagesBase64 = [...(char.images || [])];
        renderImagePreviews();
        btnDeleteChar.style.display = 'block';
    };

    // --- UPLOAD DE IMAGENS ---
    imageDropzone.addEventListener('click', () => imageInput.click());

    imageInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            Array.from(e.target.files).forEach(processFile);
        }
    });

    imageDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        imageDropzone.style.borderColor = '#2ECC71';
    });

    imageDropzone.addEventListener('dragleave', () => {
        imageDropzone.style.borderColor = '#475569';
    });

    imageDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        imageDropzone.style.borderColor = '#475569';
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            Array.from(e.dataTransfer.files).forEach(processFile);
        }
    });

    function processFile(file) {
        if (!file.type.startsWith('image/')) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                const maxDim = 1024; // Compressão leve (La Plata Padrão)

                if (width > height && width > maxDim) {
                    height *= maxDim / width;
                    width = maxDim;
                } else if (height > maxDim) {
                    width *= maxDim / height;
                    height = maxDim;
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                const base64 = canvas.toDataURL('image/jpeg', 0.8);
                pendingImagesBase64.push(base64);
                renderImagePreviews();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }

    function renderImagePreviews() {
        if (pendingImagesBase64.length === 0) {
            imagePreviewContainer.innerHTML = '';
            return;
        }

        imagePreviewContainer.innerHTML = pendingImagesBase64.map((src, idx) => `
            <div style="position:relative; width:60px; height:60px;">
                <img src="${src}" class="preview-thumb">
                <button type="button" onclick="window.removePendingImage(${idx})" style="position:absolute; top:-5px; right:-5px; background:#ef4444; color:white; border:none; border-radius:50%; width:20px; height:20px; font-size:10px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.5);">X</button>
            </div>
        `).join('');
    }

    window.removePendingImage = (idx) => {
        pendingImagesBase64.splice(idx, 1);
        renderImagePreviews();
        playClick();
    };

    // --- SALVAR PERSONAGEM ---
    btnSaveChar.addEventListener('click', async () => {
        let name = inputName.value.trim();
        if (!name) {
            showToast('Aviso', 'O personagem precisa de um nome/tag!', 'system');
            inputName.focus();
            playError();
            return;
        }

        // Força ter # no começo
        if (!name.startsWith('#')) name = '#' + name;

        if (pendingImagesBase64.length === 0) {
            showToast('Aviso', 'Envie pelo menos 1 imagem de referência!', 'system');
            playError();
            return;
        }

        const charObj = {
            id: inputId.value || crypto.randomUUID(),
            name: name,
            category: inputCategory.value.trim(),
            description: inputDescription.value.trim(),
            images: pendingImagesBase64,
            previewUrl: pendingImagesBase64[0] // A primeira imagem é o preview principal
        };

        try {
            await window.laplataDB.characters.save(charObj);
            showToast('Sucesso', `Personagem ${name} salvo com sucesso!`, 'quest');
            playSuccess();
            closeModal();
            loadCharacters(); // Recarrega e renderiza o grid
            
            // Check quest genérica de criação
            if (window.apolloQuests) window.apolloQuests.checkAction('create_character');
            
        } catch (e) {
            console.error("Erro ao salvar:", e);
            showToast('Erro', 'Falha ao salvar no IndexedDB.', 'system');
            playError();
        }
    });

    // --- EXCLUIR PERSONAGEM ---
    btnDeleteChar.addEventListener('click', async () => {
        const id = inputId.value;
        if (!id) return;

        if (confirm(`Tem certeza que deseja excluir o personagem ${inputName.value}? Esta ação não pode ser desfeita.`)) {
            try {
                await window.laplataDB.characters.delete(id);
                showToast('Excluído', 'Personagem removido da biblioteca.', 'system');
                playSuccess();
                closeModal();
                loadCharacters();
            } catch (e) {
                console.error("Erro ao excluir:", e);
                showToast('Erro', 'Falha ao excluir.', 'system');
                playError();
            }
        }
    });

    // Inicialização
    loadCharacters();
});
