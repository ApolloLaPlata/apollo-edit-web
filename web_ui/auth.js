// auth.js - Gerenciamento de Estado e Login via Supabase

// ATENÇÃO: Substitua pelos dados do seu projeto Supabase
const SUPABASE_URL = 'https://vtqzrssddtjzdzrdiplg.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_BF25laxmROr0uVsn8v_m0g_KqHembqT';

// Inicializa o cliente global (Certifique-se de importar o SDK no HTML antes deste script)
// ex: <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
const supabase = window.supabase ? window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY) : null;

async function checkAuthStatus() {
    if (!supabase) return null;
    const { data: { session } } = await supabase.auth.getSession();
    return session?.user || null;
}

async function requireAuth() {
    const user = await checkAuthStatus();
    if (!user) {
        // Se não tiver logado e não estiver na página de login, redireciona.
        if (!window.location.pathname.includes('login.html')) {
            window.location.href = 'login.html';
        }
        return null;
    } else {
        // Atualiza a interface (Avatar, Email, Créditos) se os elementos existirem
        const userNameEl = document.getElementById('user-name');
        if (userNameEl) {
            userNameEl.innerText = user.email.split('@')[0];
        }
        return user;
    }
        
        // Exemplo: Buscar saldo na tabela wallets
        // const { data } = await supabase.from('wallets').select('credits').eq('user_id', user.id).single();
        // if (data) document.getElementById('credit-value').innerText = data.credits;
    }
}

