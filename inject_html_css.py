import os
import re

css_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\global_style.css'
html_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\hub.html'

# 1. APPEND CSS
css_to_append = """
/* =========================================================================
   HYBRID RPG AESTHETIC (INJECTED)
   ========================================================================= */

body {
    background-color: #0b0510 !important;
}

#global-3d-bg {
    background-image: 
        linear-gradient(rgba(155, 89, 182, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(155, 89, 182, 0.1) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
    background-position: center center !important;
    opacity: 0.8;
}

/* Painel de Missão (Stepper) */
.mission-tracker-panel {
    background: rgba(20, 15, 30, 0.6);
    border: 1px solid #4a2b6e;
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
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

/* Centro Grid: NPC + Status */
.center-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 20px;
    margin-bottom: 30px;
}

.director-npc-card {
    background: linear-gradient(135deg, rgba(20,10,40,0.8), rgba(40,15,60,0.6));
    border: 1px solid #5a2e8c;
    border-radius: 16px;
    padding: 0;
    display: flex;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    backdrop-filter: blur(5px);
}

.npc-content {
    padding: 25px;
    flex: 1;
    z-index: 2;
}

.npc-badge {
    color: #fff;
    font-family: 'Bangers', cursive;
    font-size: 1.5rem;
    letter-spacing: 1px;
}

.npc-dialogue-box {
    margin-bottom: 20px;
}

.npc-actions { display: flex; gap: 15px; }

/* Botões gigantes estilo imagem */
.btn-gpt-green {
    background: linear-gradient(180deg, #34d399, #059669);
    border: 3px solid #6ee7b7;
    color: white;
    font-family: 'Bangers', cursive;
    font-size: 1.5rem;
    padding: 10px 20px;
    border-radius: 12px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4);
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    transition: transform 0.1s;
}
.btn-gpt-green:active { transform: scale(0.95); }

.btn-gpt-blue {
    background: linear-gradient(180deg, #60a5fa, #2563eb);
    border: 3px solid #93c5fd;
    color: white;
    font-family: 'Bangers', cursive;
    font-size: 1.5rem;
    padding: 10px 20px;
    border-radius: 12px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    transition: transform 0.1s;
}
.btn-gpt-blue:active { transform: scale(0.95); }

.npc-image-container {
    width: 250px;
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: center;
}

.npc-avatar {
    width: 200px;
    position: relative;
    z-index: 2;
    margin-bottom: -10px;
    filter: drop-shadow(0 0 15px rgba(155, 89, 182, 0.6));
}

.status-panel {
    background: rgba(20, 15, 30, 0.6);
    border: 1px solid #4a2b6e;
    border-radius: 16px;
    padding: 25px;
    backdrop-filter: blur(10px);
}

.circular-progress {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}
.progress-ring__circle { transition: stroke-dashoffset 0.3s; transform: rotate(-90deg); transform-origin: 50% 50%; }
.progress-value { position: absolute; color: #fff; font-size: 1.8rem; font-weight: bold; font-family: 'Bangers'; }

.mini-progress-bar { width: 100%; height: 6px; background: #333; border-radius: 3px; overflow: hidden; margin-top: 5px;}
.mini-progress-bar .fill { height: 100%; background: linear-gradient(90deg, #a855f7, #d8b4fe); }

/* Separador Visual para o Conteúdo Antigo */
.legacy-tools-header {
    margin-top: 40px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #4a2b6e;
    display: flex;
    align-items: center;
    gap: 10px;
}
.legacy-tools-header h2 {
    margin: 0;
    color: #e0b0ff;
    font-family: 'Bangers', cursive;
    font-size: 2rem;
    letter-spacing: 1px;
}
"""

with open(css_path, 'r', encoding='utf-8') as f:
    current_css = f.read()

if "HYBRID RPG AESTHETIC (INJECTED)" not in current_css:
    with open(css_path, 'a', encoding='utf-8') as f:
        f.write("\n" + css_to_append)

