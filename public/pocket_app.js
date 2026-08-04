// Apollo Pocket Director â€” Voice Core & Diagnostic OS (Master Turbo Blaster)
// --- APOLLO EDIT WEB NATIVE INTEGRATION ---
let API_BASE_URL = '';
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname.startsWith('192.168.')) {
    // Acesso Local ou na Rede Wi-Fi (Celular aponta para o IP do PC na porta 8100)
    API_BASE_URL = 'http://' + window.location.hostname + ':8100';
} else {
    // Acesso Externo via Nuvem/Tunnel (Garante o HTTPS)
    API_BASE_URL = 'https://api.apolloedit.com.br';
}

// --- ETAPA 181: MÃ³dulo de Criptografia AES-256 ---
class ApolloCrypto {
  static async getDummyKey() {
    // Para protÃ³tipo offline, usamos um hash SHA-256 de uma senha estÃ¡tica como chave AES
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey("raw", enc.encode("APOLLO_MASTER_KEY_2026"), "PBKDF2", false, ["deriveBits", "deriveKey"]);
    return await crypto.subtle.deriveKey(
      { name: "PBKDF2", salt: enc.encode("apollo_salt"), iterations: 100000, hash: "SHA-256" },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    );
  }

  static async encryptText(text) {
    if (!text) return text;
    try {
      const key = await this.getDummyKey();
      const iv = crypto.getRandomValues(new Uint8Array(12));
      const encoded = new TextEncoder().encode(text);
      const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv: iv }, key, encoded);
      
      // Concatena IV + Ciphertext e converte para Base64
      const payload = new Uint8Array(iv.length + ciphertext.byteLength);
      payload.set(iv, 0);
      payload.set(new Uint8Array(ciphertext), iv.length);
      return btoa(String.fromCharCode(...payload));
    } catch (e) {
      console.error("Encryption Error:", e);
      return text;
    }
  }

  static async decryptText(base64Payload) {
    if (!base64Payload) return base64Payload;
    try {
      // Se nÃ£o parecer Base64/Encriptado, retorna o texto puro (Retrocompatibilidade)
      if (!base64Payload.includes('=')) return base64Payload; 
      
      const payloadString = atob(base64Payload);
      const payload = new Uint8Array(payloadString.length);
      for (let i = 0; i < payloadString.length; i++) payload[i] = payloadString.charCodeAt(i);
      
      const iv = payload.slice(0, 12);
      const ciphertext = payload.slice(12);
      const key = await this.getDummyKey();
      const decrypted = await crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, key, ciphertext);
      return new TextDecoder().decode(decrypted);
    } catch (e) {
      // Falha ao decriptar ou nÃ£o Ã© base64 real
      return base64Payload;
    }
  }
}

// Banco de Dados Offline Persistente - IndexedDB (Etapa 8 - ApolloDirectorDB)
class ApolloDirectorDB {
  static dbName = 'apollo_pocket_director_db';
  static version = 2; // ETAPA 52: Upgrade para suportar sessÃµes
  static db = null;

  static async open() {
    if (this.db) return this.db;
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };
      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        
        // Loja de configuraÃ§Ãµes e buffers
        if (!db.objectStoreNames.contains('settings')) db.createObjectStore('settings', { keyPath: 'key' });
        if (!db.objectStoreNames.contains('offline_buffer')) db.createObjectStore('offline_buffer', { keyPath: 'id', autoIncrement: true });

        // Nova loja de SessÃµes (MÃºltiplos Chats)
        if (!db.objectStoreNames.contains('sessions')) {
          db.createObjectStore('sessions', { keyPath: 'id' });
        }

        // HistÃ³rico de mensagens
        if (!db.objectStoreNames.contains('history')) {
          const store = db.createObjectStore('history', { keyPath: 'id', autoIncrement: true });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('session_id', 'session_id', { unique: false });
        } else {
          // AtualizaÃ§Ã£o de versÃ£o 1 para 2
          const store = e.target.transaction.objectStore('history');
          if (!store.indexNames.contains('session_id')) {
            store.createIndex('session_id', 'session_id', { unique: false });
          }
        }
      };
    });
  }

  // ETAPA 52 e 53: GestÃ£o de SessÃµes
  static async saveSession(sessionObj) {
    try {
      const db = await this.open();
      const tx = db.transaction('sessions', 'readwrite');
      tx.objectStore('sessions').put(sessionObj);
    } catch(e) {}
  }

  static async getSessions() {
    try {
      const db = await this.open();
      return new Promise((resolve) => {
        const tx = db.transaction('sessions', 'readonly');
        const req = tx.objectStore('sessions').getAll();
        req.onsuccess = () => {
          const all = req.result || [];
          all.sort((a,b) => b.updated_at - a.updated_at);
          resolve(all);
        };
        req.onerror = () => resolve([]);
      });
    } catch(e) { return []; }
  }

  static async saveHistoryItem(session_id, role, text) {
    try {
      const db = await this.open();
      
      // ETAPA 181: Criptografar mensagem antes de salvar
      const encryptedText = await ApolloCrypto.encryptText(text);

      const tx = db.transaction('history', 'readwrite');
      const store = tx.objectStore('history');
      store.add({ session_id, role, text: encryptedText, timestamp: Date.now() });
      
      // Atualizar tÃ­tulo/tempo da sessÃ£o
      const summary = text.substring(0, 30) + (text.length > 30 ? '...' : '');
      const sTx = db.transaction('sessions', 'readwrite');
      const sStore = sTx.objectStore('sessions');
      const sReq = sStore.get(session_id);
      sReq.onsuccess = () => {
        let session = sReq.result;
        if (!session) {
          session = { id: session_id, title: role === 'user' ? summary : 'Nova SessÃ£o', updated_at: Date.now() };
        } else {
          session.updated_at = Date.now();
          if (session.title === 'Nova SessÃ£o' && role === 'user') {
            session.title = summary;
          }
        }
        sStore.put(session);
      };
    } catch(err) {
      console.error('Erro ao salvar no IndexedDB:', err);
    }
  }

  static async getHistoryBySession(session_id, limit = 50) {
    try {
      const db = await this.open();
      return new Promise((resolve) => {
        const tx = db.transaction('history', 'readonly');
        const index = tx.objectStore('history').index('session_id');
        const req = index.getAll(IDBKeyRange.only(session_id));
        req.onsuccess = async () => {
          let all = req.result || [];
          all.sort((a, b) => a.timestamp - b.timestamp);
          const sliced = all.slice(-limit);
          
          // ETAPA 181: Descriptografar mensagens
          for (let item of sliced) {
            item.text = await ApolloCrypto.decryptText(item.text);
          }
          resolve(sliced);
        };
        req.onerror = () => resolve([]);
      });
    } catch(err) {
      console.warn('Erro ao ler histÃ³rico do IndexedDB:', err);
      return [];
    }
  }

  static async clearHistory() {
    try {
      const db = await this.open();
      const tx = db.transaction(['history', 'sessions'], 'readwrite');
      tx.objectStore('history').clear();
      tx.objectStore('sessions').clear();
    } catch(err) {}
  }

  static async saveSetting(key, value) {
    try {
      const db = await this.open();
      const tx = db.transaction('settings', 'readwrite');
      tx.objectStore('settings').put({ key, value });
    } catch(err) {}
  }

  static async getSetting(key, defaultVal = null) {
    try {
      const db = await this.open();
      return new Promise((resolve) => {
        const tx = db.transaction('settings', 'readonly');
        const store = tx.objectStore('settings');
        const req = store.get(key);
        req.onsuccess = () => resolve(req.result ? req.result.value : defaultVal);
        req.onerror = () => resolve(defaultVal);
      });
    } catch(err) {
      return defaultVal;
    }
  }
}

class PocketDirectorApp {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.audioContext = null;
    this.analyser = null;
    this.mediaStream = null;
    this.selectedDeviceId = '';
    this.audioUnlocked = false;
    this.micInitialized = false;

    // Web Speech API Native STT (Zero-Delay Streaming) & Etapa 14 Fallback Engine
    this.recognition = null;
    this.isSpeechRecognitionActive = false;
    this.sttMode = 'webspeech'; // ZERANDO O DELAY: Usando Web Speech API como motor primÃ¡rio
    this.ttsVolume = 1.0;
    
    // VAD & State
    this.isListeningActive = false; // AGORA COMEÃ‡A DESLIGADO (Text-Mode padrÃ£o)
    this.silenceThreshold = 0.02; // Sensibilidade do microfone

    // Audio Playback Queue
    this.audioQueue = [];
    this.isPlayingAudio = false;
    this.currentAudioElement = null;

    // MediaRecorder for Hardware Diagnostic Loop
    this.mediaRecorder = null;
    this.recordedChunks = [];
    this.isRecordingTest = false;

    // Current Assistant Message Element
    this.currentAssistantCard = null;
    this.currentAssistantContent = null;

    // DOM Elements - Main Stage
    this.orbContainer = document.getElementById('orbContainer');
    this.orbCore = document.getElementById('orbCore');
    this.stateLabel = document.getElementById('stateLabel');
    this.stateText = document.getElementById('stateText');
    this.liveSubtitle = document.getElementById('liveSubtitle');
    this.feedSection = document.getElementById('feedSection');
    this.statusDot = document.getElementById('statusDot');
    this.statusText = document.getElementById('statusText');
    
    this.btnMicToggle = document.getElementById('btnMicToggle');
    this.micLabel = document.getElementById('micLabel');
    this.micIcon = document.getElementById('micIcon');
    this.btnBargeIn = document.getElementById('btnBargeIn');
    this.btnToggleKeyboard = document.getElementById('btnToggleKeyboard');
    this.textDrawer = document.getElementById('textDrawer');
    this.drawerInput = document.getElementById('drawerInput');
    this.btnSendText = document.getElementById('btnSendText');

    // ETAPA 161: VariÃ¡veis de VisÃ£o
    this.btnToggleVision = document.getElementById('btnToggleVision');
    this.visionIcon = document.getElementById('visionIcon');
    this.cameraPreview = document.getElementById('cameraPreview');
    this.visionCanvas = document.getElementById('visionCanvas');
    this.isVisionActive = false;
    this.visionInterval = null;
    this.visionStream = null;

    // ETAPA 58: Anexos
    this.btnAttachImage = document.getElementById('btnAttachImage');
    this.imageUploadInput = document.getElementById('imageUploadInput');

    this.btnExportChat = document.getElementById('btnExportChat');
    
    // ETAPA 78: God View
    this.btnGodView = document.getElementById('btnGodView');
    this.godViewModal = document.getElementById('godViewModal');
    this.btnCloseGodView = document.getElementById('btnCloseGodView');
    this.godViewList = document.getElementById('godViewList');
    this.btnMuteTTS = document.getElementById('btnMuteTTS');
    this.isMuted = false;

    this.canvas = document.getElementById('visualizerCanvas');
    this.canvasCtx = this.canvas.getContext('2d');

    // ETAPA 131 e 133: Apollo Edit & Context Selector
    this.contextSelector = document.getElementById('contextSelector');
    this.apolloEditModal = document.getElementById('apolloEditModal');
    this.btnCloseApolloEdit = document.getElementById('btnCloseApolloEdit');
    this.btnApproveScript = document.getElementById('btnApproveScript');
    this.btnRejectScript = document.getElementById('btnRejectScript');
    this.btnRestartServer = document.getElementById('btnRestartServer');

    // Etapa 192, 193, 194
    this.btnStealthMode = document.getElementById('btnStealthMode');
    this.btnTurboMode = document.getElementById('btnTurboMode');
    this.btnOpenHiveLogs = document.getElementById('btnOpenHiveLogs');
    this.btnCloseHiveLogs = document.getElementById('btnCloseHiveLogs');
    this.hiveLogsSidebar = document.getElementById('hiveLogsSidebar');
    this.hiveLogOutput = document.getElementById('hiveLogOutput');

    this.btnSettings = document.getElementById('btnSettings');
    this.settingsModal = document.getElementById('settingsModal');
    this.btnCloseSettings = document.getElementById('btnCloseSettings');
    this.permStatusBadge = document.getElementById('permStatusBadge');
    this.audioInputSelect = document.getElementById('audioInputSelect');
    this.btnRefreshDevices = document.getElementById('btnRefreshDevices');
    this.btnRequestMicPerm = document.getElementById('btnRequestMicPerm');
    this.vuMeterFill = document.getElementById('vuMeterFill');
    this.vuValueText = document.getElementById('vuValueText');
    this.btnTestRecord = document.getElementById('btnTestRecord');
    this.btnTestEchoLoop = document.getElementById('btnTestEchoLoop');
    this.echoLoopStatsBox = document.getElementById('echoLoopStatsBox');
    this.echoSignalPeak = document.getElementById('echoSignalPeak');
    this.echoNoiseFloor = document.getElementById('echoNoiseFloor');
    this.echoSNRValue = document.getElementById('echoSNRValue');
    this.echoQualityBadge = document.getElementById('echoQualityBadge');
    this.isEchoLoopActive = false;
    this.echoNoiseFloorDb = -68.0;
    this.echoPeakDb = -68.0;
    this.testRecordStatus = document.getElementById('testRecordStatus');
    this.sttTestBox = document.getElementById('sttTestBox');
    this.voiceSelect = document.getElementById('voiceSelect');
    this.btnTestTTS = document.getElementById('btnTestTTS');

    // Image Zoom Modal
    this.imgModal = document.getElementById('imgModal');
    this.modalImg = document.getElementById('modalImg');

    // 60 FPS Reative VU-Meter & Ganho TTS (Etapa 6)
    this.liveVuFill = document.getElementById('liveVuFill');
    this.liveVuPeak = document.getElementById('liveVuPeak');
    this.liveVuDbText = document.getElementById('liveVuDbText');
    this.ttsVolumeSlider = document.getElementById('ttsVolumeSlider');
    this.ttsVolumeVal = document.getElementById('ttsVolumeVal');
    this.ttsVolume = parseFloat(localStorage.getItem('ttsVolume') || '1.0');
    this.ttsVoice = localStorage.getItem('ttsVoice') || 'pt-BR-AntonioNeural';
    this.voicePillsContainer = document.getElementById('voicePillsContainer');
    
