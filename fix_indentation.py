import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("if server_up:"):
            indent = line[:len(line) - len(line.lstrip())]
            new_lines.append(line)
            i += 1
            # Check if next line is already our flag creation
            while i < len(lines) and ("modal_snapshot_done" in lines[i] or "SNAPSHOT V_HTTP OK" in lines[i] or "Servidor aguardando" in lines[i] or "t2_boot_time =" in lines[i] or "t_boot_end -" in lines[i]):
                i += 1
            # Re-insert cleanly with exact indent + 4 spaces
            sub_indent = indent + "    "
            new_lines.append(f'{sub_indent}with open("/tmp/modal_snapshot_done", "w") as f_snap:\n')
            new_lines.append(f'{sub_indent}    f_snap.write("done")\n')
            new_lines.append(f'{sub_indent}print("[Snapshot] Flag /tmp/modal_snapshot_done criada com sucesso!")\n')
            if "universal_engine.py" in f:
                new_lines.append(f'{sub_indent}t2_boot_time = time.perf_counter() - t_boot_start\n')
                new_lines.append(f'{sub_indent}print(f"[UniversalComfyEngine] SNAPSHOT V_HTTP OK! ComfyUI porta 8189 pronto em {{t2_boot_time:.2f}}s.")\n')
            elif "flux_engine.py" in f:
                new_lines.append(f'{sub_indent}print("[Flux2ComfyEngine_V2] SNAPSHOT V_HTTP OK! ComfyUI porta 8189 pronto.")\n')
            elif "flux_txt2img_engine.py" in f:
                new_lines.append(f'{sub_indent}print("[Flux2Txt2ImgEngine] Servidor aguardando requisições.")\n')
        else:
            new_lines.append(line)
            i += 1

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.writelines(new_lines)
    print(f"Fixed indentation in {f}!")
