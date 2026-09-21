import os
import sys
import time
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importar módulos da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Carrega configurações
load_dotenv()

import watcher
import writer
import designer
import publisher
import qwen_tts_client  # Novo Cliente TTS (Modal 9)

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
    
    # 2. Writer escreve o texto e decide a imagem e o roteiro de áudio
    texto_gerado = writer.escrever_artigo(pauta_escolhida, persona_prompt="Especialista")
    time.sleep(1)
    
    # 3. Designer gera a imagem com o Apollo (Capa Hero com Upscale 4x-UltraSharp)
    imagem_final = designer.gerar_imagem(texto_gerado["image_prompt"], image_format="Horizontal", upscale=True)
    time.sleep(1)
    
    # 3.5 Gerador TTS gera o áudio do post com o modelo Qwen (Modal 9)
    print("[ORQUESTRADOR] Iniciando a geração TTS no Modal 9...")
    audio_path = os.path.join("tmp", f"audio_{int(time.time())}.wav")
    os.makedirs("tmp", exist_ok=True)
    tts_client = qwen_tts_client.QwenTTSClient()
    tts_success = tts_client.generate_audio(texto_gerado.get("audio_script", "Resumo não encontrado"), audio_path)
    if tts_success:
        print(f"[ORQUESTRADOR] Áudio gerado e salvo em {audio_path}")
        # Fase X: Sincronização Inteligente Áudio ↔ Mídia (Extração de duração)
        try:
            import wave
            with wave.open(audio_path, 'r') as w:
                frames = w.getnframes()
                rate = w.getframerate()
                duracao_segundos = frames / float(rate)
                print(f"[ORQUESTRADOR] Duração exata do áudio: {duracao_segundos:.2f} segundos")
        except Exception as e:
            duracao_segundos = 0
            print(f"[ORQUESTRADOR] Falha ao extrair duração do áudio: {e}")
    else:
        duracao_segundos = 0
        print("[ORQUESTRADOR] Erro ao gerar áudio. Post prosseguirá sem áudio ou com áudio mudo.")
    time.sleep(1)

    # 4. Motor de Monetização Oculta: Achadinhos (Afiliados Shopee/AliExpress)
    try:
        from achadinhos_engine import injetar_banner_no_markdown
        print("[ORQUESTRADOR] Injetando Banners de Achadinhos no corpo do texto...")
        conteudo_md = injetar_banner_no_markdown(texto_gerado["markdown"])
    except ImportError:
        print("[ORQUESTRADOR] Motor de Achadinhos ausente, prosseguindo com texto limpo.")
        conteudo_md = texto_gerado["markdown"]

    # 5. Publisher publica o artigo (e a mídia gerada) no banco de dados da Fila
    titulo = pauta_escolhida["title"]
    publisher.publicar_artigo(titulo, conteudo_md, imagem_final, audio_path=audio_path, duracao_segundos=duracao_segundos)
    
    print("\n[ OK ] Fluxo autonomo de postagem concluido (Teste Local)!")
    print(f"Imagem a ser publicada: {imagem_final}")
    print(f"Áudio associado: {audio_path} ({duracao_segundos:.2f}s)")
    
if __name__ == "__main__":
    main()
