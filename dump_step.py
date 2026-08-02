import json
with open(r'C:\Users\v5est\.gemini\antigravity\brain\143dc2b3-a864-46e0-a51c-2f30028e42b6\.system_generated\logs\transcript_full.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        if '"step_index":10521' in line:
            with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\ssh_results.txt', 'w', encoding='utf-8') as out:
                out.write(line)
