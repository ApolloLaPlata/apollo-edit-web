import sys

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\tts.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("const filename =  pollo_tts_nuvem.wav;", "const filename = 'apollo_tts_nuvem.wav';")
content = content.replace("setStatus(? udio gerado na nuvem!, 'success');", "setStatus('✅ Áudio gerado na nuvem!', 'success');")
content = content.replace("setStatus(â\x9c\x85 udio gerado na nuvem!, 'success');", "setStatus('✅ Áudio gerado na nuvem!', 'success');")
content = content.replace("setStatus(? Áudio gerado na nuvem!, 'success');", "setStatus('✅ Áudio gerado na nuvem!', 'success');")

# Also fix the catch block if it's broken
content = content.replace("setStatus(? Erro Nuvem: , 'error');", "setStatus(❌ Erro Nuvem: , 'error');")
content = content.replace("setStatus(? Erro de conexǜo com a Nuvem: , 'error');", "setStatus(❌ Erro de conexão com a Nuvem: , 'error');")
content = content.replace("alert(?Erro: ?);", "alert(Erro: );")
content = content.replace("alert(Erro: );", "alert(Erro: );")
content = content.replace("setStatus(❌ Erro Nuvem: , 'error');", "setStatus(❌ Erro Nuvem: , 'error');")
content = content.replace("setStatus(❌ Erro de conexão com a Nuvem: , 'error');", "setStatus(❌ Erro de conexão com a Nuvem: , 'error');")

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\tts.html', 'w', encoding='utf-8') as f:
    f.write(content)
