import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess

class AbaControleVolume(ctk.CTkFrame):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        
        # Aplica cor azul piscina ao fundo da aba
        self.configure()
        
        # Lista de vídeos selecionados
        self.videos_selecionados = []
        
        # Configuração da interface
        self.criar_interface()
    
    def criar_interface(self):
        """Cria a interface da aba Controle de Volume"""
        ctk.CTkLabel(self, text="🔊 Controle de Volume - Ajustar Volume dos Blocos", 
                 font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Frame esquerdo - Seleção de vídeos
        left_frame = ctk.CTkLabelFrame(main_frame, text="📁 Seleção de Blocos")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Botão para selecionar vídeos
        ctk.CTkButton(left_frame, text="📂 Selecionar Blocos", 
                  command=self.selecionar_videos).pack(fill='x', pady=5)
        
        # Lista de vídeos selecionados com miniaturas
        ctk.CTkLabel(left_frame, text="Blocos Selecionados:").pack(anchor='w', pady=(10, 5))
        
        # Frame para a lista com scroll
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill='both', expand=True)
        
        # Canvas para scroll com miniaturas
        self.canvas = tk.Canvas(list_frame, height=400)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Lista para armazenar as miniaturas
        self.miniaturas = []
        
        # Botão para limpar seleção
        ctk.CTkButton(left_frame, text="🗑️ Limpar Seleção", 
                  command=self.limpar_selecao).pack(fill='x', pady=5)
        
        # Frame direito - Configurações de Volume
        right_frame = ctk.CTkLabelFrame(main_frame, text="🔊 Configurações de Volume")
        right_frame.pack(side='right', fill='y')
        
        # Tipo de ajuste de volume
        ctk.CTkLabel(right_frame, text="🎛️ Tipo de Ajuste:").pack(anchor='w', pady=(0, 5))
        self.tipo_ajuste = tk.StringVar(value='aumentar')
        ttk.Radiobutton(right_frame, text="Aumentar Volume", variable=self.tipo_ajuste, 
                       value='aumentar').pack(anchor='w')
        ttk.Radiobutton(right_frame, text="Reduzir Volume", variable=self.tipo_ajuste, 
                       value='reduzir').pack(anchor='w')
        ttk.Radiobutton(right_frame, text="Volume Específico", variable=self.tipo_ajuste, 
                       value='especifico').pack(anchor='w')
        
        # Valor do ajuste
        ctk.CTkLabel(right_frame, text="🔊 Valor (dB):").pack(anchor='w', pady=(10, 5))
        self.valor_volume = tk.DoubleVar(value=7.5)
        self.volume_scale = ttk.Scale(right_frame, from_=-60, to=60, variable=self.valor_volume, orient='horizontal')
        self.volume_scale.pack(fill='x', pady=(0, 5))
        self.volume_label = ctk.CTkLabel(right_frame, text="3.0 dB")
        self.volume_label.pack()
        self.volume_scale.configure(command=lambda v: self.volume_label.configure(text=f"{float(v):.1f} dB"))
        
        # --- SEÇÃO DE MÚSICA DE FUNDO ---
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=15)
        ctk.CTkLabel(right_frame, text="🎵 Música de Fundo", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(0, 10))
        
        # Canal 1
        canal1_frame = ctk.CTkLabelFrame(right_frame, text="🎵 Canal 1")
        canal1_frame.pack(fill='x', pady=5)
        self.musica1_path = tk.StringVar()
        ctk.CTkButton(canal1_frame, text="📂 Selecionar Música 1", 
                  command=lambda: self.selecionar_musica(1)).pack(fill='x', pady=2)
        ctk.CTkLabel(canal1_frame, textvariable=self.musica1_path, font=("Segoe UI", 8)).pack(anchor='w')
        
        self.volume_musica1 = tk.DoubleVar(value=-9.0)
        vol1_frame = ctk.CTkFrame(canal1_frame)
        vol1_frame.pack(fill='x', pady=(5, 0))
        ctk.CTkLabel(vol1_frame, text="Volume:").pack(side='left')
        self.lbl_vol1 = ctk.CTkLabel(vol1_frame, text="0.0 dB", width=80) # Label para mostrar dB
        self.lbl_vol1.pack(side='right')
        
        scale1 = ttk.Scale(canal1_frame, from_=-60, to=20, variable=self.volume_musica1, orient='horizontal')
        scale1.pack(fill='x')
        scale1.configure(command=lambda v: self.lbl_vol1.configure(text=f"{float(v):.1f} dB"))
        
        # Canal 2
        canal2_frame = ctk.CTkLabelFrame(right_frame, text="🎵 Canal 2")
        canal2_frame.pack(fill='x', pady=5)
        self.musica2_path = tk.StringVar()
        ctk.CTkButton(canal2_frame, text="📂 Selecionar Música 2", 
                  command=lambda: self.selecionar_musica(2)).pack(fill='x', pady=2)
        ctk.CTkLabel(canal2_frame, textvariable=self.musica2_path, font=("Segoe UI", 8)).pack(anchor='w')
        
        self.volume_musica2 = tk.DoubleVar(value=0.0)
        vol2_frame = ctk.CTkFrame(canal2_frame)
        vol2_frame.pack(fill='x', pady=(5, 0))
        ctk.CTkLabel(vol2_frame, text="Volume:").pack(side='left')
        self.lbl_vol2 = ctk.CTkLabel(vol2_frame, text="0.0 dB", width=80) # Label para mostrar dB
        self.lbl_vol2.pack(side='right')

        scale2 = ttk.Scale(canal2_frame, from_=-60, to=20, variable=self.volume_musica2, orient='horizontal')
        scale2.pack(fill='x')
        scale2.configure(command=lambda v: self.lbl_vol2.configure(text=f"{float(v):.1f} dB"))
        
        # Canal 3
        canal3_frame = ctk.CTkLabelFrame(right_frame, text="🎵 Canal 3")
        canal3_frame.pack(fill='x', pady=5)
        self.musica3_path = tk.StringVar()
        ctk.CTkButton(canal3_frame, text="📂 Selecionar Música 3", 
                  command=lambda: self.selecionar_musica(3)).pack(fill='x', pady=2)
        ctk.CTkLabel(canal3_frame, textvariable=self.musica3_path, font=("Segoe UI", 8)).pack(anchor='w')
        
        self.volume_musica3 = tk.DoubleVar(value=0.0)
        vol3_frame = ctk.CTkFrame(canal3_frame)
        vol3_frame.pack(fill='x', pady=(5, 0))
        ctk.CTkLabel(vol3_frame, text="Volume:").pack(side='left')
        self.lbl_vol3 = ctk.CTkLabel(vol3_frame, text="0.0 dB", width=80) # Label para mostrar dB
        self.lbl_vol3.pack(side='right')

        scale3 = ttk.Scale(canal3_frame, from_=-60, to=20, variable=self.volume_musica3, orient='horizontal')
        scale3.pack(fill='x')
        scale3.configure(command=lambda v: self.lbl_vol3.configure(text=f"{float(v):.1f} dB"))
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Aplicar a todos os blocos
        ctk.CTkLabel(right_frame, text="📋 Aplicar a:").pack(anchor='w', pady=(10, 5))
        self.aplicar_todos = tk.BooleanVar(value=True)
        ctk.CTkSwitch(right_frame, text="Todos os blocos selecionados", 
                       variable=self.aplicar_todos).pack(anchor='w')
        
        # Botão de processamento
        ctk.CTkButton(right_frame, text="🚀 Aplicar Ajuste de Volume", 
                  command=self.aplicar_ajuste_volume).pack(fill='x', pady=10)
        
        # Barra de progresso
        self.progresso = ttk.Progressbar(right_frame, mode='determinate')
        self.progresso.pack(fill='x', pady=5)
        
        # Label de status
        self.status_label = ctk.CTkLabel(right_frame, text="Pronto para processar", text_color='green')
        self.status_label.pack(pady=5)
    
    def selecionar_videos(self):
        """Seleciona múltiplos vídeos para ajuste de volume"""
        arquivos = filedialog.askopenfilenames(
            title="Selecionar Blocos para Ajuste de Volume",
            filetypes=[("Vídeos", "*.mp4 *.mov *.avi"), ("Todos", "*.*")]
        )
        
        if arquivos:
            self.videos_selecionados = list(arquivos)
            self.atualizar_lista_videos()
            self.status_label.config(text=f"{len(self.videos_selecionados)} blocos selecionados", text_color='blue')
    
    def atualizar_lista_videos(self):
        """Atualiza a lista de vídeos com miniaturas"""
        # Limpa miniaturas existentes
        for miniatura in self.miniaturas:
            miniatura.destroy()
        self.miniaturas.clear()
        
        # Limpa frame scrollável
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.videos_selecionados:
            return
        
        # Cria miniaturas para cada vídeo
        for i, video_path in enumerate(self.videos_selecionados):
            try:
                # Frame para cada vídeo
                video_frame = ctk.CTkFrame(self.scrollable_frame)
                video_frame.pack(fill='x', pady=2, padx=5)
                
                # Nome do arquivo
                nome_arquivo = os.path.basename(video_path)
                ctk.CTkLabel(video_frame, text=nome_arquivo, font=("Segoe UI", 9)).pack(anchor='w')
                
                # Caminho completo (truncado)
                caminho_truncado = video_path[:50] + "..." if len(video_path) > 50 else video_path
                ctk.CTkLabel(video_frame, text=caminho_truncado, font=("Segoe UI", 8), text_color='gray').pack(anchor='w')
                
                # Separador
                ttk.Separator(video_frame, orient='horizontal').pack(fill='x', pady=2)
                
                self.miniaturas.append(video_frame)
                
            except Exception as e:
                print(f"Erro ao criar miniatura para {video_path}: {e}")
    
    def limpar_selecao(self):
        """Limpa a seleção de vídeos"""
        self.videos_selecionados.clear()
        self.atualizar_lista_videos()
        self.status_label.config(text="Pronto para processar", text_color='green')
    
    def selecionar_musica(self, canal):
        """Seleciona arquivo de música para o canal especificado"""
        arquivo = filedialog.askopenfilename(
            title=f"Selecionar Música para Canal {canal}",
            filetypes=[("Áudio", "*.mp3 *.wav *.aac *.m4a"), ("Todos", "*.*")]
        )
        if arquivo:
            if canal == 1:
                self.musica1_path.set(arquivo)
            elif canal == 2:
                self.musica2_path.set(arquivo)
            elif canal == 3:
                self.musica3_path.set(arquivo)
    
    def aplicar_ajuste_volume(self):
        """Aplica o ajuste de volume aos vídeos selecionados"""
        if not self.videos_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um bloco para ajustar o volume.")
            return
        
        # Verifica se há músicas selecionadas
        musicas_selecionadas = []
        if self.musica1_path.get():
            musicas_selecionadas.append((self.musica1_path.get(), self.volume_musica1.get()))
        if self.musica2_path.get():
            musicas_selecionadas.append((self.musica2_path.get(), self.volume_musica2.get()))
        if self.musica3_path.get():
            musicas_selecionadas.append((self.musica3_path.get(), self.volume_musica3.get()))
        
        # Confirma a operação
        mensagem_confirmacao = f"Aplicar ajuste de volume a {len(self.videos_selecionados)} blocos?\n\n"
        mensagem_confirmacao += f"Tipo: {self.tipo_ajuste.get()}\n"
        mensagem_confirmacao += f"Valor: {self.valor_volume.get():.1f} dB"
        
        if musicas_selecionadas:
            mensagem_confirmacao += f"\n\nMúsicas de fundo: {len(musicas_selecionadas)} canal(is)"
        
        confirmacao = messagebox.askyesno("Confirmar Ajuste de Volume", mensagem_confirmacao)
        
        if not confirmacao:
            return
        
        try:
            self.status_label.config(text="Processando...", text_color='orange')
            self.progresso['value'] = 0
            self.progresso['maximum'] = len(self.videos_selecionados)
            
            for i, video_path in enumerate(self.videos_selecionados):
                self.progresso['value'] = i + 1
                self.progresso.update()
                
                if musicas_selecionadas:
                    self.ajustar_volume_video_com_musica(video_path, musicas_selecionadas)
                else:
                    self.ajustar_volume_video(video_path)
            
            self.status_label.config(text="Processamento concluído com sucesso!", text_color='green')
            messagebox.showinfo("Sucesso", f"Processamento concluído em {len(self.videos_selecionados)} blocos!")
            
        except Exception as e:
            self.status_label.config(text=f"Erro: {str(e)}", text_color='red')
            messagebox.showerror("Erro", f"Falha no processamento: {str(e)}")
    
    def ajustar_volume_video(self, video_path):
        """Ajusta o volume de um vídeo específico"""
        try:
            # Cria nome para o arquivo de saída
            nome_base = os.path.splitext(os.path.basename(video_path))[0]
            diretorio = os.path.dirname(video_path)
            extensao = os.path.splitext(video_path)[1]
            
            # Nome do arquivo de saída
            if self.tipo_ajuste.get() == 'aumentar':
                sufixo = f"_volume_+{self.valor_volume.get():.1f}dB"
            elif self.tipo_ajuste.get() == 'reduzir':
                sufixo = f"_volume_-{self.valor_volume.get():.1f}dB"
            else:  # específico
                sufixo = f"_volume_{self.valor_volume.get():.1f}dB"
            
            output_path = os.path.join(diretorio, f"{nome_base}{sufixo}{extensao}")
            
            # Determina resolucao alvo baseada no video original
            import subprocess, json
            alvo_w, alvo_h = 1080, 1920 # Default vertical
            try:
                probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', video_path]
                probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
                if probe_res.returncode == 0:
                    v_info = json.loads(probe_res.stdout)
                    vw = int(v_info['streams'][0]['width'])
                    vh = int(v_info['streams'][0]['height'])
                    if vw > vh:
                        alvo_w, alvo_h = 1920, 1080
                    elif vw == vh:
                        alvo_w, alvo_h = 1080, 1080
            except:
                pass
            
            vf_scale = f'scale={alvo_w}:{alvo_h}:force_original_aspect_ratio=decrease,pad={alvo_w}:{alvo_h}:(ow-iw)/2:(oh-ih)/2:black'
            
            import hardware_detector
            encoder = hardware_detector.detect_h264_encoder()
            video_codec = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast'] if encoder == 'libx264' else ['-c:v', encoder, '-b:v', '6M', '-pix_fmt', 'yuv420p']
            
            # Comando FFmpeg para ajustar volume
            if self.tipo_ajuste.get() == 'aumentar':
                # Aumenta volume
                comando = [
                    'ffmpeg', '-y', '-threads', '0', '-hwaccel', 'auto', '-i', video_path,
                    '-filter:a', f'volume={self.valor_volume.get():.1f}dB',
                    '-vf', vf_scale
                ] + video_codec + [output_path]
            elif self.tipo_ajuste.get() == 'reduzir':
                # Reduz volume
                comando = [
                    'ffmpeg', '-y', '-threads', '0', '-hwaccel', 'auto', '-i', video_path,
                    '-filter:a', f'volume={-self.valor_volume.get():.1f}dB',
                    '-vf', vf_scale
                ] + video_codec + [output_path]
            else:  # específico
                # Define volume específico
                comando = [
                    'ffmpeg', '-y', '-threads', '0', '-hwaccel', 'auto', '-i', video_path,
                    '-filter:a', f'volume={self.valor_volume.get():.1f}dB',
                    '-vf', vf_scale
                ] + video_codec + [output_path]
            
            # Executa o comando
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print(f"✅ Volume ajustado: {os.path.basename(output_path)}")
            else:
                print(f"❌ Erro ao ajustar volume: {resultado.stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao processar {video_path}: {e}")
    
    def ajustar_volume_video_com_musica(self, video_path, musicas_selecionadas):
        """Ajusta o volume de um vídeo e adiciona músicas de fundo"""
        try:
            # Cria nome para o arquivo de saída
            nome_base = os.path.splitext(os.path.basename(video_path))[0]
            diretorio = os.path.dirname(video_path)
            extensao = os.path.splitext(video_path)[1]
            
            # Nome do arquivo de saída
            if self.tipo_ajuste.get() == 'aumentar':
                sufixo = f"_volume_+{self.valor_volume.get():.1f}dB_com_musica"
            elif self.tipo_ajuste.get() == 'reduzir':
                sufixo = f"_volume_-{self.valor_volume.get():.1f}dB_com_musica"
            else:  # específico
                sufixo = f"_volume_{self.valor_volume.get():.1f}dB_com_musica"
            
            output_path = os.path.join(diretorio, f"{nome_base}{sufixo}{extensao}")
            
            # Determina resolucao alvo baseada no video original
            import subprocess, json
            alvo_w, alvo_h = 1080, 1920 # Default vertical
            try:
                probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', video_path]
                probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
                if probe_res.returncode == 0:
                    v_info = json.loads(probe_res.stdout)
                    vw = int(v_info['streams'][0]['width'])
                    vh = int(v_info['streams'][0]['height'])
                    if vw > vh:
                        alvo_w, alvo_h = 1920, 1080
                    elif vw == vh:
                        alvo_w, alvo_h = 1080, 1080
            except:
                pass
            
            vf_scale = f'scale={alvo_w}:{alvo_h}:force_original_aspect_ratio=decrease,pad={alvo_w}:{alvo_h}:(ow-iw)/2:(oh-ih)/2:black'
            
            # Constrói o comando FFmpeg com filtros complexos
            comando = ['ffmpeg', '-y', '-threads', '0']
            
            # Adiciona input do vídeo
            comando.extend(['-hwaccel', 'auto', '-i', video_path])
            
            # Adiciona inputs das músicas
            for musica_path, _ in musicas_selecionadas:
                comando.extend(['-i', musica_path])
            
            # Constrói o filtro de áudio complexo
            filtro_audio = []
            
            # Filtro para o áudio do vídeo (com ajuste de volume)
            if self.tipo_ajuste.get() == 'aumentar':
                filtro_audio.append(f"[0:a]volume={self.valor_volume.get():.1f}dB[a_video]")
            elif self.tipo_ajuste.get() == 'reduzir':
                filtro_audio.append(f"[0:a]volume={-self.valor_volume.get():.1f}dB[a_video]")
            else:  # específico
                filtro_audio.append(f"[0:a]volume={self.valor_volume.get():.1f}dB[a_video]")
            
            # Filtros para as músicas (com volumes individuais)
            for i, (_, volume_musica) in enumerate(musicas_selecionadas):
                filtro_audio.append(f"[{i+1}:a]volume={volume_musica}dB[a_musica{i+1}]")
            
            # Mixagem de todos os áudios
            inputs_audio = "[a_video]"
            for i in range(len(musicas_selecionadas)):
                inputs_audio += f"[a_musica{i+1}]"
            
            filtro_audio.append(f"{inputs_audio}amix=inputs={len(musicas_selecionadas)+1}:duration=first:dropout_transition=0:normalize=0[a_final]")
            
            import hardware_detector
            encoder = hardware_detector.detect_h264_encoder()
            video_codec = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast'] if encoder == 'libx264' else ['-c:v', encoder, '-b:v', '6M', '-pix_fmt', 'yuv420p']
            
            # Comando completo
            comando.extend([
                '-filter_complex', ';'.join(filtro_audio),
                '-map', '0:v',  # Mapeia vídeo do primeiro input
                '-map', '[a_final]',  # Mapeia áudio final
                '-vf', vf_scale
            ] + video_codec + [
                '-c:a', 'aac', '-b:a', '192k',  # Recodifica áudio
                output_path
            ])
            
            # Executa o comando
            resultado = subprocess.run(comando, capture_output=True, text=True)
            
            if resultado.returncode == 0:
                print(f"✅ Vídeo com música processado: {os.path.basename(output_path)}")
            else:
                print(f"❌ Erro ao processar vídeo com música: {resultado.stderr}")
                
        except Exception as e:
            print(f"❌ Erro ao processar {video_path} com música: {e}")


# --- ABA 6: TRANSITION ---