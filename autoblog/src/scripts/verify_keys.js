const fs = require('fs');

async function testLightning() {
  console.log("Iniciando varredura das chaves da Lightning AI...\n");
  
  for (let i = 1; i <= 4; i++) {
    const fileName = `E:\\MEUS PROGRAMAS\\FERRAMENTAS\\API Lighting IA Conta ${i}.txt`;
    let key = "";
    if (fs.existsSync(fileName)) {
      const content = fs.readFileSync(fileName, 'utf-8');
      const skMatch = content.match(/(sk-[a-zA-Z0-9\-_]+)/);
      if (skMatch) {
         key = skMatch[1];
      } else {
         const lines = content.split('\n').map(l => l.trim()).filter(l => l.length > 10 && !l.startsWith('===') && !l.includes('CHAVE'));
         if (lines.length > 0) key = lines[lines.length - 1];
      }
    }
    
    if (!key) {
       console.log(`[Conta ${i}] Nenhuma chave extraída.`);
       continue;
    }
    
    console.log(`\n[Conta ${i}] Chave lida (tamanho: ${key.length}). Testando autenticação...`);
    
    try {
      // Teste de modelos (Para descobrir o Model ID correto)
      if (i === 1) {
        const modelsRes = await fetch("https://lightning.ai/api/v1/models", {
          headers: { "Authorization": `Bearer ${key}` }
        });
        
        if (modelsRes.ok) {
           const modelsData = await modelsRes.json();
           console.log(`[Conta ${i}] Modelos disponíveis obtidos com SUCESSO! Salvando em models_dump.json...`);
           fs.writeFileSync("E:\\MEUS PROGRAMAS\\AUTO_BLOG_CMS\\frontend\\models_dump.json", JSON.stringify(modelsData.data.map(m => m.id), null, 2));
           console.log("Arquivo salvo com a lista completa.");
        } else {
           console.log(`[Conta ${i}] Erro ao listar modelos: ${modelsRes.status} ${modelsRes.statusText}`);
        }
      }

      // Teste de chat completions real
      const reqBody = {
        model: "openai/gpt-5", // Testando o gpt-5 como recomendado pelo maestro
        messages: [{ role: "user", content: "Diga apenas a palavra SUCESSO e mais nada." }],
        max_completion_tokens: 10,
        temperature: 1.0
      };
      
      const chatRes = await fetch("https://lightning.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${key}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(reqBody)
      });
      
      if (chatRes.ok) {
         const json = await chatRes.json();
         console.log(`✅ [Conta ${i}] FUNCIONANDO 100%! Resposta da IA: ${json.choices[0].message.content}`);
      } else {
         const errorText = await chatRes.text();
         console.log(`❌ [Conta ${i}] FALHOU no Chat (Status ${chatRes.status}): ${errorText}`);
      }
      
    } catch (e) {
      console.error(`[Conta ${i}] Erro de requisição:`, e.message);
    }
  }
}

testLightning();
