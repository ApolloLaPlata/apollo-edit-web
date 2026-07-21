// Gerenciador Central da Economia e Bagageiro (Conectado ao Backend F2P real)
window.ApolloEconomy = {
    _data: {
        resources: { coins: 0, crystals: 0, fuel: 0 },
        inventory: {}
    },

    sync: async function() {
        try {
            const response = await fetch('/api/store/inventory');
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    this._data.resources = data.resources;
                    this._data.inventory = data.inventory;
                    window.dispatchEvent(new Event('economyUpdated'));
                    return true;
                }
            }
        } catch (e) {
            console.error("Falha ao sincronizar com o Banco Central Apollo:", e);
        }
        return false;
    },

    getResources: function() {
        return this._data.resources;
    },

    getInventory: function() {
        return this._data.inventory;
    },

    buyItem: async function(itemId, cost, currencyType) {
        try {
            const response = await fetch('/api/store/buy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: itemId, cost: cost, currency: currencyType })
            });
            const data = await response.json();
            if (data.status === 'success') {
                await this.sync();
                alert('Compra aprovada pelo Banco Central! O item está no seu Bagageiro.');
                return true;
            } else {
                alert('Transação negada: ' + data.message);
                return false;
            }
        } catch (e) {
            alert('Erro de conexão com o servidor financeiro.');
            return false;
        }
    },

    hasCopilotTurbo: function() {
        return (this._data.inventory['copilot_turbo'] || 0) > 0;
    }
};

// Sincroniza logo ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    window.ApolloEconomy.sync();
});
