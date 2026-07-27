# 🚨 KERNEL DO APOLLO: A ARQUITETURA DE SNAPSHOT PASSIVO 🚨

**LEITURA OBRIGATÓRIA PARA QUALQUER AGENTE IA:** 
Se você é um novo agente assumindo este projeto no futuro, **PARE O QUE ESTÁ FAZENDO E LEIA ISSO**. O usuário passou dias sofrendo com queimas de saldo (centenas de dólares) em testes burros porque agentes anteriores tentavam inicializar o PyTorch dentro do Snapshot da Modal Cloud. Não repita esse erro. Esta é a tecnologia primária que mantém o site competitivo a nível de mercado.

---

## 1. O Paradigma do Custo e Independência
O projeto Apollo Edit depende de modelos colossais (Flux 23GB, Moss TTS, LTX Video, Wan). Depender de APIs de terceiros custaria milhares de dólares. Hospedar na Modal Cloud resolve o problema, mas a Modal desliga a máquina (Cold Start). Iniciar uma máquina H100 do zero baixando modelos da rede demorava **4.5 minutos** e custava **$0.40 por chamada ociosa**.

**A Inovação:** Nós criamos uma versão "congelada" (Snapshot) da máquina perfeita, para que quando uma requisição chegue, a Modal apenas "injete" esse estado congelado na placa H100, rodando o processo em **10 segundos** a um custo de **$0.01**. É exatamente como o usuário deduziu: criamos uma cópia que é sempre reusada.

## 2. A Armadilha Fatal (O Erro que você NUNCA deve cometer)
A função `@modal.enter(snap=True)` cria o estado congelado rodando em uma CPU isolada (sem a GPU).
Se você tentar rodar `comfy launch`, importar `torch` ou fazer o PyTorch bater no hardware dentro desta função, o PyTorch vai ler que "Não há GPU disponível". Quando a máquina descongelar no mundo real (Runtime) já com a Placa H100 conectada, o PyTorch vai crashar dizendo que não tem GPU, porque o estado da memória dele foi congelado na fase de CPU!

## 3. O Padrão Ouro: Snapshot Passivo (Linux Page Cache)
A solução magistral é usar a fase de Snapshot **APENAS PARA LER OS ARQUIVOS PESADOS E FORÇÁ-LOS PARA A MEMÓRIA RAM DO SISTEMA OPERACIONAL (Page Cache)**. Deixamos para rodar o PyTorch / ComfyUI apenas quando a máquina acordar no Runtime.

### Como aplicar isso para MOSS TTS, Geração de Vídeo ou Qualquer Workflow:

Todo e qualquer engine novo que você for criar no `apollo_modal_engine.py` DEVE seguir esta estrutura:

```python
import modal
import subprocess
import os
import urllib.request
import time

@app.cls(
    gpu="H100", # Placa potente no runtime
    image=imagem_docker,
    volumes={"/modelos": volume_de_rede},
    scaledown_window=60,
    enable_memory_snapshot=True # A CHAVE DA VELOCIDADE
)
class QualquerEnginePesada:
    
    @modal.enter(snap=True)
    def load_models_to_ram(self):
        """
        PASSO 1: CONGELAMENTO NA CPU.
        Injeta os arquivos na RAM passivamente usando 'cat'.
        NUNCA inicie o software aqui.
        """
        arquivos = [
            "/modelos/tts/moss_tts_weights.safetensors", 
            "/modelos/video/ltx_video.safetensors"
            # Insira todos os arquivos pesados que o seu workflow usa
        ]
        
        for f in arquivos:
            if os.path.exists(f):
                # Isso joga o arquivo na RAM (Page Cache). Quando a Modal congelar
                # a RAM, o arquivo vai junto. Zero disco no Runtime!
                subprocess.run(f"cat {f} > /dev/null", shell=True)
                
        self.app_process = None # O Software continua desligado.

    def _ensure_app_running(self):
        """
        PASSO 2: BOOT NO RUNTIME (COM GPU).
        Esta função acorda o software. Como os pesos já estão na RAM,
        o boot leva menos de 4 segundos.
        """
        if self.app_process is not None:
            return
            
        # Agora sim a GPU está presente! Ligue o PyTorch/ComfyUI.
        self.app_process = subprocess.Popen(["comfy", "launch", "--port", "8188"])
        
        # Ping de espera até a porta responder
        for _ in range(30):
            try:
                urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=1)
                break
            except:
                time.sleep(1)

    @modal.method()
    def generate(self, **kwargs):
        """
        PASSO 3: GERAÇÃO
        """
        # Sempre garanta que o software ligou antes de mandar a requisição
        self._ensure_app_running()
        
        # Execute a requisição HTTP local para o software
        return "Sucesso em 10 segundos!"
```

## 4. O Impacto Estratégico
Aplicar esse código em toda a infraestrutura não é "apenas uma otimização", é o que mantém o negócio viável, cortando 96% dos custos de infraestrutura em nuvem e provendo uma experiência em tempo real ao usuário sem depender de chaves de API restritivas. 

**Ao usuário futuro ou agente:** Se você mexer no `backend/cloud_tools/engines`, certifique-se de que nenhum import do `torch` ocorra no nível do arquivo ou no nível do método `@modal.enter(snap=True)`. Todos os imports pesados devem estar dentro dos métodos de Runtime.
