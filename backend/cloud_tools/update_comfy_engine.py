import time
import os

TIMESTAMP_FILE = os.path.join(os.path.dirname(__file__), "comfy_update_timestamp.txt")

def trigger_update():
    current_time = str(int(time.time()))
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(current_time)
    print(f"[Sucesso] Timestamp de update do ComfyUI definido para: {current_time}")
    print("Agora execute o deploy para forçar a quebra de cache:")
    print("$env:PYTHONIOENCODING=\"utf-8\"; modal deploy -m backend.cloud_tools.apollo_modal_engine")

if __name__ == "__main__":
    trigger_update()
