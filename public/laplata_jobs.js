/**
 * Apollo La Plata - Job Runner UI Logic (Etapa 15)
 * O Motor assíncrono (Etapa 16) injetará sua execução no clique de "Iniciar Automação".
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- UI ELEMENTS ---
    const promptInput = document.getElementById('prompt-input');
    const btnLoadQueue = document.getElementById('btn-load-queue');
    const btnClearQueue = document.getElementById('btn-clear-queue');
    
    const selAspect = document.getElementById('j-aspect');
    const togglePauseError = document.getElementById('toggle-pause-error');
    const toggleContinuity = document.getElementById('toggle-continuity');
    
    const btnStartBatch = document.getElementById('btn-start-batch');
    const btnStopBatch = document.getElementById('btn-stop-batch');
    
    const jobList = document.getElementById('job-list');
    const jobPlaceholder = document.getElementById('job-placeholder');
    const jobTemplate = document.getElementById('job-template');

    // Stats Elements
    const queueStats = document.getElementById('queue-stats');
    const statPend = queueStats.querySelector('.stat-pend');
    const statDone = queueStats.querySelector('.stat-done');
    const statFail = queueStats.querySelector('.stat-fail');

    // --- STATE ---
    let jobs = []; // { id, prompt, status, error, imageUrl }
    let pauseOnError = true;
    let useContinuity = false;
    let isProcessing = false;

    // Helpers
    const playClick = () => { if (window.apolloSFX) window.apolloSFX.play('click'); };
    const playError = () => { if (window.apolloSFX) window.apolloSFX.play('error'); };
    const showToast = (title, message, type = 'system') => { if (window.apolloNotifications) window.apolloNotifications.add(title, message, type); };

    // --- LOCAL STORAGE MANAGER ---
    function saveQueue() {
        // Para evitar estourar cota do localStorage, não salvamos o base64 (imageUrl)
        const queueToSave = jobs.map(j => ({ ...j, imageUrl: null }));
        localStorage.setItem('laplata_job_queue', JSON.stringify(queueToSave));
    }

    function loadQueue() {
        const saved = localStorage.getItem('laplata_job_queue');
        if (saved) {
            try {
                jobs = JSON.parse(saved);
                // NOTA: Recuperação das imagens via IndexedDB da Galeria pode ser implementada depois
            } catch (e) {
                console.error("Falha ao carregar fila:", e);
                jobs = [];
            }
        }
        renderQueue();
    }

    // --- UI RENDER ---
    function updateStats() {
        const pend = jobs.filter(j => j.status === 'pending').length;
        const proc = jobs.filter(j => j.status === 'processing').length; // Conta junto como pendente na contagem ou não
        const done = jobs.filter(j => j.status === 'completed').length;
        const fail = jobs.filter(j => j.status === 'failed').length;

        statPend.innerText = `⏳ ${pend + proc} Pendentes`;
        statDone.innerText = `✅ ${done} Concluídos`;
        statFail.innerText = `❌ ${fail} Falhas`;

        if (jobs.length > 0) {
            jobPlaceholder.style.display = 'none';
        } else {
            jobPlaceholder.style.display = 'block';
        }
    }

    // Exposto globalmente para o motor da Etapa 16 acessar
    window.renderQueue = function() {
        updateStats();
        
        // Remove existing items (except placeholder)
        Array.from(jobList.children).forEach(child => {
            if (child.id !== 'job-placeholder') {
                jobList.removeChild(child);
            }
        });

        jobs.forEach(job => {
            const clone = jobTemplate.content.cloneNode(true);
            const el = clone.querySelector('.job-item');
            
            el.dataset.id = job.id;
            el.className = `job-item ${job.status}`;
            
            el.querySelector('.job-id').innerText = `ID: ${job.id.split('-')[0]}`;
            
            const statusEl = el.querySelector('.job-status');
            if (job.status === 'pending') { statusEl.innerText = 'Pendente'; }
            if (job.status === 'processing') { statusEl.innerHTML = '<div class="spinner"></div> Processando'; }
            if (job.status === 'completed') { statusEl.innerText = 'Concluído'; }
            if (job.status === 'failed') { statusEl.innerText = 'Falha'; }

            el.querySelector('.job-prompt').innerText = job.prompt;

            if (job.error) {
                const errEl = el.querySelector('.job-error');
                errEl.innerText = job.error;
                errEl.style.display = 'block';
            }

            if (job.status === 'completed' && job.imageUrl) {
                const resEl = el.querySelector('.job-result');
                resEl.style.display = 'flex';
                resEl.querySelector('img').src = job.imageUrl;
            }

            // Actions
            el.querySelector('.btn-retry').addEventListener('click', () => {
                if (isProcessing) return;
                playClick();
                job.status = 'pending';
                job.error = null;
                job.imageUrl = null;
                saveQueue();
                window.renderQueue();
            });

            el.querySelector('.btn-remove').addEventListener('click', () => {
                if (isProcessing) return;
                playClick();
                jobs = jobs.filter(j => j.id !== job.id);
                saveQueue();
                window.renderQueue();
            });

            jobList.appendChild(el);
        });
    };

    // --- EVENTS ---

    // Load jobs from textarea
    btnLoadQueue.addEventListener('click', () => {
        const text = promptInput.value.trim();
        if (!text) {
            showToast('Aviso', 'Cole algum texto antes de carregar.', 'system');
            return;
        }

        const lines = text.split('\n').filter(l => l.trim().length > 0);
        const newJobs = lines.map(line => ({
            id: crypto.randomUUID(),
            prompt: line.trim(),
            status: 'pending',
            error: null,
            imageUrl: null
        }));

        jobs = [...jobs, ...newJobs];
        promptInput.value = '';
        playClick();
        saveQueue();
        window.renderQueue();
        showToast('Sucesso', `${newJobs.length} prompts adicionados à fila.`, 'success');
    });

    // Clear jobs
    btnClearQueue.addEventListener('click', () => {
        if (isProcessing) {
            showToast('Aviso', 'Pare o lote atual antes de limpar a fila.', 'system');
            return;
        }
        if (confirm('Tem certeza que deseja limpar a fila inteira?')) {
            playClick();
            jobs = [];
            saveQueue();
            window.renderQueue();
        }
    });

    // Toggles
    togglePauseError.addEventListener('click', () => {
        if (isProcessing) return;
        playClick();
        pauseOnError = !pauseOnError;
        togglePauseError.classList.toggle('active', pauseOnError);
        togglePauseError.querySelector('.status').innerText = pauseOnError ? 'ON' : 'OFF';
        
        // Exporting to window for Engine (Stage 16)
        window.laplataJobRunnerConfig.pauseOnError = pauseOnError;
    });

    toggleContinuity.addEventListener('click', () => {
        if (isProcessing) return;
        playClick();
        useContinuity = !useContinuity;
        toggleContinuity.classList.toggle('active', useContinuity);
        toggleContinuity.querySelector('.status').innerText = useContinuity ? 'ON' : 'OFF';
        
        window.laplataJobRunnerConfig.useContinuity = useContinuity;
    });

    selAspect.addEventListener('change', () => {
        window.laplataJobRunnerConfig.aspectRatio = selAspect.value;
    });

    // Placeholder object for Engine (Stage 16) integration
    window.laplataJobRunnerConfig = {
        pauseOnError: pauseOnError,
        useContinuity: useContinuity,
        aspectRatio: selAspect.value,
        getJobs: () => jobs,
        updateJob: (id, updates) => {
            const index = jobs.findIndex(j => j.id === id);
            if (index !== -1) {
                jobs[index] = { ...jobs[index], ...updates };
                saveQueue();
                window.renderQueue();
            }
        },
        setIsProcessing: (val) => {
            isProcessing = val;
            btnStartBatch.style.display = val ? 'none' : 'flex';
            btnStopBatch.style.display = val ? 'flex' : 'none';
            btnLoadQueue.disabled = val;
            promptInput.disabled = val;
            selAspect.disabled = val;
        }
    };

    btnStartBatch.addEventListener('click', () => {
        const pendingCount = jobs.filter(j => j.status === 'pending').length;
        if (pendingCount === 0) {
            showToast('Aviso', 'Não há tarefas pendentes na fila.', 'system');
            return;
        }
        playClick();
        if (window.laplataStartBatch) {
            // Chamada para o motor (Etapa 16)
            window.laplataStartBatch();
        } else {
            showToast('Atenção', 'Motor assíncrono do Job Runner será implementado na Etapa 16.', 'system');
        }
    });

    btnStopBatch.addEventListener('click', () => {
        playClick();
        if (window.laplataStopBatch) {
            // Chamada para o motor (Etapa 16)
            window.laplataStopBatch();
        }
    });

    // INITIAL LOAD
    loadQueue();
});
