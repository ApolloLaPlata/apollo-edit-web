import re

files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    if '"/tmp/modal_snapshot_done", "w"' not in content:
        # Match "if server_up:\n" followed by spaces and a line
        def repl(m):
            indent = m.group(1)
            return f"if server_up:\n{indent}    with open(\"/tmp/modal_snapshot_done\", \"w\") as f_snap:\n{indent}        f_snap.write(\"done\")\n{indent}    print(\"[Snapshot] Flag /tmp/modal_snapshot_done criada com sucesso!\")\n{indent}"

        content, count = re.subn(r'if server_up:\s*\n(\s+)', repl, content, count=1)
        print(f"Inserted snapshot_done flag creation in {f} ({count} matches)")
    else:
        print(f"Already present in {f}")

    with open(f, 'w', encoding='utf-8-sig') as file:
        file.write(content)
