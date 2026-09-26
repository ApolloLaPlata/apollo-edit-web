import os
import random
import time
import uuid
import datetime
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Adiciona a raiz do projeto ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, '../..')))

# Importa o motor Qwen TTS que acabamos de refatorar para o AutoBlog
from qwen_tts_client import QwenTTSClient

load_dotenv()
# Em produção, devemos usar o account_pool, mas para o AutoBlog, pegaremos a primeira
LIGHTNING_KEY = "sk-lit-8d641291-d92e-4469-8465-4a74d1c28a5d"
client = OpenAI(api_key=LIGHTNING_KEY, base_url="https://api.lightning.ai/v1")

# Diretório onde as falas ficarão salvas para o OBS Studio (Ducking)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RADIO_QUEUE_DIR = os.path.join(BASE_DIR, "..", "storage", "radio_queue")
os.makedirs(RADIO_QUEUE_DIR, exist_ok=True)

def gerar_texto_host():
    """
    Usa a Skill 'broadcaster-radio-host' para gerar inserções dinâmicas de 10-20s.
    Adiciona o requisito do usuário de intercalar em várias línguas aleatórias.
    """
    idiomas = ["Português (Brasil)", "Inglês", "Espanhol", "Japonês (com tom Cyberpunk)", "Russo (Mafia Vibes)"]
    idioma_escolhido = random.choice(idiomas)
    
    print(f"[RADIO BROADCASTER] Gerando roteiro do Host na língua: {idioma_escolhido}...")
    
    system_prompt = """Você é um Diretor de Rádio e Roteirista de entretenimento. Você escreve as inserções rápidas (ducking scripts) para o Host virtual da rádio 24/7 (ex: Dark Trap Radio).

Regras da Rádio:
- Tamanho: Inserções curtas de 10 a 20 segundos no máximo. Dinâmico, estilo rádio FM moderna.
- Tom (Dark Trap): Sombrio, noturno, "underground", cyberpunk, focado no submundo e estética neon/dark.
- Conteúdo: Mande um alô para o chat, anuncie que a música eletrônica vai continuar batendo pesado, ou faça reflexões sobre a "cidade noturna".
- Sem introduções de IA: Entregue apenas a fala pura, pronta para ser convertida em TTS. NUNCA coloque aspas, emotes, ou 'Aqui está a sua fala'.
"""
    
    user_prompt = f"Crie uma fala de Host de Rádio AGORA. O idioma da fala deve ser 100% em {idioma_escolhido}. Se for outro idioma além do português, faça soar incrivelmente cinematográfico."

    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct" if os.getenv("LIGHTNING_API_KEY") else "meta-llama/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.85
        )
        texto_gerado = response.choices[0].message.content.strip()
        print(f"[RADIO BROADCASTER] Texto gerado:\n\"{texto_gerado}\"")
        return texto_gerado
    except Exception as e:
        print(f"[RADIO BROADCASTER] Erro ao gerar texto: {e}")
        return "Conexão perdida com a cidade noturna... mas a batida continua."

def gerar_audio_insercao(texto):
    """
    Envia o texto para a nuvem (Modal 9 / Qwen-TTS) e baixa o WAV para a pasta do OBS.
    """
    tts_client = QwenTTSClient()
    filename = f"host_insert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.wav"
    output_path = os.path.join(RADIO_QUEUE_DIR, filename)
    
    print(f"[RADIO BROADCASTER] Sintetizando voz do Host via QwenTTS na Modal...")
    try:
        # Pede para o Qwen narrar no estilo dark/sombrio (se suportado pelo prompt de instrução dele)
        sucesso = tts_client.generate_audio(
            text=texto, 
            output_path=output_path,
            # Se o QwenTTS suportar instruções (conforme vimos na memória), passamos isso:
            # instruct="Um host de rádio sombrio, voz profunda e misteriosa, falando em um microfone de rádio."
        )
        if sucesso:
            print(f"[RADIO BROADCASTER] [ OK ] Inserção de Rádio pronta para Ducking: {output_path}")
            return output_path
    except Exception as e:
        print(f"[RADIO BROADCASTER] Erro ao sintetizar áudio: {e}")
    return None

def iniciar_cron_radio(intervalo_minutos=30):
    """
    Motor contínuo da Rádio. A cada X minutos, acorda e gera uma nova inserção.
    """
    print("="*60)
    print("📻 [RADIO BROADCASTER] Motor de Intervenções 24/7 Inicializado...")
    print(f"🎵 [RADIO BROADCASTER] Ciclo: Uma nova fala a cada {intervalo_minutos} minutos.")
    print("="*60)
    
    while True:
        texto = gerar_texto_host()
        if texto:
            audio_path = gerar_audio_insercao(texto)
            if audio_path:
                print(f"[RADIO BROADCASTER] Arquivo gerado, aguardando OBS e sistema de Ducking assumirem a pista.")
                
        # Calcula os segundos de pausa
        segundos = intervalo_minutos * 60
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{agora}] Zzz... Host dormindo. Próxima intervenção em {intervalo_minutos} min.")
        time.sleep(segundos)

if __name__ == "__main__":
    # Inicia o Broadcaster local testando a cada 45 minutos.
    iniciar_cron_radio(intervalo_minutos=45)
