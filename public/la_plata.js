// APIs Keys
const openRouterApiKey = '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';
const geminiApiKey = 'AIzaSyAIZ1suEFBsyoXUf2hLO7J4UWkRBTfFrH4';
const chatgptApiKey = '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';
const grokApiKey = 'xai-YnxdyfVPgVzbt0NR3EkohunMy6mFhhuzffvLiGffu4CI1Ny2Dq21IQ7y7Swbp6QmRi92gbb9hZVZbXy6';

// Configurao da API ativa
let activeApi = 'chatgpt'; // chatgpt, grok, gemini, openrouter

// Estado atual
let currentPage = 'dashboard';

// Inicializao
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    fixSelectVisibility();
    initializeVeo3();
    initializeRoteiroGenerator();
    initializeApiSelector();
    initializeContentOptimizer();
    initializeVisualScriptGenerator();
});

// Funo para corrigir visibilidade dos selects
function fixSelectVisibility() {
    // Adicionar estilos inline para garantir visibilidade
    const style = document.createElement('style');
    style.textContent = `
        select option {
            background: #1f2937 !important;
            color: #ffffff !important;
            padding: 10px !important;
            border: none !important;
            font-size: 0.95rem !important;
        }
        
        select:focus option {
            background: #1f2937 !important;
            color: #ffffff !important;
        }
        
        select option:hover {
            background: rgba(139, 92, 246, 0.3) !important;
            color: #8b5cf6 !important;
        }
        
        select option:checked {
            background: rgba(139, 92, 246, 0.5) !important;
            color: #8b5cf6 !important;
        }
    `;
    document.head.appendChild(style);
    
    // Aplicar estilos diretamente nos selects
    document.querySelectorAll('select').forEach(select => {
        select.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
        select.style.color = '#ffffff';
        select.style.border = '1px solid rgba(255, 255, 255, 0.1)';
        
        // Adicionar evento para garantir visibilidade
        select.addEventListener('focus', function() {
            this.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            this.style.borderColor = '#8b5cf6';
        });
        
        select.addEventListener('blur', function() {
            this.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            this.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        });
    });
}

function initializeApp() {
    showDashboard();
}

function setupEventListeners() {
    // Cards de ferramentas
    document.querySelectorAll('.tool-card').forEach(card => {
        card.addEventListener('click', function() {
            const tool = this.getAttribute('data-tool');
            if (tool) {
                showTool(tool);
            }
        });
    });
    
    // Formulrios
    setupFormListeners();
}

function setupFormListeners() {
    // Formulrio de Prompt
    const promptForm = document.getElementById('promptForm');
    if (promptForm) {
        promptForm.addEventListener('submit', handlePromptSubmit);
    }
    
    // Formulrio de Hashtag
    const hashtagForm = document.getElementById('hashtagForm');
    if (hashtagForm) {
        hashtagForm.addEventListener('submit', handleHashtagSubmit);
    }
    
    // Formulrio de Imagem
    const imageForm = document.getElementById('imageForm');
    if (imageForm) {
        imageForm.addEventListener('submit', handleImageSubmit);
        
        // File input change
        const imageFile = document.getElementById('imageFile');
        if (imageFile) {
            imageFile.addEventListener('change', handleFileSelect);
        }
    }
    
    // Formulrio de Ttulos
    const titulosForm = document.getElementById('titulosForm');
    if (titulosForm) {
        titulosForm.addEventListener('submit', handleTitulosSubmit);
    }
    
    // Formulrio de Descries
    const descricoesForm = document.getElementById('descricoesForm');
    if (descricoesForm) {
        descricoesForm.addEventListener('submit', handleDescricoesSubmit);
    }
    
    // Formulrio de Gerar Imagem
    const gerarImagemForm = document.getElementById('gerarImagemForm');
    if (gerarImagemForm) {
        gerarImagemForm.addEventListener('submit', handleGerarImagemSubmit);
    }
    
    // Formulrio de Tendncias
    const tendenciasForm = document.getElementById('tendenciasForm');
    if (tendenciasForm) {
        tendenciasForm.addEventListener('submit', handleTendenciasSubmit);
    }
}

function showDashboard() {
    hideAllPages();
    document.querySelector('.dashboard').style.display = 'block';
    currentPage = 'dashboard';
}

function showTool(toolName) {
    hideAllPages();
    const toolPage = document.getElementById(toolName);
    if (toolPage) {
        toolPage.classList.add('active');
        currentPage = toolName;
    }
}

function hideAllPages() {
    document.querySelector('.dashboard').style.display = 'none';
    document.querySelectorAll('.tool-page').forEach(page => {
        page.classList.remove('active');
    });
}

// ===== GERADOR DE PROMPT =====
async function handlePromptSubmit(e) {
    e.preventDefault();
    
    const data = {
        mainDescription: document.getElementById('mainDescription').value,
        visualStyle: document.getElementById('visualStyle').value,
        quality: document.getElementById('quality').value,
        lighting: document.getElementById('lighting').value,
        composition: document.getElementById('composition').value,
        language: document.getElementById('language').value,
        additionalElements: Array.from(document.querySelectorAll('#promptForm input[type="checkbox"]:checked')).map(cb => cb.value)
    };
    
    if (!data.mainDescription.trim()) {
        showNotification('Por favor, preencha a descrio principal!', 'error');
        return;
    }
    
    const resultArea = document.getElementById('promptResult');
    resultArea.innerHTML = '<div class="loading">Gerando prompt...</div>';
    
    try {
        const prompt = await generatePrompt(data);
        displayPromptResult(prompt);
    } catch (error) {
        console.error('Erro ao gerar prompt:', error);
        resultArea.innerHTML = '<div class="placeholder"><i class="fas fa-exclamation-triangle"></i><p>Erro ao gerar prompt. Tente novamente.</p></div>';
        showNotification('Erro ao gerar prompt!', 'error');
    }
}

async function generatePrompt(data) {
    const prompt = `Crie um prompt profissional para gerao de imagens com IA baseado nos seguintes parmetros:

Descrio Principal: ${data.mainDescription}
Estilo Visual: ${data.visualStyle}
Qualidade: ${data.quality}
Iluminao: ${data.lighting}
Composio: ${data.composition}
Idioma: ${data.language}
Elementos Adicionais: ${data.additionalElements.join(', ')}

Crie um prompt detalhado e profissional que combine todos esses elementos de forma coesa e criativa. O prompt deve ser otimizado para gerao de imagens com IA e incluir termos tcnicos apropriados.`;

    const response = await callOpenRouterAPI(prompt);
    return response;
}

function displayPromptResult(prompt) {
    const resultArea = document.getElementById('promptResult');
    resultArea.innerHTML = `
        <div class="result-content">
            <div class="result-text">${prompt}</div>
            <button class="copy-btn" onclick="copyToClipboard('${prompt.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i>
                Copiar Prompt
            </button>
        </div>
    `;
}

function clearPromptForm() {
    document.getElementById('promptForm').reset();
    document.getElementById('promptResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-magic"></i>
            <p>Preencha o formulrio e clique em 'Gerar Prompt' para ver o resultado aqui</p>
        </div>
    `;
}

// ===== GERADOR DE HASHTAG =====
async function handleHashtagSubmit(e) {
    e.preventDefault();
    
    const data = {
        niche: document.getElementById('niche').value,
        market: document.getElementById('market').value,
        includeTitle: document.getElementById('includeTitle').checked,
        includeDescription: document.getElementById('includeDescription').checked,
        includeEmojis: document.getElementById('includeEmojis').checked,
        quantity: parseInt(document.getElementById('quantity').value),
        contentType: document.getElementById('contentType').value,
        objectives: Array.from(document.querySelectorAll('#hashtagForm input[type="checkbox"]:checked')).map(cb => cb.value)
    };
    
    const resultArea = document.getElementById('hashtagResult');
    resultArea.innerHTML = '<div class="loading">Gerando hashtags...</div>';
    
    try {
        const hashtags = await generateHashtags(data);
        displayHashtagResult(hashtags);
    } catch (error) {
        console.error('Erro ao gerar hashtags:', error);
        resultArea.innerHTML = '<div class="placeholder"><i class="fas fa-exclamation-triangle"></i><p>Erro ao gerar hashtags. Tente novamente.</p></div>';
        showNotification('Erro ao gerar hashtags!', 'error');
    }
}

async function generateHashtags(data) {
    const prompt = `Crie hashtags estratgicas para redes sociais baseado nos seguintes parmetros:

Nicho/Categoria: ${data.niche}
Mercado/Idioma: ${data.market}
Quantidade: ${data.quantity} hashtags
Tipo de Contedo: ${data.contentType}
Objetivos: ${data.objectives.join(', ')}
Incluir Ttulo: ${data.includeTitle ? 'Sim' : 'No'}
Incluir Descrio: ${data.includeDescription ? 'Sim' : 'No'}
Incluir Emojis: ${data.includeEmojis ? 'Sim' : 'No'}

Crie hashtags que sejam:
- Relevantes para o nicho
- Otimizadas para o mercado/idioma
- Balanceadas entre populares e de nicho
- Apropriadas para o tipo de contedo
- Alinhadas com os objetivos

${data.includeTitle ? 'Inclua um ttulo envolvente sobre o assunto.' : ''}
${data.includeDescription ? 'Inclua uma descrio envolvente sobre o assunto.' : ''}
${data.includeEmojis ? 'Use emojis relevantes nas hashtags.' : ''}

Formate a resposta de forma clara e organizada.`;

    const response = await callOpenRouterAPI(prompt);
    return response;
}

function displayHashtagResult(hashtags) {
    const resultArea = document.getElementById('hashtagResult');
    resultArea.innerHTML = `
        <div class="result-content">
            <div class="result-text">${hashtags}</div>
            <button class="copy-btn" onclick="copyToClipboard('${hashtags.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i>
                Copiar Hashtags
            </button>
        </div>
    `;
}

function clearHashtagForm() {
    document.getElementById('hashtagForm').reset();
    document.getElementById('hashtagResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-hashtag"></i>
            <p>Preencha os campos e clique em "Gerar Hashtags"</p>
        </div>
    `;
}

// ===== DESCREVER IMAGEM =====
function handleFileSelect(e) {
    const file = e.target.files[0];
    const fileName = document.getElementById('fileName');
    
    if (file) {
        fileName.textContent = file.name;
        
        // Validar tamanho (50MB)
        if (file.size > 50 * 1024 * 1024) {
            showNotification('Arquivo muito grande! Mximo 50MB.', 'error');
            e.target.value = '';
            fileName.textContent = 'Nenhum arquivo escolhido';
            return;
        }
        
        // Validar tipo
        if (!file.type.startsWith('image/')) {
            showNotification('Por favor, selecione apenas arquivos de imagem!', 'error');
            e.target.value = '';
            fileName.textContent = 'Nenhum arquivo escolhido';
            return;
        }
    } else {
        fileName.textContent = 'Nenhum arquivo escolhido';
    }
}

async function handleImageSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('imageFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Por favor, selecione uma imagem!', 'error');
        return;
    }
    
    const resultArea = document.getElementById('imageResult');
    resultArea.innerHTML = '<div class="loading">Analisando imagem...</div>';
    
    try {
        const description = await analyzeImage(file);
        displayImageResult(description);
    } catch (error) {
        console.error('Erro ao analisar imagem:', error);
        resultArea.innerHTML = '<div class="placeholder"><i class="fas fa-exclamation-triangle"></i><p>Erro ao analisar imagem. Tente novamente.</p></div>';
        showNotification('Erro ao analisar imagem!', 'error');
    }
}