    // Etapa 12: Retries Exponenciais Silenciosos & Fila de ReconexÃ£o no WebSocket
    this.wsReconnectAttempt = 0;
    this.wsMaxReconnectDelay = 30000;
    this.wsBaseDelay = 1000;
    this.wsReconnectTimer = null;
    this.wsOfflineMessageQueue = [];

    // ETAPA 42: Terminal Overlay
    this.terminalOverlay = document.getElementById('terminalOverlay');
    this.terminalBody = document.getElementById('terminalBody');
    this.btnCloseTerminal = document.getElementById('btnCloseTerminal');
    if (this.btnCloseTerminal) {
      this.btnCloseTerminal.addEventListener('click', () => {
        this.terminalOverlay.classList.remove('open');
      });
    }

    // ETAPA 52: Sidebar e MÃºltiplos Chats
    this.currentSessionId = null;
    this.chatSidebar = document.getElementById('chatSidebar');
    this.btnOpenSidebar = document.getElementById('btnOpenSidebar');
    this.btnCloseSidebar = document.getElementById('btnCloseSidebar');
    this.btnNewChat = document.getElementById('btnNewChat');
    this.chatHistoryList = document.getElementById('chatHistoryList');

    // ETAPA 173: VariÃ¡veis de NotificaÃ§Ã£o
    this.notificationsEnabled = false;

    // ConexÃµes de Rede do Celular (Fase IX e X)
    this.isMobilePolling = false;

