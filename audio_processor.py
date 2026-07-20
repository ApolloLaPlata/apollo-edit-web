import os
import sys

# Bibliotecas leves no topo; as pesadas ficam dentro da função de lazy load
def lazy_import():
    """
    Importa bibliotecas pesadas apenas quando o pipeline for chamado pela primeira vez.
    Usa noisereduce (Spectral Gating) + librosa + Pedalboard para máxima qualidade
    sem dependências problemáticas no Windows.
    """
    import soundfile as sf
    from gradio_client import Client, handle_file
    from pedalboard import (
        Pedalboard, Compressor, Limiter, Gain,
        HighpassFilter, LowpassFilter,
        HighShelfFilter, PeakFilter
    )
    from pedalboard.io import AudioFile
    return sf, Client, handle_file, Pedalboard, Compressor, Limiter, Gain, HighpassFilter, LowpassFilter, HighShelfFilter, PeakFilter, AudioFile


class AudioProcessor:
    def __init__(self):
        """
        Inicializa o processador de áudio com Lazy Loading.
        As bibliotecas pesadas são carregadas apenas na primeira execução.
        """
        self.modules_loaded = False
        self.sf = None
        self.Client = None
        self.handle_file = None
        self.Pedalboard = None
        self.Compressor = None
        self.Limiter = None
        self.Gain = None
        self.HighpassFilter = None
        self.LowpassFilter = None
        self.HighShelfFilter = None
        self.PeakFilter = None
        self.AudioFile = None

    def _load_modules(self):
        """Carrega as bibliotecas pesadas na RAM (lazy load)"""
        if not self.modules_loaded:
            print("[*] Carregando bibliotecas de processamento de áudio na RAM...")
            try:
                (self.sf, self.Client, self.handle_file,
                 self.Pedalboard, self.Compressor, self.Limiter, self.Gain,
                 self.HighpassFilter, self.LowpassFilter,
                 self.HighShelfFilter, self.PeakFilter,
                 self.AudioFile) = lazy_import()
                self.modules_loaded = True
                print("[*] Bibliotecas de áudio carregadas com sucesso!")
            except Exception as e:
                print(f"[!] Erro ao carregar bibliotecas de áudio: {e}")
                import traceback
                traceback.print_exc()

    def enhance_speech(self, input_path):
        """
        Aplica Restauração de Estúdio Inteligente (Adobe Podcast-like) 
        usando modelo Resemble AI da nuvem HuggingFace via Gradio.
        
        Ele destrói o ruído nativo dos TTS/RVC e reconstrói detalhamento
        nas perdas de frequências usando Redes Neurais Generativas de verdade!
        """
        self._load_modules()
        if not self.modules_loaded:
            return input_path

        print(f"🎙️ [IA Generativa] Reconstruindo Textura de Voz em: {os.path.basename(input_path)}")
        print("   ⏳ Conectando ao Supercomputador Cloud ResembleAI (isso leva ~15s)...")
        try:
            # URL Alternativa pois o 'ResembleAI/resemble-enhance' está barrando IPs por limite de cota
            client = self.Client("ArtsyVRC/resemble-enhance")
            
            # API: (audio_path, cfm_ode_solver, num_evals, temperature, denoise_before_enhancement)
            # Retorna (path_denoised, path_enhanced)
            result = client.predict(
                self.handle_file(input_path),
                "Midpoint",
                64,
                0.5,
                True,
                api_name="/predict"
            )
            
            enhanced_audio_path = result[1]  # Retorna o modelo 100% restaurado
            
            # Copiamos para não perder quando o Temp do Gradio for deletado
            dir_name = os.path.dirname(os.path.abspath(input_path))
            temp_enhanced = os.path.join(dir_name, "_temp_resemble_enhanced.wav")
            
            import shutil
            shutil.copy2(enhanced_audio_path, temp_enhanced)
            print("   ✅ Textura recriada de forma Inteligente e Sem Robôs!")
            return temp_enhanced

        except Exception as e:
            print(f"[!] Erro ao conectar com Resemble Enhance Cloud: {e}")
            import traceback
            traceback.print_exc()
            return input_path

    def apply_mastering(self, input_path, output_path,
                        compressor_threshold=-18.0, compressor_ratio=4.0,
                        hp_cutoff=80.0, lp_cutoff=12000.0, limiter_threshold=-1.0):
        """
        Aplica chain de masterização estilo rádio/podcast via Pedalboard:
        - HighPass: Remove rumble e frequências indesejadas abaixo do corte
        - Compressor: Equaliza dinâmica de volume (punch de rádio)
        - LowPass: Corta agudos metálicos/perfurantes acima do corte
        - Limiter: Protege contra clipping e normaliza o pico final
        """
        self._load_modules()
        if not self.modules_loaded:
            import shutil
            if input_path != output_path:
                shutil.copy2(input_path, output_path)
            return

        print(f"🏛️ [IA] Aplicando Masterização Estéreo Radio-Broadcast -> {os.path.basename(output_path)}")
        try:
            board = self.Pedalboard([
                # 1. HighPass: corta rumble abaixo de 80Hz
                self.HighpassFilter(cutoff_frequency_hz=float(hp_cutoff)),
                
                # 1.5. DESABAFAR (CORPO): A pedido, liberando o médio em 800Hz para tirar o "encaixotado" do excesso de processamento
                self.PeakFilter(
                    cutoff_frequency_hz=800.0,
                    gain_db=1.5,
                    q=1.0
                ),
                
                # 2. PRESENÇA LEVE: O Resemble já cria brilho, vamos apenas firmar a dicção (+2dB em vez de +4.5dB)
                self.PeakFilter(
                    cutoff_frequency_hz=3000.0,
                    gain_db=2.0,        
                    q=1.0
                ),
                
                # 3. DE-ESSER ORGÂNICO: Reduz a área onde reside o "S" (sibilância sibilante pesada criada pela IA)
                self.PeakFilter(
                    cutoff_frequency_hz=6500.0,
                    gain_db=-3.5,       # Reduz severamente a irritação do 'SSS'
                    q=1.5
                ),
                
                # 4. AR: Suavizado, apenas acima de 12kHz, longe da área dos S
                self.HighShelfFilter(
                    cutoff_frequency_hz=12000.0,
                    gain_db=1.5
                ),
                
                # 5. COMPRESSOR SUAVE: Reduzido ratio para não esmagar/estourar a voz (Radio Moderado)
                self.Compressor(
                    threshold_db=float(compressor_threshold),  # default: -18dB (agora mais relaxado)
                    ratio=float(compressor_ratio),             # default: 3.5 (era absurdo 6.0)
                    attack_ms=5.0,      
                    release_ms=100.0    
                ),
                
                # 6. GANHO COMPENSATÓRIO: Apenas o suficiente para voltar ao volume nominal (+2.5dB)
                self.Gain(gain_db=2.5),
                
                # 7. LowPass: remove asperências finais acima do limite sem afogar
                self.LowpassFilter(cutoff_frequency_hz=float(lp_cutoff)),
                
                # 8. LIMITER: Respiro mais seguro e não tão no teto
                self.Limiter(threshold_db=float(limiter_threshold))  # default: -1.5dB
            ])

            with self.AudioFile(input_path) as f:
                audio = f.read(f.frames)
                sample_rate = f.samplerate

            processed_audio = board(audio, sample_rate)

            # Bug fix: grava no mesmo diretório com nome temp explícito para evitar File Lock no Windows
            out_dir = os.path.dirname(os.path.abspath(output_path))
            temp_out = os.path.join(out_dir, "_pedalboard_mastering_temp.wav")
            with self.AudioFile(temp_out, 'w', sample_rate, processed_audio.shape[0]) as f:
                f.write(processed_audio)

            import shutil
            shutil.move(temp_out, output_path)

        except Exception as e:
            print(f"[!] Erro durante masterização Pedalboard: {e}")
            import traceback
            traceback.print_exc()
            import shutil
            if input_path != output_path:
                shutil.copy2(input_path, output_path)

    def run_pipeline(self, input_file, output_file, config=None):
        """
        Executa o pipeline completo de processamento de áudio:
        1. [OPCIONAL] Restauração Inteligente com Resemble (Textura e Remoção Generativa)
        2. Masterização Profissional Rádio-Broadcast:
           HighPass → PeakFilter (Presença) → HighShelf (Ar) → Compressor → Gain → LowPass → Limiter
        """
        if not os.path.exists(input_file):
            print(f"[!] Arquivo de entrada não encontrado: {input_file}")
            return False

        if config is None:
            config = {}

        # Parâmetros da UI — recuados cerca de 30% e relaxados para evitar "estouro"
        use_ia       = config.get("usar_speechbrain", True) # Mantemos a mesma chave pro UI Toggle
        comp_thresh  = config.get("compressor_threshold", -18.0)  # Menos pesado
        comp_ratio   = config.get("compressor_ratio", 3.5)        # Ratio mais natural
        hp           = config.get("highpass_cutoff", 80.0)
        lp           = config.get("lowpass_cutoff", 16000.0)      # Aberto até o fim
        lim_thresh   = config.get("limiter_threshold", -1.5)      # Teto suave

        # Passo 1: IA Generativa de Restauração em Nuvem (opcional)
        if use_ia:
            temp_file = self.enhance_speech(input_file)
        else:
            temp_file = input_file

        # Passo 2: Masterização Pedalboard (sempre executa se o filtro global estiver ativo)
        self.apply_mastering(
            temp_file,
            output_file,
            compressor_threshold=comp_thresh,
            compressor_ratio=comp_ratio,
            hp_cutoff=hp,
            lp_cutoff=lp,
            limiter_threshold=lim_thresh
        )

        # Remove arquivo intermediário WAV do Spectral Gate
        if temp_file != input_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass

        return True
