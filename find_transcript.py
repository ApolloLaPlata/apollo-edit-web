import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
log_path = r"C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\.system_generated\logs\transcript_full.jsonl"
with open(log_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "estava fazendo português brasileiro mesmo" in line:
        print(f"--- MATCH AT LINE {i} ---")
        for j in range(max(0, i-10), min(len(lines), i+2)):
            print(f"Line {j}: {lines[j][:500]}")
        break
