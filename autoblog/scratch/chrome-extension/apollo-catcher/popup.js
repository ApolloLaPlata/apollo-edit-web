document.addEventListener('DOMContentLoaded', () => {
  const domainInput = document.getElementById('domain');
  const personaSelect = document.getElementById('persona');
  const apiKeyInput = document.getElementById('apiKey');
  const captureBtn = document.getElementById('captureBtn');
  const statusDiv = document.getElementById('status');

  // Carregar dados salvos
  chrome.storage.local.get(['domain', 'persona', 'apiKey'], (result) => {
    if (result.domain) domainInput.value = result.domain;
    if (result.persona) personaSelect.value = result.persona;
    if (result.apiKey) apiKeyInput.value = result.apiKey;
  });

  // Salvar mudanças
  domainInput.addEventListener('change', () => chrome.storage.local.set({ domain: domainInput.value }));
  personaSelect.addEventListener('change', () => chrome.storage.local.set({ persona: personaSelect.value }));
  apiKeyInput.addEventListener('change', () => chrome.storage.local.set({ apiKey: apiKeyInput.value }));

  function setStatus(msg, type) {
    statusDiv.textContent = msg;
    statusDiv.className = type;
    setTimeout(() => {
      statusDiv.textContent = '';
      statusDiv.className = '';
    }, 4000);
  }

  captureBtn.addEventListener('click', async () => {
    captureBtn.disabled = true;
    captureBtn.textContent = 'Extraindo...';

    const domain = domainInput.value.trim();
    const persona = personaSelect.value;
    const apiKey = apiKeyInput.value.trim();

    if (!domain || !apiKey) {
      setStatus('Preencha Domínio e API Key.', 'error');
      captureBtn.disabled = false;
      captureBtn.textContent = 'Capturar e Enviar';
      return;
    }

    try {
      // Injeta script na aba atual para extrair conteúdo
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });

      const extractedData = result[0].result;

      if (!extractedData || !extractedData.content) {
         setStatus('Nenhum artigo encontrado.', 'error');
         captureBtn.disabled = false;
         captureBtn.textContent = 'Capturar e Enviar';
         return;
      }

      captureBtn.textContent = 'Transmitindo...';

      // Envia para o Background Script fazer o POST (evita bloqueios CORS em alguns cenários)
      chrome.runtime.sendMessage(
        {
          action: 'sendToApollo',
          payload: {
            domain,
            apiKey,
            persona,
            sourceUrl: tab.url,
            title: extractedData.title,
            content: extractedData.content,
            images: extractedData.images
          }
        },
        (response) => {
          if (response && response.success) {
            setStatus('Artigo enviado p/ Apollo!', 'success');
          } else {
            setStatus('Erro: ' + (response ? response.error : 'Falha de rede'), 'error');
          }
          captureBtn.disabled = false;
          captureBtn.textContent = 'Capturar e Enviar';
        }
      );

    } catch (error) {
      console.error(error);
      setStatus('Erro de Execução.', 'error');
      captureBtn.disabled = false;
      captureBtn.textContent = 'Capturar e Enviar';
    }
  });
});
