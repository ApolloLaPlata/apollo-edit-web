const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const PORT = 5001;
const CMS_BACKEND_URL = 'http://127.0.0.1:3000/api/webhook/whatsapp';

// Inicializa o cliente com autenticação local (salva a sessão na pasta .wwebjs_auth)
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

let currentStatus = 'DISCONNECTED';
let currentQR = null;

// Gera e exibe o QR Code no terminal
client.on('qr', (qr) => {
    console.log('Escaneie o QR Code abaixo para conectar o robô do WhatsApp:');
    qrcode.generate(qr, { small: true });
    currentStatus = 'QR_READY';
    currentQR = qr;
});

// Cliente pronto
client.on('ready', () => {
    console.log('✅ WhatsApp Bridge is READY!');
    currentStatus = 'CONNECTED';
    currentQR = null;
});

client.on('disconnected', () => {
    currentStatus = 'DISCONNECTED';
    currentQR = null;
});

// Express route for status (para o CMS poder verificar se o WhatsApp tá logado)
app.get('/api/status', (req, res) => {
    res.json({ status: currentStatus, qr: currentQR });
});

// Histórico de mensagens enviadas pelo próprio robô (para não gerar loop)
const botSentMessages = [];

// Escutador de mensagens recebidas
client.on('message_create', async (msg) => {
    // Se foi enviada por nós mesmos via API, ignora para não ter loop
    if (msg.fromMe) {
        const sentIndex = botSentMessages.indexOf(msg.body);
        if (sentIndex !== -1) {
            botSentMessages.splice(sentIndex, 1);
            return;
        }
    }

    // Aceita apenas texto por enquanto
    if (msg.body) {
        console.log(`[WhatsApp In] de ${msg.from}: ${msg.body}`);
        
        try {
            // Repassa para o Next.js (CMS_BACKEND_URL)
            await axios.post(CMS_BACKEND_URL, {
                from: msg.from,
                to: msg.to,
                body: msg.body,
                timestamp: msg.timestamp,
                sender_name: msg._data.notifyName || 'Unknown',
                fromMe: msg.fromMe
            }, {
                headers: {
                    'Authorization': 'Bearer apollo-master-key' // Mesma chave usada no Next.js
                }
            });
        } catch (error) {
            if (error.code !== 'ECONNREFUSED') {
                console.error('❌ Erro ao enviar para o CMS Backend:', error.message);
            }
        }
    }
});

// Endpoint para o CMS mandar mensagem de volta para alguém (via porta 5001)
app.post('/api/send', async (req, res) => {
    const { to, message } = req.body;
    
    if (!to || !message) {
        return res.status(400).json({ error: 'Faltando campo "to" ou "message"' });
    }

    try {
        botSentMessages.push(message); 
        if (botSentMessages.length > 50) botSentMessages.shift(); // Evita vazamento de memória
        
        await client.sendMessage(to, message);
        console.log(`[WhatsApp Out] para ${to}: ${message.substring(0, 50)}...`);
        res.json({ success: true });
    } catch (error) {
        console.error('❌ Erro enviando mensagem via WhatsApp:', error.message);
        res.status(500).json({ success: false, error: error.message });
    }
});

client.initialize();

app.listen(PORT, () => {
    console.log(`✅ WhatsApp Bridge HTTP Server rodando na porta ${PORT}`);
});
