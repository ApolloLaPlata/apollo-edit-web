/**
 * Apollo La Plata - Job Runner Asynchronous Engine (Etapa 16)
 * Realiza o processamento em fila com rotação de chaves e sistema de "Gasolina".
 */

(function() {
    let abortController = null;

    window.laplataStartBatch = async () => {
        if (abortController) return; // Já está rodando

        const config = window.laplataJobRunnerConfig;
        if (!config) {
            console.error("Configuração do Job Runner não encontrada!");
            return;
        }

        abortController = new AbortController();
        const signal = abortController.signal;
        
        config.setIsProcessing(true);
        if (window.apolloSFX) window.apolloSFX.play('success'); // Som de ignição!
        if (window.apolloCopilot) window.apolloCopilot.react("job_runner_start");

        try {
            const db = await window.laplataDB.openDB();
            
            // Carrega Configurações e Chaves Gemini
            const settings = await window.laplataSettings.get();
            const keys = window.laplataApiKeys.get();
            if (!keys || keys.filter(k => k.isActive).length === 0) {
                if (window.apolloNotifications) window.apolloNotifications.add("Aviso", "Nenhuma chave Gemini ativa encontrada nas Configurações.", "error");
                return;
            }

            // Loop Principal do Motor
            while (!signal.aborted) {
                // Checar Gasolina
                const currencies = await window.laplataDB.getCurrencies();
                let currentGas = currencies.gasolina;

                // Checar Header UI para Gasolina
                const gasEl = document.getElementById('user-credits');

                const jobs = config.getJobs();
                const pendingIndex = jobs.findIndex(j => j.status === 'pending');

                // 1. Condição de Parada: Fim da Fila
                if (pendingIndex === -1) {
                    if (window.apolloNotifications) window.apolloNotifications.add("Lote Concluído", "Todos os prompts foram processados!", "success");
                    if (window.apolloCopilot) window.apolloCopilot.react("job_runner_end");
                    if (window.apolloQuests) window.apolloQuests.addProgress('batch');
                    break;
                }

                // 2. Condição de Parada: Falta de Combustível
                if (currentGas < 1) {
                    if (window.apolloNotifications) window.apolloNotifications.add("Sem Combustível", "Você precisa de mais Gasolina para rodar a IA.", "error");
                    if (window.apolloSFX) window.apolloSFX.play('error');
                    if (window.apolloCopilot) window.apolloCopilot.react("low_gas");
                    break;
                }

                const currentJob = jobs[pendingIndex];
                
                // Marcar como processando
                config.updateJob(currentJob.id, { status: 'processing', error: null });

                // Continuidade da História (Opcional)
                let previousImage = null;
                if (config.useContinuity && pendingIndex > 0) {
                    // Busca na Fila o último job completado que tenha imagem
                    for (let i = pendingIndex - 1; i >= 0; i--) {
                        if (jobs[i].status === 'completed' && jobs[i].imageUrl) {
                            previousImage = jobs[i].imageUrl;
                            break;
                        }
                    }
                }

                // Carregar Personagens
                const chars = await window.laplataDB.characters.getAll();
                
                // Mesclar as configurações do Job com as configurações Globais
                const jobSettings = { ...settings, aspectRatio: config.aspectRatio };

                let success = false;
                let generatedImageBase64 = null;

                try {
                    // === CHAMADA DO MOTOR DE IA (Com Rotação Automática de Chaves) ===
                    generatedImageBase64 = await window.laplataApiKeys.executeWithKeyRotation(
                        async (apiKey) => {
                            if (signal.aborted) throw new Error("AbortError");
                            return await window.laplataAI.generateImage(
                                apiKey,
                                currentJob.prompt,
                                chars,
                                jobSettings,
                                previousImage // Envia imagem de referência se "Continuidade" estiver ON
                            );
                        }
                    );
                    
                    if (signal.aborted) break;
                    success = true;

                } catch (err) {
                    if (err.message === "AbortError" || signal.aborted) {
                        config.updateJob(currentJob.id, { status: 'pending', error: "Pausado pelo usuário." });
                        break;
                    }

                    console.error("Erro no Job:", err);
                    let errMsg = err.message || "Erro desconhecido";
                    
                    if (err.message.includes("429")) errMsg = "Cota de API Excedida (Erro 429).";
                    if (err.message.includes("SAFETY")) errMsg = "Censura detectada (Filtro de Segurança Google).";

                    // Tratamento de Erro baseado no Toggle do Usuário
                    if (config.pauseOnError) {
                        config.updateJob(currentJob.id, { status: 'pending', error: `PAUSA: ${errMsg}` });
                        if (window.apolloNotifications) window.apolloNotifications.add("Pausa Automática", `Lote pausado. Motivo: ${errMsg}`, "error");
                        if (window.apolloSFX) window.apolloSFX.play('error');
                        if (window.apolloCopilot) window.apolloCopilot.react("generate_error");
                        break; // Sai do While
                    } else {
                        config.updateJob(currentJob.id, { status: 'failed', error: errMsg });
                        if (window.apolloCopilot) window.apolloCopilot.react("generate_error");
                    }
                }

                if (success && generatedImageBase64) {
                    // Deduzir Custo
                    await window.laplataDB.updateCurrency(null, 'gasolina', -1);
                    currentGas -= 1;
                    window.laplataDB.updateTopNav();
                    if (window.apolloCopilot && Math.random() > 0.7) window.apolloCopilot.react("generate_success");

                    // Salvar na Galeria
                    await window.laplataDB.gallery.save({
                        id: crypto.randomUUID(),
                        prompt: currentJob.prompt,
                        imageUrl: generatedImageBase64,
                        timestamp: Date.now()
                    });

                    // Atualizar UI do Job Runner
                    config.updateJob(currentJob.id, {
                        status: 'completed',
                        imageUrl: generatedImageBase64
                    });
                }

                // Delay estratégico para não estourar rate limit da API antes do próximo ciclo
                if (!signal.aborted) {
                    await new Promise(res => setTimeout(res, 2000));
                }
            }
        } catch (e) {
            console.error("Erro fatal no motor:", e);
        } finally {
            window.laplataStopBatch();
        }
    };

    window.laplataStopBatch = () => {
        if (abortController) {
            abortController.abort();
            abortController = null;
        }
        const config = window.laplataJobRunnerConfig;
        if (config) config.setIsProcessing(false);
    };

})();
