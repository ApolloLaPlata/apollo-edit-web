import os
import re

files_to_patch = [
    r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\la_plata.js',
    r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias_core.js',
    r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\scripts_logic.js',
    r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\strategy_logic.js',
    r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\timeline.js',
]

def patch_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='latin-1') as f:
        content = f.read()
    
    # We will safely replace `alert('...')` and `alert("...")` with `showToast(...)`
    # We must only replace simple alerts, because alert(variable) is harder to blindly replace.
    # Actually, we can just replace `alert(` with `(typeof showToast === 'function' ? showToast : alert)(`
    # Wait, showToast takes (msg, type), alert takes (msg). If we do that, we get default type 'success'. 
    # Let's do `(typeof showToast === 'function' ? (msg) => showToast(msg, 'info') : alert)(`
    
    # Simple replace
    # alert( -> window.ApolloAlert(
    # Then we add window.ApolloAlert at the top.
    
    if "window.ApolloAlert" not in content:
        header = """
window.ApolloAlert = function(msg) {
    if (typeof showToast === 'function') {
        showToast(msg, 'info');
    } else {
        alert(msg);
    }
};
"""
        content = header + content
        # Replace only word-boundary alert(
        content = re.sub(r'\balert\(', 'window.ApolloAlert(', content)
        
        with open(filepath, 'w', encoding='latin-1') as f:
            f.write(content)
        print(f"Patched alerts in {filepath}")
    else:
        print(f"Already patched {filepath}")

for fp in files_to_patch:
    patch_file(fp)

