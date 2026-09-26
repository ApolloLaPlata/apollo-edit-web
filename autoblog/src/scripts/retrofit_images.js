const Database = require('better-sqlite3');
const path = require('path');

// Aponta para o banco do dev
const dbPath = path.resolve(process.cwd(), 'dev.db');
const db = new Database(dbPath);

console.log('--- INICIANDO RETROFIT DE IMAGENS PARA WEBP (AUTO-BLOG CMS) ---');

try {
  // Buscar todas as imagens de capa que não estejam em WEBP
  const posts = await db.prepare(`SELECT id, title, coverImage FROM Post WHERE coverImage IS NOT NULL AND coverImage NOT LIKE '%webp%'`).all();
  
  if (posts.length === 0) {
    console.log('✅ Tudo Limpo! Nenhuma imagem antiga encontrada. Todas as imagens já estão comprimidas ou em formatos modernos.');
  } else {
    console.log(`⚠️ Encontrados ${posts.length} artigos com capas não-otimizadas. Iniciando compressão/conversão de URL...`);
    let converted = 0;

    const updateStmt = db.prepare('UPDATE Post SET coverImage = ? WHERE id = ?');

    // Executa em transação para evitar corrupção
    const transaction = db.transaction(() => {
      for (const post of posts) {
        let newUrl = post.coverImage;
        
        // Se for Unsplash (API padrão usada pelo IA para buscar fotos)
        if (newUrl.includes('images.unsplash.com')) {
          // Remover qualquer formato anterior e forçar WEBP e qualidade 80
          newUrl = newUrl.replace(/&fm=[a-zA-Z0-9]+/, '');
          newUrl = newUrl.replace(/&q=[0-9]+/, '');
          newUrl += '&fm=webp&q=80';
          
          updateStmt.run(newUrl, post.id);
          converted++;
          console.log(`[CONVERTIDO] ${post.id.substring(0,8)}... -> URL otimizada para WebP`);
        }
        // Se for imagem direta estática de .jpg ou .png, nós deixamos o Next/Image converter no Front.
        // Ou implementaremos script de Sharp. Mas como o CMS usa Unsplash gerado pelo LLM:
        else {
           // Skip outras
        }
      }
    });

    transaction();
    console.log(`\\n🎉 RETROFIT CONCLUÍDO! Foram recodificadas ${converted} URLs de imagens para alta compressão (WebP). Isso salvará terabytes de tráfego do servidor no longo prazo.`);
  }
} catch (error) {
  console.error('❌ Erro Fatal no Retrofit:', error);
} finally {
  db.close();
}