# 2. INJECT HTML
html_to_inject = """
            <!-- ========================================== -->
            <!-- INJEÇÃO DO PAINEL RPG (ESTÉTICA CHATGPT)   -->
            <!-- ========================================== -->
            
            <div class="mission-tracker-panel">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h3 style="color: #cbd5e1; margin-top:0; font-size: 0.9rem; text-transform: uppercase; letter-spacing:1px; display:flex; align-items:center; gap:10px;">
                            MISSÃO ATUAL <span class="badge-status-purple">EM ANDAMENTO</span>
                        </h3>
                        <h2 style="color: #fff; margin-top: 5px; margin-bottom: 25px; font-size: 1.8rem; font-weight:600; font-family: 'Nunito', sans-serif;">Vídeo sobre Bitcoin e o futuro das Criptos</h2>
                    </div>
                    <button class="btn-gpt-blue" style="font-size: 1rem; border-width: 2px;">DETALHES DA MISSÃO</button>
                </div>
                
                <div class="stepper-container">
                    <div class="step completed">
                        <div class="step-circle">✓</div>
                        <div class="step-label">BRIEFING<br><span style="color:#10B981; font-size:10px;">Concluído</span></div>
                    </div>
                    <div class="step-line completed"></div>
                    <div class="step completed">
                        <div class="step-circle">✓</div>
                        <div class="step-label">ROTEIRO<br><span style="color:#10B981; font-size:10px;">Concluído</span></div>
                    </div>
                    <div class="step-line partial"></div>
                    <div class="step active">
                        <div class="step-circle" style="animation: pulse 2s infinite;">⏳</div>
                        <div class="step-label">IMAGENS<br><span style="color:var(--btn-yellow); font-size:10px;">73%</span></div>
                    </div>
                    <div class="step-line"></div>
                    <div class="step">
                        <div class="step-circle">4</div>
                        <div class="step-label">NARRAÇÃO<br><span style="color:#64748b; font-size:10px;">Pendente</span></div>
                    </div>
                    <div class="step-line"></div>
                    <div class="step">
                        <div class="step-circle">5</div>
                        <div class="step-label">EDIÇÃO<br><span style="color:#64748b; font-size:10px;">Pendente</span></div>
                    </div>
                    <div class="step-line"></div>
                    <div class="step">
                        <div class="step-circle">6</div>
                        <div class="step-label">UPLOAD<br><span style="color:#64748b; font-size:10px;">Pendente</span></div>
                    </div>
                </div>
            </div>

            <div class="center-grid">
                <!-- DIRETOR APOLLO NPC -->
                <div class="director-npc-card">
                    <div class="npc-content">
                        <div class="npc-badge">DIRETOR APOLLO <span style="font-family: sans-serif; font-size:10px; background:#fff; color:#000; padding:2px 5px; border-radius:4px; vertical-align:middle; margin-left:10px;">BETA</span></div>
                        <h4 style="color:#94a3b8; font-size:13px; font-weight:normal; margin-bottom:15px; margin-top:5px;">Seu copiloto e assistente pessoal de produção</h4>
                        
                        <div class="npc-dialogue-box">
                            <p style="color:#fff; font-size:1.1rem; line-height:1.5; font-family: 'Nunito', sans-serif;">
                                "Bom retorno, Piloto! 🚀<br><br>
                                As imagens do seu vídeo estão <b>73% concluídas</b> e a qualidade está excelente no laboratório.<br><br>
                                Próxima ação recomendada na missão:"
                            </p>
                        </div>
                        <div class="npc-actions">
                            <button class="btn-gpt-green" onclick="alert('Simulação: Abrindo Gerador de Narração...')">
                                <span style="font-size:1.2rem; margin-right:5px;">🔊</span> GERAR NARRAÇÃO
                            </button>
                            <button class="btn-gpt-blue" onclick="alert('Simulação: Abrindo Revisão de Imagens...')">
                                👁️ REVISAR IMAGENS
                            </button>
                        </div>
                    </div>
                    <div class="npc-image-container">
                        <img src="assets/mascote.png" alt="Diretor Apollo" class="npc-avatar">
                    </div>
                </div>

                <!-- PAINEL DE STATUS DA MISSÃO -->
                <div class="status-panel">
                    <h3 style="margin-top:0; color:#fff; font-size:1.2rem; border-bottom:1px solid #4a2b6e; padding-bottom:10px; margin-bottom:20px; font-family:'Bangers'; letter-spacing:1px;">STATUS DA MISSÃO</h3>
                    
                    <div style="display:flex; align-items:center; gap:20px; margin-bottom:25px;">
                        <div class="circular-progress">
                            <span class="progress-value">73%</span>
                            <svg class="progress-ring" width="100" height="100">
                              <circle class="progress-ring__circle" stroke="#333" stroke-width="8" fill="transparent" r="40" cx="50" cy="50" style="stroke-dasharray: 251 251; stroke-dashoffset: 0;"/>
                              <circle class="progress-ring__circle" stroke="#a855f7" stroke-width="8" stroke-dasharray="251 251" stroke-dashoffset="67" fill="transparent" r="40" cx="50" cy="50"/>
                            </svg>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:10px;">
                            <div style="display:flex; align-items:center; gap:10px; color:#cbd5e1;">
                                <span>⏱️</span>
                                <div>
                                    <div style="font-size:10px; color:#94a3b8;">Tempo decorrido</div>
                                    <div style="font-weight:bold; font-family:'Nunito';">01:24:35</div>
                                </div>
                            </div>
                            <div style="display:flex; align-items:center; gap:10px; color:#cbd5e1;">
                                <span>⌛</span>
                                <div>
                                    <div style="font-size:10px; color:#94a3b8;">Tempo estimado</div>
                                    <div style="font-weight:bold; font-family:'Nunito';">00:45:20</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: rgba(0,0,0,0.3); border-radius:8px; padding:15px; border:1px solid #4a2b6e;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                            <span style="color:#94a3b8; font-size:13px;">IAs trabalhando</span>
                            <span style="color:#fff; font-weight:bold;">24 Agentes</span>
                        </div>
                        <div class="mini-progress-bar"><div class="fill" style="width:70%;"></div></div>
                    </div>
                </div>
            </div>

            <div class="legacy-tools-header">
                <span>⚡</span>
                <h2>SALA DE FERRAMENTAS (LIVRE ACESSO)</h2>
            </div>
            
            <!-- ========================================== -->
"""

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Only inject if not already there
if "INJEÇÃO DO PAINEL RPG" not in html_content:
    # Find the insertion point: <main class="main-stage">
    pattern = r'(<main class="main-stage">)'
    
    new_html_content = re.sub(pattern, r'\1\n' + html_to_inject, html_content, count=1)
    
    # Let's also update the "COFRE DE MOEDAS" slightly to match the aesthetic (make it purple/neon if it exists).
    # But it's safer to just inject the new panel ABOVE everything else.
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html_content)

print("Injection complete.")
