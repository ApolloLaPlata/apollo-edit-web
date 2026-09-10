import modal
import os
import base64
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando Teste Final: MÚSICA COM VOZ DE 4 MINUTOS (Prova de Fogo)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    # 4 Minutos cravados
    DURACAO = 240 
    # Passos de Alta Qualidade (sem fritar o latente)
    PASSOS = 64
    
    estilo = "brazilian trap, dark, heavy 808s, fast hi-hats, club reverb, autotuned male rap vocals, melodic singing hooks, brazilian portuguese lyrics, rio de janeiro accent, 140 bpm, hi-fi, wide stereo"
    
    # Letra GIGANTE (aprox. 35-40 linhas) para dar combustível para a IA preencher 240 segundos sem quebrar a batida e sem repetir
    letra = """[pt]
[Intro]
Yeah, Apollo Edit na área
Você já sabe quem dita as regras
Nós tamo' no topo, sem pressa

[Verse 1]
Eu tô no corre desde cedo, mano, sem parar
A rua ensina o que a escola não consegue dar
O grave bate no meu peito, faz tremer o chão
Quem tentou me derrubar hoje tá na minha mão
Eu vejo os falsos recuando quando eu chego lá
Eles falam muito mas não sabem o que é trampar
Cada gota de suor virou ouro no final
Nossa banca é fechada, instinto animal

[Pre-Chorus]
Eles tentam entender a fórmula do som
Mas o talento não se compra, mano, a gente tem o dom
Eu piso forte no asfalto, deixo a minha marca
O sistema tenta mas não para essa barca

[Chorus]
VOU SUBIR, VOU SUBIR, NINGUÉM PODE ME PARAR
(ninguém pode, ninguém pode)
A NOITE É NOSSA E O GRAVE VAI ESTOURAR
(vai estourar, vai estourar)
O TOPO É MEU LUGAR E EU VOU TE PROVAR
(eu vou provar, yeah)
NESSA SELVA DE PEDRA EU NASCI PRA REINAR

[Verse 2]
[raspy vocal]
Lembro das noites em claro virando a madrugada
Focado no projeto enquanto a cidade tava calada
Hoje eu olho pro espelho e vejo a evolução
Sem dar moral pra inveja, sem perder a razão
Eles olham de longe e perguntam como a gente faz
Só quem bota a cara a tapa sabe o que isso traz
Dinheiro na conta, respeito na rua, a tropa avançou
Quem duvidava ontem, hoje calou

[Chorus]
VOU SUBIR, VOU SUBIR, NINGUÉM PODE ME PARAR
(ninguém pode, ninguém pode)
A NOITE É NOSSA E O GRAVE VAI ESTOURAR
(vai estourar, vai estourar)
O TOPO É MEU LUGAR E EU VOU TE PROVAR
(eu vou provar, yeah)
NESSA SELVA DE PEDRA EU NASCI PRA REINAR

[Bridge]
Nada vai me deter, eu tô correndo por mim
A trajetória é longa mas eu não vejo o fim
(Não vejo o fim, yeah)
O tempo passa rápido, não dá pra esperar
Se joga no jogo se tu quer ganhar

[Chorus]
VOU SUBIR, VOU SUBIR, NINGUÉM PODE ME PARAR
(ninguém pode, ninguém pode)
A NOITE É NOSSA E O GRAVE VAI ESTOURAR
(vai estourar, vai estourar)
O TOPO É MEU LUGAR E EU VOU TE PROVAR

[Outro]
Apollo Edit, o sistema não para
Isso é história sendo escrita na sua cara
Yeah, tamo junto
(Fade out)"""
    
    engine = AceStep15Engine()
    
    print(f"Enviando pedido da MÚSICA COMPLETA ({DURACAO}s) para as H100s na nuvem ({PASSOS} passos)...")
    
    call = engine.generate.spawn(
        style_tags=estilo,
        lyrics=letra,
        length_seconds=DURACAO,
        steps=PASSOS
    )
        
    try:
        result = call.get()
        if result["status"] == "success":
            audio_bytes = base64.b64decode(result["audio_base64"])
            import time
            timestamp = int(time.time())
            out_path = f"LABORATORIO_MODAIS/testes_audio/ACE_Vocal_Musica_Completa_4Min_{timestamp}.wav"
            
            with open(out_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path} (Tempo de GPU: {result.get('render_time_seconds')}s)")
        else:
            print(f"[FALHA] Erro: {result.get('error')}")
            
    except Exception as e:
        print(f"[FALHA CRITICA]: {e}")
