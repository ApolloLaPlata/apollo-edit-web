import os
import time
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

import watcher
import writer
import designer
import publisher

def print_banner():
    print("="*50)
    print("[AUTO-BLOG CMS: AGENTE ORQUESTRADOR]")
    print("="*50)

def main():
    print_banner()
    niche = "Finanças"
    
    # 1. Watcher encontra a pauta
    pautas = watcher.buscar_pautas_recentes(niche)
    pauta_escolhida = pautas[0]
    time.sleep(1)
    
    # 2. Writer escreve o texto e decide a imagem
    texto_gerado = writer.escrever_artigo(pauta_escolhida, persona_prompt="Especialista")
    time.sleep(1)
    
    # 3. Designer gera a imagem com o Apollo
    imagem_final = designer.gerar_imagem(texto_gerado["image_prompt"])
    time.sleep(1)
    
    # 4. Publisher publica o artigo no banco de dados do Next.js
    titulo = pauta_escolhida["title"]
    conteudo_md = texto_gerado["markdown"]
    publisher.publicar_artigo(titulo, conteudo_md, imagem_final)
    
    print("\n[ OK ] Fluxo autonomo de postagem concluido (Teste Local)!")
    print(f"Imagem a ser publicada: {imagem_final}")
    
if __name__ == "__main__":
    main()
