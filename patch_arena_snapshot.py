import re

# Read Universal
with open("backend/cloud_tools/engines/universal_engine.py", "r", encoding="utf-8") as f:
    uni = f.read()

# Extract force_cpu_during_snapshot
match = re.search(r"@contextmanager\ndef force_cpu_during_snapshot\(\):.*?try:\n        yield\n    finally:.*?\n        torch\.cuda\.device_count = orig_device_count", uni, re.DOTALL)
if not match:
    print("Could not find robust force_cpu in universal_engine!")
    exit(1)

robust_force_cpu = match.group(0)

# Read Arena
with open("backend/cloud_tools/engines/apollo_arena_comfy_engine.py", "r", encoding="utf-8") as f:
    arena = f.read()

# Replace the weak force_cpu with robust one
arena = re.sub(r"@contextmanager\ndef force_cpu_during_snapshot\(\):.*?torch\.cuda\.current_device = orig_current_device", robust_force_cpu, arena, flags=re.DOTALL)

# Wrap subprocess.Popen
pop_code = """        with force_cpu_during_snapshot():
            self.comfy_process = subprocess.Popen(
                ["comfy", "--workspace", "/comfyui", "launch", "--",
                 "--listen", "127.0.0.1", "--port", "8188", "--highvram", "--extra-model-paths-config", "/comfyui/extra_model_paths.yaml", "--use-split-cross-attention"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )"""

arena = re.sub(r"        self\.comfy_process = subprocess\.Popen\([\s\S]*?text=True\n        \)", pop_code, arena)

with open("backend/cloud_tools/engines/apollo_arena_comfy_engine.py", "w", encoding="utf-8") as f:
    f.write(arena)

print("Patch applied to apollo_arena_comfy_engine.py!")
