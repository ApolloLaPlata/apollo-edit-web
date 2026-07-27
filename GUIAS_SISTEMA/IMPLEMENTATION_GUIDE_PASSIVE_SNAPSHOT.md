# GUIA DE IMPLEMENTAÇÃO: PADRÃO DE SNAPSHOT PASSIVO

Esta tecnologia deve ser utilizada como **padrão ouro** para toda e qualquer nova Engine do sistema Apollo que necessite carregar arquivos pesados (Modelos `.safetensors`, `.bin`, `.pt`) na infraestrutura da Modal Cloud, garantindo Cold Starts entre 6 e 12 segundos (ao invés de minutos).

## O Problema a ser Evitado
Nunca inicialize aplicações que requerem detecção de Hardware (como PyTorch, ComfyUI, TensorRT, CUDA) dentro da função `@modal.enter(snap=True)`. O Snapshot da Modal ocorre em um ambiente **100% CPU**. Inicializar o PyTorch nesse momento o fará cachear a inexistência de GPUs. Quando a VRAM/GPU for acoplada em Runtime, o PyTorch sofrerá crash com o erro `RuntimeError: No CUDA GPUs are available`.

## A Solução Padrão: Snapshot Passivo (Linux Page Cache)
O conceito baseia-se em usar a função de Snapshot exclusivamente para carregar os pesos gigantescos do disco para a memória RAM (Page Cache do Linux) através de um comando O.S. (como `cat`), e atrasar o Boot da Aplicação para a fase de Runtime.

### Exemplo de Estrutura de Código Padrão

```python
import modal
import subprocess
import os

@app.cls(
    gpu="H100", # ou A100, A10G, L4
    image=minha_imagem_docker,
    volumes={"/modelos": meu_volume_modal},
    scaledown_window=60,
    enable_memory_snapshot=True # OBRIGATORIO: Ativa a Restauração de RAM
)
class MinhaNovaEngine:
    
    @modal.enter(snap=True)
    def load_models_to_ram(self):
        """
        Fase 1: Construção do Snapshot (100% CPU).
        Esta fase executa apenas na compilação do Deploy.
        """
        print("[Engine] Iniciando Cache Passivo de Modelos para RAM...")
        arquivos_pesados = [
            "/modelos/unet/flux1-dev.safetensors",
            "/modelos/clip/t5xxl_fp16.safetensors",
            # Adicione aqui todos os arquivos acima de 1GB
        ]
        
        for fpath in arquivos_pesados:
            if os.path.exists(fpath):
                # O comando cat força o Linux a ler o arquivo para a Memória RAM (Page Cache)
                # Como a saída vai para /dev/null, ele não imprime nada, apenas aloca.
                subprocess.run(f"cat {fpath} > /dev/null", shell=True)
                
        print("[Engine] Cache finalizado! O Snapshot da Modal salvará esta RAM.")
        self.processo_app = None # Não inicie a aplicação principal aqui!

    def _ensure_app_running(self):
        """
        Fase 2: Boot no Runtime (GPU Acoplada).
        Garante que a aplicação inicie se ainda não estiver rodando.
        """
        if self.processo_app is not None:
            return
            
        print("[Engine] Iniciando Aplicação com GPU (Runtime)...")
        # Inicie o ComfyUI ou script de Inferência aqui.
        self.processo_app = subprocess.Popen(
            ["comfy", "launch", "--listen", "127.0.0.1", "--port", "8188"],
            # ... configs de stdout/stderr
        )
        
        # Implemente um polling de saúde (ex: loop verificando um endpoint HTTP)
        # O boot levará de 3 a 5 segundos, pois os modelos já estão na RAM!

    @modal.method()
    def generate(self, prompt: str, **kwargs) -> dict:
        """
        Fase 3: Execução da Requisição
        """
        # Sempre chame a verificação de boot primeiro
        self._ensure_app_running()
        
        # Proceda com o POST/GET para a API interna do ComfyUI/Aplicação
        # ...
        return {"status": "success", "data": "..."}
```

## Benefícios Desta Abordagem
1. **Confiabilidade:** O PyTorch nunca é "enganado" pela fase de CPU, identificando a GPU perfeitamente.
2. **Velocidade de Disco Anulada:** A taxa de transferência da RAM (DDR5) para a VRAM da GPU (HBM3) é ordens de grandeza maior que a leitura do disco de rede NVMe da Modal. O tempo de leitura de modelos de 23GB cai de 4 minutos para ~3 segundos.
3. **Escalabilidade Total:** Pode ser replicado para Modelos de Linguagem (LLMs), Modelos de Vídeo (Wan, LTX) e Voz (MOSS-TTS).
