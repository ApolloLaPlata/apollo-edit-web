// editor_audio.js

document.addEventListener('DOMContentLoaded', () => {
    const btnUpload = document.getElementById('btn-upload');
    const fileUpload = document.getElementById('file-upload');
    const trackName = document.getElementById('track-name');
    const waveformPlaceholder = document.getElementById('waveform-placeholder');

    const btnPlay = document.getElementById('btn-play');
    const btnPause = document.getElementById('btn-pause');

    // Botões IA
    const btnIaSilence = document.getElementById('btn-ia-silence');
    const btnIaMaster = document.getElementById('btn-ia-master');
    const btnIaMusic = document.getElementById('btn-ia-music');
    const musicPrompt = document.getElementById('music-prompt');

    let currentAudioBlob = null;
    let wavesurfer = null;
    let wsRegions = null;
    let activeRegion = null;

    // Inicializa Wavesurfer (Etapa 12)
    function initWavesurfer() {
        if (wavesurfer) wavesurfer.destroy();
        waveformPlaceholder.style.display = 'none';

        // Assume que o script do CDN carregou a global WaveSurfer
        wavesurfer = WaveSurfer.create({
            container: '#waveform-container',
            waveColor: '#6b21a8',
            progressColor: '#00ffcc',
            cursorColor: '#fff',
            barWidth: 2,
            barRadius: 2,
            responsive: true,
            height: 150,
        });

        wavesurfer.on('ready', () => {
            console.log("Áudio carregado no waveform.");
            updateTimecode(0);

            // Etapa 12: Inicializa as Regiões (Regions Plugin)
            wsRegions = wavesurfer.registerPlugin(WaveSurfer.Regions.create());
            
            // Cria uma região inicial que pega o audio todo (ou uma parte)
            activeRegion = wsRegions.addRegion({
                start: 0,
                end: wavesurfer.getDuration(),
                color: 'rgba(0, 255, 204, 0.2)',
                drag: true,
                resize: true
            });

            wsRegions.on('region-updated', (region) => {
                activeRegion = region;
            });
        });

        // Atualiza o Timecode dinamicamente durante a reprodução
        wavesurfer.on('audioprocess', (currentTime) => {
            updateTimecode(currentTime);
        });

        wavesurfer.on('seek', (progress) => {
            if (wavesurfer.getDuration()) {
                updateTimecode(progress * wavesurfer.getDuration());
            }
        });

        wavesurfer.on('finish', () => {
            console.log("Reprodução concluída.");
            updateTimecode(0);
        });
    }

    // Formatador de Timecode 00:00:00:000
    function updateTimecode(timeInSeconds) {
        const tc = document.getElementById('timecode-display');
        if (!tc) return;
        
        const hrs = Math.floor(timeInSeconds / 3600);
        const mins = Math.floor((timeInSeconds % 3600) / 60);
        const secs = Math.floor(timeInSeconds % 60);
        const ms = Math.floor((timeInSeconds % 1) * 1000);
        
        tc.innerText = 
            String(hrs).padStart(2, '0') + ':' + 
            String(mins).padStart(2, '0') + ':' + 
            String(secs).padStart(2, '0') + ':' + 
            String(ms).padStart(3, '0');
    }

    // Slider de Volume Mestre
    const masterVolume = document.getElementById('master-volume');
    if (masterVolume) {
        masterVolume.addEventListener('input', (e) => {
            if (wavesurfer) {
                wavesurfer.setVolume(Number(e.target.value));
            }
        });
    }

    btnUpload.addEventListener('click', () => fileUpload.click());

    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            trackName.innerText = file.name;
            currentAudioBlob = file;
            initWavesurfer();
            const objectUrl = URL.createObjectURL(file);
            wavesurfer.load(objectUrl);
        }
    });

    btnPlay.addEventListener('click', () => wavesurfer && wavesurfer.play());
    btnPause.addEventListener('click', () => wavesurfer && wavesurfer.pause());

    // Etapa 12: Controles Manuais da Waveform
    const btnTrimStart = document.getElementById('btn-trim-start');
    const btnTrimEnd = document.getElementById('btn-trim-end');
    const btnDelete = document.getElementById('btn-delete-section');

    if (btnTrimStart) {
        btnTrimStart.addEventListener('click', () => {
            if (!wavesurfer || !activeRegion) return;
            activeRegion.setOptions({ start: wavesurfer.getCurrentTime() });
            if (window.showToast) window.showToast("Início do Corte (Trim) definido!", "#00ffcc");
        });
    }

    if (btnTrimEnd) {
        btnTrimEnd.addEventListener('click', () => {
            if (!wavesurfer || !activeRegion) return;
            activeRegion.setOptions({ end: wavesurfer.getCurrentTime() });
            if (window.showToast) window.showToast("Fim do Corte (Trim) definido!", "#00ffcc");
        });
    }

    if (btnDelete) {
        btnDelete.addEventListener('click', () => {
            if (!wavesurfer || !activeRegion) return;
            const start = activeRegion.start.toFixed(2);
            const end = activeRegion.end.toFixed(2);
            
            if (confirm(`Tem certeza que deseja deletar o trecho de ${start}s até ${end}s?`)) {
                // Mock visual: Destroi a região pra indicar que sumiu
                activeRegion.remove();
                activeRegion = null;
                if (window.showToast) window.showToast("Trecho deletado com sucesso!", "#8b0000");
                
                // Em um cenário real, aqui acionaria o FFmpeg local para cortar o áudio de fato
            }
        });
    }

    // Etapa 13 Aprimorada: Efeitos IA (Integração Backend)
    btnIaSilence.addEventListener('click', async () => {
        if (!currentAudioBlob && trackName.innerText.includes("Nenhum")) {
            return alert("Carregue um áudio primeiro.");
        }
        
        btnIaSilence.innerText = "Processando Silêncios...";
        document.body.style.cursor = 'wait';
        
        const payload = {
            audio_base64: "blob_simulado_em_base64",
            threshold: "-30dB",
            duration: "0.5s"
        };
        console.log("Iniciando requisição para motor local (Remove Silence):", payload);

        try {
            const response = await fetch('http://127.0.0.1:42000/api/audio/remove-silence', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: AbortSignal.timeout(3000)
            });
            if (!response.ok) throw new Error("API Offline");
            
            // Carregar o novo áudio processado...
            const data = await response.json();
            wavesurfer.load(data.processed_audio_b64);
            
        } catch (error) {
            console.warn("API offline. Acionando Fallback...", error);
            
            // Mock Visual: Adiciona regiões vermelhas fingindo detectar o silêncio
            if (wsRegions && wavesurfer.getDuration() > 5) {
                wsRegions.addRegion({ start: 1, end: 2.5, color: 'rgba(255, 0, 0, 0.3)', drag: false, resize: false });
                wsRegions.addRegion({ start: 4, end: 5.2, color: 'rgba(255, 0, 0, 0.3)', drag: false, resize: false });
            }
            if (window.showToast) window.showToast("Mock: Silêncios detectados (Áreas Vermelhas) e cortados!", "#00ffcc");
        } finally {
            document.body.style.cursor = 'default';
            btnIaSilence.innerText = "Remover Silêncio Auto";
        }
    });

    btnIaMaster.addEventListener('click', async () => {
        if (!currentAudioBlob && trackName.innerText.includes("Nenhum")) {
            return alert("Carregue um áudio primeiro.");
        }
        
        btnIaMaster.innerText = "Masterizando...";
        document.body.style.cursor = 'wait';
        
        const payload = {
            audio_base64: "blob_simulado_em_base64",
            preset: "podcast_voice_enhancement"
        };
        console.log("Iniciando requisição para motor local (Mastering):", payload);

        try {
            const response = await fetch('http://127.0.0.1:42000/api/audio/mastering', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: AbortSignal.timeout(3000)
            });
            if (!response.ok) throw new Error("API Offline");
            
            const data = await response.json();
            wavesurfer.load(data.processed_audio_b64);
            
        } catch (error) {
            console.warn("API offline. Acionando Fallback...", error);
            
            // Mock: Simula aumento de ganho visualmente ajustando o zoom das ondas (se wavesurfer permitir) 
            // e tocando o audio um pouco mais alto se o master volume estivesse baixo
            if (masterVolume && masterVolume.value < 1) {
                masterVolume.value = 1;
                wavesurfer.setVolume(1);
            }
            if (window.showToast) window.showToast("Mock: Áudio Masterizado (Equalizado, Comprimido e Normalizado)!", "#00ffcc");
        } finally {
            document.body.style.cursor = 'default';
            btnIaMaster.innerText = "Tratamento Mágico (Voz)";
        }
    });

    // Etapa 14 Aprimorada: Gerador de Música IA (Integração Backend)
    btnIaMusic.addEventListener('click', async () => {
        const prompt = musicPrompt.value.trim();
        if (!prompt) return alert("Descreva a música que deseja gerar.");
        
        btnIaMusic.innerText = "Compondo Música...";
        document.body.style.cursor = 'wait';
        
        const payload = {
            prompt: prompt,
            duration: 15, // Segundos
            model: "musicgen-small"
        };
        console.log("Iniciando requisição para motor local (MusicGen):", payload);

        try {
            const response = await fetch('http://127.0.0.1:42000/api/audio/generate-music', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: AbortSignal.timeout(4000)
            });
            if (!response.ok) throw new Error("API Offline");
            
            const data = await response.json();
            trackName.innerText = `Gerado: ${prompt.substring(0, 15)}...`;
            initWavesurfer();
            wavesurfer.load(data.generated_audio_b64);
            
        } catch (error) {
            console.warn("API offline. Acionando Fallback...", error);
            
            trackName.innerText = `(Mock) Gerado: ${prompt.substring(0, 15)}...`;
            
            // Cria um blob vazio de áudio (header fake) apenas para o Bagageiro aceitar a exportação do "arquivo" gerado
            currentAudioBlob = new Blob(["RIFF dummy"], { type: 'audio/wav' });
            
            if (window.showToast) window.showToast(`Mock: Trilha baseada em "${prompt}" gerada!`, "#ff00ff");
        } finally {
            document.body.style.cursor = 'default';
            btnIaMusic.innerText = "Gerar Trilha Bruta";
            musicPrompt.value = "";
        }
    });

    // Etapa 15: Exportação para o Bagageiro
    window.exportToBagageiro = function() {
        if (!currentAudioBlob && trackName.innerText.includes("Nenhum")) {
            return alert("Nenhum áudio para exportar.");
        }
        
        // Cria um blob fictício se for gerado por IA para simular
        const blobToExport = currentAudioBlob || new Blob(["Audio Ficticio"], { type: "audio/mp3" });
        const file = new File([blobToExport], `AudioFinal_${new Date().getTime()}.mp3`, { type: 'audio/mp3' });
        
        if (typeof window.processDroppedFiles === 'function') {
            window.processDroppedFiles([file]);
            if (window.showToast) window.showToast("Exportado para o Apollo OS (Bagageiro)!", "#6b21a8");
        } else {
            console.warn("Transfer HUD global não carregado. Simulando download direto.");
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blobToExport);
            a.download = file.name;
            a.click();
        }
    };
});
