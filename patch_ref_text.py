# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/f5_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Substituir a assinatura de generate_voice
text = text.replace(
    'def generate_voice(self, text: str, reference_audio_bytes: bytes = None):',
    'def generate_voice(self, text: str, reference_audio_bytes: bytes = None, ref_text: str = ""):'
)

# Substituir a atribuição de ref_text
text = text.replace(
    'ref_text = "" # F5 infere sozinho ou a gente não passa texto de ref',
    '# ref_text já é recebido por parâmetro'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("f5_engine.py corrigido com suporte a ref_text!")
