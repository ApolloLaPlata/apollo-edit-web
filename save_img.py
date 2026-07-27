import json
import base64
with open(r'C:\Users\v5est\.gemini\antigravity\brain\1a81570a-dcb0-4985-9cbf-0bca86071582\.system_generated\tasks\task-24336.log', 'r') as f:
    text = f.read()

# Extract base64
start_marker = '"image_base64": "'
start = text.find(start_marker)
if start != -1:
    end = text.find('"', start + len(start_marker))
    b64 = text[start + len(start_marker):end]
    
    with open(r'C:\Users\v5est\.gemini\antigravity\brain\1a81570a-dcb0-4985-9cbf-0bca86071582\flux_modal_success.png', 'wb') as img_f:
        img_f.write(base64.b64decode(b64))
    print("Image saved successfully to artifact folder!")
