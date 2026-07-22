// apollo_os_desktop.js

window.appTabs = [];
window.activeTabId = null;
window.draggedTabId = null;

function saveSessionState() {
    const sessionData = {
        tabs: window.appTabs,
        activeTabId: window.activeTabId
    };
    localStorage.setItem('apollo_os_session', JSON.stringify(sessionData));
}

function initOS() {
    const savedSession = localStorage.getItem('apollo_os_session');
    
    if (savedSession) {
        try {
            const parsed = JSON.parse(savedSession);
            if (parsed.tabs && parsed.tabs.length > 0) {
                // Deduplicate tabs by URL to heal old duplicate sessions
                const seenUrls = new Set();
                const uniqueTabs = [];
                parsed.tabs.forEach(t => {
                    if (!seenUrls.has(t.url)) {
                        seenUrls.add(t.url);
                        uniqueTabs.push(t);
                    }
                });

                // Restore unique tabs
                uniqueTabs.forEach(t => {
                    restoreAppTab(t);
                });
                
                // Focus previously active tab (ensure it still exists after deduplication)
                if (parsed.activeTabId && uniqueTabs.find(t => t.id === parsed.activeTabId)) {
                    focusTab(parsed.activeTabId);
                } else {
                    focusTab(uniqueTabs[0].id);
                }
                return;
            }
        } catch (e) {
            console.warn("Falha ao recuperar sessão do OS", e);
        }
    }
    
    // Start with the Hub tab if no valid session
    openAppTab('hub.html', '🏠 Hub Central', false); 
}

function restoreAppTab(tabData) {
    // Forçar isClosable para true em tudo, exceto hub (corrige abas antigas corrompidas)
    tabData.isClosable = (tabData.url !== 'hub.html' && tabData.url !== 'index.html');
    
    window.appTabs.push(tabData);
    renderTabDOM(tabData.id, tabData.url, tabData.title, tabData.isClosable);
}

window.openAppTab = function(url, title, isClosable = true) {
    // Treat index.html and hub.html as the same Hub tab
    const isHub = url === 'hub.html' || url === 'index.html';
    const targetUrl = isHub ? 'hub.html' : url;
    isClosable = !isHub; // Força fechamento de abas para todas que não sejam o Hub
    
    // Check if the tab is already open (Singleton logic)
    const existingTab = window.appTabs.find(t => t.url === targetUrl || (isHub && (t.url === 'hub.html' || t.url === 'index.html')));
    if (existingTab) {
        focusTab(existingTab.id);
        return;
    }

    const uniqueHash = Math.random().toString(36).substring(2, 9);
    const tabId = isHub ? 'tab_hub_central' : 'tab_' + btoa(targetUrl).replace(/[^a-zA-Z0-9]/g, '').substring(0, 10) + '_' + uniqueHash;

    const tabData = {
        id: tabId,
        url: targetUrl,
        title: title || targetUrl.split('/').pop(),
        isClosable: isClosable
    };
    window.appTabs.push(tabData);

    renderTabDOM(tabId, targetUrl, tabData.title, isClosable);
    focusTab(tabId);
};

