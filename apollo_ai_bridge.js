// apollo_ai_bridge.js
// Script Injetado nos IFrames (Projetos Open Source) para comunicar com o Apollo OS principal

window.ApolloBridge = {
    exportToBagageiro: function(blobOrArrayBuffer, filename, mimeType) {
        window.parent.postMessage({
            action: 'export_to_bagageiro',
            content: blobOrArrayBuffer,
            filename: filename,
            mimeType: mimeType
        }, '*');
    },

    // Injeta um botão flutuante da IA no Iframe atual
    injectAIFloatingButton: function(onClickCallback) {
        const btn = document.createElement('button');
        btn.innerHTML = '✨';
        btn.title = "Acionar Inteligência Artificial (Apollo)";
        btn.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999999;
            background: linear-gradient(45deg, #8b5cf6, #d946ef);
            color: white;
            border: 2px solid #fff;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 0 20px rgba(217, 70, 239, 0.6);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        btn.onmouseover = () => {
            btn.style.transform = 'scale(1.1)';
            btn.style.boxShadow = '0 0 30px rgba(217, 70, 239, 0.9)';
        };
        btn.onmouseout = () => {
            btn.style.transform = 'scale(1)';
            btn.style.boxShadow = '0 0 20px rgba(217, 70, 239, 0.6)';
        };

        btn.onclick = () => {
            if (onClickCallback) onClickCallback();
            else console.log("IA Local Acionada.");
        };

        document.body.appendChild(btn);
    }
};

console.log("🚀 Apollo AI Bridge Carregado na Engine Externa.");
