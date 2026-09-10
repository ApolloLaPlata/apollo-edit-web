# ElevenLabs API - Referência Técnica e Comercial

Este documento serve como a base de conhecimento permanente sobre as capacidades, custos e estratégias de uso da ElevenLabs dentro do ecossistema **Apollo Edit Web**.

---

## 1. Visão Geral
A ElevenLabs é a líder atual de mercado em síntese de voz (TTS) e clonagem de emoções no formato *Zero-Shot*. 

### Vantagens (Por que usar?)
* **Qualidade Emocional Imbatível:** Consegue interpretar risadas, choros, gritos e sussurros diretamente do texto sem sotaque estrangeiro (no modelo Multilingual v2).
* **Voice Design e Voice Changer:** Ferramentas nativas prontas para criar matrizes vocais absolutas a partir de meia dúzia de palavras.
* **APIs Consolidadas:** Possui SDK oficial em Python (`elevenlabs-python`), o que facilita a integração em menos de 10 linhas de código no nosso backend.

### Desvantagens (O Gargalo)
* **Preço em Escala:** Ao contrário do nosso XTTS rodando em placa de vídeo na nuvem (Modal), a ElevenLabs cobra por caractere e por minuto gerado. Gerar centenas de vídeos curtos diários puramente na ElevenLabs pode destruir a margem de lucro.
* **Limitações do Tier Gratuito:** O plano Free restringe o uso comercial de músicas e tranca o acesso a clonagens mais sensíveis. Exige um plano Starter ($5) ou recarga de créditos (Top Up).

---

## 2. Capacidades da API e Tabela de Preços

Com base nas tabelas oficiais do sistema, estes são os custos das APIs por camada de serviço:

| Tipo de Serviço | Modelo | Preço Unitário | Detalhes e Latência |
| :--- | :--- | :--- | :--- |
| **Texto para Voz (Rápido)** | Flash / Turbo | **$0.05** por 1.000 caracteres | Latência ultra-baixa (~75ms). 32 idiomas suportados. |
| **Texto para Voz (Alta Qualidade)** | Multilingual v2 / v3 | **$0.10** por 1.000 caracteres | A melhor qualidade do mundo para emoções. Latência (~250-300ms). |
| **Transcrição (STT)** | Scribe v1 / v2 | **$0.22** por Hora | +98% de precisão. Suporta *Keyterm prompting*. |
| **Transcrição em Tempo Real** | Scribe v2 Realtime | **$0.39** por Hora | Latência baixa (~150ms). Timestamps precisos a nível de palavra. |
| **Agentes de Conversação** | Speech Engine | **$0.08** por Minuto | Pipeline único otimizado para chatbots. |
| **Geração de Música** | Music | **$0.15** por Minuto | Licença comercial apenas para contas Starter+. Limite de 5 min. |
| **Isolador de Voz (Tratamento)** | Voice Isolator | **$0.12** por Minuto | Remove ruídos ambientes, reverb e interferências (ótimo para limpar matrizes). |
| **Conversor de Voz (STS)** | Voice Changer | **$0.12** por Minuto | +10.000 vozes disponíveis para converter áudio-para-áudio. |
| **Efeitos Sonoros (SFX)** | Sound Effects | **$0.12** por Geração | SFX livres de royalties. |
| **Dublagem V1 (Básica)** | Dubbing v1 | **$0.33** por Minuto | Detecção automática de falantes. 29 idiomas. |
| **Dublagem V2 (Pro)** | Dubbing v2 | **$2.20** por Minuto | Dublagem ponta-a-ponta. 92 idiomas suportados. |

---

## 3. Créditos Pré-Pagos (Top Up)
A plataforma permite adicionar saldo via painel (Add credits). 
A conversão atual para uso sob demanda é de aproximadamente **$3.64 = 10.000 créditos**. A adição mínima recomendada na tela é de **$5**. 

---

## 4. O Veredito: Precisamos da ElevenLabs?

Temos duas formas estratégicas de usar isso no **Apollo Edit Web**, dependendo do que o cliente final busca:

### Estratégia A: O Assalto (Plano Básico do Apollo)
* **Como funciona:** Você (ou nós, internamente) paga **$5 dólares UMA VEZ na vida** e usa a API Multilingual v2 para gerar **5 áudios matrizes perfeitos** de um personagem (Rindo, Bravo, Chorando, Neutro e Assustado). 
* **O truque:** Baixamos esses 5 áudios e paramos de usar a ElevenLabs. A partir daí, nosso XTTS gratuito na nuvem engole essas matrizes e produz tudo de graça. É a forma de comprar a alma do personagem por $5.

### Estratégia B: O SaaS Premium (Plano Luxo do Apollo)
* **Como funciona:** Integramos a API oficial no código. O cliente do seu site que for exigente e não quiser o "leve ruído" do XTTS, vai assinar o Plano Premium do seu site. 
* **Monetização:** O cliente insere a própria chave API dele (*Paste to Go*) na interface do Apollo, ou usa a sua chave da empresa. Neste segundo caso, nós cobramos o custo da ElevenLabs + 20% de margem de lucro por clique do cliente. 

> **Conclusão de Arquitetura:** A ElevenLabs não substituirá o XTTS como operário padrão devido ao custo, mas ela é a **peça de luxo essencial** para criar as matrizes perfeitas e para oferecer como serviço premium cobrado à parte na plataforma.