async function analyzeImage(file) {
    // Converter imagem para base64
    const base64 = await fileToBase64(file);
    
    // Chamar Gemini API
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${geminiApiKey}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            contents: [{
                parts: [
                    {
                        text: "Analise esta imagem e crie uma descrio detalhada e profissional que possa ser usada para recriar a imagem com IA. Inclua detalhes sobre: composio, cores, iluminao, estilo, elementos visuais, texturas, atmosfera e qualquer outro aspecto importante. A descrio deve ser precisa e tcnica, adequada para gerao de imagens com IA."
                    },
                    {
                        inline_data: {
                            mime_type: file.type,
                            data: base64.split(',')[1]
                        }
                    }
                ]
            }]
        })
    });
    
    if (!response.ok) {
        throw new Error(`Erro na API: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.candidates && data.candidates[0] && data.candidates[0].content) {
        return data.candidates[0].content.parts[0].text;
    } else {
        throw new Error('Resposta invlida da API');
    }
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

function displayImageResult(description) {
    const resultArea = document.getElementById('imageResult');
    resultArea.innerHTML = `
        <div class="result-content">
            <div class="result-text">${description}</div>
            <button class="copy-btn" onclick="copyToClipboard('${description.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i>
                Copiar Descrio
            </button>
        </div>
    `;
}

function clearImageForm() {
    document.getElementById('imageForm').reset();
    document.getElementById('fileName').textContent = 'Nenhum arquivo escolhido';
    document.getElementById('imageResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-image"></i>
            <p>A descrio aparecer aqui aps a anlise...</p>
        </div>
    `;
}

async function pasteFromClipboard() {
    try {
        const clipboardItems = await navigator.clipboard.read();
        
        for (const clipboardItem of clipboardItems) {
            for (const type of clipboardItem.types) {
                if (type.startsWith('image/')) {
                    const blob = await clipboardItem.getType(type);
                    const file = new File([blob], 'clipboard-image.png', { type });
                    
                    // Simular seleo de arquivo
                    const fileInput = document.getElementById('imageFile');
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    fileInput.files = dataTransfer.files;
                    
                    // Atualizar nome do arquivo
                    document.getElementById('fileName').textContent = 'clipboard-image.png';
                    
                    showNotification('Imagem colada com sucesso!', 'success');
                    return;
                }
            }
        }
        
        showNotification('Nenhuma imagem encontrada na rea de transferncia!', 'error');
    } catch (error) {
        console.error('Erro ao colar imagem:', error);
        showNotification('Erro ao colar imagem da rea de transferncia!', 'error');
    }
}

// ===== GERADOR DE TTULOS =====
async function handleTitulosSubmit(e) {
    e.preventDefault();
    
    const data = {
        tema: document.getElementById('tituloTema').value,
        plataforma: document.getElementById('tituloPlataforma').value,
        estilo: document.getElementById('tituloEstilo').value,
        quantidade: parseInt(document.getElementById('tituloQuantidade').value)
    };
    
    if (!data.tema.trim()) {
        showNotification('Por favor, preencha o tema!', 'error');
        return;
    }
    
    const resultArea = document.getElementById('titulosResult');
    resultArea.innerHTML = '<div class="loading">Gerando ttulos...</div>';
    
    try {
        const titulos = await generateTitulos(data);
        displayTitulosResult(titulos);
    } catch (error) {
        console.error('Erro ao gerar ttulos:', error);
        resultArea.innerHTML = '<div class="placeholder"><i class="fas fa-exclamation-triangle"></i><p>Erro ao gerar ttulos. Tente novamente.</p></div>';
        showNotification('Erro ao gerar ttulos!', 'error');
    }
}

async function generateTitulos(data) {
    const gatilhosMentais = {
        'curiosidade': 'Use gatilhos de curiosidade como "O que acontece quando...", "Voc nunca vai acreditar...", "Descubra o segredo..."',
        'controversia': 'Use gatilhos de controvrsia como "Por que X est errado", "A verdade que ningum conta sobre...", "Por que todos esto fazendo errado..."',
        'mistrio': 'Use gatilhos de mistrio como "O segredo que ningum conta", "O que eles no querem que voc saiba", "A verdade oculta sobre..."',
        'urgncia': 'Use gatilhos de urgncia como "ltima chance de...", "Antes que seja tarde", "Apenas hoje..."',
        'medo': 'Use gatilhos de medo como "Cuidado com...", "Isso pode destruir...", "O perigo que voc no v..."',
        'ganancia': 'Use gatilhos de ganncia como "Como ganhar R$ X", "Mtodo para ficar rico", "Estratgia que gera lucro..."',
        'autoridade': 'Use gatilhos de autoridade como "Especialista revela...", "Mdico explica...", "Cientista descobre..."',
        'prova-social': 'Use gatilhos de prova social como "Milhes j fizeram...", "Todo mundo est falando sobre...", "Tendncia que est bombando..."',
        'escassez': 'Use gatilhos de escassez como "Apenas X vagas restantes", "Oferta limitada", "ltimas unidades..."',
        'reciprocidade': 'Use gatilhos de reciprocidade como "Presente grtis para voc", "Sem custo para voc", "De graa para seguidores..."',
        'tutorial': 'Use gatilhos de tutorial como "Como fazer X em 5 passos", "Guia completo para...", "Tutorial definitivo..."',
        'reacao': 'Use gatilhos de reao como "Minha reao quando...", "Fiquei chocado com...", "No esperava isso..."',
        'comparacao': 'Use gatilhos de comparao como "X vs Y: Qual  melhor?", "Comparao que vai te surpreender", "Diferenas que ningum conta..."',
        'lista': 'Use gatilhos de lista como "10 coisas que...", "5 motivos para...", "Lista definitiva de..."',
        'pergunta': 'Use gatilhos de pergunta como "Voc sabia que...?", "Por que isso acontece?", "O que voc faria se...?"',
        'shock': 'Use gatilhos de choque como "Isso vai te chocar", "Prepare-se para ficar surpreso", "Voc no vai acreditar..."'
    };

    const prompt = `Crie ${data.quantidade} ttulos virais para ${data.plataforma} baseado no tema: "${data.tema}"

Gatilho Mental: ${data.estilo}
${gatilhosMentais[data.estilo] || 'Use gatilhos mentais poderosos'}

Os ttulos devem ser:
- Chamativos e irresistveis usando o gatilho mental ${data.estilo}
- Otimizados para ${data.plataforma}
- Capazes de gerar cliques e engajamento
- nicos e criativos
- Com emojis quando apropriado
- Entre 40-60 caracteres para melhor performance

Formate a resposta numerando cada ttulo (1., 2., 3., etc.).`;

    const response = await callOpenRouterAPI(prompt);
    return response;
}

function displayTitulosResult(titulos) {
    const resultArea = document.getElementById('titulosResult');
    resultArea.innerHTML = `
        <div class="result-content">
            <div class="result-text">${titulos}</div>
            <button class="copy-btn" onclick="copyToClipboard('${titulos.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i>
                Copiar Ttulos
            </button>
        </div>
    `;
}

function clearTitulosForm() {
    document.getElementById('titulosForm').reset();
    document.getElementById('titulosResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-heading"></i>
            <p>Preencha o formulrio e clique em "Gerar Ttulos"</p>
        </div>
    `;
}

// ===== GERADOR DE DESCRIES =====
async function handleDescricoesSubmit(e) {
    e.preventDefault();
    
    const data = {
        tema: document.getElementById('descricaoTema').value,
        tipo: document.getElementById('descricaoTipo').value,
        tom: document.getElementById('descricaoTom').value,
        tamanho: document.getElementById('descricaoTamanho').value
    };
    
    if (!data.tema.trim()) {
        showNotification('Por favor, preencha o tema!', 'error');
        return;
    }
    
    const resultArea = document.getElementById('descricoesResult');
    resultArea.innerHTML = '<div class="loading">Gerando descrio...</div>';
    
    try {
        const descricao = await generateDescricao(data);
        displayDescricaoResult(descricao);
    } catch (error) {
        console.error('Erro ao gerar descrio:', error);
        resultArea.innerHTML = '<div class="placeholder"><i class="fas fa-exclamation-triangle"></i><p>Erro ao gerar descrio. Tente novamente.</p></div>';
        showNotification('Erro ao gerar descrio!', 'error');
    }
}

async function generateDescricao(data) {
    const tonsDescricao = {
        'formal': 'Use um tom formal, profissional e srio. Linguagem tcnica e acadmica.',
        'casual': 'Use um tom casual, descontrado e amigvel. Linguagem do dia a dia.',
        'divertido': 'Use um tom divertido, com humor e entretenimento. Linguagem descontrada e engraada.',
        'inspirador': 'Use um tom inspirador, motivacional e emocional. Linguagem que motiva e inspira.',
        'urgente': 'Use um tom urgente, criando senso de urgncia. Linguagem que pressiona para ao.',
        'autoridade': 'Use um tom de autoridade, como especialista confivel. Linguagem tcnica e assertiva.',
        'intimo': 'Use um tom ntimo, pessoal e prximo. Linguagem como se fosse um amigo prximo.',
        'dramatico': 'Use um tom dramtico, impactante e emocionante. Linguagem que causa impacto.',
        'educativo': 'Use um tom educativo, informativo e didtico. Linguagem clara e explicativa.',
        'persuasivo': 'Use um tom persuasivo, focado em convencimento e vendas. Linguagem que convence.',
        'conversacional': 'Use um tom conversacional, como uma conversa natural. Linguagem fluida e natural.',
        'misterioso': 'Use um tom misterioso, intrigante e curioso. Linguagem que desperta curiosidade.'
    };

    const tamanhosDescricao = {
        'curta': '1-2 pargrafos curtos (100-200 palavras)',
        'media': '3-4 pargrafos mdios (200-400 palavras)',
        'longa': '5+ pargrafos longos (400+ palavras)'
    };

    const prompt = `Crie uma descrio envolvente para ${data.tipo} baseada no tema: "${data.tema}"

Tom: ${data.tom}
${tonsDescricao[data.tom] || 'Use um tom apropriado'}

Tamanho: ${data.tamanho}
${tamanhosDescricao[data.tamanho] || 'Tamanho mdio'}

A descrio deve ser:
- Envolvente e atrativa usando o tom ${data.tom}
- Adequada para ${data.tipo}
- Do tamanho ${data.tamanho}
- Otimizada para engajamento e interao
- Bem estruturada com pargrafos claros
- Incluir call-to-action quando apropriado
- Usar emojis moderadamente se o tom permitir

Formate a resposta de forma clara e organizada com pargrafos bem definidos.`;

    const response = await callOpenRouterAPI(prompt);
    return response;
}

function displayDescricaoResult(descricao) {
    const resultArea = document.getElementById('descricoesResult');
    resultArea.innerHTML = `
        <div class="result-content">
            <div class="result-text">${descricao}</div>
            <button class="copy-btn" onclick="copyToClipboard('${descricao.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i>
                Copiar Descrio
            </button>
        </div>
    `;
}

function clearDescricoesForm() {
    document.getElementById('descricoesForm').reset();
    document.getElementById('descricoesResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-file-alt"></i>
            <p>Preencha o formulrio e clique em "Gerar Descrio"</p>
        </div>
    `;
}

// ===== GERADOR DE IMAGENS =====
async function handleGerarImagemSubmit(e) {
    e.preventDefault();
    
    const data = {
        prompt: document.getElementById('imagemPrompt').value,
        estilo: document.getElementById('imagemEstilo').value,
        qualidade: document.getElementById('imagemQualidade').value
    };
    
    if (!data.prompt.trim()) {
        showNotification('Por favor, preencha o prompt da imagem!', 'error');
        return;
    }
    
    const resultArea = document.getElementById('gerarImagemResult');
    resultArea.innerHTML = '<div class="loading">Gerando imagem...</div>';
    
    try {
        const imageUrl = await generateImage(data);
        displayImageGenerated(imageUrl);
    } catch (error) {
        console.error('Erro ao gerar imagem:', error);
        resultArea.innerHTML = '<div class="placeholder"><i class="fas fa-exclamation-triangle"></i><p>Erro ao gerar imagem. Tente novamente.</p></div>';
        showNotification('Erro ao gerar imagem!', 'error');
    }
}

async function generateImage(data) {
    // Primeiro, vamos tentar usar o Nano Banana via OpenRouter
    try {
        const prompt = `Generate an image based on: ${data.prompt}

Style: ${data.estilo}
Quality: ${data.qualidade}

Requirements: masterpiece, best quality, highly detailed, professional, 4k, ultra realistic`;

        const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${openRouterApiKey}`,
                'Content-Type': 'application/json',
                'HTTP-Referer': window.location.origin,
                'X-Title': 'APOLLO La PLATA'
            },
            body: JSON.stringify({
                model: "google/gemini-2.5-flash-image-preview",
                messages: [
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                max_tokens: 1000,
                temperature: 0.7
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            if (result.choices && result.choices[0] && result.choices[0].message && result.choices[0].message.content) {
                const content = result.choices[0].message.content;
                
                // Procurar por URLs de imagem na resposta
                const imageUrlMatch = content.match(/https?:\/\/[^\s]+\.(jpg|jpeg|png|gif|webp)/i);
                if (imageUrlMatch) {
                    return imageUrlMatch[0];
                }
            }
        }
    } catch (error) {
        console.log('Nano Banana no disponvel, usando fallback:', error);
    }
    
    // Fallback: Usar Pollinations.ai com prompt otimizado
    const optimizedPrompt = `${data.prompt}, ${data.estilo}, ${data.qualidade}, masterpiece, best quality, highly detailed, professional, 4k, ultra realistic`;
    const encodedPrompt = encodeURIComponent(optimizedPrompt);
    
    return `https://image.pollinations.ai/prompt/${encodedPrompt}?width=1024&height=1024&seed=${Date.now()}&model=flux&nologo=true`;
}

function displayImageGenerated(imageUrl) {
    const resultArea = document.getElementById('gerarImagemResult');
    resultArea.innerHTML = `
        <div class="result-content">
            <div style="text-align: center;">
                <img src="${imageUrl}" alt="Imagem gerada" style="max-width: 100%; border-radius: 8px; margin-bottom: 15px;">
                <br>
                <button class="copy-btn" onclick="downloadImage('${imageUrl}')">
                    <i class="fas fa-download"></i>
                    Baixar Imagem
                </button>
            </div>
        </div>
    `;
}

function downloadImage(imageUrl) {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `imagem-gerada-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showNotification('Imagem baixada com sucesso!', 'success');
}

function clearGerarImagemForm() {
    document.getElementById('gerarImagemForm').reset();
    document.getElementById('gerarImagemResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-paint-brush"></i>
            <p>Preencha o formulrio e clique em "Gerar Imagem"</p>
        </div>
    `;
}

// ===== ANALISADOR DE TENDNCIAS =====
async function handleTendenciasSubmit(e) {
    e.preventDefault();
    
    const data = {
        tema: document.getElementById('tendenciasTema').value,
        plataforma: document.getElementById('tendenciasPlataforma').value,
        periodo: document.getElementById('tendenciasPeriodo').value
    };
    
    if (!data.tema.trim()) {
        showNotification('Por favor, preencha o tema!', 'error');
        return;
    }
    
    const resultArea = document.getElementById('tendenciasResult');
    resultArea.innerHTML = '<div class="loading">Analisando tendncias...</div>';
    
    try {
        const analise = await analyzeTrends(data);
        displayTrendsResult(analise);
    } catch (error) {
        console.error('Erro ao analisar tendncias:', error);
        resultArea.innerHTML = '<div class="placeholder"><i class="fas fa-exclamation-triangle"></i><p>Erro ao analisar tendncias. Tente novamente.</p></div>';
        showNotification('Erro ao analisar tendncias!', 'error');
    }
}

async function analyzeTrends(data) {
    return await analyzeTrendsWithAI(data.tema, data.plataforma, data.periodo);
}

function displayTrendsResult(analise) {
    const resultArea = document.getElementById('tendenciasResult');
    resultArea.innerHTML = `
        <div class="result-content">
            <div class="result-text">${analise}</div>
            <button class="copy-btn" onclick="copyToClipboard('${analise.replace(/'/g, "\\'")}')">
                <i class="fas fa-copy"></i>
                Copiar Anlise
            </button>
        </div>
    `;
}

function clearTendenciasForm() {
    document.getElementById('tendenciasForm').reset();
    document.getElementById('tendenciasResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-chart-line"></i>
            <p>Preencha o formulrio e clique em "Analisar Tendncias"</p>
        </div>
    `;
}

// ===== FUNCIONALIDADES VEO3/FLOW GENERATOR =====

// Inicializao do VEO3
function initializeVeo3() {
    const veo3Input = document.getElementById('veo3MessageInput');
    if (veo3Input) {
        // Permitir envio com Enter (Shift+Enter para nova linha)
        veo3Input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendVeo3Message();
            }
        });
        
        // Auto-resize do textarea
        veo3Input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
}

// Funo para enviar mensagem no VEO3
function sendVeo3Message() {
    const input = document.getElementById('veo3MessageInput');
    const userMessage = input.value.trim();
    if (!userMessage) return;

    addVeo3UserMessage(userMessage);
    input.value = '';
    input.style.height = 'auto';

    // Simular delay de processamento
    setTimeout(() => {
        const response = generateVeo3Response(userMessage);
        addVeo3BotMessage(response);
    }, 800);
}

// Funo para adicionar mensagem do usurio
function addVeo3UserMessage(text) {
    const conversationArea = document.getElementById('veo3ConversationArea');
    
    // Remover welcome message se existir
    const welcome = conversationArea.querySelector('.veo3-welcome');
    if (welcome) {
        welcome.remove();
    }
    
    const div = document.createElement('div');
    div.className = 'veo3-message user';
    div.innerHTML = `
        <div>${text}</div>
        <div class="veo3-message-time">
            ${new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}
        </div>
    `;
    conversationArea.appendChild(div);
    conversationArea.scrollTop = conversationArea.scrollHeight;
}

// Funo para adicionar mensagem do bot
function addVeo3BotMessage(response) {
    const conversationArea = document.getElementById('veo3ConversationArea');
    const div = document.createElement('div');
    div.className = 'veo3-message bot';
    div.innerHTML = `
        <div class="veo3-json-output">${JSON.stringify(response, null, 2)}</div>
        <button class="veo3-copy-btn" onclick="copyVeo3Json(this)">Copiar JSON</button>
        <div class="veo3-message-time">
            ${new Date().toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'})}
        </div>
    `;
    conversationArea.appendChild(div);
    conversationArea.scrollTop = conversationArea.scrollHeight;
}

// Funo para gerar resposta VEO3 aprimorada
function generateVeo3Response(userPrompt) {
    // Obter configuraes do usurio
    const format = document.getElementById('veo3Format')?.value || 'vertical';
    const duration = document.getElementById('veo3Duration')?.value || 'medium';
    const style = document.getElementById('veo3Style')?.value || 'realistic';
    const quality = document.getElementById('veo3Quality')?.value || '8k';
    const music = document.getElementById('veo3Music')?.value || 'ambient';
    const language = document.getElementById('veo3Language')?.value || 'pt-br';

    // As 5 primeiras palavras em ingls
    const englishTitleStart = "Here generated prompt for";
    const englishDescStart = "Detailed description based";

    // Gera hashtags automaticamente melhoradas
    const generateHashtags = (prompt) => {
        const keywords = prompt.toLowerCase().match(/\b\w{4,}\b/g) || [];
        const stopWords = ["um", "uma", "para", "com", "que", "como", "nao", "das", "dos", "esta", "este", "isso", "aqui", "onde", "quando", "porque", "sobre", "entre", "atravs", "durante", "antes", "depois", "acima", "abaixo", "dentro", "fora"];
        
        const filteredKeywords = keywords
            .filter(kw => !stopWords.includes(kw))
            .slice(0, 6);
            
        // Adicionar hashtags baseadas no contexto
        const contextHashtags = [];
        if (prompt.toLowerCase().includes('noite')) contextHashtags.push('#Noite');
        if (prompt.toLowerCase().includes('dia')) contextHashtags.push('#Dia');
        if (prompt.toLowerCase().includes('chuva')) contextHashtags.push('#Chuva');
        if (prompt.toLowerCase().includes('sol')) contextHashtags.push('#Sol');
        if (prompt.toLowerCase().includes('cidade')) contextHashtags.push('#Cidade');
        if (prompt.toLowerCase().includes('natureza')) contextHashtags.push('#Natureza');
        
        const allHashtags = [
            ...filteredKeywords.map(kw => `#${kw.charAt(0).toUpperCase() + kw.slice(1)}`),
            ...contextHashtags
        ];
        
        return [...new Set(allHashtags)].slice(0, 8);
    };

    // Anlise inteligente aprimorada do prompt
    const promptLower = userPrompt.toLowerCase();
    
    // Detectar tipo de cena
    const isNightScene = promptLower.includes('noite') || promptLower.includes('escuro') || promptLower.includes('lua') || promptLower.includes('luzes');
    const isDayScene = promptLower.includes('dia') || promptLower.includes('sol') || promptLower.includes('claro') || promptLower.includes('manh');
    const hasDialogue = promptLower.includes('fala') || promptLower.includes('diz') || promptLower.includes('conversa') || promptLower.includes('falar');
    const isActionScene = promptLower.includes('corre') || promptLower.includes('luta') || promptLower.includes('ao') || promptLower.includes('correndo') || promptLower.includes('perseguio');
    const isRomanceScene = promptLower.includes('romance') || promptLower.includes('amor') || promptLower.includes('beijo') || promptLower.includes('casal');
    const isHorrorScene = promptLower.includes('terror') || promptLower.includes('medo') || promptLower.includes('assustador') || promptLower.includes('fantasma');
    const isComedyScene = promptLower.includes('comdia') || promptLower.includes('engraado') || promptLower.includes('riso') || promptLower.includes('humor');
    const isDramaScene = promptLower.includes('drama') || promptLower.includes('emocional') || promptLower.includes('triste') || promptLower.includes('srio');
    const isSciFiScene = promptLower.includes('futuro') || promptLower.includes('rob') || promptLower.includes('espao') || promptLower.includes('tecnologia');

    // Determinar configuraes baseadas na anlise
    let shotType, cameraAngle, cameraMovement, lighting, mood, musicGenre, durationValue;
    
    if (isActionScene) {
        shotType = "Dynamic action sequence with multiple angles";
        cameraAngle = "Dynamic multi-angle coverage with close-ups";
        cameraMovement = "Fast-paced professional transitions with handheld elements";
        lighting = "High-contrast dramatic lighting";
        mood = "High-energy and intense";
        musicGenre = "High-energy cinematic score with percussion";
        durationValue = "15-30 seconds";
    } else if (isRomanceScene) {
        shotType = "Intimate close-up and medium shots";
        cameraAngle = "Soft, romantic angles with shallow depth";
        cameraMovement = "Gentle, flowing camera movements";
        lighting = "Soft, warm lighting with golden hour tones";
        mood = "Romantic and intimate";
        musicGenre = "Romantic orchestral score";
        durationValue = "30-60 seconds";
    } else if (isHorrorScene) {
        shotType = "Tense, atmospheric shots";
        cameraAngle = "Low angles and Dutch tilts for unease";
        cameraMovement = "Slow, creeping movements";
        lighting = "Dark, shadowy lighting with minimal illumination";
        mood = "Tense and frightening";
        musicGenre = "Dark ambient with dissonant elements";
        durationValue = "30-45 seconds";
    } else if (isComedyScene) {
        shotType = "Wide shots and reaction shots";
        cameraAngle = "Eye-level with comedic timing";
        cameraMovement = "Quick cuts and comedic timing";
        lighting = "Bright, cheerful lighting";
        mood = "Light and humorous";
        musicGenre = "Upbeat, playful score";
        durationValue = "15-45 seconds";
    } else if (isDramaScene) {
        shotType = "Emotional close-ups and medium shots";
        cameraAngle = "Intimate, character-focused angles";
        cameraMovement = "Slow, deliberate movements";
        lighting = "Natural, realistic lighting";
        mood = "Emotional and serious";
        musicGenre = "Emotional orchestral score";
        durationValue = "45-90 seconds";
    } else if (isSciFiScene) {
        shotType = "Futuristic wide shots and close-ups";
        cameraAngle = "Dynamic sci-fi angles with depth";
        cameraMovement = "Smooth, futuristic movements";
        lighting = "Cool, technological lighting with neon accents";
        mood = "Futuristic and mysterious";
        musicGenre = "Electronic sci-fi score";
        durationValue = "30-60 seconds";
    } else {
        shotType = "Cinematic medium shot";
        cameraAngle = "Eye-level with depth";
        cameraMovement = "Smooth professional transitions";
        lighting = isNightScene ? "Dramatic night lighting with neon accents" : "Three-point cinematic lighting";
        mood = "Matches emotional tone described";
        musicGenre = "Custom ambient soundtrack";
        durationValue = "30-60 seconds";
    }

    // Configurar formato e resoluo
    const formatMap = {
        'vertical': 'Vertical (9:16)',
        'horizontal': 'Horizontal (16:9)',
        'square': 'Square (1:1)'
    };

    const qualityMap = {
        '4k': ['3840x2160 (4K)'],
        '8k': ['3840x2160 (4K)', '7680x4320 (8K)'],
        'custom': ['Custom resolution based on requirements']
    };

    // Configurar msica
    const musicMap = {
        'ambient': 'Ambient atmospheric soundtrack',
        'cinematic': 'Cinematic orchestral score',
        'electronic': 'Electronic/EDM soundtrack',
        'none': 'No music - ambient sounds only'
    };

    // Configurar idioma
    const languageMap = {
        'pt-br': 'Brazilian Portuguese',
        'en': 'English',
        'es': 'Spanish',
        'none': 'No dialogue'
    };

    return {
        "titulo": `${englishTitleStart}: "${userPrompt.substring(0, 30)}..."`,
        "descricao": `${englishDescStart} on: "${userPrompt}"`,
        "prompt_details": {
            "visual_description": {
                "shot_type": shotType,
                "subject": "Main character/environment from description",
                "setting": "Detailed environment matching prompt",
                "camera_work": {
                    "angle": cameraAngle,
                    "movement": cameraMovement,
                    "background": "Artistically blurred for focus"
                },
                "lighting": lighting,
                "mood": mood,
                "style": style.charAt(0).toUpperCase() + style.slice(1)
            },
            "audio_script": [
                {
                    "speaker": "Character",
                    "language": languageMap[language],
                    "dialogue_in_pt_br": hasDialogue && language !== 'none'
                        ? "Dilogo natural em portugus baseado na descrio..."
                        : "[Apenas efeitos sonoros ambientais realistas]"
                }
            ],
            "technical_requirements": {
                "resolution": qualityMap[quality],
                "framerate": isActionScene ? 120 : 60,
                "color_space": "10-bit HDR Dolby Vision",
                "render_engine": "Unreal Engine 5.4",
                "face_quality": {
                    "capture": "16K facial reference scan",
                    "texturing": "Hyper-realistic pore-level detail",
                    "consistency": "MetaHuman quality standards"
                }
            }
        },
        "formato": formatMap[format],
        "duracao": durationValue,
        "estilo_visual": style.charAt(0).toUpperCase() + style.slice(1) + " with stylized elements",
        "musica": {
            "genero": musicMap[music],
            "sugestoes": [
                "Professional audio matching scene theme",
                "Copyright-free high quality options",
                "Synchronized with visual pacing"
            ]
        },
        "hashtags": generateHashtags(userPrompt),
        "notas_tecnicas": [
            "ALL TECHNICAL PARAMETERS IN ENGLISH",
            "USER DIALOGUE IN PORTUGUESE-BR",
            "FIRST FIVE WORDS IN ENGLISH",
            "MAXIMUM QUALITY RENDER SETTINGS",
            "LUXURY DESIGN IMPLEMENTATION",
            `FORMAT: ${formatMap[format]}`,
            `DURATION: ${durationValue}`,
            `STYLE: ${style.charAt(0).toUpperCase() + style.slice(1)}`
        ]
    };
}

// Funo para copiar JSON do VEO3
function copyVeo3Json(button) {
    const jsonOutput = button.previousElementSibling;
    navigator.clipboard.writeText(jsonOutput.textContent)
        .then(() => {
            button.textContent = 'Copiado!';
            button.style.background = 'linear-gradient(135deg, #10B981, #059669)';
            setTimeout(() => {
                button.textContent = 'Copiar JSON';
                button.style.background = 'linear-gradient(135deg, #FFD700, #8b5cf6)';
            }, 2000);
        })
        .catch(() => {
            button.textContent = 'Erro';
            button.style.background = 'linear-gradient(135deg, #EF4444, #DC2626)';
            setTimeout(() => {
                button.textContent = 'Copiar JSON';
                button.style.background = 'linear-gradient(135deg, #FFD700, #8b5cf6)';
            }, 2000);
        });
}

// ===== FUNCIONALIDADES AVANADAS VEO3 =====

// Toggle das configuraes
function toggleVeo3Settings() {
    const content = document.getElementById('veo3SettingsContent');
    const toggle = document.querySelector('.toggle-settings i');
    
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        toggle.classList.remove('rotated');
    } else {
        content.classList.add('active');
        toggle.classList.add('rotated');
    }
}

// Aplicar templates pr-definidos
function applyTemplate(templateType) {
    const templates = {
        'action': {
            prompt: 'Uma perseguio emocionante pela cidade  noite, com carros em alta velocidade, luzes neon piscando, e muita adrenalina',
            format: 'horizontal',
            duration: 'short',
            style: 'cinematic',
            music: 'cinematic'
        },
        'romance': {
            prompt: 'Um casal caminhando pela praia ao pr do sol, com ondas suaves, brisa marinha, e um momento romntico e ntimo',
            format: 'vertical',
            duration: 'medium',
            style: 'realistic',
            music: 'cinematic'
        },
        'horror': {
            prompt: 'Uma casa abandonada na floresta escura, com sombras misteriosas, sons assustadores, e uma atmosfera de terror',
            format: 'vertical',
            duration: 'medium',
            style: 'realistic',
            music: 'ambient'
        },
        'comedy': {
            prompt: 'Uma situao engraada no escritrio, com personagens cmicos, expresses exageradas, e muito humor',
            format: 'square',
            duration: 'short',
            style: 'stylized',
            music: 'electronic'
        },
        'drama': {
            prompt: 'Um momento emocional profundo, com personagem em conflito interno, iluminao dramtica, e atmosfera sria',
            format: 'horizontal',
            duration: 'long',
            style: 'realistic',
            music: 'cinematic'
        },
        'sci-fi': {
            prompt: 'Uma nave espacial futurstica voando atravs de nebulosas coloridas, com tecnologia avanada e efeitos visuais impressionantes',
            format: 'horizontal',
            duration: 'medium',
            style: 'stylized',
            music: 'electronic'
        }
    };
    
    const template = templates[templateType];
    if (template) {
        // Aplicar configuraes
        document.getElementById('veo3Format').value = template.format;
        document.getElementById('veo3Duration').value = template.duration;
        document.getElementById('veo3Style').value = template.style;
        document.getElementById('veo3Music').value = template.music;
        
        // Aplicar prompt
        const input = document.getElementById('veo3MessageInput');
        input.value = template.prompt;
        input.focus();
        
        // Feedback visual
        const button = event.target;
        button.style.background = 'linear-gradient(135deg, #10B981, #059669)';
        button.textContent = ' Aplicado!';
        setTimeout(() => {
            button.style.background = 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(255, 215, 0, 0.2))';
            button.textContent = button.textContent.replace(' Aplicado!', button.textContent.includes('') ? ' Ao' : 
                button.textContent.includes('') ? ' Romance' : 
                button.textContent.includes('') ? ' Terror' : 
                button.textContent.includes('') ? ' Comdia' : 
                button.textContent.includes('') ? ' Drama' : ' Fico Cientfica');
        }, 2000);
    }
}

// Limpar histrico de conversas
function clearVeo3History() {
    const conversationArea = document.getElementById('veo3ConversationArea');
    conversationArea.innerHTML = `
        <div class="veo3-welcome">
            <div class="welcome-icon"></div>
            <h3>Bem-vindo ao Gerador VEO3/FLOW</h3>
            <p>Descreva sua cena com detalhes e receba um prompt JSON completo com especificaes tcnicas para VEO3 e FLOW</p>
            <div class="welcome-tips">
                <div class="tip">
                    <i class="fas fa-lightbulb"></i>
                    <span>Use descries detalhadas para melhores resultados</span>
                </div>
                <div class="tip">
                    <i class="fas fa-cog"></i>
                    <span>Configure as opes avanadas acima</span>
                </div>
            </div>
        </div>
    `;
    
    // Feedback visual
    const button = event.target.closest('.action-btn');
    button.style.background = 'linear-gradient(135deg, #10B981, #059669)';
    setTimeout(() => {
        button.style.background = 'rgba(255, 255, 255, 0.1)';
    }, 2000);
}

// Exportar histrico
function exportVeo3History() {
    const messages = document.querySelectorAll('.veo3-message');
    if (messages.length === 0) {
        alert('Nenhuma conversa para exportar!');
        return;
    }
    
    let exportData = {
        timestamp: new Date().toISOString(),
        conversations: []
    };
    
    messages.forEach(message => {
        const isUser = message.classList.contains('user');
        const text = message.querySelector('div:first-child').textContent;
        const time = message.querySelector('.veo3-message-time')?.textContent || '';
        
        if (isUser) {
            exportData.conversations.push({
                type: 'user',
                content: text,
                timestamp: time
            });
        } else {
            const jsonContent = message.querySelector('.veo3-json-output')?.textContent || '';
            exportData.conversations.push({
                type: 'bot',
                content: text,
                json: jsonContent,
                timestamp: time
            });
        }
    });
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `veo3-history-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // Feedback visual
    const button = event.target.closest('.action-btn');
    button.style.background = 'linear-gradient(135deg, #10B981, #059669)';
    setTimeout(() => {
        button.style.background = 'rgba(255, 255, 255, 0.1)';
    }, 2000);
}

// ===== GERADOR DE ROTEIROS =====

// Inicializao do Gerador de Roteiros
function initializeRoteiroGenerator() {
    // Atualizar meta de caracteres inicial
    updateCharacterTarget();
    
    // Adicionar event listeners para contagem em tempo real
    const textareas = ['roteiroTema', 'roteiroObjetivo', 'roteiroPontos'];
    textareas.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', updateRoteiroStats);
        }
    });
}

// Sistema de clculo de durao por caracteres
const SPEECH_RATES = {
    'lenta': { wordsPerMinute: 130, charsPerWord: 5.5 },
    'normal': { wordsPerMinute: 155, charsPerWord: 5.5 },
    'rapida': { wordsPerMinute: 180, charsPerWord: 5.5 },
    'muito-rapida': { wordsPerMinute: 210, charsPerWord: 5.5 }
};

const DURATION_MAP = {
    '5s': 5,
    '10s': 10,
    '15s': 15,
    '30s': 30,
    '1m': 60,
    '2m': 120,
    '5m': 300,
    '10m': 600,
    '15m': 900,
    '20m': 1200,
    '30m': 1800,
    '45m': 2700,
    '1h': 3600,
    '1.5h': 5400,
    '2h': 7200
};

// Atualizar meta de caracteres baseada na durao e velocidade
function updateCharacterTarget() {
    const duration = document.getElementById('roteiroDuracao')?.value || '1m';
    const speed = document.getElementById('roteiroVelocidade')?.value || 'normal';
    
    if (duration === 'custom') {
        document.getElementById('characterTarget').textContent = '~150';
        document.getElementById('durationTarget').textContent = 'Personalizada';
        return;
    }
    
    const durationSeconds = DURATION_MAP[duration];
    const speechRate = SPEECH_RATES[speed];
    
    // Calcular caracteres baseado na durao e velocidade
    const wordsPerSecond = speechRate.wordsPerMinute / 60;
    const charsPerSecond = wordsPerSecond * speechRate.charsPerWord;
    const targetChars = Math.round(durationSeconds * charsPerSecond);
    
    document.getElementById('characterTarget').textContent = `~${targetChars}`;
    document.getElementById('durationTarget').textContent = formatDuration(durationSeconds);
}

// Atualizar estatsticas em tempo real
function updateRoteiroStats() {
    const tema = document.getElementById('roteiroTema')?.value || '';
    const objetivo = document.getElementById('roteiroObjetivo')?.value || '';
    const pontos = document.getElementById('roteiroPontos')?.value || '';
    
    const fullText = `${tema} ${objetivo} ${pontos}`.trim();
    const charCount = fullText.length;
    const wordCount = fullText.split(/\s+/).filter(word => word.length > 0).length;
    
    // Calcular durao estimada
    const speed = document.getElementById('roteiroVelocidade')?.value || 'normal';
    const speechRate = SPEECH_RATES[speed];
    const estimatedSeconds = Math.round((charCount / speechRate.charsPerWord) / (speechRate.wordsPerMinute / 60));
    
    // Atualizar display
    document.getElementById('characterCount').textContent = charCount;
    document.getElementById('wordCount').textContent = wordCount;
    document.getElementById('estimatedDuration').textContent = formatDuration(estimatedSeconds);
}

// Formatar durao em formato legvel
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
    }
}

// Toggle das configuraes de roteiro
function toggleRoteiroSettings() {
    const content = document.getElementById('roteiroSettingsContent');
    const toggle = document.querySelector('#roteiro-generator .toggle-settings i');
    
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        toggle.classList.remove('rotated');
    } else {
        content.classList.add('active');
        toggle.classList.add('rotated');
    }
}

// Aplicar templates de roteiro
function applyRoteiroTemplate(templateType) {
    const templates = {
        'short': {
            duracao: '15s',
            genero: 'entretenimento',
            pegada: 'energico',
            estrutura: 'simples',
            velocidade: 'rapida',
            publico: 'jovens'
        },
        'medium': {
            duracao: '3m',
            genero: 'educativo',
            pegada: 'casual',
            estrutura: 'detalhada',
            velocidade: 'normal',
            publico: 'geral'
        },
        'long': {
            duracao: '20m',
            genero: 'educativo',
            pegada: 'profissional',
            estrutura: 'detalhada',
            velocidade: 'normal',
            publico: 'profissionais'
        },
        'podcast': {
            duracao: '1.5h',
            genero: 'entretenimento',
            pegada: 'relaxado',
            estrutura: 'narrativa',
            velocidade: 'lenta',
            publico: 'adultos'
        },
        'tutorial': {
            duracao: '10m',
            genero: 'educativo',
            pegada: 'profissional',
            estrutura: 'tutorial',
            velocidade: 'normal',
            publico: 'iniciantes'
        },
        'story': {
            duracao: '5m',
            genero: 'entretenimento',
            pegada: 'dramatico',
            estrutura: 'storytelling',
            velocidade: 'normal',
            publico: 'geral'
        }
    };
    
    const template = templates[templateType];
    if (template) {
        // Aplicar configuraes
        Object.keys(template).forEach(key => {
            const element = document.getElementById(`roteiro${key.charAt(0).toUpperCase() + key.slice(1)}`);
            if (element) {
                element.value = template[key];
            }
        });
        
        // Atualizar meta de caracteres
        updateCharacterTarget();
        
        // Feedback visual
        const button = event.target;
        button.style.background = 'linear-gradient(135deg, #10B981, #059669)';
        const originalText = button.textContent;
        button.textContent = ' Aplicado!';
        setTimeout(() => {
            button.style.background = 'linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(255, 215, 0, 0.2))';
            button.textContent = originalText;
        }, 2000);
    }
}

// Gerar roteiro
async function generateRoteiro() {
    const tema = document.getElementById('roteiroTema')?.value.trim();
    if (!tema) {
        alert('Por favor, preencha o tema do roteiro!');
        return;
    }
    
    const objetivo = document.getElementById('roteiroObjetivo')?.value.trim() || '';
    const pontos = document.getElementById('roteiroPontos')?.value.trim() || '';
    const duracao = document.getElementById('roteiroDuracao')?.value || '1m';
    const genero = document.getElementById('roteiroGenero')?.value || 'educativo';
    const pegada = document.getElementById('roteiroPegada')?.value || 'casual';
    const estrutura = document.getElementById('roteiroEstrutura')?.value || 'simples';
    const velocidade = document.getElementById('roteiroVelocidade')?.value || 'normal';
    const publico = document.getElementById('roteiroPublico')?.value || 'geral';
    
    // Calcular meta de caracteres
    const durationSeconds = DURATION_MAP[duracao] || 60;
    const speechRate = SPEECH_RATES[velocidade];
    const wordsPerSecond = speechRate.wordsPerMinute / 60;
    const charsPerSecond = wordsPerSecond * speechRate.charsPerWord;
    const targetChars = Math.round(durationSeconds * charsPerSecond);
    
    // Mostrar loading
    const resultArea = document.getElementById('roteiroResult');
    resultArea.innerHTML = '<div class="loading">Gerando roteiro com IA...</div>';
    
    try {
        // Gerar roteiro com IA
        const roteiroIA = await generateScriptWithAI(tema, objetivo, duracao, genero, pegada, publico);
        
        // Combinar com estrutura local
        const roteiro = generateRoteiroContent({
            tema,
            objetivo,
            pontos,
            duracao: durationSeconds,
            genero,
            pegada,
            estrutura,
            velocidade,
            publico,
            targetChars,
            iaContent: roteiroIA
        });
        
        // Exibir resultado
        displayRoteiroResult(roteiro, targetChars, durationSeconds);
    } catch (error) {
        console.error('Erro ao gerar roteiro com IA:', error);
        // Fallback para gerao local
        const roteiro = generateRoteiroContent({
            tema,
            objetivo,
            pontos,
            duracao: durationSeconds,
            genero,
            pegada,
            estrutura,
            velocidade,
            publico,
            targetChars
        });
        
        displayRoteiroResult(roteiro, targetChars, durationSeconds);
    }
}

// Gerar contedo do roteiro
function generateRoteiroContent(params) {
    const { tema, objetivo, pontos, duracao, genero, pegada, estrutura, publico, targetChars } = params;
    
    // Mapear configuraes para texto
    const generoMap = {
        'educativo': 'educativo e informativo',
        'entretenimento': 'divertido e envolvente',
        'noticias': 'jornalstico e objetivo',
        'tecnologia': 'tcnico e inovador',
        'lifestyle': 'inspirador e pessoal',
        'gaming': 'dinmico e competitivo',
        'culinaria': 'apetitoso e prtico',
        'viagem': 'aventureiro e inspirador',
        'fitness': 'motivador e energtico',
        'negocios': 'profissional e estratgico',
        'comedia': 'engraado e descontrado',
        'drama': 'emocional e profundo'
    };
    
    const pegadaMap = {
        'formal': 'tom formal e respeitoso',
        'casual': 'tom casual e amigvel',
        'divertido': 'tom divertido e descontrado',
        'serio': 'tom srio e respeitoso',
        'inspirador': 'tom inspirador e motivador',
        'dramatico': 'tom dramtico e envolvente',
        'relaxado': 'tom relaxado e tranquilo',
        'energico': 'tom energtico e dinmico',
        'intimo': 'tom ntimo e pessoal',
        'profissional': 'tom profissional e confivel'
    };
    
    const estruturaMap = {
        'simples': ['Introduo', 'Desenvolvimento', 'Concluso'],
        'detalhada': ['Hook', 'Introduo', 'Desenvolvimento', 'Concluso', 'Call to Action'],
        'narrativa': ['Incio', 'Meio', 'Fim'],
        'tutorial': ['Problema', 'Soluo', 'Demonstrao', 'Resumo'],
        'storytelling': ['Contexto', 'Conflito', 'Resoluo', 'Moral']
    };
    
    // Gerar roteiro baseado na estrutura
    const estruturaSecoes = estruturaMap[estrutura] || estruturaMap['simples'];
    const charsPerSecao = Math.floor(targetChars / estruturaSecoes.length);
    
    let roteiro = `ROTEIRO: ${tema.toUpperCase()}\n`;
    roteiro += `Durao: ${formatDuration(duracao)} | Gnero: ${generoMap[genero]} | Tom: ${pegadaMap[pegada]}\n`;
    roteiro += `Pblico: ${publico} | Estrutura: ${estrutura}\n\n`;
    
    if (objetivo) {
        roteiro += `OBJETIVO: ${objetivo}\n\n`;
    }
    
    if (pontos) {
        roteiro += `PONTOS PRINCIPAIS:\n${pontos}\n\n`;
    }
    
    // Gerar cada seo
    estruturaSecoes.forEach((secao, index) => {
        roteiro += `${secao.toUpperCase()}:\n`;
        
        let conteudoSecao = '';
        switch (secao) {
            case 'Hook':
                conteudoSecao = generateHook(tema, genero, pegada, publico);
                break;
            case 'Introduo':
                conteudoSecao = generateIntroducao(tema, objetivo, genero, pegada, publico);
                break;
            case 'Desenvolvimento':
                conteudoSecao = generateDesenvolvimento(tema, pontos, genero, pegada, publico);
                break;
            case 'Concluso':
                conteudoSecao = generateConclusao(tema, objetivo, genero, pegada, publico);
                break;
            case 'Call to Action':
                conteudoSecao = generateCTA(tema, genero, pegada, publico);
                break;
            case 'Incio':
                conteudoSecao = generateInicio(tema, genero, pegada, publico);
                break;
            case 'Meio':
                conteudoSecao = generateMeio(tema, pontos, genero, pegada, publico);
                break;
            case 'Fim':
                conteudoSecao = generateFim(tema, genero, pegada, publico);
                break;
            case 'Problema':
                conteudoSecao = generateProblema(tema, genero, pegada, publico);
                break;
            case 'Soluo':
                conteudoSecao = generateSolucao(tema, genero, pegada, publico);
                break;
            case 'Demonstrao':
                conteudoSecao = generateDemonstracao(tema, genero, pegada, publico);
                break;
            case 'Resumo':
                conteudoSecao = generateResumo(tema, genero, pegada, publico);
                break;
            case 'Contexto':
                conteudoSecao = generateContexto(tema, genero, pegada, publico);
                break;
            case 'Conflito':
                conteudoSecao = generateConflito(tema, genero, pegada, publico);
                break;
            case 'Resoluo':
                conteudoSecao = generateResolucao(tema, genero, pegada, publico);
                break;
            case 'Moral':
                conteudoSecao = generateMoral(tema, genero, pegada, publico);
                break;
            default:
                conteudoSecao = generateConteudoGenerico(tema, secao, genero, pegada, publico);
        }
        
        // Ajustar tamanho do contedo
        if (conteudoSecao.length > charsPerSecao) {
            conteudoSecao = conteudoSecao.substring(0, charsPerSecao - 3) + '...';
        } else if (conteudoSecao.length < charsPerSecao * 0.7) {
            conteudoSecao += generateConteudoAdicional(tema, genero, pegada, publico, charsPerSecao - conteudoSecao.length);
        }
        
        roteiro += conteudoSecao + '\n\n';
    });
    
    roteiro += `---\n`;
    roteiro += `Caracteres: ${roteiro.length}\n`;
    roteiro += `Durao estimada: ${formatDuration(duracao)}\n`;
    roteiro += `Velocidade: ${velocidade}\n`;
    
    return roteiro;
}

// Funes geradoras de contedo para cada seo
function generateHook(tema, genero, pegada, publico) {
    const hooks = {
        'educativo': `Voc sabia que ${tema} pode mudar completamente sua perspectiva?`,
        'entretenimento': `Prepare-se para descobrir algo incrvel sobre ${tema}!`,
        'noticias': `ltimas informaes sobre ${tema} que voc precisa saber.`,
        'tecnologia': `A revoluo em ${tema} est acontecendo agora.`,
        'lifestyle': `Transforme sua vida com essas dicas sobre ${tema}.`,
        'gaming': `O segredo por trs de ${tema} que todo gamer precisa conhecer.`,
        'culinaria': `A receita perfeita de ${tema} que vai impressionar todos.`,
        'viagem': `Descubra os segredos de ${tema} que ningum te conta.`,
        'fitness': `O mtodo definitivo para dominar ${tema}.`,
        'negocios': `A estratgia de ${tema} que est gerando milhes.`,
        'comedia': `A verdade hilria sobre ${tema} que ningum fala.`,
        'drama': `A histria emocionante por trs de ${tema}.`
    };
    return hooks[genero] || `Descubra tudo sobre ${tema} neste vdeo!`;
}

function generateIntroducao(tema, objetivo, genero, pegada, publico) {
    let intro = `Ol pessoal! Hoje vamos falar sobre ${tema}.`;
    
    if (objetivo) {
        intro += ` O objetivo deste vdeo  ${objetivo.toLowerCase()}.`;
    }
    
    intro += ` Vou compartilhar com vocs informaes valiosas que vo fazer toda a diferena.`;
    
    if (publico === 'jovens') {
        intro += ` Galera, vocs vo adorar!`;
    } else if (publico === 'profissionais') {
        intro += ` Profissionais, este contedo  essencial para vocs.`;
    }
    
    return intro;
}

function generateDesenvolvimento(tema, pontos, genero, pegada, publico) {
    let desenvolvimento = `Vamos comear explorando os aspectos fundamentais de ${tema}.`;
    
    if (pontos) {
        desenvolvimento += ` Os pontos principais que vamos abordar so: ${pontos.toLowerCase()}.`;
    }
    
    desenvolvimento += `  importante entender que cada detalhe faz diferena.`;
    
    if (genero === 'educativo') {
        desenvolvimento += ` Vou explicar de forma clara e didtica para que todos possam acompanhar.`;
    } else if (genero === 'entretenimento') {
        desenvolvimento += ` Vamos tornar isso divertido e envolvente!`;
    }
    
    return desenvolvimento;
}

function generateConclusao(tema, objetivo, genero, pegada, publico) {
    let conclusao = `Como vocs podem ver, ${tema}  um tema fascinante e cheio de possibilidades.`;
    
    if (objetivo) {
        conclusao += ` Espero que tenham conseguido ${objetivo.toLowerCase()} com este contedo.`;
    }
    
    conclusao += ` Lembrem-se de praticar e aplicar essas informaes no seu dia a dia.`;
    
    return conclusao;
}

function generateCTA(tema, genero, pegada, publico) {
    const ctas = {
        'educativo': `Se gostaram do contedo, deixem um like e se inscrevam no canal para mais dicas como esta!`,
        'entretenimento': `Curtiram? Deixem um like e comentem qual foi a parte mais divertida!`,
        'noticias': `Para mais notcias como esta, se inscrevam e ativem o sininho!`,
        'tecnologia': `Se inscrevam para ficarem por dentro das ltimas novidades em tecnologia!`,
        'lifestyle': `Se inscrevam para transformarem suas vidas com mais contedos como este!`,
        'gaming': `Se inscrevam para mais gameplays e dicas incrveis!`,
        'culinaria': `Se inscrevam para mais receitas deliciosas!`,
        'viagem': `Se inscrevam para mais dicas de viagem e aventuras!`,
        'fitness': `Se inscrevam para mais dicas de fitness e sade!`,
        'negocios': `Se inscrevam para mais estratgias de negcios!`,
        'comedia': `Se inscrevam para mais diverso e risadas!`,
        'drama': `Se inscrevam para mais histrias emocionantes!`
    };
    return ctas[genero] || `Se inscrevam no canal para mais contedos como este!`;
}

// Funes auxiliares para outras sees
function generateInicio(tema, genero, pegada, publico) {
    return `Tudo comeou quando descobri ${tema}. Foi uma experincia que mudou minha perspectiva completamente.`;
}

function generateMeio(tema, pontos, genero, pegada, publico) {
    return `Durante essa jornada, aprendi que ${tema} envolve muito mais do que imaginamos. ${pontos ? `Especialmente quando se trata de ${pontos.toLowerCase()}.` : ''}`;
}

function generateFim(tema, genero, pegada, publico) {
    return `E assim chegamos ao final desta histria sobre ${tema}. Uma experincia que certamente ficar marcada.`;
}

function generateProblema(tema, genero, pegada, publico) {
    return `Muitas pessoas enfrentam dificuldades com ${tema}.  um problema comum que precisa de uma soluo eficaz.`;
}

function generateSolucao(tema, genero, pegada, publico) {
    return `A soluo para ${tema} est mais prxima do que voc imagina. Vou mostrar o caminho certo.`;
}

function generateDemonstracao(tema, genero, pegada, publico) {
    return `Agora vou demonstrar na prtica como funciona ${tema}. Observem atentamente cada passo.`;
}

function generateResumo(tema, genero, pegada, publico) {
    return `Para resumir, ${tema}  essencial quando aplicado corretamente. Lembrem-se dos pontos principais.`;
}

function generateContexto(tema, genero, pegada, publico) {
    return `A histria de ${tema} comea em um contexto muito especfico. Vamos entender melhor essa situao.`;
}

function generateConflito(tema, genero, pegada, publico) {
    return `Mas nem tudo foi fcil. O conflito principal envolvendo ${tema} trouxe desafios inesperados.`;
}

function generateResolucao(tema, genero, pegada, publico) {
    return `A resoluo veio quando finalmente entendemos a verdade sobre ${tema}. Foi um momento de clareza.`;
}

function generateMoral(tema, genero, pegada, publico) {
    return `A lio que fica sobre ${tema}  que sempre h algo novo para aprender e descobrir.`;
}

function generateConteudoGenerico(tema, secao, genero, pegada, publico) {
    return `Nesta seo sobre ${secao.toLowerCase()}, vamos explorar ${tema} de forma detalhada e envolvente.`;
}

function generateConteudoAdicional(tema, genero, pegada, publico, charsNeeded) {
    const frases = [
        `  importante destacar que cada detalhe faz diferena.`,
        ` Vamos explorar isso mais profundamente.`,
        ` Essa informao  crucial para o sucesso.`,
        ` No percam nenhum detalhe importante.`,
        ` Vamos tornar isso ainda mais interessante.`
    ];
    
    let conteudo = '';
    let charsUsados = 0;
    
    while (charsUsados < charsNeeded && frases.length > 0) {
        const frase = frases[Math.floor(Math.random() * frases.length)];
        if (charsUsados + frase.length <= charsNeeded) {
            conteudo += frase;
            charsUsados += frase.length;
        } else {
            break;
        }
    }
    
    return conteudo;
}

// Exibir resultado do roteiro
function displayRoteiroResult(roteiro, targetChars, durationSeconds) {
    const resultArea = document.getElementById('roteiroResult');
    const charCount = roteiro.length;
    const wordCount = roteiro.split(/\s+/).filter(word => word.length > 0).length;
    
    resultArea.innerHTML = `
        <div class="roteiro-output">${roteiro}</div>
        <div class="roteiro-stats">
            <div class="stats-info">
                <div class="stat-item">
                    <span class="stat-value">${charCount}</span>
                    <span class="stat-label">Caracteres</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${wordCount}</span>
                    <span class="stat-label">Palavras</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${formatDuration(durationSeconds)}</span>
                    <span class="stat-label">Durao</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${Math.round((charCount / targetChars) * 100)}%</span>
                    <span class="stat-label">Meta</span>
                </div>
            </div>
            <div class="roteiro-actions">
                <button class="roteiro-btn" onclick="copyRoteiro()">
                    <i class="fas fa-copy"></i>
                    Copiar
                </button>
                <button class="roteiro-btn secondary" onclick="exportRoteiro()">
                    <i class="fas fa-download"></i>
                    Exportar
                </button>
            </div>
        </div>
    `;
}

// Copiar roteiro
function copyRoteiro() {
    const roteiroOutput = document.querySelector('.roteiro-output');
    if (roteiroOutput) {
        navigator.clipboard.writeText(roteiroOutput.textContent)
            .then(() => {
                const button = event.target.closest('.roteiro-btn');
                button.innerHTML = '<i class="fas fa-check"></i> Copiado!';
                button.style.background = 'linear-gradient(135deg, #10B981, #059669)';
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-copy"></i> Copiar';
                    button.style.background = 'linear-gradient(135deg, #8b5cf6, #7c3aed)';
                }, 2000);
            });
    }
}

// Exportar roteiro
function exportRoteiro() {
    const roteiroOutput = document.querySelector('.roteiro-output');
    if (roteiroOutput) {
        const blob = new Blob([roteiroOutput.textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `roteiro-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        const button = event.target.closest('.roteiro-btn');
        button.innerHTML = '<i class="fas fa-check"></i> Exportado!';
        button.style.background = 'linear-gradient(135deg, #10B981, #059669)';
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-download"></i> Exportar';
            button.style.background = 'rgba(255, 255, 255, 0.1)';
        }, 2000);
    }
}

