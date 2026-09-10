import sys
with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r') as f:
    text = f.read()

text = text.replace('req = client.build_request("POST", modal_url, content=body, headers=req_headers)', 'req = client.build_request("POST", modal_url, content=body, headers=req_headers)\n        with open("/home/ubuntu/proxy_debug.log", "a") as dbg:\n            dbg.write(f"URL: {modal_url}\\nHeaders: {req_headers}\\n\\n")')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w') as f:
    f.write(text)
