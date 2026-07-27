import sys
import re

files = [
    r'backend\cloud_tools\engines\universal_engine.py',
    r'backend\cloud_tools\engines\flux_engine.py',
    r'backend\cloud_tools\engines\flux_txt2img_engine.py'
]

new_mock_context = '''    orig_get_device_name = getattr(torch.cuda, "get_device_name", lambda d=None: "Mock GPU")
    orig_get_device_properties = getattr(torch.cuda, "get_device_properties", None)

    def safe_get_device_name(device=None):
        if not os.path.exists("/tmp/modal_snapshot_done"):
            return "Mock GPU"
        try:
            return orig_get_device_name(device)
        except Exception:
            return "Mock GPU"

    class MockPropertiesLocal:
        name = "Mock GPU"
        total_memory = 85899345920
        major = 8
        minor = 0

    def safe_get_device_properties(device=None):
        if not os.path.exists("/tmp/modal_snapshot_done"):
            return MockPropertiesLocal()
        try:
            if orig_get_device_properties:
                return orig_get_device_properties(device)
            return MockPropertiesLocal()
        except Exception:
            return MockPropertiesLocal()

    torch.cuda.get_device_name = safe_get_device_name
    torch.cuda.get_device_properties = safe_get_device_properties
    torch.cuda.memory_stats = safe_memory_stats'''

for target_file in files:
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the setting of memory_stats in the context manager
    content = content.replace("    torch.cuda.memory_stats = safe_memory_stats", new_mock_context)
    
    # Also add the restore
    content = content.replace("        torch.cuda.memory_stats = orig_memory_stats", "        torch.cuda.get_device_name = orig_get_device_name\n        torch.cuda.get_device_properties = orig_get_device_properties\n        torch.cuda.memory_stats = orig_memory_stats")

    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)

