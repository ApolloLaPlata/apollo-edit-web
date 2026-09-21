const fetch = require('node-fetch');

async function testSocialAPI() {
  console.log("1. Buscando configurações (GET)...");
  const res = await fetch('http://localhost:3000/api/admin/social');
  const data = await res.json();
  
  if (!data.success || !data.data) {
     console.log("GET falhou. Mockando objeto...", data);
     return;
  }
  
  console.log("GET OK! Dados atuais:", data.data.telegramBotToken);

  console.log("2. Atualizando chaves (PUT)...");
  const updateRes = await fetch('http://localhost:3000/api/admin/social', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      id: data.data.id,
      telegramBotToken: "TESTE_TOKEN_UPDATE_" + Date.now(),
      telegramChatId: "-100TESTE",
      discordWebhookUrl: "https://discord.com/api/test",
      whatsappApiUrl: null,
      whatsappGroupId: null
    })
  });
  
  const updateData = await updateRes.json();
  console.log("PUT Result:", updateData);

  console.log("3. Verificando DB via GET novamente...");
  const verifyRes = await fetch('http://localhost:3000/api/admin/social');
  const verifyData = await verifyRes.json();
  console.log("GET Novo Token:", verifyData.data.telegramBotToken);
}

testSocialAPI();
