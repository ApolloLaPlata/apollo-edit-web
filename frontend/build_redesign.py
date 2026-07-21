import re
import os

html_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\hub.html'
css_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\apollo_redesign.css'

# =======================================================
# 1. NEW HTML STRUCTURE
# =======================================================
new_body_content = """
    <div id="global-3d-bg" class="redesign-bg"></div>

    <div class="apollo-app-container">
        
        <!-- LEFT MAIN CONTENT -->
        <div class="apollo-main-content">
            
            <!-- HEADER / TOP ACTIONS -->
            <div class="top-dashboard-section">
                
                <!-- PRO CARD -->
                <div class="pro-upgrade-card">
                    <img src="assets/car_level1.png" alt="Apollo Pro Car" class="pro-car-img" style="filter: hue-rotate(270deg);">
                    <div class="pro-card-content">
                        <h3>APOLLO PRO</h3>
                        <p>Desbloqueie todo o poder da IA e acelere suas criações.</p>
                        <button class="btn-upgrade">👑 UPGRADE AGORA</button>
                    </div>
                </div>

                <!-- FERRAMENTAS RÁPIDAS -->
                <div class="quick-tools-panel">
                    <div class="panel-header">
                        <h3>FERRAMENTAS RÁPIDAS <span class="subtitle">(ACESSO RÁPIDO)</span></h3>
                    </div>
                    <div class="quick-tools-grid">
                        <a href="laplata_script.html" class="quick-tool-item">
                            <div class="icon-box"><span class="icon-svg">📝</span></div>
                            <span class="label">Estúdio de Roteiro</span>
                        </a>
                        <a href="noticias_studio.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #10B981;"><span class="icon-svg">🖼️</span></div>
                            <span class="label">Estúdio de Imagens</span>
                        </a>
                        <a href="tts.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #D946EF;"><span class="icon-svg">🎤</span></div>
                            <span class="label">Estúdio de Vozes</span>
                        </a>
                        <a href="laplata_roster.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #F59E0B;"><span class="icon-svg">🧑‍🚀</span></div>
                            <span class="label">Personagens</span>
                        </a>
                        <a href="timeline.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #3B82F6;"><span class="icon-svg">🎞️</span></div>
                            <span class="label">Timeline</span>
                        </a>
                        <a href="ferramentas.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #8B5CF6;"><span class="icon-svg">🛠️</span></div>
                            <span class="label">Mini-Tools</span>
                        </a>
                        <a href="laplata_creator.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #EC4899;"><span class="icon-svg">🧪</span></div>
                            <span class="label">Laboratório</span>
                        </a>
                        <a href="noticias_radar.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #EAB308;"><span class="icon-svg">📡</span></div>
                            <span class="label">Radar YT</span>
                        </a>
                        <a href="mercado.html" class="quick-tool-item">
                            <div class="icon-box" style="color: #14B8A6;"><span class="icon-svg">🛒</span></div>
                            <span class="label">Mercado</span>
                        </a>
                        <a href="#" class="quick-tool-item add-btn">
                            <div class="icon-box"><span>+</span></div>
                        </a>
                    </div>
                </div>
            </div>

            <!-- MISSÕES DIÁRIAS & COPILOTO -->
            <div class="middle-dashboard-section">
                <div class="daily-missions-panel">
                    <div class="panel-header" style="justify-content: space-between;">
                        <h3>MISSÕES DIÁRIAS</h3>
                        <span class="subtitle">Renovam em: <strong style="color: #fff;">08:45:12</strong></span>
                    </div>
                    <div class="missions-cards-row">
                        <div class="mission-card">
                            <div class="mission-icon" style="color: #F59E0B;">📝</div>
                            <div class="mission-info">
                                <h4>Criar 1 Roteiro com IA</h4>
                                <div class="progress-track"><div class="progress-fill" style="width: 0%; background: #F59E0B;"></div></div>
                                <div class="mission-reward"><span style="color: #F59E0B;">+30 💎</span> <span class="count">0/1</span></div>
                            </div>
                        </div>
                        <div class="mission-card">
                            <div class="mission-icon" style="color: #10B981;">🖼️</div>
                            <div class="mission-info">
                                <h4>Gerar 5 Imagens com IA</h4>
                                <div class="progress-track"><div class="progress-fill" style="width: 60%; background: #10B981;"></div></div>
                                <div class="mission-reward"><span style="color: #10B981;">+40 💎</span> <span class="count">3/5</span></div>
                            </div>
                        </div>
                        <div class="mission-card">
                            <div class="mission-icon" style="color: #D946EF;">🎞️</div>
                            <div class="mission-info">
                                <h4>Renderizar 1 Vídeo completo</h4>
                                <div class="progress-track"><div class="progress-fill" style="width: 0%; background: #D946EF;"></div></div>
                                <div class="mission-reward"><span style="color: #D946EF;">+50 💎</span> <span class="count">0/1</span></div>
                            </div>
                        </div>
                    </div>
                    <button class="btn-full-width" style="margin-top: 15px;">VER TODAS MISSÕES</button>
                </div>

                <div class="rewards-panel">
                    <div class="panel-header">
                        <h3 style="color: #F59E0B;">✨ RECOMPENSAS</h3>
                    </div>
                    <div class="reward-content">
                        <img src="assets/bg_timeline.png" alt="Chest" class="chest-img" style="filter: hue-rotate(270deg);">
                        <div class="reward-info">
                            <p>Próxima recompensa no Nível 28</p>
                            <h2 style="color: #60A5FA;">+100 Cristais</h2>
                        </div>
                    </div>
                    <div class="progress-track" style="margin-top: 10px;"><div class="progress-fill" style="width: 49%; background: #D946EF;"></div></div>
                    <div style="text-align: right; font-size: 11px; margin-top: 5px; color: #94A3B8;">2.450 / 5.000 XP</div>
                </div>

                <div class="copilot-panel">
                    <div class="panel-header">
                        <h3>SEU COPILOTO ATUAL</h3>
                    </div>
                    <div class="copilot-content">
                        <img src="assets/ai_robot_racer.png" alt="Copilot" class="copilot-img" style="filter: hue-rotate(270deg);">
                        <div class="copilot-info">
                            <h3 style="color: #D946EF; margin:0; font-family: 'Orbitron', sans-serif;">Apollo V1.2</h3>
                            <p style="color: #94A3B8; margin: 5px 0;">Nível 10</p>
                            <p style="color: #94A3B8; margin: 0;">Eficiência: <strong style="color: #fff;">98%</strong></p>
                            <button class="btn-outline" style="margin-top: 10px;">TROCAR COPILOTO</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- FERRAMENTAS PRINCIPAIS -->
            <div class="section-container">
                <div class="panel-header" style="justify-content: space-between;">
                    <div>
                        <h3>FERRAMENTAS PRINCIPAIS</h3>
                        <p class="subtitle">Acesse suas ferramentas mais utilizadas</p>
                    </div>
                    <button class="btn-outline">VER TODAS AS FERRAMENTAS</button>
                </div>
                <div class="horizontal-cards-row">
                    <a href="timeline.html" class="horiz-card">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_timeline.png');"></div>
                        <div class="horiz-card-info">
                            <h4>TIMELINE</h4>
                            <p>Montagem avançada de vídeos</p>
                        </div>
                    </a>
                    <a href="montador.html" class="horiz-card">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_generic_garage.png');"></div>
                        <div class="horiz-card-info">
                            <h4>MONTADOR DARK</h4>
                            <p>Edição profissional</p>
                        </div>
                    </a>
                    <a href="laplata_jobs.html" class="horiz-card">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_timeline.png'); filter: hue-rotate(180deg);"></div>
                        <div class="horiz-card-info">
                            <h4>AUTO EXECUÇÃO</h4>
                            <p>Gere vídeos no automático</p>
                        </div>
                    </a>
                    <a href="laplata_videodirector.html" class="horiz-card">
                        <div class="horiz-card-img" style="background-image: url('assets/mascote.png'); background-position: top;"></div>
                        <div class="horiz-card-info">
                            <h4>DIRETOR DE VÍDEO</h4>
                            <p>Controle total da criação</p>
                        </div>
                    </a>
                </div>
            </div>

            <!-- MISSÕES PRINCIPAIS E NOTICIAS -->
            <div class="split-section">
                <div class="main-missions-panel">
                    <div class="panel-header">
                        <div>
                            <h3>MISSÕES PRINCIPAIS (CRIAÇÃO)</h3>
                            <p class="subtitle">Acompanhe e conclua suas missões de criação</p>
                        </div>
                    </div>
                    <div class="vertical-cards-row">
                        <a href="noticias_scripts.html" class="vert-card">
                            <div class="level-tag">Lv.25</div>
                            <div class="vert-img" style="background-image: url('assets/bg_generic_garage.png'); filter: hue-rotate(270deg);"></div>
                            <h4>ROTEIRO PERFEITO</h4>
                        </a>
                        <a href="noticias_strategy.html" class="vert-card">
                            <div class="level-tag">Lv.20</div>
                            <div class="vert-img" style="background-image: url('assets/bg_timeline.png'); filter: hue-rotate(200deg);"></div>
                            <h4>ESTRATÉGIA DE VÍDEO</h4>
                        </a>
                        <a href="dublagem.html" class="vert-card">
                            <div class="level-tag">Lv.20</div>
                            <div class="vert-img" style="background-image: url('assets/bg_dublagem.png');"></div>
                            <h4>NARRAÇÃO ÉPICA</h4>
                        </a>
                        <a href="noticias_miner.html" class="vert-card">
                            <div class="level-tag">Lv.20</div>
                            <div class="vert-img" style="background-image: url('assets/bg_generic_garage.png'); filter: hue-rotate(100deg);"></div>
                            <h4>VÍDEO VIRAL</h4>
                        </a>
                        <a href="laplata_social.html" class="vert-card">
                            <div class="level-tag">Lv.20</div>
                            <div class="vert-img" style="background-image: url('assets/bg_timeline.png'); filter: hue-rotate(40deg);"></div>
                            <h4>POSTAGEM SOCIAL</h4>
                        </a>
                    </div>
                    <button class="btn-full-width" style="margin-top: 15px;">VER TODAS MISSÕES</button>
                </div>

                <div class="news-panel">
                    <div class="panel-header">
                        <div>
                            <h3>CENTRAL DE NOTÍCIAS</h3>
                            <p class="subtitle">Fique por dentro das novidades</p>
                        </div>
                    </div>
                    <div class="news-list">
                        <div class="news-item">
                            <div class="news-icon" style="color: #F59E0B;">🛡️</div>
                            <div class="news-text">Nova API Nano Banana disponível!</div>
                            <div class="news-time">2h atrás</div>
                        </div>
                        <div class="news-item">
                            <div class="news-icon" style="color: #10B981;">▶️</div>
                            <div class="news-text">Sistema de Vozes atualizado</div>
                            <div class="news-time">5h atrás</div>
                        </div>
                        <div class="news-item">
                            <div class="news-icon" style="color: #D946EF;">🛡️</div>
                            <div class="news-text">Tutorial: Crie vídeos virais</div>
                            <div class="news-time">1d atrás</div>
                        </div>
                        <div class="news-item">
                            <div class="news-icon" style="color: #F59E0B;">📍</div>
                            <div class="news-text">Nova missão especial liberada</div>
                            <div class="news-time">2d atrás</div>
                        </div>
                    </div>
                    <button class="btn-full-width" style="margin-top: 15px;">VER TODAS NOTÍCIAS</button>
                </div>
            </div>

            <!-- ECOSSISTEMA APOLLO -->
            <div class="section-container">
                <div class="panel-header">
                    <div>
                        <h3>ECOSSISTEMA APOLLO</h3>
                        <p class="subtitle">Explore o ecossistema completo</p>
                    </div>
                </div>
                <div class="horizontal-cards-row">
                    <a href="laplata_creator.html" class="horiz-card small">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_generic_garage.png');"></div>
                        <div class="horiz-card-info"><h4>LABORATÓRIO</h4><p>Experimentos e testes</p></div>
                    </a>
                    <a href="noticias_studio.html" class="horiz-card small">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_timeline.png');"></div>
                        <div class="horiz-card-info"><h4>ESTÚDIO DE IMAGENS</h4><p>Criação de imagens IA</p></div>
                    </a>
                    <a href="laplata_roster.html" class="horiz-card small">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_generic_garage.png');"></div>
                        <div class="horiz-card-info"><h4>PERSONAGENS</h4><p>Avatares e personagens</p></div>
                    </a>
                    <a href="laplata_gallery.html" class="horiz-card small">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_timeline.png');"></div>
                        <div class="horiz-card-info"><h4>GALERIA</h4><p>Seus projetos salvos</p></div>
                    </a>
                    <a href="laplata_script.html" class="horiz-card small">
                        <div class="horiz-card-img" style="background-image: url('assets/bg_generic_garage.png');"></div>
                        <div class="horiz-card-info"><h4>SALA DE ROTEIRO</h4><p>Roteiros e ideias</p></div>
                    </a>
                </div>
                <button class="btn-full-width" style="margin-top: 15px;">VER ECOSSISTEMA COMPLETO</button>
            </div>

            <!-- MINI-TOOLS -->
            <div class="section-container">
                <div class="panel-header" style="justify-content: space-between;">
                    <div>
                        <h3>MINI-TOOLS</h3>
                        <p class="subtitle">Ferramentas rápidas do dia a dia</p>
                    </div>
                    <button class="btn-outline">VER TODAS MINI-TOOLS</button>
                </div>
                <div class="mini-tools-grid">
                    <a href="ferramentas.html?tool=redimensionar" class="mini-tool-card">
                        <div class="mini-icon" style="color: #D946EF;">📐</div>
                        <h4>RESIZE CROP</h4>
                        <p>Redimensione</p>
                    </a>
                    <a href="ferramentas.html?tool=acelerar_desacelerar" class="mini-tool-card">
                        <div class="mini-icon" style="color: #EC4899;">⚡</div>
                        <h4>SPEED FX</h4>
                        <p>Efeitos de velocidade</p>
                    </a>
                    <a href="ferramentas.html?tool=remover_audio" class="mini-tool-card">
                        <div class="mini-icon" style="color: #8B5CF6;">🔇</div>
                        <h4>NOISE VÍDEO</h4>
                        <p>Adicione ruído</p>
                    </a>
                    <a href="ferramentas.html?tool=ajustar_brilho_contraste" class="mini-tool-card">
                        <div class="mini-icon" style="color: #F59E0B;">🎨</div>
                        <h4>COLOR GRADE</h4>
                        <p>Correção de cor</p>
                    </a>
                    <a href="ferramentas.html?tool=inverter_video" class="mini-tool-card">
                        <div class="mini-icon" style="color: #14B8A6;">⏪</div>
                        <h4>REWIND FX</h4>
                        <p>Efeito replay</p>
                    </a>
                    <a href="ferramentas.html?tool=remover_silencios" class="mini-tool-card">
                        <div class="mini-icon" style="color: #10B981;">✂️</div>
                        <h4>AUTO-CUT</h4>
                        <p>Corte automático</p>
                    </a>
                    <a href="ferramentas.html?tool=compressor_video" class="mini-tool-card">
                        <div class="mini-icon" style="color: #3B82F6;">🗜️</div>
                        <h4>COMPRESSOR</h4>
                        <p>Compressão</p>
                    </a>
                    <a href="ferramentas.html?tool=padronizar_celular" class="mini-tool-card">
                        <div class="mini-icon" style="color: #F59E0B;">📱</div>
                        <h4>SHORTS MAKER</h4>
                        <p>Vídeos curtos</p>
                    </a>
                </div>
            </div>

            <!-- FOOTER RODAPÉ FLUTUANTE -->
            <div class="bottom-footer-bar">
                <div class="recent-projects">
                    <h4>ÚLTIMOS PROJETOS</h4>
                    <div class="proj-item"><div class="proj-img"></div><div class="p-info"><span class="p-title">Bitcoin 2025</span><span class="p-stat">Em andamento</span></div></div>
                    <div class="proj-item"><div class="proj-img"></div><div class="p-info"><span class="p-title">IA e Futuro</span><span class="p-stat">Concluído</span></div></div>
                    <div class="proj-item"><div class="proj-img"></div><div class="p-info"><span class="p-title">Top 10 Criptos</span><span class="p-stat">Renderizado</span></div></div>
                    <div class="proj-item"><div class="proj-img"></div><div class="p-info"><span class="p-title">Tecnologia Hoje</span><span class="p-stat">Em edição</span></div></div>
                    <a href="#" style="color: #D946EF; font-size: 12px; margin-left: 10px; text-decoration: none;">VER TODOS ></a>
                </div>
                <div class="community-stats">
                    <h4>COMUNIDADE APOLLO</h4>
                    <div style="display:flex; align-items:center; gap: 10px;">
                        <span style="color: #10B981;">🟢 +1.250 Pilotos online</span>
                        <div class="avatars-group">
                            <div class="av"></div><div class="av"></div><div class="av"></div><div class="av"></div><div class="av text">+1246</div>
                        </div>
                    </div>
                </div>
                <!-- Chatbot trigger icon on bottom right -->
                <div class="chatbot-trigger-icon" onclick="openChatbot()"></div>
            </div>

        </div> <!-- END LEFT MAIN CONTENT -->

        <!-- RIGHT SIDEBAR (Perfil & Status) -->
        <div class="apollo-right-sidebar">
            
            <div class="sidebar-card profile-section">
                <div class="profile-header">
                    <img src="assets/mascote.png" alt="Avatar" class="profile-avatar">
                    <div class="profile-titles">
                        <h3 style="color: #D946EF; font-family: 'Orbitron'; margin: 0;">PILOTO DE ELITE</h3>
                        <p style="color: #cbd5e1; margin: 2px 0;">Nível 27</p>
                    </div>
                </div>
                <div class="progress-track" style="margin-top: 10px;"><div class="progress-fill" style="width: 49%; background: #F59E0B;"></div></div>
                <div style="text-align: right; font-size: 11px; margin-top: 5px; color: #94A3B8;">2.450 / 5.000 XP</div>
                
                <div class="economy-row">
                    <div class="econ-item"><span class="icon">⛽</span><div><span class="label">GASOLINA</span><span class="val">100</span></div></div>
                    <div class="econ-item"><span class="icon" style="color: #3B82F6;">💎</span><div><span class="label" style="color: #3B82F6;">CRISTAIS</span><span class="val">12</span></div></div>
                    <div class="econ-item"><span class="icon" style="color: #F59E0B;">🪙</span><div><span class="label" style="color: #F59E0B;">MOEDAS</span><span class="val">3.250</span></div></div>
                </div>
                <button class="btn-full-width primary-purple" style="margin-top: 15px;" onclick="window.location.href='loja.html'">LOJA APOLLO 💎</button>
            </div>

            <div class="sidebar-card">
                <div class="panel-header">
                    <h3>CONQUISTAS RECENTES</h3>
                </div>
                <div class="achievements-list">
                    <div class="achieve-item">
                        <div class="achieve-icon" style="color: #F59E0B;">⭐</div>
                        <div class="achieve-info">
                            <h4>Primeiro Vídeo</h4>
                            <p>Conclua seu primeiro vídeo</p>
                        </div>
                        <div class="achieve-xp" style="color: #10B981;">+100 XP</div>
                    </div>
                    <div class="achieve-item">
                        <div class="achieve-icon" style="color: #10B981;">❇️</div>
                        <div class="achieve-info">
                            <h4>Roteirista</h4>
                            <p>Crie 5 roteiros incríveis</p>
                        </div>
                        <div class="achieve-xp" style="color: #10B981;">+250 XP</div>
                    </div>
                    <div class="achieve-item">
                        <div class="achieve-icon" style="color: #F59E0B;">🏅</div>
                        <div class="achieve-info">
                            <h4>Editor Master</h4>
                            <p>Edite 10 vídeos</p>
                        </div>
                        <div class="achieve-xp" style="color: #10B981;">+500 XP</div>
                    </div>
                </div>
                <button class="btn-full-width" style="margin-top: 15px;">VER TODAS</button>
            </div>

            <div class="sidebar-card">
                <div class="panel-header">
                    <h3>STATUS DO SISTEMA</h3>
                </div>
                <div class="status-list">
                    <div class="status-item">
                        <div class="s-icon">🤖</div>
                        <div class="s-name">IA Director</div>
                        <div class="s-val" style="color: #10B981;">Online 🟢</div>
                    </div>
                    <div class="status-item">
                        <div class="s-icon">🖥️</div>
                        <div class="s-name">Render Farm</div>
                        <div class="s-val" style="color: #10B981;">Online 🟢</div>
                    </div>
                    <div class="status-item">
                        <div class="s-icon">🎙️</div>
                        <div class="s-name">Banco de Vozes</div>
                        <div class="s-val" style="color: #10B981;">Online 🟢</div>
                    </div>
                    <div class="status-item">
                        <div class="s-icon">🗂️</div>
                        <div class="s-name">Armazenamento</div>
                        <div class="s-val" style="color: #F59E0B;">78% 🔶</div>
                    </div>
                </div>
            </div>

            <div class="sidebar-footer-img">
                <img src="assets/car_level1.png" alt="Garage" style="width: 100%; border-radius: 12px; filter: hue-rotate(270deg);">
            </div>

            <div style="text-align: center; color: #64748b; font-size: 11px; margin-top: 10px;">
                APOLLO EDIT • 2024<br>Todos os direitos reservados
            </div>

        </div> <!-- END RIGHT SIDEBAR -->
    </div>
"""

