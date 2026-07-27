files = [
    'backend/cloud_tools/engines/universal_engine.py',
    'backend/cloud_tools/engines/flux_engine.py',
    'backend/cloud_tools/engines/flux_txt2img_engine.py'
]

for f in files:
    with open(f, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()

    new_lines = []
    i = 0
    count = 0
    while i < len(lines):
        line = lines[i]
        if 'def _safe_is_available():' in line or 'def safe_is_available():' in line:
            new_lines.append(line)
            i += 1
            if i < len(lines) and 'if not os.path.exists("/tmp/modal_snapshot_done"):' in lines[i]:
                new_lines.append(lines[i])
                i += 1
                if i < len(lines) and 'return True' in lines[i]:
                    indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                    new_lines.append(f'{indent}return False\n')
                    count += 1
                    i += 1
                else:
                    new_lines.append(lines[i])
                    i += 1
        else:
            new_lines.append(line)
            i += 1

    print(f"Replaced return True with return False in {f} ({count} matches)")
    with open(f, 'w', encoding='utf-8-sig') as file:
        file.writelines(new_lines)
