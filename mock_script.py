import os
import torch
_orig_is_available = getattr(torch.cuda, ""is_available"", lambda: False)
_orig_current_device = getattr(torch.cuda, ""current_device"", lambda: 0)
_orig_device_count = getattr(torch.cuda, ""device_count"", lambda: 0)
_orig_memory_stats = getattr(torch.cuda, ""memory_stats"", lambda device=None: {})
_orig_mem_get_info = getattr(torch.cuda, ""mem_get_info"", lambda device=None: (85899345920, 85899345920))

def _safe_memory_stats(device=None):
    try:
        return _orig_memory_stats(device)
    except Exception:
        return {}

def _safe_mem_get_info(device=None):
    try:
        return _orig_mem_get_info(device)
    except Exception:
        return (85899345920, 85899345920)

def _safe_is_available():
    if not os.path.exists(""/tmp/modal_snapshot_done""):
        return False
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
        return _orig_device_count()
    except Exception:
        return 0

class DummyDeviceProperties:
    def __init__(self):
        self.name = ""NVIDIA H100 80GB HBM3""
        self.major = 9
        self.minor = 0
        self.total_memory = 85899345920
        self.multi_processor_count = 114

def _safe_get_device_properties(device=None):
    if not os.path.exists(""/tmp/modal_snapshot_done""):
        return DummyDeviceProperties()
    try:
        return getattr(torch.cuda, ""_orig_get_device_properties"", lambda d: DummyDeviceProperties())(device)
    except Exception:
        return DummyDeviceProperties()

def _safe_get_device_name(device=None):
    if not os.path.exists(""/tmp/modal_snapshot_done""):
        return ""NVIDIA H100 80GB HBM3""
    try:
        return getattr(torch.cuda, ""_orig_get_device_name"", lambda d: ""NVIDIA H100 80GB HBM3"")(device)
    except Exception:
        return ""NVIDIA H100 80GB HBM3""

def _safe_get_device_capability(device=None):
    if not os.path.exists(""/tmp/modal_snapshot_done""):
        return (9, 0)
    try:
        return getattr(torch.cuda, ""_orig_get_device_capability"", lambda d: (9, 0))(device)
    except Exception:
        return (9, 0)

if hasattr(torch.cuda, ""get_device_properties"") and not hasattr(torch.cuda, ""_orig_get_device_properties""):
    torch.cuda._orig_get_device_properties = torch.cuda.get_device_properties
if hasattr(torch.cuda, ""get_device_name"") and not hasattr(torch.cuda, ""_orig_get_device_name""):
    torch.cuda._orig_get_device_name = torch.cuda.get_device_name
if hasattr(torch.cuda, ""get_device_capability"") and not hasattr(torch.cuda, ""_orig_get_device_capability""):
    torch.cuda._orig_get_device_capability = torch.cuda.get_device_capability

torch.cuda.is_available = _safe_is_available
torch.cuda.current_device = _safe_current_device
torch.cuda.device_count = _safe_device_count
torch.cuda.memory_stats = _safe_memory_stats
torch.cuda.mem_get_info = _safe_mem_get_info
torch.cuda.get_device_properties = _safe_get_device_properties
torch.cuda.get_device_name = _safe_get_device_name
torch.cuda.get_device_capability = _safe_get_device_capability
torch.cuda.is_bf16_supported = lambda: True

print(""[sitecustomize] Holy Grail CUDA & VRAM stats fallback active for ComfyUI boot!"")
