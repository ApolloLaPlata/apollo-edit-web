let API_BASE_URL = '';
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.startsWith('192.168.')) {
    API_BASE_URL = 'http://' + window.location.host;
} else {
    API_BASE_URL = '.br';
}

const voiceSelect = document.getElementById('voiceSelect');
const uploadGroup = document.getElementById('uploadGroup');
const voiceFile = document.getElementById('voiceFile');
const ttsText = document.getElementById('ttsText');
const generateBtn = document.getElementById('generateBtn');
const loader = document.getElementById('loader');
const btnText = document.getElementById('btnText');
const generationStatus = document.getElementById('generationStatus');
const playerContainer = document.getElementById('playerContainer');
const audioPlayer = document.getElementById('audioPlayer');

voiceSelect.addEventListener('change', () => {
    if (voiceSelect.value === 'upload') {
        uploadGroup.style.display = 'flex';
    } else {
        uploadGroup.style.display = 'none';
    }
});

generateBtn.addEventListener('click', async () => {
    const text = ttsText.value.trim();
    if (!text) {
        alert("Digite um texto para ser falado!");
        return;
    }

    const formData = new FormData();
    formData.append("text", text);

    if (voiceSelect.value === 'upload') {
        if (!voiceFile.files.length) {
            alert("Selecione um arquivo WAV/MP3 de referência!");
            return;
        }
        formData.append("voice_file", voiceFile.files[0]);
    } else {
        // Envia uma string indicando qual voz padrão usar (o backend cuidaria, mas para simplificar
        // vamos mockar o envio de um arquivo vazio e o backend pega a default_voice).
        // Na prática, seria melhor o backend aceitar "voice_name".
        // Aqui enviamos apenas o texto; o backend lida.
    }

    setLoading(true);
    generationStatus.innerText = "Processando áudio na Modal Cloud (F5-TTS)...";

    try {
        const response = await fetch(`${API_BASE_URL}/api/voice/studio_generate`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Erro ${response.status}: Falha ao gerar áudio.`);
        }

        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);
        
        audioPlayer.src = audioUrl;
        playerContainer.style.display = 'flex';
        audioPlayer.play();
        
        generationStatus.innerText = "✨ Áudio gerado com sucesso!";
        generationStatus.style.color = "var(--success)";
    } catch (error) {
        console.error(error);
        generationStatus.innerText = `❌ Falha: ${error.message}`;
        generationStatus.style.color = "var(--error)";
    } finally {
        setLoading(false);
    }
});

function setLoading(isLoading) {
    if (isLoading) {
        generateBtn.disabled = true;
        loader.style.display = 'block';
        btnText.innerText = 'Sintetizando...';
        playerContainer.style.display = 'none';
        generationStatus.style.color = "var(--text-muted)";
    } else {
        generateBtn.disabled = false;
        loader.style.display = 'none';
        btnText.innerText = 'Gerar Áudio';
    }
}