// Limpar formulrio de roteiro
function clearRoteiroForm() {
    document.getElementById('roteiroTema').value = '';
    document.getElementById('roteiroObjetivo').value = '';
    document.getElementById('roteiroPontos').value = '';
    
    document.getElementById('roteiroResult').innerHTML = `
        <div class="placeholder">
            <i class="fas fa-file-alt"></i>
            <h3>Roteiro Gerado</h3>
            <p>Preencha os campos acima e clique em "Gerar Roteiro"</p>
        </div>
    `;
    
    updateRoteiroStats();
}

// ===== SISTEMA DE APIS INTEGRADO =====

// Inicializao do seletor de API
function initializeApiSelector() {
    updateApiStatus();
}

// Selecionar API
function selectApi(apiName) {
    activeApi = apiName;
    
    // Atualizar interface
    document.querySelectorAll('.api-option').forEach(option => {
        option.classList.remove('active');
    });
    
    document.querySelector(`[data-api="${apiName}"]`).classList.add('active');
    
    // Atualizar status
    updateApiStatus();
    
    // Feedback visual
    showApiChangeNotification(apiName);
}

// Atualizar status da API
function updateApiStatus() {
    const apiStatus = document.getElementById('apiStatus');
    const apiNames = {
        'chatgpt': 'ChatGPT',
        'grok': 'Grok',
        'gemini': 'Gemini',
        'openrouter': 'OpenRouter'
    };
    
    if (apiStatus) {
        apiStatus.querySelector('.api-name').textContent = apiNames[activeApi] || 'ChatGPT';
    }
}

