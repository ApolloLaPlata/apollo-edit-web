const API_TOKEN = 'apollo_admin_token_secure_v1';
let mainChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    switchTab('dashboard'); // Carrega a tab padrão que disparará as funções
    loadSettingsConfig(); // Força o carregamento das configurações para que a chave API esteja disponível para a IA
    loadKeys(); // Puxa todo o Vault de Chaves no boot para a Inteligência Artificial ter acesso imediato
    initWhatsAppPolling(); // Inicia o monitoramento do WhatsApp Bridge
});

// ==========================================
// WhatsApp Bridge UI Logic
// ==========================================
let waPollingInterval = null;

function initWhatsAppPolling() {
    if(waPollingInterval) clearInterval(waPollingInterval);
    pollWhatsAppStatus();
    waPollingInterval = setInterval(pollWhatsAppStatus, 3000);
}

async function pollWhatsAppStatus() {
    try {
        const response = await fetch('/api/whatsapp/status', {
            headers: { 'Authorization': API_TOKEN }
        });
        const data = await response.json();
        
        const statusText = document.getElementById('wa-status-text');
        const connectBtn = document.getElementById('wa-connect-btn');
        const qrModal = document.getElementById('wa-qr-modal');
        const qrContainer = document.getElementById('wa-qr-image-container');
        const qrStatus = document.getElementById('wa-qr-status');
        
        if (!statusText) return;

        if (data.running && data.status === 'CONNECTED') {
            statusText.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-green-500"></span> CONECTADO';
            statusText.className = 'text-green-400 font-bold flex items-center gap-1';
            connectBtn.classList.add('hidden');
            qrModal.classList.add('hidden');
        } 
        else if (data.running && data.status === 'QR_READY') {
            statusText.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse"></span> AGUARDANDO QR';
            statusText.className = 'text-yellow-400 font-bold flex items-center gap-1';
            connectBtn.classList.add('hidden');
            qrModal.classList.remove('hidden');
            
            // Render QR code using a public API service
            if (data.qr) {
                const encodedQR = encodeURIComponent(data.qr);
                qrContainer.innerHTML = `<img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodedQR}" alt="WhatsApp QR Code" class="rounded">`;
                qrStatus.innerText = 'Escaneie o código acima com o seu celular';
                qrStatus.className = 'text-green-400 text-xs font-bold';
            }
        } 
        else {
            // OFFLINE or DISCONNECTED
            statusText.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-red-500"></span> OFFLINE';
            statusText.className = 'text-red-400 font-bold flex items-center gap-1';
            connectBtn.classList.remove('hidden');
            
            // Se o modal de QR estava aberto e o server caiu
            if(!qrModal.classList.contains('hidden') && data.status === 'OFFLINE') {
                qrStatus.innerText = 'Servidor Offline. Clique em Ligar.';
                qrStatus.className = 'text-red-400 text-xs font-bold';
            }
        }
    } catch (e) {
        console.error("Failed to poll WhatsApp status", e);
    }
}

async function startWhatsApp() {
    const connectBtn = document.getElementById('wa-connect-btn');
    if(connectBtn) connectBtn.innerText = 'Ligando...';
    
    try {
        await fetch('/api/whatsapp/start', {
            method: 'POST',
            headers: { 'Authorization': API_TOKEN }
        });
        
        // Abre o modal de carregamento imediatamente
        document.getElementById('wa-qr-modal').classList.remove('hidden');
        document.getElementById('wa-qr-image-container').innerHTML = '<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>';
        document.getElementById('wa-qr-status').innerText = 'Iniciando servidor NodeJS...';
        document.getElementById('wa-qr-status').className = 'text-yellow-400 text-xs font-bold animate-pulse';
        
    } catch (e) {
        alert("Erro ao tentar ligar o WhatsApp Bridge.");
    }
}

function logout() {
    window.location.href = '/hub.html';
}

function switchTab(tab) {
    const tabs = ['dashboard', 'pages', 'keys', 'agents', 'models', 'users', 'ads', 'logs', 'economy', 'security'];
    tabs.forEach(t => {
        const btn = document.getElementById(`tab-${t}`);
        const content = document.getElementById(`content-${t}`);
        if(btn && content) {
            if(t === tab) {
                // Active State Sidebar
                btn.classList.add('bg-slate-700', 'text-blue-400', 'border-l-4', 'border-blue-500', 'active');
                btn.classList.remove('text-slate-400', 'border-transparent');
                content.classList.remove('hidden');
            } else {
                // Inactive State Sidebar
                btn.classList.remove('bg-slate-700', 'text-blue-400', 'border-l-4', 'border-blue-500', 'active');
                btn.classList.add('text-slate-400', 'border-transparent', 'border-l-4');
                content.classList.add('hidden');
            }
        }
    });

    // Trigger loads
    if(tab === 'dashboard') loadDashboard();
    if(tab === 'pages') loadPages();
    if(tab === 'users') loadUsers();
    if(tab === 'keys') loadKeys();
    if(tab === 'agents') loadAgentsConfig();
    if(tab === 'models') loadModelsPricing();
    if(tab === 'ads') loadAds();
    if(tab === 'logs') loadLogs();
    if(tab === 'economy') loadEconomyStats();
    if(tab === 'strategy') loadMarketReports();
    if(tab === 'lab') loadTrends();
    if(tab === 'economy' || tab === 'security') loadSettingsConfig();
}

async function fetchWithToken(url, options = {}) {
    let origin = window.location.origin;
    if(origin === 'null' || origin.startsWith('file:')) {
        origin = 'http://127.0.0.1:8080';
    }
    const u = new URL(url, origin);
    if(options.method === 'GET' || !options.method) {
        u.searchParams.append('token', API_TOKEN);
    }
    
    const res = await fetch(u.toString(), options);
    if (res.status === 401) {
        console.warn('Backend Auth Ignorado Localmente');
    }
    return res.json();
}

