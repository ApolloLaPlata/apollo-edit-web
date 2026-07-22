// analytics_logic.js - Lógica para a Aba de Analytics (Dashboard MOCK/DEMO)

const MOCK_STATS = [
    { label: 'Seguidores',    value: '45.2K',  icon: 'fa-users',      color: '#9B59B6', trend: '+2.3%', trendUp: true },
    { label: 'Visualizações', value: '1.2M',   icon: 'fa-eye',        color: '#3498DB', trend: '+12.5%', trendUp: true },
    { label: 'Engajamento',   value: '8.5%',   icon: 'fa-heart',      color: '#E74C3C', trend: '+0.8%', trendUp: true },
    { label: 'Comentários',   value: '12.3K',  icon: 'fa-comments',   color: '#2ECC71', trend: '-1.2%', trendUp: false }
];

const MOCK_NETWORKS = [
    {
        name: 'YouTube',
        icon: 'fa-youtube',
        color: '#FF0000',
        subscribers: '28.4K',
        views: '890K',
        engagement: '9.2%',
        posts: '142',
        trend: '+5.1%'
    },
    {
        name: 'Instagram',
        icon: 'fa-instagram',
        color: '#E1306C',
        subscribers: '15.8K',
        views: '245K',
        engagement: '7.8%',
        posts: '328',
        trend: '+3.4%'
    },
    {
        name: 'TikTok',
        icon: 'fa-music',
        color: '#00F2EA',
        subscribers: '8.9K',
        views: '1.5M',
        engagement: '12.1%',
        posts: '89',
        trend: '+18.7%'
    },
    {
        name: 'Kwai',
        icon: 'fa-video',
        color: '#FF7E29',
        subscribers: '3.2K',
        views: '56K',
        engagement: '6.4%',
        posts: '45',
        trend: '+8.2%'
    },
    {
        name: 'Facebook',
        icon: 'fa-facebook',
        color: '#1877F2',
        subscribers: '12.1K',
        views: '320K',
        engagement: '4.2%',
        posts: '215',
        trend: '-0.5%'
    },
    {
        name: 'Twitter/X',
        icon: 'fa-twitter',
        color: '#1DA1F2',
        subscribers: '6.7K',
        views: '180K',
        engagement: '5.9%',
        posts: '512',
        trend: '+1.8%'
    }
];

document.addEventListener('DOMContentLoaded', () => {
    initAnalyticsTab();
});

function initAnalyticsTab() {
    renderAnalytics();
}

function renderAnalytics() {
    const container = document.getElementById('analytics-container');
    if (!container) return;

    container.innerHTML = `
        <!-- Demo Banner -->
        <div style="background:rgba(255,211,42,0.1); border:1px solid rgba(255,211,42,0.3); border-radius:10px; padding:12px 20px; margin-bottom:20px; display:flex; align-items:center; gap:10px;">
            <i class="fas fa-info-circle" style="color:#FFD32A; font-size:18px;"></i>
            <span style="color:#FFD32A; font-family:'Nunito',sans-serif; font-size:13px; font-weight:600;">
                📊 Modo Demonstração — Conecte suas redes sociais nas Configurações para ver dados reais.
            </span>
        </div>

        <!-- Stat Cards -->
        <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:16px; margin-bottom:24px;">
            ${MOCK_STATS.map(stat => renderStatCard(stat)).join('')}
        </div>

        <!-- Networks Section -->
        <div class="news-card">
            <h2 style="font-family:'Bangers',cursive; font-size:1.6rem; color:#E84393; margin:0 0 6px 0; letter-spacing:2px;">
                <i class="fas fa-chart-line"></i> Performance por Rede
            </h2>
            <p style="color:#64748b; font-family:'Nunito',sans-serif; font-size:13px; margin:0 0 20px 0;">
                Visão geral de todas as suas redes sociais conectadas.
            </p>
            <div style="display:flex; flex-direction:column; gap:12px;">
                ${MOCK_NETWORKS.map(net => renderNetworkRow(net)).join('')}
            </div>
        </div>

        <!-- Weekly Summary -->
        <div class="news-card">
            <h2 style="font-family:'Bangers',cursive; font-size:1.6rem; color:#3498DB; margin:0 0 6px 0; letter-spacing:2px;">
                <i class="fas fa-calendar-week"></i> Resumo Semanal
            </h2>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap:16px; margin-top:16px;">
                ${renderWeeklyCard('Melhor Dia', 'Terça-feira', 'fa-star', '#FFD32A', '32K views')}
                ${renderWeeklyCard('Horário Pico', '18:00 - 21:00', 'fa-clock', '#E67E22', 'Mais engajamento')}
                ${renderWeeklyCard('Conteúdo Top', 'Vídeos Curtos', 'fa-fire', '#E74C3C', '+45% alcance')}
                ${renderWeeklyCard('Crescimento', '+1.2K seguidores', 'fa-chart-line', '#2ECC71', 'Esta semana')}
            </div>
        </div>
    `;
}

