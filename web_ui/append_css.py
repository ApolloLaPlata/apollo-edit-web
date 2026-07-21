import os

css_code = """
/* =========================================================================
   UX RE-ARCHITECTURE: CENTRO DE COMANDO & DOCA INFERIOR
   ========================================================================= */

body.commander-mode {
    margin: 0;
    overflow: hidden; /* Evita scroll duplo na página toda */
}

.apollo-architecture {
    display: flex;
    height: calc(100vh - 71px); /* Header height */
    width: 100vw;
    background: transparent;
    position: relative;
    z-index: 10;
}

/* --- BARRA LATERAL (HUBs) --- */
.apollo-sidebar {
    width: 260px;
    background: rgba(15, 15, 20, 0.9);
    backdrop-filter: blur(10px);
    border-right: 1px solid #333;
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}

.hub-group {
    margin-bottom: 25px;
}

.hub-title {
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 10px;
    text-transform: uppercase;
}
.hub-title.active { color: var(--btn-purple); }

.hub-link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    color: #cbd5e1;
    text-decoration: none;
    border-radius: 6px;
    font-size: 14px;
    margin-bottom: 4px;
    transition: all 0.2s;
}

.hub-link:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
}

.hub-link.active {
    background: rgba(155, 89, 182, 0.2);
    color: #fff;
    border-left: 3px solid var(--btn-purple);
}

.badge-yellow { background: var(--btn-yellow); color: #000; font-size: 10px; padding: 2px 6px; border-radius: 10px; font-weight: bold; }
.badge-new { background: #e11d48; color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 10px; font-weight: bold; }

.upgrade-banner {
    margin-top: auto;
    background: linear-gradient(135deg, rgba(155, 89, 182, 0.2), rgba(0, 0, 0, 0.5));
    border: 1px solid var(--btn-purple);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
}
.upgrade-banner h3 { margin: 0 0 5px 0; color: #fff; font-size: 1.2rem; }
.upgrade-banner p { color: #aaa; font-size: 0.8rem; margin: 0 0 10px 0; }

/* --- MAIN COMMAND CENTER --- */
.command-center {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
    padding-bottom: 250px; /* Espaço para a doca fixa embaixo */
}

/* STEPPER MISSÃO ATUAL */
.mission-tracker-panel {
    background: rgba(20, 20, 25, 0.8);
    border: 1px solid #333;
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
}

.badge-status-purple {
    background: rgba(155, 89, 182, 0.2);
    color: #e0b0ff;
    border: 1px solid #9B59B6;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 10px;
    font-weight: bold;
}

.stepper-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    z-index: 2;
}

.step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #1e1e24;
    border: 2px solid #444;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    font-weight: bold;
    font-size: 1.2rem;
    transition: 0.3s;
}

.step.completed .step-circle { background: rgba(16, 185, 129, 0.2); border-color: #10B981; color: #10B981; }
.step.active .step-circle { background: rgba(245, 158, 11, 0.2); border-color: var(--btn-yellow); color: var(--btn-yellow); }

.step-circle.pulsate {
    animation: pulse-yellow 2s infinite;
}

.step-label {
    text-align: center;
    color: #fff;
    font-size: 12px;
    font-weight: bold;
}

.step-line {
    flex: 1;
    height: 4px;
    background: #333;
    margin: 0 -20px;
    margin-top: -25px; /* Alinhar com o centro do círculo */
    border-radius: 2px;
    z-index: 1;
}

.step-line.completed { background: #10B981; }
.step-line.partial { background: linear-gradient(90deg, #10B981 50%, #333 50%); }

/* CENTRO GRID: NPC + STATUS */
.center-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

.director-npc-card {
    background: linear-gradient(135deg, rgba(20,10,40,0.9), rgba(40,15,60,0.8));
    border: 1px solid #5a2e8c;
    border-radius: 16px;
    padding: 0;
    display: flex;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.npc-content {
    padding: 30px;
    flex: 1;
    z-index: 2;
}

.npc-badge {
    color: #fff;
    font-family: 'Bangers', cursive;
    font-size: 1.5rem;
    letter-spacing: 1px;
}
.beta-tag { font-family: 'Inter', sans-serif; font-size:10px; background:#fff; color:#000; padding:2px 5px; border-radius:4px; vertical-align:middle; margin-left:10px; }

.npc-dialogue-box {
    background: rgba(0,0,0,0.4);
    border-left: 4px solid var(--btn-purple);
    padding: 15px 20px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 25px;
}

.npc-actions { display: flex; gap: 15px; }

.npc-image-container {
    width: 250px;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: center;
}

.hologram-circle {
    position: absolute;
    bottom: -20px;
    width: 200px;
    height: 60px;
    background: radial-gradient(ellipse at center, rgba(155,89,182,0.8) 0%, rgba(0,0,0,0) 70%);
    border-radius: 50%;
    filter: blur(10px);
}

.npc-avatar {
    width: 220px;
    position: relative;
    z-index: 2;
    margin-bottom: -10px;
}

.status-panel {
    background: rgba(20, 20, 25, 0.8);
    border: 1px solid #333;
    border-radius: 16px;
    padding: 25px;
}

.circular-progress {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}
.progress-ring__circle { transition: stroke-dashoffset 0.3s; transform: rotate(-90deg); transform-origin: 50% 50%; }
.progress-value { position: absolute; color: #fff; font-size: 1.5rem; font-weight: bold; }

.mini-progress-bar { width: 100%; height: 6px; background: #333; border-radius: 3px; overflow: hidden; }
.mini-progress-bar .fill { height: 100%; background: linear-gradient(90deg, var(--btn-purple), #e0b0ff); }

/* AÇÕES RÁPIDAS (ZONA 4) */
.quick-actions-row {
    display: flex;
    gap: 15px;
}

.quick-action-card {
    flex: 1;
    background: rgba(20, 20, 25, 0.8);
    border: 1px solid #333;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    text-decoration: none;
    color: inherit;
    overflow: hidden;
    transition: 0.2s;
}

.quick-action-card:hover { border-color: var(--btn-purple); transform: translateY(-5px); }

.qa-bg {
    height: 80px;
    background-size: cover;
    background-position: center;
    border-bottom: 1px solid #333;
}

.qa-content { padding: 15px; }
.qa-content h4 { margin: 0 0 5px 0; color: #fff; font-size: 1rem; }
.qa-content p { margin: 0; color: #94a3b8; font-size: 0.8rem; line-height: 1.4; }

/* --- DOCA INFERIOR (ÁREA DE TRANSFERÊNCIA) --- */
.bottom-dock {
    position: fixed;
    bottom: 0;
    left: 260px; /* Largura da sidebar */
    right: 0;
    height: 250px;
    background: rgba(15, 15, 20, 0.98);
    backdrop-filter: blur(15px);
    border-top: 2px solid #5a2e8c;
    box-shadow: 0 -10px 40px rgba(0,0,0,0.8);
    transform: translateY(calc(100% - 40px)); /* Mostra só o header */
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1000;
    display: flex;
    flex-direction: column;
}

.bottom-dock.open {
    transform: translateY(0);
}

.dock-header {
    height: 40px;
    background: linear-gradient(90deg, #1a1a24, #2a1b38);
    border-bottom: 1px solid #333;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    cursor: pointer;
}
.dock-header:hover { background: linear-gradient(90deg, #2a1b38, #3a2b48); }

.dock-title { color: #fff; font-weight: bold; font-size: 14px; }
.dock-badge { background: var(--btn-purple); color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; }
.dock-toggle-icon { color: #888; font-size: 12px; }

.dock-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0;
}

.dock-tabs {
    display: flex;
    border-bottom: 1px solid #333;
    padding: 0 10px;
    background: #111;
}

.dock-tab {
    background: transparent;
    border: none;
    color: #64748b;
    padding: 10px 15px;
    font-size: 12px;
    font-weight: bold;
    cursor: pointer;
    border-bottom: 2px solid transparent;
}
.dock-tab:hover { color: #fff; }
.dock-tab.active { color: #fff; border-bottom-color: var(--btn-purple); }

/* Animations */
@keyframes pulse-yellow {
    0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
    70% { box-shadow: 0 0 0 15px rgba(245, 158, 11, 0); }
    100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}

/* ========================================================================= */
"""

path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\global_style.css'
with open(path, 'a', encoding='utf-8') as f:
    f.write(css_code)