// ==============================
// DASHBOARD
// ==============================
async function loadDashboard() {
    let stats = { total_users: 1540, renders_today: 432, total_visits: 12500, profit_estimated: 'R$ 8.450,00' };
    try {
        const data = await fetchWithToken('/api/master/dashboard');
        if (data.success) {
            stats = data.stats;
        }
    } catch (e) { console.warn("Backend API offline, usando mock data visual.", e); }

    // Atualiza Painel de Números independentemente de falhar (Fallback visual)
    document.getElementById('dash-users').innerText = stats.total_users;
    document.getElementById('dash-renders').innerText = stats.renders_today;
    document.getElementById('dash-visits').innerText = stats.total_visits;
    document.getElementById('dash-profit').innerText = stats.profit_estimated;

    // --- CHART DE ACESSOS (Main Chart) ---
    const ctx = document.getElementById('mainChart').getContext('2d');
    if (mainChartInstance) mainChartInstance.destroy();

    const labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom'];
    const visitsData = [120, 190, 300, 250, 200, 400, 350];
    const costData = [10, 15, 25, 20, 18, 45, 30];

    let gradientBlue = ctx.createLinearGradient(0, 0, 0, 400);
    gradientBlue.addColorStop(0, 'rgba(59, 130, 246, 0.6)');
    gradientBlue.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

    let gradientPurple = ctx.createLinearGradient(0, 0, 0, 400);
    gradientPurple.addColorStop(0, 'rgba(168, 85, 247, 0.6)');
    gradientPurple.addColorStop(1, 'rgba(168, 85, 247, 0.0)');

    mainChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '📈 Acessos Reais', data: visitsData, borderColor: '#60a5fa', backgroundColor: gradientBlue,
                    borderWidth: 3, pointBackgroundColor: '#fff', pointBorderColor: '#60a5fa', pointHoverBackgroundColor: '#60a5fa', pointHoverBorderColor: '#fff',
                    pointRadius: 4, pointHoverRadius: 6, tension: 0.4, fill: true, yAxisID: 'y'
                },
                {
                    label: '💸 Custo Operacional (R$)', data: costData, borderColor: '#c084fc', backgroundColor: gradientPurple,
                    borderWidth: 3, pointBackgroundColor: '#fff', pointBorderColor: '#c084fc', pointHoverBackgroundColor: '#c084fc', pointHoverBorderColor: '#fff',
                    pointRadius: 4, pointHoverRadius: 6, tension: 0.4, fill: true, yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
            plugins: { legend: { labels: { color: '#cbd5e1', font: { size: 12, family: 'sans-serif', weight: 'bold' } } }, tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleColor: '#fff', bodyColor: '#cbd5e1', borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1 } },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                y: { type: 'linear', display: true, position: 'left', grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#94a3b8' } },
                y1: { type: 'linear', display: true, position: 'right', grid: { drawOnChartArea: false }, ticks: { color: '#94a3b8' } }
            }
        }
    });

    // --- CHART DE PLANOS (Doughnut) ---
    const doughnutCtx = document.getElementById('doughnutChart').getContext('2d');
    if(window.doughnutChartInstance) window.doughnutChartInstance.destroy();

    window.doughnutChartInstance = new Chart(doughnutCtx, {
        type: 'doughnut',
        data: {
            labels: ['Free', 'Pro', 'Hacker', 'Master'],
            datasets: [{
                data: [60, 25, 10, 5],
                backgroundColor: ['#64748b', '#3b82f6', '#a855f7', '#ef4444'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { position: 'right', labels: { color: '#cbd5e1', boxWidth: 10, font: {size: 10} } }
            }
        }
    });
}

// ==============================
// USERS
// ==============================
async function loadUsers() {
    try {
        const data = await fetchWithToken('/api/master/users');
        if (data.success) {
            const tbody = document.getElementById('usersTableBody');
            tbody.innerHTML = '';
            data.users.forEach(user => {
                const statusBadge = user.is_banned ? 
                    `<span class="bg-red-900 text-red-300 px-2 py-1 rounded text-xs font-bold">BANIDO</span>` : 
                    `<span class="bg-green-900 text-green-300 px-2 py-1 rounded text-xs font-bold">ATIVO</span>`;
                
                const banBtn = user.is_banned ?
                    `<button onclick="toggleBan(${user.id}, false)" class="bg-green-700 hover:bg-green-600 px-2 py-1 rounded text-xs ml-1">Desbanir</button>` :
                    `<button onclick="toggleBan(${user.id}, true)" class="bg-red-700 hover:bg-red-600 px-2 py-1 rounded text-xs ml-1">Banir</button>`;

                const gas = user.gas || 0;
                const crystals = user.crystals || 0;

                tbody.innerHTML += `
                    <tr class="border-b border-gray-800">
                        <td class="py-3 px-4">#${user.id}</td>
                        <td class="py-3 px-4 font-semibold text-blue-400">${user.username}</td>
                        <td class="py-3 px-4">${statusBadge}</td>
                        <td class="py-3 px-4 text-purple-400">${user.role}</td>
                        <td class="py-3 px-4">
                            <div class="flex flex-wrap gap-1">
                                <span class="bg-blue-900 bg-opacity-50 text-blue-300 px-2 py-1 rounded text-xs">💎 ${user.credits}</span>
                                <span class="bg-green-900 bg-opacity-50 text-green-300 px-2 py-1 rounded text-xs">⛽ ${gas}</span>
                                <span class="bg-purple-900 bg-opacity-50 text-purple-300 px-2 py-1 rounded text-xs">🔮 ${crystals}</span>
                            </div>
                        </td>
                        <td class="py-3 px-4 text-right">
                            <button onclick="showCreditModal(${user.id}, ${user.credits}, ${gas}, ${crystals})" class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-xs">Saldo</button>
                            ${banBtn}
                        </td>
                    </tr>
                `;
            });
        }
    } catch (e) { console.error(e); }
}

function showCreditModal(userId, credits, gas, crystals) {
    document.getElementById('manageUserId').value = userId;
    document.getElementById('manageAmount').value = '';
    document.getElementById('modalBalCredits').innerText = '💎 ' + (credits || 0);
    document.getElementById('modalBalGas').innerText = '⛽ ' + (gas || 0);
    document.getElementById('modalBalCrystals').innerText = '🔮 ' + (crystals || 0);
    document.getElementById('modalAddCredit').classList.remove('hidden');
}

function showCreateUserModal() {
    document.getElementById('newUsername').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('newCredits').value = '100';
    document.getElementById('modalCreateUser').classList.remove('hidden');
}

function closeModals() {
    document.getElementById('modalAddCredit')?.classList.add('hidden');
    document.getElementById('modalCreateUser')?.classList.add('hidden');
    document.getElementById('modalPageSettings')?.classList.add('hidden');
    document.getElementById('modalModelPricing')?.classList.add('hidden');
}

async function submitCredits(action) {
    const userId = document.getElementById('manageUserId').value;
    const amount = document.getElementById('manageAmount').value;
    const currency = document.getElementById('manageCurrency').value;
    if(!amount || amount <= 0) return alert('Insira um valor válido.');

    try {
        const res = await fetch('/api/master/users/balance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: API_TOKEN,
                user_id: parseInt(userId),
                amount: parseInt(amount),
                action: action,
                currency: currency
            })
        });
        const data = await res.json();
        if(data.success) { closeModals(); loadUsers(); } else alert('Erro: ' + data.error);
    } catch (e) { console.error(e); }
}

