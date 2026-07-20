filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\scripts_logic.js'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

content = content.replace("replace(/```markdown\\\\n?/g, '').replace(/```\\\\n?/g, '')", "replace(/```markdown\\n?/g, '').replace(/```\\n?/g, '')")

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)
print("Regex fixed in scripts_logic.js")