async function loadWebUserProfile() {
    try {
        const response = await fetch('https://api.apolloedit.com/api/user/profile');
        const data = await response.json();
        
        // FASE 4: Bloqueios e Globais (Banimento e Manutenção)
        if (data.is_banned) {
            document.body.innerHTML = `
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; background:#000; color:#fff; text-align:center; padding:20px; z-index:999999999; position:fixed; top:0; left:0; width:100vw;">
                    <h1 style="color:#ef4444; font-size:3rem; font-family:'Bangers', cursive; margin-bottom:10px;">ACESSO BLOQUEADO</h1>
                    <p style="font-size:1.2rem; color:#aaa; max-width:500px;">Sua conta foi suspensa por violação dos termos de uso ou pendência administrativa. Entre em contato com o suporte para mais informações.</p>
                </div>
            `;
            return true;
        }

        if (data.module_settings) {
            if (data.module_settings.maintenance_mode === 'on' && !data.is_master) {
                document.body.innerHTML = `
                    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; background:#111; color:#fff; text-align:center; padding:20px; z-index:999999999; position:fixed; top:0; left:0; width:100vw;">
                        <h1 style="color:#facc15; font-size:3rem; font-family:'Bangers', cursive; margin-bottom:10px;">🛠️ MANUTENÇÃO PROGRAMADA 🛠️</h1>
                        <p style="font-size:1.2rem; color:#aaa; max-width:500px;">O Apollo Edit está passando por atualizações. Voltaremos em breve!</p>
                    </div>
                `;
                return true;
            }

            if (data.module_settings.global_broadcast && data.module_settings.global_broadcast.trim().length > 0) {
                const banner = document.createElement('div');
                banner.style.background = 'linear-gradient(90deg, #f59e0b, #ef4444)';
                banner.style.color = '#fff';
                banner.style.textAlign = 'center';
                banner.style.padding = '8px 15px';
                banner.style.fontSize = '14px';
                banner.style.fontWeight = 'bold';
                banner.style.position = 'fixed';
                banner.style.top = '0';
                banner.style.left = '0';
                banner.style.width = '100%';
                banner.style.zIndex = '99999999';
                banner.style.boxShadow = '0 2px 10px rgba(0,0,0,0.5)';
                banner.innerHTML = `⚠️ <strong>AVISO GLOBAL:</strong> ${data.module_settings.global_broadcast} <span style="float:right; cursor:pointer;" onclick="this.parentElement.remove()">X</span>`;
                document.body.appendChild(banner);
            }
        }
        
        // 1. Atualizar créditos (Gasolina) se existir o elemento no Header
        const creditsEl = document.getElementById('user-credits');
        if (creditsEl) {
            creditsEl.innerText = Number(data.credits).toLocaleString('pt-BR');
        }

        // 2. Atualizar Avatar Gamificado e Ranks no Header
        const avatarContainer = document.querySelector('.avatar-container');
        
        // Inicializar Cristais no localStorage para persistência local (mock shop)
        let currentCrystals = localStorage.getItem('apollo_mock_crystals');
        if (currentCrystals === null) {
            currentCrystals = data.cristais !== undefined ? data.cristais : 12;
            localStorage.setItem('apollo_mock_crystals', currentCrystals);
        } else {
            currentCrystals = parseInt(currentCrystals);
        }

        // Atualiza display de cristais na página de perfil
        const crystalBalanceEl = document.getElementById('crystal-balance');
        if (crystalBalanceEl) {
            crystalBalanceEl.innerText = `${currentCrystals} Cristais`;
        }

        if (avatarContainer) {
            // Determinar raridade do Card ou Cosmético Equipado
            let rarityClass = 'rarity-common';
            if (data.is_master) rarityClass = 'rarity-master';
            else if (data.is_pro) rarityClass = 'rarity-pro';
            
            const equippedCosmetic = localStorage.getItem('apollo_equipped_cosmetic');
            if (equippedCosmetic && equippedCosmetic !== 'nenhum') {
                rarityClass = equippedCosmetic;
            }
            
            // Determinar texto de Nível
            let userLevel = data.level || 15;
            
            // Remover avatar antigo se existir, e inserir o RPG Card
            const oldAvatar = avatarContainer.querySelector('.avatar') || avatarContainer.querySelector('.avatar-rpg-card');
            if (oldAvatar) {
                // Criar o RPG Avatar Card
                const rpgCard = document.createElement('div');
                rpgCard.className = `avatar-rpg-card ${rarityClass}`;
                rpgCard.style.width = '40px'; // Header size
                rpgCard.style.height = '40px';
                rpgCard.style.marginRight = '12px'; // align correctly
                rpgCard.title = `${data.is_master ? 'MASTER' : (data.is_pro ? 'PRO' : 'FREE')} (Nível ${userLevel})`;
                
                rpgCard.innerHTML = `
                    <div class="rpg-level-banner" style="font-size: 6px; top: -5px; padding: 0px 3px;">Lv.${userLevel}</div>
                    <img src="${data.avatar || 'assets/mascote.png'}" class="avatar-img-rpg" alt="Avatar">
                    <div class="corner-badge mini hacker-badge ${data.is_hacker ? '' : 'locked'}" 
                         style="top:-4px; left:-4px; font-size:7px; width:12px; height:12px;" 
                         id="hdr-hacker-badge"
                         title="${data.is_hacker ? 'Hacker Licenciado ⚙️' : 'Acesso Hacker Bloqueado 🔒 - Clique p/ liberar'}">
                        ${data.is_hacker ? '⚙️' : '🔒'}
                    </div>
                    <div class="corner-badge mini flag-badge" 
                         style="bottom:-4px; left:-4px; font-size:8px; width:12px; height:12px; background:#000; border-radius:50%;" 
                         title="País: ${data.pais === 'BR' || !data.pais ? 'Brasil' : data.pais}">
                        🇧🇷
                    </div>
                    <div class="corner-badge mini rank-badge" 
                         style="bottom:-4px; right:-4px; font-size:7px; width:12px; height:12px;" 
                         title="Rank Global: ${data.rank_global || '#1'}">
                        <span>${data.rank_global || '#1'}</span>
                    </div>
                `;
                
                // Add click event for locked hacker badge to open pitch modal
                const hkBadge = rpgCard.querySelector('#hdr-hacker-badge');
                if (hkBadge) {
                    hkBadge.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        showHackerUpsellModal();
                    });
                }
                
                oldAvatar.replaceWith(rpgCard);
            }
        }

        // 3. Atualizar Nome e Badges no Header
        const userNameEl = document.getElementById('user-name');
        if (userNameEl) {
            // Construir badges com efeitos de luz (glowing)
            let badgesHTML = '';
            
            if (data.is_hacker) {
                badgesHTML += `<span style="background: rgba(155, 89, 182, 0.2); color: #c084fc; border: 1px solid #9B59B6; font-size: 10px; padding: 2px 5px; border-radius: 4px; font-weight: bold; text-shadow: 0 0 5px rgba(155, 89, 182, 0.5); margin-left: 5px; display: inline-flex; align-items: center; gap: 2px;">⚙️ HACKER</span>`;
            }
            if (data.is_pro) {
                badgesHTML += `<span style="background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid #fbbf24; font-size: 10px; padding: 2px 5px; border-radius: 4px; font-weight: bold; text-shadow: 0 0 5px rgba(251, 191, 36, 0.5); margin-left: 5px; display: inline-flex; align-items: center; gap: 2px;">👑 PRO</span>`;
            }
            if (data.is_master) {
                badgesHTML += `<span style="background: rgba(6, 182, 212, 0.2); color: #22d3ee; border: 1px solid #06b6d4; font-size: 10px; padding: 2px 5px; border-radius: 4px; font-weight: bold; text-shadow: 0 0 5px rgba(6, 182, 212, 0.5); margin-left: 5px; display: inline-flex; align-items: center; gap: 2px;">⚡ MASTER</span>`;
            }

            // Construir subtítulo com base no nível/tipo
            let subtitle = 'Piloto Comum';
            if (data.is_master && data.is_hacker) subtitle = 'Hacker Master (Elite)';
            else if (data.is_master) subtitle = 'Mestre da Oficina';
            else if (data.is_pro) subtitle = 'Piloto de Elite';
            else if (data.is_hacker) subtitle = 'Engenheiro de Elite';

            userNameEl.innerHTML = `
                <strong style="font-size:14px; color: #fff; display: flex; align-items: center; gap: 2px;">
                    ${data.name} ${badgesHTML}
                </strong>
                <span style="color: #aaa; font-size:11px; margin-top: 2px;">${subtitle}</span>
            `;
        }

        // 4. Atualizar elementos da página perfil.html se ela for a ativa
        const lblName = document.getElementById('lbl-name');
        if (lblName) {
            lblName.innerText = data.name;
        }

        const avatarFrame = document.getElementById('avatar-frame');
        if (avatarFrame) {
            // Determinar raridade do Card ou Cosmético Equipado
            let rarityClass = 'rarity-common';
            if (data.is_master) rarityClass = 'rarity-master';
            else if (data.is_pro) rarityClass = 'rarity-pro';
            
            const equippedCosmetic = localStorage.getItem('apollo_equipped_cosmetic');
            if (equippedCosmetic && equippedCosmetic !== 'nenhum') {
                rarityClass = equippedCosmetic;
            }
            
            let userLevel = data.level || 15;
            
            // Criar o RPG Card Grande
            avatarFrame.className = `avatar-rpg-card large ${rarityClass}`;
            avatarFrame.style.background = 'none'; // reset background color
            avatarFrame.style.border = 'none';
            avatarFrame.style.boxShadow = 'none';
            avatarFrame.style.width = '250px';
            avatarFrame.style.height = '250px';
            
            avatarFrame.innerHTML = `
                <div class="rpg-level-banner">Lv.${userLevel}</div>
                <img src="${data.avatar || 'assets/mascote.png'}" id="avatar-img" class="avatar-img-rpg" alt="Avatar">
                <div class="scanning-line" id="scanning-line" style="display:none;"></div>
                
                <!-- Quinas Grandes -->
                <div class="corner-badge hacker-badge ${data.is_hacker ? '' : 'locked'}" 
                     id="large-hacker-badge"
                     style="background: ${data.is_hacker ? 'linear-gradient(135deg, #a855f7, #6b21a8)' : 'linear-gradient(135deg, #475569, #1e293b)'}; border-radius:50%;"
                     title="${data.is_hacker ? 'Hacker Licenciado ⚙️' : 'Acesso Hacker Bloqueado 🔒 - Clique p/ liberar'}">
                    ${data.is_hacker ? '⚙️' : '🔒'}
                </div>
                <div class="corner-badge flag-badge" style="background:#000; border-radius:50%;" title="País: Brasil">
                    🇧🇷
                </div>
                <div class="corner-badge rank-badge" title="Rank Global: ${data.rank_global || '#1'}">
                    <span>${data.rank_global || '#1'}</span>
                </div>
                <div class="badge-edge-right" title="Upgrade de Tier / Customizações disponíveis!" onclick="showSaaSPricingModal()">▲</div>
            `;
            
            // Adicionar evento para badge hacker grande
            const lghkBadge = avatarFrame.querySelector('#large-hacker-badge');
            if (lghkBadge) {
                lghkBadge.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    showHackerUpsellModal();
                });
            }
        }
        
        const statRows = document.querySelectorAll('.stat-row');
        statRows.forEach(row => {
            if (row.innerHTML.includes('NÍVEL:')) {
                let lvlName = 'Piloto Comum';
                if (data.is_master && data.is_hacker) lvlName = '<span style="color:#c084fc;">Hacker Master</span> (Lv. Max)';
                else if (data.is_master) lvlName = '<span style="color:#22d3ee;">Mestre da Oficina</span> (Lv. 50)';
                else if (data.is_pro) lvlName = '<span style="color:#fbbf24;">Piloto Pro</span> (Lv. 15)';
                else if (data.is_hacker) lvlName = '<span style="color:#c084fc;">Hacker</span> (Lv. 30)';
                
                row.querySelector('span:last-child').innerHTML = lvlName;
            }
            if (row.innerHTML.includes('XP (Gasolina Gasta):')) {
                row.querySelector('span:last-child').innerText = Number(data.xp_litros).toLocaleString('pt-BR') + ' L';
            }
        });
        
        // FASE 37: Aplicar permissões de módulos com base no cargo (Role-based access)
        applyModulePermissions(data);

        return false; // Indica que não foi bloqueado
    } catch (e) {
        console.error("Erro ao carregar perfil do Apollo:", e);
        return false;
    }
}