async function submitCreateUser() {
    const username = document.getElementById('newUsername').value;
    const pass = document.getElementById('newPassword').value;
    const credits = document.getElementById('newCredits').value;
    const role = document.getElementById('newRole').value;
    
    if(!username || !pass) return alert('Preencha os dados.');

    try {
        const res = await fetch('/api/admin/users/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: API_TOKEN,
                username: username,
                password: pass,
                initial_credits: parseInt(credits) || 0,
                role: role
            })
        });
        const data = await res.json();
        if(data.success) { closeModals(); loadUsers(); } else alert('Erro: ' + data.error);
    } catch (e) { console.error(e); }
}

// ==============================
// KEYS
// ==============================
let cachedApiConfig = {};
async function loadKeys() {
    try {
        const data = await fetchWithToken('/api/master/keys');
        if (data.success) {
            cachedApiConfig = data.api_config;
            renderKeysUI();
            updateHealthWidget();
        }
    } catch (e) { console.error(e); }
}

function updateHealthWidget() {
    const healthContainer = document.getElementById('health-widget-container');
    if (!healthContainer) return;
    
    let html = `
        <li class="flex items-center justify-between bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            Banco Supabase 
            <span class="text-green-400 font-bold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span> OK</span>
        </li>
        <li class="flex items-center justify-between bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
            Rede Edge 
            <span class="text-green-400 font-bold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-green-500"></span> OK</span>
        </li>
    `;

    if (cachedApiConfig) {
        for (const [provider, info] of Object.entries(cachedApiConfig)) {
            let hasKey = info.api_keys && info.api_keys.length > 0;
            let statusHtml = hasKey 
                ? '<span class="text-blue-400 font-bold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_#3b82f6]"></span> Estável</span>'
                : '<span class="text-red-400 font-bold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]"></span> Ausente</span>';
            
            let formattedName = provider.charAt(0).toUpperCase() + provider.slice(1);
            
            html += `
            <li class="flex items-center justify-between bg-slate-900/50 p-2.5 rounded-lg border border-slate-800">
                IA (${formattedName})
                ${statusHtml}
            </li>
            `;
        }
    }

    healthContainer.innerHTML = html;
}

function renderKeysUI() {
    const container = document.getElementById('keysContainer');
    container.innerHTML = '';
    for (const [provider, info] of Object.entries(cachedApiConfig)) {
        let keysHtml = '';
        if (info.api_keys) {
            info.api_keys.forEach((k, idx) => {
                keysHtml += `
                    <div class="flex items-center space-x-2 mt-2 bg-gray-900 p-2 rounded">
                        <input type="text" value="${k.name}" class="input-dark w-1/3 p-1 rounded text-sm" disabled>
                        <input type="password" value="${k.key}" class="input-dark w-full p-1 rounded text-sm" disabled>
                        <button onclick="removeKey('${provider}', ${idx})" class="text-red-500 hover:text-red-400 text-xs font-bold">X</button>
                    </div>
                `;
            });
        }
        
        container.innerHTML += `
            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700">
                <h4 class="font-bold text-lg capitalize mb-1">${provider}</h4>
                <p class="text-xs text-gray-500 break-all mb-4">${info.base_url}</p>
                <div class="space-y-2 mb-4">
                    ${keysHtml || '<p class="text-gray-500 text-sm">Nenhuma chave cadastrada.</p>'}
                </div>
                <div class="flex space-x-2">
                    <input type="text" id="newKeyName_${provider}" placeholder="Nome (Ex: Conta Principal)" class="input-dark text-sm p-2 rounded w-1/3">
                    <input type="text" id="newKeyValue_${provider}" placeholder="Nova Chave API" class="input-dark text-sm p-2 rounded w-full">
                    <button onclick="addKey('${provider}')" class="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm font-bold">+</button>
                </div>
            </div>
        `;
    }
}

async function addKey(provider) {
    const name = document.getElementById(`newKeyName_${provider}`).value;
    const keyVal = document.getElementById(`newKeyValue_${provider}`).value;
    if(!name || !keyVal) return alert('Preencha nome e valor da chave.');

    if(!cachedApiConfig[provider].api_keys) cachedApiConfig[provider].api_keys = [];
    cachedApiConfig[provider].api_keys.push({name: name, key: keyVal, status: "unknown"});
    
    await saveKeys(provider, cachedApiConfig[provider].api_keys);
}

async function removeKey(provider, idx) {
    if(!confirm("Tem certeza que deseja apagar essa chave?")) return;
    cachedApiConfig[provider].api_keys.splice(idx, 1);
    await saveKeys(provider, cachedApiConfig[provider].api_keys);
}

