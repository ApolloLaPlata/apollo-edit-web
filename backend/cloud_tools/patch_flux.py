with open('backend/cloud_tools/engines/flux_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
for i in range(len(lines)):
    if 'enable_memory_snapshot=True' in lines[i]:
        lines[i] = lines[i].replace('enable_memory_snapshot=True', 'enable_memory_snapshot=False')

start_idx = -1
end_idx = -1
for i in range(len(lines)):
    if 'print("[Flux2ComfyEngine_V2] Caching models into RAM' in lines[i]:
        start_idx = i
    if 'print("[Flux2ComfyEngine_V2] Caching finished!")' in lines[i]:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    lines = lines[:start_idx] + ['        print("[Flux2ComfyEngine_V2] Setup de paths concluído!")\n'] + lines[end_idx+1:]

with open('backend/cloud_tools/engines/flux_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Patch aplicado com sucesso no flux_engine.py!')
