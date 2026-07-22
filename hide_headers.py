import os
import glob

# Script injection string
injection_block = """
<!-- APOLLO OS IFRAME CSS CLEANUP -->
<script>
    if (window.self !== window.top) {
        document.write('<style> body > header, .apollo-header, .topbar { display: none !important; } </style>');
    }
</script>
"""

# HTML Files to exclude
exclude_files = [
    "hub.html",
    "apollo_os.html",
    "index.html",
    "dashboard.html"
]

target_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui"

files = glob.glob(os.path.join(target_dir, "*.html"))
injected_count = 0

for file_path in files:
    filename = os.path.basename(file_path)
    if filename in exclude_files:
        continue
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Check if already injected
    if "APOLLO OS IFRAME CSS CLEANUP" in content:
        continue
        
    # Inject before </head>
    if "</head>" in content:
        content = content.replace("</head>", f"{injection_block}\n</head>")
        
        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)
        injected_count += 1
        print(f"Injected into {filename}")

print(f"Injection complete. Modified {injected_count} files.")
