// Gerencia o estado persistente do chat_ia usando localStorage
const CHAT_STATE_KEY = 'apollo_chat_state';

window.ChatStateManager = {
    saveState: function(chatHtml, dropZoneHtml, dropZoneClass, dropZoneBorder, actionTabVisible, budgetButtonText, budgetButtonEnabled, slotsDataState) {
        const state = {
            chatHtml: chatHtml,
            dropZoneHtml: dropZoneHtml,
            dropZoneClass: dropZoneClass,
            dropZoneBorder: dropZoneBorder,
            actionTabVisible: actionTabVisible,
            budgetButtonText: budgetButtonText,
            budgetButtonEnabled: budgetButtonEnabled,
            slotsData: slotsDataState
        };
        localStorage.setItem(CHAT_STATE_KEY, JSON.stringify(state));
    },
    
    loadState: function() {
        const data = localStorage.getItem(CHAT_STATE_KEY);
        if (data) {
            return JSON.parse(data);
        }
        return null;
    },
    
    clearState: function() {
        localStorage.removeItem(CHAT_STATE_KEY);
    }
};
