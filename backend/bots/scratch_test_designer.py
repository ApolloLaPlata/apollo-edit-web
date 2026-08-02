import os
import sys

# Adiciona o diretório atual ao path para poder importar designer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import designer

if __name__ == "__main__":
    print("Iniciando Teste de API Modal...")
    prompt = "A cinematic and realistic photo of a futuristic robot writing a blog on a holographic laptop, cyberpunk style, highly detailed, 4k"
    
    try:
        # Testa chamada com formato Horizontal e Upscale Desligado (pra ir rapido - 7s)
        # O upscale=True pode demorar ~36s a 60s se for cold start
        imagem_path = designer.gerar_imagem(prompt, image_format="Horizontal", upscale=False)
        print(f"SUCESSO! A imagem foi salva em: {imagem_path}")
    except Exception as e:
        print(f"ERRO FATAL DURANTE O TESTE: {e}")
