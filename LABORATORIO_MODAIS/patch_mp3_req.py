with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace("from fastapi import FastAPI", "from fastapi import FastAPI, Request")

with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py", "w", encoding="utf-8") as f:
    f.write(code)
