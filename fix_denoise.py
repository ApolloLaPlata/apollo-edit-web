import codecs
path = 'backend/cloud_tools/engines/flux_engine.py'
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# We need to inject the denoise setting in the generate method
target = 'node["inputs"]["height"] = cfg["height"]'
replacement = '''node["inputs"]["height"] = cfg["height"]
                elif node["class_type"] == "BasicScheduler":
                    node["inputs"]["denoise"] = 0.35'''
                    
if target in content:
    content = content.replace(target, replacement)
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
    print("Denoise injected!")
else:
    print("Target not found")
