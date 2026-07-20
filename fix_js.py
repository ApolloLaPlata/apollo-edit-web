import io
import re

files_to_fix = [
    'web_ui/monitor_logic.js',
    'web_ui/noticias_core.js',
    'web_ui/transfer_hud.js',
    'web_ui/dashboard_logic.js'
]

for filepath in files_to_fix:
    try:
        content = io.open(filepath, 'r', encoding='utf-8', errors='replace').read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        continue
    
    # Fix monitor_logic.js
    if 'monitor_logic.js' in filepath:
        content = re.sub(
            r"if \(modal\) modal\.style\.display = 'none';\r?\n\}\. \$\{v\.title\}`\)\.join\('\\n'\);\r?\n\s*alert\('[^']+' \+ titles\);\r?\n\}",
            r"if (modal) modal.style.display = 'none';\n}",
            content
        )
    
    # Fix noticias_core.js
    if 'noticias_core.js' in filepath:
        content = content.replace(
            "// --- Studio Logic ---\nlet studioCtx;\nlet studioImg;\n\n// --- Studio Canvas Logic ---\nlet studioCtx;\nlet studioImg;\n",
            "// --- Studio Canvas Logic ---\nlet studioCtx;\nlet studioImg;\n"
        )
        content = content.replace(
            "// --- Studio Logic ---\r\nlet studioCtx;\r\nlet studioImg;\r\n\r\n// --- Studio Canvas Logic ---\r\nlet studioCtx;\r\nlet studioImg;\r\n",
            "// --- Studio Canvas Logic ---\nlet studioCtx;\nlet studioImg;\n"
        )

    # Clean up literal backslashes escaping backticks globally if they exist in these files:
    content = content.replace(r"\`", "`")

    io.open(filepath, 'w', encoding='utf-8').write(content)
    print(f"Fixed {filepath}")
