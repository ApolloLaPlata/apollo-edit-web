chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sendToApollo') {
    const { domain, apiKey, persona, sourceUrl, title, content, images } = request.payload;

    // Constrói a URL da API
    let baseUrl = domain;
    if (!baseUrl.startsWith('http')) {
      // Assume http para localhost, https para o resto
      baseUrl = baseUrl.includes('localhost') ? `http://${baseUrl}` : `https://${baseUrl}`;
    }
    
    const endpoint = `${baseUrl}/api/apollo/ingest`;

    fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-apollo-key': apiKey
      },
      body: JSON.stringify({
        sourceUrl,
        title,
        content,
        persona,
        images
      })
    })
    .then(async (res) => {
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Status ${res.status}: ${errText}`);
      }
      return res.json();
    })
    .then(data => {
      sendResponse({ success: true, data });
    })
    .catch(error => {
      console.error('Apollo Catcher Background Error:', error);
      sendResponse({ success: false, error: error.message });
    });

    return true; // Mantém o canal aberto para a resposta assíncrona
  }
});
