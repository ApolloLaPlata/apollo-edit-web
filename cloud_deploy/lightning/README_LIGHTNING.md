# Padrão de Instalação: Frota Lightning AI (LLM / Cérebro)

Este é o padrão ouro oficial de implantação para **todas** as suas contas da Lightning AI. Ao aplicar esta arquitetura em um Studio (máquina) da Lightning, você criará um endpoint privado de API idêntico à OpenAI que rodará o **Llama 3 (8B)** usando a GPU gratuita oferecida.

## Arquivos Necessários
1. `lightning_llm_engine.py` (O Código-fonte Mestre do FastAPI)

## Passos para Padronização

1. **Crie um Novo Studio na Lightning AI:**
   - Faça login na conta.
   - Crie um Studio na nuvem selecionando Python ou "Start from scratch".
   - (Opcional mas recomendado) Selecione a GPU `T4` se estiver no Free Tier, ou CPU se for apenas testes.

2. **Instalação das Bibliotecas Mestre:**
   Abra o Terminal dentro do Studio da Lightning AI e cole este comando exato para instalar as dependências necessárias de aceleração em GPU (vLLM / Llama CPP):
   ```bash
   pip install fastapi uvicorn huggingface_hub
   
   # O llama-cpp-python com suporte a CUDA para usar os 16GB da placa T4:
   CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python
   ```

3. **Inicie o Motor:**
   Faça upload do arquivo `lightning_llm_engine.py` para a pasta raiz do Studio. Em seguida, inicie o servidor:
   ```bash
   python lightning_llm_engine.py
   ```
   *Na primeira vez, ele fará o download do modelo GGUF (aprox. 5GB). Nas próximas vezes, o boot será imediato.*

4. **Registro no Apollo Master:**
   - Com o servidor rodando, o Studio abrirá uma aba lateral Web, ou você pode clicar no link que diz "Port 8000".
   - Copie o **URL público gerado pelo Lightning** (ex: `https://8000-roxingo-xxx.projects.lightning.ai`).
   - Vá no seu Painel Apollo > Aba Cloud, cadastre a nova conta Lightning e **COLE ESSE URL INTEIRO NO CAMPO "WORKSPACE"**.

Seu Cérebro IA particular agora está vivo e conectado à Colmeia!
