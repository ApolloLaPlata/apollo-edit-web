import os
with open("backend/cloud_tools/apollo_modal_engine.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("steps=64", "steps=50")

with open("backend/cloud_tools/apollo_modal_engine.py", "w", encoding="utf-8") as f:
    f.write(text)
print("FIXED APOLLO MODAL ENGINE")
