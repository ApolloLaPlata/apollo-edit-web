/**
 * APOLLO OS - Economy & Gamification Engine
 * Gerencia Gasolina, Apollo Coins, Cristais, Nível do Piloto e Quests.
 */

class ApolloEconomyStore {
    constructor() {
        this.defaultState = {
            gasolina: 100,     // Combustível para render/exportação
            maxGasolina: 100,
            apolloCoins: 0,    // Soft currency
            cristais: 0,       // Hard currency (API)
            chipsLLM: 0,       // Moeda para requisições avançadas de texto/LLM
            placasGPU: 0,      // Moeda para renderização massiva/especial de imagem
            xp: 0,             // Experiência de produção
            level: 1,          // Nível do Piloto
            
            // Quests
            quests: {
                daily_export: { id: 'daily_export', title: 'Diretor Focado', desc: 'Exporte 1 Vídeo', target: 1, current: 0, rewardType: 'apolloCoins', rewardAmount: 50, completed: false },
                daily_audio: { id: 'daily_audio', title: 'Engenheiro de Som', desc: 'Gere 3 Áudios', target: 3, current: 0, rewardType: 'xp', rewardAmount: 100, completed: false },
            }
        };

        this.state = this.loadState();
        this.listeners = [];
        
        // Expor para o Window para acesso global (pelos iframes também)
        window.ApolloEconomy = this;

        // Escuta eventos de missão vindos do sistema
        window.addEventListener('apollo_mission_progress', (e) => {
            const { action, kms } = e.detail;
            if (action === 'export_video') {
                this.progressQuest('daily_export', 1);
            } else if (action === 'generate_audio') {
                this.progressQuest('daily_audio', 1);
            }
        });
    }

    loadState() {
        const saved = localStorage.getItem('apollo_economy_state');
        if (saved) {
            try {
                return { ...this.defaultState, ...JSON.parse(saved) };
            } catch (e) {
                console.error("Erro ao ler economia salva", e);
            }
        }
        return JSON.parse(JSON.stringify(this.defaultState));
    }

    saveState() {
        localStorage.setItem('apollo_economy_state', JSON.stringify(this.state));
        this.notifyListeners();
    }

    subscribe(callback) {
        this.listeners.push(callback);
        callback(this.state); // Chamada inicial
        return () => {
            this.listeners = this.listeners.filter(cb => cb !== callback);
        };
    }

    notifyListeners() {
        const stateCopy = JSON.parse(JSON.stringify(this.state));
        this.listeners.forEach(cb => cb(stateCopy));
        
        // Emite evento global para que a HUD intercepte
        const event = new CustomEvent('apollo_economy_updated', { detail: stateCopy });
        window.dispatchEvent(event);
    }

    // --- AÇÕES PRINCIPAIS ---

    addXP(amount) {
        this.state.xp += amount;
        
        // Fórmula de Level: Level = piso(raiz_quadrada(XP / 100)) + 1
        const novoLevel = Math.floor(Math.sqrt(this.state.xp / 100)) + 1;
        
        if (novoLevel > this.state.level) {
            this.state.level = novoLevel;
            this.triggerLevelUpEvent(novoLevel);
        }
        this.saveState();
    }

    addCurrency(type, amount) {
        if (typeof this.state[type] !== 'undefined') {
            this.state[type] += amount;
            if (type === 'gasolina' && this.state.gasolina > this.state.maxGasolina) {
                this.state.gasolina = this.state.maxGasolina;
            }
            this.saveState();
        }
    }

    consumeGasolina(amount) {
        if (this.state.gasolina >= amount) {
            this.state.gasolina -= amount;
            this.saveState();
            return true; // Sucesso
        }
        return false; // Sem gasolina
    }

    // --- SISTEMA DE QUESTS ---

    progressQuest(questId, amount = 1) {
        const quest = this.state.quests[questId];
        if (!quest || quest.completed) return;

        quest.current += amount;
        
        if (quest.current >= quest.target) {
            quest.current = quest.target;
            this.completeQuest(questId);
        } else {
            this.saveState();
        }
    }

    completeQuest(questId) {
        const quest = this.state.quests[questId];
        if (quest && !quest.completed) {
            quest.completed = true;
            // Dar recompensa
            if (quest.rewardType === 'xp') {
                this.addXP(quest.rewardAmount);
            } else {
                this.addCurrency(quest.rewardType, quest.rewardAmount);
            }
            
            // Notificar UI global de quest completa
            const event = new CustomEvent('apollo_quest_completed', { detail: quest });
            window.dispatchEvent(event);
            
            this.saveState();
        }
    }

    // --- EVENTOS VISUAIS ---
    triggerLevelUpEvent(newLevel) {
        const event = new CustomEvent('apollo_level_up', { detail: { level: newLevel } });
        window.dispatchEvent(event);
    }
}

// Inicializa globalmente
if (!window.ApolloEconomy) {
    new ApolloEconomyStore();
}
