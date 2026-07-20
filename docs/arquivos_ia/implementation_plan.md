# Sistema de Orquestração, Tabela de Preços e Meta-Agente Financeiro

O usuário solicitou um salto gigantesco na arquitetura do Apollo, transformando-o num verdadeiro maestro de operações de IA.

## Objetivos do Plano
1. **Tabela de Custos e Rate Limits**: Registrar o custo de input/output, rate limits e performance de todos os modelos (Groq, OpenRouter, Gemini) no banco de dados.
2. **Painel de Orquestração (Estilo N8N)**: Interface no painel Master para criar uma *pipeline* (ex: 1º Roteirista -> 2º Revisor -> 3º Crítico) definindo estaticamente ou dinamicamente quem processa o quê.
3. **Meta-Agente de Otimização Financeira**: Um agente IA interno que lê a tabela de preços e escolhe, em tempo real, qual o melhor modelo (custo-benefício) para assumir os papéis automáticos, maximizando a margem de lucro (ex: +30% sobre o custo da API).
4. **Seleção de IA pelo Usuário**: Nas páginas de criação de roteiro/vídeo, o usuário comum terá um seletor ("Automático Gratuito" vs "Premium Pago"). O modelo pago cobrará diretamente em `Gas` ou `Credits`.
5. **Chaves Gratuitas do OpenRouter**: Mapear/utilizar chaves gratuitas do OpenRouter no modelo de rodízio.

## Proposed Changes

### Banco de Dados (`user_database.py`)
#### [MODIFY] user_database.py
- Adicionar tabela `models_pricing`:
  - `model_id` (Ex: `llama-3.3-70b-versatile`)
  - `provider` (Ex: `Groq`, `OpenRouter`, `Gemini`)
  - `tier` (`Free` vs `Paid`)
  - `input_price_per_1m`, `output_price_per_1m`
  - `rpm_limit`, `tpm_limit`
  - `status` (`Ativo`, `Rate_Limited`, `Inativo`)
- Adicionar tabela `agent_orchestration_nodes` para salvar o fluxo da pipeline.

---

### Backend Python (`admin_api.py`, `meta_agent.py`, `llm_cascade.py`)
#### [MODIFY] admin_api.py
- Criar endpoints CRUD para o `models_pricing` para a interface web ler e gravar os custos e margens de lucro.
- Criar endpoint `/api/master/orchestrator` para salvar o mapa de cadência (N8N-style).

#### [NEW] meta_agent.py
- Um daemon/background task (ou executado a cada X minutos via cron/schedule) que varre a tabela `models_pricing`.
- Verifica quais modelos Premium estão mais baratos hoje.
- Atualiza a engine padrão dos Agentes no `system_settings` (substituindo a configuração manual).

#### [MODIFY] llm_cascade.py e servidor_web.py
- Modificar o gerador de roteiro (ex: `/api/news/generate_script`) para aceitar o parâmetro `model_choice`.
- Se `model_choice == 'auto'`, usa o Meta-Agente (gratuito) sem cobrar Gas extra.
- Se `model_choice == 'gemini-1.5-pro'`, calcula o custo estimado via `models_pricing`, adiciona 30% de margem, converte para `Gas` e deduz do usuário.

---

### Frontend Admin UI (`web_ui/admin.html` e `admin.js`)
#### [MODIFY] web_ui/admin.html
- **Nova Aba "Orquestração (N8N)"**: Um construtor visual simples de colunas (Passo 1, Passo 2) com seletores de qual Agente assumirá a etapa.
- **Nova Aba "Tabela de Preços (LLMs)"**: Uma tabela em tempo real com todos os modelos, custos preenchidos por você e a "Margem de Lucro Apollo" (ex: 25%).

---

### Frontend User UI (`web_ui/noticias_scripts.html` ou semelhante)
#### [MODIFY] web_ui/noticias_scripts.html e web_ui/prime_chat.html
- Incluir o dropdown de seleção de inteligência:
  - 🤖 Apollo Otimizado (Grátis / Llama) - Rápido
  - 🧠 Gemini 1.5 Pro (Custo: ~5 Gas) - Profundo
  - 🧠 GPT-4o (Custo: ~15 Gas) - Especialista
- Implementar verificação de saldo de `Gas` antes de enviar o request.

> [!CAUTION]
> **User Review Required**
> Como estamos mudando a forma de cobrança para um modelo flutuante baseado no custo real da API + margem, o saldo do usuário (Gas) passará a flutuar dependendo do tamanho da resposta do LLM. Você aprova a cobrança retroativa após o texto ser gerado (onde sabemos exatamente a contagem de tokens), travando uma pré-autorização antes?

## Verification Plan
1. Inserir alguns modelos manualmente via Painel Admin (Groq Llama 3 = $0, Gemini 1.5 Pro = $2.50).
2. Definir a margem de 30%.
3. Fazer login como usuário comum, tentar gerar roteiro com modelo Premium, e confirmar que o saldo em `Gas` do banco de dados caiu correspondente ao custo.
4. Testar visualmente a montagem do Fluxo de Agentes na nova UI Admin.
