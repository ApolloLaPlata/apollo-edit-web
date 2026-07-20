import json

log_path = r'C:\Users\v5est\.gemini\antigravity\brain\503447eb-5141-4dbd-b759-19c00d97be99\.system_generated\logs\transcript.jsonl'
lines = open(log_path, 'r', encoding='utf-8').readlines()
lines.reverse()

content = ''
for line in lines:
    try:
        obj = json.loads(line)
        calls = obj.get('tool_calls', [])
        for call in calls:
            if call.get('name') == 'write_to_file' and 'noticias.html' in call.get('args', {}).get('TargetFile', ''):
                content = call['args']['CodeContent']
                break
        if content:
            break
    except:
        pass

if content:
    open(r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html', 'w', encoding='utf-8').write(content)
    print('Restored noticias.html from transcript!')
else:
    print('Not found')