function applyModulePermissions(data) {
    if (!data.module_settings) return;

    const moduleMap = {
        'module_copilots': 'a[href="copilotos.html"]',
        'module_vestiary': 'a[href="perfil.html"]',
        'module_tank': 'a[href="tanque.html"]',
        'module_workshop': 'a[href="oficina.html"]',
        'module_farm': 'a[href="fila.html"]',
        'module_music': 'a[href="musica.html"]',
        'module_mapper': 'a[href="noticias_timeline.html"]',
        'module_quests': '#btn-quests-floating'
    };

    let userLevel = 0;
    if (data.is_hacker) userLevel = 1;
    if (data.is_master) userLevel = 2; // Master is highest

    for (const [modId, selector] of Object.entries(moduleMap)) {
        const reqAccess = data.module_settings[`${modId}_access`] || 'User';
        let reqLevel = 0;
        if (reqAccess === 'Hacker') reqLevel = 1;
        if (reqAccess === 'Master') reqLevel = 2;
        if (reqAccess === 'Disabled') reqLevel = 99; // Only disabled

        const el = document.querySelector(selector);
        if (el) {
            if (userLevel < reqLevel) {
                // Bloquear visualmente e impedir clique
                el.style.opacity = '0.4';
                el.style.pointerEvents = 'none';
                el.style.filter = 'grayscale(100%)';
                el.style.position = 'relative';
                
                // Add lock icon if not already present
                if (!el.querySelector('.module-lock-icon')) {
                    const lock = document.createElement('div');
                    lock.className = 'module-lock-icon';
                    lock.innerHTML = '🔒';
                    lock.style.position = 'absolute';
                    lock.style.top = '5px';
                    lock.style.right = '5px';
                    lock.style.fontSize = '1.2rem';
                    lock.style.zIndex = '10';
                    el.appendChild(lock);
                }
            } else {
                // Liberar (caso estivesse bloqueado por um state anterior, though unlikely to happen dynamically here)
                el.style.opacity = '1';
                el.style.pointerEvents = 'auto';
                el.style.filter = 'none';
                const lock = el.querySelector('.module-lock-icon');
                if (lock) lock.remove();
            }
        }
    }
}