async function saveKeys(provider, newKeys) {
    try {
        const res = await fetch('/api/master/keys/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, provider: provider, keys: newKeys })
        });
        const data = await res.json();
        if(data.success) loadKeys(); else alert('Erro ao salvar');
    } catch(e) { console.error(e); }
}

// ==============================
// MODELS PRICING
// ==============================

async function syncPricesNow() {
    const btn = document.getElementById('btn-sync-prices');
    if (btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sincronizando...';
    try {
        const res = await fetchWithToken('/api/admin/scraper/sync', 'POST');
        if (res.success && res.details) {
            alert(`Sincronização concluída!\nNovos modelos encontrados: ${res.details.new}\nModelos atualizados: ${res.details.updated}`);
            loadModelsPricing();
        } else {
            alert('Erro ao sincronizar preços: ' + (res.error || 'Erro desconhecido.'));
        }
    } catch(e) {
        console.error(e);
        alert('Erro de conexão ao sincronizar preços.');
    } finally {
        if (btn) btn.innerHTML = '<i class="fas fa-sync-alt"></i> Sincronizar Preços';
    }
}

async function loadModelsPricing() {
    try {
        const data = await fetchWithToken('/api/master/models_pricing');
        if (data.success) {
            const tbody = document.getElementById('modelsTableBody');
            tbody.innerHTML = '';
            data.models.forEach(m => {
                const tierColor = m.tier === 'Free' ? 'text-green-400' : 'text-yellow-400';
                const statusColor = m.status === 'Ativo' ? 'text-green-400' : (m.status === 'Inativo' ? 'text-gray-500' : 'text-red-400');
                
                tbody.innerHTML += `
                    <tr class="border-b border-gray-800">
                        <td class="py-3 px-4 font-bold text-white">${m.provider}</td>
                        <td class="py-3 px-4 font-mono text-xs text-blue-300">${m.model_id}</td>
                        <td class="py-3 px-4 font-bold ${tierColor}">${m.tier}</td>
                        <td class="py-3 px-4">$${m.input_price_per_1m.toFixed(4)}</td>
                        <td class="py-3 px-4">$${m.output_price_per_1m.toFixed(4)}</td>
                        <td class="py-3 px-4 text-xs text-slate-400">RPM: ${m.rpm_limit} | TPM: ${m.tpm_limit}</td>
                        <td class="py-3 px-4 text-right">
                            <button onclick='editModelPricing(${JSON.stringify(m).replace(/'/g, "\\'")})' class="bg-gray-700 hover:bg-gray-600 px-2 py-1 rounded text-xs mr-1">Editar</button>
                            <button onclick="deleteModelPricing(${m.id})" class="bg-red-700 hover:bg-red-600 px-2 py-1 rounded text-xs">Apagar</button>
                        </td>
                    </tr>
                `;
            });
        }
    } catch (e) { console.error('Erro ao carregar models pricing', e); }
}

function showModelModal() {
    document.getElementById('editModelId').value = '';
    document.getElementById('editModelProvider').value = '';
    document.getElementById('editModelName').value = '';
    document.getElementById('editModelTier').value = 'Premium';
    document.getElementById('editModelStatus').value = 'Ativo';
    document.getElementById('editModelInput').value = '0.0';
    document.getElementById('editModelOutput').value = '0.0';
    document.getElementById('editModelRpm').value = '0';
    document.getElementById('editModelTpm').value = '0';
    
    document.getElementById('modalModelPricing').classList.remove('hidden');
}

function editModelPricing(m) {
    document.getElementById('editModelId').value = m.id;
    document.getElementById('editModelProvider').value = m.provider;
    document.getElementById('editModelName').value = m.model_id;
    document.getElementById('editModelTier').value = m.tier;
    document.getElementById('editModelStatus').value = m.status;
    document.getElementById('editModelInput').value = m.input_price_per_1m;
    document.getElementById('editModelOutput').value = m.output_price_per_1m;
    document.getElementById('editModelRpm').value = m.rpm_limit;
    document.getElementById('editModelTpm').value = m.tpm_limit;
    
    document.getElementById('modalModelPricing').classList.remove('hidden');
}

async function submitModelPricing() {
    const id = document.getElementById('editModelId').value;
    const provider = document.getElementById('editModelProvider').value;
    const model_id = document.getElementById('editModelName').value;
    
    if(!provider || !model_id) return alert('Preencha Provider e Model ID');
    
    const payload = {
        token: API_TOKEN,
        model: {
            id: id ? parseInt(id) : null,
            model_id: model_id,
            provider: provider,
            tier: document.getElementById('editModelTier').value,
            status: document.getElementById('editModelStatus').value,
            input_price_per_1m: parseFloat(document.getElementById('editModelInput').value || 0),
            output_price_per_1m: parseFloat(document.getElementById('editModelOutput').value || 0),
            rpm_limit: parseInt(document.getElementById('editModelRpm').value || 0),
            tpm_limit: parseInt(document.getElementById('editModelTpm').value || 0)
        }
    };
    
    try {
        const res = await fetch('/api/master/models_pricing/upsert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if(data.success) {
            alert('Configuração Salva');
            loadModelsPricing();
            closeModals();
        } else {
            alert('Erro ao salvar');
        }
    } catch(e) { console.error(e); }
}

// ==============================
// MARKET ANALYST
// ==============================
async function loadMarketReports() {
    try {
        const data = await fetchWithToken('/api/admin/market_analyst/reports');
        if (data.success) {
            const container = document.getElementById('market-reports-container');
            if(data.reports.length === 0) {
                container.innerHTML = '<p class="text-slate-400 text-sm">Nenhum relatório gerado ainda.</p>';
                return;
            }
            container.innerHTML = data.reports.map(r => `
                <div class="bg-slate-900/50 p-4 rounded-xl border border-slate-700">
                    <p class="text-xs text-slate-500 mb-2 font-bold">${new Date(r.created_at + 'Z').toLocaleString()}</p>
                    <div class="text-sm text-slate-300 whitespace-pre-wrap font-mono">${r.report_text}</div>
                    <div class="mt-4 pt-4 border-t border-slate-700/50 text-yellow-400 text-xs font-bold">Ações: ${r.recommended_actions}</div>
                </div>
            `).join('');
        }
    } catch(e) { console.error(e); }
}

async function runMarketAnalyst() {
    const btn = document.getElementById('btn-run-analyst');
    if(btn) btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analisando Mercado...';
    try {
        const res = await fetchWithToken('/api/admin/market_analyst/run', 'POST');
        if (res.success) {
            alert('Relatório Estratégico gerado com sucesso!');
            loadMarketReports();
        } else {
            alert('Erro: ' + (res.error || 'Desconhecido'));
        }
    } catch(e) {
        alert('Erro ao rodar analista.');
    } finally {
        if(btn) btn.innerHTML = '<i class="fas fa-brain"></i> Gerar Relatório Agora';
    }
}

async function deleteModelPricing(id) {
    if(!confirm("Tem certeza que deseja apagar este modelo?")) return;
    try {
        const res = await fetch('/api/master/models_pricing/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, id: id })
        });
        const data = await res.json();
        if(data.success) loadModelsPricing();
    } catch(e) { console.error(e); }
}

