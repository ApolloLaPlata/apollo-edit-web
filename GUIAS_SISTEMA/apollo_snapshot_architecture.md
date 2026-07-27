# Apollo Edit Web: Arquitetura de Snapshot Passivo (Cold Start Zero)

## O Problema Original (Cold Start de 4.5 minutos)

Originalmente, a tentativa de usar a funcionalidade de `enable_memory_snapshot=True` da Modal Cloud estava falhando silenciosamente no background.
A Modal constrói o snapshot rodando a função `@modal.enter(snap=True)` em um ambiente **apenas com CPU**.
Ao tentar iniciar o ComfyUI durante essa fase, o PyTorch era inicializado, buscava por GPUs, e registrava no cache interno da C++ engine que a máquina possuía `0 GPUs`. Quando a placa de vídeo H100 era acoplada na fase de runtime, o estado da memória era restaurado com o PyTorch permanentemente "cego", resultando em erros fatais do tipo `No CUDA GPUs are available`.

Como proteção, a Modal abortava o snapshot e voltava a subir as máquinas do zero toda vez. Isso forçava o download e alocação de 23GB de modelos (`.safetensors`) do disco de rede para a RAM e VRAM em tempo real, custando **272 segundos (4.5 minutos)** por requisição inicial.

---

## A Solução: Snapshot Passivo (Linux Page Cache)

A solução definitiva ("Xeque-Mate") evitou a inicialização do ComfyUI e do PyTorch na fase de Snapshot. Em vez de subir o aplicativo, nós forçamos o Sistema Operacional Linux a carregar os arquivos pesados para a **memória RAM (Page Cache)**.

```python
# Fase 1: Construção do Snapshot (Apenas CPU)
@modal.enter(snap=True)
def load_model(self):
    cache_files = [
        "/comfyui_models/unet/flux1-dev.safetensors",
        "/comfyui_models/clip/t5xxl_fp16.safetensors",
        "/comfyui_models/vae/ae.safetensors",
    ]
    for fpath in cache_files:
        # Força os arquivos para a memória RAM sem iniciar o PyTorch
        subprocess.run(f"cat {fpath} > /dev/null", shell=True)
```

Na fase de Tempo Real (quando a API é requisitada e a H100 é acoplada), o ComfyUI é finalmente iniciado. Como os 23GB de arquivos já estão armazenados na memória RAM restaurada do Snapshot, o ComfyUI carrega instantaneamente, detecta a GPU perfeitamente, e a geração ocorre em segundos.

---

## Contabilidade de Tempos (Logs Oficiais)

Os testes reais monitorados apontam a seguinte cronologia para o **Cold Start Verdadeiro**:

| Etapa | Duração | Descrição |
|-------|---------|-----------|
| **Snapshot Restore** | `~4.50s` | A Modal acorda o container H100 e restaura a imagem da RAM contendo os 23GB de modelos pré-carregados. |
| **ComfyUI Boot** | `~3.80s` | O ComfyUI é ligado. Como o IO do disco é evitado (os arquivos já estão na RAM), o boot é relâmpago. |
| **Geração na VRAM** | `~1.31s` | A GPU H100 engole os tensores e executa as 20 iterações do Flux 2 DEV absurdamente rápido (em torno de 17.30it/s). |
| **Overhead de HTTP** | `~1.28s` | Conversão da imagem para Base64, tráfego de rede e roteamento FastAPI. |
| **Tempo Total Visível** | **10.89s** | Tempo exato cronometrado pelo cliente HTTP, desde o disparo até o recebimento da imagem PNG. |

*Nota: Em máquinas já aquecidas (Warm Start), o tempo total cai para **~5.01s** (pois o Boot já ocorreu).*

---

## Contabilidade Financeira (Redução de Custos em Dólar)

O custo da NVIDIA H100 na Modal Cloud é de aproximadamente **$5.50 por hora** (cerca de **$0.0015 por segundo**).

### Antes (Cold Start sem Snapshot)
- Tempo de espera inútil: 272 segundos
- Custo desperdiçado por Cold Start: **$0.40** (Quarenta centavos de dólar *apenas para a máquina ligar*).

### Agora (Cold Start com Snapshot Passivo)
- Tempo de espera: 10.89 segundos
- Custo por Cold Start: **$0.016** (Apenas um centavo e meio de dólar).
- Geração quente (5s): **$0.007** (Menos de um centavo por imagem gerada).

### Impacto Financeiro
Essa arquitetura reduziu o custo de inicialização inativa em **96%**, economizando quase meio dólar toda vez que o servidor precisava ser escalado. Se o servidor escalasse apenas 100 vezes por dia, a economia gerada chega a **$38.00 por dia**, viabilizando o projeto economicamente para a produção em larga escala.
