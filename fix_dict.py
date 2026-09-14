import re

with open('web_ui/modal_ai_studio.html', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    'Ã§Ã£': 'çã',
    'AÃ§Ã£o': 'Ação',
    'DuraÃ§Ã£o': 'Duração',
    'AleatÃ³rio': 'Aleatório',
    'GeraÃ§Ã£o': 'Geração',
    'AutomÃ¡tica': 'Automática',
    'VÃ­deo': 'Vídeo',
    'MÃºsica': 'Música',
    'renderizaÃ§Ã£o': 'renderização',
    'â€¢': '•',
    'â€”': '—',
    'ðŸš€': '🚀',
    'ðŸ”·': '🔹',
    'ðŸŽ¬': '🎬',
    'ðŸŽ™ï¸ ': '🎙️',
    'ðŸŽµ': '🎵',
    'ðŸŽ§': '🎧',
    'â›”': '⛔',
    'â ³': '⏳',
    'â†’': '→',
    'Ã©': 'é',
    'serÃ¡': 'será',
    'mÃºsica': 'música',
    'inglÃªs': 'inglês',
    'ReferÃªncia': 'Referência',
    'resoluÃ§Ã£o': 'resolução',
    'DiagnÃ³stico': 'Diagnóstico',
    'ConexÃ£o': 'Conexão',
    'AvanÃ§adas': 'Avançadas',
    'opÃ§Ãµes': 'opções',
    'PadrÃ£o': 'Padrão',
    'SÃ­ntese': 'Síntese',
    'Clonagem': 'Clonagem',
    'Ã\x81udio': 'Áudio',
    'MÃ¡x': 'Máx',
    'NÃºmero': 'Número',
    'Única': 'Única', # Wait, let's fix carefully
}

for bad, good in replacements.items():
    text = text.replace(bad, good)

# also any standalone
text = text.replace('Ã§', 'ç')
text = text.replace('Ã£', 'ã')
text = text.replace('Ã¡', 'á')
text = text.replace('Ã³', 'ó')
text = text.replace('Ã©', 'é')
text = text.replace('Ãª', 'ê')
text = text.replace('Ã­', 'í')
text = text.replace('Ãº', 'ú')
text = text.replace('Ãµ', 'õ')
text = text.replace('Ã¢', 'â')
text = text.replace('Ã§', 'ç')
text = text.replace('Ã‡', 'Ç')
text = text.replace('Ãƒ', 'Ã')
text = text.replace('Ã\x81', 'Á')

with open('web_ui/modal_ai_studio_fixed.html', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")