/* =========================================
   HACKER UPSELL MODAL & SAAS UPGRADES
   ========================================= */
function showHackerUpsellModal() {
    let modal = document.getElementById('hacker-upsell-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'hacker-upsell-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.background = 'rgba(19, 10, 42, 0.95)';
        modal.style.backdropFilter = 'blur(10px)';
        modal.style.zIndex = '9999999';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.overflowY = 'auto';
        
        const style = document.createElement('style');
        style.innerHTML = `
            .upsell-card {
                background: linear-gradient(135deg, #1e0b3b 0%, #2e1065 50%, #4c1d95 100%);
                border: 4px solid #a855f7;
                box-shadow: 0 0 30px rgba(168, 85, 247, 0.6), 0 10px 0 #000;
                border-radius: 24px;
                width: 550px;
                max-width: 90%;
                padding: 40px;
                text-align: center;
                position: relative;
                color: #fff;
            }
            .upsell-title {
                font-family: 'Bangers', cursive;
                font-size: 3.2rem;
                color: #facc15;
                text-shadow: 3px 3px 0 #000, 0 0 15px rgba(250, 204, 21, 0.5);
                margin-bottom: 5px;
                letter-spacing: 2px;
            }
            .hacker-badge-stamp {
                background: #a855f7;
                color: #fff;
                font-family: 'Bangers', cursive;
                font-size: 1.5rem;
                padding: 5px 20px;
                border-radius: 12px;
                border: 3px solid #000;
                box-shadow: 0 4px 0 #000;
                display: inline-block;
                transform: rotate(-3deg);
                margin-bottom: 20px;
                text-shadow: 2px 2px 0 #000;
            }
            .feature-list {
                text-align: left;
                margin: 25px 0;
                background: rgba(0,0,0,0.4);
                padding: 20px;
                border-radius: 16px;
                border: 1px solid #4c1d95;
            }
            .feature-item {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
                font-weight: 800;
                color: #cbd5e1;
                text-shadow: 1px 1px 0 #000;
            }
            .feature-item:last-child {
                margin-bottom: 0;
            }
            .feature-icon {
                font-size: 1.5rem;
                filter: drop-shadow(0 2px 0 #000);
            }
            .price-tag-hacker {
                font-family: 'Bangers', cursive;
                font-size: 2.2rem;
                color: #4ade80;
                text-shadow: 2px 2px 0 #000;
                margin: 15px 0;
            }
            .upsell-close {
                position: absolute;
                top: -15px;
                right: -15px;
                background: #f87171;
                border: 4px solid #000;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                color: #fff;
                font-family: 'Bangers', cursive;
                font-size: 1.5rem;
                cursor: pointer;
                box-shadow: 0 4px 0 #000;
                transition: transform 0.1s;
                z-index: 999;
            }
            .upsell-close:active {
                transform: translateY(4px);
                box-shadow: 0 0px 0 #000;
            }
        `;
        document.head.appendChild(style);
        
        modal.innerHTML = `
            <div class="upsell-card">
                <button class="upsell-close" onclick="document.getElementById('hacker-upsell-modal').style.display='none'">X</button>
                <h2 class="upsell-title">ACESSO HACKER</h2>
                <div class="hacker-badge-stamp">⚡ CURSO DE INFRA E AUTOMAÇÃO 💻</div>
                <p style="font-size:1.1rem; font-weight:800; text-shadow:1px 1px 0 #000; color:#fff; margin-bottom:15px;">
                    Quer rodar o Apollo Edit com <strong style="color:var(--btn-yellow);">CUSTO DE SERVIDOR R$ 0,00</strong> gerando áudio e vídeo ilimitado?
                </p>
                <p style="font-size:0.95rem; color:#cbd5e1; font-weight:700;">
                    Ao adquirir nosso curso completo de R$ 400, você aprende a instalar e configurar o ecossistema local na sua máquina com Pinokio, RVC de voz e conexões BYOK!
                </p>
                
                <div class="feature-list">
                    <div class="feature-item">
                        <span class="feature-icon">⚙️</span>
                        <span><strong>BYOK Inteligente:</strong> Insira suas próprias chaves e gaste $0 em servidores.</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">🎙️</span>
                        <span><strong>Clonagem RVC local:</strong> Treinamento de voz e imitação perfeita de timbres.</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">💻</span>
                        <span><strong>Configuração Estendida:</strong> Desbloqueie roteamentos, chaves e conexões de porta locais.</span>
                    </div>
                    <div class="feature-item">
                        <span class="feature-icon">👑</span>
                        <span><strong>Status na Comunidade:</strong> Ganhe a badge roxa de Hacker exclusiva no perfil e quina do avatar.</span>
                    </div>
                </div>
                
                <div class="price-tag-hacker">
                    R$ 400 <span style="font-size:1rem; color:#aaa;">(Vitalício Curso + 1 ano Status Badge)</span>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:5px;">Renovação da badge por R$ 200/ano</div>
                </div>
                
                <button class="btn yellow" style="width:100%; font-size:1.6rem; animation: pulse 2s infinite;" onclick="buyHackerCourse()">
                    ⚡ QUERO SER HACKER (ADQUIRIR AGORA)
                </button>
            </div>
        `;
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';
}

function buyHackerCourse() {
    alert("🚀 Redirecionando para o Checkout de R$ 400 (Educação + Upgrade de Conta Hacker)!\n\nApós o pagamento, o sistema irá liberar as ferramentas extensas de API BYOK, roteamento e seu selo Hacker estará ativo por 1 ano.");
    document.getElementById('hacker-upsell-modal').style.display = 'none';
}

function showSaaSPricingModal() {
    let modal = document.getElementById('saas-pricing-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'saas-pricing-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.background = 'rgba(19, 10, 42, 0.95)';
        modal.style.backdropFilter = 'blur(10px)';
        modal.style.zIndex = '9999999';
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        modal.style.overflowY = 'auto';
        
        const style = document.createElement('style');
        style.innerHTML = `
            .pricing-container {
                background: linear-gradient(135deg, #130a2a 0%, #1e1b4b 100%);
                border: 4px solid #3b82f6;
                box-shadow: 0 0 30px rgba(59, 130, 246, 0.6), 0 10px 0 #000;
                border-radius: 24px;
                width: 800px;
                max-width: 95%;
                padding: 40px;
                text-align: center;
                position: relative;
                color: #fff;
            }
            .pricing-title {
                font-family: 'Bangers', cursive;
                font-size: 3rem;
                color: #22d3ee;
                text-shadow: 3px 3px 0 #000;
                margin-bottom: 20px;
            }
            .pricing-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 25px;
                margin: 20px 0;
            }
            .pricing-card {
                background: rgba(0,0,0,0.4);
                border: 3px solid #333;
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                transition: all 0.2s;
                position: relative;
                overflow: hidden;
            }
            .pricing-card:hover {
                transform: translateY(-5px);
            }
            .pricing-card.pro {
                border-color: #facc15;
                box-shadow: 0 0 15px rgba(250, 204, 21, 0.3);
            }
            .pricing-card.master {
                border-color: #22d3ee;
                box-shadow: 0 0 15px rgba(34, 211, 238, 0.3);
            }
            .pricing-card-title {
                font-family: 'Bangers', cursive;
                font-size: 2.2rem;
                margin-bottom: 10px;
                letter-spacing: 1px;
            }
            .pricing-card.pro .pricing-card-title { color: #facc15; }
            .pricing-card.master .pricing-card-title { color: #22d3ee; }
            
            .pricing-price {
                font-size: 2rem;
                font-weight: 900;
                color: #fff;
                margin-bottom: 15px;
                text-shadow: 1px 1px 0 #000;
            }
            .pricing-features {
                text-align: left;
                margin-bottom: 20px;
                font-size: 0.9rem;
                color: #cbd5e1;
                font-weight: 700;
                line-height: 1.5;
            }
            .pricing-feature-line {
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
        `;
        document.head.appendChild(style);
        
        modal.innerHTML = `
            <div class="pricing-container">
                <button class="upsell-close" onclick="document.getElementById('saas-pricing-modal').style.display='none'">X</button>
                <h2 class="pricing-title">UPGRADE DE PLANO</h2>
                <p style="font-weight:800; color:#cbd5e1; margin-bottom:20px; text-shadow:1px 1px 0 #000;">
                    Adquira cotas extras de processamento em nuvem e mostre seu poder com bordinhas exclusivas!
                </p>
                
                <div class="pricing-grid">
                    <!-- PRO -->
                    <div class="pricing-card pro">
                        <h3 class="pricing-card-title">👑 PLANO PRO</h3>
                        <div class="pricing-price">R$ 49 <span style="font-size:0.9rem; color:#aaa;">/ mês</span></div>
                        
                        <div class="pricing-features">
                            <div class="pricing-feature-line">✨ Borda Dourada Épica (Gold Frame)</div>
                            <div class="pricing-feature-line">⛽ 5.000 L de Gasolina de Render</div>
                            <div class="pricing-feature-line">🤖 Acesso total ao Diretor de IA V2</div>
                            <div class="pricing-feature-line">⚡ Prioridade média na Fila de Render</div>
                        </div>
                        
                        <button class="btn yellow" style="width:100%;" onclick="alert('Assinando Plano PRO!')">ASSINAR PRO</button>
                    </div>
                    
                    <!-- MASTER -->
                    <div class="pricing-card master">
                        <div style="position:absolute; top:12px; right:-25px; background:#e11d48; color:#fff; font-family:'Bangers'; padding:3px 25px; transform:rotate(45deg); font-size:0.7rem; font-weight:bold; box-shadow:0 2px 4px rgba(0,0,0,0.5);">DOBRO!</div>
                        <h3 class="pricing-card-title">⚡ PLANO MASTER</h3>
                        <div class="pricing-price">R$ 98 <span style="font-size:0.9rem; color:#aaa;">/ mês</span></div>
                        
                        <div class="pricing-features">
                            <div class="pricing-feature-line">💎 Borda Neon Ciano Lendária (Legendary)</div>
                            <div class="pricing-feature-line">⛽ 12.000 L de Gasolina de Render (O Dobro!)</div>
                            <div class="pricing-feature-line">🏎️ Skins e Trajes Lendários de Vestiário</div>
                            <div class="pricing-feature-line">🚀 Prioridade Máxima Instantânea no Render</div>
                        </div>
                        
                        <button class="btn" style="width:100%; background:var(--btn-blue); border-color:#000;" onclick="alert('Assinando Plano MASTER!')">ASSINAR MASTER</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';
}

// Verifica na inicialização da página
document.addEventListener('DOMContentLoaded', async () => {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    if(currentPage === 'admin.html' || currentPage === 'admin_login.html') return;

    // Carregar informações do perfil unificado E checar bloqueios
    const isBlocked = await loadWebUserProfile();
    if (isBlocked) return; // Halt execution if banned or in maintenance

    let user = null;
    if (window.location.pathname.includes('hub.html')) {
        user = await requireAuth();
    }
    
    // FASE 38: Registrar Visita, Checar Acesso e Renderizar Ads
    checkPageAccessAndLog();

    // FASE 34: Injeção do Master Toggle Button no HUD (Dev Tools)
    injectDevModeToggle();

    // FASE 36: Tintura Temática (Theme Tinting)
    applyChannelTheme();
});

async function checkPageAccessAndLog() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    if(currentPage === 'admin.html' || currentPage === 'login.html') return;

    try {
        const response = await fetch('https://api.apolloedit.com/api/log_visit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ page_name: currentPage })
        });
        const data = await response.json();
        
        if (data.settings) {
            // Verifica permissão da página inteira
            const reqAccess = data.settings[`page_${currentPage}_access`] || 'Free';
            if (reqAccess !== 'Free') {
                const profileRes = await fetch('https://api.apolloedit.com/api/user/profile');
                const profileData = await profileRes.json();
                
                let userLevel = 0;
                if (profileData.is_pro) userLevel = 1;
                if (profileData.is_hacker) userLevel = 2;
                if (profileData.is_master) userLevel = 3;

                let reqLevel = 0;
                if (reqAccess === 'Pro') reqLevel = 1;
                if (reqAccess === 'Hacker') reqLevel = 2;
                if (reqAccess === 'Master') reqLevel = 3;
                if (reqAccess === 'Disabled') reqLevel = 99;

                if (userLevel < reqLevel) {
                    alert(`ACESSO NEGADO: Esta página requer nível ${reqAccess}.`);
                    window.location.href = '/hub.html';
                    return;
                }
            }

            // Verifica se exibe Ads
            const showAds = data.settings[`page_${currentPage}_ads`] !== 'no';
            if (showAds) {
                renderAds();
            }
        }
    } catch(e) { console.error("Erro ao registrar acesso", e); }
}

async function renderAds() {
    try {
        const res = await fetch('https://api.apolloedit.com/api/public/ads');
        const data = await res.json();
        if(data.success && data.ads.length > 0) {
            // Escolhe um AD aleatório ativo
            const ad = data.ads[Math.floor(Math.random() * data.ads.length)];
            
            // Cria div de anúncio no canto inferior direito
            const adDiv = document.createElement('div');
            adDiv.className = 'floating-ad';
            adDiv.style.position = 'fixed';
            adDiv.style.bottom = '20px';
            adDiv.style.right = '20px';
            adDiv.style.width = '300px';
            adDiv.style.background = '#1e1b4b';
            adDiv.style.border = '2px solid #a855f7';
            adDiv.style.borderRadius = '12px';
            adDiv.style.boxShadow = '0 10px 25px rgba(0,0,0,0.8)';
            adDiv.style.zIndex = '999998';
            adDiv.style.overflow = 'hidden';
            adDiv.style.cursor = 'pointer';
            
            adDiv.innerHTML = `
                <div style="position: absolute; top: 0; right: 0; background: rgba(0,0,0,0.8); color: white; padding: 2px 8px; font-size: 10px; z-index: 10;">Patrocinado</div>
                <button onclick="event.stopPropagation(); this.parentElement.remove()" style="position: absolute; top: 0; left: 0; background: red; color: white; border: none; padding: 2px 8px; font-size: 10px; z-index: 10; cursor: pointer;">X</button>
                <img src="${ad.image_url}" style="width: 100%; height: 120px; object-fit: cover;">
                <div style="padding: 10px;">
                    <h4 style="color: white; font-size: 14px; margin: 0; font-family: 'Bangers', cursive; letter-spacing: 1px;">${ad.title}</h4>
                </div>
            `;
            
            adDiv.onclick = () => window.open(ad.link_url, '_blank');
            document.body.appendChild(adDiv);
        }
    } catch(e) { console.error(e); }
}

function applyChannelTheme() {
    const activeId = localStorage.getItem('apollo_active_channel_id');
    if (!activeId) return;

    const channels = JSON.parse(localStorage.getItem('apollo_channels')) || [];
    const activeCh = channels.find(c => c.id === activeId);

    if (activeCh && activeCh.color) {
        // Inject global CSS variables for the color
        document.documentElement.style.setProperty('--btn-purple', activeCh.color);
        // Add a subtle radial gradient overlay to the body to tint the entire app
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100vw';
        overlay.style.height = '100vh';
        overlay.style.pointerEvents = 'none'; // click-through
        overlay.style.zIndex = '1';
        // 5% opacity tint over everything
        overlay.style.background = `radial-gradient(circle at center, transparent 30%, ${activeCh.color}11 100%)`;
        document.body.appendChild(overlay);
        
        // Also tint the global 3d bg if it exists
        const bg3d = document.getElementById('global-3d-bg');
        if (bg3d) {
            bg3d.style.boxShadow = `inset 0 0 100px ${activeCh.color}`;
        }
    }
}

function injectDevModeToggle() {
    // Only inject if not in login screen
    if (window.location.pathname.includes('login.html')) return;

    const currentMode = localStorage.getItem('apollo_user_mode') || 'cloud';
    
    const toggleBtn = document.createElement('button');
    toggleBtn.innerHTML = currentMode === 'cloud' ? '☁️ Mudar p/ Local' : '💻 Mudar p/ Nuvem';
    toggleBtn.style.position = 'fixed';
    toggleBtn.style.bottom = '10px';
    toggleBtn.style.left = '10px';
    toggleBtn.style.zIndex = '999999';
    toggleBtn.style.background = currentMode === 'cloud' ? '#3b82f6' : '#10b981';
    toggleBtn.style.color = 'white';
    toggleBtn.style.border = '2px solid white';
    toggleBtn.style.borderRadius = '20px';
    toggleBtn.style.padding = '5px 15px';
    toggleBtn.style.fontSize = '12px';
    toggleBtn.style.fontWeight = 'bold';
    toggleBtn.style.cursor = 'pointer';
    toggleBtn.style.boxShadow = '0 4px 6px rgba(0,0,0,0.3)';
    
    toggleBtn.onclick = () => {
        const newMode = currentMode === 'cloud' ? 'local' : 'cloud';
        localStorage.setItem('apollo_user_mode', newMode);
        alert(`Modo alterado para: ${newMode.toUpperCase()}.\nA página será recarregada para aplicar as mudanças.`);
        window.location.reload();
    };

    document.body.appendChild(toggleBtn);
}
