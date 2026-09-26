const { generateArticle } = require('./src/lib/llm/lightning-client.ts');
// TypeScript script to test the LLM
const tsNode = require('ts-node');
tsNode.register({ transpileOnly: true });

async function runTest() {
  console.log('🤖 INICIANDO TESTE AUTÔNOMO DE GERAÇÃO DA COLMEIA...');
  try {
    const { generateArticle } = require('./src/lib/llm/lightning-client.ts');
    
    // Tema aleatório atual para validar pesquisa online e redação analítica
    const topic = "O impacto da Inteligência Artificial Autônoma na criação de conteúdo em 2026";
    
    console.log(`📌 Tema Pautado: "${topic}"`);
    console.log('⏳ Acionando os Agentes (Pesquisador, Redator, Editor)...');
    
    const startTime = Date.now();
    
    const article = await generateArticle(topic, "Apollo Edit Web CMS", "[\"article\"]");
    
    const endTime = Date.now();
    
    console.log('\n======================================================');
    console.log('🏆 ARTIGO CONCLUÍDO COM SUCESSO');
    console.log('======================================================');
    console.log(`⏱️ Tempo levado: ${((endTime - startTime) / 1000).toFixed(2)}s`);
    console.log(`🏷️ Título Clickbait: ${article.title}`);
    console.log(`🖼️ Prompt de Imagem Gerado (Inglês): ${article.imagePrompt}`);
    console.log(`🔍 Busca Real Solicitada (Pexels): ${article.searchQuery || 'Nenhuma'}`);
    console.log(`📷 URL da Imagem Real Encontrada: ${article.realImageUrl || 'Nenhuma/Falha na Chave Pexels'}`);
    console.log(`📝 Trecho do Corpo (Markdown):\n\n${article.contentMd.substring(0, 500)}...`);
    console.log('\n✅ FIM DO PROCESSO.');
  } catch (err) {
    console.error('❌ ERRO NO TESTE AUTÔNOMO:', err);
  }
}

runTest();
