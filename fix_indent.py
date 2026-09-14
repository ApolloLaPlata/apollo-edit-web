import sys

with open("servidor_web.py", "r", encoding="utf-8") as f:
    text = f.read()

bad_indent = '        lyrics = body.get("lyrics", "")\n                model_mapped = model_map.get(engine, engine)'
good_indent = '        lyrics = body.get("lyrics", "")\n        model_mapped = model_map.get(engine, engine)'

text = text.replace(bad_indent, good_indent)

with open("servidor_web.py", "w", encoding="utf-8") as f:
    f.write(text)
print("INDENTATION FIXED")
