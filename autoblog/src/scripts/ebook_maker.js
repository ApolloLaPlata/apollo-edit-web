const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

const DB_PATH = path.resolve(process.cwd(), 'dev.db');
const EXPORT_DIR = path.resolve(process.cwd(), 'public/exports');

// Garante que o diretório exista
if (!fs.existsSync(EXPORT_DIR)) {
  fs.mkdirSync(EXPORT_DIR, { recursive: true });
}

function generateEbook() {
  console.log('[EBOOK-MAKER] 📚 Iniciando Máquina de E-books (Amazon KDP Ready)...');
  
  const db = new Database(DB_PATH);
  
  // Pega os 50 posts mais acessados
  const topPosts = await db.prepare(`
    SELECT title, author, contentMd, publishedAt 
    FROM Post 
    WHERE isPublished = 1 AND isDeleted = 0
    ORDER BY views DESC 
    LIMIT 50
  `).all();

  if (topPosts.length === 0) {
    console.log('[EBOOK-MAKER] 💤 Sem posts suficientes para um e-book.');
    return;
  }

  let markdownBook = `# As Maiores Histórias e Polêmicas\n\n`;
  markdownBook += `*Compilado automaticamente pela Redação de Inteligência Artificial*\n\n`;
  markdownBook += `---\n\n`;

  // Índice (Table of Contents)
  markdownBook += `## Índice\n\n`;
  topPosts.forEach((post, index) => {
    markdownBook += `${index + 1}. [${post.title}](#capitulo-${index + 1})\n`;
  });
  markdownBook += `\n---\n\n`;

  // Conteúdo dos Capítulos
  topPosts.forEach((post, index) => {
    // Limpeza de marcações internas
    let cleanContent = post.contentMd
       .replace(/\[TLDR\]([\s\S]*?)\[\/TLDR\]/gi, '')
       .replace(/\[SENSITIVE\]/gi, '')
       .replace(/\[PAYWALL\]/gi, '');

    markdownBook += `<a id="capitulo-${index + 1}"></a>\n`;
    markdownBook += `# Capítulo ${index + 1}: ${post.title}\n\n`;
    markdownBook += `**Por ${post.author || 'Redação'}**\n\n`;
    markdownBook += `${cleanContent}\n\n`;
    markdownBook += `<div style="page-break-after: always;"></div>\n\n`;
  });

  const fileName = `Ebook_Compilado_${Date.now()}.md`;
  const filePath = path.join(EXPORT_DIR, fileName);

  fs.writeFileSync(filePath, markdownBook);
  console.log(`[EBOOK-MAKER] ✅ E-book (Markdown puro) gerado com sucesso!`);
  console.log(`[EBOOK-MAKER] 📁 Salvo em: ${filePath}`);
  console.log(`[EBOOK-MAKER] 💡 Dica: Você pode usar ferramentas como Pandoc ou Calibre para converter este arquivo para PDF ou MOBI para vender na Amazon!`);
}

// Execução Avulsa
if (require.main === module) {
  generateEbook();
}

module.exports = { generateEbook };
