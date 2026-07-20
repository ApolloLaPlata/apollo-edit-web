import json
import re

with open(r'C:\Users\v5est\.gemini\antigravity\brain\1a81570a-dcb0-4985-9cbf-0bca86071582\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        matches = re.findall(r'modal profile activate \w+', line)
        if matches:
            print(matches)
