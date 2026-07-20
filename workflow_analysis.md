# Análise de Workflows do Curso ComfyUI

## Especificações da Máquina Local

| Item | Especificação |
|------|--------------|
| **CPU** | AMD Ryzen 7 1700 (8 cores / 16 threads, 3.0GHz) |
| **RAM** | 32 GB |
| **GPU** | AMD Radeon RX 580 2048SP |
| **VRAM** | 8 GB GDDR5 |
| **API** | DirectX 12 (sem CUDA) |

> [!CAUTION]
> A RX 580 é uma GPU **AMD** — ela **NÃO tem CUDA**. A maioria dos modelos AI (PyTorch, safetensors) rodam via CUDA da NVIDIA. Rodar localmente exige o **DirectML** ou **ROCm**, que têm suporte limitado e geralmente mais lento. **Recomendação: usar cloud para AI pesada.**

---

## 86 Workflows — Classificação por Compatibilidade

### ✅ PODE RODAR LOCALMENTE (RX 580 / 8GB VRAM via DirectML)
*Modelos leves, sem GPU intensivo, ou baseados em CPU/API.*

| Workflow | Motivo |
|----------|--------|
| WORKFLOW - CAPTION | Apenas análise de imagem (BLIP/Florence) — leve |
| WORKFLOW - REMOVE BACKGROUND | Leve, REMBG roda em CPU |
| WORKFLOW - IMAGE UPSCALE BASICO | Upscale básico, baixo consumo VRAM |
| WORKFLOW - VIDEO WATERMARK REMOVE | Processamento de vídeo CPU |
| WORKFLOW - STABLE AUDIO | Modelos de áudio são leves |
| WORKFLOW - F5 TTS | TTS, roda em CPU |
| WORKFLOW - QWEN TTS | TTS via API Qwen |
| API NODES | Chamadas de API externas, sem GPU local |

---

### ☁️ SOMENTE CLOUD — Exige NVIDIA CUDA + VRAM Alta

#### 🖼️ **Geração de Imagem (FLUX)**
| Workflow | GPU Recomendada | VRAM Mínima |
|----------|----------------|-------------|
| WORKFLOW - FLUX TXT2IMG (yt) | L4 | 16 GB |
| WORKFLOW - FLUX IMG2IMG + LORA | L4 | 16 GB |
| WORKFLOW - FLUX QTZ + LORA | L4 | 16 GB |
| WORKFLOW - FLUX INPAINT | L4 | 16 GB |
| WORKFLOW - FLUX OUTPAINT | L4 | 16 GB |
| WORKFLOW - FLUX REDUX | L4 | 16 GB |
| WORKFLOW - FLUX KONTEXT | L4 | 16 GB |
| WORKFLOW - FLUX KREA | L4 | 16 GB |
| WORKFLOW - FLUX UNION (CONTROL NET) | L4 | 24 GB |
| WORKFLOW - FLUX USO | L4 | 16 GB |
| WORKFLOW - HIDREAM | L4 | 24 GB |

#### 🖼️ **Geração de Imagem (FLUX2 / Outros)**
| Workflow | GPU Recomendada | VRAM Mínima |
|----------|----------------|-------------|
| WORKFLOW - FLUX2 KLEIN | **L40S** | 48 GB |
| WORKFLOW - FLUX2 TXT2IMG QTZ | **L40S** | 48 GB |
| WORKFLOW - FLUX2 REF2IMG QTZ | **L40S** | 48 GB |
| WORKFLOW - TXT2IMG BÁSICO | L4 | 12 GB |
| WORKFLOW - TXT2IMG BÁSICO + LORA | L4 | 12 GB |
| WORKFLOW - TXT2IMG BÁSICO + POWERLORA | L4 | 12 GB |
| WORKFLOW - TXT2IMG + INPAINT | L4 | 12 GB |
| WORKFLOW - TXT2IMG + PROMPT BATCH | L4 | 12 GB |
| WORKFLOW - Z-IMAGE TXT2IMG | L4 | 12 GB |
| WORKFLOW - Z IMAGE TURBO TXT2IMG+LORA | L4 | 12 GB |
| WORKFLOW - Z IMAGE UNION | L4 | 16 GB |
| WORKFLOW - IMG2IMG | L4 | 12 GB |
| WORKFLOW - CHARACTER INFLUENCER FLUX | L4 | 24 GB |
| WORKFLOW - ARCH STYLE | L4 | 12 GB |
| WORKFLOW - PRODUCT PHOTO | L4 | 16 GB |
| WORKFLOW - IMAGE RESTYLE (GHIBLI) | L4 | 16 GB |
| WORKFLOW - SEAMLESS TILING | L4 | 12 GB |
| WORKFLOW - QWEN TXT2IMG | L4 | 16 GB |
| WORKFLOW - QWEN CRIATIVOS | L4 | 16 GB |
| WORKFLOW - QWEN IMG EDIT | L4 | 16 GB |
| WORKFLOW - QWEN INPAINT | L4 | 16 GB |
| WORKFLOW - QWEN IMAGE EDIT RELIGHT | L4 | 16 GB |
| WORKFLOW - QWEN IMAGE LAYERED | L4 | 16 GB |
| WORKFLOW - QWEN NEXT SCENE | L4 | 16 GB |
| WORKFLOW - QWEN MULTI ANGLE | L4 | 16 GB |
| WORKFLOW - INSANE UPSCALE | L4 | 16 GB |
| WORKFLOW - RELIGHT | L4 | 12 GB |
| WORKFLOW - SEGMENT ANYTHING | L4 | 8 GB |
| WORKFLOW - IPADAPTER | L4 | 16 GB |
| WORKFLOW - CONTROL NET | L4 | 12 GB |
| WORKFLOW - CATVTON | L4 | 16 GB |

