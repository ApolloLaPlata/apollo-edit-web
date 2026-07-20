import json

workflow = {
  "9": {
    "inputs": {
      "filename_prefix": "Flux2_Banana",
      "images": ["68:8", 0]
    },
    "class_type": "SaveImage"
  },
  "45": {
    "inputs": {
      "upscale_method": "lanczos",
      "megapixels": 1.0,
      "resolution_steps": 1,
      "image": ["46", 0]
    },
    "class_type": "ImageScaleToTotalPixels"
  },
  "46": {
    "inputs": {
      "image": "image_flux2_input_image.png"
    },
    "class_type": "LoadImage"
  },
  "68:48": {
    "inputs": {
      "scheduler": "simple",
      "steps": 8,
      "denoise": 1.0,
      "model": ["68:89", 0]
    },
    "class_type": "BasicScheduler"
  },
  "68:22": {
    "inputs": {
      "model": ["68:89", 0],
      "conditioning": ["68:43", 0]
    },
    "class_type": "BasicGuider"
  },
  "68:16": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect"
  },
  "68:10": {
    "inputs": {
      "vae_name": "full_encoder_small_decoder.safetensors"
    },
    "class_type": "VAELoader"
  },
  "68:13": {
    "inputs": {
      "noise": ["68:25", 0],
      "guider": ["68:22", 0],
      "sampler": ["68:16", 0],
      "sigmas": ["68:48", 0],
      "latent_image": ["68:47", 0]
    },
    "class_type": "SamplerCustomAdvanced"
  },
  "68:6": {
    "inputs": {
      "text": "Prompt text",
      "clip": ["68:38", 0]
    },
    "class_type": "CLIPTextEncode"
  },
  "68:38": {
    "inputs": {
      "clip_name": "mistral_3_small_flux2_bf16.safetensors",
      "type": "flux2",
      "device": "default"
    },
    "class_type": "CLIPLoader"
  },
  "68:25": {
    "inputs": {
      "noise_seed": 42
    },
    "class_type": "RandomNoise"
  },
  "68:8": {
    "inputs": {
      "samples": ["68:13", 0],
      "vae": ["68:10", 0]
    },
    "class_type": "VAEDecode"
  },
  "68:26": {
    "inputs": {
      "guidance": 3.5,
      "conditioning": ["68:6", 0]
    },
    "class_type": "FluxGuidance"
  },
  "68:12": {
    "inputs": {
      "unet_name": "flux2_dev_fp8mixed.safetensors",
      "weight_dtype": "default"
    },
    "class_type": "UNETLoader"
  },
  "68:44": {
    "inputs": {
      "pixels": ["45", 0],
      "vae": ["68:10", 0]
    },
    "class_type": "VAEEncode"
  },
  "68:43": {
    "inputs": {
      "conditioning": ["68:26", 0],
      "latent": ["68:44", 0]
    },
    "class_type": "ReferenceLatent"
  },
  "68:89": {
    "inputs": {
      "lora_name": "Flux_2-Turbo-LoRA_comfyui.safetensors",
      "strength_model": 1.0,
      "model": ["68:12", 0]
    },
    "class_type": "LoraLoaderModelOnly"
  },
  "68:47": {
    "inputs": {
      "width": 768,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyFlux2LatentImage"
  }
}

import codecs
with codecs.open('Comfyui Workflow API/image_flux2/image_flux2.json', 'w', 'utf-8') as f:
    json.dump(workflow, f, indent=2)

print('Workflow RESTAURADO para o Nano Banana original (EmptyLatent + ReferenceLatent + LoRA Turbo)!')
