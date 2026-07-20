import sys
import os
os.environ["TORCHAUDIO_USE_BACKEND"] = "soundfile"
import os
import subprocess
import shutil
from pathlib import Path
from gradio_client import Client

class VideoRVCProcessor:
    def __init__(self, config_manager, logger=None):
        self.config_manager = config_manager
        self.logger = logger or print
        
    def _log(self, message):
        if hasattr(self.logger, '__call__'):
            self.logger(message)
        else:
            print(message)

    def extract_audio(self, video_path: str, temp_dir: str) -> str:
        self._log(f"Extracao de audio do video: {video_path}")
        output_audio = os.path.join(temp_dir, "original_audio.wav")
        command = [
            "ffmpeg", "-y", "-i", video_path,
            "-ac", "2", "-ar", "44100", "-vn", output_audio
        ]
        subprocess.run(command, check=True, capture_output=True)
        return output_audio

    def separate_vocals(self, audio_path: str, temp_dir: str) -> tuple:
        self._log(f"Separando vocais usando Demucs... (Pode demorar)")
        demucs_script = os.path.join(temp_dir, "run_demucs_patched.py")
        with open(demucs_script, "w") as f:
            f.write(
                "import sys\n"
                "import torchaudio\n"
                "import soundfile as sf\n"
                "def my_save(filepath, src, sample_rate, *args, **kwargs):\n"
                "    sf.write(filepath, src.cpu().numpy().T, sample_rate, subtype='PCM_16')\n"
                "torchaudio.save = my_save\n"
                "from demucs.separate import main\n"
                "if __name__ == '__main__':\n"
                "    main()\n"
            )
            
        command = [
            sys.executable, demucs_script,
            "-n", "htdemucs_ft",
            "--shifts", "3",
            "--overlap", "0.25",
            "-o", temp_dir,
            "--two-stems=vocals",
            audio_path
        ]
        try:
            # Captura stdout/stderr para logar em caso de erro real
            env = os.environ.copy()
            env["TORCHAUDIO_USE_BACKEND"] = "soundfile"
            result = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
            
            # Demucs salva na pasta nome_do_modelo/nome_do_arquivo/
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            model_dir = os.path.join(temp_dir, "htdemucs_ft", base_name)
            
            vocals_path = os.path.join(model_dir, "vocals.wav")
            background_path = os.path.join(model_dir, "no_vocals.wav")
            
            if not os.path.exists(vocals_path) or not os.path.exists(background_path):
                raise FileNotFoundError(f"Arquivos separados não encontrados em: {model_dir}")
                
            return vocals_path, background_path
            
        except subprocess.CalledProcessError as e:
            err_output = e.stderr if e.stderr else e.stdout
            self._log(f"❌ ERRO CRÍTICO NO DEMUCS (Status {e.returncode}):\n{err_output}")
            raise Exception("O isolamento de voz falhou. Instalação do Demucs pode estar incompleta ou FFmpeg incompatível.")
        except Exception as e:
            self._log(f"❌ Erro inesperado na separação: {e}")
            raise

    def process_rvc(self, vocals_path: str, temp_dir: str, character_config: dict) -> str:
        # Puxa as configs globais na hora H
        vps_config = self.config_manager.get('vps_config', {})
        rvc_mode = vps_config.get('rvc_mode', 'local')
        
        if rvc_mode == 'vps':
            applio_url = vps_config.get('applio_rvc', {}).get('url', '')
        else:
            applio_url = vps_config.get('applio_rvc_local', {}).get('url', 'http://127.0.0.1:6969')
            
        self._log(f"Processando RVC via Gradio Client no servidor ({rvc_mode.upper()}): {applio_url}...")
        
        pth_file = character_config.get("modelo_rvc", "")
        index_file = character_config.get("index_rvc", "")
        pitch = character_config.get("pitch_rvc", 0)
        index_rate = float(character_config.get("index_rate_rvc", 0.75))
        
        if not pth_file:
            raise ValueError("Personagem selecionado não possui modelo PTH configurado.")
            
        output_rvc_path = os.path.join(temp_dir, f"rvc_{os.path.basename(vocals_path)}")
        
        try:
            try:
                client = Client(applio_url, verbose=False)
            except Exception as conn_e:
                if "10061" in str(conn_e) or "Connection refused" in str(conn_e):
                    raise ConnectionError(f"O servidor RVC ({applio_url}) não está respondendo. O Pinokio Applio está ligado? Ligue-o antes de usar.")
                raise conn_e
            
            embedder_rvc = character_config.get("embedder_rvc", "contentvec")
            
            # O Passo local salva no server temporario do gradio/applio primeiro
            from gradio_client import handle_file
            upload_result = client.predict(
                upload_audio=handle_file(vocals_path),
                api_name="/save_to_wav2"
            )
            audio_path_on_server = upload_result[0]
            output_path_on_server = upload_result[1]
            
            if rvc_mode == "local":
                # Applio v3 exige caminhos relativos identicos aos da interface Gradio
                pth_file_path = f"logs\\weights\\{pth_file}" if not pth_file.startswith("logs") else pth_file
                
                index_file_path = ""
                if index_file:
                    try:
                        parts = index_file.replace("\\", "/").split("/logs/")
                        if len(parts) > 1:
                            index_file_path = "logs\\" + parts[1].replace("/", "\\")
                        else:
                            index_file_path = index_file
                    except:
                        index_file_path = index_file

                infer_kwargs = {
                    "terms_accepted": True, "param_1": pitch, "param_2": index_rate, "param_3": 1.0, "param_4": 0.33,
                    "param_5": "rmvpe", "param_6": audio_path_on_server, "param_7": output_path_on_server,
                    "param_8": pth_file_path, "param_9": index_file_path, "param_10": False,
                    "param_11": False, "param_12": 1.0, "param_13": False, "param_14": 155.0, "param_15": False,
                    "param_16": 0.5, "param_17": "WAV", "param_18": embedder_rvc, "param_19": None, "param_20": False,
                    "param_21": 1.0, "param_22": 1.0, "param_23": False, "param_24": False, "param_25": False, "param_26": False,
                    "param_27": False, "param_28": False, "param_29": False, "param_30": False, "param_31": False, 
                    "param_32": False, "param_33": False, "param_34": 0.5, "param_35": 0.5, "param_36": 0.33, "param_37": 0.4, 
                    "param_38": 1.0, "param_39": 0.0, "param_40": 0.0, "param_41": -6.0, "param_42": 0.05, 
                    "param_43": 0.0, "param_44": 25.0, "param_45": 1.0, "param_46": 0.25, "param_47": 7.0, 
                    "param_48": 0.0, "param_49": 0.5, "param_50": 8.0, "param_51": -6.0, "param_52": 0.0, 
                    "param_53": 1.0, "param_54": 1.0, "param_55": 100.0, "param_56": 0.5, "param_57": 0.0, 
                    "param_58": 0.5, "param_59": 0, "api_name": "/enforce_terms"
                }
            else:
                infer_kwargs = {
                    "terms_accepted": True, "param_1": pitch, "param_2": index_rate, "param_3": 1.0, "param_4": 0.33,
                    "param_5": 128.0, "param_6": "rmvpe", "param_7": audio_path_on_server, "param_8": output_path_on_server,
                    "param_9": pth_file, "param_10": index_file if index_file else "", "param_11": False,
                    "param_12": False, "param_13": 1.0, "param_14": False, "param_15": 0.5, "param_16": "WAV",
                    "param_17": None, "param_18": embedder_rvc, "param_19": None, "param_20": False, "param_21": 1.0,
                    "param_22": 1.0, "param_23": False, "param_24": False, "param_25": False, "param_26": False, "param_27": False,
                    "param_28": False, "param_29": False, "param_30": False, "param_31": False, "param_32": False, "param_33": False,
                    "param_34": 0.5, "param_35": 0.5, "param_36": 0.33, "param_37": 0.4, "param_38": 1.0, "param_39": 0.0, "param_40": 0.0, "param_41": -6.0,
                    "param_42": 0.05, "param_43": 0.0, "param_44": 25.0, "param_45": 1.0, "param_46": 0.25, "param_47": 7.0, "param_48": 0.0, "param_49": 0.5,
                    "param_50": 8.0, "param_51": -6.0, "param_52": 0.0, "param_53": 1.0, "param_54": 1.0, "param_55": 100.0, "param_56": 0.5, "param_57": 0.0,
                    "param_58": 0.5, "param_59": 0, "api_name": "/enforce_terms"
                }
                
            try:
                infer_result = client.predict(**infer_kwargs)
                
                audio_file = infer_result[1]
                if audio_file and hasattr(audio_file, 'name'):
                    shutil.copy2(audio_file.name, output_rvc_path)
                elif isinstance(audio_file, str) and os.path.exists(audio_file):
                    shutil.copy2(audio_file, output_rvc_path)
                else:
                    raise Exception("Arquivo de saída do RVC não encontrado (formato desconhecido).")
            except Exception as e:
                # O Applio v3 (Pinokio) gera o arquivo internamente mas barra o request de download da lib gradio_client via HTTP (403 Forbidden).
                # Sorte nossa: sabemos que a conversão rodou até o final e que a gravação já foi salva em output_path_on_server localmente!
                if "403 Forbidden" in str(e) and output_path_on_server and os.path.exists(output_path_on_server):
                    self._log(f"Contorno de erro HTTP 403 acionado. Carregando áudio diretamente do diretório local: {output_path_on_server}")
                    shutil.copy2(output_path_on_server, output_rvc_path)
                else:
                    self._log(f"Erro no Gradio Applio RVC: {e}")
                    raise
                
            return output_rvc_path
        except Exception as e:
            self._log(f"Erro no Gradio Applio RVC (Falha Geral): {e}")
            raise
            
    def mix_and_replace_video(self, video_path: str, new_vocals_path: str, bg_path: str, temp_dir: str, final_output: str):
        self._log("Misturando novo vocal com fundo original e substituindo no video...")
        
        mixed_audio = os.path.join(temp_dir, "mixed_audio.wav")
        # Mistura usando FFmpeg filter_complex amix (sem normalização automática para não cair o volume)
        mix_command = [
            "ffmpeg", "-y",
            "-i", new_vocals_path,
            "-i", bg_path,
            "-filter_complex", "amix=inputs=2:duration=longest:dropout_transition=0:normalize=0",
            "-ac", "2", "-ar", "44100",
            mixed_audio
        ]
        subprocess.run(mix_command, check=True, capture_output=True)
        
        # Substitui na track do vídeo
        replace_cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", mixed_audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            final_output
        ]
        subprocess.run(replace_cmd, check=True, capture_output=True)
        self._log(f"Processo finalizado com sucesso. Salvo em: {final_output}")
