import re

with open("backend/cloud_tools/engines/apollo_arena_comfy_engine.py", "r", encoding="utf-8") as f:
    arena = f.read()

flag_code = """        if not server_up:
            print("Timeout waiting for ComfyUI to start")
        else:
            with open("/tmp/modal_snapshot_done", "w") as f_snap:
                f_snap.write("done")
            print("[ArenaComfyEngine] Flag /tmp/modal_snapshot_done criada com sucesso!")"""

arena = re.sub(r"        if not server_up:\n            print\(\"Timeout waiting for ComfyUI to start\"\)", flag_code, arena)

with open("backend/cloud_tools/engines/apollo_arena_comfy_engine.py", "w", encoding="utf-8") as f:
    f.write(arena)

print("Flag patch applied!")
