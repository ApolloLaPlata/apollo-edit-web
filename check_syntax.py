import sys
with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/public/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

import json
print("Has throw 1?", 'throw new Error(HTTP : );' in text)
print("Has throw 2?", 'throw new Error(Nenhum dado valido retornado: );' in text)
print("Has split?", "split('\n  ');" in text)