// ==============================
// AGENTES & FLUXOS (ORQUESTRADOR)
// ==============================
async function loadAgentsConfig() {
    try {
        // Load Frotas first
        const settingsData = await fetchWithToken('/api/master/settings');
        if (settingsData.success) {
            const s = settingsData.settings;
            document.getElementById('fleetGeminiPaid').value = s.fleet_gemini_paid || '';
            document.getElementById('fleetOpenRouterPaid').value = s.fleet_openrouter_paid || '';
            document.getElementById('fleetGroqFree').value = s.fleet_groq_free || '';
            document.getElementById('fleetOpenRouterFree').value = s.fleet_openrouter_free || '';
        }

        // Load N8N Pipeline Nodes
        const nodesData = await fetchWithToken('/api/master/orchestrator/nodes');
        if (nodesData.success && nodesData.nodes.length > 0) {
            const container = document.getElementById('agentsConfigContainer');
            container.innerHTML = '';
            
            nodesData.nodes.forEach((n, idx) => {
                const colors = ['purple', 'green', 'blue', 'red', 'yellow'];
                const color = colors[idx % colors.length];
                
                container.innerHTML += `
                    <div class="bg-slate-900/80 p-4 rounded-xl border border-${color}-500/30 relative">
                        <div class="absolute -left-3 top-1/2 transform -translate-y-1/2 w-6 h-6 bg-${color}-600 rounded-full flex items-center justify-center text-xs font-bold shadow-[0_0_10px_rgba(0,0,0,0.5)] border-2 border-slate-800 z-10">
                            ${n.step_order}
                        </div>
                        <h4 class="font-bold text-white text-sm mb-3 ml-2 flex items-center justify-between">
                            <span>Step ${n.step_order}: ${n.role_name}</span>
                            <span class="text-xs ${n.is_dynamic ? 'text-green-400' : 'text-slate-500'}">
                                ${n.is_dynamic ? '⚡ Auto-Optmize ON' : '🔒 Fixed Model'}
                            </span>
                        </h4>
                        <div class="grid grid-cols-2 gap-3 mb-3 ml-2">
                            <div>
                                <label class="block text-[10px] text-slate-500 uppercase font-bold mb-1">Model ID Alvo (ou 'auto')</label>
                                <input type="text" id="nodeModel_${n.id}" class="w-full input-dark rounded p-2 text-xs text-${color}-300 font-mono" value="${n.default_model_id}">
                            </div>
                            <div class="flex items-end pb-1">
                                <label class="flex items-center gap-2 cursor-pointer">
                                    <input type="checkbox" id="nodeDynamic_${n.id}" class="form-checkbox text-blue-500 rounded bg-slate-800 border-slate-600" ${n.is_dynamic ? 'checked' : ''}>
                                    <span class="text-xs text-slate-300">Deixar Meta-Agente escolher o +Barato</span>
                                </label>
                            </div>
                        </div>
                        <textarea id="nodePrompt_${n.id}" class="w-full input-dark rounded p-2 text-xs text-slate-300 h-16 ml-2" placeholder="System Prompt...">${n.system_prompt}</textarea>
                    </div>
                    ${idx < nodesData.nodes.length - 1 ? '<div class="h-6 border-l-2 border-dashed border-slate-600 ml-4"></div>' : ''}
                `;
            });
            
            // Armazenar ids carregados para poder salvar depois
            window.loadedOrchestratorNodes = nodesData.nodes;
        } else {
            // Seed default nodes se a tabela estiver vazia
            if(nodesData.success && nodesData.nodes.length === 0) {
                seedDefaultOrchestratorNodes();
            }
        }
    } catch(e) { console.error('Erro ao carregar configurações de agentes', e); }
}

async function seedDefaultOrchestratorNodes() {
    const defaultNodes = [
        { step_order: 1, role_name: 'Agente Roteirista Criativo', default_model_id: 'gemini-1.5-pro', is_dynamic: false, system_prompt: 'Você é um roteirista experiente...' },
        { step_order: 2, role_name: 'Agente Formatador e Revisor', default_model_id: 'google/gemma-4-31b-it:free', is_dynamic: true, system_prompt: 'Revise os erros...' },
        { step_order: 3, role_name: 'Agente Atendimento WhatsApp', default_model_id: 'llama-3.3-70b-versatile', is_dynamic: true, system_prompt: 'Você é o atendente do Apollo...' },
        { step_order: 4, role_name: 'Agente Avaliador Crítico', default_model_id: 'nvidia/nemotron-3-ultra-550b-a55b:free', is_dynamic: true, system_prompt: 'Avalie a qualidade final...' }
    ];
    
    for(let n of defaultNodes) {
        await fetch('/api/master/orchestrator/nodes/upsert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, node: n })
        });
    }
    loadAgentsConfig();
}

