/**
 * Apollo La Plata - Database (IndexedDB)
 * Traduzido de db.ts para Vanilla JS.
 * Gerencia a persistência de Personagens e da Galeria.
 */

const DB_NAME = 'GeminiStudioDB';
const DB_VERSION = 1;

const STORE_CHARACTERS = 'characters';
const STORE_GALLERY = 'gallery';
const STORE_PROJECTS = 'projects';

const openDB = () => {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = (event) => reject("Database error: " + event.target.error);

        request.onsuccess = (event) => resolve(event.target.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_CHARACTERS)) {
                db.createObjectStore(STORE_CHARACTERS, { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains(STORE_GALLERY)) {
                db.createObjectStore(STORE_GALLERY, { keyPath: 'id' });
            }
            if (!db.objectStoreNames.contains(STORE_PROJECTS)) {
                db.createObjectStore(STORE_PROJECTS, { keyPath: 'id' });
            }
        };
    });
};

const getAll = async (storeName) => {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(storeName, 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.getAll();

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
};

const saveItem = async (storeName, item) => {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.put(item);

        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
};

const deleteItem = async (storeName, id) => {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.delete(id);

        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
};

const clearStore = async (storeName) => {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.clear();

        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
};

// Objeto global de acesso ao DB
window.laplataDB = {
    characters: {
        getAll: () => getAll(STORE_CHARACTERS),
        save: (char) => saveItem(STORE_CHARACTERS, char),
        delete: (id) => deleteItem(STORE_CHARACTERS, id),
    },
    gallery: {
        getAll: () => getAll(STORE_GALLERY),
        save: (img) => saveItem(STORE_GALLERY, img),
        delete: (id) => deleteItem(STORE_GALLERY, id),
        clear: () => clearStore(STORE_GALLERY)
    },
    projects: {
        getAll: () => getAll(STORE_PROJECTS),
        save: (project) => saveItem(STORE_PROJECTS, project),
        delete: (id) => deleteItem(STORE_PROJECTS, id),
        clear: () => clearStore(STORE_PROJECTS)
    },
    // --- Economy API (LocalStorage for simplicity) ---
    getCurrencies: () => {
        const stored = localStorage.getItem('laplata_currencies');
        if (stored) return JSON.parse(stored);
        return { gasolina: 100, cristais: 0 }; // Starting balance
    },
    updateCurrency: (db_placeholder, type, amount) => {
        // db_placeholder is ignored, we use localStorage
        const curs = window.laplataDB.getCurrencies();
        curs[type] += amount;
        localStorage.setItem('laplata_currencies', JSON.stringify(curs));
        return curs;
    },
    updateTopNav: (db_placeholder) => {
        const curs = window.laplataDB.getCurrencies();
        
        // Update Gasolina
        const gasEl = document.getElementById('user-credits');
        if (gasEl) {
            gasEl.innerText = curs.gasolina;
            
            // Inject Cristais badge if it doesn't exist
            let crystalBadge = document.getElementById('user-crystal-badge');
            if (!crystalBadge) {
                const gasBadge = gasEl.closest('.credits-badge');
                if (gasBadge) {
                    crystalBadge = document.createElement('div');
                    crystalBadge.id = 'user-crystal-badge';
                    crystalBadge.className = 'credits-badge';
                    crystalBadge.style.marginLeft = '10px';
                    crystalBadge.style.display = 'flex';
                    crystalBadge.style.alignItems = 'center';
                    crystalBadge.innerHTML = `<span style="font-size: 1.2rem; margin-right: 5px;">💎</span><strong id="user-cristais">${curs.cristais}</strong>&nbsp;<span>Cristais</span>`;
                    gasBadge.parentNode.insertBefore(crystalBadge, gasBadge.nextSibling);
                }
            } else {
                document.getElementById('user-cristais').innerText = curs.cristais;
            }
        }
    },
    // Alias to avoid errors on Job Engine
    openDB: async () => { return null; }
};

// Auto-update top nav on load
document.addEventListener('DOMContentLoaded', () => {
    window.laplataDB.updateTopNav();
});
