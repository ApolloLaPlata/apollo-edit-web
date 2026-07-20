import base64

patch_script = """import os

filepath = '/comfyui/custom_nodes/ComfyUI-PuLID-Flux/pulidflux.py'
with open(filepath, 'r') as f:
    code = f.read()

code = code.replace(
    'control=None,\\n) -> Tensor:',
    'control=None,\\n    **kwargs\\n) -> Tensor:'
)

code = code.replace(
    '    vec = vec + self.vector_in(y)',
    '    if getattr(self, "vector_in", None) is not None:\\n        if y is None:\\n            import torch as _torch\\n            y = _torch.zeros((img.shape[0], self.params.vec_in_dim), device=img.device, dtype=img.dtype)\\n        vec = vec + self.vector_in(y[:, :self.params.vec_in_dim])'
)

old_pe = '    pe = self.pe_embedder(ids)'
new_pe = '''    pe = self.pe_embedder(ids)

    vec_orig = vec
    txt_vec = vec
    extra_kwargs = {}
    modulation_dims = []
    
    if kwargs.get('timestep_zero_index', None) is not None:
        timestep_zero_index = kwargs['timestep_zero_index']
        batch = vec.shape[0] // 2
        vec_orig = vec_orig.reshape(2, batch, vec.shape[1]).movedim(0, 1)
        
        inverted = []
        last = 0
        for s in timestep_zero_index:
            if s[0] > last:
                inverted.append((last, s[0]))
            last = s[1]
        if last < img.shape[1]:
            inverted.append((last, img.shape[1]))
            
        for s in inverted:
            modulation_dims.append((s[0], s[1], 0))
        for s in timestep_zero_index:
            modulation_dims.append((s[0], s[1], 1))
            
        extra_kwargs['modulation_dims_img'] = modulation_dims
        txt_vec = vec[:batch]

    if getattr(self.params, 'global_modulation', False):
        vec = (self.double_stream_modulation_img(vec_orig), self.double_stream_modulation_txt(txt_vec))
'''
code = code.replace(old_pe, new_pe)

code = code.replace(
    'img, txt = block(img=img, txt=txt, vec=vec, pe=pe)',
    'img, txt = block(img=img, txt=txt, vec=vec, pe=pe, **extra_kwargs)'
)

old_cat = '    img = torch.cat((txt, img), 1)'
new_cat = '''    img = torch.cat((txt, img), 1)

    if getattr(self.params, 'global_modulation', False):
        vec, _ = self.single_stream_modulation(vec_orig)

    if kwargs.get('timestep_zero_index', None) is not None:
        modulation_dims_combined = []
        for x in modulation_dims:
            new_x0 = 0 if x[0] == 0 else x[0] + txt.shape[1]
            new_x1 = x[1] + txt.shape[1]
            modulation_dims_combined.append((new_x0, new_x1, x[2]))
        extra_kwargs['modulation_dims'] = modulation_dims_combined
        if 'modulation_dims_img' in extra_kwargs:
            del extra_kwargs['modulation_dims_img']
'''
code = code.replace(old_cat, new_cat)

code = code.replace(
    'img = block(img, vec=vec, pe=pe)',
    'img = block(img, vec=vec, pe=pe, **extra_kwargs)'
)

debug_pulid_ca = "                        img = img + node_data['weight'] * self.pulid_ca[ca_idx](node_data['embedding'], img)"
debug_pulid_ca_new = "                        emb_shape = node_data['embedding'].shape\\n                        print('PULID_CA DEBUG: img shape =', img.shape, 'emb shape =', emb_shape)\\n                        img = img + node_data['weight'] * self.pulid_ca[ca_idx](node_data['embedding'], img)"
code = code.replace(debug_pulid_ca, debug_pulid_ca_new)

with open(filepath, 'w') as f:
    f.write(code)
"""

patch_b64 = base64.b64encode(patch_script.encode('utf-8')).decode('utf-8')
print(patch_b64)
