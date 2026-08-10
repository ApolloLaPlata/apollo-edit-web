# Arquitetura de TTS Emocional (Voice Forge)
**Data de Criação:** Agosto de 2026
**Status:** Validado Teoricamente (Aguardando Testes Laboratoriais)

## O Problema
O modelo XTTSv2 domina a pronúncia e clonagem (Zero-Shot) do Português (PT-BR) com perfeição, além de ser open-source e rodar localmente/Modal.
**Limitação Crítica:** Ele não suporta parâmetros explícitos de emoção (como [SAD] ou [ANGRY]). A emoção é extraída 100% da leitura do arquivo de referência (speaker_wav) e da pontuação do texto.

## A Solução: Transferência de Emoção Cross-Lingual (Duas Camadas)
Para não ficarmos reféns de modelos pagos (ElevenLabs) ou modelos com sotaque americano crônico em PT-BR (F5-TTS, CosyVoice), o Apollo OS utiliza a arquitetura de **Voice Forge**:

### Camada 1: O "Ator" (Gerador de Referência)
1. O usuário fornece o áudio base (Neutro) do Personagem (ex: Joãozinho).
2. O sistema envia esse áudio neutro para um modelo secundário de atuação extrema (ex: **F5-TTS**).
3. O F5-TTS é comandado a gerar 3 frases em **Português (Americanizado)**, focadas em emoções extremas:
   - Raiva: *"Eu estou com muita raiva de você!"*
   - Tristeza: *"Eu não aguento mais isso... por favor..."*
   - Alegria: *"Isso é maravilhoso! Que incrível!"*
4. O F5-TTS gerará esses áudios com a identidade do Joãozinho e com uma **alta carga emocional**, mas com um sotaque de gringo. Estes áudios são salvos no banco de dados como os **Arquétipos Emocionais de Referência**.

### Camada 2: O "Locutor" (XTTS)
1. No chat ao vivo, o LLM decide a emoção através de tags (ex: [RAIVA]).
2. O Roteador intercepta a tag e seleciona a referência correspondente gerada na Camada 1 (joaozinho_raiva_ref.wav).
3. O **XTTSv2** recebe o texto final em PT-BR e usa a referência com raiva.
4. **O Efeito Mágico:** O XTTS "suga" a respiração ofegante, a agressividade e a velocidade do áudio de referência, mas descarta o sotaque gringo, reconstruindo os fonemas com sua base de dados perfeita de PT-BR.
5. O resultado final é a fala do LLM em Português Nativo, com a voz do Joãozinho, atuando com a emoção extraída do F5-TTS.

## Testes Laboratoriais Primários (Pure XTTS)
Antes de invocar o Pipeline completo, o sistema deve ser testado no seu estado puro (Pure TTS).
O script 	est_xtts_limits.py expõe parâmetros ocultos do XTTS para validar o quanto de emoção pode ser extraído sem a Camada 1:
- 	emperature: (0.1 a 1.0) Define a taxa de caos/expressividade da geração.
- speed: Define a velocidade, auxiliando na prosódia de ansiedade ou melancolia.
- **Pontuação:** O XTTS é altamente sensível a reticências (...), exclamações múltiplas (!!!) e MAIÚSCULAS.

O LLM do Apollo Edit Web será condicionado (Prompt Engineering) para gerar roteiros que maximizem a eficácia desses gatilhos sintáticos.
