import os
import subprocess

def process_audio(input_folder, pattern):
    """
    Processa os áudios na pasta fornecida, buscando pelos nomes no padrão
    especificado (exemplo: dariuscena (1).wav) e removendo os silêncios.
    Salva os arquivos processados na subpasta 'processed_audio'.
    """
    # Obtém o diretório pai (dariusfala, hugofala ou joyefala)
    parent_folder = os.path.dirname(input_folder)
    output_folder = os.path.join(parent_folder, "processed_audio")
    os.makedirs(output_folder, exist_ok=True)  # Cria a pasta de saída, se não existir

    for i in range(1, 14):  # Itera de 1 a 13
        audio_file = f"{pattern} ({i}).wav"
        input_path = os.path.join(input_folder, audio_file)
        if os.path.exists(input_path):
            # Primeiro remove os silêncios
            temp_output = os.path.join(output_folder, f"{pattern} ({i})_temp.wav")
            final_output = os.path.join(output_folder, f"{pattern} ({i})_edited.wav")
            
            print(f"Processando áudio: {input_path}")
            # Remove silêncios
            subprocess.run([
                "auto-editor", input_path, "--silent-speed", "99999", "--video-speed", "1", "-o", temp_output
            ])
            
            # Normaliza o áudio para -14 LUFS com limite de pico em -0.1dB
            print(f"Normalizando áudio: {temp_output}")
            subprocess.run([
                "ffmpeg", "-i", temp_output,
                "-af", "loudnorm=I=-14:LRA=11:TP=-0.1",
                "-ar", "48000",
                final_output
            ])
            
            # Remove o arquivo temporário
            os.remove(temp_output)
        else:
            print(f"Arquivo não encontrado: {input_path}")

    print(f"Áudios processados e salvos em: {output_folder}")

def verificar_pastas(base_folder):
    """
    Verifica se as pastas 'narração/dariusfala/output', 'narração/hugofala/output' e 'narração/joyefala/output' existem.
    """
    pastas_necessarias = [
        os.path.join("narração", "dariusfala", "output"),
        os.path.join("narração", "hugofala", "output"),
        os.path.join("narração", "joyefala", "output")
    ]
    pastas_encontradas = []

    for pasta in pastas_necessarias:
        caminho_completo = os.path.join(base_folder, pasta)
        nome_pasta = pasta.split(os.sep)[1]  # pega 'dariusfala', 'hugofala' ou 'joyefala'
        if os.path.exists(caminho_completo):
            print(f"Pasta encontrada: {caminho_completo}")
            pastas_encontradas.append((caminho_completo, nome_pasta))
        else:
            print(f"Pasta não encontrada: {caminho_completo}")

    if len(pastas_encontradas) == len(pastas_necessarias):
        print("Todas as pastas necessárias foram encontradas. Iniciando processamento...")
    else:
        print("Nem todas as pastas foram encontradas. Processo interrompido.")
        exit()

    return pastas_encontradas

# Configuração
base_folder = os.getcwd()  # Usa o diretório atual do CMD
print(f"Diretório atual (onde o CMD foi iniciado): {base_folder}")

# Definir padrões de busca para cada pasta
padroes_nome = {
    "dariusfala": "dariuscena",
    "hugofala": "hugocena",
    "joyefala": "joyecena"
}

pastas_para_processar = verificar_pastas(base_folder)

# Processar os áudios com os padrões específicos
for caminho_completo, nome_pasta in pastas_para_processar:
    pattern = padroes_nome[nome_pasta]  # Busca o padrão correto para a pasta
    process_audio(caminho_completo, pattern)

print("Processamento concluído.")  # Mensagem de conclusão sem interrupção 