import json

workflow = {
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
  "11": {
    "inputs": {
      "pixels": [
        "45",
        0
      ],
      "vae": [
        "10",
        0
      ]
    },
    "class_type": "VAEEncode"
  },
  "45": {
    "inputs": {
      "upscale_method": "lanczos",
      "megapixels": 1,
      "resolution_steps": 1,
      "image": [
        "16",
        0
      ]
    },
    "class_type": "ImageScaleToTotalPixels"
  },
  "38": {
    "inputs": {
      "clip_name": "mistral_3_small_flux2_bf16.safetensors",
      "type": "flux2",
      "device": "default"
    },
    "class_type": "CLIPLoader"
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
  "26": {
    "inputs": {
      "guidance": 3.5,
      "conditioning": [
        "6",
        0
      ]
    },
    "class_type": "FluxGuidance"
  },
  "22": {
    "inputs": {
      "model": [
        "12",
        0
      ],
      "conditioning": [
        "26",
        0
      ]
    },
    "class_type": "BasicGuider"
  },
  "48": {
    "inputs": {
      "scheduler": "simple",
      "steps": 20,
      "denoise": 0.45,
      "model": [
        "12",
        0
      ]
    },
    "class_type": "BasicScheduler"
  },
  "16_sampler": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect"
  },
  "25": {
    "inputs": {
      "noise_seed": 42
    },
    "class_type": "RandomNoise"
  },
  "13": {
    "inputs": {
      "noise": [
        "25",
        0
      ],
      "guider": [
        "22",
        0
      ],
      "sampler": [
        "16_sampler",
        0
      ],
      "sigmas": [
        "48",
        0
      ],
      "latent_image": [
        "11",
        0
      ]
    },
    "class_type": "SamplerCustomAdvanced"
  },
  "8": {
    "inputs": {
      "samples": [
        "13",
        0
      ],
      "vae": [
        "10",
        0
      ]
    },
    "class_type": "VAEDecode"
  }
}

with open('Comfyui Workflow API/image_flux2/image_flux2.json', 'w') as f:
    json.dump(workflow, f, indent=2)

print('Workflow configured for Pure Img2Img with SamplerCustomAdvanced (Flux)!')
