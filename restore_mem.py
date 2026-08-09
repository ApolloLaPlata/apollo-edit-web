import json
filepath = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\.system_generated\logs\transcript_full.jsonl'
found_content = None
with open(filepath, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('type') == 'TOOL_RESPONSE':
                content = data.get('content', '')
                if 'O Pivot CapCut (Dark Channels)' in content and 'cat E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\MEMORIA_ATIVA_SISTEMA.md' in content:
                    found_content = content
        except:
            pass

if found_content:
    # The content usually starts with 'The command exited with code 0.\nOutput:\n'
    idx = found_content.find('Output:\n')
    if idx != -1:
        found_content = found_content[idx + 8:]
    with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\MEMORIA_ATIVA_SISTEMA_RESTORED.md', 'w', encoding='utf-8') as f:
        f.write(found_content.strip())
    print('Restored from transcript!')
else:
    print('Not found')

