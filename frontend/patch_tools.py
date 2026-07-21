import codecs
import re

# 1. Estudio de Dublagem
filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\estudio_dublagem.html'
with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
content = re.sub(
    r'(setTimeout\(\(\) => \{)([\s\n]*)(if \(window\.showToast\) window\.showToast\(".*?gerado e enviado ao Bagageiro.*?\);)',
    r'\1\2if (window.apolloTransferOS) { window.apolloTransferOS.addItem("audio", "dublagem_rvc.wav", "Estudio RVC", null, { url: "/dummy_voice.m4a" }); }\n\2\3',
    content,
    flags=re.IGNORECASE|re.DOTALL
)
with codecs.open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Patched {filepath}")

# 2. Gerador de Musica
filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\gerador_musica.html'
with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
content = re.sub(
    r'(setTimeout\(\(\) => \{.*?btn\.style\.pointerEvents = "all";)([\s\n]*)(if \(window\.showToast\))',
    r'\1\2if (window.apolloTransferOS) { window.apolloTransferOS.addItem("audio", "musica_ia.wav", "Gerador de Musica", null, { url: "/dummy_music.m4a" }); }\n\2\3',
    content,
    flags=re.IGNORECASE|re.DOTALL
)
with codecs.open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Patched {filepath}")

# 3. Removedor de Fundo
filepath = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\removedor_fundo.html'
with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
content = re.sub(
    r'(setTimeout\(\(\) => \{)([\s\n]*)(if \(window\.showToast\) window\.showToast\("Processo Conclu.*? Imagem salva no Bagageiro.*?\);)',
    r'\1\2if (window.apolloTransferOS) { window.apolloTransferOS.addItem("image", type === "bg" ? "fundo_removido.png" : "imagem_4k.png", "AI Image Studio", null, { url: "/test.png" }); }\n\2\3',
    content,
    flags=re.IGNORECASE|re.DOTALL
)
with codecs.open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Patched {filepath}")
