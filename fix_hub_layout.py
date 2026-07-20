import re

file_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\hub.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the old COFRE DE MOEDAS if it's there
content = re.sub(r'<!-- COFRE DE MOEDAS \(MICRO-ECONOMIA\) -->.*?</div>\s*</div>', '', content, flags=re.DOTALL)

# Remove the old ROLETA DA SORTE if it's there
content = re.sub(r'<!-- GACHA / ROLETA DIÁRIA -->.*?</div>\s*</div>', '', content, flags=re.DOTALL)

# Remove the old OUTDOOR DE PROMOÇÕES
content = re.sub(r'<!-- 📺 OUTDOOR DE PROMOÇÕES \(CAROUSEL\) -->.*?</div>\s*</div>', '', content, flags=re.DOTALL)

# Remove the old SUPER BANNER
super_banner_pattern = r'<!-- 🤖 SUPER BANNER ANIMADO DE I\.A\. E PUBLICIDADE -->.*?</div>\s*</div>\s*</div>'
super_banner_match = re.search(super_banner_pattern, content, flags=re.DOTALL)
if super_banner_match:
    super_banner_html = super_banner_match.group(0)
    content = content.replace(super_banner_html, '')
else:
    super_banner_html = ""

# Now build the new top layout:
# 1. OUTDOOR PROMOÇÕES (mini)
# 2. SUPER BANNER (Diretor IA)
# 3. MISSÃO ATUAL (Stepper)
# 4. MISSÕES DIÁRIAS | ROLETA DA SORTE

