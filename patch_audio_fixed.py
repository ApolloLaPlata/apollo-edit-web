import re

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

with open('/home/ubuntu/apollo_edit/correct_interceptor.txt', 'r', encoding='utf-8') as f:
    new_code = f.read()

text = re.sub(r'async def audio_interceptor\(\):[\s\S]*?yield json.dumps\(\{"status": "error"[\s\S]*?b"\\n"(?:\")?', new_code, text)

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
