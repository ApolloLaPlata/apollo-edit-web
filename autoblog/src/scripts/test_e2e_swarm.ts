import { generateArticle } from './src/lib/llm/lightning-client';
async function runTest() {
  console.log('Iniciando Teste E2E...');
  try {
    const result = await generateArticle('A evolução da IA em 2026', 'tech_blog', 'news');
    console.log('SUCESSO!', result.title);
  } catch(e) { console.error('ERRO:', e); }
}
runTest();
