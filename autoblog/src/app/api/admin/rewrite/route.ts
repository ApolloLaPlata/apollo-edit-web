import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const { content, instruction } = await req.json();

    if (!content) {
      return NextResponse.json({ error: 'Conteúdo vazio' }, { status: 400 });
    }

    const fs = require('fs');
    
    function getGeminiKey(): string {
      try {
        const keyPath = "E:\\MEUS PROGRAMAS\\FERRAMENTAS\\Api GEMINI APOLLO EDIT WEB.txt";
        if (fs.existsSync(keyPath)) {
          const keyContent = fs.readFileSync(keyPath, 'utf-8');
          return keyContent.trim().split('\n')[0].trim();
        }
      } catch (e) {
        console.warn("Não foi possível ler a chave Gemini em FERRAMENTAS");
      }
      return process.env.GEMINI_API_KEY || "";
    }

    const apiKey = getGeminiKey();
    if (!apiKey) {
      return NextResponse.json({ error: 'Chave de API não configurada' }, { status: 500 });
    }

    let prompt = "";
    if (instruction === 'improve') {
      prompt = "Aja como um Editor-Chefe premiado. Reescreva o seguinte artigo Markdown para melhorar a fluidez, corrigir erros gramaticais e aumentar a retenção do leitor, sem inventar fatos novos e mantendo o formato Markdown original:\n\n";
    } else if (instruction === 'expand') {
      prompt = "Aja como um Jornalista Sênior. Expanda o seguinte artigo Markdown adicionando mais detalhes lógicos, contexto relevante e exemplos explicativos, sem fugir do tema e mantendo o formato Markdown original:\n\n";
    } else if (instruction === 'summarize') {
      prompt = "Crie um resumo executivo muito denso e profissional (1 ou 2 parágrafos) do seguinte artigo Markdown:\n\n";
    } else {
      prompt = `Aja como um Editor Sênior. O usuário deu a seguinte ordem direta para modificar o artigo: "${instruction}".\nExecute essa ordem rigorosamente, mantendo a formatação Markdown original e sem adicionar comentários extras ao texto:\n\n`;
    }

    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    
    const payload = {
      contents: [{
        parts: [{ text: `${prompt}${content}` }]
      }],
      generationConfig: {
        temperature: 0.7,
      }
    };

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      return NextResponse.json({ error: 'Falha ao contatar a IA' }, { status: 500 });
    }

    const data = await response.json();
    const aiText = data.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!aiText) {
      return NextResponse.json({ error: 'IA não retornou conteúdo' }, { status: 500 });
    }

    return NextResponse.json({ success: true, result: aiText });
  } catch (error: any) {
    console.error("Erro no Rewrite AI:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
