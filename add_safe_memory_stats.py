import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

new_sitecustomize = '''import os
import torch
_orig_is_available = getattr(torch.cuda, "is_available", lambda: False)
_orig_current_device = getattr(torch.cuda, "current_device", lambda: 0)
_orig_device_count = getattr(torch.cuda, "device_count", lambda: 0)
_orig_memory_stats = getattr(torch.cuda, "memory_stats", lambda device=None: {})
_orig_mem_get_info = getattr(torch.cuda, "mem_get_info", lambda device=None: (85899345920, 85899345920))

def _safe_memory_stats(device=None):
    try:
        stats = _orig_memory_stats(device)
        if isinstance(stats, dict) and 'reserved_bytes.all.current' not in stats:
            return {
                'reserved_bytes.all.current': 0,
                'allocated_bytes.all.current': 0,
                'active_bytes.all.current': 0,
                'inactive_split_bytes.all.current': 0
            }
        return stats
    except Exception:
        return {
            'reserved_bytes.all.current': 0,
            'allocated_bytes.all.current': 0,
            'active_bytes.all.current': 0,
            'inactive_split_bytes.all.current': 0
        }

def _safe_mem_get_info(device=None):
    try:
        return _orig_mem_get_info(device)
    except Exception:
        return (85899345920, 85899345920)

def _safe_is_available():
    if not os.path.exists("/tmp/modal_snapshot_done"):
        return True  # Retorna True no boot com --highvram para o ComfyUI iniciar sem falhar na CPU
    try:
        return _orig_is_available()
    except Exception:
        return False

def _safe_current_device():
    try:
        return _orig_current_device()
    except Exception:
        return 0

def _safe_device_count():
    try:
        res = _orig_device_count()
        return res if res > 0 else 1
    except Exception:
        return 1

torch.cuda.memory_stats = _safe_memory_stats
torch.cuda.mem_get_info = _safe_mem_get_info
torch.cuda.is_available = _safe_is_available
torch.cuda.current_device = _safe_current_device
torch.cuda.device_count = _safe_device_count
print("[sitecustomize] Holy Grail CUDA & VRAM stats fallback active for ComfyUI boot!")
'''

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Replace the sitecustomize string inside f.write('''...''')
    pattern = r'f\.write\(\'\'\'import os\nimport torch[\s\S]+?print\("\[sitecustomize\] Holy Grail CUDA fallback active for ComfyUI boot!"\)\n\'\'\)'
    
    content, count = re.subn(pattern, f"f.write('''{new_sitecustomize}''')", content)
    print(f"Updated sitecustomize in {f} ({count} matches)")

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(content)
