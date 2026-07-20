import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess
import random

class AbaGeracaoVideoNarrador(ctk.CTkFrame):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        # Cache de personagens carregado via config_manager
        if config_manager is not None:
            _p = config_manager.get('personagens', {})
            self.personagens_cache = dict(_p) if _p else {}
        else:
            self.personagens_cache = {}
        
        # Aplica cor azul piscina ao fundo da aba
        self.configure()

        ctk.CTkLabel(self, text="Gerador de Vídeo do Narrador", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Seleção do Personagem
        ctk.CTkLabel(self, text="Selecione o Narrador:").pack(pady=5)
        if self.personagens_cache:
            self.personagem_var = tk.StringVar(value=list(self.personagens_cache.keys())[0])
            self.personagem_menu = ctk.CTkOptionMenu(self, variable=self.personagem_var, values=list(self.personagens_cache.keys()))
            self.personagem_menu.pack(pady=5, padx=20, fill='x')
        else:
            self.personagem_var = tk.StringVar(value="Nenhum personagem disponível")
            self.personagem_menu = ctk.CTkOptionMenu(self, variable=self.personagem_var, values=["Nenhum personagem disponível"], state='disabled')
            self.personagem_menu.pack(pady=5, padx=20, fill='x')
            self.personagem_var.set("Nenhum personagem disponível")

        # Formato fixo - agora todos os vídeos são quadrados
        self.formato_var = tk.StringVar(value="quadrado")

        # Seleção de Estado Emocional
        ctk.CTkLabel(self, text="Estado Emocional:").pack(pady=5)
        self.estado_emocional_var = tk.StringVar(value="normal")
        self.estado_emocional_menu = ctk.CTkOptionMenu(self, variable=self.estado_emocional_var, 
                                                 values=["normal", "feliz", "raiva", "triste"])
        self.estado_emocional_menu.pack(pady=5, padx=20, fill='x')

        # Upload do Áudio
        self.btn_upload_audio = ctk.CTkButton(self, text="Carregar Arquivo de Áudio (.mp3)", command=self.carregar_audio)
        self.btn_upload_audio.pack(pady=10)
        self.label_audio = ctk.CTkLabel(self, text="Nenhum áudio carregado.")
        self.label_audio.pack()

        # Botão para gerar o vídeo
        self.btn_gerar = ctk.CTkButton(self, text="Gerar Vídeo do Narrador", command=self.gerar_video)
        self.btn_gerar.pack(pady=20)

    def carregar_audio(self):
        self.audio_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if self.audio_path:
            self.label_audio.config(text=os.path.basename(self.audio_path))

    def get_duration(self, filepath):
        """Retorna a duração de um arquivo de mídia usando ffprobe."""
        comando_ffprobe = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', filepath
        ]
        try:
            resultado = subprocess.run(comando_ffprobe, check=True, capture_output=True, text=True)
            return float(resultado.stdout)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("Erro", "FFprobe não encontrado ou erro ao ler o arquivo. Verifique se o FFmpeg está no PATH do sistema.")
            return None

    def gerar_video(self):
        narrador = self.personagem_var.get()
        estado_emocional = self.estado_emocional_var.get()
        
        print(f"🎬 Gerando vídeo do narrador:")
        print(f"   👤 Narrador: {narrador}")
        print(f"   😊 Estado: {estado_emocional}")
        
        # Obtém o vídeo do narrador diretamente do config.json
        try:
            if narrador not in self.personagens_cache:
                print(f"   ❌ Personagem não encontrado: {narrador}")
                messagebox.showerror("Erro", f"Personagem não encontrado: {narrador}")
                return
            
            personagem_config = self.personagens_cache[narrador]
            
            # Verifica se o estado emocional existe
            if "estados_emocionais" not in personagem_config:
                print(f"   ❌ Estados emocionais não configurados para: {narrador}")
                messagebox.showerror("Erro", f"Estados emocionais não configurados para: {narrador}")
                return
            
            if estado_emocional not in personagem_config["estados_emocionais"]:
                print(f"   ❌ Estado emocional não encontrado: {estado_emocional}")
                messagebox.showerror("Erro", f"Estado emocional não encontrado: {estado_emocional}")
                return
            
            # Obtém o vídeo do estado emocional
            video_source = personagem_config["estados_emocionais"][estado_emocional]["video_source"]
            
            if not video_source:
                print(f"   ❌ Vídeo não configurado para {narrador} - {estado_emocional}")
                messagebox.showerror("Erro", f"Vídeo não configurado para {narrador} - {estado_emocional}")
                return
            
            print(f"   ✅ Vídeo encontrado: {video_source}")
            
        except Exception as e:
            print(f"   ❌ Erro ao buscar vídeo: {e}")
            messagebox.showerror("Erro", f"Erro ao buscar vídeo do narrador: {str(e)}")
            return

        if not self.audio_path:
            messagebox.showerror("Erro", "Carregue um arquivo de áudio primeiro.")
            return

        # Verifica se o arquivo de vídeo existe
        if not os.path.exists(video_source):
            print(f"   ❌ Arquivo de vídeo não existe: {video_source}")
            messagebox.showerror("Erro", f"Arquivo de vídeo não encontrado:\n{video_source}")
            return

        duracao_audio = self.get_duration(self.audio_path)
        duracao_video_total = self.get_duration(video_source)

        if duracao_audio is None or duracao_video_total is None:
            return

        if duracao_audio > duracao_video_total:
            messagebox.showerror("Erro", f"O áudio ({duracao_audio:.1f}s) é mais longo que o vídeo ({duracao_video_total:.1f}s).")
            return

        # Calcula um ponto de início aleatório para o clipe de vídeo
        max_start_time = duracao_video_total - duracao_audio
        start_time = random.uniform(0, max_start_time)
        
        print(f"   ⏱️ Duração do áudio: {duracao_audio:.2f}s")
        print(f"   ⏱️ Duração do vídeo: {duracao_video_total:.2f}s")
        print(f"   🎲 Ponto de início: {start_time:.2f}s")

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("MOV files", "*.mov"), ("All files", "*.*")],
            title="Salvar Vídeo do Narrador Como..."
        )
        if not output_path:
            return

        print(f"   💾 Salvando em: {output_path}")

        # Comando FFmpeg para cortar o vídeo e substituir o áudio
        # CORREÇÃO: Usar filter_complex para corte preciso
        comando_ffmpeg = [
            'ffmpeg',
            '-i', video_source,          # Vídeo de origem (MP4)
            '-i', self.audio_path,       # Áudio a ser inserido
            '-filter_complex', f'[0:v]trim=start={start_time}:duration={duracao_audio},setpts=PTS-STARTPTS[v]',
            '-map', '[v]',               # Mapeia o vídeo filtrado
            '-map', '1:a',               # Mapeia o áudio do segundo input
            '-c:v', 'libx264',           # Recodifica o vídeo para garantir compatibilidade
            '-preset', 'superfast',      # Preset muito rápido para codificação (Otimização)
            '-c:a', 'aac',               # Codifica o áudio para AAC
            '-b:a', '128k',              # Bitrate do áudio
            '-shortest',                 # Termina quando o input mais curto acabar
            output_path,                 # Saída em MP4
            '-y'                         # Sobrescreve o arquivo se existir
        ]

        try:
            print(f"   🔧 Executando comando FFmpeg...")
            resultado = subprocess.run(comando_ffmpeg, check=True, capture_output=True, text=True)
            print(f"   ✅ FFmpeg executado com sucesso")
            
            # Verifica se o arquivo foi criado e tem tamanho > 0
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                # Verifica a duração do arquivo gerado
                duracao_gerado = self.get_duration(output_path)
                if duracao_gerado:
                    print(f"   ✅ Arquivo gerado com sucesso:")
                    print(f"      📁 Tamanho: {os.path.getsize(output_path)} bytes")
                    print(f"      ⏱️ Duração: {duracao_gerado:.2f}s")
                    print(f"      🎯 Duração esperada: {duracao_audio:.2f}s")
                    
                    if abs(duracao_gerado - duracao_audio) < 0.1:
                        print(f"      ✅ Duração correta!")
                        messagebox.showinfo("Sucesso", f"Vídeo do narrador gerado com sucesso em:\n{output_path}\n\nDuração: {duracao_gerado:.2f}s")
                    else:
                        print(f"      ⚠️ Duração diferente do esperado!")
                        messagebox.showwarning("Atenção", f"Vídeo gerado, mas com duração diferente:\nEsperado: {duracao_audio:.2f}s\nGerado: {duracao_gerado:.2f}s")
                else:
                    print(f"   ⚠️ Arquivo gerado mas não foi possível verificar a duração")
                    messagebox.showinfo("Sucesso", f"Vídeo do narrador gerado em:\n{output_path}")
            else:
                print(f"   ❌ Arquivo não foi criado ou está vazio")
                messagebox.showerror("Erro", "Arquivo não foi criado corretamente")
                
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro no FFmpeg: {e}")
            print(f"   📋 Comando executado: {' '.join(comando_ffmpeg)}")
            if e.stderr:
                print(f"   🔍 Erro detalhado: {e.stderr}")
            if e.stdout:
                print(f"   📤 Saída: {e.stdout}")
            messagebox.showerror("Erro no FFmpeg", f"Falha ao gerar o vídeo do narrador.\n\nErro: {e}\n\nComando: {' '.join(comando_ffmpeg)}")
        except Exception as e:
            print(f"   ❌ Erro inesperado: {e}")
            messagebox.showerror("Erro", f"Erro inesperado ao gerar vídeo: {str(e)}")


# --- DIALOGS ---