import codecs

path = 'backend/cloud_tools/apollo_modal_engine.py'
with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

# Replace literal newline with \n in the python source
content = content.replace('yield json.dumps(res) + "\n"', 'yield json.dumps(res) + "\\n"')
content = content.replace('yield " \n"', 'yield " \\n"')
content = content.replace('yield json.dumps({"status": "error", "message": f"Erro na Modal: {str(e)}"}) + "\n"', 'yield json.dumps({"status": "error", "message": f"Erro na Modal: {str(e)}"}) + "\\n"')

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(content)

print("Fixed syntax error")
