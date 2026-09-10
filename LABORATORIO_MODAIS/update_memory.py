import datetime

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/MEMORIA_ATIVA_SISTEMA.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add log to MEMÓRIA ATIVA (HISTÓRICO)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
log_entry = f"""
- **{now} - [ENGINE AUDIO FIXES & TIMEOUT BYPASS]**
  - **Vercel Timeout Bypass**: Nginx/Vercel was timing out on long 150s cold-starts (like MiniMax). Implemented `StreamingResponse` NDJSON heartbeat in both `apollo_modal_engine.py` (Modal) and `servidor_web.py` (Oracle). The proxy now yields 4096 spaces padding every 5 seconds to flush the Nginx buffer and keep the Vercel connection alive indefinitely.
  - **MiniMax Crash**: Fixed cold start crash by downgrading `huggingface_hub<=0.23.2` as newer versions removed `is_offline_mode` which crashed diffusers `ModularPipeline`.
  - **Ace-Step Robotic Sound**: Fixed by reducing `guidance_scale` from 18.0 (burned) to 4.5 and `infer_step` from 100 to 50 for more natural dynamics.
  - **Stable Audio 3 Muffled Sound**: Injected backend mastering tags (`high quality, 4k audio, high fidelity, clean, sharp, stereo, masterpiece`) implicitly into all user prompts.
"""

if "## 4. MEMÓRIA ATIVA (HISTÓRICO)" in content:
    content = content.replace("## 4. MEMÓRIA ATIVA (HISTÓRICO)", "## 4. MEMÓRIA ATIVA (HISTÓRICO)\n" + log_entry)
else:
    content += "\n## 4. MEMÓRIA ATIVA (HISTÓRICO)\n" + log_entry

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Memória atualizada.")
