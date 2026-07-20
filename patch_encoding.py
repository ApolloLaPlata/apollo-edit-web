import os

filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\servidor_web.py'
# Read it as latin-1 since that's what I wrote it as
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

# I wrote: 'user_prompt = f"Aprofunde esta not\xedcia:\\n\\n{req.input_text}"'
# The \xed is the character 'í'. Let's ensure it's properly set as a standard string.
content = content.replace("Aprofunde esta not\xedcia", "Aprofunde esta noticia")

# Save as UTF-8 which Python 3 expects
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Encoding fixed to UTF-8 and problematic character removed!")
