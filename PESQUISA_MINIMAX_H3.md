# 🔬 DOSSIÊ DE PESQUISA: MINIMAX H3 (VÍDEO OPEN-SOURCE) 🔬

## 1. INTRODUÇÃO
O MiniMax H3 é o modelo líder absoluto em código aberto para geração de vídeos (Text-to-Video e Image-to-Video), batendo de frente com o Sora. O modelo foi otimizado pela comunidade e já roda perfeitamente no **ComfyUI**.

## 2. REQUISITOS DE HARDWARE E VRAM (NA NUVEM MODAL)
O tamanho do modelo é colossal (passa dos 80GB dependendo da versão original), mas a comunidade open-source criou "quantizações" (versões compactadas FP8 / INT4).

- **Força Bruta (Precisão Máxima - 24GB+ VRAM):** 
  - Placas recomendadas: RTX 3090, 4090, ou **GPU A10G / A100** na Nuvem Modal.
  - O modelo roda nativo e liso.
- **Modo Otimizado (12GB a 16GB VRAM):**
  - Roda usando pesos quantizados. É mais barato e consome menos memória na GPU.
- **Tempo de Geração (Benchmark):**
  - Em uma placa de 24GB VRAM (Ex: RTX 4090 / A10G), um vídeo HD de 12 segundos demora entre **10 a 13 minutos**.
  - *Decisão para a Modal Farm:* O tempo alto (10 minutos) justifica 100% a sua estratégia de **20 contas separadas**! Se cada vídeo demora 10 minutos de placa, o Load Balancer é obrigatório para não engarrafar os vídeos dos usuários do SaaS.

## 3. NODES DO COMFYUI (GITHUB)
Para rodarmos o MiniMax H3 no Modal, nós precisamos injetar os "Custom Nodes" corretos na instalação do ComfyUI. Os principais repositórios mantidos pela comunidade no GitHub são:

1. **ComfyUI-MiniMaxH3-Easy** (github.com/nkxx188/ComfyUI-MiniMaxH3-Easy):
   - O melhor e mais estável. Possui fluxos completos de T2V (Texto para Vídeo) e I2V (Imagem para Vídeo).
2. **ComfyUI_MiniMax_H3_Extender** (github.com/tritant/ComfyUI-MiniMax_H3_Extender):
   - Focado em **emendar clipes**. Essencial para o Autoblog/Apollo Edit, pois permite juntar várias cenas de 12 segundos mantendo a consistência visual.
3. **ComfyUI-VDN-H3** (github.com/Saganaki22/ComfyUI-VDN-H3):
   - Focado em otimização de atenção. Reduz brutalmente o consumo de VRAM e acelera a geração. Obrigatório no nosso setup.

## 4. BIBLIOTECA DE PROMPTS E ESTRUTURA
O MiniMax H3 **não** aceita prompts comuns (ex: "um cara correndo na chuva"). A engenharia de prompt dele é extremamente complexa e técnica. O repositório oficial possui a documentação (h3-prompt-writing).

A estrutura OBRIGATÓRIA de um prompt do MiniMax H3 deve ser fragmentada nestes blocos:
- integrated_multimodal_description: Descrição visual exata, ângulos de câmera e iluminação.
- overall_soundscape: Como o MiniMax gera áudio junto, você precisa descrever os efeitos sonoros ambientes.
- 
on_diegetic_music: Qual o clima da música de fundo.
- **Listas de Cenas Cronometradas:** O prompt exige que você defina o que acontece no segundo 0:02, 0:05, etc.

*Conclusão da Engenharia de Prompt:* Nós vamos ter que usar um **Sub-Agente LLM (Lightning AI)** no Apollo Edit para pegar a ideia simples do usuário e "traduzir" secretamente para esse formato técnico gigantesco antes de enviar para o ComfyUI na Modal.

---
**Status da Pesquisa:** Compilada e arquivada com sucesso. Pronta para integração na infraestrutura de vídeo.
