import re

files = [
    r'backend\cloud_tools\engines\universal_engine.py',
    r'backend\cloud_tools\engines\flux_engine.py',
    r'backend\cloud_tools\engines\flux_txt2img_engine.py'
]

new_mock_site = '''_orig_get_device_name = getattr(torch.cuda, "get_device_name", lambda d=None: "Mock GPU")
_orig_get_device_properties = getattr(torch.cuda, "get_device_properties", None)

def _safe_get_device_name(device=None):
    if not os.path.exists("/tmp/modal_snapshot_done"):
        return "Mock GPU"
    try:
        return _orig_get_device_name(device)
    except Exception:
        return "Mock GPU"

class MockPropertiesSite:
    name = "Mock GPU"
    total_memory = 85899345920
    major = 8
    minor = 0

def _safe_get_device_properties(device=None):
    if not os.path.exists("/tmp/modal_snapshot_done"):
        return MockPropertiesSite()
    try:
        if _orig_get_device_properties:
            return _orig_get_device_properties(device)
        return MockPropertiesSite()
    except Exception:
        return MockPropertiesSite()

torch.cuda.get_device_name = _safe_get_device_name
torch.cuda.get_device_properties = _safe_get_device_properties
torch.cuda.memory_stats = _safe_memory_stats'''

for target_file in files:
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace sitecustomize
    content = content.replace("torch.cuda.memory_stats = _safe_memory_stats", new_mock_site)

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)

