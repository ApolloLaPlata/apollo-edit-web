import json
with open(r'C:\Users\v5est\.gemini\antigravity\brain\1a81570a-dcb0-4985-9cbf-0bca86071582\.system_generated\tasks\task-24336.log', 'r') as f:
    text = f.read()
    # The output format is:
    # Status code: 200
    # Response: {"status": "success", "images": ["data:image/png;base64...
    if "Status code: 200" in text:
        print("HTTP 200 OK")
    if "status\": \"success\"" in text or "status': 'success'" in text:
        print("SUCCESS! IMAGE GENERATED!")
    if "error" in text.lower():
        print("WAIT, THERE WAS AN ERROR:", text[:500])