new_top_html = """
            <!-- 📺 OUTDOOR DE PROMOÇÕES (MINI) -->
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                <div style="background: #e11d48; color: #fff; padding: 5px 15px; border-radius: 6px; font-weight: bold; font-family: 'Bangers'; font-size: 1.1rem; letter-spacing: 1px;">NOVIDADES</div>
                <div style="flex: 1; background: #1e1e1e; border: 1px solid #444; border-radius: 6px; padding: 5px 15px; color: #cbd5e1; display: flex; align-items: center; overflow: hidden; white-space: nowrap;">
                    <marquee scrollamount="5" style="width: 100%;">
                        🚀 Nova API Nano Banana Disponível no Sistema! &nbsp;&nbsp;|&nbsp;&nbsp; ⛽ Oferta de Fim de Semana: Compre 1.000L de Gasolina e Ganhe o Dobro!
                    </marquee>
                </div>
            </div>

            <!-- 🤖 SUPER BANNER ANIMADO DE I.A. E PUBLICIDADE -->
            <div class="ai-super-banner" style="margin-bottom: 25px;">
                <div class="banner-track">
                    <div class="banner-slide" style="border: 2px solid #9B59B6;">
                        <div class="ai-chat-area">
                            <h2>Diretor de IA</h2>
                            <p>Eu sou a sua I.A. Faço o roteiro, monto o vídeo e publico. Tudo no automático!</p>
                            <button class="btn yellow" style="font-size: 1.5rem;" onclick="demoRacingLoader('premium')">CONVERSAR COM IA 🤖</button>
                        </div>
                        <img src="assets/mascote.png" alt="Apollo Mascote" class="ai-mascot">
                    </div>
                </div>
            </div>

            <!-- ========================================== -->
            <!-- INJEÇÃO DO PAINEL RPG (ESTÉTICA CHATGPT)   -->
            <!-- ========================================== -->
            <div class="mission-tracker-panel" style="background: rgba(20, 15, 30, 0.6); border: 1px solid #4a2b6e; border-radius: 16px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); backdrop-filter: blur(10px);">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h3 style="color: #cbd5e1; margin-top:0; font-size: 0.9rem; text-transform: uppercase; letter-spacing:1px; display:flex; align-items:center; gap:10px;">
                            MISSÃO ATUAL <span style="background: rgba(155, 89, 182, 0.2); color: #e0b0ff; border: 1px solid #9B59B6; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: bold;">EM ANDAMENTO</span>
                        </h3>
                        <h2 style="color: #fff; margin-top: 5px; margin-bottom: 25px; font-size: 1.5rem; font-family: 'Nunito', sans-serif;">Vídeo sobre Bitcoin e o futuro das criptomoedas</h2>
                    </div>
                    <button class="btn" style="background: transparent; border: 1px solid #60a5fa; color: #60a5fa; padding: 5px 15px; border-radius: 8px;">VER STATUS NO NODE</button>
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 5px; z-index: 2;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: rgba(16, 185, 129, 0.2); border: 2px solid #10B981; display: flex; align-items: center; justify-content: center; color: #10B981; font-weight: bold; font-size: 1.2rem;">✓</div>
                        <div style="text-align: center; color: #fff; font-size: 11px; font-weight: bold;">ROTEIRO<br><span style="color:#10B981; font-size:9px;">Concluído</span></div>
                    </div>
                    <div style="flex: 1; height: 4px; background: #10B981; margin: 0 -20px; margin-top: -25px; border-radius: 2px; z-index: 1;"></div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 5px; z-index: 2;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: rgba(16, 185, 129, 0.2); border: 2px solid #10B981; display: flex; align-items: center; justify-content: center; color: #10B981; font-weight: bold; font-size: 1.2rem;">✓</div>
                        <div style="text-align: center; color: #fff; font-size: 11px; font-weight: bold;">PARSER IA<br><span style="color:#10B981; font-size:9px;">Concluído</span></div>
                    </div>
                    <div style="flex: 1; height: 4px; background: linear-gradient(90deg, #10B981 50%, #333 50%); margin: 0 -20px; margin-top: -25px; border-radius: 2px; z-index: 1;"></div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 5px; z-index: 2;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: rgba(245, 158, 11, 0.2); border: 2px solid #facc15; display: flex; align-items: center; justify-content: center; color: #facc15; font-weight: bold; font-size: 1.2rem; animation: pulse 2s infinite;">🎙️</div>
                        <div style="text-align: center; color: #fff; font-size: 11px; font-weight: bold;">VOZ<br><span style="color:#facc15; font-size:9px;">Em andamento</span></div>
                    </div>
                    <div style="flex: 1; height: 4px; background: #333; margin: 0 -20px; margin-top: -25px; border-radius: 2px; z-index: 1;"></div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 5px; z-index: 2;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: #1e1e24; border: 2px solid #444; display: flex; align-items: center; justify-content: center; color: #64748b; font-weight: bold; font-size: 1.2rem;">0</div>
                        <div style="text-align: center; color: #fff; font-size: 11px; font-weight: bold;">VÍDEO<br><span style="color:#64748b; font-size:9px;">Pendente</span></div>
                    </div>
                    <div style="flex: 1; height: 4px; background: #333; margin: 0 -20px; margin-top: -25px; border-radius: 2px; z-index: 1;"></div>
                    <div style="display: flex; flex-direction: column; align-items: center; gap: 5px; z-index: 2;">
                        <div style="width: 40px; height: 40px; border-radius: 50%; background: #1e1e24; border: 2px solid #444; display: flex; align-items: center; justify-content: center; color: #64748b; font-weight: bold; font-size: 1.2rem;">S</div>
                        <div style="text-align: center; color: #fff; font-size: 11px; font-weight: bold;">UPLOAD<br><span style="color:#64748b; font-size:9px;">Pendente</span></div>
                    </div>
                </div>
            </div>

            <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                <!-- MISSÕES DIÁRIAS -->
                <div style="flex: 1; background: rgba(20, 15, 30, 0.6); border: 1px solid #4a2b6e; border-radius: 12px; padding: 20px; backdrop-filter: blur(10px);">
                    <h3 style="margin-top:0; color:#fff; font-family:'Bangers'; letter-spacing:1px; border-bottom: 1px solid #4a2b6e; padding-bottom: 10px;">🏆 MISSÕES DIÁRIAS</h3>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 30px; height: 30px; border-radius: 6px; background: #9B59B6; display: flex; justify-content: center; align-items: center; font-size: 1.2rem;">🎨</div>
                            <div>
                                <div style="color: #fff; font-size: 0.9rem;">Gerar Imagens IA</div>
                            </div>
                        </div>
                        <span style="color: #94a3b8; font-size: 0.8rem;">1/5</span>
                    </div>
                    <div style="width: 100%; height: 6px; background: #333; border-radius: 3px; overflow: hidden; margin-bottom: 15px;">
                        <div style="width: 20%; height: 100%; background: linear-gradient(90deg, #8b5cf6, #d946ef);"></div>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="width: 30px; height: 30px; border-radius: 6px; background: #1ABC9C; display: flex; justify-content: center; align-items: center; font-size: 1.2rem;">⚙️</div>
                            <div>
                                <div style="color: #fff; font-size: 0.9rem;">Lote Assíncrono</div>
                            </div>
                        </div>
                        <span style="color: #10B981; font-weight: bold; font-size: 0.8rem;">PRONTO</span>
                    </div>
                    <div style="width: 100%; height: 6px; background: #333; border-radius: 3px; overflow: hidden;">
                        <div style="width: 100%; height: 100%; background: #10B981;"></div>
                    </div>
                </div>

                <!-- ROLETA DA SORTE -->
                <div style="flex: 1; background: rgba(20, 15, 30, 0.6); border: 1px solid #f59e0b; border-radius: 12px; padding: 20px; backdrop-filter: blur(10px); display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <h3 style="margin-top:0; color:#FFD32A; font-family:'Bangers'; letter-spacing:1px; border-bottom: 1px solid #f59e0b; padding-bottom: 10px;">🎰 ROLETA DA SORTE</h3>
                        <p style="color: #cbd5e1; font-size: 0.9rem; margin-top: 10px;">Assista um anúncio para girar e ganhar Peças Premium ou Minutos de Render!</p>
                    </div>
                    <button class="btn" style="background: linear-gradient(90deg, #f59e0b, #d97706); border: none; font-weight: bold; font-size: 1rem; padding: 10px; width: 100%; border-radius: 8px; color: #fff;">
                        📺 GIRAR AGORA (GRÁTIS)
                    </button>
                </div>
            </div>

            <!-- MERCADO DO CANAL -->
            <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                <div style="flex: 1; background: rgba(20, 15, 30, 0.6); border: 1px solid #3498db; border-radius: 12px; padding: 20px; backdrop-filter: blur(10px);">
                    <h3 style="margin-top:0; color:#3498db; font-family:'Bangers'; letter-spacing:1px; border-bottom: 1px solid #3498db; padding-bottom: 10px;">🛒 MERCADO DO CANAL</h3>
                    <p style="color: #cbd5e1; font-size: 0.9rem;">Caixas de Loot, Prompts e Scripts à venda.</p>
                    <div style="display: flex; gap: 10px; margin-top: 15px;">
                        <button class="btn" style="flex: 1; background: #2980b9; border: none; font-size: 0.9rem; color: #fff;"><span style="color:#FFD32A;">💎</span> 10 CRISTAIS</button>
                        <button class="btn" style="flex: 1; background: #16a085; border: none; font-size: 0.9rem; color: #fff;"><span style="color:#FFD32A;">💎</span> 50 CRISTAIS</button>
                    </div>
                </div>
                <div style="flex: 1; border: 2px dashed #444; border-radius: 12px; display: flex; justify-content: center; align-items: center; color: #666; font-family: 'Bangers'; font-size: 1.5rem;">
                    ESPAÇO VAZIO
                </div>
            </div>
"""

content = content.replace('<main class="main-stage">', '<main class="main-stage">\n' + new_top_html)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Hub layout fixed successfully!")
