import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { messages, articleContext } = await req.json();

    if (!messages || !articleContext) {
      return NextResponse.json({ error: 'Faltam parâmetros obrigatórios' }, { status: 400 });
    }

    const fs = require('fs');
    
    // Função para pegar a chave API (mesma usada no gemini-tts)
    function getGeminiKey(): string {
      try {
        const keyPath = "E:\\MEUS PROGRAMAS\\FERRAMENTAS\\Api GEMINI APOLLO EDIT WEB.txt";
        if (fs.existsSync(keyPath)) {
          const content = fs.readFileSync(keyPath, 'utf-8');
          return content.trim().split('\n')[0].trim();
        }
      } catch (e) {
        console.warn("Aviso: Não foi possível ler a chave Gemini em FERRAMENTAS");
      }
      return process.env.GEMINI_API_KEY || "";
    }

    const apiKey = getGeminiKey();
    if (!apiKey) {
      return NextResponse.json({ error: 'Chave de API não configurada' }, { status: 500 });
    }

    // Pega a última mensagem do usuário
    const userMessage = messages[messages.length - 1].content;
    const history = messages.slice(0, -1).map((m: any) => `${m.role === 'user' ? 'Usuário' : 'IA'}: ${m.content}`).join('\n');

    // Prompt do RAG (Retrieve and Generate) restrito
    const systemPrompt = `Você é um Assistente de Leitura AI inteligente acoplado a um artigo de blog.
Sua missão é responder às dúvidas do usuário baseando-se EXCLUSIVAMENTE no texto do artigo fornecido abaixo.
Se a resposta não estiver no artigo, diga educadamente que o texto não menciona essa informação.
Seja conciso, moderno e cordial.

ARTIGO:
${articleContext.substring(0, 8000)} // Limite seguro de contexto
`;

    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    
    const payload = {
      contents: [{
        parts: [{ text: `${systemPrompt}\n\nHistórico:\n${history}\n\nPergunta Atual: ${userMessage}` }]
      }]
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Gemini Error:", errorText);
      return NextResponse.json({ error: 'Falha ao contatar a IA' }, { status: 500 });
    }

    const data = await response.json();
    const aiText = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Desculpe, não consegui processar a resposta.';

    return NextResponse.json({ success: true, reply: aiText });
  } catch (error: any) {
    console.error("Erro na rota de Chat:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
