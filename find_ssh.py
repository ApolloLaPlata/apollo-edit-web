import re
import json

with open(r'C:\Users\v5est\.gemini\antigravity\brain\143dc2b3-a864-46e0-a51c-2f30028e42b6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if 'task-10408' in line and 'ssh' in line:
            print(line)
