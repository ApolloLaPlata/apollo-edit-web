---
name: apollo_qwen_mastery
description: >-
  Use esta skill para entender a arquitetura definitiva de geração de voz emocional com Qwen3-TTS. Contém a Regra de Ouro (Texto Puro + Temperatura Dinâmica + Instruct Teatral) validada empiricamente para o Apollo Edit Web e Descarga News.
---

# Apollo Qwen Mastery (O Padrão-Ouro de Áudio)

Esta skill documenta o limite extremo extraído do modelo Qwen3-TTS para geração de vozes clonadas com altíssima carga emocional, seja humor histérico, raiva ou depressão. Qualquer nova implementação de roteiro ou áudio deve seguir estritamente estas diretrizes.

## A "Regra de Ouro" do Qwen3-TTS

Durante os testes intensivos do Laboratório de Modais, descobrimos que o modelo Qwen3 não reage bem a manipulações diretas no texto (como injetar `[laugh]` ou onomatopeias artificiais). A magia acontece exclusivamente na **combinação de 3 fatores**:

### 1. Texto Estritamente Puro (`text_to_speak`)
- **NÃO** insira tags artificiais (ex: `[risos]`, `*choro*`).
- **NÃO** adultere a sintaxe do que deve ser falado.
- O texto deve ser a fala limpa, gramaticalmente correta, permitindo apenas pontuações naturais (`!`, `?`, `...`) para gerar pausas de respiração.

### 2. A Instrução Teatral Pesada (`instruct_mood`)
- Toda a carga emocional é direcionada pelo parâmetro `instruct`.
- Trate o modelo como um Ator de Hollywood. 
- **Exemplo de Instruct:** "O ator está em um ataque incontrolável de riso e felicidade. Ele ri enquanto fala, num tom de total humor e escárnio descontraído."
- **Nunca seja brando.** Descreva a intensidade e a vibração (ex: "sussurro misterioso", "grito de terror").

### 3. Temperatura Dinâmica (O Fator Máximo de Alucinação)
- O Qwen3-TTS é um LLM auto-regressivo. Emoções complexas exigem que ele "quebre" o padrão engessado e arrisque novos caminhos neurais.
- A **Temperatura** deve ser definida **cena a cena** pelo robô roteirista (LLM), variando de `0.5` a `2.0`:
  - `0.5 a 0.8`: Falas sérias, jornalísticas, leitura de documentário reta.
  - `1.0 a 1.2`: Conversa casual, pequenas flutuações de humor.
  - `1.5 a 2.0`: **Zona de Risco/Emoção Extrema.** Use para choro, pânico, risadas pesadas, agressividade verbal. Força o modelo a "alucinar" ofegadas e trejeitos sem desmanchar a fala.

## A Dinâmica do Script Engine (SaaS B2C)

No Orquestrador do Apollo Edit, o prompt do LLM (Roteirista) é obrigado a retornar um JSON (validado via Pydantic) contendo:
- A Cena.
- O Texto Puro.
- O Prompt de Imagem.
- A Instrução Teatral.
- **A Temperatura Flutuante**.

Desta forma, a IA roteirista tem o poder absoluto de dirigir a temperatura emocional do Qwen3 de forma autônoma durante o vídeo, entregando um produto hiper-dinâmico que intercala tom sério com surtos emocionais de forma natural.

## Integração Futura (Aviso sobre Modelos Musicais)
Assim como o Qwen3 exigiu pesquisa empírica para achar seu "sweet spot" de Temperatura, modelos de música como o **ACE-Step** exigem experimentação semelhante (inserção de letras estruturadas e ajustes de guidance/omega). Se for implementar música, aplique este mesmo rigor de laboratório e crie uma nova Skill específica para documentar o padrão-ouro descoberto.
