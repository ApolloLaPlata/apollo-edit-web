
export const PROJECT_COLORS = [
  { id: 'blue', class: 'bg-blue-500', text: 'text-blue-400', border: 'border-blue-500' },
  { id: 'purple', class: 'bg-purple-500', text: 'text-purple-400', border: 'border-purple-500' },
  { id: 'emerald', class: 'bg-emerald-500', text: 'text-emerald-400', border: 'border-emerald-500' },
  { id: 'rose', class: 'bg-rose-500', text: 'text-rose-400', border: 'border-rose-500' },
  { id: 'amber', class: 'bg-amber-500', text: 'text-amber-400', border: 'border-amber-500' },
  { id: 'cyan', class: 'bg-cyan-500', text: 'text-cyan-400', border: 'border-cyan-500' },
  { id: 'slate', class: 'bg-slate-500', text: 'text-slate-400', border: 'border-slate-500' },
];

export const PROJECT_ICONS = [
  'Layout', 'Video', 'Gamepad2', 'BookOpen', 'Music', 'Camera', 'Palette', 'MonitorPlay', 'Smartphone', 'Newspaper', 'Sword', 'Ghost'
];

export const ASPECT_RATIOS = [
  { label: 'Quadrado (1:1)', value: '1:1' },
  { label: 'Paisagem (16:9)', value: '16:9' },
  { label: 'Retrato (9:16)', value: '9:16' },
  { label: 'Paisagem (4:3)', value: '4:3' },
  { label: 'Retrato (3:4)', value: '3:4' },
  { label: 'Ultra Panorâmico (4:1)', value: '4:1' },
  { label: 'Arranha-Céu (1:4)', value: '1:4' },
];

export const MODELS = [
  { id: 'gemini-3.1-flash-image-preview', name: 'Gemini 3.1 Flash Image (Nano Banana 2 - Requer Acesso/Pago)' },
  { id: 'gemini-2.5-flash-image', name: 'Gemini 2.5 Flash Image (Gratuito & Rápido)' },
  { id: 'gemini-3.1-pro-image-preview', name: 'Gemini 3.1 Pro Image (Alta Qualidade - Pago)' },
];

export const VISUAL_STYLES = [
  { id: 'none', label: 'Nenhum (Prompt Puro)' },
  { id: 'dark_fantasy', label: 'Fantasia Sombria (Estilo Elden Ring)' },
  { id: 'cinematic', label: 'Cinematográfico Realista (Filme)' },
  { id: 'anime', label: 'Anime / Mangá (Alta Fidelidade)' },
  { id: 'digital_art', label: 'Arte Digital (ArtStation)' },
  { id: 'oil_painting', label: 'Pintura a Óleo (Clássico)' },
  { id: 'cyberpunk', label: 'Cyberpunk / Neon' },
  { id: 'watercolor', label: 'Aquarela (Sketch)' },
  { id: 'pixar', label: 'Animação 3D (Estilo Pixar)' },
  { id: 'simpsons', label: 'Família Amarela (Cartoon)' },
  { id: 'retro_80s', label: 'Retro 80s Synthwave' },
  { id: 'horror', label: 'Horror Analógico / VHS' },
];

export const THUMBNAIL_STYLES = [
  { id: 'mrbeast', label: 'Alto Contraste / Viral (Estilo MrBeast)', prompt: 'High saturation, expressive face close-up, bright background, bold outcome' },
  { id: 'tech_review', label: 'Review Tech (MKBHD/The Verge)', prompt: 'Clean, minimalist, product focus, matte background, professional lighting' },
  { id: 'gaming', label: 'Gaming / Gameplay', prompt: 'Action packed, vibrant neon colors, game assets, dramatic lighting, 3D text' },
  { id: 'vlog', label: 'Vlog Lifestyle', prompt: 'Natural lighting, bright, warm tones, authentic expression, blurred background' },
  { id: 'educational', label: 'Educacional / Explainer', prompt: 'Vector illustrations, flat design, clean typography, split screen comparison' },
  { id: 'podcast', label: 'Podcast / Entrevista', prompt: 'Professional studio lighting, dark elegant background, subject focus' },
  { id: 'horror_story', label: 'Terror / True Crime', prompt: 'Dark, vignette, high contrast, red highlights, mysterious atmosphere' },
];

