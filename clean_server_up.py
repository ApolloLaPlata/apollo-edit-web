import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Match from "if server_up:" up to "@modal.method()"
    pattern = r'if server_up:[\s\S]+?@modal\.method\(\)'

    if 'universal_engine.py' in f:
        new_block = '''if server_up:
                with open("/tmp/modal_snapshot_done", "w") as f_snap:
                    f_snap.write("done")
                print("[Snapshot] Flag /tmp/modal_snapshot_done criada com sucesso!")
                t2_boot_time = time.perf_counter() - t_boot_start
                print(f"[UniversalComfyEngine] SNAPSHOT V_HTTP OK! ComfyUI porta 8189 pronto em {t2_boot_time:.2f}s.")
            else:
                raise RuntimeError("[UniversalComfyEngine] Timeout no boot do ComfyUI para snapshot.")

    @modal.method()'''
    elif 'flux_engine.py' in f:
        new_block = '''if server_up:
                with open("/tmp/modal_snapshot_done", "w") as f_snap:
                    f_snap.write("done")
                print("[Snapshot] Flag /tmp/modal_snapshot_done criada com sucesso!")
                print("[Flux2ComfyEngine_V2] SNAPSHOT V_HTTP OK! ComfyUI porta 8189 pronto.")
            else:
                raise RuntimeError("[Flux2ComfyEngine_V2] Timeout no boot do ComfyUI para snapshot.")

    @modal.method()'''
    elif 'flux_txt2img_engine.py' in f:
        new_block = '''if server_up:
                with open("/tmp/modal_snapshot_done", "w") as f_snap:
                    f_snap.write("done")
                print("[Snapshot] Flag /tmp/modal_snapshot_done criada com sucesso!")
                print("[Flux2Txt2ImgEngine] Servidor aguardando requisições.")
            else:
                raise RuntimeError("Falha no boot do ComfyUI no tempo limite.")

    @modal.method()'''

    content, count = re.subn(pattern, new_block, content)
    print(f"Replaced server_up in {f} ({count} matches)")

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(content)