// Notificao de mudana de API
function showApiChangeNotification(apiName) {
    const apiNames = {
        'chatgpt': 'ChatGPT',
        'grok': 'Grok',
        'gemini': 'Gemini',
        'openrouter': 'OpenRouter'
    };
    
    // Criar notificao temporria
    const notification = document.createElement('div');
    notification.className = 'api-notification';
    notification.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <span>API alterada para ${apiNames[apiName]}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Funo principal para chamar APIs
async function callAIAPI(prompt, options = {}) {
    const {
        model = 'default',
        temperature = 0.7,
        maxTokens = 1000,
        systemPrompt = null
    } = options;
    
    try {
        switch (activeApi) {
            case 'chatgpt':
                return await callChatGPTAPI(prompt, { model, temperature, maxTokens, systemPrompt });
            case 'grok':
                return await callGrokAPI(prompt, { model, temperature, maxTokens, systemPrompt });
            case 'gemini':
                return await callGeminiAPI(prompt, { model, temperature, maxTokens, systemPrompt });
            case 'openrouter':
                return await callOpenRouterAPI(prompt, model);
            default:
                return await callChatGPTAPI(prompt, { model, temperature, maxTokens, systemPrompt });
        }
    } catch (error) {
        console.error(`Erro na API ${activeApi}:`, error);
        // Fallback para outra API
        return await fallbackToOtherAPI(prompt, options);
    }
}

// API do ChatGPT
async function callChatGPTAPI(prompt, options = {}) {
    const {
        model = 'gpt-4',
        temperature = 0.7,
        maxTokens = 1000,
        systemPrompt = null
    } = options;
    
    const messages = [];
    
    if (systemPrompt) {
        messages.push({ role: 'system', content: systemPrompt });
    }
    
    messages.push({ role: 'user', content: prompt });
    
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${chatgptApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: model,
            messages: messages,
            temperature: temperature,
            max_tokens: maxTokens
        })
    });
    
    if (!response.ok) {
        throw new Error(`ChatGPT API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.choices[0].message.content;
}

// API do Grok
async function callGrokAPI(prompt, options = {}) {
    const {
        model = 'grok-beta',
        temperature = 0.7,
        maxTokens = 1000,
        systemPrompt = null
    } = options;
    
    const messages = [];
    
    if (systemPrompt) {
        messages.push({ role: 'system', content: systemPrompt });
    }
    
    messages.push({ role: 'user', content: prompt });
    
    const response = await fetch('https://api.x.ai/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${grokApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: model,
            messages: messages,
            temperature: temperature,
            max_tokens: maxTokens
        })
    });
    
    if (!response.ok) {
        throw new Error(`Grok API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.choices[0].message.content;
}

// API do Gemini (j existente, mas melhorada)
async function callGeminiAPI(prompt, options = {}) {
    const {
        model = 'gemini-pro',
        temperature = 0.7,
        maxTokens = 1000,
        systemPrompt = null
    } = options;
    
    let fullPrompt = prompt;
    if (systemPrompt) {
        fullPrompt = `${systemPrompt}\n\n${prompt}`;
    }
    
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${geminiApiKey}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            contents: [{
                parts: [{
                    text: fullPrompt
                }]
            }],
            generationConfig: {
                temperature: temperature,
                maxOutputTokens: maxTokens
            }
        })
    });
    
    if (!response.ok) {
        throw new Error(`Gemini API error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.candidates[0].content.parts[0].text;
}

// Sistema de fallback
async function fallbackToOtherAPI(prompt, options) {
    const fallbackOrder = ['chatgpt', 'grok', 'gemini', 'openrouter'];
    const currentIndex = fallbackOrder.indexOf(activeApi);
    
    for (let i = 0; i < fallbackOrder.length; i++) {
        const nextIndex = (currentIndex + i + 1) % fallbackOrder.length;
        const fallbackApi = fallbackOrder[nextIndex];
        
        try {
            activeApi = fallbackApi;
            updateApiStatus();
            
            switch (fallbackApi) {
                case 'chatgpt':
                    return await callChatGPTAPI(prompt, options);
                case 'grok':
                    return await callGrokAPI(prompt, options);
                case 'gemini':
                    return await callGeminiAPI(prompt, options);
                case 'openrouter':
                    return await callOpenRouterAPI(prompt, options.model);
            }
        } catch (error) {
            console.error(`Fallback para ${fallbackApi} falhou:`, error);
            continue;
        }
    }
    
    throw new Error('Todas as APIs falharam');
}

// Funes especficas para diferentes tipos de contedo
async function generateCreativeContent(prompt, options = {}) {
    const systemPrompt = "Voc  um criador de contedo especializado em criar textos criativos, envolventes e virais. Seja original, criativo e mantenha o tom adequado para o pblico-alvo.";
    return await callAIAPI(prompt, { ...options, systemPrompt });
}

async function generateTechnicalContent(prompt, options = {}) {
    const systemPrompt = "Voc  um especialista tcnico que cria contedo preciso, detalhado e bem estruturado. Use linguagem clara e fornea informaes tcnicas precisas.";
    return await callAIAPI(prompt, { ...options, systemPrompt });
}

async function generateEducationalContent(prompt, options = {}) {
    const systemPrompt = "Voc  um educador experiente que cria contedo didtico, claro e fcil de entender. Use exemplos prticos e explique conceitos de forma acessvel.";
    return await callAIAPI(prompt, { ...options, systemPrompt });
}

async function generateEntertainmentContent(prompt, options = {}) {
    const systemPrompt = "Voc  um criador de contedo de entretenimento que sabe como engajar audincias com humor, criatividade e contedo envolvente. Seja divertido mas respeitoso.";
    return await callAIAPI(prompt, { ...options, systemPrompt });
}

// Funo para anlise de tendncias com IA
async function analyzeTrendsWithAI(topic, platform, period) {
    const prompt = `Analise as tendncias atuais sobre "${topic}" na plataforma ${platform} no perodo de ${period}. 
    Fornea insights sobre:
    1. Tpicos em alta
    2. Palavras-chave populares
    3. Formato de contedo que funciona
    4. Pblico-alvo
    5. Oportunidades de contedo
    6. Sugestes prticas
    
    Seja especfico e acionvel.`;
    
    return await callAIAPI(prompt, {
        temperature: 0.3,
        maxTokens: 1500,
        systemPrompt: "Voc  um analista de tendncias especializado em mdias sociais e marketing digital."
    });
}

// Funo para gerao de roteiros com IA
async function generateScriptWithAI(tema, objetivo, duracao, genero, pegada, publico) {
    const prompt = `Crie um roteiro profissional para um vdeo sobre "${tema}".
    
    Especificaes:
    - Objetivo: ${objetivo}
    - Durao: ${duracao}
    - Gnero: ${genero}
    - Tom/Pegada: ${pegada}
    - Pblico-alvo: ${publico}
    
    O roteiro deve incluir:
    1. Hook inicial (primeiros 3 segundos)
    2. Introduo clara do tema
    3. Desenvolvimento com pontos principais
    4. Concluso forte
    5. Call-to-action
    
    Seja especfico, envolvente e adequado ao pblico-alvo.`;
    
    return await callAIAPI(prompt, {
        temperature: 0.7,
        maxTokens: 2000,
        systemPrompt: "Voc  um roteirista profissional especializado em criar roteiros virais para diferentes plataformas e pblicos."
    });
}

// ===== OTIMIZADOR DE CONTEDO =====

// Inicializao do Otimizador de Contedo
function initializeContentOptimizer() {
    const contentInput = document.getElementById('contentInput');
    if (contentInput) {
        contentInput.addEventListener('input', updateContentStats);
        contentInput.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                optimizeContent();
            }
        });
    }
    
    updateContentStats();
}

// Atualizar estatsticas do contedo
function updateContentStats() {
    const contentInput = document.getElementById('contentInput');
    const contentStats = document.getElementById('contentStats');
    
    if (contentInput && contentStats) {
        const text = contentInput.value;
        const charCount = text.length;
        const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
        
        contentStats.textContent = `${charCount} caracteres  ${wordCount} palavras`;
    }
}

// Alternar configuraes do otimizador
function toggleContentOptimizerSettings() {
    const settingsContent = document.getElementById('contentOptimizerSettings');
    const toggleBtn = document.querySelector('.content-optimizer-settings .toggle-settings i');
    
    if (settingsContent && toggleBtn) {
        settingsContent.classList.toggle('active');
        
        if (settingsContent.classList.contains('active')) {
            toggleBtn.style.transform = 'rotate(180deg)';
        } else {
            toggleBtn.style.transform = 'rotate(0deg)';
        }
    }
}

// Limpar entrada de contedo
function clearContentInput() {
    const contentInput = document.getElementById('contentInput');
    if (contentInput) {
        contentInput.value = '';
        updateContentStats();
    }
}

// Otimizar contedo
async function optimizeContent() {
    const contentInput = document.getElementById('contentInput');
    const resultsArea = document.getElementById('optimizationResults');
    
    if (!contentInput || !contentInput.value.trim()) {
        alert('Por favor, insira o contedo para otimizar!');
        return;
    }
    
    const content = contentInput.value.trim();
    const contentType = document.getElementById('contentType')?.value || 'video';
    const contentTone = document.getElementById('contentTone')?.value || 'professional';
    const targetAudience = document.getElementById('targetAudience')?.value || 'general';
    const contentGoal = document.getElementById('contentGoal')?.value || 'engagement';
    
    // Obter plataformas selecionadas
    const selectedPlatforms = getSelectedPlatforms();
    
    if (selectedPlatforms.length === 0) {
        alert('Por favor, selecione pelo menos uma rede social!');
        return;
    }
    
    // Mostrar loading
    resultsArea.innerHTML = '<div class="loading">Otimizando contedo para todas as redes sociais...</div>';
    
    try {
        // Gerar contedo otimizado
        const optimizedContent = {};
        for (const platform of selectedPlatforms) {
            optimizedContent[platform] = generateLocalPlatformContent({
                content,
                contentType,
                contentTone,
                targetAudience,
                contentGoal,
                platform
            });
        }
        
        displayOptimizationResults(optimizedContent);
    } catch (error) {
        console.error('Erro ao otimizar contedo:', error);
        resultsArea.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Erro na Otimizao</h3>
                <p>No foi possvel otimizar o contedo. Tente novamente.</p>
                <button class="btn-secondary" onclick="optimizeContent()">
                    <i class="fas fa-refresh"></i> Tentar Novamente
                </button>
            </div>
        `;
    }
}

