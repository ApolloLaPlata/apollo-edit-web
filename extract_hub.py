import json
import os

log_path = r"C:\Users\v5est\.gemini\antigravity\brain\9270dd65-160e-47e8-aea2-6a92fd50cfc6\.system_generated\logs\transcript.jsonl"
out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\hub_extracted.html"

last_hub_content = None

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if 'tool_calls' in data:
                for tc in data['tool_calls']:
                    if tc.get('name') == 'write_to_file':
                        args = tc.get('args', {})
                        if 'hub.html' in args.get('TargetFile', ''):
                            last_hub_content = args.get('CodeContent')
        except Exception as e:
            pass

if last_hub_content:
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(last_hub_content)
    print(f"Extracted hub.html! Size: {len(last_hub_content)}")
else:
    print("Could not find full write_to_file for hub.html")
