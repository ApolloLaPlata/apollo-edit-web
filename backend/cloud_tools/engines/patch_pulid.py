import os

filepath = '/comfyui/custom_nodes/ComfyUI-PuLID-Flux/pulidflux.py'
with open(filepath, 'r') as f:
    code = f.read()

# Fix 1: signature
code = code.replace('control=None,\n) -> Tensor:', 'control=None,\n    **kwargs\n) -> Tensor:')

# Fix 2: vector_in NoneType
old_vector_in = '    vec = vec + self.vector_in(y)'
new_vector_in = '''    if getattr(self, 'vector_in', None) is not None:
        if y is None:
            import torch as _torch
            y = _torch.zeros((img.shape[0], self.params.vec_in_dim), device=img.device, dtype=img.dtype)
        vec = vec + self.vector_in(y[:, :self.params.vec_in_dim])'''
code = code.replace(old_vector_in, new_vector_in)

# Fix 3: global_modulation and timestep_zero_index (ComfyUI updates)
old_pe = '    pe = self.pe_embedder(ids)'
new_pe = '''    pe = self.pe_embedder(ids)
    
    vec_orig = vec
    txt_vec = vec
    extra_kwargs = {}
    if kwargs.get('timestep_zero_index', None) is not None:
        batch = img.shape[0]
        modulation_dims = []
        for s in kwargs['timestep_zero_index']:
            modulation_dims.append((s[0], s[1], 1))
        extra_kwargs['modulation_dims_img'] = modulation_dims
        txt_vec = vec[:batch]

    if getattr(self.params, 'global_modulation', False):
        vec = (self.double_stream_modulation_img(vec_orig), self.double_stream_modulation_txt(txt_vec))
'''
code = code.replace(old_pe, new_pe)

# Fix 4: passing extra_kwargs to blocks
code = code.replace('img, txt = block(img=img, txt=txt, vec=vec, pe=pe)', 'img, txt = block(img=img, txt=txt, vec=vec, pe=pe, **extra_kwargs)')

with open(filepath, 'w') as f:
    f.write(code)
