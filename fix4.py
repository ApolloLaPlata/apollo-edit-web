import codecs

for path in [r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias_core.js', r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.css']:
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    if c.startswith('"') and c.endswith('"'):
        c = c[1:-1]
        
    c = c.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t').replace('\\\\', '\\')

    # Fix accents
    c = c.replace('EstratǸgia', 'Estratégia').replace('Caador', 'Caçador').replace('Notcias', 'Notícias').replace('Configuraes', 'Configurações').replace('Histrico', 'Histórico').replace('Mineraǜo', 'Mineração').replace('Estǧdio', 'Estúdio')
    c = c.replace('configuraes', 'configurações').replace('padrǜo', 'padrão')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

print("Done decoding")