// Obter plataformas selecionadas
function getSelectedPlatforms() {
    const checkboxes = document.querySelectorAll('.platform-option input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// Gerar contedo otimizado
async function generateOptimizedContent(params) {
    const { content, contentType, contentTone, targetAudience, contentGoal, platforms } = params;
    
    const optimizedContent = {};
    
    for (const platform of platforms) {
        try {
            const platformContent = await generatePlatformContent({
                content,
                contentType,
                contentTone,
                targetAudience,
                contentGoal,
                platform
            });
            
            optimizedContent[platform] = platformContent;
        } catch (error) {
            console.error(`Erro ao gerar contedo para ${platform}:`, error);
            // Fallback para gerao local
            optimizedContent[platform] = generateLocalPlatformContent({
                content,
                contentType,
                contentTone,
                targetAudience,
                contentGoal,
                platform
            });
        }
    }
    
    return optimizedContent;
}

// Gerar contedo para plataforma especfica com IA
async function generatePlatformContent(params) {
    const { content, contentType, contentTone, targetAudience, contentGoal, platform } = params;
    
    const platformConfig = getPlatformConfig(platform);
    
    const prompt = `Voc  um especialista em marketing digital e criao de contedo viral. Sua tarefa  analisar o contedo original abaixo e criar verses otimizadas para ${platformConfig.name}, MANTENDO A ESSNCIA E RELEVNCIA DO CONTEDO ORIGINAL.

CONTEDO ORIGINAL (BASE PRINCIPAL):
"${content}"

CONFIGURAES SECUNDRIAS:
- Tipo de Contedo: ${contentType}
- Tom: ${contentTone}
- Pblico-Alvo: ${targetAudience}
- Objetivo: ${contentGoal}
- Plataforma: ${platformConfig.name}

REQUISITOS ESPECFICOS DA PLATAFORMA:
- Ttulo: ${platformConfig.titleMaxLength} caracteres mximo
- Descrio: ${platformConfig.descriptionMaxLength} caracteres mximo
- Hashtags: ${platformConfig.hashtagCount} hashtags relevantes${platformConfig.hasTags ? `
- Tags: Tags para YouTube (separadas por vrgula, mximo ${platformConfig.tagsMaxLength} caracteres)` : ''}

INSTRUES CRTICAS:

TTULO:
- BASEIE-SE PRINCIPALMENTE no contedo original
- Use as palavras-chave e conceitos do contedo original
- Aplique o tom ${contentTone} mantendo a essncia do contedo
- Torne o ttulo clickvel e relevante ao contedo original
- NO ignore o contedo original - ele  a base principal

DESCRIO:
- USE O CONTEDO ORIGINAL como base principal
- Expanda e desenvolva o contedo original com valor agregado
- Inclua um HOOK inicial baseado no contedo original
- Desenvolva os pontos principais do contedo original
- Use emojis estratgicos para engajamento
- Inclua CALL-TO-ACTION especfico para ${contentGoal}
- Adapte o formato para ${platformConfig.name}
- MANTENHA A RELEVNCIA com o contedo original

HASHTAGS:
- Use hashtags baseadas nas palavras-chave do contedo original
- Inclua hashtags trending para ${platformConfig.name}
- Misture hashtags especficas do contedo e populares
- Foque em hashtags que geram engajamento

${platformConfig.hasTags ? `TAGS (YouTube):
- Use tags baseadas no contedo original
- Inclua tags populares do YouTube
- Separe por vrgulas
- Foque em descoberta orgnica` : ''}

IMPORTANTE: O contedo original  a BASE PRINCIPAL. As configuraes secundrias (tom, objetivo, etc.) so apenas para AJUSTAR o formato e estilo, mas NO devem substituir ou ignorar o contedo original.

Formate a resposta EXATAMENTE assim:
TTULO: [ttulo baseado no contedo original]
DESCRIO: [descrio expandindo o contedo original com hook, desenvolvimento e CTA]
HASHTAGS: [hashtag1] [hashtag2] [hashtag3]...${platformConfig.hasTags ? `
TAGS: [tag1, tag2, tag3, ...]` : ''}`;

    const response = await callAIAPI(prompt, {
        temperature: 0.7,
        maxTokens: 800,
        systemPrompt: `Voc  um especialista em marketing digital e otimizao de contedo para redes sociais. Crie ttulos, descries e hashtags que maximizem o engajamento e alcance em cada plataforma especfica.`
    });
    
    return parsePlatformResponse(response, platform);
}

// Gerar contedo local (fallback)
function generateLocalPlatformContent(params) {
    const { content, contentType, contentTone, targetAudience, contentGoal, platform } = params;
    const platformConfig = getPlatformConfig(platform);
    
    // Extrair palavras-chave do contedo
    const keywords = extractKeywords(content);
    
    // Gerar ttulo
    const title = generateLocalTitle(content, keywords, platformConfig, contentTone);
    
    // Gerar descrio
    const description = generateLocalDescription(content, keywords, platformConfig, contentTone, contentGoal);
    
    // Gerar hashtags
    const hashtags = generateLocalHashtags(keywords, contentType, platformConfig);
    
    // Gerar tags para YouTube (se aplicvel)
    let tags = null;
    if (platformConfig.hasTags) {
        tags = generateYouTubeTags(keywords, contentType, platformConfig);
    }
    
    const result = {
        title: title.substring(0, platformConfig.titleMaxLength),
        description: description.substring(0, platformConfig.descriptionMaxLength),
        hashtags: hashtags.slice(0, platformConfig.hashtagCount)
    };
    
    if (tags) {
        result.tags = tags;
    }
    
    return result;
}

// Configuraes das plataformas
function getPlatformConfig(platform) {
    const configs = {
        'instagram': {
            name: 'Instagram',
            titleMaxLength: 125,
            descriptionMaxLength: 2200,
            hashtagCount: 30,
            icon: 'fab fa-instagram'
        },
        'tiktok': {
            name: 'TikTok',
            titleMaxLength: 100,
            descriptionMaxLength: 2200,
            hashtagCount: 5,
            icon: 'fab fa-tiktok'
        },
        'youtube': {
            name: 'YouTube',
            titleMaxLength: 100,
            descriptionMaxLength: 5000,
            hashtagCount: 15,
            tagsMaxLength: 500,
            hasTags: true,
            icon: 'fab fa-youtube'
        },
        'youtube-shorts': {
            name: 'YouTube Shorts',
            titleMaxLength: 100,
            descriptionMaxLength: 5000,
            hashtagCount: 15,
            tagsMaxLength: 500,
            hasTags: true,
            icon: 'fab fa-youtube'
        },
        'twitter': {
            name: 'Twitter',
            titleMaxLength: 280,
            descriptionMaxLength: 280,
            hashtagCount: 3,
            icon: 'fab fa-twitter'
        },
        'threads': {
            name: 'Threads',
            titleMaxLength: 500,
            descriptionMaxLength: 500,
            hashtagCount: 5,
            icon: 'fas fa-comments'
        },
        'facebook': {
            name: 'Facebook',
            titleMaxLength: 100,
            descriptionMaxLength: 63206,
            hashtagCount: 10,
            icon: 'fab fa-facebook'
        },
        'linkedin': {
            name: 'LinkedIn',
            titleMaxLength: 200,
            descriptionMaxLength: 3000,
            hashtagCount: 5,
            icon: 'fab fa-linkedin'
        }
    };
    
    return configs[platform] || configs['instagram'];
}

// Extrair palavras-chave do contedo
function extractKeywords(content) {
    // Primeiro, extrair frases principais do contedo
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);
    
    // Extrair palavras-chave das frases principais
    const words = content.toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(word => word.length > 3);
    
    const wordCount = {};
    words.forEach(word => {
        wordCount[word] = (wordCount[word] || 0) + 1;
    });
    
    // Priorizar palavras que aparecem em frases principais
    const mainWords = Object.entries(wordCount)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)
        .map(([word]) => word);
    
    return mainWords;
}

