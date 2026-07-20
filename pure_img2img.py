import json

workflow = {
  "3": {
    "inputs": {
      "seed": 42,
      "steps": 20,
      "cfg": 1.0,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 0.5,
      "model": [
        "12",
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
        "11",
        0
      ]
    },
    "class_type": "KSampler"
  },
  "6": {
    "inputs": {
      "text": "Prompt text",
      "clip": [
        "38",
        0
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "7": {
    "inputs": {
      "text": "",
      "clip": [
        "38",
        0
      ]
    },
    "class_type": "CLIPTextEncode"
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "10",
        0
      ]
    },
    "class_type": "VAEDecode"
  },
  "9": {
    "inputs": {
      "filename_prefix": "Flux2_Img2Img",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage"
  },
  "10": {
    "inputs": {
      "vae_name": "full_encoder_small_decoder.safetensors"
    },
    "class_type": "VAELoader"
  },
  "11": {
    "inputs": {
      "pixels": [
        "16",
        0
      ],
      "vae": [
        "10",
        0
      ]
    },
    "class_type": "VAEEncode"
  },
  "12": {
    "inputs": {
      "unet_name": "flux2_dev_fp8mixed.safetensors",
      "weight_dtype": "default"
    },
    "class_type": "UNETLoader"
  },
  "16": {
    "inputs": {
      "image": "image_flux2_input_image.png"
    },
    "class_type": "LoadImage"
  },
  "38": {
    "inputs": {
      "clip_name": "mistral_3_small_flux2_bf16.safetensors",
      "type": "flux2",
      "device": "default"
    },
    "class_type": "CLIPLoader"
  }
}

with open('Comfyui Workflow API/image_flux2/image_flux2.json', 'w') as f:
    json.dump(workflow, f, indent=2)

print('Workflow configured for Pure, Simple Img2Img with KSampler!')
