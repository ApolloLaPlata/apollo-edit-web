import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess

class AbaFerramentas(ctk.CTkFrame):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        
        # Aplica cor azul piscina ao fundo da aba
        self.configure()
        
        # Configuração da interface
        self.criar_interface()
    
    def criar_interface(self):
        """Cria a interface da aba Ferramentas"""
        ctk.CTkLabel(self, text="🔧 Ferramentas de Edição Rápida", 
                 font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Frame esquerdo - Seleção de arquivo
        left_frame = ctk.CTkLabelFrame(main_frame, text="📁 Arquivo de Entrada")
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Seleção de vídeo
        ctk.CTkLabel(left_frame, text="🎬 Vídeo de Entrada:").pack(anchor='w', pady=2)
        self.video_path = tk.StringVar()
        ctk.CTkButton(left_frame, text="📂 Selecionar Vídeo", 
                  command=self._choose_video).pack(fill='x', pady=2)
        ctk.CTkLabel(left_frame, textvariable=self.video_path, width=400).pack(anchor='w', pady=2)
        
        # Informações do vídeo
        self.info_video = ctk.CTkLabel(left_frame, text="Informações do vídeo aparecerão aqui...")
        self.info_video.pack(anchor='w', pady=10)
        
        
        # Frame direito - Ferramentas
        right_frame = ctk.CTkLabelFrame(main_frame, text="🔧 Ferramentas Disponíveis")
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Setup do Scroll
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Status Label fora do scroll, embaixo
        self.status_label = ctk.CTkLabel(right_frame, text="Status: Aguardando seleção de vídeo...")
        self.status_label.pack(side='bottom', fill='x', pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Lista de ferramentas expandida
        ferramentas = [
            ("🖼️ Adicionar Capa", "Adiciona uma capa de 1 segundo no início do vídeo"),
            ("🔄 Inverter Vídeo", "Inverte a ordem dos frames do vídeo"),
            ("✂️ Remover Último Frame", "Remove o último frame do vídeo"),
            ("🎵 Extrair Áudio", "Extrai apenas o áudio do vídeo"),
            ("📐 Redimensionar", "Redimensiona o vídeo para novas dimensões"),
            ("⚡ Acelerar/Desacelerar", "Altera a velocidade do vídeo"),
            ("🎨 Ajustar Brilho/Contraste", "Ajusta parâmetros visuais"),
            ("🔇 Remover Áudio", "Remove o áudio do vídeo"),
            ("🔄 Rotacionar", "Rotaciona o vídeo em 90°, 180° ou 270°"),
            ("📱 Criador de Stories (30s)", "Corta automaticamente os primeiros 30 segundos do vídeo"),
            ("🗜️ Compressor de Vídeo", "Reduz o tamanho do vídeo (compressão h264/CRF-28)"),
            ("🔀 Espelhar Vídeo (Horizontal)", "Espelha o vídeo horizontalmente (hflip)"),
            ("🔕 Remover Silêncios do Áudio", "Remove partes silenciosas do áudio (usa silenceremove)"),
            ("🎬 Converter para MP4 (H.264)", "Padroniza arquivos (.mov, .mkv, .avi) para MP4 h264/aac"),
            ("📸 Extrair Frames", "Extrai 1 frame por segundo como imagem (thumbnails)"),
            ("📱 Padronizar p/ Celular (9:16)", "Força a resolução 1080x1920 adicionando bordas pretas"),
        ]
        
        for i, (nome, descricao) in enumerate(ferramentas):
            frame_ferramenta = ctk.CTkFrame(self.scrollable_frame)
            frame_ferramenta.pack(fill='x', pady=4, padx=5)
            
            ctk.CTkLabel(frame_ferramenta, text=nome, font=("Segoe UI", 9, "bold")).pack(anchor='w')
            ctk.CTkLabel(frame_ferramenta, text=descricao, font=("Segoe UI", 8), text_color='gray').pack(anchor='w')
            ctk.CTkButton(frame_ferramenta, text="Aplicar", 
                      command=lambda f=nome: self._aplicar_ferramenta(f)).pack(anchor='e', pady=2)
            ttk.Separator(self.scrollable_frame).pack(fill='x')

    
    def _choose_video(self):
        """Seleciona arquivo de vídeo"""
        filename = filedialog.askopenfilename(
            title="Selecionar Arquivo de Vídeo",
            filetypes=[
                ("Arquivos de vídeo", "*.mp4 *.avi *.mov *.mkv"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if filename:
            self.video_path.set(filename)
            self._carregar_info_video()
    
    def _carregar_info_video(self):
        """Carrega informações do vídeo selecionado"""
        try:
            if not self.video_path.get():
                return
            
            # TODO: Implementar extração de informações do vídeo usando FFprobe
            # Por enquanto, mostra apenas o nome do arquivo
            nome_arquivo = os.path.basename(self.video_path.get())
            self.info_video.config(text=f"Arquivo: {nome_arquivo}\n\nInformações detalhadas serão exibidas aqui...")
            
        except Exception as e:
            self.info_video.config(text=f"Erro ao carregar informações: {str(e)}")
    
    def _aplicar_ferramenta(self, ferramenta):
        """Aplica a ferramenta selecionada"""
        if not self.video_path.get():
            messagebox.showwarning("Aviso", "Selecione um arquivo de vídeo primeiro!")
            return
        
        try:
            self.status_label.config(text=f"Status: Aplicando {ferramenta}...")
            self.update()
            
            if ferramenta == "🖼️ Adicionar Capa":
                self._adicionar_capa()
            elif ferramenta == "🎵 Extrair Áudio":
                self._extrair_audio()
            elif ferramenta == "🔇 Remover Áudio":
                self._remover_audio()
            elif ferramenta == "🔄 Inverter Vídeo":
                self._inverter_video()
            elif ferramenta == "🔄 Rotacionar":
                self._rotacionar_video()
            elif ferramenta == "⚡ Acelerar/Desacelerar":
                self._alterar_velocidade()
            elif ferramenta == "✂️ Remover Último Frame":
                self._remover_ultimo_frame()
            elif ferramenta == "📐 Redimensionar":
                self._redimensionar_video()
            elif ferramenta == "🎨 Ajustar Brilho/Contraste":
                self._ajustar_brilho_contraste()
            elif ferramenta == "📱 Criador de Stories (30s)":
                self._criar_stories()
            elif ferramenta == "🗜️ Compressor de Vídeo":
                self._comprimir_video()
            elif ferramenta == "🔀 Espelhar Vídeo (Horizontal)":
                self._espelhar_video()
            elif ferramenta == "🔕 Remover Silêncios do Áudio":
                self._remover_silencios()
            elif ferramenta == "🎬 Converter para MP4 (H.264)":
                self._converter_mp4()
            elif ferramenta == "📸 Extrair Frames":
                self._extrair_frames()
            elif ferramenta == "📱 Padronizar p/ Celular (9:16)":
                self._padronizar_vertical()
            else:
                # TODO: Implementar lógica das outras ferramentas
                messagebox.showinfo("Sucesso", f"Ferramenta '{ferramenta}' aplicada!\n\nFuncionalidade em desenvolvimento.")
                self.status_label.config(text="Status: Ferramenta aplicada com sucesso")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro ao aplicar ferramenta: {str(e)}")
            self.status_label.config(text="Status: Erro na aplicação")

    def _extrair_audio(self):
        video_path = self.video_path.get()
        import subprocess
        
        output_path = filedialog.asksaveasfilename(
            title="Salvar Áudio Extraído",
            defaultextension=".mp3",
            filetypes=[("Áudio MP3", "*.mp3"), ("Áudio WAV", "*.wav"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Extração cancelada")
            return
            
        self.status_label.config(text="Status: Extraindo áudio via FFmpeg...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-q:a', '0', '-map', 'a',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro na extração de áudio: {result.stderr}")
            
        self.status_label.config(text="Status: Áudio extraído com sucesso!")
        messagebox.showinfo("Sucesso", f"Áudio extraído!\nSalvo em: {output_path}")

    def _remover_audio(self):
        video_path = self.video_path.get()
        import subprocess
        
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Mudo",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text="Status: Removendo áudio via FFmpeg...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-c:v', 'copy', '-an',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao remover áudio: {result.stderr}")
            
        self.status_label.config(text="Status: Vídeo mudo criado com sucesso!")
        messagebox.showinfo("Sucesso", f"Áudio removido!\nSalvo em: {output_path}")

    def _inverter_video(self):
        video_path = self.video_path.get()
        import subprocess
        
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Invertido",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text="Status: Invertendo vídeo e áudio via FFmpeg (Isso pode demorar)...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', 'reverse', '-af', 'areverse',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao inverter vídeo: {result.stderr}")
            
        self.status_label.config(text="Status: Vídeo invertido com sucesso!")
        messagebox.showinfo("Sucesso", f"Vídeo invertido!\nSalvo em: {output_path}")
    def _criar_stories(self):
        video_path = self.video_path.get()
        import subprocess
        
        output_path = filedialog.asksaveasfilename(
            title="Salvar Stories (30s)",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text="Status: Cortando os primeiros 60s via FFmpeg...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-t', '30',
            '-c', 'copy',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao criar stories: {result.stderr}")
            
        self.status_label.config(text="Status: Stories de 30s criado com sucesso!")
        messagebox.showinfo("Sucesso", f"Stories cortado (30s)!\nSalvo em: {output_path}")

    def _comprimir_video(self):
        video_path = self.video_path.get()
        import subprocess
        
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Comprimido",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text="Status: Comprimindo vídeo via FFmpeg (CRF 28, Pode demorar muito)...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro na compressão de vídeo: {result.stderr}")
            
        self.status_label.config(text="Status: Vídeo comprimido com sucesso!")
        messagebox.showinfo("Sucesso", f"Vídeo comprimido de forma otimizada!\nSalvo em: {output_path}")

    def _rotacionar_video(self):
        import tkinter.simpledialog as simpledialog
        video_path = self.video_path.get()
        import subprocess
        
        rot = simpledialog.askinteger(
            "Rotacionar", 
            "Digite 1 para rotacionar 90º Direita\nDigite 2 para rotacionar 90º Esquerda\nDigite 3 para rotacionar 180º:",
            minvalue=1, maxvalue=3
        )
        
        if rot is None:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        vf_param = "transpose=1"
        if rot == 2: vf_param = "transpose=2"
        if rot == 3: vf_param = "transpose=2,transpose=2"
            
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Rotacionado",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text="Status: Rotacionando vídeo via FFmpeg...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', vf_param, '-c:a', 'copy',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao rotacionar vídeo: {result.stderr}")
            
        self.status_label.config(text="Status: Vídeo rotacionado com sucesso!")
        messagebox.showinfo("Sucesso", f"Vídeo rotacionado!\nSalvo em: {output_path}")

    def _alterar_velocidade(self):
        import tkinter.simpledialog as simpledialog
        video_path = self.video_path.get()
        import subprocess
        
        speed = simpledialog.askfloat(
            "Velocidade", 
            "Indique o multiplicador de velocidade (Ex: 0.5 para metade, 2.0 para o dobro):",
            minvalue=0.1, maxvalue=10.0
        )
        
        if speed is None:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        v_speed = 1.0 / speed
        a_speed = speed
            
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Modificado",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text=f"Status: Aplicando velocidade ({speed}x) via FFmpeg...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-filter_complex', f'[0:v]setpts={v_speed}*PTS[v];[0:a]atempo={a_speed}[a]',
            '-map', '[v]', '-map', '[a]',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao alterar velocidade: {result.stderr}")
            
        self.status_label.config(text="Status: Velocidade alterada com sucesso!")
        messagebox.showinfo("Sucesso", f"Velocidade alterada!\nSalvo em: {output_path}")

    def _remover_ultimo_frame(self):
        video_path = self.video_path.get()
        import subprocess
        
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Cortado",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text="Status: Cortando final do vídeo (removendo 0.1s)...")
        self.update()
        
        probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        try:
            duration = float(result.stdout.strip())
            new_duration = duration - 0.1
        except:
            raise Exception("Não foi possível detectar a duração do vídeo pelo FFprobe.")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-t', str(new_duration),
            '-c', 'copy',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao remover frame: {result.stderr}")
            
        self.status_label.config(text="Status: Final removido com sucesso!")
        messagebox.showinfo("Sucesso", f"Último frame / finalzinho (0.1s) removido!\nSalvo em: {output_path}")

    def _redimensionar_video(self):
        import tkinter.simpledialog as simpledialog
        video_path = self.video_path.get()
        import subprocess
        
        largura = simpledialog.askinteger("Redimensionar", "Digite a largura (Ex: 1920):", minvalue=100)
        if not largura: return
        altura = simpledialog.askinteger("Redimensionar", "Digite a altura (Ex: 1080):", minvalue=100)
        if not altura: return
            
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Redimensionado",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text=f"Status: Redimensionando para {largura}x{altura}...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'scale={largura}:{altura}',
            '-c:a', 'copy',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao redimensionar: {result.stderr}")
            
        self.status_label.config(text="Status: Redimensionado com sucesso!")
        messagebox.showinfo("Sucesso", f"Vídeo redimensionado para {largura}x{altura}!\nSalvo em: {output_path}")

    def _ajustar_brilho_contraste(self):
        import tkinter.simpledialog as simpledialog
        video_path = self.video_path.get()
        import subprocess
        
        brilho = simpledialog.askfloat("Brilho", "Digite ajuste de brilho (-1.0 a 1.0, 0 é o original):", minvalue=-1.0, maxvalue=1.0)
        if brilho is None: return
        contraste = simpledialog.askfloat("Contraste", "Digite multiplicador de contraste (-2.0 a 2.0, 1.0 é o original):", minvalue=-2.0, maxvalue=2.0)
        if contraste is None: return
            
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Ajustado",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
            
        self.status_label.config(text="Status: Ajustando brilho e contraste (pode demorar)...")
        self.update()
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', f'eq=brightness={brilho}:contrast={contraste}',
            '-c:a', 'copy',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao ajustar brilho/contraste: {result.stderr}")
            
        self.status_label.config(text="Status: Ajustes aplicados com sucesso!")
        messagebox.showinfo("Sucesso", f"Brilho e contraste ajustados!\nSalvo em: {output_path}")
    
    def _adicionar_capa(self):
        """Adiciona uma capa de 1 segundo no início do vídeo"""
        try:
            # Selecionar arquivo de capa (imagem)
            capa_path = filedialog.askopenfilename(
                title="Selecionar Imagem da Capa",
                filetypes=[
                    ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            if not capa_path:
                self.status_label.config(text="Status: Seleção de capa cancelada")
                return
            
            # Obter informações do vídeo
            video_path = self.video_path.get()
            
            # Detectar formato do vídeo (horizontal/vertical)
            formato = self._detectar_formato_video(video_path)
            self.status_label.config(text=f"Status: Vídeo detectado como {formato}")
            self.update()
            
            # Selecionar arquivo de saída
            output_path = filedialog.asksaveasfilename(
                title="Salvar Vídeo com Capa",
                defaultextension=".mp4",
                filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
            )
            
            if not output_path:
                self.status_label.config(text="Status: Salvamento cancelado")
                return
            
            # Processar capa
            self.status_label.config(text="Status: Processando capa...")
            self.update()
            
            self._processar_capa(video_path, capa_path, output_path, formato)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar capa: {str(e)}")
            self.status_label.config(text="Status: Erro no processamento")
    
    def _detectar_formato_video(self, video_path):
        """Detecta se o vídeo é horizontal ou vertical"""
        try:
            import subprocess
            import json
            
            # Usar FFprobe para obter dimensões
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            
            # Encontrar stream de vídeo
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    width = int(stream['width'])
                    height = int(stream['height'])
                    
                    if width > height:
                        return "horizontal"
                    else:
                        return "vertical"
            
            return "horizontal"  # padrão
            
        except Exception as e:
            print(f"Erro ao detectar formato: {e}")
            return "horizontal"  # padrão em caso de erro
    
    def _processar_capa(self, video_path, capa_path, output_path, formato):
        """Processa a adição da capa ao vídeo"""
        try:
            import subprocess
            import os
            import json
            
            # Criar diretório temporário se não existir
            temp_dir = r"e:\MEUS PROGRAMAS\DESCARGA NEWS CODIGOS\Midias\Temp"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Obter dimensões do vídeo original
            self.status_label.config(text="Status: Analisando dimensões do vídeo...")
            self.update()
            
            cmd_probe = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd_probe, capture_output=True, text=True, timeout=30)
            data = json.loads(result.stdout)
            
            # Encontrar dimensões do vídeo
            video_width = None
            video_height = None
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    video_width = int(stream['width'])
                    video_height = int(stream['height'])
                    break
            
            if not video_width or not video_height:
                raise Exception("Não foi possível obter dimensões do vídeo")
            
            # Converter imagem para vídeo de 1 segundo com dimensões corretas
            capa_video = os.path.join(temp_dir, "capa_temp.mp4")
            
            self.status_label.config(text="Status: Redimensionando capa para o formato do vídeo...")
            self.update()
            
            # Comando para converter imagem em vídeo de 1 frame com redimensionamento
            cmd_capa = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', capa_path,
                '-vf', f'scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2:black',
                '-c:v', 'libx264',
                '-frames:v', '1',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                '-an',  # Sem áudio na capa
                capa_video
            ]
            
            result = subprocess.run(cmd_capa, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                raise Exception(f"Erro ao converter capa: {result.stderr}")
            
            self.status_label.config(text="Status: Concatenando capa com vídeo (preservando áudio)...")
            self.update()
            
            # Comando para concatenar capa + vídeo preservando áudio com sincronização perfeita
            cmd_concat = [
                'ffmpeg', '-y',
                '-i', capa_video,
                '-i', video_path,
                '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v];[1:a]acopy[a]',
                '-map', '[v]',
                '-map', '[a]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                '-avoid_negative_ts', 'make_zero',
                '-fflags', '+genpts',
                output_path
            ]
            
            result = subprocess.run(cmd_concat, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"Erro na concatenação: {result.stderr}")
            
            # Limpar arquivos temporários
            try:
                os.remove(capa_video)
            except:
                pass
            
            self.status_label.config(text="Status: Capa adicionada com sucesso!")
            messagebox.showinfo("Sucesso", f"Capa adicionada com sucesso!\n\nArquivo salvo em:\n{output_path}\n\nDimensões: {video_width}x{video_height}\nCapa: 1 frame (thumbnail)")
            
        except Exception as e:
            raise Exception(f"Erro no processamento: {str(e)}")

    def _espelhar_video(self):
        """Espelha o vídeo horizontalmente (hflip) via FFmpeg."""
        video_path = self.video_path.get()
        output_path = filedialog.asksaveasfilename(
            title="Salvar Vídeo Espelhado",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
        self.status_label.config(text="Status: Espelhando vídeo via FFmpeg...")
        self.update()
        cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', 'hflip', '-c:a', 'copy', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao espelhar: {result.stderr[-400:]}")
        self.status_label.config(text="Status: Vídeo espelhado com sucesso!")
        messagebox.showinfo("Sucesso", f"Vídeo espelhado!\nSalvo em: {output_path}")

    def _remover_silencios(self):
        """Remove silêncios do áudio de um arquivo de áudio/vídeo via FFmpeg silenceremove."""
        video_path = self.video_path.get()
        output_path = filedialog.asksaveasfilename(
            title="Salvar Áudio/Vídeo sem Silêncios",
            defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Áudio MP3", "*.mp3"), ("Todos", "*.*")]
        )
        if not output_path:
            self.status_label.config(text="Status: Operação cancelada")
            return
        self.status_label.config(text="Status: Removendo silêncios (pode demorar)...")
        self.update()
        # -50dB threshold, silêncios > 0.5s são removidos
        is_audio_only = output_path.lower().endswith('.mp3') or output_path.lower().endswith('.wav')
        if is_audio_only:
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-af', 'silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=-1:stop_threshold=-50dB:stop_duration=0.5',
                output_path
            ]
        else:
            # Extrai áudio, remove silêncio, remux (só áudio processado)
            cmd = [
                'ffmpeg', '-y', '-i', video_path,
                '-af', 'silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=-1:stop_threshold=-50dB:stop_duration=0.5',
                '-c:v', 'copy',
                output_path
            ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Erro ao remover silêncios: {result.stderr[-400:]}")
        self.status_label.config(text="Status: Silêncios removidos com sucesso!")
        messagebox.showinfo("Sucesso", f"Silêncios removidos!\nSalvo em: {output_path}")




    def _converter_mp4(self):
        video_path = self.video_path.get()
        import subprocess
        output_path = filedialog.asksaveasfilename(
            title="Salvar como MP4", defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4")]
        )
        if not output_path: return
        self.status_label.config(text="Status: Convertendo para MP4 (h264)...")
        self.update()
        cmd = ['ffmpeg', '-y', '-i', video_path, '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0: raise Exception(f"Erro ao converter: {result.stderr[-400:]}")
        self.status_label.config(text="Status: Convertido com sucesso!")
        messagebox.showinfo("Sucesso", f"Vídeo convertido!\nSalvo em: {output_path}")

    def _extrair_frames(self):
        video_path = self.video_path.get()
        import subprocess
        out_dir = filedialog.askdirectory(title="Selecione a pasta para salvar os frames")
        if not out_dir: return
        self.status_label.config(text="Status: Extraindo frames (1 fps)...")
        self.update()
        import os
        out_pattern = os.path.join(out_dir, "frame_%04d.jpg")
        cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', 'fps=1', out_pattern]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0: raise Exception(f"Erro ao extrair: {result.stderr[-400:]}")
        self.status_label.config(text="Status: Frames extraídos com sucesso!")
        messagebox.showinfo("Sucesso", f"Frames extraídos em:\n{out_dir}")

    def _padronizar_vertical(self):
        video_path = self.video_path.get()
        import subprocess
        output_path = filedialog.asksaveasfilename(
            title="Salvar Padronizado Vertical", defaultextension=".mp4",
            filetypes=[("Vídeos MP4", "*.mp4")]
        )
        if not output_path: return
        self.status_label.config(text="Status: Padronizando para Vertical 1080x1920...")
        self.update()
        # Filtro poderoso: redimensiona mantendo proporção, preenche com preto
        vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
        cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', vf, '-c:a', 'copy', output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0: raise Exception(f"Erro ao padronizar: {result.stderr[-400:]}")
        self.status_label.config(text="Status: Padronizado com sucesso!")
        messagebox.showinfo("Sucesso", f"Vídeo padronizado p/ 9:16!\nSalvo em: {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ferramentas Rápida")
    app = AbaFerramentas(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