// Gerar ttulo local
function generateLocalTitle(content, keywords, platformConfig, tone) {
    // Extrair a primeira frase principal do contedo
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);
    const firstSentence = sentences[0] || content;
    
    // Extrair palavras-chave principais do contedo
    const mainKeyword = keywords[0] || '';
    const secondKeyword = keywords[1] || '';
    const thirdKeyword = keywords[2] || '';
    
    // Criar ttulos baseados no contedo real
    const contentBasedTitles = {
        'instagram': {
            'professional': ` ${firstSentence}`,
            'casual': ` ${firstSentence}`,
            'funny': ` ${firstSentence}`,
            'inspiring': ` ${firstSentence}`,
            'educational': ` ${firstSentence}`,
            'dramatic': ` ${firstSentence}`,
            'mysterious': ` ${firstSentence}`,
            'urgent': ` ${firstSentence}`
        },
        'tiktok': {
            'professional': `POV: ${firstSentence}`,
            'casual': `${firstSentence}`,
            'funny': ` ${firstSentence}`,
            'inspiring': ` ${firstSentence}`,
            'educational': `Como ${mainKeyword} funciona`,
            'dramatic': ` ${firstSentence}`,
            'mysterious': ` ${firstSentence}`,
            'urgent': ` ${firstSentence}`
        },
        'youtube': {
            'professional': `${firstSentence} - Guia Completo`,
            'casual': `${firstSentence} - Minha experincia`,
            'funny': ` ${firstSentence}`,
            'inspiring': ` ${firstSentence}`,
            'educational': `Tutorial: ${firstSentence}`,
            'dramatic': ` ${firstSentence} - Situao Crtica`,
            'mysterious': ` ${firstSentence} - Segredos Revelados`,
            'urgent': ` ${firstSentence} - URGENTE`
        },
        'twitter': {
            'professional': `${firstSentence}`,
            'casual': `${firstSentence}`,
            'funny': ` ${firstSentence}`,
            'inspiring': ` ${firstSentence}`,
            'educational': `Thread: ${firstSentence}`,
            'dramatic': ` ${firstSentence}`,
            'mysterious': ` ${firstSentence}`,
            'urgent': ` ${firstSentence}`
        }
    };
    
    const platformTitles = contentBasedTitles[platformConfig.name.toLowerCase()] || contentBasedTitles['instagram'];
    let title = platformTitles[tone] || platformTitles['casual'];
    
    // Limitar o tamanho do ttulo
    if (title.length > platformConfig.titleMaxLength) {
        title = title.substring(0, platformConfig.titleMaxLength - 3) + '...';
    }
    
    return title;
}

// Gerar descrio local
function generateLocalDescription(content, keywords, platformConfig, tone, goal) {
    // Usar o contedo original como base principal
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 10);
    const firstSentence = sentences[0] || content;
    const secondSentence = sentences[1] || '';
    const thirdSentence = sentences[2] || '';
    
    // Extrair palavras-chave principais
    const mainKeyword = keywords[0] || '';
    const secondKeyword = keywords[1] || '';
    const thirdKeyword = keywords[2] || '';
    
    // Criar descries baseadas no contedo real
    const contentBasedDescriptions = {
        'instagram': {
            'professional': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Este  um tpico importante que merece ateno. ${mainKeyword ? `Especialmente quando se trata de ${mainKeyword}, ` : ''} fundamental entender todos os aspectos.\n\n Se voc est interessado em saber mais sobre isso, continue acompanhando para mais informaes valiosas.`,
            'casual': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Que interessante, n? ${mainKeyword ? `Especialmente essa parte sobre ${mainKeyword} ` : ''} algo que todo mundo deveria saber.\n\n Compartilha com seus amigos que tambm vo achar interessante!`,
            'funny': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Srio, isso  mais engraado do que parece! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''} algo que voc no vai esquecer.\n\n Compartilha a para todo mundo rir junto!`,
            'inspiring': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Isso  realmente inspirador! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''}pode mudar a perspectiva de muita gente.\n\n Compartilha para inspirar mais pessoas!`,
            'educational': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Este  um conhecimento valioso! ${mainKeyword ? `Especialmente sobre ${mainKeyword}, ` : ''} importante entender bem.\n\n Salva este post para consultar depois!`,
            'dramatic': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n ATENO: ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''} algo que voc precisa saber.\n\n Compartilha para alertar outras pessoas!`,
            'mysterious': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n H algo mais por trs disso... ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''}tem segredos que poucos conhecem.\n\n Compartilha para descobrir mais juntos!`,
            'urgent': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n URGENTE: ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''} algo que no pode esperar.\n\n Compartilha AGORA para alertar todo mundo!`
        },
        'tiktok': {
            'professional': `POV: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Isso  mais importante do que voc imagina! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''}pode mudar tudo.\n\n Comenta a o que voc acha!`,
            'casual': `${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Srio, isso  mais legal do que parece! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''} incrvel.\n\n Curte se gostou!`,
            'funny': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Isso  hilrio! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''} mais engraado do que voc imagina.\n\n Compartilha para todo mundo rir!`,
            'inspiring': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Isso  inspirador! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''}pode mudar sua vida.\n\n Salva o vdeo!`,
            'educational': `Como ${mainKeyword || 'isso'} funciona: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Aprende algo novo hoje! ${mainKeyword ? `Especialmente sobre ${mainKeyword} ` : ''} conhecimento valioso.\n\n Aplica as dicas e me conta!`,
            'dramatic': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Voc precisa saber disso! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''} srio.\n\n Compartilha para alertar!`,
            'mysterious': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n H algo mais aqui... ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''}tem segredos.\n\n Descobre mais comigo!`,
            'urgent': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n URGENTE! ${mainKeyword ? `Especialmente ${mainKeyword} ` : ''}no pode esperar.\n\n Compartilha AGORA!`
        },
        'youtube': {
            'professional': `Neste vdeo, vou te explicar: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n O que voc vai aprender:\n ${mainKeyword ? `Como ${mainKeyword} funciona` : 'Os conceitos principais'}\n ${secondKeyword ? `A relao com ${secondKeyword}` : 'Por que isso  importante'}\n ${thirdKeyword ? `Como ${thirdKeyword} se conecta` : 'Aplicaes prticas'}\n Dicas e insights valiosos\n\n Este  um contedo que vai agregar muito valor  sua vida!`,
            'casual': `Oi galera! No vdeo de hoje vou falar sobre: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Vou te mostrar:\n ${mainKeyword ? `Como ${mainKeyword} funciona` : 'Os detalhes importantes'}\n ${secondKeyword ? `A conexo com ${secondKeyword}` : 'Por que isso importa'}\n ${thirdKeyword ? `Como ${thirdKeyword} se relaciona` : 'Exemplos prticos'}\n Minha experincia pessoal\n\n Espero que vocs gostem!`,
            'funny': ` Pessoal, vocs no vo acreditar: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Neste vdeo hilrio:\n ${mainKeyword ? `Como ${mainKeyword} funciona` : 'Os detalhes engraados'}\n ${secondKeyword ? `A relao com ${secondKeyword}` : 'Por que isso  engraado'}\n ${thirdKeyword ? `Como ${thirdKeyword} se conecta` : 'Situaes cmicas'}\n Muitas risadas garantidas\n\n Preparem-se para rir muito!`,
            'inspiring': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Neste vdeo inspirador:\n ${mainKeyword ? `Como ${mainKeyword} pode mudar sua vida` : 'A transformao possvel'}\n ${secondKeyword ? `A conexo com ${secondKeyword}` : 'Por que isso  inspirador'}\n ${thirdKeyword ? `Como ${thirdKeyword} se relaciona` : 'Histrias de superao'}\n Lies de vida valiosas\n\n Este vdeo vai te motivar!`,
            'educational': ` Tutorial completo: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n O que voc vai aprender:\n ${mainKeyword ? `Como ${mainKeyword} funciona` : 'Os conceitos fundamentais'}\n ${secondKeyword ? `A relao com ${secondKeyword}` : 'Por que isso  importante'}\n ${thirdKeyword ? `Como ${thirdKeyword} se conecta` : 'Aplicaes prticas'}\n Passo a passo detalhado\n Dicas e truques\n\n Conhecimento que vai fazer a diferena!`,
            'dramatic': ` SITUAO CRTICA: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Neste vdeo urgente:\n ${mainKeyword ? `Como ${mainKeyword} afeta voc` : 'O que voc precisa saber'}\n ${secondKeyword ? `A relao com ${secondKeyword}` : 'Por que isso  crtico'}\n ${thirdKeyword ? `Como ${thirdKeyword} se conecta` : 'Situaes de emergncia'}\n Aes imediatas necessrias\n\n Este vdeo pode salvar vidas!`,
            'mysterious': ` SEGREDOS REVELADOS: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Neste vdeo misterioso:\n ${mainKeyword ? `Os segredos de ${mainKeyword}` : 'O que eles no querem que voc saiba'}\n ${secondKeyword ? `A conexo com ${secondKeyword}` : 'Por que isso  secreto'}\n ${thirdKeyword ? `Como ${thirdKeyword} se relaciona` : 'Descobertas surpreendentes'}\n Verdades ocultas\n\n Prepare-se para descobrir a verdade!`,
            'urgent': ` URGENTE: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Neste vdeo de emergncia:\n ${mainKeyword ? `Como ${mainKeyword} afeta voc AGORA` : 'O que voc precisa saber AGORA'}\n ${secondKeyword ? `A relao com ${secondKeyword}` : 'Por que isso  urgente'}\n ${thirdKeyword ? `Como ${thirdKeyword} se conecta` : 'Situaes crticas'}\n Aes imediatas\n\n Este vdeo no pode esperar!`
        },
        'twitter': {
            'professional': `${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Thread sobre ${mainKeyword || 'este tpico'}: insights importantes que voc precisa saber.\n\n Retweet se foi til!`,
            'casual': `${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Dica rpida sobre ${mainKeyword || 'isso'}:  mais interessante do que parece!\n\n Compartilha a!`,
            'funny': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n ${mainKeyword || 'Isso'}  mais engraado do que voc imagina!\n\n Retweet para todo mundo rir!`,
            'inspiring': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n ${mainKeyword || 'Isso'} pode mudar sua perspectiva!\n\n Compartilha para inspirar!`,
            'educational': `Thread: ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n Conhecimento valioso sobre ${mainKeyword || 'este tpico'}.\n\n Salva o tweet!`,
            'dramatic': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n ${mainKeyword || 'Isso'}  mais srio do que parece!\n\n Retweet para alertar!`,
            'mysterious': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n ${mainKeyword || 'Isso'} tem segredos que poucos conhecem!\n\n Descobre mais comigo!`,
            'urgent': ` ${firstSentence}${secondSentence ? ` ${secondSentence}` : ''}${thirdSentence ? ` ${thirdSentence}` : ''}\n\n ${mainKeyword || 'Isso'}  URGENTE!\n\n Retweet AGORA!`
        }
    };
    
    const platformName = platformConfig.name.toLowerCase();
    const platformDescriptions = contentBasedDescriptions[platformName] || contentBasedDescriptions['instagram'];
    let description = platformDescriptions[tone] || platformDescriptions['casual'];
    
    // Adicionar call-to-action baseado no objetivo
    const ctas = {
        'engagement': {
            'instagram': '\n\n Deixe nos comentrios: o que voc acha sobre isso?\n Curta se este post te ajudou!\n Compartilhe com quem precisa ver!',
            'tiktok': '\n\n Comenta a: voc j sabia disso?\n Curte se gostou!\n Compartilha com os amigos!',
            'youtube': '\n\n Deixe seu comentrio: qual parte foi mais interessante?\n Curta o vdeo se te ajudou!\n Ative o sininho para no perder os prximos!\n Compartilhe com quem precisa ver!',
            'twitter': '\n\n O que voc acha? Comenta a!\n Retweet se foi til!\n Compartilha com a galera!'
        },
        'sales': {
            'instagram': '\n\n Link na bio para mais informaes!\n Quer saber mais? Me chama no DM!\n Agende uma conversa!',
            'tiktok': '\n\n Link no perfil para mais detalhes!\n Quer saber mais? Me chama!',
            'youtube': '\n\n Links teis na descrio!\n Quer resultados profissionais? Entre em contato!\n Email para parcerias na descrio!',
            'twitter': '\n\n Link no perfil para mais info!\n DM aberto para conversas!'
        },
        'awareness': {
            'instagram': '\n\n Compartilhe este post para espalhar a informao!\n Marque seus amigos que precisam ver!\n Salve o post para consultar depois!',
            'tiktok': '\n\n Compartilha com todo mundo!\n Marca os amigos!\n Salva o vdeo!',
            'youtube': '\n\n Compartilhe este vdeo com quem precisa ver!\n Marque seus amigos nos comentrios!\n Salve o vdeo para assistir depois!',
            'twitter': '\n\n Retweet para espalhar a informao!\n Marca a galera que precisa ver!\n Salva o tweet!'
        },
        'education': {
            'instagram': '\n\n Salve este post para consultar depois!\n Aplique as dicas e me conta o resultado!\n Quer mais contedo assim? Me segue!',
            'tiktok': '\n\n Salva o vdeo para no esquecer!\n Aplica as dicas e me conta!\n Me segue para mais contedo!',
            'youtube': '\n\n Salve o vdeo para assistir depois!\n Aplique as dicas e me conta o resultado!\n Ative o sininho para mais tutoriais!',
            'twitter': '\n\n Salva o tweet para consultar depois!\n Aplica as dicas e me conta!\n Me segue para mais contedo!'
        }
    };
    
    const cta = ctas[goal]?.[platformName] || ctas['engagement'][platformName] || ctas['engagement']['instagram'];
    description += cta;
    
    // Limitar o tamanho da descrio
    if (description.length > platformConfig.descriptionMaxLength) {
        description = description.substring(0, platformConfig.descriptionMaxLength - 3) + '...';
    }
    
    return description;
}

