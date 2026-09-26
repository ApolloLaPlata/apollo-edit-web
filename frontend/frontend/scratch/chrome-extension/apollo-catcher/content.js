// Auto-executado pelo chrome.scripting.executeScript
(() => {
  // Tenta encontrar o título
  const title = document.querySelector('h1')?.innerText || document.title;
  
  // Tenta encontrar o corpo principal (melhor esforço)
  let content = '';
  
  // Tenta achar tag article
  const articleNode = document.querySelector('article');
  if (articleNode) {
    // Pega todos os parágrafos dentro de article
    const paragraphs = Array.from(articleNode.querySelectorAll('p')).map(p => p.innerText);
    content = paragraphs.join('\n\n');
  } else {
    // Fallback: Pega todos os parágrafos da página que tenham algum tamanho razoável
    const paragraphs = Array.from(document.querySelectorAll('p'))
      .map(p => p.innerText)
      .filter(text => text.length > 50);
    content = paragraphs.join('\n\n');
  }

  // Tenta pegar algumas imagens (capa)
  const images = Array.from(document.querySelectorAll('img'))
    .map(img => img.src)
    .filter(src => src.startsWith('http') && !src.includes('logo') && !src.includes('icon'))
    .slice(0, 3); // top 3

  return {
    title: title.trim(),
    content: content.trim(),
    images: images
  };
})();
