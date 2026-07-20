# Agente Diretor de Vendas e Marketing (Dynamic Pricing & Marketing Agent) 💰🎯

A sua visão está perfeita. Vamos transformar o sistema em um e-commerce inteligente de IAs. O Agente de Vendas não apenas vai gerar o relatório, como vai **agir**, baixando a margem de lucro de IAs ociosas para fazer "Promoções Relâmpago" e gerar *Banners* diários na tela do usuário.

## User Review Required
> [!IMPORTANT]
> **Imagens dos Banners Promocionais:** Você mencionou que o Agente precisa ter acesso a imagens e ícones para criar os banners. A abordagem mais barata, instantânea e visualmente impressionante no desenvolvimento web atual é permitir que o Agente gere **Banners com HTML/CSS Avançado (Gradients, Emojis 3D, Animações)** em vez de gastar APIs pesadas gerando arquivos `.jpg`. Esses banners rodam perfeitamente no site e carregam na hora. Você concorda com essa abordagem de Banners HTML Dinâmicos?

> [!WARNING]
> **Regra de Lucratividade:** O Agente terá permissão para alterar a margem do banco de dados (que hoje é fixa em 30% / 1.3x). Para garantir que a máquina nunca te dê prejuízo, vou programar um **Piso Mínimo de Margem (ex: 10%)** e um **Teto Máximo (ex: 100%)**. Concorda com essas travas de segurança na hora dele precificar?

## Proposed Changes

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\user_database.py`
#### [MODIFY] `user_database.py`
- Adicionar a coluna `margin_multiplier REAL DEFAULT 1.3` (que representa seus 30% de lucro base) na tabela `models_pricing`.

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py`
#### [MODIFY] `servidor_web.py`
- Atualizar a dedução de "Gasolina" (linha 3802) para parar de usar a margem fixa de `1.3` e passar a calcular o custo em cima do `margin_multiplier` específico daquele modelo no banco de dados.
- Criar a rota de API para o frontend do usuário puxar as `ad_campaigns` ativas e exibi-las.

### `E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\marketing_agent.py`
#### [NEW] `marketing_agent.py`
- Um novo agente autônomo (Pós-Venda + Marketing).
- **Passo 1 (Precificação Dinâmica):** Ele olha os modelos menos usados nos últimos 7 dias. Pega 1 ou 2 deles e abaixa a `margin_multiplier` de 1.3 para 1.1 (apenas 10% de lucro) para criar uma "Promoção Oportunista". Já para os mais usados, ele sobe sutilmente (ex: 1.35) para aumentar a lucratividade silenciosamente.
- **Passo 2 (Criação de Campanha):** Ele se conecta a um modelo Premium no OpenRouter e pede: *"Crie um texto persuasivo anunciando que o modelo X está em promoção hoje com crédito reduzido. E crie o código CSS para o banner"*.
- **Passo 3:** Ele injeta esse Banner na tabela `ad_campaigns`.

### Interface do Usuário Final (`web_ui/noticias_scripts.html`)
#### [MODIFY] `noticias_scripts.html`
- Adicionar uma div no topo da página de Geração de Roteiros que carrega e exibe automaticamente o Banner Promocional criado pelo Agente de Marketing naquele dia.

## Verification Plan

### Testes Manuais
- Rodar o `marketing_agent.py` localmente.
- Verificar se ele altera a margem de algum modelo no banco para `1.1`.
- Checar a tabela `ad_campaigns` para ver se ele criou a campanha com sucesso.
- Abrir a interface de criação de roteiros (`noticias_scripts.html`) e verificar se um banner super chamativo avisando sobre a promoção do dia aparece para o usuário final, e se a calculadora de "Custo em Gas" reflete o desconto na interface.