// Gerar hashtags locais
function generateLocalHashtags(keywords, contentType, platformConfig) {
    // Hashtags baseadas nas palavras-chave principais do contedo
    const baseHashtags = keywords.slice(0, 5).map(keyword => `#${keyword}`);
    
    // Hashtags especficas por tipo de contedo
    const typeHashtags = {
        'video': ['#video', '#conteudo', '#criativo', '#entretenimento', '#viral'],
        'post': ['#post', '#conteudo', '#dica', '#informacao', '#util'],
        'story': ['#story', '#stories', '#conteudo', '#viral', '#trending'],
        'reel': ['#reel', '#reels', '#viral', '#entretenimento', '#fyp'],
        'article': ['#artigo', '#leitura', '#conhecimento', '#educacao', '#aprenda'],
        'tutorial': ['#tutorial', '#dica', '#aprenda', '#como', '#passoapasso'],
        'review': ['#review', '#avaliacao', '#opiniao', '#analise', '#teste'],
        'news': ['#noticia', '#atualidade', '#informacao', '#novidades', '#trending']
    };
    
    // Hashtags especficas por plataforma
    const platformHashtags = {
        'instagram': ['#instagram', '#insta', '#foto', '#feed', '#stories'],
        'tiktok': ['#tiktok', '#fyp', '#viral', '#trending', '#foryou'],
        'youtube': ['#youtube', '#video', '#subscribe', '#like', '#compartilhe'],
        'youtube-shorts': ['#shorts', '#youtube', '#viral', '#fyp', '#trending'],
        'twitter': ['#twitter', '#tweet', '#trending', '#thread', '#compartilhe'],
        'threads': ['#threads', '#meta', '#social', '#conversa', '#comunidade'],
        'facebook': ['#facebook', '#fb', '#social', '#compartilhe', '#curtir'],
        'linkedin': ['#linkedin', '#professional', '#career', '#networking', '#negocios']
    };
    
    // Hashtags populares e trending
    const trendingHashtags = {
        'instagram': ['#brasil', '#portugues', '#conteudo', '#criativo', '#inspiracao'],
        'tiktok': ['#brasil', '#portugues', '#fyp', '#viral', '#trending'],
        'youtube': ['#brasil', '#portugues', '#video', '#conteudo', '#subscribe'],
        'youtube-shorts': ['#brasil', '#portugues', '#shorts', '#viral', '#fyp'],
        'twitter': ['#brasil', '#portugues', '#trending', '#noticias', '#debate'],
        'threads': ['#brasil', '#portugues', '#conversa', '#comunidade', '#social'],
        'facebook': ['#brasil', '#portugues', '#social', '#comunidade', '#compartilhe'],
        'linkedin': ['#brasil', '#portugues', '#carreira', '#negocios', '#networking']
    };
    
    const typeTags = typeHashtags[contentType] || ['#conteudo', '#dica'];
    const platformTags = platformHashtags[platformConfig.name.toLowerCase()] || ['#social'];
    const trendingTags = trendingHashtags[platformConfig.name.toLowerCase()] || ['#brasil', '#portugues'];
    
    // Combinar todas as hashtags, priorizando as do contedo
    const allHashtags = [...baseHashtags, ...typeTags, ...platformTags, ...trendingTags];
    
    // Remover duplicatas e limitar
    const uniqueHashtags = [...new Set(allHashtags)];
    
    return uniqueHashtags.slice(0, platformConfig.hashtagCount);
}

// Gerar tags para YouTube
function generateYouTubeTags(keywords, contentType, platformConfig) {
    const mainKeyword = keywords[0] || 'conteudo';
    const secondKeyword = keywords[1] || '';
    const thirdKeyword = keywords[2] || '';
    
    // Tags baseadas nas palavras-chave principais do contedo
    const baseTags = keywords.slice(0, 8).map(keyword => keyword.toLowerCase());
    
    // Tags especficas por tipo de contedo
    const typeTags = {
        'video': ['video', 'conteudo', 'criativo', 'entretenimento', 'viral', 'youtube'],
        'post': ['post', 'conteudo', 'dica', 'informacao', 'util', 'youtube'],
        'story': ['story', 'stories', 'conteudo', 'viral', 'trending', 'youtube'],
        'reel': ['reel', 'reels', 'viral', 'entretenimento', 'fyp', 'youtube'],
        'article': ['artigo', 'leitura', 'conhecimento', 'educacao', 'aprenda', 'youtube'],
        'tutorial': ['tutorial', 'dica', 'aprenda', 'como fazer', 'passo a passo', 'youtube'],
        'review': ['review', 'avaliacao', 'opiniao', 'analise', 'teste', 'youtube'],
        'news': ['noticia', 'atualidade', 'informacao', 'novidades', 'trending', 'youtube']
    };
    
    // Tags populares e trending do YouTube
    const popularTags = [
        'brasil', 'portugues', 'youtube', 'video', 'conteudo',
        'entretenimento', 'educativo', 'dicas', 'tutorial',
        'review', 'analise', 'opiniao', 'viral', 'trending',
        'subscribe', 'like', 'compartilhe', 'comentario',
        'canal', 'youtuber', 'criador', 'influencer'
    ];
    
    // Tags especficas por nicho (baseadas nas palavras-chave do contedo)
    const nicheTags = [];
    const allKeywords = keywords.join(' ').toLowerCase();
    
    if (allKeywords.includes('tecnologia') || allKeywords.includes('tech') || allKeywords.includes('digital')) {
        nicheTags.push('tecnologia', 'tech', 'inovacao', 'digital', 'futuro');
    }
    if (allKeywords.includes('negocio') || allKeywords.includes('empreendedor') || allKeywords.includes('marketing')) {
        nicheTags.push('negocio', 'empreendedorismo', 'marketing', 'vendas', 'sucesso');
    }
    if (allKeywords.includes('educacao') || allKeywords.includes('aprender') || allKeywords.includes('ensino')) {
        nicheTags.push('educacao', 'aprendizado', 'conhecimento', 'estudo', 'formacao');
    }
    if (allKeywords.includes('lifestyle') || allKeywords.includes('vida') || allKeywords.includes('rotina')) {
        nicheTags.push('lifestyle', 'vida', 'rotina', 'bem estar', 'saude');
    }
    if (allKeywords.includes('medicina') || allKeywords.includes('medico') || allKeywords.includes('saude')) {
        nicheTags.push('medicina', 'saude', 'medico', 'hospital', 'tratamento');
    }
    if (allKeywords.includes('empresa') || allKeywords.includes('trabalho') || allKeywords.includes('carreira')) {
        nicheTags.push('empresa', 'trabalho', 'carreira', 'profissional', 'negocios');
    }
    if (allKeywords.includes('familia') || allKeywords.includes('crianca') || allKeywords.includes('filho')) {
        nicheTags.push('familia', 'crianca', 'filho', 'pais', 'educacao');
    }
    if (allKeywords.includes('dinheiro') || allKeywords.includes('financas') || allKeywords.includes('investimento')) {
        nicheTags.push('dinheiro', 'financas', 'investimento', 'economia', 'renda');
    }
    
    const typeSpecificTags = typeTags[contentType] || ['conteudo', 'video', 'youtube'];
    
    // Combinar todas as tags
    const allTags = [...baseTags, ...typeSpecificTags, ...popularTags, ...nicheTags];
    
    // Remover duplicatas
    const uniqueTags = [...new Set(allTags)];
    
    // Converter para string separada por vrgulas
    let tagsString = uniqueTags.join(', ');
    
    // Limitar a 500 caracteres
    if (tagsString.length > platformConfig.tagsMaxLength) {
        tagsString = tagsString.substring(0, platformConfig.tagsMaxLength);
        // Encontrar a ltima vrgula completa
        const lastComma = tagsString.lastIndexOf(',');
        if (lastComma > 0) {
            tagsString = tagsString.substring(0, lastComma);
        }
    }
    
    return tagsString;
}

// ===== GERADOR DE ROTEIRO VISUAL =====

// Inicializar Gerador de Roteiro Visual
function initializeVisualScriptGenerator() {
    const scriptInput = document.getElementById('scriptInput');
    if (scriptInput) {
        scriptInput.addEventListener('input', updateScriptStats);
        scriptInput.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                generateVisualScript();
            }
        });
    }
}

// Atualizar estatsticas do roteiro
function updateScriptStats() {
    const scriptInput = document.getElementById('scriptInput');
    const statsElement = document.getElementById('scriptStats');
    
    if (!scriptInput || !statsElement) return;
    
    const content = scriptInput.value;
    const charCount = content.length;
    const wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
    
    // Calcular segmentos estimados baseado na durao selecionada
    const segmentDuration = parseInt(document.getElementById('segmentDuration')?.value || 8);
    const estimatedSegments = Math.ceil(charCount / (segmentDuration * 12)); // ~12 caracteres por segundo
    
    statsElement.innerHTML = `
        <span>${charCount} caracteres  ${wordCount} palavras  ${estimatedSegments} segmentos estimados</span>
    `;
}

// Alternar configuraes
function toggleVisualScriptSettings() {
    const settingsContent = document.querySelector('.visual-script-settings .settings-content');
    const toggleBtn = document.querySelector('.visual-script-settings .toggle-settings i');
    
    if (settingsContent && toggleBtn) {
        const isVisible = settingsContent.style.display !== 'none';
        settingsContent.style.display = isVisible ? 'none' : 'block';
        toggleBtn.style.transform = isVisible ? 'rotate(180deg)' : 'rotate(0deg)';
    }
}

// Limpar input do roteiro
function clearScriptInput() {
    const scriptInput = document.getElementById('scriptInput');
    const statsElement = document.getElementById('scriptStats');
    
    if (scriptInput) {
        scriptInput.value = '';
        scriptInput.focus();
    }
    
    if (statsElement) {
        statsElement.innerHTML = '<span>0 caracteres  0 palavras  0 segmentos estimados</span>';
    }
    
    // Limpar resultados
    const resultsElement = document.getElementById('visualScriptResults');
    if (resultsElement) {
        resultsElement.innerHTML = `
            <div class="results-placeholder">
                <div class="placeholder-icon"></div>
                <h3>Prompts Visuais Gerados</h3>
                <p>Cole seu roteiro acima e clique em "Gerar Prompts Visuais" para converter em prompts de imagem e animao</p>
            </div>
        `;
    }
}

