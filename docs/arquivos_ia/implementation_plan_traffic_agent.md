# Agentes de Publicidade: Gestor de Tráfego & Diretor de Criação 📊🎨

Sua visão é criar um ecossistema completo de agência de publicidade operando de forma autônoma dentro da Apollo. Você quer maximizar o ROI, criar imagens de alta conversão, e monetizar cada pixel da tela dos usuários através de um rodízio inteligente.

## User Review Required
> [!IMPORTANT]
> **API de Geração de Imagem:** Para o Agente criar banners usando imagens reais (DALL-E 3 ou Midjourney/Stable Diffusion), precisaremos fazer chamadas para uma API geradora de imagens, o que consome créditos na faixa de $0.02 a $0.04 por imagem gerada. Você concorda em plugar uma API como a da OpenAI (DALL-E 3) ou fal.ai (Stable Diffusion) para a geração de peças reais pelo Diretor de Criação?

> [!IMPORTANT]
> **Regra do Rodízio:** O sistema carregará todas as campanhas ativas e trocará a imagem a cada **30 segundos**. Cada vez que o banner aparecer na tela por 30s, o sistema contará como **1 View (Impressão)**, mesmo sem o usuário recarregar a página. Isso te dará as métricas exatas de CTR (Taxa de Clique). Concorda?

## Proposed Changes

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py`
#### [MODIFY] `servidor_web.py`
- Adicionar endpoints de Telemetria de Anúncios:
  - `POST /api/public/campaigns/{id}/view`: Incrementa o contador de `views` no banco de dados (+1).
  - `POST /api/public/campaigns/{id}/click`: Incrementa o contador de `clicks` no banco de dados (+1).

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\noticias_scripts.html`
#### [MODIFY] `noticias_scripts.html`
- Aprimorar o script injetado hoje. Em vez de mostrar apenas o 1º banner estático, ele vai guardar todas as campanhas ativas em memória.
- Iniciar um loop (setInterval de 30s) que faz fade-out do banner atual, fade-in do próximo e dispara o endpoint de `/view` para o banner exibido, cobrando o anunciante ou contabilizando nossa métrica interna.

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\traffic_manager_agent.py`
#### [NEW] `traffic_manager_agent.py`
- O "Gestor de Tráfego" da IA.
- Ele calculará o **CTR (Click-Through Rate = Clicks / Views)** de todas as campanhas ativas.
- Se um banner rodou 10.000 vezes e teve menos de 10 cliques (CTR baixo), ele **pausa** a campanha automaticamente (is_active = 0) para não desperdiçar espaço nobilíssimo da tela, e aciona o *Marketing Agent* para gerar uma arte nova.
- Ele gerará o Relatório de ROI.

### Melhoria no Agente Existente
#### [MODIFY] `marketing_agent.py` (Diretor de Criação)
- Adicionar a capacidade de gerar **Prompts de Imagem** complexos.
- Preparar a função `generate_ad_image()` que fará a chamada de rede para a API de imagem selecionada, salvará o arquivo gerado (ou link) e usará como capa do banner.

## Verification Plan

### Testes Manuais
- Abrir a interface de usuário e deixar a tela parada por 2 minutos para confirmar se o banner alterna sozinho a cada 30s.
- Clicar no banner e verificar se o contador de `clicks` subiu no banco de dados.
- Rodar o script `traffic_manager_agent.py` com campanhas de teste e validar se ele desativa (mata) os banners com péssima performance de cliques, mantendo apenas os banners que dão lucro.
