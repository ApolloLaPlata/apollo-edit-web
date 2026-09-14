import sys

with open("servidor_web.py", "r", encoding="utf-8") as f:
    text = f.read()

bad_payload = """        payload = {
            "model": model_map.get(engine, engine),
            "prompt": prompt,
            "lyrics": lyrics,
            "duration": float(duration)
        }"""
        
good_payload = """        payload = {
            "model": model_mapped,
            "prompt": final_prompt,
            "lyrics": final_lyrics,
            "duration": float(duration)
        }"""

text = text.replace(bad_payload, good_payload)
with open("servidor_web.py", "w", encoding="utf-8") as f:
    f.write(text)
print("FIXED PAYLOAD")