// Gerar roteiro visual
async function generateVisualScript() {
    const scriptInput = document.getElementById('scriptInput');
    const resultsElement = document.getElementById('visualScriptResults');
    
    if (!scriptInput || !resultsElement) return;
    
    const script = scriptInput.value.trim();
    if (!script) {
        alert('Por favor, cole seu roteiro no campo de texto.');
        return;
    }
    
    // Obter configuraes
    const generationType = document.getElementById('generationType')?.value || 'both';
    const segmentDuration = parseInt(document.getElementById('segmentDuration')?.value || 8);
    const videoFormat = document.getElementById('videoFormat')?.value || 'vertical';
    const animationModel = document.getElementById('animationModel')?.value || 'veo3';
    const includeAudio = document.getElementById('includeAudio')?.value || 'with-audio';
    const visualStyle = document.getElementById('visualStyle')?.value || 'realistic';
    
    // Mostrar loading
    resultsElement.innerHTML = `
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p>Gerando prompts visuais...</p>
        </div>
    `;
    
    try {
        // Calcular segmentos
        const segments = calculateScriptSegments(script, segmentDuration);
        
        // Gerar prompts para cada segmento
        const visualPrompts = await generateVisualPrompts(segments, {
            generationType,
            segmentDuration,
            videoFormat,
            animationModel,
            includeAudio,
            visualStyle
        });
        
        // Exibir resultados
        displayVisualScriptResults(visualPrompts, generationType);
        
    } catch (error) {
        console.error('Erro ao gerar roteiro visual:', error);
        resultsElement.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Erro na Gerao</h3>
                <p>Ocorreu um erro ao gerar os prompts visuais. Tente novamente.</p>
            </div>
        `;
    }
}

// Calcular segmentos do roteiro
function calculateScriptSegments(script, segmentDuration) {
    // Taxa de fala: ~12 caracteres por segundo (baseado em fala normal em portugus)
    const charsPerSecond = 12;
    const charsPerSegment = segmentDuration * charsPerSecond;
    
    // Dividir o roteiro em segmentos
    const segments = [];
    let currentPos = 0;
    let segmentIndex = 1;
    
    while (currentPos < script.length) {
        const endPos = Math.min(currentPos + charsPerSegment, script.length);
        
        // Tentar quebrar em uma frase completa
        let segmentEnd = endPos;
        if (endPos < script.length) {
            // Procurar por ponto, exclamao ou interrogao prximos
            const searchStart = Math.max(0, endPos - 30);
            const searchEnd = Math.min(script.length, endPos + 30);
            const searchText = script.substring(searchStart, searchEnd);
            
            const nextSentence = searchText.indexOf('.');
            const nextExclamation = searchText.indexOf('!');
            const nextQuestion = searchText.indexOf('?');
            
            let bestBreak = -1;
            if (nextSentence > 0) bestBreak = searchStart + nextSentence + 1;
            if (nextExclamation > 0 && (bestBreak === -1 || nextExclamation < nextSentence)) {
                bestBreak = searchStart + nextExclamation + 1;
            }
            if (nextQuestion > 0 && (bestBreak === -1 || nextQuestion < Math.min(nextSentence || 999, nextExclamation || 999))) {
                bestBreak = searchStart + nextQuestion + 1;
            }
            
            if (bestBreak > 0 && bestBreak <= endPos + 30) {
                segmentEnd = bestBreak;
            }
        }
        
        const segmentText = script.substring(currentPos, segmentEnd).trim();
        
        if (segmentText) {
            segments.push({
                index: segmentIndex,
                text: segmentText,
                duration: segmentDuration,
                startTime: (segmentIndex - 1) * segmentDuration,
                endTime: segmentIndex * segmentDuration
            });
            segmentIndex++;
        }
        
        currentPos = segmentEnd;
    }
    
    return segments;
}

// Gerar prompts visuais
async function generateVisualPrompts(segments, config) {
    const prompts = [];
    
    for (const segment of segments) {
        try {
            const prompt = await generateSegmentPrompt(segment, config);
            // Garantir que o prompt tenha tanto imagem quanto animao se necessrio
            if (config.generationType === 'both') {
                if (!prompt.imagePrompt) {
                    prompt.imagePrompt = generateFallbackPrompt(segment, config).imagePrompt;
                }
                if (!prompt.animationPrompt) {
                    prompt.animationPrompt = generateFallbackPrompt(segment, config).animationPrompt;
                }
            } else if (config.generationType === 'image-only' && !prompt.imagePrompt) {
                prompt.imagePrompt = generateFallbackPrompt(segment, config).imagePrompt;
            } else if (config.generationType === 'video-only' && !prompt.animationPrompt) {
                prompt.animationPrompt = generateFallbackPrompt(segment, config).animationPrompt;
            }
            prompts.push(prompt);
        } catch (error) {
            console.error(`Erro ao gerar prompt para segmento ${segment.index}:`, error);
            // Adicionar prompt de fallback
            prompts.push(generateFallbackPrompt(segment, config));
        }
    }
    
    return prompts;
}

// Gerar prompt para um segmento
async function generateSegmentPrompt(segment, config) {
    const formatSpecs = {
        'vertical': '9:16 aspect ratio, mobile format, portrait orientation',
        'horizontal': '16:9 aspect ratio, cinematic format, landscape orientation',
        'square': '1:1 aspect ratio, social media format, square composition'
    };
    
    const styleSpecs = {
        'realistic': 'photorealistic, high quality, detailed, natural lighting',
        'cinematic': 'cinematic lighting, dramatic composition, film quality, professional',
        'animated': 'animated style, vibrant colors, dynamic, stylized',
        'documentary': 'documentary style, natural lighting, authentic, realistic',
        'commercial': 'commercial quality, professional, polished, high-end'
    };
    
    const prompt = `Analyze this script segment and generate optimized visual prompts for AI video generation:

SEGMENT ${segment.index} (${segment.duration}s):
"${segment.text}"

CONFIGURATIONS:
- Type: ${config.generationType}
- Duration: ${config.segmentDuration} seconds
- Format: ${config.videoFormat} (${formatSpecs[config.videoFormat]})
- Model: ${config.animationModel.toUpperCase()}
- Audio: ${config.includeAudio}
- Style: ${config.visualStyle} (${styleSpecs[config.visualStyle]})

Generate the following prompts:

${config.generationType === 'image-only' || config.generationType === 'both' ? `
IMAGE PROMPT (for image generation):
- Detailed visual description for the segment
- Focus on narrative content
- Style: ${config.visualStyle}
- Format: ${config.videoFormat}
- Specific visual elements
- High quality, professional composition` : ''}

${config.generationType === 'video-only' || config.generationType === 'both' ? `
ANIMATION PROMPT (for ${config.animationModel.toUpperCase()}):
- Movement and transition descriptions
- Duration: ${config.segmentDuration} seconds
- Format: ${config.videoFormat}
- ${config.includeAudio === 'with-audio' ? 'Include audio synchronization' : 'No audio'}
- Style: ${config.visualStyle}
- Technical parameters optimized for ${config.animationModel}
- Professional video quality` : ''}

Format the response as:
${config.generationType === 'image-only' || config.generationType === 'both' ? 'IMAGE: [image prompt in English]' : ''}
${config.generationType === 'video-only' || config.generationType === 'both' ? 'ANIMATION: [animation prompt in English]' : ''}`;

    try {
        const response = await callAIAPI(prompt, {
            temperature: 0.7,
            maxTokens: 800,
            systemPrompt: `You are an expert in AI visual content generation and prompt engineering. Create detailed, technical prompts for image and video generation, optimized for VEO3/VEO2. Always respond in English with professional, technical language. Focus on creating prompts that will generate high-quality, professional visual content.`
        });
        
        return parseVisualPromptResponse(response, segment, config);
    } catch (error) {
        console.error('Erro na API:', error);
        return generateFallbackPrompt(segment, config);
    }
}

// Parsear resposta do prompt visual
function parseVisualPromptResponse(response, segment, config) {
    const lines = response.split('\n');
    let imagePrompt = '';
    let animationPrompt = '';
    
    for (const line of lines) {
        if (line.startsWith('IMAGE:')) {
            imagePrompt = line.replace('IMAGE:', '').trim();
        } else if (line.startsWith('ANIMATION:')) {
            animationPrompt = line.replace('ANIMATION:', '').trim();
        }
    }
    
    // Se no encontrou os prompts, usar fallback
    if (!imagePrompt && !animationPrompt) {
        const fallback = generateFallbackPrompt(segment, config);
        imagePrompt = fallback.imagePrompt;
        animationPrompt = fallback.animationPrompt;
    }
    
    return {
        segment: segment,
        imagePrompt: imagePrompt,
        animationPrompt: animationPrompt,
        config: config
    };
}

// Gerar prompt de fallback
function generateFallbackPrompt(segment, config) {
    const formatSpecs = {
        'vertical': '9:16 aspect ratio, mobile format, portrait orientation',
        'horizontal': '16:9 aspect ratio, cinematic format, landscape orientation',
        'square': '1:1 aspect ratio, social media format, square composition'
    };
    
    const styleSpecs = {
        'realistic': 'photorealistic, high quality, detailed, natural lighting, professional',
        'cinematic': 'cinematic lighting, dramatic composition, film quality, professional cinematography',
        'animated': 'animated style, vibrant colors, dynamic, stylized, modern',
        'documentary': 'documentary style, natural lighting, authentic, realistic, journalistic',
        'commercial': 'commercial quality, professional, polished, high-end, premium'
    };
    
    // Gerar prompt de imagem em ingls
    const imagePrompt = `Create a ${styleSpecs[config.visualStyle]} image representing the concept: "${segment.text}". Format: ${formatSpecs[config.videoFormat]}. High quality, detailed composition, professional lighting, sharp focus.`;
    
    // Gerar prompt de animao em ingls otimizado para VEO3/VEO2
    const animationPrompt = config.animationModel === 'veo3' 
        ? `Create a ${config.segmentDuration}-second video showing: "${segment.text}". Format: ${config.videoFormat}. Style: ${config.visualStyle}. ${config.includeAudio === 'with-audio' ? 'Include audio synchronization and lip sync.' : 'No audio, focus on visual storytelling.'} Professional quality, smooth motion, cinematic transitions.`
        : `Generate a ${config.segmentDuration}-second video depicting: "${segment.text}". Format: ${config.videoFormat}. Style: ${config.visualStyle}. ${config.includeAudio === 'with-audio' ? 'Include audio synchronization.' : 'No audio, visual focus.'} High quality, professional video production.`;
    
    return {
        segment: segment,
        imagePrompt: imagePrompt,
        animationPrompt: animationPrompt,
        config: config
    };
}

// Exibir resultados do roteiro visual
function displayVisualScriptResults(prompts, generationType) {
    const resultsElement = document.getElementById('visualScriptResults');
    
    if (!resultsElement) return;
    
    let html = '<div class="visual-script-results-content">';
    
    // Estatsticas gerais
    const totalDuration = prompts.reduce((sum, prompt) => sum + prompt.segment.duration, 0);
    const totalSegments = prompts.length;
    
    html += `
        <div class="results-summary">
            <h3><i class="fas fa-chart-bar"></i> Resumo da Gerao</h3>
            <div class="summary-stats">
                <div class="stat-item">
                    <span class="stat-value">${totalSegments}</span>
                    <span class="stat-label">Segmentos</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${totalDuration}s</span>
                    <span class="stat-label">Durao Total</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value">${Math.round(totalDuration / 60 * 10) / 10}min</span>
                    <span class="stat-label">Minutos</span>
                </div>
            </div>
        </div>
    `;
    
    // Segmentos
    prompts.forEach((prompt, index) => {
        html += `
            <div class="script-segment">
                <div class="segment-header">
                    <span class="segment-title">Segmento ${prompt.segment.index}</span>
                    <span class="segment-duration">${prompt.segment.duration}s</span>
                </div>
                
                <div class="segment-content">
                    ${prompt.segment.text}
                </div>
                
                ${(generationType === 'image-only' || generationType === 'both') ? `
                <div class="prompt-section">
                    <h5><i class="fas fa-image"></i> Prompt de Imagem</h5>
                    <div class="prompt-content">${prompt.imagePrompt || 'Prompt no gerado'}</div>
                </div>
                ` : ''}
                
                ${(generationType === 'video-only' || generationType === 'both') ? `
                <div class="prompt-section">
                    <h5><i class="fas fa-video"></i> Prompt de Animao</h5>
                    <div class="prompt-content">${prompt.animationPrompt || 'Prompt no gerado'}</div>
                </div>
                ` : ''}
                
                <div class="segment-actions">
                    <button class="copy-segment-btn" onclick="copySegmentPrompt(${index})">
                        <i class="fas fa-copy"></i> Copiar Segmento
                    </button>
                    ${(generationType === 'image-only' || generationType === 'both') ? `
                    <button class="copy-segment-btn" onclick="copyImagePrompt(${index})">
                        <i class="fas fa-image"></i> Copiar Imagem
                    </button>
                    ` : ''}
                    ${(generationType === 'video-only' || generationType === 'both') ? `
                    <button class="copy-segment-btn" onclick="copyAnimationPrompt(${index})">
                        <i class="fas fa-video"></i> Copiar Animao
                    </button>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    // Boto de exportar tudo
    html += `
        <button class="export-all-btn" onclick="exportAllVisualPrompts()">
            <i class="fas fa-download"></i> Exportar Todos os Prompts
        </button>
    `;
    
    html += '</div>';
    
    resultsElement.innerHTML = html;
    
    // Armazenar prompts globalmente para acesso nas funes de cpia
    window.visualPrompts = prompts;
}

// Funes de cpia
function copySegmentPrompt(index) {
    const prompt = window.visualPrompts[index];
    if (!prompt) return;
    
    const text = `SEGMENTO ${prompt.segment.index} (${prompt.segment.duration}s):
${prompt.segment.text}

${prompt.imagePrompt ? `PROMPT DE IMAGEM:
${prompt.imagePrompt}

` : ''}${prompt.animationPrompt ? `PROMPT DE ANIMAO:
${prompt.animationPrompt}` : ''}`;
    
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Segmento copiado para a rea de transferncia!', 'success');
    });
}

function copyImagePrompt(index) {
    const prompt = window.visualPrompts[index];
    if (!prompt || !prompt.imagePrompt) return;
    
    navigator.clipboard.writeText(prompt.imagePrompt).then(() => {
        showNotification('Prompt de imagem copiado!', 'success');
    });
}

function copyAnimationPrompt(index) {
    const prompt = window.visualPrompts[index];
    if (!prompt || !prompt.animationPrompt) return;
    
    navigator.clipboard.writeText(prompt.animationPrompt).then(() => {
        showNotification('Prompt de animao copiado!', 'success');
    });
}

// Exportar todos os prompts
function exportAllVisualPrompts() {
    const prompts = window.visualPrompts;
    if (!prompts || prompts.length === 0) return;
    
    let content = `# ROTEIRO VISUAL GERADO\n\n`;
    content += `**Configuraes:**\n`;
    content += `- Tipo: ${prompts[0].config.generationType}\n`;
    content += `- Durao por segmento: ${prompts[0].config.segmentDuration}s\n`;
    content += `- Formato: ${prompts[0].config.videoFormat}\n`;
    content += `- Modelo: ${prompts[0].config.animationModel}\n`;
    content += `- udio: ${prompts[0].config.includeAudio}\n`;
    content += `- Estilo: ${prompts[0].config.visualStyle}\n\n`;
    
    const totalDuration = prompts.reduce((sum, prompt) => sum + prompt.segment.duration, 0);
    content += `**Resumo:** ${prompts.length} segmentos, ${totalDuration}s total (${Math.round(totalDuration / 60 * 10) / 10} minutos)\n\n`;
    
    content += `---\n\n`;
    
    prompts.forEach((prompt, index) => {
        content += `## SEGMENTO ${prompt.segment.index} (${prompt.segment.duration}s)\n\n`;
        content += `**Texto:** ${prompt.segment.text}\n\n`;
        
        if (prompt.imagePrompt) {
            content += `**Prompt de Imagem:**\n${prompt.imagePrompt}\n\n`;
        }
        
        if (prompt.animationPrompt) {
            content += `**Prompt de Animao:**\n${prompt.animationPrompt}\n\n`;
        }
        
        content += `---\n\n`;
    });
    
    // Criar e baixar arquivo
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `roteiro-visual-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Arquivo exportado com sucesso!', 'success');
}

// Parsear resposta da IA
function parsePlatformResponse(response, platform) {
    const lines = response.split('\n');
    let title = '';
    let description = '';
    let hashtags = [];
    let tags = '';
    
    for (const line of lines) {
        if (line.startsWith('TTULO:')) {
            title = line.replace('TTULO:', '').trim();
        } else if (line.startsWith('DESCRIO:')) {
            description = line.replace('DESCRIO:', '').trim();
        } else if (line.startsWith('HASHTAGS:')) {
            const hashtagText = line.replace('HASHTAGS:', '').trim();
            hashtags = hashtagText.split(/\s+/).filter(tag => tag.startsWith('#'));
        } else if (line.startsWith('TAGS:')) {
            tags = line.replace('TAGS:', '').trim();
        }
    }
    
    const platformConfig = getPlatformConfig(platform);
    
    const result = {
        title: title.substring(0, platformConfig.titleMaxLength),
        description: description.substring(0, platformConfig.descriptionMaxLength),
        hashtags: hashtags.slice(0, platformConfig.hashtagCount)
    };
    
    // Adicionar tags se for YouTube
    if (platformConfig.hasTags && tags) {
        result.tags = tags.substring(0, platformConfig.tagsMaxLength);
    }
    
    return result;
}

// Exibir resultados da otimizao
function displayOptimizationResults(optimizedContent) {
    const resultsArea = document.getElementById('optimizationResults');
    
    if (!optimizedContent || Object.keys(optimizedContent).length === 0) {
        resultsArea.innerHTML = `
            <div class="error">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Nenhum contedo gerado</h3>
                <p>No foi possvel gerar contedo otimizado.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="optimization-results-content">';
    
    for (const [platform, content] of Object.entries(optimizedContent)) {
        const platformConfig = getPlatformConfig(platform);
        
        if (!content || !content.title || !content.description || !content.hashtags) {
            continue;
        }
        
        // Escapar caracteres especiais para HTML
        const safeTitle = content.title.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        const safeDescription = content.description.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        
        html += `
            <div class="platform-result">
                <div class="platform-header">
                    <i class="${platformConfig.icon}"></i>
                    <h4>${platformConfig.name}</h4>
                </div>
                
                <div class="platform-content">
                    <div class="content-section">
                        <div class="section-header">
                            <h5>Ttulo</h5>
                            <button class="copy-btn" onclick="copySectionContent('${platform}', 'title')" title="Copiar ttulo">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                        <p>${safeTitle}</p>
                    </div>
                    
                    <div class="content-section">
                        <div class="section-header">
                            <h5>Descrio</h5>
                            <button class="copy-btn" onclick="copySectionContent('${platform}', 'description')" title="Copiar descrio">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                        <p>${safeDescription}</p>
                    </div>
                    
                    <div class="content-section">
                        <div class="section-header">
                            <h5>Hashtags</h5>
                            <button class="copy-btn" onclick="copySectionContent('${platform}', 'hashtags')" title="Copiar hashtags">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                        <div class="hashtags">
                            ${content.hashtags.map(tag => `<span class="hashtag">${tag}</span>`).join('')}
                        </div>
                    </div>
                    
                    ${content.tags ? `
                    <div class="content-section">
                        <div class="section-header">
                            <h5>Tags (YouTube)</h5>
                            <button class="copy-btn" onclick="copySectionContent('${platform}', 'tags')" title="Copiar tags">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                        <p class="tags-content">${content.tags.replace(/"/g, '&quot;').replace(/'/g, '&#39;')}</p>
                    </div>
                    ` : ''}
                </div>
                
                <div class="platform-actions">
                    <button onclick="copyPlatformContent('${platform}')">
                        <i class="fas fa-copy"></i> Copiar Tudo
                    </button>
                    <button onclick="exportPlatformContent('${platform}')">
                        <i class="fas fa-download"></i> Exportar
                    </button>
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    
    resultsArea.innerHTML = html;
}

// Copiar seo especfica do contedo
function copySectionContent(platform, section) {
    // Encontrar o boto clicado e navegar para o card da plataforma
    const button = event.target.closest('button');
    const platformResult = button.closest('.platform-result');
    
    if (!platformResult) return;
    
    let contentToCopy = '';
    let sectionName = '';
    
    switch (section) {
        case 'title':
            contentToCopy = platformResult.querySelector('.content-section:nth-child(1) p').textContent;
            sectionName = 'ttulo';
            break;
        case 'description':
            contentToCopy = platformResult.querySelector('.content-section:nth-child(2) p').textContent;
            sectionName = 'descrio';
            break;
        case 'hashtags':
            const hashtags = Array.from(platformResult.querySelectorAll('.hashtag')).map(tag => tag.textContent);
            contentToCopy = hashtags.join(' ');
            sectionName = 'hashtags';
            break;
        case 'tags':
            const tagsElement = platformResult.querySelector('.tags-content');
            if (tagsElement) {
                contentToCopy = tagsElement.textContent;
                sectionName = 'tags';
            } else {
                showNotification('Tags no encontradas!', 'error');
                return;
            }
            break;
        default:
            showNotification('Seo no encontrada!', 'error');
            return;
    }
    
    navigator.clipboard.writeText(contentToCopy).then(() => {
        showNotification(`${sectionName.charAt(0).toUpperCase() + sectionName.slice(1)} copiado para a rea de transferncia!`, 'success');
    }).catch(() => {
        showNotification('Erro ao copiar contedo!', 'error');
    });
}

// Copiar contedo completo da plataforma
function copyPlatformContent(platform) {
    // Encontrar o boto clicado e navegar para o card da plataforma
    const button = event.target.closest('button');
    const platformResult = button.closest('.platform-result');
    
    if (!platformResult) return;
    
    const title = platformResult.querySelector('.content-section:nth-child(1) p').textContent;
    const description = platformResult.querySelector('.content-section:nth-child(2) p').textContent;
    const hashtags = Array.from(platformResult.querySelectorAll('.hashtag')).map(tag => tag.textContent).join(' ');
    
    let fullContent = `${title}\n\n${description}\n\n${hashtags}`;
    
    // Adicionar tags se existirem
    const tagsElement = platformResult.querySelector('.tags-content');
    if (tagsElement) {
        fullContent += `\n\nTags: ${tagsElement.textContent}`;
    }
    
    navigator.clipboard.writeText(fullContent).then(() => {
        showNotification('Contedo completo copiado para a rea de transferncia!', 'success');
    }).catch(() => {
        showNotification('Erro ao copiar contedo!', 'error');
    });
}

// Exportar contedo da plataforma
function exportPlatformContent(platform) {
    // Encontrar o boto clicado e navegar para o card da plataforma
    const button = event.target.closest('button');
    const platformResult = button.closest('.platform-result');
    
    if (!platformResult) return;
    
    const title = platformResult.querySelector('.content-section:nth-child(1) p').textContent;
    const description = platformResult.querySelector('.content-section:nth-child(2) p').textContent;
    const hashtags = Array.from(platformResult.querySelectorAll('.hashtag')).map(tag => tag.textContent).join(' ');
    
    let content = `TTULO:\n${title}\n\nDESCRIO:\n${description}\n\nHASHTAGS:\n${hashtags}`;
    
    // Adicionar tags se existirem
    const tagsElement = platformResult.querySelector('.tags-content');
    if (tagsElement) {
        content += `\n\nTAGS (YouTube):\n${tagsElement.textContent}`;
    }
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conteudo-${platform}-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showNotification('Contedo exportado com sucesso!', 'success');
}

// ===== OPENROUTER API =====
async function callOpenRouterAPI(prompt, model = "meta-llama/llama-3.2-3b-instruct:free") {
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${openRouterApiKey}`,
            'Content-Type': 'application/json',
            'HTTP-Referer': window.location.origin,
            'X-Title': 'APOLLO La PLATA'
        },
        body: JSON.stringify({
            model: model,
            messages: [
                {
                    role: 'user',
                    content: prompt
                }
            ],
            max_tokens: 1500,
            temperature: 0.7
        })
    });
    
    if (!response.ok) {
        throw new Error(`Erro na API: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.choices && data.choices[0] && data.choices[0].message) {
        return data.choices[0].message.content;
    } else {
        throw new Error('Resposta invlida da API');
    }
}

// ===== UTILITRIOS =====
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copiado para a rea de transferncia!', 'success');
    }).catch(err => {
        console.error('Erro ao copiar:', err);
        showNotification('Erro ao copiar!', 'error');
    });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
