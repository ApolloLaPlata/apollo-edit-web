import json
with open(r'C:\Users\v5est\.gemini\antigravity\brain\143dc2b3-a864-46e0-a51c-2f30028e42b6\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if '"step_index":10708' in line:
            data = json.loads(line)
            print(json.dumps(data.get('tool_calls', []), indent=2))
