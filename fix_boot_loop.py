import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # 1. Ensure --highvram in flux_txt2img_engine.py
    if 'flux_txt2img_engine.py' in f:
        content = content.replace(
            '["comfy", "--workspace", "/comfyui", "launch", "--", "--listen", "127.0.0.1", "--port", "8188"]',
            '["comfy", "--workspace", "/comfyui", "launch", "--", "--listen", "127.0.0.1", "--port", "8188", "--highvram"]'
        )

    # 2. Update boot loop to 300s and check process poll()
    # Match for _ in range(180): or similar loops
    old_loop_pattern = r'server_up = False\s+for _ in range\(\d+\):\s+(?:if self\.comfy_process\.poll\(\).*?\n\s+)?try:\s+with urllib\.request\.urlopen\("http://127\.0\.0\.1:(\d+)/system_stats", timeout=2\):\s+server_up = True\s+break\s+except Exception:\s+time\.sleep\(1\)'
    
    def loop_replacer(match):
        port = match.group(1)
        return f'''server_up = False
            for _ in range(300):
                if self.comfy_process.poll() is not None:
                    raise RuntimeError(f"[Boot] ComfyUI (porta {port}) encerrou inesperadamente com código {{self.comfy_process.returncode}}!")
                try:
                    with urllib.request.urlopen("http://127.0.0.1:{port}/system_stats", timeout=2):
                        server_up = True
                        break
                except Exception:
                    time.sleep(1)'''

    new_content, count = re.subn(old_loop_pattern, loop_replacer, content)
    
    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(new_content)
    print(f"Updated boot loop in {f} (matched {count} times)!")
