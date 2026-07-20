# Padrão de Instalação: Frota Modal (Vídeo & Imagem)

Este é o padrão ouro oficial de implantação para **todas** as suas contas Modal. A padronização garante que qualquer chave inserida no sistema Apollo funcionará instantaneamente com os mesmos modelos de VRAM, Snapshots e configurações de Load Balance.

## Arquivos Necessários
1. `apollo_modal_engine.py` (O Código-fonte Mestre)

## Passos para Padronização

1. **Faça o Login na Conta Desejada:**
   Abra o terminal e execute:
   ```bash
   modal token new
   ```
   *Isso abrirá o navegador. Faça login com a respectiva conta e confirme.*

2. **Sincronização Inicial (Download do Arsenal):**
   Execute o script pela primeira vez invocando a função de download de modelos. Isso criará o volume persistente SSD na conta atual e fará o cache do LTX, Wan e Flux:
   ```bash
   modal run apollo_modal_engine.py::download_ai_models
   ```
   *Aguarde a conclusão. Pode demorar alguns minutos dependendo da taxa de transferência da HuggingFace.*

3. **Implantação na Nuvem (Deploy):**
   Uma vez com os modelos cacheados no disco virtual da Modal, suba o motor como um endpoint de API fixo e contínuo:
   ```bash
   modal deploy apollo_modal_engine.py
   ```

4. **Registro no Apollo Master:**
   Pegue o **Token ID**, o **Token Secret** e, principalmente, o **Workspace** (o prefixo da conta que a Modal gerou, ex: `roxingo`) e insira na aba "Painel Cloud" do sistema, selecionando o provedor `modal`. 

A infraestrutura dessa conta está padronizada e conectada à Colmeia!