#### 🎬 **Geração de Vídeo (LTX-2)**
| Workflow | GPU Recomendada | VRAM Mínima |
|----------|----------------|-------------|
| WORKFLOW - LTX2 TXT2VID | L4 | 24 GB |
| WORKFLOW - LTX2 IMG2VID | L4 | 24 GB |
| WORKFLOW - LTX2 POSE2VID | L4 | 24 GB |
| WORKFLOW - LTX IMG2VID | L4 | 16 GB |
| WORKFLOW - LTX TXT2VID | L4 | 16 GB |

#### 🎬 **Geração de Vídeo (Wan 2.1 / 2.2)**
| Workflow | GPU Recomendada | VRAM Mínima |
|----------|----------------|-------------|
| WORKFLOW - WAN IMG2VID | L40S | 24 GB+ |
| WORKFLOW - WAN 2.2 ANIMATE | L40S | 24 GB+ |
| WORKFLOW - WAN 2.2 VIDEO UPSCALE | L40S | 24 GB+ |
| WORKFLOW - WAN2.2 IMG2VID | L40S | 24 GB+ |
| WORKFLOW - WAN2.2 TXT2VID | L40S | 24 GB+ |
| WORKFLOW - WAN2.2 INFINITE VIDEO | L40S | 48 GB |
| WORKFLOW - WAN2.2 FLF2V | L40S | 24 GB+ |
| WORKFLOW - WAN ALPHA | L40S | 24 GB+ |
| WORKFLOW - WAN ATI | L40S | 24 GB+ |
| WORKFLOW - WAN DEPTH | L40S | 24 GB+ |
| WORKFLOW - WAN FUN CONTROL | L40S | 24 GB+ |
| WORKFLOW - WAN OVI | L40S | 24 GB+ |
| WORKFLOW - WAN PHANTOM | L40S | 24 GB+ |
| WORKFLOW - WAN VACE CONTROL VIDEO | L40S | 24 GB+ |
| WORKFLOW - WAN VACE INPAINT | L40S | 24 GB+ |
| WORKFLOW - HUNYUAN TXT2VID | L40S | 48 GB |
| WORKFLOW - HUNYUAN LOOM VID2VID | L40S | 48 GB |
| WORKFLOW - LOGO ANIMATING | L4 | 16 GB |
| WORKFLOW - RECAMMASTER | L40S | 24 GB+ |
| WORKFLOW - VIDEO UPSCALE BASICO | L4 | 12 GB |
| WORKFLOW - MINIMAX REMOVER BMO | L4 | 16 GB |

#### 👄 **Lip Sync / Talking Head**
| Workflow | GPU Recomendada | VRAM Mínima |
|----------|----------------|-------------|
| WORKFLOW - INFINITE TALK | L40S | 48 GB |
| WORKFLOW - INFINITE TALK V2V | L40S | 48 GB |
| WORKFLOW - MULTI TALK | L40S | 48 GB |
| WORKFLOW - SONIC LIPSYNC | L4 | 16 GB |

#### 🎵 **Áudio / Outros**
| Workflow | GPU Recomendada | VRAM Mínima |
|----------|----------------|-------------|
| WORKFLOW - ACE STEP | L4 | 16 GB |
| WORKFLOW - ACE STEP 1.5 | L4 | 16 GB |
| WORKFLOW - FACE SWAP | L4 | 12 GB |
| WORKFLOW - 3D+KONTEXT | L40S | 48 GB |
| WORKFLOW - HUNYUAN 3D | L40S | 48 GB |
| WORKFLOW - APLICAÇÃO DE LUTS EM MASSA | L4 | CPU |

---

## 🎯 Stack Recomendado para Automação

### 🥇 Melhor Custo-Benefício: L4 (24GB VRAM)

| Função | Workflow | Modelo |
|--------|----------|--------|
| **Geração de Imagem** | FLUX QTZ + LORA | FLUX.1 Dev FP8 |
| **Vídeo T2V / I2V** | LTX2 TXT2VID / IMG2VID | LTX-2 FP8 |
| **Lip Sync** | SONIC LIPSYNC | SonicSAM / LatentSync |
| **Upscale** | INSANE UPSCALE | Real-ESRGAN |

### 🥈 Para Wan 2.2 Avançado: L40S (48GB VRAM)

| Função | Workflow | Observação |
|--------|----------|------------|
| **Vídeo longo** | WAN 2.2 ANIMATE | Usa LoRA 4-steps |
| **Vídeo I2V** | WAN2.2 IMG2VID | Alta qualidade |
| **Lip Sync avançado** | MULTI TALK | Multi falantes |
