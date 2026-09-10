import torch
from diffusers import LTXPipeline, LTXImageToVideoPipeline
pipe = LTXPipeline.from_pretrained('diffusers/LTX-2.3-Distilled-Diffusers', torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()
pipe2 = LTXImageToVideoPipeline.from_pipe(pipe)
print('pipe device:', pipe.device, 'execution:', getattr(pipe, '_execution_device', None))
print('pipe2 device:', pipe2.device, 'execution:', getattr(pipe2, '_execution_device', None))

