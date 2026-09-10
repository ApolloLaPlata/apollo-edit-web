import os
from pydub import AudioSegment

def loop_beat():
    print("Iniciando extensor de Beat Trap (Crossfade Looping)...")
    
    input_file = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_sfx/StableAudio_Instrumental_Trap.wav"
    output_file = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_sfx/StableAudio_Instrumental_Trap_2Minutos_Looped.wav"
    
    if not os.path.exists(input_file):
        print(f"Arquivo nao encontrado: {input_file}")
        return
        
    print(f"Carregando: {input_file}")
    # Carrega o audio gerado (que tem 47s)
    beat = AudioSegment.from_wav(input_file)
    
    # Vamos cortar os 5 segundos iniciais (as vezes tem fade in) e os 5 segundos finais (pra evitar silecio)
    # Pegamos um 'miolo' bom e pesado de 30 segundos
    core_beat = beat[5000:35000] 
    
    # Quantas vezes precisamos repetir 30 segundos pra dar 2 minutos? (120s / 30s = 4)
    # Vamos fazer 5 vezes com crossfade para ficar suave
    print("Multiplicando e costurando o áudio com Crossfade...")
    long_beat = core_beat
    for _ in range(4):
        # 1.5 segundos de crossfade funde as batidas (como se fosse um DJ mixando o mesmo disco)
        long_beat = long_beat.append(core_beat, crossfade=1500)
    
    # Salvar o beat de 2+ minutos
    long_beat.export(output_file, format="wav")
    print(f"\n[SUCESSO] Beat extendido salvo em: {output_file}")
    print(f"Duracao original: {len(beat)/1000}s | Nova duracao: {len(long_beat)/1000}s")

if __name__ == "__main__":
    loop_beat()
