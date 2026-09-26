// Apollo Studio V2 - Mobile First Interaction Logic

document.addEventListener("DOMContentLoaded", () => {
    // Menu elements
    const btnMenu = document.getElementById("btnMenu");
    const btnCloseMenu = document.getElementById("btnCloseMenu");
    const sideMenu = document.getElementById("sideMenu");
    const menuOverlay = document.getElementById("menuOverlay");

    // UI elements
    const btnGenerate = document.getElementById("btnGenerateStoryboard");
    const frameCountSelect = document.getElementById("frameCount");
    const emptyState = document.getElementById("emptyState");
    const floatingTimeline = document.getElementById("floatingTimeline");
    const timelineTrack = document.getElementById("timelineTrack");
    const progressText = document.getElementById("progressText");
    const btnPlayMovie = document.getElementById("btnPlayMovie");

    // Modal elements
    const imageModal = document.getElementById("imageModal");
    const btnModalClose = document.getElementById("btnModalClose");
    const modalImage = document.getElementById("modalImage");
    const modalSceneNum = document.getElementById("modalSceneNum");
    const btnModalRedo = document.getElementById("btnModalRedo");
    const modalLoading = document.getElementById("modalLoading");
    const modalPromptText = document.getElementById("modalPromptText");

    // State
    let totalFrames = 30;
    let frames = [];
    let currentModalIndex = 0;
    
    // Configurações do Backend / Queue
    const API_URL = "/api/studio/modal/generate_image";
    let generationQueue = [];
    let activeGenerations = 0;
    const MAX_CONCURRENT_GENERATIONS = 5;

    // --- Sidebar Menu Logic ---
    btnMenu.addEventListener("click", () => {
        sideMenu.classList.add("open");
        menuOverlay.classList.add("active");
    });

    const closeMenu = () => {
        sideMenu.classList.remove("open");
        menuOverlay.classList.remove("active");
    };

    btnCloseMenu.addEventListener("click", closeMenu);
    menuOverlay.addEventListener("click", closeMenu);

    // --- Generation Logic ---
    btnGenerate.addEventListener("click", () => {
        totalFrames = parseInt(frameCountSelect.value);
        generateStoryboard();
    });

    function generateStoryboard() {
        // Hide empty state
        emptyState.classList.add("hidden");
        // Show floating timeline
        floatingTimeline.classList.remove("hidden");
        // Force reflow for animation
        setTimeout(() => {
            floatingTimeline.classList.add("active");
        }, 50);

        // Clear track
        timelineTrack.innerHTML = '';
        frames = [];
        let loadedCount = 0;
        generationQueue = [];
        activeGenerations = 0;
        
        const mainPrompt = document.getElementById("mainPrompt").value || "Cena padrao gerada pelo sistema";
        const baseSeed = Math.floor(Math.random() * 1000000);

        // Create boxes and push to queue
        for (let i = 0; i < totalFrames; i++) {
            const box = document.createElement("div");
            box.className = "frame-box loading";
            
            const num = document.createElement("div");
            num.className = "frame-num";
            num.textContent = i + 1;
            
            const img = document.createElement("img");
            
            box.appendChild(img);
            box.appendChild(num);
            timelineTrack.appendChild(box);

            const frameData = {
                index: i,
                boxElement: box,
                imgElement: img,
                isLoaded: false,
                prompt: `${mainPrompt} [Parte ${i+1}]`,
                seed: baseSeed + i,
                onComplete: () => {
                    loadedCount++;
                    progressText.textContent = `(${loadedCount}/${totalFrames})`;
                    if (loadedCount === totalFrames) {
                        btnPlayMovie.disabled = false;
                        progressText.textContent = "Concluído!";
                    }
                }
            };
            frames.push(frameData);

            // Adiciona a tarefa na fila
            generationQueue.push(frameData);

            // Click event to open modal
            box.addEventListener("click", () => {
                if (frameData.isLoaded || frameData.hasError) {
                    openModal(frameData);
                }
            });
        }
        
        // Inicia o processamento da fila
        processQueue();
    }

    async function processQueue() {
        while (generationQueue.length > 0 && activeGenerations < MAX_CONCURRENT_GENERATIONS) {
            const frameData = generationQueue.shift();
            activeGenerations++;
            generateSingleFrame(frameData).finally(() => {
                activeGenerations--;
                processQueue();
            });
        }
    }

    async function generateSingleFrame(frame) {
        try {
            const payload = {
                prompt: frame.prompt,
                model: "flux2-universal",
                format: "vertical", // Storyboard costuma ser vertical no CapCut
                seed: frame.seed,
                use_upscale: false // Upscale falso para maior velocidade na prototipação
            };

            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json", "x-apollo-lock": "apollo-beta-key-2026" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("Network response was not ok");
            
            // Lidar com retorno da proxy NDJSON (ou raw JSON no caso da proxy falha)
            const text = await res.text();
            let jsonResponse;
            try {
                // Tenta pegar a última linha em caso de streaming/ndjson
                const lines = text.trim().split('\n');
                jsonResponse = JSON.parse(lines[lines.length - 1]);
            } catch (e) {
                jsonResponse = JSON.parse(text);
            }
            
            if (jsonResponse.status === "success" && jsonResponse.image_base64) {
                completeFrame(frame, jsonResponse.image_base64);
            } else {
                throw new Error(jsonResponse.message || "Falha na resposta do servidor");
            }
        } catch (error) {
            console.error("Erro gerando frame:", error);
            errorFrame(frame);
        }
    }

    function completeFrame(frame, b64) {
        frame.isLoaded = true;
        frame.boxElement.classList.remove("loading", "error");
        frame.boxElement.classList.add("loaded");
        frame.imgElement.src = `data:image/jpeg;base64,${b64}`;
        if(frame.onComplete) frame.onComplete();
    }
    
    function errorFrame(frame) {
        frame.isLoaded = false;
        frame.hasError = true;
        frame.boxElement.classList.remove("loading");
        frame.boxElement.classList.add("error");
        frame.boxElement.style.border = "2px solid red";
        if(frame.onComplete) frame.onComplete();
    }

    // --- Modal Logic ---
    function openModal(frame) {
        currentModalIndex = frame.index;
        modalImage.src = frame.imgElement.src;
        modalSceneNum.textContent = frame.index + 1;
        modalPromptText.textContent = frame.prompt;
        
        imageModal.classList.add("open");
    }

    btnModalClose.addEventListener("click", () => {
        imageModal.classList.remove("open");
    });

    btnModalRedo.addEventListener("click", async () => {
        const frame = frames[currentModalIndex];
        modalLoading.classList.remove("hidden");
        
        // Mudar semente para forçar uma geração nova
        frame.seed = Math.floor(Math.random() * 1000000);
        
        try {
            const payload = {
                prompt: frame.prompt,
                model: "flux2-universal",
                format: "vertical",
                seed: frame.seed,
                use_upscale: false
            };

            const res = await fetch(API_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json", "x-apollo-lock": "apollo-beta-key-2026" },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("Erro na rede");
            
            const text = await res.text();
            let jsonResponse;
            try {
                const lines = text.trim().split('\n');
                jsonResponse = JSON.parse(lines[lines.length - 1]);
            } catch (e) {
                jsonResponse = JSON.parse(text);
            }
            
            if (jsonResponse.status === "success" && jsonResponse.image_base64) {
                const newImgSrc = `data:image/jpeg;base64,${jsonResponse.image_base64}`;
                modalImage.src = newImgSrc;
                frame.imgElement.src = newImgSrc;
                frame.isLoaded = true;
                frame.hasError = false;
                frame.boxElement.classList.remove("error");
                frame.boxElement.classList.add("loaded");
                frame.boxElement.style.border = "";
            } else {
                alert("Falha ao refazer: " + jsonResponse.message);
            }
        } catch (error) {
            console.error(error);
            alert("Erro ao refazer a cena.");
        } finally {
            modalLoading.classList.add("hidden");
        }
    });

    // Finalize Video
    btnPlayMovie.addEventListener("click", () => {
        alert("Enviando todas as imagens para o pipeline Img2Vid na Modal (Fase 2)!");
    });
});
