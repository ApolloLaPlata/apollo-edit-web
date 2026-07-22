/**
 * Apollo La Plata - Settings & API Key Rotation
 * Gerencia as configurações globais, constantes e o algoritmo de Rotação Inteligente de Chaves.
 */

// --- Constants (Migrated from constants.ts) ---
window.LAPLATA_MODELS = [
    { id: 'gemini-3.1-flash-image-preview', name: 'Gemini 3.1 Flash Image (Nano Banana 2 - Requer Acesso/Pago)' },
    { id: 'gemini-2.5-flash-image', name: 'Gemini 2.5 Flash Image (Gratuito & Rápido)' },
    { id: 'gemini-3.1-pro-image-preview', name: 'Gemini 3.1 Pro Image (Alta Qualidade - Pago)' },
];

window.LAPLATA_VISUAL_STYLES = [
    { id: 'none', label: 'Nenhum (Prompt Puro)' },
    { id: 'dark_fantasy', label: 'Fantasia Sombria (Estilo Elden Ring)' },
    { id: 'cinematic', label: 'Cinematográfico Realista (Filme)' },
    { id: 'anime', label: 'Anime / Mangá (Alta Fidelidade)' },
    { id: 'digital_art', label: 'Arte Digital (ArtStation)' },
    { id: 'oil_painting', label: 'Pintura a Óleo (Clássico)' },
    { id: 'cyberpunk', label: 'Cyberpunk / Neon' },
    { id: 'watercolor', label: 'Aquarela (Sketch)' },
    { id: 'pixar', label: 'Animação 3D (Estilo Pixar)' },
    { id: 'simpsons', label: 'Família Amarela (Cartoon)' },
    { id: 'retro_80s', label: 'Retro 80s Synthwave' },
    { id: 'horror', label: 'Horror Analógico / VHS' },
];

window.LAPLATA_OPENROUTER_MODELS = [
    { id: 'liquid/lfm-40b:free', name: 'Liquid LFM 40B MoE (Raciocínio - Grátis)', isFree: true },
    { id: 'deepseek/deepseek-r1:free', name: 'DeepSeek R1 (Raciocínio - Grátis)', isFree: true },
    { id: 'arcee-ai/trinity-large-preview:free', name: 'Arcee Trinity (Storytelling - Grátis)', isFree: true },
    { id: 'stepfun/step-3.5-flash', name: 'Step 3.5 Flash (Rápido - Grátis)', isFree: true },
    { id: 'google/gemini-2.0-flash-001', name: 'Gemini 2.0 Flash (OpenRouter - Baixo Custo)', isFree: false },
    { id: 'x-ai/grok-2-vision-1212', name: 'Grok 2 Vision (xAI - Pago)', isFree: false },
    { id: 'openai/gpt-4o', name: 'GPT-4o (OpenAI - Pago)', isFree: false },
    { id: 'anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet (Qualidade Max - Pago)', isFree: false },
];

window.LAPLATA_DEFAULT_SETTINGS = {
    aspectRatio: '16:9',
    modelId: 'gemini-2.5-flash-image',
    imageSize: '1K',
    useThinking: false,
    delayBetweenRequests: 2000,
    useStoryContinuity: false,
    globalContext: '',
    sceneContext: '',
    generateVideoPrompt: false,
    negativePrompt: '',
    useGrounding: false,
    textProvider: 'gemini',
    imageProvider: 'gemini',
    videoProvider: 'gemini',
    comfyUrl: 'http://127.0.0.1:8188',
    openRouterTextModel: 'arcee-ai/trinity-large-preview:free',
};

// --- Settings Management ---
window.laplataSettings = {
    get: () => {
        const stored = localStorage.getItem('laplata_settings');
        if (stored) {
            return { ...window.LAPLATA_DEFAULT_SETTINGS, ...JSON.parse(stored) };
        }
        return window.LAPLATA_DEFAULT_SETTINGS;
    },
    save: (newSettings) => {
        const current = window.laplataSettings.get();
        const updated = { ...current, ...newSettings };
        localStorage.setItem('laplata_settings', JSON.stringify(updated));
        return updated;
    }
};


// --- API Key Management & Intelligent Rotation ---
// Formato da chave: { key: string, name: string, isActive: boolean, isRateLimited: boolean, rateLimitedUntil: number, usageCount: number, usageLimit: number, errorCount: number, lastReset: number }

