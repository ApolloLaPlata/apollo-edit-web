import sys
import re

with open('/home/ubuntu/apollo_edit/backend/cloud_tools/apollo_modal_engine.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''              if isinstance(res, bytes):
                  import uuid
                  filename = f"audio_{uuid.uuid4().hex}.wav"
                  filepath = f"/home/ubuntu/apollo_edit/media/{filename}"
                  with open(filepath, "wb") as af:
                      af.write(res)
                  return {"status": "success", "audio_url": f"https://www.apolloedit.com.br/media/{filename}", "message": "SA3 Recebido e salvo na Oracle!"}'''

text = re.sub(r'              if isinstance\(res, bytes\):[\s\S]*?return \{"status": "error", "error_type": "generation_failed"', replacement + '\n              return {"status": "error", "error_type": "generation_failed"', text)

with open('/home/ubuntu/apollo_edit/backend/cloud_tools/apollo_modal_engine.py', 'w', encoding='utf-8') as f:
    f.write(text)