# =======================================================
# 2. CSS STYLES (apollo_redesign.css)
# =======================================================
css_content = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Orbitron:wght@700;900&family=Rajdhani:wght@600&display=swap');

:root {
    --primary: #8B5CF6;
    --secondary: #D946EF;
    --highlight: #F59E0B;
    --success: #10B981;
    --surface: #1A1332;
    --surface-sec: #2D1B69;
    --bg-dark: #0A0612;
    --text-main: #FFFFFF;
    --text-muted: #94A3B8;
}

body {
    background-color: var(--bg-dark);
    color: var(--text-main);
    font-family: 'Inter', sans-serif;
    margin: 0; padding: 0;
}

.redesign-bg {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image: linear-gradient(rgba(139, 92, 246, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(139, 92, 246, 0.05) 1px, transparent 1px);
    background-size: 30px 30px; z-index: -1;
}

h1, h2, h3, h4 { font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }

.apollo-app-container {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 20px;
    padding: 20px;
    max-width: 1600px;
    margin: 0 auto;
}

/* ================== LEFT MAIN CONTENT ================== */
.apollo-main-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.panel-header {
    display: flex; align-items: center; margin-bottom: 15px;
}
.panel-header h3 { font-size: 1.1rem; color: #fff; margin: 0; }
.panel-header .subtitle { font-family: 'Rajdhani', sans-serif; color: var(--text-muted); font-size: 0.9rem; margin-top: 2px; }

/* Top Section */
.top-dashboard-section {
    display: grid; grid-template-columns: 300px 1fr; gap: 20px;
}

.pro-upgrade-card {
    background: linear-gradient(145deg, #2D1B69, #1A1332);
    border: 1px solid var(--primary);
    border-radius: 16px; padding: 20px;
    display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
    position: relative; overflow: hidden;
}
.pro-car-img { width: 150px; margin-bottom: 10px; }
.pro-card-content h3 { color: var(--secondary); margin: 0 0 5px 0; }
.pro-card-content p { color: var(--text-muted); font-size: 0.8rem; margin: 0 0 15px 0; }

.btn-upgrade {
    background: transparent; border: 1px solid var(--highlight); color: var(--highlight);
    padding: 8px 15px; border-radius: 8px; font-weight: bold; font-family: 'Rajdhani'; cursor: pointer; transition: 0.3s;
}
.btn-upgrade:hover { background: rgba(245, 158, 11, 0.2); }

.quick-tools-panel {
    background: var(--surface); border: 1px solid var(--surface-sec); border-radius: 16px; padding: 20px;
}
.quick-tools-grid { display: flex; flex-wrap: wrap; gap: 15px; }
.quick-tool-item {
    display: flex; flex-direction: column; align-items: center; gap: 8px; text-decoration: none; width: 75px;
}
.icon-box {
    width: 50px; height: 50px; border-radius: 12px; background: var(--surface-sec);
    display: flex; justify-content: center; align-items: center; font-size: 1.5rem;
    border: 1px solid rgba(255,255,255,0.1); transition: 0.3s;
}
.quick-tool-item:hover .icon-box { border-color: var(--primary); box-shadow: 0 0 10px rgba(139, 92, 246, 0.5); transform: translateY(-3px); }
.quick-tool-item .label { font-size: 0.7rem; color: var(--text-muted); text-align: center; font-family: 'Rajdhani'; }

/* Middle Section */
.middle-dashboard-section { display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 20px; }

.daily-missions-panel, .rewards-panel, .copilot-panel, .section-container, .split-section > div {
    background: var(--surface); border: 1px solid var(--surface-sec); border-radius: 16px; padding: 20px;
}

.missions-cards-row { display: flex; gap: 10px; }
.mission-card { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; flex: 1; display: flex; gap: 10px; }
.mission-card h4 { font-size: 0.8rem; margin: 0 0 5px 0; font-family: 'Inter'; font-weight: normal; }
.mission-reward { display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: 5px; font-family: 'Rajdhani'; font-weight: bold; }

.progress-track { width: 100%; height: 6px; background: rgba(0,0,0,0.5); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 3px; }

.reward-content { display: flex; gap: 15px; align-items: center; }
.chest-img { width: 60px; }
.reward-info p { margin: 0; font-size: 0.8rem; color: var(--text-muted); }
.reward-info h2 { margin: 0; font-size: 1.2rem; }

.copilot-content { display: flex; gap: 15px; align-items: center; }
.copilot-img { width: 60px; border-radius: 12px; border: 1px solid var(--surface-sec); background: rgba(0,0,0,0.5); }
.copilot-info { font-family: 'Rajdhani'; }

/* Cards Layouts */
.horizontal-cards-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
.horiz-card {
    display: flex; gap: 15px; background: var(--bg-dark); border: 1px solid var(--surface-sec); border-radius: 12px; padding: 15px;
    text-decoration: none; transition: 0.3s; align-items: center;
}
.horiz-card:hover { border-color: var(--primary); transform: translateY(-3px); }
.horiz-card-img { width: 60px; height: 60px; border-radius: 8px; background-size: cover; background-position: center; border: 1px solid rgba(255,255,255,0.1); }
.horiz-card-info h4 { margin: 0 0 5px 0; color: #fff; font-size: 0.9rem; }
.horiz-card-info p { margin: 0; font-size: 0.75rem; color: var(--text-muted); font-family: 'Inter'; }

.split-section { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }

.vertical-cards-row { display: flex; gap: 10px; }
.vert-card {
    flex: 1; display: flex; flex-direction: column; background: var(--bg-dark); border: 1px solid var(--surface-sec); border-radius: 12px;
    padding: 10px; text-decoration: none; transition: 0.3s; position: relative;
}
.vert-card:hover { border-color: var(--secondary); transform: translateY(-3px); }
.level-tag { position: absolute; top: 15px; left: 15px; background: var(--secondary); color: #fff; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 4px; z-index: 2; }
.vert-img { width: 100%; height: 100px; border-radius: 8px; background-size: cover; background-position: center; margin-bottom: 10px; }
.vert-card h4 { margin: 0; font-size: 0.75rem; color: #fff; text-align: center; }

.news-list { display: flex; flex-direction: column; gap: 15px; }
.news-item { display: flex; align-items: center; gap: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px; }
.news-text { flex: 1; font-size: 0.85rem; color: #cbd5e1; }
.news-time { font-size: 0.7rem; color: var(--text-muted); }

.mini-tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px; }
.mini-tool-card {
    background: var(--bg-dark); border: 1px solid var(--surface-sec); border-radius: 12px; padding: 15px 5px;
    text-decoration: none; text-align: center; transition: 0.3s; display: flex; flex-direction: column; align-items: center;
}
.mini-tool-card:hover { border-color: var(--primary); transform: translateY(-3px); }
.mini-icon { font-size: 1.5rem; margin-bottom: 5px; }
.mini-tool-card h4 { margin: 0 0 3px 0; font-size: 0.7rem; color: #fff; }
.mini-tool-card p { margin: 0; font-size: 0.6rem; color: var(--text-muted); font-family: 'Inter'; }

.bottom-footer-bar { display: flex; justify-content: space-between; align-items: center; background: var(--surface); border: 1px solid var(--surface-sec); border-radius: 16px; padding: 15px 25px; position: relative; }
.recent-projects, .community-stats { display: flex; align-items: center; gap: 15px; }
.recent-projects h4, .community-stats h4 { margin: 0; font-size: 0.85rem; color: #fff; border-right: 1px solid rgba(255,255,255,0.1); padding-right: 15px; }
.proj-item { display: flex; align-items: center; gap: 8px; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
.proj-img { width: 30px; height: 30px; background: var(--surface-sec); border-radius: 6px; }
.p-info { display: flex; flex-direction: column; }
.p-title { font-size: 0.75rem; color: #fff; font-weight: bold; }
.p-stat { font-size: 0.65rem; color: var(--text-muted); }

.avatars-group { display: flex; }
.av { width: 30px; height: 30px; border-radius: 50%; background: var(--primary); border: 2px solid var(--surface); margin-left: -10px; }
.av.text { background: rgba(0,0,0,0.5); font-size: 10px; display: flex; align-items: center; justify-content: center; color: #fff; }

.chatbot-trigger-icon {
    position: absolute; right: -25px; top: -25px; width: 60px; height: 60px; border-radius: 50%;
    background: url('assets/ai_robot_racer.png') center/cover;
    border: 3px solid var(--secondary); box-shadow: 0 0 20px rgba(217, 70, 239, 0.5); cursor: pointer; transition: 0.3s;
}
.chatbot-trigger-icon:hover { transform: scale(1.1); }

/* ================== RIGHT SIDEBAR ================== */
.apollo-right-sidebar { display: flex; flex-direction: column; gap: 20px; }
.sidebar-card { background: var(--surface); border: 1px solid var(--surface-sec); border-radius: 16px; padding: 20px; }

.profile-header { display: flex; align-items: center; gap: 15px; }
.profile-avatar { width: 60px; height: 60px; border-radius: 50%; border: 2px solid var(--primary); }

.economy-row { display: flex; flex-direction: column; gap: 10px; margin-top: 20px; }
.econ-item { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
.econ-item .icon { font-size: 1.5rem; }
.econ-item .label { display: block; font-size: 0.7rem; font-family: 'Orbitron'; color: #10B981; }
.econ-item .val { font-size: 1.2rem; font-weight: bold; color: #fff; font-family: 'Rajdhani'; }

.achievements-list, .status-list { display: flex; flex-direction: column; gap: 15px; }
.achieve-item, .status-item { display: flex; justify-content: space-between; align-items: center; }
.achieve-item { justify-content: flex-start; gap: 15px; }
.achieve-info h4 { margin: 0; font-size: 0.85rem; color: #fff; font-family: 'Inter'; font-weight: 500; }
.achieve-info p { margin: 0; font-size: 0.75rem; color: var(--text-muted); }
.achieve-xp { margin-left: auto; font-family: 'Rajdhani'; font-weight: bold; }

.status-item .s-icon { width: 30px; text-align: center; }
.status-item .s-name { flex: 1; font-size: 0.85rem; color: #cbd5e1; }
.status-item .s-val { font-family: 'Rajdhani'; font-weight: bold; font-size: 0.9rem; }

/* Buttons */
.btn-outline { background: transparent; border: 1px solid var(--surface-sec); color: #fff; padding: 8px 15px; border-radius: 8px; font-family: 'Rajdhani'; font-weight: bold; cursor: pointer; transition: 0.3s; }
.btn-outline:hover { background: rgba(255,255,255,0.05); }
.btn-full-width { width: 100%; background: var(--surface-sec); border: none; color: #fff; padding: 12px; border-radius: 8px; font-family: 'Rajdhani'; font-weight: bold; cursor: pointer; transition: 0.3s; }
.btn-full-width:hover { background: #3b2488; }
.btn-full-width.primary-purple { background: var(--primary); }
.btn-full-width.primary-purple:hover { background: #7c3aed; }
"""

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css_content)

# =======================================================
# 3. REWRITE HUB.HTML SAFELY
# =======================================================
with open(html_path, 'r', encoding='utf-8') as f:
    original_html = f.read()

# Extract the header block exactly (before <div class="editor-layout"> or <div id="global-3d-bg">)
# Actually, the user's legacy HTML starts with <div id="global-3d-bg"> and then <header>
# We want to replace everything inside <body> up to <!-- FASE 35: Modal de Seleção de Canais -->
match = re.search(r'(<body.*?>)(.*?)(<!-- FASE 35: Modal de Seleção de Canais -->.*)', original_html, re.DOTALL | re.IGNORECASE)

if match:
    body_tag = match.group(1)
    bottom_part = match.group(3)
    
    # Check if there is already a link to apollo_redesign.css, if not add it in head
    head_match = re.search(r'(<head>)(.*?)(</head>)', original_html, re.DOTALL | re.IGNORECASE)
    if head_match:
        head_inner = head_match.group(2)
        if "apollo_redesign.css" not in head_inner:
            head_inner += '    <link rel="stylesheet" href="apollo_redesign.css">\n'
            new_head = f"{head_match.group(1)}{head_inner}{head_match.group(3)}"
            original_html = original_html.replace(head_match.group(0), new_head)
    
    new_html = original_html[:match.start(2)] + new_body_content + bottom_part
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("hub.html rewritten successfully.")
else:
    print("Could not find markers to replace.")

