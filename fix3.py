import json

log_path = r'C:\Users\v5est\.gemini\antigravity\brain\503447eb-5141-4dbd-b759-19c00d97be99\.system_generated\logs\transcript.jsonl'
lines = open(log_path, 'r', encoding='utf-8').readlines()
lines.reverse()

files_to_recover = {
    'noticias_core.js': None,
    'noticias.css': None
}

for line in lines:
    try:
        obj = json.loads(line)
        calls = obj.get('tool_calls', [])
        for call in calls:
            if call.get('name') == 'write_to_file':
                target = call.get('args', {}).get('TargetFile', '')
                for f in files_to_recover:
                    if files_to_recover[f] is None and f in target:
                        files_to_recover[f] = call['args']['CodeContent']
    except:
        pass
    
    if all(files_to_recover.values()):
        break

for f, content in files_to_recover.items():
    if content:
        with open(fr'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\{f}', 'w', encoding='utf-8') as out:
            out.write(content)
        print(f"Restored {f}")
    else:
        print(f"Could not find {f}")
