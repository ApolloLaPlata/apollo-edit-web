# 🚀 A BÍBLIA DA ARQUITETURA APOLLO MODAL AI
**Transformando o ComfyUI em uma API Serverless de Alta Performance**
*(Data de Conclusão: Julho de 2026)*

---

## 📖 INTRODUÇÃO
Este documento registra a arquitetura de otimização desenvolvida após 1 mês de intensos testes para o projeto **Apollo Edit Web**. O objetivo alcançado foi transformar workflows do ComfyUI (como o FLUX.1) em uma API serverless hospedada na Modal, alcançando tempos de resposta de nível comercial (nível Midjourney).

**Marcas de Tempo Alcançadas:**
- 🥶 **Cold Start (Máquina Fria):** ~127 segundos (com modelos pesados de 35GB + Upscaler).
- 🔥 **Warm Start (Máquina Quente) S/ Upscale:** ~7.4 segundos.
- 🔥 **Warm Start (Máquina Quente) C/ Upscale 4x:** ~36.3 segundos.

Esses tempos foram atingidos eliminando transferências de rede e engarrafamentos de processamento. Toda IA que operar na base de código deste projeto **deve** consultar este guia antes de implementar novos modelos de geração (ex: Imagem-para-Imagem, Multi-Personagens, LTX-Video, etc).

---

## 🧠 PILAR 1: MEMORY SNAPSHOTS (O Assassino do Cold Start)
Se você apenas subir um container com GPU e mandar carregar o modelo do disco (mmap lazy loading), a Modal levará de 4 a 6 minutos toda vez que a máquina esfriar. Para resolver isso, usamos os **Memory Snapshots**.

### Como Funciona?
A Modal permite capturar o estado da memória RAM do container **durante o build**. Quando o container "acorda" na internet, ele não precisa ler o HD; a memória já acorda com os 35GB de modelos FLUX carregados.

### O Código de Snapshot Perfeito
Para que o Snapshot não quebre (já que a Modal executa o snapshot usando CPU, não GPU), precisamos mockar o PyTorch. Abaixo a estrutura padrão que **sempre deve ser usada**:

```python
import modal
import subprocess
from contextlib import contextmanager
import os

# MOCK PARA O SNAPSHOT DA MODAL (CPU-ONLY) NÃO CRASHAR
@contextmanager
def force_cpu_during_snapshot():
    import torch
    orig_is_available = getattr(torch.cuda, 'is_available', lambda: False)
    orig_current_device = getattr(torch.cuda, 'current_device', lambda: torch.device('cpu'))
    torch.cuda.is_available = lambda: False
    torch.cuda.current_device = lambda: torch.device('cpu')
    try:
        yield
    finally:
        torch.cuda.is_available = orig_is_available
        torch.cuda.current_device = orig_current_device

app = modal.App(name="apollo-render-router")

@app.cls(gpu="H100", timeout=1200, enable_memory_snapshot=True)
class MinhaEngine:
    @modal.enter()
    def load_model(self):
        with force_cpu_during_snapshot():
            print("Lendo modelos para a RAM (Snapshot)...")
            # Ler o arquivo bruto puxa o modelo pra memória RAM
            subprocess.run("cat /comfyui_models/unet/flux1-dev.safetensors > /dev/null", shell=True)
```
**Regra de Ouro:** Nunca inicie o servidor do ComfyUI no `@modal.enter()`. Deixe para iniciar o servidor apenas quando o método `generate()` for chamado. Assim, evitamos dependências de GPU no snapshot.

---

## ⚡ PILAR 2: ARQUITETURA "IN-NODE" (Único Workflow Mutante)
O maior erro de otimização é tentar dividir etapas (ex: Geração -> Upscale -> Envio) em containers diferentes. A transferência da imagem de uma máquina pra outra destrói o tempo de resposta.

**A Solução In-Node:**
Tudo deve ocorrer dentro da mesma GPU que gerou a imagem base, enquanto a imagem ainda habita a VRAM (Video RAM).

Em vez de criar um `.json` gigante pra cada possibilidade, o código Python atua como um "cirurgião" de JSON:
1. O Python carrega o workflow base (ex: `apollo_flux2_klein.json`).
2. Se o usuário ativou o Upscale, o Python **injeta os nodes de Upscale no JSON**.
3. O Python redireciona a saída do VAE Decode direto para o Upscale.
4. Somente então a requisição completa é enviada para o ComfyUI interno do container.

### Exemplo Lógico (Injeção de Código):
```python
if use_upscale:
    # Cria o node do Upscale no JSON
    prompt["999"] = {
        "class_type": "UpscaleModelLoader",
        "inputs": {"model_name": "4x-UltraSharp.pth"}
    }
    prompt["1000"] = {
        "class_type": "ImageUpscaleWithModel",
        "inputs": {
            "upscale_model": ["999", 0],
            "image": ["NODE_DE_IMAGEM_BASE", 0] # Linka dinamicamente a saída base
        }
    }
```

---

## 🐛 PILAR 3: A REGRA DO SYMLINK (Erro 400 Bad Request)
Sempre que usamos a API do ComfyUI junto com Volumes Montados da Modal, arquivos de modelos como o de Upscale podem sofrer rejeição (ex: `Value not in list: model_name: '4x-UltraSharp.pth' not in []`). Isso ocorre porque nodes nativos muitas vezes ignoram o arquivo `extra_model_paths.yaml`.

**A Solução Absoluta:**
Sempre crie symlinks (`ln -sf`) dos Volumes diretamente para a pasta original de modelos do ComfyUI antes do servidor iniciar. 
No método `load_model()`:
```python
subprocess.run("rm -rf /comfyui/models/upscale_models", shell=True)
subprocess.run("ln -sf /comfyui_models/upscale_models /comfyui/models/upscale_models", shell=True)
```

---

## 🛠️ PASSO-A-PASSO PARA NOVOS MODELOS
Quando o usuário (ou a IA Autoblog) pedir para implementar um novo workflow de ComfyUI (ex: Multi-Personagem ou Image-to-Image), execute a seguinte esteira de produção:

1. **Desenvolvimento Local:** Construa e teste o Workflow normalmente na interface visual do ComfyUI até que os resultados fiquem perfeitos.
2. **Exportação API:** Salve o arquivo no formato "API Format" (sem dados da GUI, apenas os nodes lógicos).
3. **Mapeamento de Variáveis:** Identifique os IDs dos Nodes que recebem o Prompt Positivo, Negativo, Seeds, Aspect Ratio e Imagens (Base64).
4. **Criação da Engine Modal:** Crie uma nova classe `class NovaEngine:` seguindo as diretrizes do `flux_txt2img_engine.py`. Garanta que a Engine:
   - Use `enable_memory_snapshot=True`.
   - Baixe modelos faltando no `load_model()`.
   - Injete funções extras (Upscale) **in-node** alterando o JSON manipulado em Python.
5. **Teste Rápido:** Lance comandos `modal run` enviando um JSON de teste e meça o tempo (Cold e Warm Start).
6. **Integração no Router:** Registre a nova engine no arquivo principal `apollo_modal_engine.py` (no roteador `POST /generate/image` ou `POST /generate/video`).
7. **Refino de Qualidade:** Certifique-se que o frontend fará chamadas diretamente pela API da Modal e não pelo Vercel, pois a Vercel corta as conexões após 10 segundos.

---

Este manual representa o estado-da-arte de computação em nuvem otimizada para IAs Generativas em 2026. Respeite os pilares. Construa rápido, processe mais rápido ainda.
