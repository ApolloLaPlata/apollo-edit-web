"""
Patch DEFINITIVO para integração PuLID-Flux no ComfyUI moderno.

PROBLEMAS:
1. pulidflux.py: forward_orig não aceita **kwargs
2. pulidflux.py: vec = vec + self.vector_in(y) quebra
3. pulidflux.py: global_modulation mudou (separado em img e txt)
"""
import os
import ast
import re

pulid_path = "/comfyui/custom_nodes/ComfyUI-PuLID-Flux/pulidflux.py"

with open(pulid_path, "r") as f:
    pulid = f.read()

# Patch 1: **kwargs
if "**kwargs" not in re.search(r"def forward_orig.*?\) -> Tensor:", pulid, re.DOTALL).group(0) if re.search(r"def forward_orig.*?\) -> Tensor:", pulid, re.DOTALL) else "**kwargs":
    def add_kwargs(m):
        full = m.group(0)
        closing = re.search(r'\)\s*->\s*Tensor\s*:', full)
        if closing:
            insert_pos = full.rfind('\n', 0, closing.start())
            if insert_pos >= 0:
                prev_line = full[full.rfind('\n', 0, insert_pos) + 1:insert_pos]
                indent = len(prev_line) - len(prev_line.lstrip())
                indent_str = " " * indent
                new_full = full[:insert_pos] + f"\n{indent_str}**kwargs," + full[insert_pos:]
                return new_full
        return full
    pulid = re.sub(r"def forward_orig.*?\) -> Tensor:", add_kwargs, pulid, count=1, flags=re.DOTALL)
    print("\n[PATCH] pulidflux.py — **kwargs adicionado.")

# Patch 2: vector_in guard
vec_pattern = r'(\s+)(vec = vec \+ self\.vector_in\(y\))'
vec_replacement = r'\1if getattr(self, "vector_in", None) is not None and y is not None:\n\1    \2'
pulid = re.sub(vec_pattern, vec_replacement, pulid, count=1)
print("\n[PATCH] pulidflux.py — vector_in guard adicionado.")

# Patch 3: global_modulation double
double_loop = r"(for [^:]* in self\.double_blocks:.*?)(img, txt = block\(img=img, txt=txt, vec=vec, pe=pe\))"
double_rep = (
    r"transformer_options = kwargs.get('transformer_options', {})\n"
    r"    attn_mask = kwargs.get('attn_mask', None)\n"
    r"    vec_orig = vec\n"
    r"    txt_vec = vec\n"
    r"    if getattr(self.params, 'global_modulation', False) and hasattr(self, 'double_stream_modulation_img'):\n"
    r"        vec = (self.double_stream_modulation_img(vec_orig), self.double_stream_modulation_txt(txt_vec))\n"
    r"    \1img, txt = block(img=img, txt=txt, vec=vec, pe=pe, attn_mask=attn_mask, transformer_options=transformer_options)"
)
pulid = re.sub(double_loop, double_rep, pulid, count=1, flags=re.DOTALL)

# Patch 4: global_modulation single
single_loop = r"(for [^:]* in self\.single_blocks:.*?)(img = block\(img, vec=vec, pe=pe\))"
single_rep = (
    r"if getattr(self.params, 'global_modulation', False) and hasattr(self, 'single_stream_modulation'):\n"
    r"        vec, _ = self.single_stream_modulation(vec_orig)\n"
    r"    \1img = block(img, vec=vec, pe=pe, attn_mask=attn_mask, transformer_options=transformer_options)"
)
pulid = re.sub(single_loop, single_rep, pulid, count=1, flags=re.DOTALL)

# Patch 5: final_layer
final_layer_pat = r"img = self\.final_layer\(img, vec\)"
final_layer_rep = r"img = self.final_layer(img, vec_orig if getattr(self.params, 'global_modulation', False) else vec)"
pulid = re.sub(final_layer_pat, final_layer_rep, pulid, count=1)

print("\n[PATCH] pulidflux.py — global_modulation completo.")

ast.parse(pulid)
with open(pulid_path, "w") as f:
    f.write(pulid)

print("\n[PATCH] Todos os patches concluídos com sucesso.")