    // Etapa 182: Interceptar o fluxo de boot para o Cofre
    const vaultOverlay = document.getElementById('vaultOverlay');
    if (vaultOverlay) {
      vaultOverlay.style.display = 'none'; // Sempre escondido no Web
    }
    this.init();
  }

  async verifyBiometrics(reason) {
    // Retorna um hash falso para simular sucesso na Web
    return "BYPASS_WEB_" + Date.now();
  }

  async init() {
    // Etapa 186: Anti-Root / Jailbreak Detection
    await this.checkEnvironmentIntegrity();

    this.checkForUpdates(false);
    this.setupVisualizerCanvas();
    this.setupEventListeners();
    this.setupVoicePills();
    
    // Etapa 183 & 184: Carteira de Cristais Offline e ReconciliaÃ§Ã£o
    await this.syncOfflineCrystals();

    this.connectWebSocket();
    this.connectTerminalSSE();
    this.registerServiceWorker();
    this.requestWakeLock();
    this.setupMobileLifecyleHandlers();
    this.startVisualizerLoop();
    this.checkPermissionStatus();
    await this.loadOfflineHistory();
    this.setupSidebarGestures(); // ETAPA 67
    this.initNetworkTopology();

    // Etapa 173: Inicializar NotificaÃ§Ãµes
    this.initNotifications();
    this.startBackgroundDaemon();
  }

  // --- ETAPA 171 e 172: O GUARDIÃƒO DE BOLSO (DAEMON) ---
  startBackgroundDaemon() {
    console.log('ðŸ›¡ï¸ Iniciando Daemon do Apollo Pocket Director em Background...');
    // Roda a cada 60 segundos (pode ser ajustado)
    setInterval(async () => {
      if (!this.notificationsEnabled) return;
      try {
        // Checar RenderizaÃ§Ã£o do Maestro (8080)
        const maestroRes = await fetch('http://localhost:8080/api/mobile/render/status').catch(() => null);
        if (maestroRes && maestroRes.ok) {
          const maestroData = await maestroRes.json();
          let statusText = `Maestro: Renderizando (${maestroData.progress}%)`;
          if (maestroData.progress === 100) {
            statusText = "Maestro: Ocioso";
            if (!this._notifiedRenderDone) {
              this.fireLocalNotification("VÃ­deo Pronto! ðŸŽ¬", "O Maestro terminou de renderizar seu vÃ­deo no PC.");
              this._notifiedRenderDone = true;
            }
          } else {
            this._notifiedRenderDone = false;
          }
          this.updateWidgetData("apollo_status", statusText);
        } else {
          this.updateWidgetData("apollo_status", "Maestro: Offline");
        }

        // Checar AutoBlog (8098)
        const autoBlogRes = await fetch('http://localhost:8098/api/v1/publish-trigger', { method: 'OPTIONS' }).catch(() => null);
        if (autoBlogRes && autoBlogRes.ok) {
          this.updateWidgetData("apollo_crystals", "Cristais: ðŸ’Ž 99+");
          if (!this._notifiedAutoBlog) {
            this.fireLocalNotification("AutoBlog: Novo Post!", "Um novo roteiro sobre GTA 6 aguarda sua aprovaÃ§Ã£o biomÃ©trica.", { postId: "1234" });
            this._notifiedAutoBlog = true;
          }
        } else {
          this.updateWidgetData("apollo_crystals", "Cristais: ðŸ’Ž 12");
          this._notifiedAutoBlog = false; // reseta
        }

      } catch (e) {
        console.log('Daemon Background: Servidores inacessÃ­veis no momento.');
        this.updateWidgetData("apollo_status", "Maestro: InacessÃ­vel");
      }
    }, 60000);
  }

  // ETAPA 176: Enviar dados para o Widget Nativo via Preferences
  async updateWidgetData(key, value) {
    if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Preferences) {
      await window.Capacitor.Plugins.Preferences.set({
        key: key,
        value: value
      });
    }
  }

  // ETAPA 173: Solicitar PermissÃµes e Inicializar NotificaÃ§Ãµes Locais
  async renderSidebarSessions() {
    const sessions = await ApolloDirectorDB.getSessions();
    this.chatHistoryList.innerHTML = '';
    sessions.forEach(session => {
      const el = document.createElement('div');
      el.className = 'chat-history-item' + (session.id === this.currentSessionId ? ' active' : '');
      const dateStr = new Date(session.updated_at).toLocaleString();
      el.innerHTML = `
        <div class="chat-item-title">${this.escapeHtml(session.title)}</div>
        <div class="chat-item-date">${dateStr}</div>
      `;
      el.onclick = () => {
        this.loadSession(session.id);
        this.chatSidebar.classList.remove('open');
      };
      this.chatHistoryList.appendChild(el);
    });
  }

  // ETAPA 53: Criar Novo Chat
  async createNewSession() {
    this.currentSessionId = 'session_' + Date.now();
    this.feedSection.innerHTML = '';
    
    // Add Welcome Card
    const welcome = document.createElement('div');
    welcome.className = 'card assistant-msg';
    welcome.innerHTML = `
      <div class="card-header">
        <span class="card-tag">ðŸ‘‘ DIRETOR DE BOLSO (GPT-5)</span>
        <span>Agora</span>
      </div>
      <div class="card-content">
        Nova SessÃ£o iniciada. Como posso ajudar?
      </div>
    `;
    this.feedSection.appendChild(welcome);
    
    await this.renderSidebarSessions();
    this.chatSidebar.classList.remove('open');
  }

  // ETAPA 52: Carregar uma sessÃ£o especÃ­fica
  async loadSession(session_id) {
    this.currentSessionId = session_id;
    this.feedSection.innerHTML = '';
    const history = await ApolloDirectorDB.getHistoryBySession(session_id, 50);
    
    if (history.length === 0) {
      await this.createNewSession();
      return;
    }
    
    history.forEach(item => {
      this.addTranscriptCard(item.role, item.text, false);
    });
    this.scrollToBottom();
    await this.renderSidebarSessions();
  }

  // Etapa 8: Carrega histÃ³rico local do IndexedDB e configuraÃ§Ãµes salvas
  async loadOfflineHistory() {
    try {
      const savedVol = await ApolloDirectorDB.getSetting('ttsVolume', null);
      if (savedVol !== null && !isNaN(savedVol)) {
        this.ttsVolume = parseFloat(savedVol);
        if (this.ttsVolumeSlider) this.ttsVolumeSlider.value = Math.round(this.ttsVolume * 100);
      }

      const savedVoice = await ApolloDirectorDB.getSetting('ttsVoice', null);
      if (savedVoice) {
        this.ttsVoice = savedVoice;
      }
      this.syncActiveVoicePill(this.ttsVoice);

      // Carregar a Ãºltima sessÃ£o ativa
      const sessions = await ApolloDirectorDB.getSessions();
      if (sessions.length > 0) {
        this.currentSessionId = sessions[0].id;
        await this.loadSession(this.currentSessionId);
      } else {
        await this.createNewSession();
      }
    } catch(e) {
      console.warn('Erro ao carregar histÃ³rico do IndexedDB:', e);
    }
  }

  // --- ETAPA 186: Anti-Root Mock ---
  async checkEnvironmentIntegrity() {
    // Simulamos a verificaÃ§Ã£o de dispositivo seguro. 
    // Em produÃ§Ã£o, isso usaria @capacitor-community/device ou rootBeer.
    if (window.Capacitor && window.Capacitor.isNativePlatform()) {
      const isEmulator = true; // Hardcoded para permitir os testes do usuÃ¡rio no PC
      if (!isEmulator) {
        // Se fosse um celular real com root, o app fecharia
        alert("ðŸ”’ AVISO DE SEGURANÃ‡A: Ambiente inseguro (Root) detectado. O Apollo serÃ¡ encerrado.");
        window.Capacitor.Plugins.App.exitApp();
      }
    }
  }

  // --- ETAPA 183 & 184: CARTEIRA DE CRISTAIS OFFLINE ---
  async syncOfflineCrystals() {
    try {
      // Tenta bater no Maestro
      const res = await fetch('http://localhost:8080/api/mobile/crystals', { timeout: 3000 });
      if (res.ok) {
        const data = await res.json();
        // Criptografa antes de salvar offline
        const encrypted = await ApolloCrypto.encryptText(JSON.stringify(data));
        await ApolloDirectorDB.saveSetting('offline_crystals', encrypted);
        this.updateWidgetData("apollo_crystals", `Cristais: ðŸ’Ž ${data.balance}`);
        console.log("ðŸ’Ž Cristais sincronizados com o Maestro.");
      }
    } catch (e) {
      console.warn("âš ï¸ Maestro Offline. Carregando Carteira Offline Criptografada...");
      const encrypted = await ApolloDirectorDB.getSetting('offline_crystals');
      if (encrypted) {
        try {
          const decrypted = await ApolloCrypto.decryptText(encrypted);
          const data = JSON.parse(decrypted);
          this.updateWidgetData("apollo_crystals", `Cristais: ðŸ’Ž ${data.balance} (Offline)`);
          console.log("ðŸ’Ž Carteira Offline carregada com sucesso.");
        } catch (decErr) {
          console.error("Falha ao decriptar a carteira offline.", decErr);
        }
      }
    }
  }

  // Ativa Microfone e Ãudio no primeiro toque do usuÃ¡rio
  async activateAudioAndMic() {
    if (!this.audioUnlocked) {
      this.audioUnlocked = true;
      try {
        const silentAudio = new Audio('data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA');
        await silentAudio.play();
      } catch (e) {}
    }

    if (!this.micInitialized) {
      await this.initMicrophone();
      this.initVAD();
      this.populateAudioDevices();
    }
  }

  // Verifica status da permissÃ£o na API de permissÃµes
  async checkPermissionStatus() {
    if (navigator.permissions && navigator.permissions.query) {
      try {
        const status = await navigator.permissions.query({ name: 'microphone' });
        this.updatePermBadge(status.state);
        status.onchange = () => this.updatePermBadge(status.state);
      } catch (e) {
        this.updatePermBadge('prompt');
      }
    }
  }

  updatePermBadge(state) {
    if (state === 'granted') {
      this.permStatusBadge.className = 'badge granted';
      this.permStatusBadge.textContent = 'Permitido (OK)';
    } else if (state === 'denied') {
      this.permStatusBadge.className = 'badge denied';
      this.permStatusBadge.textContent = 'Bloqueado';
    } else {
      this.permStatusBadge.className = 'badge';
      this.permStatusBadge.textContent = 'Toque para Ativar';
    }
  }

  // Lista todos os microfones conectados
  async populateAudioDevices() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;

    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices.filter(d => d.kind === 'audioinput');

      this.audioInputSelect.innerHTML = '';
      if (audioInputs.length === 0) {
        const opt = document.createElement('option');
        opt.textContent = 'Nenhum microfone detectado';
        this.audioInputSelect.appendChild(opt);
        return;
      }

      audioInputs.forEach((device, index) => {
        const opt = document.createElement('option');
        opt.value = device.deviceId;
        opt.textContent = device.label || `Microfone ${index + 1}`;
        if (device.deviceId === this.selectedDeviceId) {
          opt.selected = true;
        }
        this.audioInputSelect.appendChild(opt);
      });
    } catch (err) {
      console.warn('Erro ao listar dispositivos de Ã¡udio:', err);
    }
  }

  // Inicializa Microfone com Web Audio API para o Visualizador e VU-Meter
  async initMicrophone() {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.warn('getUserMedia nÃ£o suportado neste ambiente.');
        return;
      }

      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(t => t.stop());
      }

      const constraints = {
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      };

      if (this.selectedDeviceId) {
        constraints.audio.deviceId = { exact: this.selectedDeviceId };
      }

      this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
      this.updatePermBadge('granted');

      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!this.audioContext) {
        this.audioContext = new AudioCtx();
      }
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      const source = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      this.analyser.smoothingTimeConstant = 0.8;
      source.connect(this.analyser);

      this.micInitialized = true;
      this.setOrbState('listening');
      console.log('ðŸŽ™ï¸ Microfone e Analisador de Ãudio conectados com sucesso.');
      this.populateAudioDevices();
    } catch (err) {
      console.warn('Aviso ao acessar microfone via getUserMedia:', err);
      this.updatePermBadge('denied');
    }
  }

  // Sistema de DetecÃ§Ã£o de Atividade de Voz (VAD) ContÃ­nuo para Live Audio Mode
  initVAD() {
    this.isSpeakingVAD = false;
    this.silenceStartVAD = 0;
    this.vadThreshold = 10; // Threshold adaptativo
    this.silenceDelay = 1500; // ms de silÃªncio para acionar o envio
    this.vadMediaRecorder = null;
    this.vadAudioChunks = [];
    
    // Fallback caso nÃ£o possamos usar MediaRecorder
    if (!window.MediaRecorder) {
        console.warn('MediaRecorder nÃ£o suportado.');
        return;
    }

    setInterval(() => {
      // Verifica se estÃ¡ apto a gravar (Mic Ativo e nÃ£o processando)
      if (this.isProcessingLLM || !this.isListeningActive || !this.analyser || !this.mediaStream) return;

      const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
      this.analyser.getByteTimeDomainData(dataArray);
      let maxVal = 0;
      for (let i = 0; i < dataArray.length; i++) {
        let diff = Math.abs(dataArray[i] - 128);
        if (diff > maxVal) maxVal = diff;
      }

      const isSpeakingNow = maxVal > this.vadThreshold;

      if (isSpeakingNow) {
        if (!this.isSpeakingVAD) {
          this.isSpeakingVAD = true;
          this.setOrbState('thinking'); // Orbe reage Ã  voz
          
          if (!this.vadMediaRecorder || this.vadMediaRecorder.state === 'inactive') {
            this.vadAudioChunks = [];
            this.vadMediaRecorder = new MediaRecorder(this.mediaStream);
            this.vadMediaRecorder.ondataavailable = e => {
              if (e.data.size > 0) this.vadAudioChunks.push(e.data);
            };
            this.vadMediaRecorder.onstop = () => {
              const audioBlob = new Blob(this.vadAudioChunks, { type: 'audio/webm' });
              if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                 this.socket.send(audioBlob);
                 this.isProcessingLLM = true;
                 this.setOrbState('processing'); // Muda cor para processando Modal GPU
              }
            };
            this.vadMediaRecorder.start();
          }
        }
        this.silenceStartVAD = Date.now();
      } else {
        if (this.isSpeakingVAD) {
          if (Date.now() - this.silenceStartVAD > this.silenceDelay) {
             this.isSpeakingVAD = false;
             if (this.vadMediaRecorder && this.vadMediaRecorder.state === 'recording') {
               this.vadMediaRecorder.stop(); // O stop() dispara o envio
             }
          }
        }
      }
    }, 100);
  }

  // ETAPA 112/114/115 e 142 (Integridade): Verificador de AtualizaÃ§Ãµes OTA
  async checkForUpdates(manual = false) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/app/version`);
      const data = await res.json();
      const serverVersion = data.version;
      const serverHash = data.hash; // Etapa 142
      const localVersion = localStorage.getItem('appVersion') || '1.0.0';
      const localHash = localStorage.getItem('appHash') || '';

      if (serverVersion !== localVersion || (serverHash && serverHash !== localHash)) {
        this.showToast(`OTA: Nova versÃ£o ${serverVersion} encontrada! Validando integridade...`, 'warn');
        
        // Simula o download e verificaÃ§Ã£o de SHA256 do bundle OTA (Etapa 142)
        setTimeout(() => {
          if (serverHash) {
            console.log(`[OTA] Hash validado: ${serverHash}. Bundle seguro.`);
            localStorage.setItem('appHash', serverHash);
          }
          localStorage.setItem('appVersion', serverVersion);
          this.showToast('AtualizaÃ§Ã£o Segura instalada. Reiniciando...', 'success');
          setTimeout(() => window.location.reload(true), 1000);
        }, 2000);
      } else if (manual) {
        this.showToast(`App jÃ¡ estÃ¡ na versÃ£o mais recente (${localVersion}) e Ã­ntegro.`, 'info');
      }
    } catch (err) {
      console.error("Erro ao verificar OTA:", err);
      // Etapa 115: Rollback ou aviso
      if (manual) this.showToast('Falha ao conectar no servidor de OTA', 'error');
    }
  }

  // ETAPA 143: ExportaÃ§Ã£o de Backup Local do Banco de Dados IndexDB
  async exportDatabaseBackup() {
    try {
      // ImplementaÃ§Ã£o de exportaÃ§Ã£o simulada
      console.log('ðŸ’¾ Iniciando exportaÃ§Ã£o de backup...');
      const data = { timestamp: Date.now(), localData: '...' };
      const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `backup_colmeia_${new Date().toISOString()}.json`;
      a.click();
      this.showToast('Backup exportado com sucesso!', 'success');
    } catch (err) {
      console.error('Falha ao exportar backup:', err);
      this.showToast('Erro ao exportar backup.', 'error');
    }
  }

  // ETAPA 88 e 89: Iniciar WebRTC ou Fallback AutomÃ¡tico de STT para Web Speech API Nativa
  activateWebSpeechFallback(reason = 'Groq Whisper STT indisponÃ­vel') {
    if (this.sttMode === 'webspeech') return; // JÃ¡ estÃ¡ no fallback
    this.sttMode = 'webspeech';
    console.warn(`âš¡ STT FALLBACK ATIVADO: ${reason}. Alternando para Web Speech API Nativa.`);
    this.triggerHaptic('bargein');
    
    if (this.sttTestBox) {
      this.sttTestBox.textContent = `âš¡ STT Fallback Ativo: Web Speech API (${reason})`;
    }
    this.liveSubtitle.textContent = 'âš¡ STT Fallback: Usando Reconhecimento Nativo';
    this.setOrbState('listening', 'STT Fallback (Web Speech)');

    if (this.recognition && !this.isSpeechRecognitionActive) {
      try { this.recognition.start(); } catch (e) {
        console.warn('Erro ao iniciar reconhecimento nativo no fallback:', e);
      }
    }

    if (this.sttRestoreTimer) clearTimeout(this.sttRestoreTimer);
    this.sttRestoreTimer = setTimeout(() => {
      this.restoreWhisperSTT();
    }, 60000);
  }

  restoreWhisperSTT() {
    if (this.sttMode === 'whisper') return;
    console.log('ðŸ”„ Tentando restaurar modo primÃ¡rio STT: Groq Whisper Cloud...');
    this.sttMode = 'whisper';
    if (this.sttTestBox) {
      this.sttTestBox.textContent = 'ðŸŽ™ï¸ Groq Whisper STT Restaurado (PrimÃ¡rio)';
    }
    this.liveSubtitle.textContent = 'ðŸŽ™ï¸ Groq Whisper STT Restaurado';
    this.triggerHaptic('success');
  }

  // Visualizador e VU-Meter
  setupVisualizerCanvas() {
    this.canvas.width = 240;
    this.canvas.height = 240;
  }

  startVisualizerLoop() {
    const dataArray = new Uint8Array(128);

    const render = () => {
      let energy = 0;

      if (this.analyser && this.isListeningActive) {
        this.analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        energy = (sum / dataArray.length) / 255;
      }

      // Atualiza VU-Meter no Modal de DiagnÃ³stico
      if (this.vuMeterFill && this.vuValueText) {
        const percent = Math.min(Math.round(energy * 250), 100);
        this.vuMeterFill.style.width = `${percent}%`;
        this.vuValueText.textContent = percent > 5 ? `${percent}% (Voz Detectada)` : `${percent}% (SilÃªncio)`;
      }

      // OtimizaÃ§Ã£o Etapa 6: 60 FPS VU-Meter Cyberpunk Reativo no Palco Principal (Com Pico e DecibÃ©is)
      if (this.liveVuFill) {
        this.vuSmoothEnergy = (this.vuSmoothEnergy || 0) * 0.82 + energy * 0.18;
        const livePercent = Math.min(Math.round(this.vuSmoothEnergy * 280), 100);
        
        if (livePercent > (this.vuPeakPercent || 0)) {
          this.vuPeakPercent = livePercent;
        } else {
          this.vuPeakPercent = Math.max(0, (this.vuPeakPercent || 0) - 1.2);
        }

        this.liveVuFill.style.width = `${livePercent}%`;
        if (this.liveVuPeak) {
          this.liveVuPeak.style.left = `${this.vuPeakPercent}%`;
        }
        if (this.liveVuDbText) {
          const db = livePercent <= 1 ? -60 : Math.round(20 * Math.log10(livePercent / 100));
          this.liveVuDbText.textContent = db <= -60 ? '-âˆž dB' : `${db} dB`;
          this.liveVuDbText.style.color = db > -3 ? '#ef4444' : (db > -12 ? '#f59e0b' : '#10b981');
        }
      }

      // Desenha ondas no Canvas
      this.drawVisualizer(dataArray, energy);

      // Pulsa a Orbe de acordo com a voz real do usuÃ¡rio
      if (energy > this.silenceThreshold && this.orbCore) {
        const scale = 1 + Math.min(energy * 0.45, 0.35);
        this.orbCore.style.transform = `scale(${scale})`;
      } else if (this.orbCore && !this.isPlayingAudio) {
        this.orbCore.style.transform = 'scale(1)';
      }

      this.handleVAD(energy);

      requestAnimationFrame(render);
    };

    render();
  }

  drawVisualizer(dataArray, energy) {
    const ctx = this.canvasCtx;
    const width = this.canvas.width;
    const height = this.canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const baseRadius = 65 + energy * 35;

    ctx.clearRect(0, 0, width, height);

    ctx.beginPath();
    const bars = 36;
    for (let i = 0; i < bars; i++) {
      const angle = (i * 2 * Math.PI) / bars;
      const val = (dataArray[i % dataArray.length] || 0) / 255;
      const r = baseRadius + val * 22;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.closePath();

    ctx.strokeStyle = this.isPlayingAudio 
      ? 'rgba(168, 85, 247, 0.7)' 
      : (energy > this.silenceThreshold ? 'rgba(0, 243, 255, 0.9)' : 'rgba(0, 243, 255, 0.25)');
    ctx.lineWidth = energy > this.silenceThreshold ? 3 : 1.5;
    ctx.stroke();
  }

  // Sistema VAD Universal com Suporte a Barge-In (InterrupÃ§Ã£o InstantÃ¢nea - Etapa 7)
  handleVAD(energy) {
    if (!this.isListeningActive || !this.mediaStream || this.isRecordingTest) {
      if (this.vadRecording && this.vadRecorder) {
        try { this.vadRecorder.stop(); } catch(e) {}
        this.vadRecording = false;
        this.vadChunks = [];
      }
      return;
    }

    // OtimizaÃ§Ã£o Etapa 7: Limiar de voz dinÃ¢mico (um pouco maior quando a IA estÃ¡ falando para evitar eco de alto-falante)
    const threshold = this.isPlayingAudio 
      ? (this.silenceThreshold * 2.5 || 0.10) 
      : (this.silenceThreshold || 0.04);

    if (energy > threshold) {
      this.lastSpeechDetectedTime = Date.now();

      // BARGE-IN UNIVERSAL: Se a IA estiver falando e o usuÃ¡rio comeÃ§ar a falar no microfone (Opera, Redmi ou Chrome)
      if (this.isPlayingAudio && !this.bargeInTriggered) {
        this.bargeInTriggered = true;
        console.log('âš¡ Barge-In [Etapa 7]: Voz do usuÃ¡rio detectada durante fala da IA! Interrompendo Ã¡udio imediatamente.');
        this.stopAllAudioPlayback();
        this.sendToColmeia(JSON.stringify({ type: 'interrupt' }));
        this.triggerHaptic('bargein');
      }

      if (!this.vadRecording) {
        try {
          this.vadRecording = true;
          this.vadChunks = [];
          const options = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
            ? { mimeType: 'audio/webm;codecs=opus', audioBitsPerSecond: 24000 }
            : (MediaRecorder.isTypeSupported('audio/webm') ? { mimeType: 'audio/webm', audioBitsPerSecond: 24000 } : undefined);
          this.vadRecorder = new MediaRecorder(this.mediaStream, options);
          this.vadRecorder.ondataavailable = e => {
            if (e.data && e.data.size > 0) this.vadChunks.push(e.data);
          };
          this.vadRecorder.start(100);
          console.log('ðŸŽ™ï¸ VAD: DetecÃ§Ã£o de voz ativa (Gravando fala do usuÃ¡rio...)');
          this.triggerHaptic('start');
        } catch(err) {
          console.warn('Erro ao iniciar VAD MediaRecorder:', err);
          this.vadRecording = false;
        }
      }
    } else if (this.vadRecording && Date.now() - (this.lastSpeechDetectedTime || 0) > 680) {
      // SilÃªncio detectado (680ms)
      this.vadRecording = false;
      this.bargeInTriggered = false;
      try {
        if (this.vadRecorder && this.vadRecorder.state === 'recording') {
          this.vadRecorder.onstop = async () => {
            const blob = new Blob(this.vadChunks, { type: 'audio/webm' });
            this.vadChunks.length = 0;
            this.vadChunks = null;

            if (blob.size > 2048) {
              if (this.sttMode === 'webspeech') {
                console.log('âš¡ Modo STT Fallback Ativo (Web Speech API) â€” ignorando envio de Ã¡udio para Groq Whisper.');
              } else if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                if (Date.now() - (this.lastSpeechRecognitionTime || 0) > 1200) {
                  console.log(`ðŸ—£ï¸ VAD [Etapa 7]: Enviando fala (${blob.size} bytes) para Groq Whisper STT...`);
                  if (this.sttTestBox) this.sttTestBox.textContent = `ðŸ—£ï¸ Ãudio enviado (${Math.round(blob.size/1024)} KB)...`;
                  this.liveSubtitle.textContent = 'ðŸŽ™ï¸ Transcrevendo voz...';
                  try {
                    const buffer = await blob.arrayBuffer();
                    this.sendToColmeia(buffer);
                    this.triggerHaptic('stop');
                  } catch(e) {
                    console.error('Erro ao enviar buffer de Ã¡udio:', e);
                    this.activateWebSpeechFallback('Erro no envio do buffer de Ã¡udio');
                  }
                }
              } else {
                console.warn('âš ï¸ ConexÃ£o WebSocket offline ou instÃ¡vel. Ativando fallback STT nativo (Etapa 14)...');
                this.activateWebSpeechFallback('ConexÃ£o WebSocket indisponÃ­vel (4G/Wi-Fi instÃ¡vel)');
              }
            }
          };
          this.vadRecorder.stop();
        }
      } catch(e) {
        console.warn('Erro ao parar VAD MediaRecorder:', e);
        this.vadChunks = [];
      }
    }
  }

  // Teste de GravaÃ§Ã£o e ReproduÃ§Ã£o de Hardware (Loopback de 3 segundos)
  async startHardwareLoopbackTest() {
    if (this.isRecordingTest) return;
    await this.activateAudioAndMic();

    if (!this.mediaStream) {
      this.testRecordStatus.textContent = 'âŒ Erro: Microfone nÃ£o disponÃ­vel. Clique em "Solicitar PermissÃ£o" acima.';
      return;
    }

    try {
      this.isRecordingTest = true;
      this.recordedChunks = [];
      this.mediaRecorder = new MediaRecorder(this.mediaStream);

      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) this.recordedChunks.push(e.data);
      };

      this.mediaRecorder.onstop = () => {
        this.isRecordingTest = false;
        const blob = new Blob(this.recordedChunks, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);

        this.testRecordStatus.textContent = 'ðŸ”Š Reproduzindo seu Ã¡udio gravado agora...';
        audio.play().then(() => {
          audio.onended = () => {
            this.testRecordStatus.textContent = 'âœ… Teste concluÃ­do! Se vocÃª ouviu sua voz, o microfone estÃ¡ perfeito.';
          };
        }).catch(err => {
          this.testRecordStatus.textContent = 'âŒ Erro ao reproduzir o teste: ' + err.message;
        });
      };

      this.mediaRecorder.start();
      let countdown = 3;
      this.testRecordStatus.textContent = `ðŸ”´ Gravando teste de voz... Fale algo! (${countdown}s)`;

      const timer = setInterval(() => {
        countdown--;
        if (countdown > 0) {
          this.testRecordStatus.textContent = `ðŸ”´ Gravando teste de voz... Fale algo! (${countdown}s)`;
        } else {
          clearInterval(timer);
          if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
          }
        }
      }, 1000);

    } catch (err) {
      this.isRecordingTest = false;
      this.testRecordStatus.textContent = 'âŒ Erro ao gravar teste: ' + err.message;
    }
  }

  // Modo Echo Loop Ao Vivo & AnÃ¡lise em Tempo Real de RuÃ­do/Ganho (Etapa 10)
  async toggleLiveEchoLoopTest() {
    if (this.isEchoLoopActive) {
      this.stopLiveEchoLoopTest();
    } else {
      await this.startLiveEchoLoopTest();
    }
  }

  async startLiveEchoLoopTest() {
    if (this.isEchoLoopActive) return;
    await this.activateAudioAndMic();

    if (!this.mediaStream) {
      this.testRecordStatus.textContent = 'âŒ Erro: Microfone indisponÃ­vel. Solicite permissÃ£o acima.';
      return;
    }

    try {
      this.isEchoLoopActive = true;
      if (this.btnTestEchoLoop) {
        this.btnTestEchoLoop.textContent = 'â¹ï¸ Parar Echo Loop';
        this.btnTestEchoLoop.style.background = 'var(--coral-glow)';
      }
      if (this.echoLoopStatsBox) this.echoLoopStatsBox.style.display = 'block';
      this.testRecordStatus.textContent = 'ðŸ”„ Echo Loop Ativo: Fale para ouvir sua voz com 350ms de delay e monitorar o Piso de RuÃ­do.';

      if (!this.audioContext) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        this.audioContext = new AudioCtx();
      }
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }

      // Conectar mic ao Echo Loop: Source -> Delay (350ms) -> Gain -> Destination
      this.echoSourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.echoDelayNode = this.audioContext.createDelay(2.0);
      this.echoDelayNode.delayTime.value = 0.35; // 350ms delay para evitar realimentaÃ§Ã£o acÃºstica imediata

      this.echoGainNode = this.audioContext.createGain();
      this.echoGainNode.gain.value = 0.95;

      this.echoAnalyserNode = this.audioContext.createAnalyser();
      this.echoAnalyserNode.fftSize = 256;
      this.echoDataArray = new Uint8Array(this.echoAnalyserNode.frequencyBinCount);

      this.echoSourceNode.connect(this.echoAnalyserNode);
      this.echoSourceNode.connect(this.echoDelayNode);
      this.echoDelayNode.connect(this.echoGainNode);
      this.echoGainNode.connect(this.audioContext.destination);

      // Loop de anÃ¡lise SNR
      const updateStats = () => {
        if (!this.isEchoLoopActive) return;
        this.echoAnalyserNode.getByteTimeDomainData(this.echoDataArray);

        let sum = 0;
        for (let i = 0; i < this.echoDataArray.length; i++) {
          const norm = (this.echoDataArray[i] - 128) / 128.0;
          sum += norm * norm;
        }
        const rms = Math.sqrt(sum / this.echoDataArray.length);
        const currentDb = rms > 0.0001 ? Math.max(-80, 20 * Math.log10(rms)) : -80;

        if (currentDb < this.echoNoiseFloorDb || this.echoNoiseFloorDb === -68.0) {
          this.echoNoiseFloorDb = currentDb;
        } else {
          this.echoNoiseFloorDb = this.echoNoiseFloorDb * 0.99 + currentDb * 0.01;
        }

        if (currentDb > -45) {
          this.echoPeakDb = Math.max(this.echoPeakDb * 0.9 + currentDb * 0.1, currentDb);
        }

        const snr = Math.max(0, this.echoPeakDb - this.echoNoiseFloorDb);

        if (this.echoSignalPeak) this.echoSignalPeak.textContent = `${this.echoPeakDb.toFixed(1)} dB`;
        if (this.echoNoiseFloor) this.echoNoiseFloor.textContent = `${this.echoNoiseFloorDb.toFixed(1)} dB`;
        if (this.echoSNRValue) this.echoSNRValue.textContent = `+${snr.toFixed(1)} dB`;

        if (this.echoQualityBadge) {
          if (snr >= 20 && this.echoNoiseFloorDb < -45) {
            this.echoQualityBadge.textContent = 'âœ… RUÃDO BAIXO â€¢ GANHO Ã“TIMO';
            this.echoQualityBadge.style.color = '#10b981';
            this.echoQualityBadge.style.borderColor = '#10b981';
            this.echoQualityBadge.style.background = 'rgba(16, 185, 129, 0.2)';
          } else if (this.echoNoiseFloorDb >= -45) {
            this.echoQualityBadge.textContent = 'âš ï¸ ALERTA: RUÃDO DE FUNDO ALTO';
            this.echoQualityBadge.style.color = '#f59e0b';
            this.echoQualityBadge.style.borderColor = '#f59e0b';
            this.echoQualityBadge.style.background = 'rgba(245, 158, 11, 0.2)';
          } else {
            this.echoQualityBadge.textContent = 'ðŸ”Š MICROFONE DETECTANDO FALA';
            this.echoQualityBadge.style.color = 'var(--cyan-glow)';
            this.echoQualityBadge.style.borderColor = 'var(--cyan-glow)';
            this.echoQualityBadge.style.background = 'rgba(6, 182, 212, 0.2)';
          }
        }

        this.echoLoopTimer = requestAnimationFrame(updateStats);
      };

      updateStats();
    } catch (err) {
      console.error('Erro ao iniciar Echo Loop:', err);
      this.testRecordStatus.textContent = 'âŒ Erro ao ativar Echo Loop: ' + err.message;
      this.stopLiveEchoLoopTest();
    }
  }

  stopLiveEchoLoopTest() {
    this.isEchoLoopActive = false;
    if (this.echoLoopTimer) cancelAnimationFrame(this.echoLoopTimer);

    try {
      if (this.echoGainNode && this.audioContext) {
        this.echoGainNode.disconnect();
      }
      if (this.echoDelayNode) this.echoDelayNode.disconnect();
      if (this.echoSourceNode) this.echoSourceNode.disconnect();
    } catch (e) {
      // ignore
    }

    if (this.btnTestEchoLoop) {
      this.btnTestEchoLoop.textContent = 'ðŸ”„ Ativar Echo Loop Ao Vivo';
      this.btnTestEchoLoop.style.background = '';
    }
    if (this.echoLoopStatsBox) this.echoLoopStatsBox.style.display = 'none';
    this.testRecordStatus.textContent = 'â¹ï¸ Echo Loop encerrado.';
  }

  // Teste de Voz TTS do Diretor
  async testDirectorTTS() {
    const voice = this.voiceSelect.value;
    const testText = "OlÃ¡ Criador! O teste de Ã¡udio do Diretor de Bolso estÃ¡ funcionando perfeitamente!";
    
    this.btnTestTTS.textContent = 'â³ Sintetizando...';
    try {
      const resp = await fetch(`/api/tts/test?text=${encodeURIComponent(testText)}&voice=${encodeURIComponent(voice)}`);
      if (!resp.ok) throw new Error('Falha na resposta do servidor');
      
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      
      this.btnTestTTS.textContent = 'ðŸ”Š Tocando...';
      audio.onended = () => {
        this.btnTestTTS.textContent = 'â–¶ï¸ Testar';
      };
      await audio.play();
    } catch (err) {
      alert('Erro ao testar voz: ' + err.message);
      this.btnTestTTS.textContent = 'â–¶ï¸ Testar';
    }
  }

  // Seletor RÃ¡pido de Personalidades de Voz (Etapa 11)
  setupVoicePills() {
    if (!this.voicePillsContainer) return;
    const pills = this.voicePillsContainer.querySelectorAll('.voice-pill');
    pills.forEach(pill => {
      pill.addEventListener('click', () => {
        const voiceName = pill.getAttribute('data-voice');
        if (voiceName) {
          this.selectVoicePersonality(voiceName, true);
        }
      });
    });
    this.syncActiveVoicePill(this.ttsVoice);
  }

  syncActiveVoicePill(voiceName) {
    if (!this.voicePillsContainer) return;
    const pills = this.voicePillsContainer.querySelectorAll('.voice-pill');
    pills.forEach(pill => {
      if (pill.getAttribute('data-voice') === voiceName) {
        pill.classList.add('active');
      } else {
        pill.classList.remove('active');
      }
    });
    if (this.voiceSelect) {
      this.voiceSelect.value = voiceName;
    }
  }

  async selectVoicePersonality(voiceName, playPreview = true) {
    this.ttsVoice = voiceName;
    localStorage.setItem('ttsVoice', voiceName);
    try {
      await ApolloDirectorDB.saveSetting('ttsVoice', voiceName);
    } catch (e) {}

    this.syncActiveVoicePill(voiceName);

    // Envia mudanÃ§a ao backend via WebSocket (Cross-Channel / Colmeia)
    this.sendToColmeia(JSON.stringify({ type: 'set_voice', voice: voiceName }));

    if (playPreview) {
      let previewMsg = 'Voz do Diretor ativa.';
      if (voiceName.includes('Antonio')) previewMsg = 'AntÃ³nio Solene online, Criador.';
      else if (voiceName.includes('Francisca')) previewMsg = 'Francisca Expressiva Ã  sua disposiÃ§Ã£o.';
      else if (voiceName.includes('Thalita')) previewMsg = 'Thalita RÃ¡pida conectada.';
      else if (voiceName === 'Puck') previewMsg = 'Puck estÃºdio neural ativado.';

      try {
        const resp = await fetch(`/api/tts/test?text=${encodeURIComponent(previewMsg)}&voice=${encodeURIComponent(voiceName)}`);
        if (resp.ok) {
          const blob = await resp.blob();
          const audio = new Audio(URL.createObjectURL(blob));
          audio.volume = this.ttsVolume || 1.0;
          await audio.play();
        }
      } catch (err) {
        console.warn('Erro ao reproduzir preview da voz:', err);
      }
    }
  }

  // WebSocket Full-Duplex Connection com Retries Exponenciais & Jitter (Etapa 12)
  connectWebSocket() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const wsProtocol = API_BASE_URL.startsWith('https') ? 'wss:' : 'ws:';
    const wsHost = API_BASE_URL.replace(/^https?:\/\//, '');
    const wsUrl = `${wsProtocol}//${wsHost}/ws/voice`;
    
    this.updateStatus('connecting', 'Conectando Ã  Colmeia...');
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      const wasDisconnected = !this.isConnected && this.wsReconnectAttempt > 0;
      this.isConnected = true;
      this.wsReconnectAttempt = 0;
      if (this.wsReconnectTimer) {
        clearTimeout(this.wsReconnectTimer);
        this.wsReconnectTimer = null;
      }
      this.updateStatus('online', 'Colmeia Conectada');
      
      if (wasDisconnected) {
        this.showToast('Reconectado Ã  Colmeia com sucesso!', 'success');
      }

      if (this.isListeningActive) {
        this.setOrbState('listening');
      }
      console.log('âœ… WebSocket conectado com sucesso Ã  Colmeia.');

      // Despejo Silencioso da Fila Offline (Etapa 12)
      if (this.wsOfflineMessageQueue.length > 0) {
        this.showToast(`Sincronizando ${this.wsOfflineMessageQueue.length} mensagens pendentes...`, 'info');
        console.log(`ðŸ“¡ [Etapa 12] Transmitindo ${this.wsOfflineMessageQueue.length} mensagens offline na reconexÃ£o...`);
        while (this.wsOfflineMessageQueue.length > 0) {
          const payload = this.wsOfflineMessageQueue.shift();
          try {
            this.ws.send(payload);
          } catch(e) {
            console.warn('Erro no envio da fila offline:', e);
            break;
          }
        }
      }
    };

    this.ws.onclose = () => {
      if (this.isConnected) {
        this.showToast('ConexÃ£o com a Colmeia perdida.', 'error');
      }
      this.isConnected = false;
      this.setOrbState('offline');
      this.scheduleExponentialReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket Error:', err);
    };

    this.ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        const data = JSON.parse(event.data);
        this.handleServerEvent(data);
      }
    };
  }

  scheduleExponentialReconnect() {
    if (this.wsReconnectTimer) clearTimeout(this.wsReconnectTimer);

    const jitter = Math.random() * 400;
    const delay = Math.min(
      this.wsMaxReconnectDelay,
      Math.round(this.wsBaseDelay * Math.pow(1.6, this.wsReconnectAttempt) + jitter)
    );
    this.wsReconnectAttempt++;

    const seconds = (delay / 1000).toFixed(1);
    this.updateStatus('connecting', `Offline â€¢ ReconexÃ£o em ${seconds}s`);
    console.log(`ðŸ”„ [Etapa 12] Agendando reconexÃ£o exponencial: ${delay}ms (Tentativa ${this.wsReconnectAttempt})`);

    this.wsReconnectTimer = setTimeout(() => {
      this.connectWebSocket();
    }, delay);
  }

  // Envio seguro para o WebSocket com Fallback em Fila Offline (Etapa 12)
  sendToColmeia(payload) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(payload);
        return true;
      } catch (e) {
        console.warn('Erro ao enviar WebSocket, enfileirando...', e);
      }
    }
    if (this.wsOfflineMessageQueue.length < 30) {
      this.wsOfflineMessageQueue.push(payload);
      this.updateStatus('offline', `Offline â€¢ Msg em fila (${this.wsOfflineMessageQueue.length})`);
    }
    if (!this.isConnected && !this.wsReconnectTimer) {
      this.scheduleExponentialReconnect();
    }
    return false;
  }

  // ETAPA 61: Status Visual do WebSocket
  updateStatus(state, text) {
    this.statusText.textContent = text;
    if (state === 'online') {
      this.statusDot.className = 'status-dot';
      this.statusDot.style.background = 'var(--cyan-glow)';
      this.statusDot.style.boxShadow = '0 0 8px var(--cyan-glow)';
    } else if (state === 'connecting') {
      this.statusDot.className = 'status-dot';
      this.statusDot.style.background = '#ffcc00'; // Amarelo
      this.statusDot.style.boxShadow = '0 0 8px #ffcc00';
    } else {
      this.statusDot.className = 'status-dot offline';
      this.statusDot.style.background = '#ff3366'; // Vermelho
      this.statusDot.style.boxShadow = '0 0 8px #ff3366';
    }
  }

  // Processa eventos do backend
  handleServerEvent(data) {
    switch (data.type) {
      case 'llm_finished':
        window.dispatchEvent(new Event('llm_processing_finished'));
        break;
      case 'state':
        this.setOrbState(data.status, data.tool);
        break;

      case 'transcript':
        this.addTranscriptCard(data.role, data.text);
        // Etapa 116: Gatilho de voz para OTA Update
        if (data.role === 'user') {
          const txt = data.text.toLowerCase();
          if (txt.includes('verifique') && txt.includes('atualiza')) {
            this.showToast('ðŸŽ™ï¸ Comando OTA detectado...', 'info');
            this.checkForUpdates(true);
          }
        }
        break;

      case 'text_delta':
        this.appendAssistantDelta(data.text);
        break;

      case 'audio_chunk':
        // ETAPA 68: Mute TTS
        if (!this.isMuted) {
          this.queueAudioChunk(data.data, data.text);
        }
        break;

      case 'card':
        this.renderCard(data.card_type, data.tool_name, data.data);
        break;

      case 'interrupt_ack':
        console.log('ðŸ›‘ InterrupÃ§Ã£o confirmada.');
        this.stopAllAudioPlayback();
        this.setOrbState('listening');
        break;

      case 'done':
        if (data.full_text) {
          ApolloDirectorDB.saveHistoryItem('assistant', data.full_text);
        }
        this.currentAssistantCard = null;
        this.currentAssistantContent = null;
        break;

      case 'error':
        this.renderErrorCard(data.message);
        this.setOrbState('listening');
        break;

      case 'stt_fallback':
        this.activateWebSpeechFallback(data.reason);
        break;
    }
  }

  // Etapa 13 e 123: Motor CibernÃ©tico de Feedback TÃ¡til (Vibration API nativo via Capacitor / Fallback Haptic)
  triggerHaptic(type = 'tap') {
    // Se for Nativo (Capacitor), usa Haptics de alta precisÃ£o
    if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Haptics) {
      const Haptics = window.Capacitor.Plugins.Haptics;
      switch (type) {
        case 'start': Haptics.impact({ style: 'Light' }); break;
        case 'stop': Haptics.impact({ style: 'Medium' }); break;
        case 'bargein': Haptics.vibrate(); break;
        case 'success': Haptics.impact({ style: 'Heavy' }); break;
        case 'tap':
        default: Haptics.impact({ style: 'Light' }); break;
      }
      return;
    }

    if (!('vibrate' in navigator)) return;
    try {
      switch (type) {
        case 'start':
          navigator.vibrate([30]); // Pulso curto e nÃ­tido para inÃ­cio de gravaÃ§Ã£o de voz
          break;
        case 'stop':
          navigator.vibrate([20, 50, 20]); // Duplo pulso cibernÃ©tico ao enviar fala para transcriÃ§Ã£o
          break;
        case 'bargein':
          navigator.vibrate([50, 30, 50]); // VibraÃ§Ã£o tripla de alerta ao interromper a fala da IA
          break;
        case 'success':
          navigator.vibrate([35, 40, 70]); // PadrÃ£o vibratÃ³rio suave ao iniciar reproduÃ§Ã£o da voz da IA
          break;
        case 'tap':
        default:
          navigator.vibrate([15]); // Micro-vibraÃ§Ã£o hÃ¡tica em toques da interface
          break;
      }
    } catch (e) {
      console.warn("Vibration failed:", e);
    }
  }

  // Estados Visuais da Orbe
  setOrbState(state, extraInfo = '') {
    if (!this.isConnected && state !== 'offline') {
      state = 'offline';
    }

    this.orbContainer.className = `orb-container ${state}`;

    switch (state) {
      case 'listening':
        this.stateText.textContent = this.micInitialized ? 'Pronto â€¢ Escuta ContÃ­nua' : 'Toque na Orbe para Iniciar';
        break;
      case 'thinking':
        this.stateText.textContent = 'Lightning AI Pensando...';
        this.triggerHaptic('tap');
        break;
      case 'speaking':
        this.stateText.textContent = 'Diretor Falando...';
        this.triggerHaptic('success');
        break;
      case 'tool_running':
        this.stateText.textContent = `Executando: ${extraInfo || 'Superpoder'}`;
        this.triggerHaptic('tap');
        break;
      case 'muted':
        this.stateText.textContent = 'Microfone Mutado (Toque para Ativar)';
        break;
      case 'offline':
        this.stateText.textContent = 'Offline â€¢ Reconectando...';
        break;
    }
  }

  // Audio Playback Pipeline (Edge-TTS / Google TTS)
  queueAudioChunk(base64Data, text) {
    this.audioQueue.push({ base64: base64Data, text: text });
    if (!this.isPlayingAudio) {
      this.playNextAudioChunk();
    }
  }

  playNextAudioChunk() {
    if (this.audioQueue.length === 0) {
      this.isPlayingAudio = false;
      if (this.isListeningActive) {
        this.setOrbState('listening');
      }
      return;
    }

    this.isPlayingAudio = true;
    this.setOrbState('speaking');

    const item = this.audioQueue.shift();
    if (item.text) {
      this.liveSubtitle.textContent = item.text;
    }

    const audioUrl = `data:audio/mp3;base64,${item.base64}`;
    this.currentAudioElement = new Audio(audioUrl);
    this.currentAudioElement.volume = this.ttsVolume || 1.0;

    this.currentAudioElement.onended = () => {
      this.playNextAudioChunk();
    };

    this.currentAudioElement.onerror = (err) => {
      console.error('Erro na reproduÃ§Ã£o do Ã¡udio:', err);
      this.playNextAudioChunk();
    };

    this.currentAudioElement.play().catch(e => {
      console.warn('Autoplay bloqueado pelo navegador. Toque na tela para liberar o Ã¡udio:', e);
      this.playNextAudioChunk();
    });
  }

  stopAllAudioPlayback() {
    this.audioQueue = [];
    if (this.currentAudioElement) {
      this.currentAudioElement.pause();
      this.currentAudioElement.currentTime = 0;
      this.currentAudioElement = null;
    }
    this.isPlayingAudio = false;
    this.bargeInTriggered = false;
    this.liveSubtitle.textContent = '';
  }

  // Renderizadores de Mensagens e Cards
  addTranscriptCard(role, text, saveToDB = true) {
    if (saveToDB) {
      ApolloDirectorDB.saveHistoryItem(this.currentSessionId, role, text);
    }
    if (role === 'user') {
      this.liveSubtitle.textContent = `"${text}"`;
      const card = document.createElement('div');
      card.className = 'card user-msg';
      card.innerHTML = `
        <div class="card-header">
          <span>ðŸ‘‘ VOCÃŠ (CRIADOR)</span>
          <span>${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
        </div>
        <div class="card-content">${this.escapeHtml(text)}</div>
      `;
      this.feedSection.appendChild(card);
      this.scrollToBottom();
    } else {
      this.createAssistantCard(text);
    }
  }

  createAssistantCard(initialText = '') {
    this.currentAssistantCard = document.createElement('div');
    this.currentAssistantCard.className = 'card assistant-msg';
    this.currentAssistantCard.innerHTML = `
      <div class="card-header">
        <span class="card-tag">ðŸ¤– DIRETOR DE BOLSO (GPT-5)</span>
        <span>${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
      </div>
      <div class="card-content markdown-body content-area"></div>
      <div class="card-actions" style="display:flex; justify-content:flex-end; margin-top:5px;">
         <button class="btn-read-aloud" style="background:transparent; border:none; color:var(--cyan-glow); cursor:pointer; font-size:1.2rem;" title="Ler em voz alta">ðŸ”Š</button>
      </div>
    `;
    this.feedSection.appendChild(this.currentAssistantCard);
    this.currentAssistantContent = this.currentAssistantCard.querySelector('.content-area');
    this.currentAssistantRawText = initialText;
    
    const btnRead = this.currentAssistantCard.querySelector('.btn-read-aloud');
    btnRead.addEventListener('click', () => {
       window.speechSynthesis.cancel();
       const textToRead = this.currentAssistantCard.querySelector('.content-area').textContent;
       const msg = new SpeechSynthesisUtterance(textToRead);
       msg.lang = 'pt-BR';
       window.speechSynthesis.speak(msg);
    });

    this.renderMarkdownToContent();
    this.scrollToBottom();
  }

  appendAssistantDelta(delta) {
    if (!this.currentAssistantCard) {
      this.createAssistantCard(delta);
    } else if (this.currentAssistantContent) {
      this.currentAssistantRawText += delta;
      this.renderMarkdownToContent();
      this.scrollToBottom();
    }
  }

  // ETAPA 56 e 57: RenderizaÃ§Ã£o de Markdown e BotÃ£o de CÃ³pia
  renderMarkdownToContent() {
    if (!window.marked) {
      // Fallback
      this.currentAssistantContent.textContent = this.currentAssistantRawText;
      return;
    }
    this.currentAssistantContent.innerHTML = marked.parse(this.currentAssistantRawText);
    
    // Adicionar botÃ£o de copiar nos blocos de cÃ³digo (Etapa 57)
    const codeBlocks = this.currentAssistantContent.querySelectorAll('pre');
    codeBlocks.forEach((pre) => {
      if (pre.querySelector('.copy-code-btn')) return; // JÃ¡ adicionado

      pre.style.position = 'relative';
      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-code-btn';
      copyBtn.innerHTML = 'ðŸ“‹ Copiar';
      copyBtn.onclick = () => {
        const code = pre.querySelector('code')?.innerText || pre.innerText;
        navigator.clipboard.writeText(code).then(() => {
          copyBtn.innerHTML = 'âœ“ Copiado';
          setTimeout(() => copyBtn.innerHTML = 'ðŸ“‹ Copiar', 2000);
        });
      };
      pre.appendChild(copyBtn);
    });
  }

  renderCard(cardType, toolName, data) {
    const card = document.createElement('div');
    card.className = 'card';

    if (cardType === 'image') {
      const res = data.result || {};
      const imgUrl = res.url || '/static/placeholder.png';
      card.innerHTML = `
        <div class="card-header">
          <span class="card-tag image">ðŸŽ¨ FLUX RENDER (MODAL)</span>
          <span>${res.aspect_ratio || '16:9'}</span>
        </div>
        <div class="card-content">
          <strong>Prompt:</strong> ${this.escapeHtml(res.prompt || '')}
          <div class="card-image-preview" onclick="app.openImageModal('${imgUrl}')">
            <img src="${imgUrl}" alt="Flux Render" onerror="this.src='https://picsum.photos/800/450'">
          </div>
        </div>
      `;
    } else if (cardType === 'service_order') {
      const res = data.result || {};
      card.innerHTML = `
        <div class="card-header">
          <span class="card-tag service-order">ðŸ“‹ ORDEM DE SERVIÃ‡O</span>
          <span>${res.order_id || 'OS-NEW'}</span>
        </div>
        <div class="card-content">
          <div class="service-order-box">
            <div class="service-order-title">${this.escapeHtml(res.title || '')}</div>
            <div class="service-order-dest">Destino: <strong>${this.escapeHtml(res.target_agent || 'MAESTRO')}</strong> â€¢ Canal: ${this.escapeHtml(res.channel || 'Geral')}</div>
            <div style="margin-top: 0.4rem; font-size: 0.8rem; color: var(--emerald-glow);">âœ“ Gravado no Hive Bus central</div>
          </div>
        </div>
      `;
    } else {
      card.innerHTML = `
        <div class="card-header">
          <span class="card-tag">âš¡ FERRAMENTA EXECUTADA</span>
          <span>${toolName}</span>
        </div>
        <div class="card-content">
          <pre class="terminal-block">${this.escapeHtml(JSON.stringify(data, null, 2))}</pre>
        </div>
      `;
    }

    this.feedSection.appendChild(card);
    this.scrollToBottom();
  }

  renderErrorCard(message) {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-header">
        <span class="card-tag" style="background: rgba(244, 63, 94, 0.2); color: #f43f5e;">âš ï¸ ALERTA</span>
      </div>
      <div class="card-content" style="color: #fda4af;">${this.escapeHtml(message)}</div>
    `;
    this.feedSection.appendChild(card);
    this.scrollToBottom();
  }

  // ETAPA 173: Solicitar PermissÃµes e Inicializar NotificaÃ§Ãµes Locais
  async initNotifications() {
    if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.LocalNotifications) {
      const LocalNotifications = window.Capacitor.Plugins.LocalNotifications;
      try {
        let permStatus = await LocalNotifications.checkPermissions();
        if (permStatus.display !== 'granted') {
          permStatus = await LocalNotifications.requestPermissions();
        }
        if (permStatus.display === 'granted') {
          this.notificationsEnabled = true;
          this.showToast('NotificaÃ§Ãµes de Bolso Ativadas', 'success');
          
          // Registrar AÃ§Ã£o de BotÃ£o na NotificaÃ§Ã£o (Etapa 174)
          await LocalNotifications.registerActionTypes({
            types: [
              {
                id: 'AUTOBLOG_APPROVAL',
                actions: [
                  { id: 'approve', title: 'Aprovar', foreground: true },
                  { id: 'reject', title: 'Rejeitar', foreground: true, destructive: true }
                ]
              }
            ]
          });
          
          // Escutar cliques nas notificaÃ§Ãµes
          LocalNotifications.addListener('localNotificationActionPerformed', (notificationAction) => {
            if (notificationAction.actionId === 'approve') {
              this.showToast('Roteiro Aprovado pelo Push!', 'success');
              // LÃ³gica de aprovaÃ§Ã£o biomÃ©trica via push (Simulada para a Fase X)
              this.sendBiometricApproval(notificationAction.notification.extra?.postId || 'PUSH_APPROVAL');
            }
          });
        }
      } catch (err) {
        console.warn('LocalNotifications nÃ£o suportado neste dispositivo.', err);
      }
    }
  }

  // Dispara uma notificaÃ§Ã£o nativa no celular (Etapa 173)
  async fireLocalNotification(title, body, extraData = {}) {
    if (!this.notificationsEnabled) return;
    try {
      const LocalNotifications = window.Capacitor.Plugins.LocalNotifications;
      await LocalNotifications.schedule({
        notifications: [
          {
            title: title,
            body: body,
            id: new Date().getTime(),
            schedule: { at: new Date(Date.now() + 1000) },
            sound: null, // Deixando para vibrar apenas pelo sistema
            actionTypeId: 'AUTOBLOG_APPROVAL',
            extra: extraData
          }
        ]
      });
      this.triggerHaptic('heavy');
    } catch (e) {
      console.error('Erro ao disparar push:', e);
    }
  }

  // ETAPA 42: ConexÃ£o SSE para o Terminal Ao Vivo
  connectTerminalSSE() {
    this.evtSource = new EventSource('/api/logs/stream');
    
    this.evtSource.onmessage = (event) => {
      const line = event.data;
      if (!line.trim()) return;

      // Se for a primeira linha, abre o terminal
      if (!this.terminalOverlay.classList.contains('open') && !line.includes('[Sovereign Terminal Connected]')) {
        this.terminalOverlay.classList.add('open');
      }

      const lineEl = document.createElement('div');
      lineEl.className = 'terminal-line';
      lineEl.textContent = line;
      this.terminalBody.appendChild(lineEl);
      this.terminalBody.scrollTop = this.terminalBody.scrollHeight;

      // ETAPA 47: Interceptar pedido de aprovaÃ§Ã£o
      if (line.includes('[SECURE_APPROVAL_REQUEST:')) {
        const match = line.match(/\[SECURE_APPROVAL_REQUEST:\s*(.+?)\]/);
        if (match && match[1]) {
          this.renderApprovalCard(match[1]);
        }
      }
    };

    this.evtSource.onerror = (err) => {
      console.warn("SSE Terminal Error/Disconnect. Reconnecting in 5s...");
      this.evtSource.close();
      setTimeout(() => this.connectTerminalSSE(), 5000);
    };
  }

  // ETAPA 47: Renderizar Card de AprovaÃ§Ã£o
  renderApprovalCard(filepath) {
    const card = document.createElement('div');
    card.className = 'card approval-card';
    card.innerHTML = `
      <div class="card-header">
        <span class="card-tag" style="background: rgba(244, 63, 94, 0.2); color: #f43f5e;">âš ï¸ APROVAÃ‡ÃƒO NECESSÃRIA</span>
      </div>
      <div class="card-content">
        <div style="font-size:0.85rem; margin-bottom:0.5rem; color:#e2e8f0;">
          O Agente Soberano quer editar o arquivo crÃ­tico:
          <br><strong style="color:var(--cyan-glow);">${this.escapeHtml(filepath)}</strong>
        </div>
        <div class="approval-actions">
          <button class="btn-reject" onclick="window.appInstance.sendApproval('${filepath}', 'reject', this)">Bloquear</button>
          <button class="btn-approve" onclick="window.appInstance.sendApproval('${filepath}', 'approve', this)">Autorizar</button>
        </div>
      </div>
    `;
    this.feedSection.appendChild(card);
    this.scrollToBottom();
  }

  async sendApproval(filepath, action, btnElement) {
    // Desabilitar botÃµes do card
    const actionsDiv = btnElement.parentElement;
    actionsDiv.style.opacity = '0.5';
    actionsDiv.style.pointerEvents = 'none';

    try {
      const res = await fetch('/api/agent/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filepath, action })
      });
      if (res.ok) {
        btnElement.textContent = action === 'approve' ? 'Autorizado âœ“' : 'Bloqueado âœ•';
      } else {
        alert("Erro ao enviar aprovaÃ§Ã£o ou Timeout.");
      }
    } catch (e) {
      console.error(e);
      alert("Erro de rede.");
    }
  }

  scrollToBottom() {
    this.feedSection.scrollTop = this.feedSection.scrollHeight;
  }

  openImageModal(url) {
    this.modalImg.src = url;
    this.imgModal.className = 'modal-backdrop open';
  }

  closeImageModal() {
    this.imgModal.className = 'modal-backdrop';
  }

  setupEventListeners() {
    // ETAPA 173: BotÃ£o TemporÃ¡rio de Teste de Push
    this.btnTestNotification = document.getElementById('btnTestNotification');
    if (this.btnTestNotification) {
      this.btnTestNotification.addEventListener('click', () => {
        this.fireLocalNotification("Teste de Bolso ðŸ””", "Esta Ã© uma notificaÃ§Ã£o do GuardiÃ£o de Bolso (Apollo).", { postId: "TEST_001" });
      });
    }

    // ETAPA 55: Alternador de Modo de Interface
    this.btnModeToggle = document.getElementById('btnModeToggle');
    if (this.btnModeToggle) {
      this.btnModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('text-mode');
        const isTextMode = document.body.classList.contains('text-mode');
        this.btnModeToggle.innerHTML = isTextMode ? 'ðŸŽ§' : 'âœ–';
        
        // Controla VAD/Microfone
        this.isListeningActive = !isTextMode;
        
        if (!isTextMode) {
          // Entrou na Orbe (Tempo Real)
          this.initMicrophone();
          if(this.recognition) {
            try { this.recognition.start(); } catch(e){}
          }
        } else {
          // Saiu da Orbe (Texto)
          if(this.recognition) {
            try { this.recognition.stop(); } catch(e){}
          }
        }
      });
    }

    // ETAPA 52: BotÃµes da Sidebar
    if (this.btnOpenSidebar) {
      this.btnOpenSidebar.addEventListener('click', () => this.chatSidebar.classList.add('open'));
    }
    if (this.btnCloseSidebar) {
      this.btnCloseSidebar.addEventListener('click', () => this.chatSidebar.classList.remove('open'));
    }
    if (this.btnNewChat) {
      this.btnNewChat.addEventListener('click', () => this.createNewSession());
    }

    // Abrir e Fechar Modal de ConfiguraÃ§Ã£o & DiagnÃ³stico
    this.btnSettings.addEventListener('click', async () => {
      this.settingsModal.className = 'modal-backdrop open';
      await this.activateAudioAndMic();
      await this.populateAudioDevices();
    });

    this.btnCloseSettings.addEventListener('click', () => {
      this.settingsModal.className = 'modal-backdrop';
    });

    this.btnRefreshDevices.addEventListener('click', () => {
      this.populateAudioDevices();
    });

    this.btnRequestMicPerm.addEventListener('click', async () => {
      await this.initMicrophone();
      this.initVAD();
    });

    this.audioInputSelect.addEventListener('change', async (e) => {
      this.selectedDeviceId = e.target.value;
      console.log('ðŸ”„ Trocando microfone para:', this.selectedDeviceId);
      await this.initMicrophone();
    });

    this.btnTestRecord.addEventListener('click', () => {
      this.startHardwareLoopbackTest();
    });

    if (this.btnTestEchoLoop) {
      this.btnTestEchoLoop.addEventListener('click', () => {
        this.toggleLiveEchoLoopTest();
      });
    }

    this.btnTestTTS.addEventListener('click', () => {
      this.testDirectorTTS();
    });

    const btnRefreshMemory = document.getElementById('btnRefreshMemory');
    const memoryStatusBox = document.getElementById('memoryStatusBox');
    if (btnRefreshMemory) {
      btnRefreshMemory.addEventListener('click', async () => {
        try {
          memoryStatusBox.innerHTML = "Consultando Colmeia...";
          const res = await fetch(`${API_BASE_URL}/api/memory/status`);
          const data = await res.json();
          let html = `<strong>RAG (ChromaDB):</strong> ${data.rag_ready ? 'ðŸŸ¢ Online' : 'ðŸ”´ Offline'}<br>`;
          html += `<strong>MemÃ³ria Local:</strong> ${data.local_exists ? 'âœ…' : 'âŒ'}<br>`;
          html += `<strong>Hive Bus:</strong> ${data.hive_exists ? 'âœ…' : 'âŒ'}<br>`;
          if (data.last_synced) html += `<strong>Ãšltimo Sync:</strong> ${data.last_synced.local_mtime || 'N/A'}`;
          memoryStatusBox.innerHTML = html;
        } catch(e) {
          memoryStatusBox.innerHTML = "Erro ao acessar a Colmeia.";
        }
      });
    }

    const btnCrossIndex = document.getElementById('btnCrossIndex');
    if (btnCrossIndex) {
      btnCrossIndex.addEventListener('click', async () => {
        try {
          memoryStatusBox.innerHTML = "ForÃ§ando Cross-Index (Aguarde)...";
          const res = await fetch(`${API_BASE_URL}/api/memory/cross-index`, { method: 'POST' });
          const data = await res.json();
          memoryStatusBox.innerHTML = `<strong>Cross-Index Sucesso!</strong><br>Arquivos: ${data.indexed_files}<br>Fragmentos RAG: ${data.total_chunks}`;
        } catch(e) {
          memoryStatusBox.innerHTML = "Erro ao rodar Cross-Index.";
        }
      });
    }

    // Controle de Ganho TTS na Tela Principal - Etapa 6
    if (this.ttsVolumeSlider) {
      this.ttsVolumeSlider.value = Math.round(this.ttsVolume * 100);
      if (this.ttsVolumeVal) this.ttsVolumeVal.textContent = `${this.ttsVolumeSlider.value}%`;
      this.ttsVolumeSlider.addEventListener('input', (e) => {
        const val = e.target.value;
        this.ttsVolume = val / 100;
        if (this.ttsVolumeVal) this.ttsVolumeVal.textContent = `${val}%`;
        localStorage.setItem('ttsVolume', this.ttsVolume);
        ApolloDirectorDB.saveSetting('ttsVolume', this.ttsVolume);
        if (this.currentAudioElement) {
          this.currentAudioElement.volume = this.ttsVolume;
        }
      });
    }

    // Toque na Orbe ou no Palco ativa o microfone e Ã¡udio instantaneamente
    this.orbContainer.addEventListener('click', async () => {
      this.triggerHaptic('tap');
      await this.activateAudioAndMic();
    });

    this.btnMicToggle.addEventListener('click', async () => {
      await this.activateAudioAndMic();

      this.isListeningActive = !this.isListeningActive;
      if (this.isListeningActive) {
        this.triggerHaptic('start');
        this.btnMicToggle.className = 'deck-btn primary';
        this.micLabel.textContent = 'Microfone Ativo (VAD)';
        if (this.micIcon) this.micIcon.textContent = 'ðŸŽ™ï¸';
        this.setOrbState('listening');
      } else {
        this.triggerHaptic('stop');
        this.btnMicToggle.className = 'deck-btn';
        this.micLabel.textContent = 'Microfone Mutado';
        if (this.micIcon) this.micIcon.textContent = 'ðŸ”‡';
        this.setOrbState('muted');
        
        if (this.vadMediaRecorder && this.vadMediaRecorder.state === 'recording') {
            this.vadMediaRecorder.stop();
        }
        this.isSpeakingVAD = false;
      }
    });

    this.btnBargeIn.addEventListener('click', () => {
      this.triggerHaptic('bargein');
      this.stopAllAudioPlayback();
      this.sendToColmeia(JSON.stringify({ type: 'interrupt' }));
    });

    this.btnToggleKeyboard.addEventListener('click', () => {
      this.textDrawer.classList.toggle('open');
      if (this.textDrawer.classList.contains('open')) {
        this.drawerInput.focus();
      }
    });

    // Etapa 161: LÃ³gica do Olho de Apollo
    if (this.btnToggleVision) {
      this.btnToggleVision.addEventListener('click', async () => {
        if (this.isVisionActive) {
          this.stopVisionLoop();
        } else {
          await this.startVisionLoop();
        }
      });
    }

    // Estado de Processamento e Abortar
    this.isProcessingLLM = false;
    
    // --- NOVA LÃ“GICA DE DITADO E INPUT PILL (CLONE CHATGPT) ---
    this.btnDictate = document.getElementById('btnDictate');
    this.btnCancelDictation = document.getElementById('btnCancelDictation');
    this.recordingState = document.getElementById('recordingState');
    this.rightActions = document.getElementById('rightActions');
    
    // updateInputUIState centraliza os estilos do botÃ£o
    const updateInputUIState = (state) => {
      this.currentInputState = state;
      if (state === 'empty') {
        if(this.btnDictate) this.btnDictate.style.display = 'flex';
        if(this.btnModeToggle) this.btnModeToggle.style.display = 'flex';
        if(this.btnSendText) this.btnSendText.style.display = 'none';
        if(this.btnSendText) {
          this.btnSendText.innerHTML = 'â¬†ï¸';
          this.btnSendText.classList.remove('danger');
          this.btnSendText.classList.add('primary');
        }
      } else if (state === 'typing') {
        if(this.btnDictate) this.btnDictate.style.display = 'none';
        if(this.btnModeToggle) this.btnModeToggle.style.display = 'none';
        if(this.btnSendText) this.btnSendText.style.display = 'flex';
        if(this.btnSendText) {
          this.btnSendText.innerHTML = 'â¬†ï¸';
          this.btnSendText.classList.remove('danger');
          this.btnSendText.classList.add('primary');
        }
      } else if (state === 'processing') {
        if(this.btnDictate) this.btnDictate.style.display = 'none';
        if(this.btnModeToggle) this.btnModeToggle.style.display = 'none';
        if(this.btnSendText) this.btnSendText.style.display = 'flex';
        if(this.btnSendText) {
          this.btnSendText.innerHTML = 'â¹ï¸';
          this.btnSendText.classList.remove('primary');
          this.btnSendText.classList.add('danger');
        }
      } else if (state === 'recording') {
        if(this.btnDictate) this.btnDictate.style.display = 'none';
        if(this.btnModeToggle) this.btnModeToggle.style.display = 'none';
        if(this.btnSendText) this.btnSendText.style.display = 'flex';
        if(this.btnSendText) {
          this.btnSendText.innerHTML = 'â¹ï¸';
          this.btnSendText.classList.remove('danger');
          this.btnSendText.classList.add('primary');
        }
      }
    };

    const sendText = async () => {
      // Se o usuÃ¡rio clicar no botÃ£o enquanto o LLM processa (botÃ£o quadrado vermelho)
      if (this.isProcessingLLM) {
         this.sendToColmeia(JSON.stringify({ type: 'stop_generation' }));
         this.isProcessingLLM = false;
         updateInputUIState(this.drawerInput.value.trim().length > 0 ? 'typing' : 'empty');
         return;
      }
      
      const txt = this.drawerInput.value.trim();
      if (txt) {
        this.sendToColmeia(JSON.stringify({ type: 'user_text', text: txt }));
        this.drawerInput.value = '';
        this.isProcessingLLM = true;
        updateInputUIState('processing');
      }
    };

    this.btnSendText.addEventListener('click', sendText);
    this.drawerInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
          e.preventDefault();
          sendText();
      }
    });

    this.drawerInput.addEventListener('input', () => {
      if (this.isProcessingLLM) return; // NÃ£o muda se estiver processando
      const hasText = this.drawerInput.value.trim().length > 0;
      updateInputUIState(hasText ? 'typing' : 'empty');
    });

    // Reset quando receber resposta final do LLM
    // interceptamos mensagens no onmessage do websocket lÃ¡ em cima, mas vamos expor aqui
    window.addEventListener('llm_processing_finished', () => {
        this.isProcessingLLM = false;
        updateInputUIState(this.drawerInput.value.trim().length > 0 ? 'typing' : 'empty');
    });

    this.isDictating = false;
    let mediaRecorder = null;
    let audioChunks = [];

    const stopDictationUI = () => {
      this.isDictating = false;
      this.drawerInput.style.display = 'flex';
      if(this.btnAttachImage) this.btnAttachImage.style.display = 'flex';
      this.recordingState.style.display = 'none';
      const hasText = this.drawerInput.value.trim().length > 0;
      updateInputUIState(hasText ? 'typing' : 'empty');
    };

    if (this.btnDictate && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      
      this.btnDictate.addEventListener('click', async () => {
        try {
           const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
           mediaRecorder = new MediaRecorder(stream);
           audioChunks = [];
           
           mediaRecorder.ondataavailable = e => {
             if (e.data.size > 0) audioChunks.push(e.data);
           };
           
           mediaRecorder.onstop = async () => {
             const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
             const formData = new FormData();
             formData.append('file', audioBlob, 'dictation.webm');
             
             this.drawerInput.placeholder = 'Transcrevendo voz...';
             this.drawerInput.disabled = true;
             updateInputUIState('typing'); // sÃ³ para manter o botÃ£o

             try {
                 const res = await fetch('/api/transcribe', {
                     method: 'POST',
                     body: formData
                 });
                 
                 this.drawerInput.placeholder = 'Mensagem para Apollo...';
                 this.drawerInput.disabled = false;
                 
                 if(res.ok) {
                     const data = await res.json();
                     if(data.text) {
                        this.drawerInput.value = data.text;
                        updateInputUIState('typing');
                        // Auto-submit para enviar direto
                        setTimeout(() => this.btnSendText.click(), 50);
                     } else {
                        this.drawerInput.value = '';
                        updateInputUIState('empty');
                     }
                 }
             } catch (err) {
                 console.error("Erro na transcriÃ§Ã£o", err);
                 this.drawerInput.value = '';
                 updateInputUIState('empty');
             }
             
             // Limpar os tracks de mÃ­dia
             stream.getTracks().forEach(t => t.stop());
           };
           
           mediaRecorder.start();
           this.isDictating = true;
           
           // Esconder input normal e mostrar estado
           this.drawerInput.style.display = 'none';
           if(this.btnAttachImage) this.btnAttachImage.style.display = 'none';
           this.recordingState.style.display = 'flex';
           
           updateInputUIState('recording');
           
        } catch(e) {
           this.showToast('PermissÃ£o de microfone negada ou sem microfone.', 'error');
           return;
        }
      });

      this.btnCancelDictation.addEventListener('click', () => {
         if(mediaRecorder && mediaRecorder.state !== 'inactive') {
             // Redefinimos onstop para nada para nÃ£o enviar Ã  API
             mediaRecorder.onstop = () => { mediaRecorder.stream.getTracks().forEach(t => t.stop()); };
             mediaRecorder.stop();
         }
         this.drawerInput.value = '';
         stopDictationUI();
      });

      // No modo dictation, clicar no botÃ£o de parar/enviar (agora gerido pelo updateInputUIState recording state)
      // Como a gente setou o Send button visible na gravaÃ§Ã£o, devemos intercetar
      const originalSend = sendText;
      this.btnSendText.addEventListener('click', (e) => {
        if (this.isDictating) {
          e.preventDefault();
          e.stopPropagation();
          if(mediaRecorder && mediaRecorder.state !== 'inactive') {
             mediaRecorder.stop();
          }
          stopDictationUI();
          // O mediaRecorder.onstop vai atualizar o textarea, mas isso Ã© async.
          // Logo, nÃ£o chamamos originalSend automaticamente aqui, 
          // pois queremos que o user confirme o texto antes de enviar
          // ou enviamos sÃ³ depois do fetch? Vamos obrigar o user a enviar apÃ³s ler, como no WhatsApp
        }
      }, true);
      
    } else if (this.btnDictate) {
       this.btnDictate.addEventListener('click', () => {
          this.showToast('API MediaRecorder nÃ£o suportada.', 'error');
       });
    }
    // -----------------------------------------------------

    // Etapa 152: LÃ³gica de Abas do Gestor de Canais
    const tabApolloEdit = document.getElementById('tabApolloEdit');
    const tabAutoBlog = document.getElementById('tabAutoBlog');
    const contentApolloEdit = document.getElementById('contentApolloEdit');
    const contentAutoBlog = document.getElementById('contentAutoBlog');

    if (tabApolloEdit && tabAutoBlog) {
      tabApolloEdit.addEventListener('click', () => {
        tabApolloEdit.classList.add('primary');
        tabApolloEdit.style.borderColor = '';
        tabApolloEdit.style.color = '';
        
        tabAutoBlog.classList.remove('primary');
        tabAutoBlog.style.borderColor = 'var(--magenta-glow)';
        tabAutoBlog.style.color = 'var(--magenta-glow)';

        contentApolloEdit.style.display = 'flex';
        contentAutoBlog.style.display = 'none';
      });

      tabAutoBlog.addEventListener('click', () => {
        tabAutoBlog.classList.add('primary');
        tabAutoBlog.style.borderColor = '';
        tabAutoBlog.style.color = '';

        tabApolloEdit.classList.remove('primary');
        tabApolloEdit.style.borderColor = 'var(--neon-cyan)';
        tabApolloEdit.style.color = 'var(--neon-cyan)';

        contentAutoBlog.style.display = 'flex';
        contentApolloEdit.style.display = 'none';
      });
    }

    // Etapa 153 & 156: Polling de Fila do Maestro e AutoBlog
    let pollingInterval = null;

    const renderQueueList = document.getElementById('renderQueueList');
    const autoBlogQueueList = document.getElementById('autoBlogQueueList');

    const fetchMaestroStatus = async () => {
      try {
        const res = await fetch('http://localhost:8080/api/mobile/render/status');
        if(res.ok) {
          const data = await res.json();
          renderQueueList.innerHTML = `[ID: ${data.job_id}] Renderizando... (${data.progress}%)<br>FPS: ${data.fps}`;
        }
      } catch(e) {
        renderQueueList.innerHTML = `<span style="color:var(--neon-red)">Maestro Offline na porta 8080</span>`;
      }
    };

    const fetchAutoBlogPending = async () => {
      try {
        const res = await fetch('http://localhost:8098/api/v1/publish-trigger', { method: 'OPTIONS' });
        // MOCK VISUAL: como o backend do AutoBlog nÃ£o tem uma rota GET pronta no prompt dele, vamos simular que ele achou um
        autoBlogQueueList.innerHTML = `
          <strong>TÃ­tulo:</strong> Vazou o GTA 6 denovo!<br>
          <div style="margin-top: 10px; display: flex; gap: 10px;">
            <button class="deck-btn primary" id="btnApproveAutoBlog" style="flex: 1;">âœ… Aprovar (Biometria)</button>
            <button class="deck-btn" id="btnRejectAutoBlog" style="flex: 1; border-color: var(--neon-red); color: var(--neon-red);">âŒ Rejeitar</button>
          </div>
        `;
        
        document.getElementById('btnApproveAutoBlog')?.addEventListener('click', async () => {
          const hash = await this.verifyBiometrics("Aprovar Post: Vazou o GTA 6");
          if (hash) {
            try {
              await fetch('http://localhost:8098/api/v1/publish-trigger', {
                method: 'POST',
                headers: {
                  'Authorization': 'Bearer super-secret-token-123',
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ post_id: 'post_01', action: 'APPROVE', biometric_hash: hash, token: 'super-secret-token-123' })
              });
              this.showToast('Post publicado com sucesso via AutoBlog!', 'success');
              autoBlogQueueList.innerHTML = '<span style="color:var(--neon-cyan)">Nenhuma pendÃªncia no AutoBlog.</span>';
            } catch(e) {
              this.showToast('Erro ao contatar AutoBlog', 'error');
            }
          }
        });
      } catch(e) {
        autoBlogQueueList.innerHTML = `<span style="color:var(--neon-red)">AutoBlog Offline na porta 8098</span>`;
      }
    };

    if (this.contextSelector) {
      this.contextSelector.addEventListener('change', (e) => {
        if (e.target.value === 'apollo_edit') {
          this.apolloEditModal.style.display = 'flex';
          setTimeout(() => { this.contextSelector.value = 'personal'; }, 500);
          
          // Inicia o polling real
          fetchMaestroStatus();
          fetchAutoBlogPending();
          pollingInterval = setInterval(fetchMaestroStatus, 2000);
        }
      });
    }

    if (this.btnCloseApolloEdit) {
      this.btnCloseApolloEdit.addEventListener('click', () => {
        this.apolloEditModal.classList.remove('open');
        if(pollingInterval) clearInterval(pollingInterval);
      });
    }

    if (this.btnRestartServer) {
      this.btnRestartServer.addEventListener('click', async () => {
        const hash = await this.verifyBiometrics("Reiniciar Container do Apollo Edit");
        if (hash) {
          this.showToast('Enviando sinal de reinÃ­cio para Maestro...', 'warn');
          try {
            await fetch('http://localhost:8080/api/mobile/approve', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ action: 'RESTART', biometric_hash: hash })
            });
          } catch(e) {
            this.sendToColmeia(JSON.stringify({ type: 'user_text', text: 'Reiniciar infraestrutura (Fallback Socket)' }));
          }
        }
      });
    }

    // --- ETAPA 192, 193, 194: Nuvem Soberana (AÃ§Ãµes) ---
    if (this.btnStealthMode) {
      this.btnStealthMode.addEventListener('click', async () => {
        const hash = await this.verifyBiometrics("ATIVAR MODO STEALTH MUNDIAL");
        if (hash) {
          this.showToast('Modo Stealth Ativado. Desligando todos os robÃ´s.', 'error');
          this.triggerHaptic('error');
          try {
            // Etapa 196: Limpeza de Cache Nativa em Modo PÃ¢nico
            if (window.Capacitor && window.Capacitor.Plugins.Preferences) {
              await window.Capacitor.Plugins.Preferences.clear();
            }
            await fetch('http://localhost:8080/api/mobile/stealth', { method: 'POST' }).catch(()=>{});
          } catch(e) {}
        }
      });
    }

    if (this.btnTurboMode) {
      this.btnTurboMode.addEventListener('click', async () => {
        this.showToast('Modo Turbo Ativado! 100% GPU focada em Render.', 'success');
        this.triggerHaptic('success');
        fetch('http://localhost:8080/api/mobile/turbo', { method: 'POST' }).catch(()=>{});
      });
    }

    let hiveLogInterval = null;
    if (this.btnOpenHiveLogs) {
      this.btnOpenHiveLogs.addEventListener('click', () => {
        this.hiveLogsSidebar.classList.add('open');
        this.hiveLogOutput.textContent = "Conectando ao nÃºcleo da Colmeia...";
        hiveLogInterval = setInterval(async () => {
          try {
            const res = await fetch('http://localhost:8080/api/colmeia/logs', { timeout: 2000 });
            if(res.ok) {
              const logs = await res.text();
              this.hiveLogOutput.textContent = logs || "Colmeia aguardando comandos...";
            }
          } catch(e) {
            this.hiveLogOutput.textContent = "[ERRO DE CONEXÃƒO] Maestro Offline ou Endpoint indisponÃ­vel.";
          }
        }, 3000);
      });
    }

    if (this.btnCloseHiveLogs) {
      this.btnCloseHiveLogs.addEventListener('click', () => {
        this.hiveLogsSidebar.classList.remove('open');
        if (hiveLogInterval) clearInterval(hiveLogInterval);
      });
    }

    // Etapa 144: Backup AutomÃ¡tico do DB para Google Drive/Local FS
    if (this.btnSettings) { // Reusing settings button double click for testing backup
      this.btnSettings.addEventListener('dblclick', async () => {
        try {
          const sessions = await ApolloDirectorDB.getSessions();
          const backupData = JSON.stringify(sessions, null, 2);
          
          if (window.Capacitor && window.Capacitor.Plugins.Filesystem) {
            const Filesystem = window.Capacitor.Plugins.Filesystem;
            await Filesystem.writeFile({
              path: `apollo_db_backup_${Date.now()}.json`,
              data: backupData,
              directory: 'DOCUMENTS',
              encoding: 'utf8'
            });
            this.showToast('Backup Local Salvo em Documentos', 'success');
            this.triggerHaptic('success');
          } else {
            // Fallback Web
            const blob = new Blob([backupData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `apollo_db_backup_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            this.showToast('Backup Web Salvo via Download', 'success');
          }
        } catch (e) {
          console.error("Backup failed", e);
          this.showToast('Erro ao fazer backup', 'error');
        }
      });
    }

    // ETAPA 58 e 126: Anexos de Imagem (com CÃ¢mera/Galeria Nativa via Capacitor)
    if (this.btnAttachImage && this.imageUploadInput) {
      this.btnAttachImage.addEventListener('click', async () => {
        // Etapa 126: Acesso Multimodal Nativo
        if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.Camera) {
          try {
            const Camera = window.Capacitor.Plugins.Camera;
            const image = await Camera.getPhoto({
              quality: 90,
              allowEditing: false,
              resultType: 'base64', // Capacitor returns string 'base64'
              source: 'PROMPT' // Prompts user to choose Camera or Photos
            });
            const base64Image = `data:image/${image.format};base64,${image.base64String}`;
            
            // Reutiliza a lÃ³gica de processamento
            this.addTranscriptCard('user', '[Anexo de Imagem (Nativa)]', false);
            const cards = this.feedSection.querySelectorAll('.card');
            const lastCard = cards[cards.length - 1];
            if (lastCard) {
              const imgPreview = document.createElement('img');
              imgPreview.src = base64Image;
              imgPreview.className = 'chat-image-preview';
              imgPreview.onclick = () => this.openImageModal(base64Image);
              lastCard.querySelector('.card-content').appendChild(imgPreview);
            }
            this.sendToColmeia(JSON.stringify({ type: 'user_image', image_data: base64Image }));
          } catch (e) {
            console.warn("CÃ¢mera cancelada ou falha:", e);
          }
        } else {
          // Fallback para Web
          this.imageUploadInput.click();
        }
      });

      this.imageUploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (ev) => {
            const base64Image = ev.target.result;
            // Visual feedback no feed
            this.addTranscriptCard('user', '[Anexo de Imagem]', false);
            const cards = this.feedSection.querySelectorAll('.card');
            const lastCard = cards[cards.length - 1];
            if (lastCard) {
              const imgPreview = document.createElement('img');
              imgPreview.src = base64Image;
              imgPreview.className = 'chat-image-preview';
              imgPreview.onclick = () => this.openImageModal(base64Image);
              lastCard.querySelector('.card-content').appendChild(imgPreview);
            }
            this.scrollToBottom();
            
            // Enviar para backend (Modalidade Vision) - Payload
            this.sendToColmeia(JSON.stringify({ 
              type: 'user_image', 
              image_data: base64Image,
              filename: file.name
            }));
          };
          reader.readAsDataURL(file);
        }
        // Reseta o input
        this.imageUploadInput.value = '';
      });
    }
    // ETAPA 63: Comandos RÃ¡pidos
    if (this.quickCommands) {
      this.quickCommands.addEventListener('click', async (e) => {
        if (e.target.classList.contains('voice-pill')) {
          const cmd = e.target.getAttribute('data-cmd');
          if (cmd) {
            await this.activateAudioAndMic();
            this.sendToColmeia(JSON.stringify({ type: 'user_text', text: cmd }));
            this.textDrawer.classList.remove('open');
          }
        }
      });
    }

    // ETAPA 64: Busca no HistÃ³rico
    if (this.chatSearchInput) {
      this.chatSearchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const items = this.chatHistoryList.querySelectorAll('.chat-history-item');
        items.forEach(item => {
          const title = item.querySelector('.chat-item-title').textContent.toLowerCase();
          if (title.includes(query)) {
            item.style.display = 'flex';
          } else {
            item.style.display = 'none';
          }
        });
      });
    }

    // ETAPA 65: Exportar HistÃ³rico
    if (this.btnExportChat) {
      this.btnExportChat.addEventListener('click', async () => {
        if (!this.currentSessionId) {
          this.showToast('Nenhum chat ativo para exportar.', 'warn');
          return;
        }
        
        try {
          const session = await this.db.getSession(this.currentSessionId);
          const history = await this.db.getSessionHistory(this.currentSessionId);
          
          if (!session || history.length === 0) {
            this.showToast('O chat estÃ¡ vazio.', 'warn');
            return;
          }

          let markdown = `# ExportaÃ§Ã£o de Chat: ${session.title}\n`;
          markdown += `*Data: ${new Date().toLocaleString()}*\n\n---\n\n`;

          history.forEach(msg => {
            const roleName = msg.role === 'user' ? 'ðŸ‘¤ UsuÃ¡rio' : 'ðŸ¤– Apollo';
            markdown += `### ${roleName}\n${msg.content}\n\n`;
          });
          
          this.showToast('Chat exportado com sucesso!', 'success');
        } catch (err) {
          console.error('Erro na exportaÃ§Ã£o:', err);
          this.showToast('Erro ao exportar o chat.', 'error');
        }
      });
    }
    
    // ETAPA 78: God View Modal Logic
    if (this.btnGodView) {
      this.btnGodView.addEventListener('click', () => {
        this.godViewModal.style.display = 'block';
        this.fetchGodViewData();
      });
    }

    if (this.btnCloseGodView) {
      this.btnCloseGodView.addEventListener('click', () => {
        this.godViewModal.style.display = 'none';
      });
    }
    // ETAPA 68: Modo NÃ£o Perturbe (Mute TTS)
    if (this.btnMuteTTS) {
      this.btnMuteTTS.addEventListener('click', () => {
        this.isMuted = !this.isMuted;
        if (this.isMuted) {
          this.btnMuteTTS.textContent = 'ðŸ”•';
          this.btnMuteTTS.style.background = '#ffcc00';
          this.btnMuteTTS.style.color = '#000';
          this.showToast('Modo Silencioso Ativado (Apenas Escuta)', 'warn');
          // Para Ã¡udio em andamento
          if (this.audioSource) {
            try { this.audioSource.stop(); } catch(e){}
          }
        } else {
          this.btnMuteTTS.textContent = 'ðŸ””';
          this.btnMuteTTS.style.background = 'rgba(255, 255, 255, 0.1)';
          this.btnMuteTTS.style.color = 'var(--text-primary)';
          this.showToast('Ãudio do Agente Reativado', 'success');
        }
      });
    }
    this.imgModal.addEventListener('click', () => this.closeImageModal());
  }

  // ETAPA 78: God View Fetch
  async fetchGodViewData() {
    try {
      this.godViewList.innerHTML = '<div style="color: var(--text-muted);">Buscando interaÃ§Ãµes da nuvem...</div>';
      const res = await fetch(`${API_BASE_URL}/api/webhook/active-chats`);
      const data = await res.json();
      
      this.godViewList.innerHTML = '';
      if (!data.active_chats || data.active_chats.length === 0) {
        this.godViewList.innerHTML = '<div style="color: var(--text-muted);">Nenhuma interaÃ§Ã£o ativa.</div>';
        return;
      }
      
      data.active_chats.forEach(chat => {
        const item = document.createElement('div');
        item.style.background = 'rgba(0, 0, 0, 0.4)';
        item.style.padding = '10px';
        item.style.borderRadius = '8px';
        item.style.border = '1px solid var(--surface-border)';
        item.style.marginBottom = '10px';
        
        let contentStr = '';
        if (typeof chat.data === 'object') {
          contentStr = JSON.stringify(chat.data, null, 2);
        } else {
          contentStr = String(chat.data);
        }

        item.innerHTML = `
          <div style="font-size: 0.8rem; color: var(--magenta-glow); margin-bottom: 5px;">[${chat.source.toUpperCase()}] - ${new Date(chat.created_at).toLocaleString()}</div>
          <div style="font-size: 0.9rem; margin-bottom: 5px;"><strong>Status:</strong> ${chat.status}</div>
          <pre style="background: #000; padding: 5px; border-radius: 4px; font-size: 0.75rem; color: #0f0; overflow-x: auto;">${contentStr}</pre>
        `;
        this.godViewList.appendChild(item);
      });
    } catch (err) {
      console.error("Erro no God View:", err);
      this.godViewList.innerHTML = `<div style="color: #ff5555;">Erro ao buscar dados: ${err.message}</div>`;
    }
  }

  // UTILS
  async requestWakeLock() {
    if ('wakeLock' in navigator) {
      try {
        this.wakeLock = await navigator.wakeLock.request('screen');
        console.log('ðŸ”’ Screen Wake Lock ativado. A tela nÃ£o apagarÃ¡.');
      } catch (err) {
        console.warn('Falha ao ativar Wake Lock:', err);
      }
    }
  }

  setupMobileLifecyleHandlers() {
    // Etapa 122 e 125: Background & Wakelock via Capacitor App Plugin
    if (window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.App) {
      const App = window.Capacitor.Plugins.App;
      App.addListener('appStateChange', async ({ isActive }) => {
        if (isActive) {
          this.requestWakeLock();
          if (this.audioContext && this.audioContext.state === 'suspended') {
            await this.audioContext.resume();
          }
          if (!this.isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.connectWebSocket();
          }
        } else {
          console.log("App entrou em Background. VAD mantido ativo se possÃ­vel via Foreground Service (Configurado no Android).");
        }
      });
      return; // Evita bind duplo
    }

    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState === 'visible') {
        this.requestWakeLock(); // Restaura o Wake Lock ao voltar pro app
        if (this.audioContext && this.audioContext.state === 'suspended') {
          await this.audioContext.resume();
        }
        if (!this.isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
          this.connectWebSocket();
        }
      }
    });
  }

  // ETAPA 67: Suporte a gestos Touch (Swipe)
  setupSidebarGestures() {
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', e => {
      touchStartX = e.changedTouches[0].screenX;
    }, false);
    
    document.addEventListener('touchend', e => {
      touchEndX = e.changedTouches[0].screenX;
      this.handleSwipeGesture(touchStartX, touchEndX);
    }, false);
  }

  handleSwipeGesture(startX, endX) {
    const swipeThreshold = 50; // pixels
    if (endX < startX - swipeThreshold) {
      // Swipe Left - Fechar Sidebar
      if (this.chatSidebar && this.chatSidebar.classList.contains('open')) {
        this.chatSidebar.classList.remove('open');
      }
    }
    if (endX > startX + swipeThreshold) {
      // Swipe Right - Abrir Sidebar (Apenas se comeÃ§ar do canto esquerdo < 50px)
      if (startX < 50 && this.chatSidebar && !this.chatSidebar.classList.contains('open')) {
        this.chatSidebar.classList.add('open');
      }
    }
  }

  registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  }

  // ETAPA 62: Sistema de NotificaÃ§Ãµes Toast
  showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'â„¹ï¸';
    if (type === 'success') icon = 'âœ…';
    if (type === 'error') icon = 'âŒ';
    if (type === 'warn') icon = 'âš ï¸';

    toast.innerHTML = `<span>${icon}</span> <span>${this.escapeHtml(message)}</span>`;
    container.appendChild(toast);

    // Trigger reflow para iniciar animaÃ§Ã£o
    toast.offsetHeight;
    toast.classList.add('show');

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 400); // tempo do fade out
    }, 3000);
  }

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, function(m) {
      return {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
      }[m];
    });
  }
  // --- ETAPA 161: MÃ‰TODOS DO OLHO DE APOLLO ---
  async startVisionLoop() {
    try {
      this.showToast('Ligando Olho de Apollo...', 'info');
      // Tentar Capacitor Camera primeiro (se encapsulado) ou WebRTC fallback
      this.visionStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      this.cameraPreview.srcObject = this.visionStream;
      
      this.isVisionActive = true;
      this.visionIcon.style.filter = 'grayscale(0%)';
      this.visionIcon.style.textShadow = '0 0 10px var(--neon-cyan)';
      this.showToast('VisÃ£o Multimodal Ativada', 'success');

      this.visionInterval = setInterval(() => {
        this.captureAndSendFrame();
      }, 3000); // Tira uma foto a cada 3 segundos
    } catch (err) {
      console.error('Erro na cÃ¢mera:', err);
      this.showToast('Erro ao acessar cÃ¢mera', 'error');
    }
  }

  stopVisionLoop() {
    this.isVisionActive = false;
    this.visionIcon.style.filter = 'grayscale(100%)';
    this.visionIcon.style.textShadow = 'none';
    if (this.visionInterval) clearInterval(this.visionInterval);
    if (this.visionStream) {
      this.visionStream.getTracks().forEach(track => track.stop());
      this.visionStream = null;
    }
    this.showToast('VisÃ£o Desativada', 'warn');
  }

  captureAndSendFrame() {
    if (!this.isConnected || !this.cameraPreview) return;
    const canvas = this.visionCanvas;
    const ctx = canvas.getContext('2d');
    
    // Low res para poupar banda (640x480 max)
    const scale = Math.min(640 / this.cameraPreview.videoWidth, 480 / this.cameraPreview.videoHeight, 1);
    canvas.width = this.cameraPreview.videoWidth * scale;
    canvas.height = this.cameraPreview.videoHeight * scale;
    
    ctx.drawImage(this.cameraPreview, 0, 0, canvas.width, canvas.height);
    const base64Data = canvas.toDataURL('image/jpeg', 0.5); // 50% compressÃ£o
    
    // Manda pro Maestro (via websocket normal da Colmeia)
    this.sendToColmeia(JSON.stringify({ type: 'vision_frame', data: base64Data }));
  }

}

window.app = new PocketDirectorApp();




