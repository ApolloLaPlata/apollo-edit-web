import os

filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias_core.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# Patch 1: saveSettings
t1 = """    localStorage.setItem('api_key_kwai', document.getElementById('api_key_kwai').value);
    
    const statusDiv = document.getElementById('settings-save-status');"""
r1 = """    localStorage.setItem('api_key_kwai', document.getElementById('api_key_kwai').value);
    
    // Webhooks
    const webhookDeepdive = document.getElementById('webhook_url_deepdive');
    if (webhookDeepdive) localStorage.setItem('webhook_url_deepdive', webhookDeepdive.value);
    
    const statusDiv = document.getElementById('settings-save-status');"""
content = content.replace(t1, r1)

# Patch 2: testWebhook
t2 = """        const data = await response.json();
        showToast(data.message || 'API funcionando corretamente!');
    } catch (err) {
        showToast('Erro ao testar API: ' + err.message);
    }
}

// ---------------------------------------------------"""
r2 = """        const data = await response.json();
        showToast(data.message || 'API funcionando corretamente!');
    } catch (err) {
        showToast('Erro ao testar API: ' + err.message);
    }
}

async function testWebhook(type) {
    if (type === 'deepdive') {
        const url = document.getElementById('webhook_url_deepdive').value.trim();
        if (!url) {
            showToast('Preencha a URL do Webhook primeiro!');
            return;
        }
        
        try {
            const payload = {
                title: "Teste de Webhook",
                summary: "Este é um disparo de teste da Central de Notícias.",
                url: "https://exemplo.com",
                deepdive_text: "Texto de aprofundamento simulado...",
                timestamp: new Date().toISOString()
            };
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                showToast('Webhook disparado com sucesso!');
            } else {
                showToast('Falha no Webhook: HTTP ' + response.status);
            }
        } catch (err) {
            showToast('Erro ao disparar Webhook: ' + err.message);
        }
    }
}

// ---------------------------------------------------"""
content = content.replace(t2, r2)

# Patch 3: loadSettings
t3 = """        'api_key_twitter', 'api_key_youtube', 'api_key_instagram',
        'api_key_facebook', 'api_key_tiktok', 'api_key_kwai'
    ];"""
r3 = """        'api_key_twitter', 'api_key_youtube', 'api_key_instagram',
        'api_key_facebook', 'api_key_tiktok', 'api_key_kwai',
        'webhook_url_deepdive'
    ];"""
content = content.replace(t3, r3)

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)
print("Settings patched in noticias_core.js!")
