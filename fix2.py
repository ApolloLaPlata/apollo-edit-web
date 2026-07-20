path = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\web_ui\noticias.html'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.lstrip('"')
c = c.replace('Notcias', 'Notícias').replace('Estratgia', 'Estratégia').replace('Caador', 'Caçador').replace('Concludo', 'Concluído').replace('Padres', 'Padrões').replace('Opes', 'Opções').replace('transcrio', 'transcrição').replace('Atualizao', 'Atualização')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("Done")
