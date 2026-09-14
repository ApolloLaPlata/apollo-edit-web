
with open('apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re

# We will cut lines 87-101 (indexes 87 to 101)
cut_lines = lines[87:102]
lines_without_cut = lines[:87] + lines[102:]

# Find where 'app = FastAPI' is now in lines_without_cut
insert_idx = -1
for i, line in enumerate(lines_without_cut):
    if 'app = FastAPI(' in line:
        insert_idx = i + 1
        break

if insert_idx != -1:
    lines_without_cut = lines_without_cut[:insert_idx] + cut_lines + lines_without_cut[insert_idx:]

with open('apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.writelines(lines_without_cut)

