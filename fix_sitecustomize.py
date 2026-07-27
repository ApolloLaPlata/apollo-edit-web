import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

new_sitecustomize = '''@contextmanager
def force_cpu_during_snapshot():
    import os
    import sys
    import torch

    mock_dir = "/tmp/mock_cuda"
    os.makedirs(mock_dir, exist_ok=True)
    site_path = os.path.join(mock_dir, "sitecustomize.py")
    with open(site_path, "w") as f:
        f.write(\'\'\'import torch
_orig_is_available = getattr(torch.cuda, "is_available", lambda: False)
_orig_current_device = getattr(torch.cuda, "current_device", lambda: 0)

def _smart_is_available():
    try:
        if _orig_is_available():
            x = torch.zeros(1, device="cuda")
            del x
            stats = torch.cuda.memory_stats(0)
            if 'reserved_bytes.all.current' in stats:
                return True
    except Exception:
        pass
    return False

def _smart_current_device():
    try:
        return _orig_current_device()
    except Exception:
        return 0

torch.cuda.is_available = _smart_is_available
torch.cuda.current_device = _smart_current_device
print("[sitecustomize] Smart CUDA fallback active for ComfyUI boot!")
\'\'\')

    old_pythonpath = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = f"{mock_dir}:{old_pythonpath}" if old_pythonpath else mock_dir

    orig_is_available = getattr(torch.cuda, "is_available", lambda: False)
    orig_current_device = getattr(torch.cuda, "current_device", lambda: 0)

    def smart_is_available():
        try:
            if orig_is_available():
                x = torch.zeros(1, device="cuda")
                del x
                stats = torch.cuda.memory_stats(0)
                if 'reserved_bytes.all.current' in stats:
                    return True
        except Exception:
            pass
        return False

    def smart_current_device():
        try:
            return orig_current_device()
        except Exception:
            return 0

    torch.cuda.is_available = smart_is_available
    torch.cuda.current_device = smart_current_device

    try:
        yield
    finally:
        torch.cuda.is_available = orig_is_available
        torch.cuda.current_device = orig_current_device
        if old_pythonpath:
            os.environ["PYTHONPATH"] = old_pythonpath
        else:
            os.environ.pop("PYTHONPATH", None)
'''

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Replace the existing force_cpu_during_snapshot block
    pattern = r'@contextmanager\s+def force_cpu_during_snapshot\(\):[\s\S]*?os\.environ\.pop\("PYTHONPATH", None\)\n'
    new_content, count = re.subn(pattern, new_sitecustomize, content)
    
    if count == 0:
        # Fallback if regex didn't match exact newline
        pattern2 = r'@contextmanager\s+def force_cpu_during_snapshot\(\):[\s\S]*?os\.environ\.pop\("PYTHONPATH", None\)'
        new_content, count = re.subn(pattern2, new_sitecustomize.strip(), content)

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(new_content)
    print(f"Updated sitecustomize in {f} (replaced {count} times)!")