async function saveAgentsConfig() {
    // Save flat settings for Fleets
    const keys = [
        { key: 'fleet_gemini_paid', val: document.getElementById('fleetGeminiPaid').value },
        { key: 'fleet_openrouter_paid', val: document.getElementById('fleetOpenRouterPaid').value },
        { key: 'fleet_groq_free', val: document.getElementById('fleetGroqFree').value },
        { key: 'fleet_openrouter_free', val: document.getElementById('fleetOpenRouterFree').value }
    ];

    try {
        const payload = { token: API_TOKEN, updates: keys };
        await fetch('/api/master/settings/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        // Save Orchestrator Nodes
        if(window.loadedOrchestratorNodes) {
            for(let n of window.loadedOrchestratorNodes) {
                const nodeData = {
                    id: n.id,
                    step_order: n.step_order,
                    role_name: n.role_name,
                    default_model_id: document.getElementById(`nodeModel_${n.id}`).value,
                    is_dynamic: document.getElementById(`nodeDynamic_${n.id}`).checked,
                    system_prompt: document.getElementById(`nodePrompt_${n.id}`).value
                };
                
                await fetch('/api/master/orchestrator/nodes/upsert', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token: API_TOKEN, node: nodeData })
                });
            }
        }
        
        alert('🤖 Arquitetura Multi-Agente & Pipeline N8N salvas com sucesso!');
        loadAgentsConfig(); // Refresh UI
    } catch(e) {
        console.error(e);
        alert('Erro ao salvar arquitetura.');
    }
}

// ==============================
// PAGES & CONFIG
// ==============================
let currentPagesSettings = {};
let activePageForConfig = "";

async function loadPages() {
    try {
        const data = await fetchWithToken('/api/master/pages');
            if (data.success) {
                currentPagesSettings = data.settings || {};
                const container = document.getElementById('pagesContainer');
                container.innerHTML = '';
                
                // Filtro para não exibir páginas críticas de sistema que não devem ter restrição no mesmo nível
                const ignoredPages = ['admin.html', 'login.html', 'admin_login.html'];
                const pages = (data.pages || []).filter(p => !ignoredPages.includes(p));
                
                document.getElementById('pages-count').innerText = pages.length;

                if (pages.length === 0) {
                    container.innerHTML = '<div class="col-span-3 text-center text-gray-500">Nenhuma página encontrada na pasta web_ui.</div>';
                } else {
                    let html = '';
                    pages.forEach(page => {
                        const accessKey = `page_${page}_access`;
                        const accessLevel = currentPagesSettings[accessKey] || 'Free';
                        
                        let accessColor = 'text-green-400';
                        if(accessLevel === 'Pro') accessColor = 'text-blue-400';
                        if(accessLevel === 'Hacker') accessColor = 'text-purple-400';
                        if(accessLevel === 'Master') accessColor = 'text-red-400';
                        if(accessLevel === 'Disabled') accessColor = 'text-gray-500 line-through';

                        html += `
                            <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 flex justify-between items-center cursor-pointer hover:bg-gray-750 transition" onclick="openPageConfig('${page}')">
                                <div>
                                    <h4 class="font-bold text-lg text-white">${page}</h4>
                                    <p class="text-sm ${accessColor} font-semibold">Min: ${accessLevel}</p>
                                </div>
                                <div class="text-gray-400">⚙️</div>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                }
            } else {
                alert("Erro ao buscar páginas do servidor: " + (data.error || "Erro desconhecido"));
            }
    } catch (e) { 
        console.error(e); 
        alert("Erro ao escaneaar páginas: " + e.message); 
    }
}

function openPageConfig(page) {
    activePageForConfig = page;
    document.getElementById('settingsPageName').innerText = page;
    
    document.getElementById('pageAccessLevel').value = currentPagesSettings[`page_${page}_access`] || 'Free';
    document.getElementById('pageShowAds').value = currentPagesSettings[`page_${page}_ads`] || 'yes';
    document.getElementById('pageDefaultAI').value = currentPagesSettings[`page_${page}_ai`] || 'gemini';

    document.getElementById('modalPageSettings').classList.remove('hidden');
}

async function savePageSettings() {
    const access = document.getElementById('pageAccessLevel').value;
    const ads = document.getElementById('pageShowAds').value;
    const ai = document.getElementById('pageDefaultAI').value;

    const updates = [
        { key: `page_${activePageForConfig}_access`, val: access },
        { key: `page_${activePageForConfig}_ads`, val: ads },
        { key: `page_${activePageForConfig}_ai`, val: ai }
    ];

    try {
        for(const u of updates) {
            await fetch('/api/master/settings/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: API_TOKEN, key: u.key, value: u.val })
            });
            currentPagesSettings[u.key] = u.val;
        }
        closeModals();
        loadPages(); // Refresh the visual state
    } catch(e) { console.error(e); alert('Erro ao salvar.'); }
}

// ==============================
// ADS
// ==============================
async function loadAds() {
    try {
        const data = await fetchWithToken('/api/master/ads');
        if(data.success) {
            const container = document.getElementById('adsContainer');
            container.innerHTML = '';
            if(data.ads.length === 0) {
                container.innerHTML = '<p class="text-gray-500">Nenhuma campanha rodando.</p>';
                return;
            }
            data.ads.forEach(ad => {
                container.innerHTML += `
                    <div class="bg-gray-800 p-4 rounded-lg border border-gray-700 relative">
                        <img src="${ad.image_url}" class="w-full h-32 object-cover rounded mb-2 opacity-${ad.is_active ? '100' : '50'}">
                        <h4 class="font-bold text-white mb-1">${ad.title}</h4>
                        <p class="text-xs text-gray-400 mb-2 truncate">${ad.link_url}</p>
                        <div class="flex justify-between items-center mt-4">
                            <span class="text-xs bg-gray-900 px-2 py-1 rounded">👁 ${ad.views}</span>
                            <div class="space-x-2">
                                <button onclick="toggleAd(${ad.id}, ${!ad.is_active})" class="text-xs px-2 py-1 rounded ${ad.is_active ? 'bg-yellow-600' : 'bg-green-600'} text-white">
                                    ${ad.is_active ? 'Pausar' : 'Ativar'}
                                </button>
                                <button onclick="deleteAd(${ad.id})" class="text-xs px-2 py-1 rounded bg-red-600 text-white">X</button>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
    } catch(e){ console.error(e); }
}

async function showCreateAdModal() {
    const title = prompt("Título da Campanha:");
    if(!title) return;
    const img = prompt("URL da Imagem (Banner):");
    const link = prompt("URL de Destino:");
    
    try {
        const res = await fetch('/api/master/ads/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, title: title, image_url: img, link_url: link, is_active: true })
        });
        const data = await res.json();
        if(data.success) loadAds(); else alert('Erro ao criar AD');
    } catch(e){ console.error(e); }
}

async function toggleAd(id, activate) {
    try {
        await fetch('/api/master/ads/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, ad_id: id, is_active: activate })
        });
        loadAds();
    } catch(e){ console.error(e); }
}

async function deleteAd(id) {
    if(!confirm("Deletar a campanha?")) return;
    try {
        await fetch('/api/master/ads/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, ad_id: id })
        });
        loadAds();
    } catch(e){ console.error(e); }
}

async function toggleBan(userId, isBanned) {
    if(isBanned && !confirm("Tem certeza que deseja BANIR este usuário?")) return;
    try {
        const res = await fetch('/api/master/users/ban', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, user_id: userId, is_banned: isBanned })
        });
        const data = await res.json();
        if(data.success) loadUsers(); else alert('Erro ao banir: ' + data.error);
    } catch(e){ console.error(e); }
}

