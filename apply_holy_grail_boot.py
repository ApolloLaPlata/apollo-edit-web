import re
import os

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

new_force_cpu_code = '''@contextmanager
def force_cpu_during_snapshot():
    import os
    import sys
    import torch

    # Garante que o arquivo indicador NÃƒO existe no inicio do boot CPU
    if os.path.exists("/tmp/modal_snapshot_done"):
        try:
            os.remove("/tmp/modal_snapshot_done")
        except Exception:
            pass

    mock_dir = "/tmp/mock_cuda"
    os.makedirs(mock_dir, exist_ok=True)
    site_path = os.path.join(mock_dir, "sitecustomize.py")
    with open(site_path, "w") as f:
        f.write(\'\'\'import os
import torch
_orig_is_available = getattr(torch.cuda, "is_available", lambda: False)
_orig_current_device = getattr(torch.cuda, "current_device", lambda: 0)
_orig_device_count = getattr(torch.cuda, "device_count", lambda: 0)

def _safe_is_available():
    # Durante a criacao do snapshot na CPU, o arquivo NÃƒO existe -> retorna False sem tocar na CUDA!
    if not os.path.exists("/tmp/modal_snapshot_done"):
        return False
    # Quando acorda na H100 GPU, o arquivo EXISTE -> retorna o status real da CUDA!
    try:
        return _orig_is_available()
    except Exception:
        return False

def _safe_current_device():
    if not _safe_is_available():
        return 0
    try:
        return _orig_current_device()
    except Exception:
        return 0

def _safe_device_count():
    if not _safe_is_available():
        return 0
    try:
        return _orig_device_count()
    except Exception:
        return 0

torch.cuda.is_available = _safe_is_available
torch.cuda.current_device = _safe_current_device
torch.cuda.device_count = _safe_device_count
print("[sitecustomize] Holy Grail CUDA fallback active for ComfyUI boot!")
\'\'\')

    old_pythonpath = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = f"{mock_dir}:{old_pythonpath}" if old_pythonpath else mock_dir

    orig_is_available = getattr(torch.cuda, "is_available", lambda: False)
    orig_current_device = getattr(torch.cuda, "current_device", lambda: 0)
    orig_device_count = getattr(torch.cuda, "device_count", lambda: 0)

    def safe_is_available():
        if not os.path.exists("/tmp/modal_snapshot_done"):
            return False
        try:
            return orig_is_available()
        except Exception:
            return False

    def safe_current_device():
        if not safe_is_available():
            return 0
        try:
            return orig_current_device()
        except Exception:
            return 0

    def safe_device_count():
        if not safe_is_available():
            return 0
        try:
            return orig_device_count()
        except Exception:
            return 0

    torch.cuda.is_available = safe_is_available
    torch.cuda.current_device = safe_current_device
    torch.cuda.device_count = safe_device_count

    try:
        yield
    finally:
        torch.cuda.is_available = orig_is_available
        torch.cuda.current_device = orig_current_device
        torch.cuda.device_count = orig_device_count
        if old_pythonpath:
            os.environ["PYTHONPATH"] = old_pythonpath
        else:
            os.environ.pop("PYTHONPATH", None)'''

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Replace old force_cpu_during_snapshot implementation
    # Match from @contextmanager\ndef force_cpu_during_snapshot(): up to the end of finally block
    pattern = r'@contextmanager\s+def force_cpu_during_snapshot\(\):[\s\S]+?os\.environ\.pop\("PYTHONPATH", None\)'
    content, count = re.subn(pattern, new_force_cpu_code, content)
    print(f"Replaced force_cpu_during_snapshot in {f} ({count} matches)")

    # Ensure we create /tmp/modal_snapshot_done right after the server_up loop succeeds!
    # In load_model, after "print(f"[UniversalComfyEngine] ComfyUI pronto em {t_boot_end - t_boot_start:.2f}s!")" or similar
    # Let's check where to insert open("/tmp/modal_snapshot_done", "w").close()
    # It should be at the very end of load_model(self)
    if 'open("/tmp/modal_snapshot_done", "w")' not in content:
        # Match the end of load_model
        # Look for "ComfyUI pronto em" or "ComfyUI pronto na porta"
        content = re.sub(
            r'(print\(f?"\[.*?\] ComfyUI pronto.*?s!"\))',
            r'\1\n        with open("/tmp/modal_snapshot_done", "w") as f_snap:\n            f_snap.write("done")\n        print("[Snapshot] Flag /tmp/modal_snapshot_done criada! Snapshot pronto para acordar na H100.")',
            content
        )

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(content)
    print(f"Updated {f} successfully!")