function renderTabDOM(tabId, url, title, isClosable) {
    const tabsBar = document.getElementById('os-tabs-bar');
    const tabEl = document.createElement('div');
    tabEl.className = 'os-tab';
    tabEl.id = `tab_el_${tabId}`;
    tabEl.onclick = () => focusTab(tabId);
    
    // Configura Drag and Drop
    tabEl.draggable = true;
    tabEl.addEventListener('dragstart', (e) => {
        window.draggedTabId = tabId;
        e.dataTransfer.effectAllowed = 'move';
        tabEl.style.opacity = '0.4';
    });
    tabEl.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        const bounding = tabEl.getBoundingClientRect();
        const offset = bounding.x + (bounding.width / 2);
        if (e.clientX - offset > 0) {
            tabEl.style.borderRight = '2px solid #8b5cf6';
            tabEl.style.borderLeft = '';
        } else {
            tabEl.style.borderLeft = '2px solid #8b5cf6';
            tabEl.style.borderRight = '';
        }
    });
    tabEl.addEventListener('dragleave', () => {
        tabEl.style.borderLeft = '';
        tabEl.style.borderRight = '';
    });
    tabEl.addEventListener('dragend', () => {
        tabEl.style.opacity = '1';
        document.querySelectorAll('.os-tab').forEach(el => {
            el.style.borderLeft = '';
            el.style.borderRight = '';
        });
    });
    tabEl.addEventListener('drop', (e) => {
        e.preventDefault();
        tabEl.style.borderLeft = '';
        tabEl.style.borderRight = '';
        if (window.draggedTabId === tabId) return;

        const bounding = tabEl.getBoundingClientRect();
        const offset = bounding.x + (bounding.width / 2);
        const insertAfter = (e.clientX - offset > 0);

        reorderTabs(window.draggedTabId, tabId, insertAfter);
    });
    
    let html = `<span class="os-tab-title">${title}</span>`;
    html += `<span class="os-tab-reload" onclick="reloadTab(event, '${tabId}')" title="Recarregar esta aba">↻</span>`;
    
    if (isClosable) {
        html += `<span class="os-tab-close" onclick="closeAppTab(event, '${tabId}')" title="Fechar aba">✕</span>`;
    }
    tabEl.innerHTML = html;
    tabsBar.appendChild(tabEl);

    // Render Iframe
    const workspace = document.getElementById('os-workspace');
    const iframe = document.createElement('iframe');
    iframe.className = 'os-app-frame';
    iframe.id = `frame_${tabId}`;
    iframe.src = url;
    
    iframe.onload = () => {
        try {
            const innerDoc = iframe.contentWindow.document;
            const links = innerDoc.querySelectorAll('a');
            links.forEach(link => {
                const href = link.getAttribute('href');
                if (href && href.endsWith('.html')) {
                    link.onclick = (e) => {
                        e.preventDefault();
                        if (href === 'hub.html' || href === 'index.html') {
                            window.parent.openAppTab('hub.html', '🏠 Hub Central', false);
                        } else {
                            window.parent.openAppTab(href, link.innerText.trim(), true);
                        }
                    };
                }
            });
            // Try updating title dynamically, avoid tracking it in session strictly if it gets too noisy
        } catch(e) {}
    };
    
    workspace.appendChild(iframe);
}

window.reloadTab = function(e, tabId) {
    if (e) e.stopPropagation();
    const frame = document.getElementById(`frame_${tabId}`);
    if (frame) {
        // Silently reload the iframe without affecting OS state
        const originalSrc = frame.src;
        frame.src = 'about:blank';
        setTimeout(() => { frame.src = originalSrc; }, 50);
    }
};

window.reorderTabs = function(draggedId, targetId, insertAfter) {
    const tabsBar = document.getElementById('os-tabs-bar');
    const draggedEl = document.getElementById(`tab_el_${draggedId}`);
    const targetEl = document.getElementById(`tab_el_${targetId}`);
    
    if (!draggedEl || !targetEl) return;
    
    if (insertAfter) targetEl.after(draggedEl);
    else targetEl.before(draggedEl);

    const dragIndex = window.appTabs.findIndex(t => t.id === draggedId);
    const dragItem = window.appTabs.splice(dragIndex, 1)[0];
    const newTargetIndex = window.appTabs.findIndex(t => t.id === targetId);
    
    if (insertAfter) window.appTabs.splice(newTargetIndex + 1, 0, dragItem);
    else window.appTabs.splice(newTargetIndex, 0, dragItem);
    
    saveSessionState();
};

window.focusTab = function(tabId) {
    window.activeTabId = tabId;
    
    document.querySelectorAll('.os-tab').forEach(el => el.classList.remove('active'));
    const targetTab = document.getElementById(`tab_el_${tabId}`);
    if (targetTab) targetTab.classList.add('active');

    document.querySelectorAll('.os-app-frame').forEach(el => el.classList.remove('active'));
    const targetFrame = document.getElementById(`frame_${tabId}`);
    if (targetFrame) targetFrame.classList.add('active');
    
    saveSessionState();
};

window.closeAppTab = function(e, tabId) {
    if (e) e.stopPropagation();

    const tabIndex = window.appTabs.findIndex(t => t.id === tabId);
    if (tabIndex === -1) return;
    
    const tabData = window.appTabs[tabIndex];
    if (!tabData.isClosable) return;

    document.getElementById(`tab_el_${tabId}`)?.remove();
    document.getElementById(`frame_${tabId}`)?.remove();

    window.appTabs.splice(tabIndex, 1);

    if (window.activeTabId === tabId) {
        if (window.appTabs.length > 0) {
            const newIndex = Math.max(0, tabIndex - 1);
            focusTab(window.appTabs[newIndex].id);
        } else {
            window.activeTabId = null;
        }
    }
    
    saveSessionState();
};

document.addEventListener('DOMContentLoaded', () => {
    initOS();
});
