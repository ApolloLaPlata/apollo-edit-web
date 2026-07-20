import os
import glob

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tailwind Color Replacements
    replacements = [
        ('bg-zinc-50', 'bg-transparent'),
        ('bg-white', 'bg-zinc-900'),
        ('text-zinc-900', 'text-zinc-100'),
        ('text-zinc-800', 'text-zinc-200'),
        ('text-zinc-600', 'text-zinc-400'),
        ('text-zinc-500', 'text-zinc-400'),
        ('border-zinc-200', 'border-zinc-800'),
        ('border-zinc-300', 'border-zinc-700'),
        ('hover:bg-zinc-50', 'hover:bg-zinc-800'),
        ('hover:bg-zinc-100', 'hover:bg-zinc-800'),
        ('bg-zinc-100', 'bg-zinc-800'),
        ('bg-indigo-50', 'bg-indigo-900/30'),
        ('text-indigo-700', 'text-indigo-400'),
        ('bg-orange-50', 'bg-orange-900/30'),
        ('text-orange-700', 'text-orange-400'),
        ('bg-red-50', 'bg-red-900/30'),
        ('text-red-700', 'text-red-400'),
        ('bg-emerald-50', 'bg-emerald-900/30'),
        ('text-emerald-700', 'text-emerald-400'),
        # Add embedded and tab logic overrides
        ("new URLSearchParams(window.location.search).get('embedded')", "window.__APOLLO_EMBEDDED__")
    ]

    new_content = content
    for old, new in replacements:
        new_content = new_content.replace(old, new)
        
    # Also patch active tab initialization in App.tsx
    if "App.tsx" in filepath:
        new_content = new_content.replace(
            "const tab = params.get('tab');\n    return (tab as any) || 'scripts';",
            "const tab = params.get('tab');\n    return (tab as any) || window.__APOLLO_TAB__ || 'scripts';"
        )

    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Patched: {os.path.basename(filepath)}")

src_dir = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\Programas externos\central-das-noticias\src"
for ext in ('*.tsx', '*.ts'):
    for filepath in glob.glob(os.path.join(src_dir, '**', ext), recursive=True):
        patch_file(filepath)
print("All files patched for Dark Mode!")
