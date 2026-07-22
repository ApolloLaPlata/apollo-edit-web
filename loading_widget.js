// loading_widget.js (Oficina Rush MAX)

(function() {
    const style = document.createElement('style');
    style.innerHTML = `
        #rush-loading-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: #0a0510;
            background-image: 
                linear-gradient(rgba(10, 5, 16, 0.8), rgba(10, 5, 16, 0.9)),
                repeating-linear-gradient(0deg, transparent, transparent 40px, rgba(139, 92, 246, 0.1) 40px, rgba(139, 92, 246, 0.1) 80px);
            background-size: 100% 160px;
            animation: scrollBg 2s linear infinite;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s;
        }

        @keyframes scrollBg {
            from { background-position: 0 0; }
            to { background-position: 0 160px; }
        }

        #rush-loading-overlay.active {
            opacity: 1;
            pointer-events: all;
        }

        .rush-widget-container {
            background: rgba(20, 11, 46, 0.95);
            border: 3px solid #8b5cf6;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 0 40px rgba(139, 92, 246, 0.6);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
            position: relative;
            z-index: 10;
        }

        .rush-widget-header {
            text-align: center;
            color: #00f0ff;
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            font-weight: 900;
            letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
            margin-bottom: 5px;
            font-size: 1.5rem;
        }

        .rush-scoreboard {
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
            font-family: 'Inter', sans-serif;
            font-weight: bold;
        }

        .rush-score-box {
            background: rgba(0,0,0,0.5);
            padding: 5px 15px;
            border-radius: 8px;
            border: 1px solid #00f0ff;
            color: #00f0ff;
            text-shadow: 0 0 5px #00f0ff;
        }

        .rush-highscore-box {
            background: rgba(0,0,0,0.5);
            padding: 5px 15px;
            border-radius: 8px;
            border: 1px solid #fbbf24;
            color: #fbbf24;
            text-shadow: 0 0 5px #fbbf24;
        }

        .rush-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 4px;
            background: rgba(0,0,0,0.5);
            padding: 8px;
            border-radius: 10px;
            position: relative;
        }

        .rush-cell {
            width: 45px; height: 45px;
            background: rgba(255,255,255,0.05);
            border-radius: 6px;
            cursor: pointer;
            user-select: none;
            transition: transform 0.2s, background 0.2s;
            background-size: 80%;
            background-position: center;
            background-repeat: no-repeat;
            position: relative;
        }

        .rush-cell.selected {
            background-color: rgba(0, 240, 255, 0.3);
            border: 2px solid #00f0ff;
            transform: scale(1.1);
            z-index: 2;
        }

        .rush-cell:hover {
            background-color: rgba(139, 92, 246, 0.3);
        }

        .rush-progress-container {
            width: 100%;
            height: 15px;
            background: #000;
            border-radius: 8px;
            border: 1px solid #8b5cf6;
            overflow: hidden;
            margin-top: 10px;
        }

        .rush-progress-bar {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #8b5cf6, #00f0ff);
            transition: width 0.3s linear;
        }

        .rush-status-text {
            color: #fbbf24;
            font-size: 0.9rem;
            font-weight: bold;
            font-family: 'Inter', sans-serif;
        }

        /* Particle animations */
        .rush-particle {
            position: absolute;
            width: 8px;
            height: 8px;
            background: #00f0ff;
            border-radius: 50%;
            pointer-events: none;
            box-shadow: 0 0 10px #00f0ff;
            animation: explode 0.5s forwards ease-out;
            z-index: 20;
        }

        @keyframes explode {
            0% { transform: scale(1) translate(0, 0); opacity: 1; }
            100% { transform: scale(0) translate(var(--dx), var(--dy)); opacity: 0; }
        }

        /* Ambient animated car at the bottom */
        .rush-car-ambient {
            position: absolute;
            bottom: 20px;
            left: -100px;
            width: 150px;
            height: 60px;
            background-image: url('assets/peca_carro.png');
            background-size: contain;
            background-repeat: no-repeat;
            filter: drop-shadow(0 0 10px #ff0055);
            animation: driveCar 4s linear infinite;
            z-index: 5;
        }

        @keyframes driveCar {
            0% { left: -150px; transform: scaleX(1); }
            45% { left: 110vw; transform: scaleX(1); }
            50% { left: 110vw; transform: scaleX(-1); }
            95% { left: -150px; transform: scaleX(-1); }
            100% { left: -150px; transform: scaleX(1); }
        }
    `;
    document.head.appendChild(style);

    const overlay = document.createElement('div');
    overlay.id = 'rush-loading-overlay';
    
    // Animated car background
    const carAmbient = document.createElement('div');
    carAmbient.className = 'rush-car-ambient';
    overlay.appendChild(carAmbient);

    const container = document.createElement('div');
    container.className = 'rush-widget-container';
    
    const header = document.createElement('div');
    header.className = 'rush-widget-header';
    header.innerHTML = 'Oficina Rush <span style="font-size: 0.6em; color: #00f0ff;">MAX</span>';
    
    const scoreboard = document.createElement('div');
    scoreboard.className = 'rush-scoreboard';
    
    const scoreBox = document.createElement('div');
    scoreBox.className = 'rush-score-box';
    scoreBox.innerHTML = '⛽ <span id="rush-score-val">0</span> L';
    
    const highscoreBox = document.createElement('div');
    highscoreBox.className = 'rush-highscore-box';
    highscoreBox.innerHTML = '🏆 Recorde: <span id="rush-highscore-val">0</span> L';
    
    scoreboard.appendChild(scoreBox);
    scoreboard.appendChild(highscoreBox);

    const gridEl = document.createElement('div');
    gridEl.className = 'rush-grid';
    
    const progressContainer = document.createElement('div');
    progressContainer.className = 'rush-progress-container';
    const progressBar = document.createElement('div');
    progressBar.className = 'rush-progress-bar';
    progressBar.id = 'rush-progress-bar';
    progressContainer.appendChild(progressBar);
    
    const statusText = document.createElement('div');
    statusText.className = 'rush-status-text';
    statusText.id = 'rush-status-text';
    statusText.innerText = 'Preparando...';
    
    container.appendChild(header);
    container.appendChild(scoreboard);
    container.appendChild(gridEl);
    container.appendChild(progressContainer);
    container.appendChild(statusText);
    
    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.innerText = "Ocultar Minigame";
    closeBtn.style.cssText = "margin-top: 15px; background: transparent; border: 1px solid #555; color: #aaa; padding: 5px 15px; border-radius: 20px; cursor: pointer; transition: 0.2s; font-family: 'Inter', sans-serif;";
    closeBtn.onmouseover = () => closeBtn.style.color = "#fff";
    closeBtn.onmouseout = () => closeBtn.style.color = "#aaa";
    closeBtn.onclick = () => window.hideLoadingRush();
    container.appendChild(closeBtn);

    overlay.appendChild(container);

    window.addEventListener('DOMContentLoaded', () => {
        document.body.appendChild(overlay);
        loadHighscore();
    });

    // Sound Synthesizer (No external files needed)
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx;
    
    function playTone(freq, type, duration, vol=0.1) {
        try {
            if (!audioCtx) audioCtx = new AudioContext();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            
            gain.gain.setValueAtTime(vol, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);
            
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch(e) {}
    }

    function playMatchSound() {
        playTone(600, 'sine', 0.1, 0.1);
        setTimeout(() => playTone(800, 'sine', 0.2, 0.1), 50);
    }

    function playExplosionSound() {
        playTone(150, 'square', 0.2, 0.1); // low crunch
        playTone(300, 'sawtooth', 0.1, 0.05);
    }

    function playDropSound() {
        playTone(400, 'triangle', 0.05, 0.05);
    }

    // Game Logic
    const pieces = [
        'url("assets/peca_engrenagem.png")',
        'url("assets/peca_bateria.png")',
        'url("assets/peca_chave.png")',
        'url("assets/peca_pneu.png")',
        'url("assets/peca_cristal.png")',
        'url("assets/peca_carro.png")'
    ];
    
    const width = 8;
    let grid = [];
    let selectedCell = null;
    let isProcessing = false;
    let currentScore = 0;
    let highscore = 0;

    function loadHighscore() {
        const saved = localStorage.getItem('apollo_rush_highscore');
        if (saved) highscore = parseInt(saved);
        const hiEl = document.getElementById('rush-highscore-val');
        if (hiEl) hiEl.innerText = highscore;
    }

    function saveHighscore() {
        if (currentScore > highscore) {
            highscore = currentScore;
            localStorage.setItem('apollo_rush_highscore', highscore);
            const hiEl = document.getElementById('rush-highscore-val');
            if (hiEl) hiEl.innerText = highscore;
        }
    }

    function updateScore(points) {
        currentScore += points;
        document.getElementById('rush-score-val').innerText = currentScore;
    }

    function createParticles(cell) {
        const rect = cell.getBoundingClientRect();
        const gridRect = gridEl.getBoundingClientRect();
        const x = rect.left - gridRect.left + rect.width / 2;
        const y = rect.top - gridRect.top + rect.height / 2;
        
        for (let i = 0; i < 6; i++) {
            const p = document.createElement('div');
            p.className = 'rush-particle';
            p.style.left = x + 'px';
            p.style.top = y + 'px';
            
            // Random direction
            const angle = Math.random() * Math.PI * 2;
            const dist = 30 + Math.random() * 40;
            p.style.setProperty('--dx', Math.cos(angle) * dist + 'px');
            p.style.setProperty('--dy', Math.sin(angle) * dist + 'px');
            
            // Random color from the pieces
            const colors = ['#00f0ff', '#8b5cf6', '#fbbf24', '#ff0055'];
            p.style.background = colors[Math.floor(Math.random()*colors.length)];
            p.style.boxShadow = `0 0 10px ${p.style.background}`;
            
            gridEl.appendChild(p);
            setTimeout(() => p.remove(), 500);
        }
    }

    function initBoard() {
        gridEl.innerHTML = '';
        grid = [];
        currentScore = 0;
        document.getElementById('rush-score-val').innerText = 0;
        loadHighscore();
        
        for (let i = 0; i < width * width; i++) {
            const cell = document.createElement('div');
            cell.className = 'rush-cell';
            cell.dataset.id = i;
            cell.style.backgroundImage = pieces[Math.floor(Math.random() * pieces.length)];
            cell.addEventListener('click', onCellClick);
            gridEl.appendChild(cell);
            grid.push(cell);
        }
        while(checkMatches(false)) refillBoard();
    }

    function onCellClick() {
        if (isProcessing) return;
        const clickedId = parseInt(this.dataset.id);

        if (!selectedCell) {
            selectedCell = this;
            this.classList.add('selected');
            playTone(900, 'sine', 0.05, 0.05);
        } else {
            const selectedId = parseInt(selectedCell.dataset.id);
            const validMoves = [selectedId - 1, selectedId + 1, selectedId - width, selectedId + width];
            
            if (selectedId % width === 0) validMoves.splice(validMoves.indexOf(selectedId - 1), 1);
            if (selectedId % width === width - 1) validMoves.splice(validMoves.indexOf(selectedId + 1), 1);

            if (validMoves.includes(clickedId)) {
                swapPieces(selectedCell, this);
                isProcessing = true;
                setTimeout(() => {
                    if (!checkMatches(true)) {
                        swapPieces(grid[selectedId], grid[clickedId]); // swap back
                        playTone(300, 'sawtooth', 0.1, 0.05); // error sound
                        isProcessing = false;
                    } else {
                        processCascade();
                    }
                }, 200);
            } else {
                selectedCell.classList.remove('selected');
                selectedCell = this;
                this.classList.add('selected');
                playTone(900, 'sine', 0.05, 0.05);
                return;
            }
            selectedCell.classList.remove('selected');
            selectedCell = null;
        }
    }

    function swapPieces(c1, c2) {
        const temp = c1.style.backgroundImage;
        c1.style.backgroundImage = c2.style.backgroundImage;
        c2.style.backgroundImage = temp;
    }

    function checkMatches(animate) {
        let matched = false;
        let toClear = new Set();

        // Horizontal
        for (let r = 0; r < width; r++) {
            for (let c = 0; c < width - 2; c++) {
                let id1 = r * width + c;
                let id2 = id1 + 1;
                let id3 = id1 + 2;
                let p1 = grid[id1].style.backgroundImage;
                if (p1 !== '' && p1 !== 'none' && p1 === grid[id2].style.backgroundImage && p1 === grid[id3].style.backgroundImage) {
                    toClear.add(id1); toClear.add(id2); toClear.add(id3);
                    matched = true;
                }
            }
        }
        // Vertical
        for (let c = 0; c < width; c++) {
            for (let r = 0; r < width - 2; r++) {
                let id1 = r * width + c;
                let id2 = id1 + width;
                let id3 = id1 + width * 2;
                let p1 = grid[id1].style.backgroundImage;
                if (p1 !== '' && p1 !== 'none' && p1 === grid[id2].style.backgroundImage && p1 === grid[id3].style.backgroundImage) {
                    toClear.add(id1); toClear.add(id2); toClear.add(id3);
                    matched = true;
                }
            }
        }
        
        if (toClear.size > 0) {
            toClear.forEach(id => {
                if (animate) createParticles(grid[id]);
                grid[id].style.backgroundImage = 'none';
            });
            if (animate) {
                updateScore(toClear.size * 5);
                playMatchSound();
                playExplosionSound();
            }
            return true;
        }
        return false;
    }

    function dropPieces() {
        let moved = false;
        for (let c = 0; c < width; c++) {
            for (let r = width - 1; r > 0; r--) {
                let curr = r * width + c;
                let above = (r - 1) * width + c;
                if ((grid[curr].style.backgroundImage === '' || grid[curr].style.backgroundImage === 'none') && grid[above].style.backgroundImage !== 'none' && grid[above].style.backgroundImage !== '') {
                    grid[curr].style.backgroundImage = grid[above].style.backgroundImage;
                    grid[above].style.backgroundImage = 'none';
                    moved = true;
                }
            }
        }
        return moved;
    }

    function refillBoard() {
        for (let c = 0; c < width; c++) {
            if (grid[c].style.backgroundImage === '' || grid[c].style.backgroundImage === 'none') {
                grid[c].style.backgroundImage = pieces[Math.floor(Math.random() * pieces.length)];
            }
        }
    }

    function processCascade() {
        let gInt = setInterval(() => {
            if (!dropPieces()) {
                refillBoard();
                playDropSound();
                let topFull = true;
                for (let c=0; c<width; c++) {
                    if(grid[c].style.backgroundImage==='' || grid[c].style.backgroundImage==='none') topFull = false;
                }
                if (topFull) {
                    clearInterval(gInt);
                    setTimeout(() => {
                        if (checkMatches(true)) {
                            processCascade();
                        } else {
                            isProcessing = false;
                            saveHighscore();
                        }
                    }, 200);
                }
            }
        }, 80);
    }

    let progressInterval = null;

    window.showLoadingRush = function(taskName, durationMs) {
        initBoard();
        document.getElementById('rush-status-text').innerText = taskName + '... 0%';
        document.getElementById('rush-progress-bar').style.width = '0%';
        
        let overlayDiv = document.getElementById('rush-loading-overlay');
        if(!overlayDiv && document.body) {
            document.body.appendChild(overlay);
        }
        
        document.getElementById('rush-loading-overlay').classList.add('active');
        
        if (progressInterval) clearInterval(progressInterval);
        
        let startTime = Date.now();
        progressInterval = setInterval(() => {
            let elapsed = Date.now() - startTime;
            let percent = Math.min(100, (elapsed / durationMs) * 100);
            
            document.getElementById('rush-progress-bar').style.width = percent + '%';
            document.getElementById('rush-status-text').innerText = taskName + '... ' + Math.floor(percent) + '%';
            
            if (percent >= 100) {
                clearInterval(progressInterval);
                document.getElementById('rush-status-text').innerText = "Processo Concluído!";
                playTone(1000, 'sine', 0.2, 0.1);
                setTimeout(()=>playTone(1200, 'sine', 0.4, 0.1), 200);
                saveHighscore();
                setTimeout(() => window.hideLoadingRush(), 2000); 
            }
        }, 100);
    };

    window.hideLoadingRush = function() {
        if (progressInterval) clearInterval(progressInterval);
        saveHighscore();
        const el = document.getElementById('rush-loading-overlay');
        if (el) el.classList.remove('active');
    };

})();