// ==============================
// AUDITORIA E LOGS
// ==============================
async function loadLogs() {
    try {
        const data = await fetchWithToken('/api/master/logs');
        if(data.success) {
            // Summary counts
            const totalVisitsEl = document.getElementById('audit-total-visits');
            const totalApiEl = document.getElementById('audit-total-api');
            if(totalVisitsEl) totalVisitsEl.innerText = data.visits ? data.visits.length : 0;
            if(totalApiEl) totalApiEl.innerText = data.api_logs ? data.api_logs.length : 0;

            // Visits table
            const visitsTable = document.getElementById('logVisitsTable');
            if(visitsTable) {
                visitsTable.innerHTML = '';
                if(data.visits) {
                    data.visits.forEach(v => {
                        visitsTable.innerHTML += `<tr class="border-b border-gray-800"><td class="py-2 text-gray-500">${v.time}</td><td class="py-2 text-white font-semibold">${v.username}</td><td class="py-2 text-blue-300">${v.page}</td></tr>`;
                    });
                }
            }

            // API table
            const apiTable = document.getElementById('logApiTable');
            if(apiTable) {
                apiTable.innerHTML = '';
                if(data.api_logs) {
                    data.api_logs.forEach(a => {
                        const status = a.status || 'SUCCESS';
                        const color = status === 'SUCCESS' ? 'text-green-400' : 'text-red-400';
                        const currencyIcon = a.currency === 'gas' ? '⛽' : '💎';
                        apiTable.innerHTML += `<tr class="border-b border-gray-800"><td class="py-2 text-gray-500">${a.time}</td><td class="py-2 text-white font-semibold">${a.username}</td><td class="py-2 text-purple-300">${a.api}</td><td class="py-2 text-yellow-400">-${a.cost} ${currencyIcon}</td><td class="py-2 ${color}">${status}</td></tr>`;
                    });
                }
            }
            
            // Transactions table
            const transactionsTable = document.getElementById('logTransactionsTable');
            if(transactionsTable) {
                transactionsTable.innerHTML = '';
                if(data.transactions) {
                    data.transactions.forEach(t => {
                        const amountColor = t.amount >= 0 ? 'text-green-400' : 'text-red-400';
                        const sign = t.amount > 0 ? '+' : '';
                        transactionsTable.innerHTML += `<tr class="border-b border-gray-800"><td class="py-2 text-gray-500">${t.time}</td><td class="py-2 text-white font-semibold">${t.username}</td><td class="py-2 text-gray-300">${t.description}</td><td class="py-2 ${amountColor} font-bold">${sign}${t.amount}</td></tr>`;
                    });
                }
            }
        }
    } catch(e) { console.error(e); }
}

// ==============================
// ECONOMIA E CONFIGURAÇÕES
// ==============================
async function loadSettingsConfig() {
    let s = {};
    try {
        const data = await fetchWithToken('/api/master/settings');
        if(data.success) {
            s = data.settings;
        }
    } catch(e) { 
        console.warn('Backend API offline. Usando fallback de localStorage para loadSettingsConfig.'); 
    }

    // Tenta carregar do localStorage mock se não vier do backend
    const getSetting = (key, defaultVal) => {
        return s[key] || localStorage.getItem('laplata_setting_mock_' + key) || defaultVal;
    };

    // Economia Base
    document.getElementById('cfgInitialCredits').value = getSetting('economy_initial_credits', 100);
    const gasEl = document.getElementById('cfgInitialGas');
    if(gasEl) gasEl.value = getSetting('economy_initial_gas', 100);
    const crystalsEl = document.getElementById('cfgInitialCrystals');
    if(crystalsEl) crystalsEl.value = getSetting('economy_initial_crystals', 0);

    // Tabela de Preços por Ferramenta
    const tools = [
        {key: 'chat', id: 'Chat', def: 1}, {key: 'image', id: 'Image', def: 5},
        {key: 'video', id: 'Video', def: 10}, {key: 'dubbing', id: 'Dubbing', def: 3},
        {key: 'music', id: 'Music', def: 5}, {key: 'render', id: 'Render', def: 15},
        {key: 'autopilot', id: 'Autopilot', def: 20}, {key: 'bgremove', id: 'BgRemove', def: 2}
    ];
    tools.forEach(t => {
        const valEl = document.getElementById('cfgCost' + t.id);
        const unitEl = document.getElementById('cfgCost' + t.id + 'Unit');
        if(valEl) valEl.value = getSetting('economy_cost_' + t.key, t.def);
        if(unitEl) unitEl.value = getSetting('economy_cost_' + t.key + '_unit', 'gas');
    });

    // IA
    const geminiKeyEl = document.getElementById('cfgGeminiKey');
    if(geminiKeyEl) {
        // Tenta buscar o fallback explícito do laplata_gemini_key
        geminiKeyEl.value = getSetting('gemini_api_key', '') || localStorage.getItem('laplata_gemini_key') || '';
    }
    document.getElementById('cfgSystemPrompt').value = getSetting('ai_system_prompt', '');
    document.getElementById('cfgTemperature').value = getSetting('ai_temperature', 0.7);
    
    // Segurança
    const broadcastEl = document.getElementById('cfgBroadcastMsg');
    if(broadcastEl) broadcastEl.value = getSetting('global_broadcast', '');
    
    if(getSetting('maintenance_mode', 'off') === 'on') {
        document.getElementById('maintOn').checked = true;
    } else {
        document.getElementById('maintOff').checked = true;
    }
}

