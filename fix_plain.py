import sys
with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r') as f:
    text = f.read()

text = text.replace('from fastapi import FastAPI, UploadFile, File, Form, Depends, Request', 'from fastapi import FastAPI, UploadFile, File, Form, Depends, Request\nfrom fastapi.responses import PlainTextResponse')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w') as f:
    f.write(text)
