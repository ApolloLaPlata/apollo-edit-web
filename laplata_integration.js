document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tool = urlParams.get('tool');
    renderTool(tool);
});

function showNotification(msg, type='info') {
    const notif = document.getElementById('notification');
    document.getElementById('notif-text').innerText = msg;
    
    if(type === 'error') {
        notif.style.background = '#e74c3c';
        notif.querySelector('i').className = 'fas fa-exclamation-triangle';
    } else if(type === 'success') {
        notif.style.background = '#2ecc71';
        notif.querySelector('i').className = 'fas fa-check-circle';
    } else {
        notif.style.background = '#9B59B6';
        notif.querySelector('i').className = 'fas fa-info-circle';
    }

    notif.style.right = '20px';
    setTimeout(() => { notif.style.right = '-300px'; }, 3000);
}

function renderTool(tool) {
    const container = document.getElementById('tool-container');
    
    let html = '';
    let setupFunc = null;

    if (tool === 'prompt') {
        html = `
            <div class="laplata-header">
                <i class="fas fa-magic laplata-icon"></i>
                <div>
                    <h3>Gerador de Prompt</h3>
                    <p>Crie prompts profissionais para gerar imagens com inteligência artificial</p>
                </div>
            </div>
            <form id="laplataForm">
                <div class="input-group">
                    <label>Descrição Principal *</label>
                    <textarea id="mainDescription" placeholder="Descreva a imagem..." required></textarea>
                </div>
                <div style="display:flex; gap:15px; margin-bottom:15px;">
                    <div class="input-group" style="flex:1;">
                        <label>Estilo Visual</label>
                        <select id="visualStyle">
                            <option value="realista">Realista</option>
                            <option value="cinematografico">Cinematográfico</option>
                            <option value="anime">Anime</option>
                            <option value="3d">3D Render</option>
                            <option value="cyberpunk">Cyberpunk</option>
                        </select>
                    </div>
                    <div class="input-group" style="flex:1;">
                        <label>Qualidade</label>
                        <select id="quality">
                            <option value="masterpiece">Obra-prima (Masterpiece)</option>
                            <option value="high">Alta Qualidade (4k, 8k)</option>
                            <option value="normal">Normal</option>
                        </select>
                    </div>
                </div>
                <div class="input-group">
                    <label>Elementos Adicionais</label>
                    <div class="checkbox-group">
                        <label class="checkbox-item"><input type="checkbox" value="iluminação dramática"> Iluminação Dramática</label>
                        <label class="checkbox-item"><input type="checkbox" value="cores vibrantes"> Cores Vibrantes</label>
                        <label class="checkbox-item"><input type="checkbox" value="foco profundo"> Foco Profundo</label>
                        <label class="checkbox-item"><input type="checkbox" value="fotorealista"> Fotorealista</label>
                    </div>
                </div>
                <button type="submit" class="btn-laplata"><i class="fas fa-bolt"></i> GERAR PROMPT</button>
            </form>
            <div class="result-area" id="resultArea" style="display:none;">
                <div class="result-content" id="resultContent"></div>
                <button class="copy-btn" onclick="copyResult()"><i class="fas fa-copy"></i> Copiar Resultado</button>
            </div>
        `;
        setupFunc = () => {
            document.getElementById('laplataForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = {
                    tool: 'prompt',
                    mainDescription: document.getElementById('mainDescription').value,
                    visualStyle: document.getElementById('visualStyle').value,
                    quality: document.getElementById('quality').value,
                    additionalElements: Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value)
                };
                await callBackend(data);
            });
        };
    } else if (tool === 'hashtag') {
        html = `
            <div class="laplata-header">
                <i class="fas fa-hashtag laplata-icon"></i>
                <div>
                    <h3>Gerador de Hashtags</h3>
                    <p>Hashtags virais e estratégicas para redes sociais</p>
                </div>
            </div>
            <form id="laplataForm">
                <div class="input-group">
                    <label>Nicho / Categoria *</label>
                    <input type="text" id="niche" placeholder="Ex: Marketing Digital, Fitness, Gamer..." required>
                </div>
                <div style="display:flex; gap:15px; margin-bottom:15px;">
                    <div class="input-group" style="flex:1;">
                        <label>Mercado</label>
                        <select id="market">
                            <option value="brasil">Brasil (PT-BR)</option>
                            <option value="global">Global (EN)</option>
                        </select>
                    </div>
                    <div class="input-group" style="flex:1;">
                        <label>Quantidade</label>
                        <input type="number" id="quantity" value="15" min="5" max="30">
                    </div>
                </div>
                <button type="submit" class="btn-laplata"><i class="fas fa-bolt"></i> GERAR HASHTAGS</button>
            </form>
            <div class="result-area" id="resultArea" style="display:none;">
                <div class="result-content" id="resultContent"></div>
                <button class="copy-btn" onclick="copyResult()"><i class="fas fa-copy"></i> Copiar Resultado</button>
            </div>
        `;
        setupFunc = () => {
            document.getElementById('laplataForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = {
                    tool: 'hashtag',
                    niche: document.getElementById('niche').value,
                    market: document.getElementById('market').value,
                    quantity: document.getElementById('quantity').value
                };
                await callBackend(data);
            });
        };
    } else {
        html = `
            <div style="text-align:center; padding: 50px;">
                <i class="fas fa-tools" style="font-size: 50px; color: #9B59B6; margin-bottom: 20px;"></i>
                <h3>Ferramenta em Desenvolvimento</h3>
                <p>A ferramenta "${tool}" está sendo integrada ao novo ecossistema.</p>
                <button class="btn-laplata" onclick="window.location.href='hub.html'" style="width:auto; margin-top: 20px;">Voltar ao Hub</button>
            </div>
        `;
    }

    container.innerHTML = html;
    if(setupFunc) setupFunc();
}

async function callBackend(data) {
    document.getElementById('loading').style.display = 'flex';
    document.getElementById('resultArea').style.display = 'none';

    try {
        const response = await fetch('https://api.apolloedit.com/api/laplata/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        
        if (result.success) {
            document.getElementById('resultContent').innerText = result.content;
            document.getElementById('resultArea').style.display = 'block';
            showNotification('Gerado com sucesso!', 'success');
        } else {
            showNotification(result.error || 'Erro ao processar', 'error');
        }
    } catch (e) {
        document.getElementById('loading').style.display = 'none';
        showNotification('Falha de conexão com o servidor', 'error');
        console.error(e);
    }
}

function copyResult() {
    const content = document.getElementById('resultContent').innerText;
    navigator.clipboard.writeText(content).then(() => {
        showNotification('Copiado para a área de transferência!', 'success');
    });
}