export const DEFAULT_SETTINGS = {
  aspectRatio: '16:9',
  modelId: 'gemini-2.5-flash-image',
  imageSize: '1K',
  useThinking: false,
  delayBetweenRequests: 2000, // 2 seconds default delay
  useStoryContinuity: false,
  globalContext: '',
  sceneContext: '',
  generateVideoPrompt: false,
  negativePrompt: '',
  useGrounding: false,
  styleReferenceImage: undefined,
  textProvider: 'gemini',
  imageProvider: 'gemini',
  videoProvider: 'gemini',
  comfyUrl: 'http://127.0.0.1:8188',
  openRouterTextModel: 'arcee-ai/trinity-large-preview:free',
  comfyWorkflows: [
    {
      id: 'comfyui-basic-default',
      name: 'ComfyUI Básico (Garrafa Roxa)',
      type: 'image',
      category: 'Básico',
      json: JSON.stringify({
        "3": {
          "inputs": {
            "seed": 156680208700286,
            "steps": 20,
            "cfg": 8,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": [
              "4",
              0
            ],
            "positive": [
              "6",
              0
            ],
            "negative": [
              "7",
              0
            ],
            "latent_image": [
              "5",
              0
            ]
          },
          "class_type": "KSampler",
          "_meta": {
            "title": "KSampler"
          }
        },
        "4": {
          "inputs": {
            "ckpt_name": "v1-5-pruned-emaonly-fp16.safetensors"
          },
          "class_type": "CheckpointLoaderSimple",
          "_meta": {
            "title": "Carregar Checkpoint"
          }
        },
        "5": {
          "inputs": {
            "width": 512,
            "height": 512,
            "batch_size": 1
          },
          "class_type": "EmptyLatentImage",
          "_meta": {
            "title": "Imagem Latente Vazia"
          }
        },
        "6": {
          "inputs": {
            "text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
            "clip": [
              "4",
              1
            ]
          },
          "class_type": "CLIPTextEncode",
          "_meta": {
            "title": "Codificação de Texto CLIP (Prompt)"
          }
        },
        "7": {
          "inputs": {
            "text": "text, watermark",
            "clip": [
              "4",
              1
            ]
          },
          "class_type": "CLIPTextEncode",
          "_meta": {
            "title": "Codificação de Texto CLIP (Prompt)"
          }
        },
        "8": {
          "inputs": {
            "samples": [
              "3",
              0
            ],
            "vae": [
              "4",
              2
            ]
          },
          "class_type": "VAEDecode",
          "_meta": {
            "title": "VAE Decodificar"
          }
        },
        "9": {
          "inputs": {
            "filename_prefix": "ComfyUI",
            "images": [
              "8",
              0
            ]
          },
          "class_type": "SaveImage",
          "_meta": {
            "title": "Salvar Imagem"
          }
        }
      })
    },
    {
      id: 'flux-2-dev-default',
      name: 'Flux.2 Dev (Padrão)',
      type: 'image',
      category: 'Flux',
      json: JSON.stringify({
        "9": {
          "inputs": {
            "filename_prefix": "Flux2",
            "images": [
              "68:8",
              0
            ]
          },
          "class_type": "SaveImage",
          "_meta": {
            "title": "Save Image"
          }
        },
        "45": {
          "inputs": {
            "upscale_method": "lanczos",
            "megapixels": 1,
            "resolution_steps": 1,
            "image": [
              "46",
              0
            ]
          },
          "class_type": "ImageScaleToTotalPixels",
          "_meta": {
            "title": "ImageScaleToTotalPixels"
          }
        },
        "46": {
          "inputs": {
            "image": "ae83038684b58b03a94525d302a5966b9147f3ccd0ff29efdc90371521e16707.jpg"
          },
          "class_type": "LoadImage",
          "_meta": {
            "title": "Load Image"
          }
        },
        "68:48": {
          "inputs": {
            "steps": [
              "68:93",
              0
            ],
            "width": [
              "68:72",
              0
            ],
            "height": [
              "68:72",
              1
            ]
          },
          "class_type": "Flux2Scheduler",
          "_meta": {
            "title": "Flux2Scheduler"
          }
        },
        "68:22": {
          "inputs": {
            "model": [
              "68:92",
              0
            ],
            "conditioning": [
              "68:43",
              0
            ]
          },
          "class_type": "BasicGuider",
          "_meta": {
            "title": "BasicGuider"
          }
        },
        "68:16": {
          "inputs": {
            "sampler_name": "euler"
          },
          "class_type": "KSamplerSelect",
          "_meta": {
            "title": "KSamplerSelect"
          }
        },
        "68:10": {
          "inputs": {
            "vae_name": "flux2-vae.safetensors"
          },
          "class_type": "VAELoader",
          "_meta": {
            "title": "Load VAE"
          }
        },
        "68:13": {
          "inputs": {
            "noise": [
              "68:25",
              0
            ],
            "guider": [
              "68:22",
              0
            ],
            "sampler": [
              "68:16",
              0
            ],
            "sigmas": [
              "68:48",
              0
            ],
            "latent_image": [
              "68:47",
              0
            ]
          },
          "class_type": "SamplerCustomAdvanced",
          "_meta": {
            "title": "SamplerCustomAdvanced"
          }
        },
        "68:6": {
          "inputs": {
            "text": "personagem correndo no meio da floresta",
            "clip": [
              "68:38",
              0
            ]
          },
          "class_type": "CLIPTextEncode",
          "_meta": {
            "title": "CLIP Text Encode (Positive Prompt)"
          }
        },
        "68:38": {
          "inputs": {
            "clip_name": "mistral_3_small_flux2_bf16.safetensors",
            "type": "flux2",
            "device": "default"
          },
          "class_type": "CLIPLoader",
          "_meta": {
            "title": "Load CLIP"
          }
        },
        "68:25": {
          "inputs": {
            "noise_seed": 1077250302352238
          },
          "class_type": "RandomNoise",
          "_meta": {
            "title": "RandomNoise"
          }
        },
        "68:8": {
          "inputs": {
            "samples": [
              "68:13",
              0
            ],
            "vae": [
              "68:10",
              0
            ]
          },
          "class_type": "VAEDecode",
          "_meta": {
            "title": "VAE Decode"
          }
        },
        "68:26": {
          "inputs": {
            "guidance": 4,
            "conditioning": [
              "68:6",
              0
            ]
          },
          "class_type": "FluxGuidance",
          "_meta": {
            "title": "FluxGuidance"
          }
        },
        "68:89": {
          "inputs": {
            "lora_name": "Flux_2-Turbo-LoRA_comfyui.safetensors",
            "strength_model": 1,
            "model": [
              "68:12",
              0
            ]
          },
          "class_type": "LoraLoaderModelOnly",
          "_meta": {
            "title": "Load LoRA"
          }
        },
        "68:12": {
          "inputs": {
            "unet_name": "flux2_dev_fp8mixed.safetensors",
            "weight_dtype": "default"
          },
          "class_type": "UNETLoader",
          "_meta": {
            "title": "Load Diffusion Model"
          }
        },
        "68:92": {
          "inputs": {
            "switch": [
              "68:94",
              0
            ],
            "on_false": [
              "68:12",
              0
            ],
            "on_true": [
              "68:89",
              0
            ]
          },
          "class_type": "ComfySwitchNode",
          "_meta": {
            "title": "Switch(model)"
          }
        },
        "68:90": {
          "inputs": {
            "value": 8
          },
          "class_type": "PrimitiveInt",
          "_meta": {
            "title": "Steps"
          }
        },
        "68:91": {
          "inputs": {
            "value": 20
          },
          "class_type": "PrimitiveInt",
          "_meta": {
            "title": "Steps"
          }
        },
        "68:93": {
          "inputs": {
            "switch": [
              "68:94",
              0
            ],
            "on_false": [
              "68:91",
              0
            ],
            "on_true": [
              "68:90",
              0
            ]
          },
          "class_type": "ComfySwitchNode",
          "_meta": {
            "title": "Switch(steps)"
          }
        },
        "68:47": {
          "inputs": {
            "width": [
              "68:72",
              0
            ],
            "height": [
              "68:72",
              1
            ],
            "batch_size": 1
          },
          "class_type": "EmptyFlux2LatentImage",
          "_meta": {
            "title": "Empty Flux 2 Latent"
          }
        },
        "68:72": {
          "inputs": {
            "image": [
              "45",
              0
            ]
          },
          "class_type": "GetImageSize",
          "_meta": {
            "title": "Get Image Size"
          }
        },
        "68:44": {
          "inputs": {
            "pixels": [
              "45",
              0
            ],
            "vae": [
              "68:10",
              0
            ]
          },
          "class_type": "VAEEncode",
          "_meta": {
            "title": "VAE Encode"
          }
        },
        "68:43": {
          "inputs": {
            "conditioning": [
              "68:26",
              0
            ],
            "latent": [
              "68:44",
              0
            ]
          },
          "class_type": "ReferenceLatent",
          "_meta": {
            "title": "ReferenceLatent"
          }
        },
        "68:94": {
          "inputs": {
            "value": false
          },
          "class_type": "PrimitiveBoolean",
          "_meta": {
            "title": "Enable 8 steps lora"
          }
        }
      })
    }
  ],
  comfyImageWorkflow: JSON.stringify({
    "3": {
      "inputs": {
        "seed": 156680208700286,
        "steps": 20,
        "cfg": 8,
        "sampler_name": "euler",
        "scheduler": "normal",
        "denoise": 1,
        "model": [
          "4",
          0
        ],
        "positive": [
          "6",
          0
        ],
        "negative": [
          "7",
          0
        ],
        "latent_image": [
          "5",
          0
        ]
      },
      "class_type": "KSampler",
      "_meta": {
        "title": "KSampler"
      }
    },
    "4": {
      "inputs": {
        "ckpt_name": "v1-5-pruned-emaonly.ckpt"
      },
      "class_type": "CheckpointLoaderSimple",
      "_meta": {
        "title": "Load Checkpoint"
      }
    },
    "5": {
      "inputs": {
        "width": 512,
        "height": 512,
        "batch_size": 1
      },
      "class_type": "EmptyLatentImage",
      "_meta": {
        "title": "Empty Latent Image"
      }
    },
    "6": {
      "inputs": {
        "text": "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,",
        "clip": [
          "4",
          1
        ]
      },
      "class_type": "CLIPTextEncode",
      "_meta": {
        "title": "CLIP Text Encode (Positive Prompt)"
      }
    },
    "7": {
      "inputs": {
        "text": "text, watermark",
        "clip": [
          "4",
          1
        ]
      },
      "class_type": "CLIPTextEncode",
      "_meta": {
        "title": "CLIP Text Encode (Negative Prompt)"
      }
    },
    "8": {
      "inputs": {
        "samples": [
          "3",
          0
        ],
        "vae": [
          "4",
          2
        ]
      },
      "class_type": "VAEDecode",
      "_meta": {
        "title": "VAE Decode"
      }
    },
    "9": {
      "inputs": {
        "filename_prefix": "ComfyUI",
        "images": [
          "8",
          0
        ]
      },
      "class_type": "SaveImage",
      "_meta": {
        "title": "Save Image"
      }
    }
  })
};

export const OPENROUTER_TEXT_MODELS = [
    // --- FREE TIER ---
    { id: 'liquid/lfm-40b:free', name: 'Liquid LFM 40B MoE (Raciocínio - Grátis)', isFree: true },
    { id: 'deepseek/deepseek-r1:free', name: 'DeepSeek R1 (Raciocínio - Grátis)', isFree: true },
    { id: 'arcee-ai/trinity-large-preview:free', name: 'Arcee Trinity (Storytelling - Grátis)', isFree: true },
    { id: 'stepfun/step-3.5-flash', name: 'Step 3.5 Flash (Rápido - Grátis)', isFree: true },
    
    // --- PAID / PREMIUM ---
    { id: 'google/gemini-2.0-flash-001', name: 'Gemini 2.0 Flash (OpenRouter - Baixo Custo)', isFree: false },
    { id: 'x-ai/grok-2-vision-1212', name: 'Grok 2 Vision (xAI - Pago)', isFree: false },
    { id: 'openai/gpt-4o', name: 'GPT-4o (OpenAI - Pago)', isFree: false },
    { id: 'anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet (Qualidade Max - Pago)', isFree: false },
];