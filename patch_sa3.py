import re

with open('backend/cloud_tools/engines/stable_audio_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the hardcoded params
content = content.replace('steps = 8 # HARDCODED para destilado', 'steps = 100')
content = content.replace('cfg = 1.0 # HARDCODED para destilado', 'cfg = 7.0')
content = content.replace('sampler_type="pingpong"', 'sampler_type="dpmpp-3m-sde"')

with open('backend/cloud_tools/engines/stable_audio_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
