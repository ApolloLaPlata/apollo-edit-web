import codecs

path = 'backend/cloud_tools/engines/flux_engine.py'
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# Make sure we map denoise to BasicScheduler correctly
target = 'elif node["class_type"] == "BasicScheduler":'
replacement = '''elif node["class_type"] == "BasicScheduler":
                    node["inputs"]["denoise"] = 0.45'''
                    
if target in content:
    # Just in case it's already there with a different value
    import re
    content = re.sub(r'elif node\["class_type"\] == "BasicScheduler":\s*node\["inputs"\]\["denoise"\] = [0-9.]+', replacement, content)
else:
    print("BasicScheduler not found in engine.py! Adding it.")
    target2 = 'elif node["class_type"] == "RandomNoise":'
    replacement2 = '''elif node["class_type"] == "BasicScheduler":
                    node["inputs"]["denoise"] = 0.45
                elif node["class_type"] == "RandomNoise":'''
    content = content.replace(target2, replacement2)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)

print("Flux engine updated to inject denoise into BasicScheduler.")
