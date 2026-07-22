/**
 * APOLLO MASCOT FORGE
 * UI para forjar, comprar e alternar entre Avatares (Mascotes/Copilotos).
 */

class MascotForge {
    constructor() {
        this.isOpen = false;
        this.unlockedAvatares = [
            { id: 'ruby', name: 'Ruby (Default)', role: 'Assistente Geral', prompt: 'Você é Ruby, assistente oficial do Apollo Edit.', image: 'assets/ruby_mascot.png' },
            { id: 'master_chef', name: 'Master Chef', role: 'Copiloto de Culinária', prompt: 'Você é um chef francês estressado que julga receitas.', image: 'https://cdn-icons-png.flaticon.com/512/3461/3461836.png' }
        ];

        this.initUI();
        this.bindEvents();
    }

    initUI() {
        const forgeHtml = `
            <div id="mascot-forge-overlay" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); z-index: 20000; justify-content: center; align-items: center;">
                <div id="mascot-forge-modal" style="width: 800px; max-width: 95%; background: #121212; border: 1px solid #333; border-radius: 16px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(90deg, #1f1f1f, #2a1b40); padding: 20px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #8b5cf6;">
                        <h2 style="margin: 0; color: #fff; display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 24px;">🧬</span> Mascot Forge
                        </h2>
                        <button id="close-forge-btn" style="background: transparent; border: none; color: #aaa; font-size: 24px; cursor: pointer; transition: color 0.2s;">&times;</button>
                    </div>

                    <!-- Layout Principal -->
                    <div style="display: flex; height: 500px;">
                        
                        <!-- Menu Lateral -->
                        <div style="width: 250px; background: #1a1a1a; border-right: 1px solid #333; display: flex; flex-direction: column; padding: 15px; gap: 10px;">
                            <h3 style="color: #888; font-size: 12px; text-transform: uppercase; margin: 0 0 10px 0; letter-spacing: 1px;">Sua Frota</h3>
                            <div id="forge-avatar-list" style="display: flex; flex-direction: column; gap: 8px; overflow-y: auto;">
                                <!-- Avatares renderizados via JS -->
                            </div>
                            
                            <div style="margin-top: auto;">
                                <button id="btn-tab-forjar" style="width: 100%; padding: 12px; background: #8b5cf6; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; transition: all 0.2s;">
                                    + Forjar Nova Entidade
                                </button>
                            </div>
                        </div>

                        <!-- Área de Conteúdo -->
                        <div id="forge-content-area" style="flex: 1; padding: 30px; overflow-y: auto;">
                            <!-- Formulario de Forja -->
                            <div id="tab-forjar" style="display: none; animation: fadeIn 0.3s;">
                                <h3 style="color: #fff; margin-top: 0; margin-bottom: 20px;">Sintetizar Nova Identidade</h3>
                                
                                <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                                    <div style="flex: 1;">
                                        <label style="color: #aaa; font-size: 13px;">Nome do Personagem</label>
                                        <input type="text" placeholder="Ex: Sr. Sarcasmo" style="width: 100%; padding: 12px; background: #222; border: 1px solid #444; border-radius: 8px; color: white; margin-top: 5px;">
                                    </div>
                                    <div style="flex: 1;">
                                        <label style="color: #aaa; font-size: 13px;">Profissão / Role</label>
                                        <input type="text" placeholder="Ex: Editor Chefe" style="width: 100%; padding: 12px; background: #222; border: 1px solid #444; border-radius: 8px; color: white; margin-top: 5px;">
                                    </div>
                                </div>

                                <div style="margin-bottom: 20px;">
                                    <label style="color: #aaa; font-size: 13px;">System Prompt (Cérebro da IA)</label>
                                    <textarea placeholder="Descreva como ele deve agir, suas gírias, seu nível de grosseria ou educação..." style="width: 100%; height: 80px; padding: 12px; background: #222; border: 1px solid #444; border-radius: 8px; color: white; margin-top: 5px; resize: none;"></textarea>
                                </div>

                                <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                                    <div style="flex: 1; border: 2px dashed #444; border-radius: 8px; padding: 20px; text-align: center; cursor: pointer; transition: border-color 0.2s;" onmouseover="this.style.borderColor='#8b5cf6'" onmouseout="this.style.borderColor='#444'">
                                        <div style="font-size: 24px; margin-bottom: 10px;">🖼️</div>
                                        <div style="color: #fff; font-size: 14px;">Upload Imagem Base</div>
                                        <div style="color: #777; font-size: 11px; margin-top: 5px;">O motor visual gerará as expressões (feliz, raiva, etc) com base nesta foto.</div>
                                    </div>
                                    <div style="flex: 1; border: 2px dashed #444; border-radius: 8px; padding: 20px; text-align: center; cursor: pointer; transition: border-color 0.2s;" onmouseover="this.style.borderColor='#10b981'" onmouseout="this.style.borderColor='#444'">
                                        <div style="font-size: 24px; margin-bottom: 10px;">🎙️</div>
                                        <div style="color: #fff; font-size: 14px;">Audio Sample (15s)</div>
                                        <div style="color: #777; font-size: 11px; margin-top: 5px;">Para o Voice Cloning (TTS). Suba um áudio limpo do personagem falando.</div>
                                    </div>
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(139, 92, 246, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(139, 92, 246, 0.3);">
                                    <div style="color: #aaa; font-size: 14px;">Custo de Sintetização: <strong style="color: #a78bfa;">1.500 Cristais</strong></div>
                                    <button style="background: #10b981; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);">
                                        Sintetizar & Acordar IA
                                    </button>
                                </div>
                            </div>

                            <!-- Seleção de Avatar -->
                            <div id="tab-selecao" style="display: block; animation: fadeIn 0.3s; text-align: center;">
                                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                                    <img id="preview-avatar-img" src="" style="width: 150px; height: 150px; border-radius: 50%; border: 4px solid #8b5cf6; box-shadow: 0 0 30px rgba(139, 92, 246, 0.3); margin-bottom: 20px; object-fit: cover;">
                                    <h2 id="preview-avatar-name" style="color: #fff; margin: 0 0 5px 0;">Personagem</h2>
                                    <p id="preview-avatar-role" style="color: #a78bfa; font-weight: bold; margin: 0 0 20px 0;">Role</p>
                                    
                                    <div style="background: #222; padding: 15px; border-radius: 8px; color: #ccc; font-size: 14px; max-width: 400px; margin-bottom: 20px; font-style: italic;">
                                        "<span id="preview-avatar-prompt">Prompt</span>"
                                    </div>

                                    <div style="display: flex; flex-direction: column; align-items: center; gap: 5px; margin-bottom: 30px; background: rgba(0,0,0,0.4); padding: 10px 20px; border-radius: 8px; border: 1px dashed #444; width: 100%; max-width: 300px;">
                                        <label for="select-nitro-level" style="color: #ccc; font-size: 14px; font-weight: bold;">Motor de Geração de Voz</label>
                                        <select id="select-nitro-level" style="background: #333; color: white; border: 1px solid #555; padding: 8px; border-radius: 4px; width: 100%; outline: none; cursor: pointer;">
                                            <option value="free">Lento (CPU Compartilhada) - Grátis</option>
                                            <option value="nitro">Rápido (GPU T4) - 2 Cristais/msg</option>
                                            <option value="nitro_master">Instantâneo (GPU Ultra) - 5 Cristais/msg</option>
                                        </select>
                                    </div>

                                    <button id="btn-equip-avatar" style="background: #8b5cf6; color: white; border: none; padding: 12px 40px; border-radius: 20px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); transition: transform 0.2s;">
                                        Equipar Mascote
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <style>
                @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
                .avatar-item { padding: 12px; background: #222; border-radius: 8px; cursor: pointer; border: 1px solid #333; transition: all 0.2s; display: flex; align-items: center; gap: 10px; }
                .avatar-item:hover { background: #2a2a2a; border-color: #555; }
                .avatar-item.active { background: rgba(139, 92, 246, 0.2); border-color: #8b5cf6; }
                .avatar-item img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 2px solid #555; }
                .avatar-item.active img { border-color: #8b5cf6; }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', forgeHtml);

        this.overlay = document.getElementById('mascot-forge-overlay');
        this.listContainer = document.getElementById('forge-avatar-list');
        this.tabForjar = document.getElementById('tab-forjar');
        this.tabSelecao = document.getElementById('tab-selecao');
        
        this.renderList();
        
        // Substituir o alert do apollo_mascot pelo método open() do forge
        if (window.apolloCompanion) {
            window.apolloCompanion.openMascotMenu = () => this.open();
        }
    }

    renderList() {
        this.listContainer.innerHTML = '';
        this.unlockedAvatares.forEach((avatar, index) => {
            const el = document.createElement('div');
            el.className = 'avatar-item' + (index === 0 ? ' active' : '');
            el.innerHTML = `
                <img src="${avatar.image}">
                <div style="display: flex; flex-direction: column;">
                    <span style="color: #fff; font-size: 13px; font-weight: bold;">${avatar.name}</span>
                    <span style="color: #888; font-size: 11px;">${avatar.role}</span>
                </div>
            `;
            el.onclick = () => {
                // Atualiza seleção visual na lista
                document.querySelectorAll('.avatar-item').forEach(i => i.classList.remove('active'));
                el.classList.add('active');
                this.selectAvatar(avatar);
            };
            this.listContainer.appendChild(el);
        });
        
        // Seleciona o primeiro por padrão
        if(this.unlockedAvatares.length > 0) this.selectAvatar(this.unlockedAvatares[0]);
    }

    selectAvatar(avatar) {
        this.tabForjar.style.display = 'none';
        this.tabSelecao.style.display = 'block';
        this.selectedAvatar = avatar;

        document.getElementById('preview-avatar-img').src = avatar.image;
        document.getElementById('preview-avatar-name').innerText = avatar.name;
        document.getElementById('preview-avatar-role').innerText = avatar.role;
        document.getElementById('preview-avatar-prompt').innerText = avatar.prompt;
    }

    bindEvents() {
        document.getElementById('close-forge-btn').addEventListener('click', () => this.close());
        
        // Botão Forjar Tab
        document.getElementById('btn-tab-forjar').addEventListener('click', () => {
            document.querySelectorAll('.avatar-item').forEach(i => i.classList.remove('active'));
            this.tabSelecao.style.display = 'none';
            this.tabForjar.style.display = 'block';
        });

        // Botão Equipar
        document.getElementById('btn-equip-avatar').addEventListener('click', () => {
            this.equipCurrentAvatar();
        });
    }

    equipCurrentAvatar() {
        if(!this.selectedAvatar) return;
        
        if (window.apolloCompanion) {
            // Atualiza as imagens idle/speaking/listening globalmente para o novo avatar
            const img = this.selectedAvatar.image;
            window.apolloCompanion.sprites = {
                idle: img, listening: img, thinking: img, speaking: img, happy: img, sad: img, angry: img
            };
            window.apolloCompanion.setEmotion('idle');
            
            // Toca um áudio ou exibe alerta de sucesso
            if(window.apolloSfx) window.apolloSfx.play('success');
            
            // Fala de entrada
            window.apolloCompanion.speak(`Identidade alterada para ${this.selectedAvatar.name}. Às ordens!`);
        }
        
        this.close();
    }

    open() {
        this.overlay.style.display = 'flex';
        // Efeito sonoro de menu se existir
        if(window.apolloSfx) window.apolloSfx.play('click');
    }

    close() {
        this.overlay.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.apolloMascotForge = new MascotForge();
});