function renderStatCard(stat) {
    return `
        <div class="news-card" style="padding:20px; position:relative; overflow:hidden;">
            <div style="position:absolute; top:0; left:0; right:0; height:4px; background:${stat.color};"></div>
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
                <div style="width:44px; height:44px; border-radius:12px; background:${stat.color}22; display:flex; align-items:center; justify-content:center;">
                    <i class="fas ${stat.icon}" style="color:${stat.color}; font-size:20px;"></i>
                </div>
                <span style="font-size:12px; font-weight:700; font-family:'Nunito',sans-serif; padding:4px 8px; border-radius:12px; background:${stat.trendUp ? 'rgba(46,204,113,0.15)' : 'rgba(231,76,60,0.15)'}; color:${stat.trendUp ? '#2ECC71' : '#E74C3C'};">
                    <i class="fas fa-arrow-${stat.trendUp ? 'up' : 'down'}" style="font-size:10px;"></i> ${stat.trend}
                </span>
            </div>
            <div style="font-family:'Bangers',cursive; font-size:2.2rem; color:#fff; letter-spacing:2px; line-height:1;">
                ${stat.value}
            </div>
            <div style="font-family:'Nunito',sans-serif; font-size:13px; color:#94a3b8; margin-top:4px; font-weight:600;">
                ${stat.label}
            </div>
        </div>
    `;
}

function renderNetworkRow(net) {
    const isPositive = !net.trend.startsWith('-');
    return `
        <div style="display:flex; align-items:center; gap:16px; padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.08); transition:all 0.2s; flex-wrap:wrap;"
             onmouseover="this.style.borderColor='${net.color}44'; this.style.transform='translateX(4px)';"
             onmouseout="this.style.borderColor='rgba(255,255,255,0.08)'; this.style.transform='translateX(0)';">
            <!-- Network Icon -->
            <div style="width:48px; height:48px; border-radius:12px; background:${net.color}22; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                <i class="fab ${net.icon}" style="color:${net.color}; font-size:22px;"></i>
            </div>

            <!-- Name -->
            <div style="min-width:100px;">
                <div style="font-family:'Nunito',sans-serif; font-weight:800; font-size:15px; color:#fff;">${net.name}</div>
                <div style="font-size:12px; color:#64748b; font-family:'Nunito',sans-serif;">
                    <span style="color:${isPositive ? '#2ECC71' : '#E74C3C'}; font-weight:700;">
                        <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}" style="font-size:10px;"></i> ${net.trend}
                    </span>
                </div>
            </div>

            <!-- Metrics -->
            <div style="display:flex; gap:20px; flex:1; justify-content:space-around; flex-wrap:wrap;">
                <div style="text-align:center; min-width:70px;">
                    <div style="font-family:'Nunito',sans-serif; font-weight:800; font-size:16px; color:#fff;">${net.subscribers}</div>
                    <div style="font-size:11px; color:#64748b; font-family:'Nunito',sans-serif;">Inscritos</div>
                </div>
                <div style="text-align:center; min-width:70px;">
                    <div style="font-family:'Nunito',sans-serif; font-weight:800; font-size:16px; color:#fff;">${net.views}</div>
                    <div style="font-size:11px; color:#64748b; font-family:'Nunito',sans-serif;">Views</div>
                </div>
                <div style="text-align:center; min-width:70px;">
                    <div style="font-family:'Nunito',sans-serif; font-weight:800; font-size:16px; color:#fff;">${net.engagement}</div>
                    <div style="font-size:11px; color:#64748b; font-family:'Nunito',sans-serif;">Engaj.</div>
                </div>
                <div style="text-align:center; min-width:70px;">
                    <div style="font-family:'Nunito',sans-serif; font-weight:800; font-size:16px; color:#fff;">${net.posts}</div>
                    <div style="font-size:11px; color:#64748b; font-family:'Nunito',sans-serif;">Posts</div>
                </div>
            </div>
        </div>
    `;
}

function renderWeeklyCard(title, value, icon, color, subtitle) {
    return `
        <div style="padding:16px; background:rgba(0,0,0,0.3); border-radius:10px; border:1px solid rgba(255,255,255,0.08); text-align:center;">
            <div style="width:40px; height:40px; border-radius:10px; background:${color}22; display:flex; align-items:center; justify-content:center; margin:0 auto 10px auto;">
                <i class="fas ${icon}" style="color:${color}; font-size:18px;"></i>
            </div>
            <div style="font-family:'Nunito',sans-serif; font-size:12px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
                ${title}
            </div>
            <div style="font-family:'Bangers',cursive; font-size:1.3rem; color:#fff; letter-spacing:1px;">
                ${value}
            </div>
            <div style="font-family:'Nunito',sans-serif; font-size:11px; color:#94a3b8; margin-top:2px;">
                ${subtitle}
            </div>
        </div>
    `;
}
