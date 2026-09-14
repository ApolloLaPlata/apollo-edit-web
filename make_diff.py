import difflib

with open('frontend/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    old = f.readlines()
    
with open('web_ui/modal_ai_studio_fixed.html', 'r', encoding='utf-8') as f:
    new = f.readlines()

diff = list(difflib.unified_diff(old, new))
with open('diff.html', 'w', encoding='utf-8') as f:
    f.writelines(diff)
print("Done. diff.html has", len(diff), "lines.")
