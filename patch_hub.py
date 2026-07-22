import re

file_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\hub.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fix selectChannel function
content = re.sub(
    r"localStorage\.setItem\('apollo_active_channel_id',\s*id\);\s*updateHeaderChannelName\(\);\s*renderChannelsList\(\);\s*window\.location\.reload\(\);",
    "window.open('apollo_os.html?channel_id=' + id, '_blank');",
    content
)

# 2. Fix all window.location.href assignments
# Find all occurrences of window.location.href='filename.html'
# Replace with a wrapper function call that tries to use window.parent.openAppTab
content = re.sub(
    r"window\.location\.href='([^']+)'",
    r"((window.parent && window.parent.openAppTab) ? window.parent.openAppTab('\1') : (window.location.href='\1'))",
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied to hub.html successfully!")