window.laplataApiKeys = {
    get: () => {
        const stored = localStorage.getItem('laplata_apikeys');
        let keys = stored ? JSON.parse(stored) : [];
        // Checar reset diário
        return window.laplataApiKeys._checkDailyReset(keys);
    },
    save: (keysArray) => {
        localStorage.setItem('laplata_apikeys', JSON.stringify(keysArray));
    },
    
    // --- Rotation Logic ---
    _checkDailyReset: (keys) => {
        const now = Date.now();
        const oneDay = 24 * 60 * 60 * 1000;
        let changed = false;

        const newKeys = keys.map(k => {
            const lastReset = k.lastReset || 0;
            if (now - lastReset > oneDay) {
                changed = true;
                return { ...k, usageCount: 0, lastReset: now, isRateLimited: false, rateLimitedUntil: 0, errorCount: 0 };
            }
            if (k.isRateLimited && k.rateLimitedUntil && now > k.rateLimitedUntil) {
                changed = true;
                return { ...k, isRateLimited: false, rateLimitedUntil: 0 };
            }
            return k;
        });

        if (changed) {
            localStorage.setItem('laplata_apikeys', JSON.stringify(newKeys));
        }
        return newKeys;
    },

    getBestKey: () => {
        const keys = window.laplataApiKeys.get();
        const now = Date.now();
        
        const availableKeys = keys.filter(k => {
            if (!k.isActive) return false;
            if (k.isRateLimited) {
                if (k.rateLimitedUntil && now > k.rateLimitedUntil) return true;
                return false;
            }
            if (k.usageLimit > 0 && k.usageCount >= k.usageLimit) return false;
            return true;
        });

        if (availableKeys.length === 0) {
            const expiredCooldown = keys.find(k => k.isActive && k.isRateLimited && k.rateLimitedUntil && now > k.rateLimitedUntil);
            if (expiredCooldown) return expiredCooldown;
            
            const hasRateLimitedKeys = keys.some(k => k.isActive && k.isRateLimited);
            if (hasRateLimitedKeys) {
                throw new Error("Todas as chaves da API estão no limite de uso (Rate Limit). Aguarde 1 minuto ou adicione mais chaves nas Configurações.");
            }
            return null;
        }

        const sortedKeys = [...availableKeys].sort((a, b) => {
            const limitA = a.usageLimit || 100;
            const limitB = b.usageLimit || 100;
            const usageA = (a.usageCount || 0) / limitA;
            const usageB = (b.usageCount || 0) / limitB;
            return usageA - usageB;
        });

        return sortedKeys[0];
    },

    registerUsage: (keyString) => {
        let keys = window.laplataApiKeys.get();
        keys = keys.map(k => {
            if (k.key === keyString) {
                return { ...k, usageCount: (k.usageCount || 0) + 1, isRateLimited: false, rateLimitedUntil: undefined, errorCount: 0 };
            }
            return k;
        });
        window.laplataApiKeys.save(keys);
    },

    registerFailure: (keyString, errorMessage) => {
        let keys = window.laplataApiKeys.get();
        keys = keys.map(k => {
            if (k.key === keyString) {
                let cooldownMs = 2 * 60 * 1000; // 2 min
                const errStr = (errorMessage || "").toLowerCase();
                if (errStr.includes('per day') && !errStr.includes('billing details')) {
                    cooldownMs = 12 * 60 * 60 * 1000; // 12 hours
                }
                return { ...k, isRateLimited: true, rateLimitedUntil: Date.now() + cooldownMs, errorCount: (k.errorCount || 0) + 1 };
            }
            return k;
        });
        window.laplataApiKeys.save(keys);
    },

    /**
     * Helper global para executar qualquer função async com rotação automática
     * Uso: window.laplataApiKeys.executeWithKeyRotation(async (apiKey) => { ... })
     */
    executeWithKeyRotation: async (action, maxRetries = 3) => {
        let attempts = 0;
        let lastError = null;

        while (attempts < maxRetries) {
            const bestKey = window.laplataApiKeys.getBestKey();
            if (!bestKey) {
                throw new Error("Nenhuma chave API Gemini ativa ou disponível.");
            }

            const apiKey = bestKey.key;

            try {
                const result = await action(apiKey);
                window.laplataApiKeys.registerUsage(apiKey);
                return result;
            } catch (error) {
                lastError = error;
                const errorMessage = error.message || String(error);
                const isSafetyBlock = errorMessage.includes('safety') || errorMessage.includes('blocked') || errorMessage.includes('policy');
                const isTextProviderError = errorMessage.includes('TextProviderError:');

                if (isTextProviderError || isSafetyBlock) {
                    throw error; // Não rotacionar por safety ou provider
                }

                console.warn(`Key ${apiKey.substring(0, 8)}... failed (${errorMessage}). Rotating...`);
                window.laplataApiKeys.registerFailure(apiKey, errorMessage);
                
                attempts++;
                if (attempts < maxRetries) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
        }

        throw new Error(`Todas as ${maxRetries} tentativas de rotação falharam. Último erro: ${lastError?.message || lastError}`);
    }
};