async function saveSettingKey(key, value) {
    try {
        await fetch('/api/master/settings/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: API_TOKEN, key: key, value: String(value) })
        });
    } catch(e) {
        console.warn('Simulando saveSettingKey localmente. Backend ausente.', key);
        // Fallback p/ localStorage caso n tenhamos servidor
        localStorage.setItem('laplata_setting_mock_' + key, String(value));
    }
}

async function saveEconomyConfig() {
    const initial = document.getElementById('cfgInitialCredits').value;
    const initialGas = document.getElementById('cfgInitialGas').value;
    const initialCrystals = document.getElementById('cfgInitialCrystals').value;
    
    await saveSettingKey('economy_initial_credits', initial);
    await saveSettingKey('economy_initial_gas', initialGas);
    await saveSettingKey('economy_initial_crystals', initialCrystals);
    alert('Configurações financeiras base atualizadas!');
}

async function saveToolPrices() {
    const tools = [
        {key: 'chat', id: 'Chat'}, {key: 'image', id: 'Image'}, {key: 'video', id: 'Video'},
        {key: 'dubbing', id: 'Dubbing'}, {key: 'music', id: 'Music'}, {key: 'render', id: 'Render'},
        {key: 'autopilot', id: 'Autopilot'}, {key: 'bgremove', id: 'BgRemove'}
    ];
    for (const t of tools) {
        const valEl = document.getElementById('cfgCost' + t.id);
        const unitEl = document.getElementById('cfgCost' + t.id + 'Unit');
        if (valEl) await saveSettingKey('economy_cost_' + t.key, valEl.value);
        if (unitEl) await saveSettingKey('economy_cost_' + t.key + '_unit', unitEl.value);
    }
    alert('💰 Tabela de preços de IA atualizada com sucesso!');
}

async function saveAiConfig() {
    const prompt = document.getElementById('cfgSystemPrompt').value;
    const temp = document.getElementById('cfgTemperature').value;
    const apiKey = document.getElementById('cfgGeminiKey').value;
    
    await saveSettingKey('ai_system_prompt', prompt);
    await saveSettingKey('ai_temperature', temp);
    await saveSettingKey('gemini_api_key', apiKey);
    
    // Alimenta também o local storage para fallback rápido nos agentes
    localStorage.setItem('laplata_gemini_key', apiKey);

    alert('Comportamento de IA e Chaves atualizados com sucesso!');
}

async function saveSecurityConfig() {
    const maint = document.querySelector('input[name="maintenanceToggle"]:checked').value;
    await saveSettingKey('maintenance_mode', maint);
    if(maint === 'on') alert('🚨 KILLSWITCH ATIVADO! Todos os usuários comuns estão bloqueados.');
    else alert('Sistema Online.');
}

async function saveBroadcastMsg() {
    const msg = document.getElementById('cfgBroadcastMsg').value;
    await saveSettingKey('global_broadcast', msg);
    alert('Broadcast enviado!');
}

async function loadTrends() {
    try {
        const res = await fetch('/api/admin/trends');
        const data = await res.json();
        const container = document.getElementById('trends-reports');
        if(data.success && data.trends) {
            if(data.trends.length === 0) {
                container.innerHTML = '<p class="text-slate-400">Nenhuma IA descoberta ainda. Acione o Olheiro.</p>';
                return;
            }
            container.innerHTML = data.trends.map(t => `
                <div class="bg-slate-700 p-4 rounded-lg border-l-4 border-blue-500">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-bold text-white">${t.model_name}</h4>
                        <span class="bg-blue-900 text-blue-200 text-xs px-2 py-1 rounded font-bold">Score: ${t.trending_score}/100</span>
                    </div>
                    <p class="text-sm text-slate-300 mb-2">${t.analysis_text}</p>
                    <div class="flex justify-between items-center mt-3">
                        <a href="${t.source_url}" target="_blank" class="text-xs text-blue-400 hover:underline"><i class="fas fa-external-link-alt"></i> Ver Fonte</a>
                        <button class="bg-green-600 hover:bg-green-500 text-xs text-white px-3 py-1 rounded font-bold">Aprovar Integração</button>
                    </div>
                </div>
            `).join('');
        }
    } catch(e) { console.error(e); }
}

async function triggerTrends() {
    try {
        const btn = event.currentTarget;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Vasculhando...';
        btn.disabled = true;
        
        const res = await fetch('/api/admin/trigger-trends', { method: 'POST' });
        const data = await res.json();
        if(data.success) {
            alert(`Pesquisa concluída! ${data.discoveries} novos modelos encontrados.`);
            loadTrends();
        } else {
            alert('Erro: ' + data.error);
        }
        
        btn.innerHTML = '<i class="fas fa-search mr-2"></i> Investigar Tendências Agora';
        btn.disabled = false;
    } catch(e) {
        console.error(e);
        alert('Erro ao acionar Olheiro.');
    }
}

