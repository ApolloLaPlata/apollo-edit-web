import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import random
import threading
import subprocess

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class AbaTransition(ctk.CTkFrame):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        
        # Aplica cor azul piscina ao fundo da aba
        self.configure()
        
        # Cache de configurações
        self.cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_montador.json")
        
        # Pastas como StringVars (editáveis pela UI)
        self.pasta_trans_h = tk.StringVar()
        self.pasta_trans_v = tk.StringVar()
        self.pasta_cta_h = tk.StringVar()
        self.pasta_cta_v = tk.StringVar()
        self.pasta_logo_h = tk.StringVar()
        self.pasta_logo_v = tk.StringVar()
        
        # Lista de vídeos selecionados
        self.videos_selecionados = []
        
        # Configuração da interface
        self.criar_interface()
        self._carregar_cache_montador()
        self._setup_autosave_montador()
    
    def criar_interface(self):
        """Cria a interface da aba Transition"""
        ctk.CTkLabel(self, text="🎬 Transition - Adicionar Transições e Logomarcas", 
                 font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Frame esquerdo - Seleção de vídeos
        left_frame = ctk.CTkLabelFrame(main_frame, text="📁 Seleção de Vídeos")
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Botão para selecionar vídeos
        ctk.CTkButton(left_frame, text="📂 Selecionar Vídeos", 
                  command=self.selecionar_videos).pack(fill='x', pady=12)
        
        # Lista de vídeos selecionados com miniaturas
        ctk.CTkLabel(left_frame, text="Vídeos Selecionados:").pack(anchor='w', pady=(20, 10))
        
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
                  command=self.limpar_selecao).pack(fill='x', pady=12)
        
        # Frame direito - Configurações
        right_frame = ctk.CTkLabelFrame(main_frame, text="⚙️ Configurações")
        right_frame.pack(side='right', fill='y')
        
        # Formato
        ctk.CTkLabel(right_frame, text="📐 Formato:").pack(anchor='w', pady=(0, 5))
        self.formato_var = tk.StringVar(value='horizontal')
        formato_frame = ctk.CTkFrame(right_frame)
        formato_frame.pack(fill='x', pady=(0, 10))
        ttk.Radiobutton(formato_frame, text="Horizontal", variable=self.formato_var, 
                       value='horizontal').pack(side='left')
        ttk.Radiobutton(formato_frame, text="Vertical", variable=self.formato_var, 
                       value='vertical').pack(side='left')
        
        # Sequência de Processamento
        ctk.CTkLabel(right_frame, text="🎬 Adicionar ao Final (Sequência):").pack(anchor='w', pady=(20, 10))
        self.var_transicao = tk.BooleanVar(value=True)
        self.var_cta = tk.BooleanVar(value=False)
        self.var_logomarca = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(right_frame, text="1. Transição", variable=self.var_transicao).pack(anchor='w', pady=2)
        ctk.CTkCheckBox(right_frame, text="2. Somente CTA", variable=self.var_cta).pack(anchor='w', pady=2)
        ctk.CTkCheckBox(right_frame, text="3. Logomarca com CTA", variable=self.var_logomarca).pack(anchor='w', pady=2)

        # Fase 27: Pastas configuráveis via UI
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', pady=20)
        ctk.CTkLabel(right_frame, text="📁 Pastas de Transições Longas:", font=("Segoe UI", 9, "bold")).pack(anchor='w')
        
        def _add_pasta_row(parent, label, var):
            f = ctk.CTkFrame(parent)
            f.pack(fill='x', pady=2)
            ctk.CTkLabel(f, text=label, width=100).pack(side='left')
            ctk.CTkEntry(f, textvariable=var, width=180).pack(side='left', padx=2)
            ctk.CTkButton(f, text="...", width=30, command=lambda v=var: v.set(filedialog.askdirectory() or v.get())).pack(side='left')
        
        _add_pasta_row(right_frame, "H (Trans):", self.pasta_trans_h)
        _add_pasta_row(right_frame, "V (Trans):", self.pasta_trans_v)
        
        ctk.CTkLabel(right_frame, text="📁 Pastas de Somente CTA:", font=("Segoe UI", 9, "bold")).pack(anchor='w', pady=(8,0))
        _add_pasta_row(right_frame, "H (CTA):", self.pasta_cta_h)
        _add_pasta_row(right_frame, "V (CTA):", self.pasta_cta_v)
        
        ctk.CTkLabel(right_frame, text="📁 Pastas de Logomarcas com CTA:", font=("Segoe UI", 9, "bold")).pack(anchor='w', pady=(8,0))
        _add_pasta_row(right_frame, "H (Logo):", self.pasta_logo_h)
        _add_pasta_row(right_frame, "V (Logo):", self.pasta_logo_v)
        # Botão de processamento
        ctk.CTkButton(right_frame, text="🚀 Processar Vídeos", 
                  command=self.processar_videos).pack(fill='x', pady=20)
        
        # Status
        self.status_label = ctk.CTkLabel(right_frame, text="Status: Aguardando seleção de vídeos...")
        self.status_label.pack(pady=20)
        
        # Informações das pastas
        self.info_label = ctk.CTkLabel(right_frame, text="", font=("Segoe UI", 8))
        self.info_label.pack(pady=12)

    def _setup_autosave_montador(self):
        for v in [self.pasta_trans_h, self.pasta_trans_v, self.pasta_cta_h, self.pasta_cta_v, self.pasta_logo_h, self.pasta_logo_v]:
            v.trace_add('write', lambda *a: self._salvar_cache_montador())

    def _salvar_cache_montador(self):
        try:
            data = {
                'pasta_trans_h': self.pasta_trans_h.get(),
                'pasta_trans_v': self.pasta_trans_v.get(),
                'pasta_logo_h': self.pasta_logo_h.get(),
                'pasta_logo_v': self.pasta_logo_v.get(),
                'pasta_cta_h': self.pasta_cta_h.get(),
                'pasta_cta_v': self.pasta_cta_v.get(),
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except: pass

    def _carregar_cache_montador(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.pasta_trans_h.set(data.get('pasta_trans_h', ''))
                self.pasta_trans_v.set(data.get('pasta_trans_v', ''))
                self.pasta_logo_h.set(data.get('pasta_logo_h', ''))
                self.pasta_logo_v.set(data.get('pasta_logo_v', ''))
                self.pasta_cta_h.set(data.get('pasta_cta_h', ''))
                self.pasta_cta_v.set(data.get('pasta_cta_v', ''))
                self.verificar_pastas_logomarcas()
            except: pass
    
    def selecionar_videos(self):
        """Seleciona múltiplos vídeos"""
        try:
            videos = filedialog.askopenfilenames(
                title="Selecionar Vídeos para Processar",
                filetypes=[
                    ("Vídeos", "*.mp4 *.avi *.mov *.mkv"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            if videos:
                for video_path in videos:
                    if video_path not in self.videos_selecionados:
                        self.videos_selecionados.append(video_path)
                        self.criar_miniatura(video_path, len(self.videos_selecionados))
                
                self.status_label.config(text=f"Status: {len(self.videos_selecionados)} vídeos selecionados")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao selecionar vídeos: {str(e)}")
    
    def criar_miniatura(self, video_path, numero):
        """Cria uma miniatura do vídeo e adiciona à lista"""
        try:
            # Cria um frame para a miniatura
            miniatura_frame = ctk.CTkFrame(self.scrollable_frame)
            miniatura_frame.pack(fill='x', padx=15, pady=2)
            
            # Tenta múltiplas estratégias para extrair miniatura
            thumbnail_path = self.extrair_miniatura_robusta(video_path, numero)
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                # Carrega a miniatura
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(thumbnail_path)
                        photo = ImageTk.PhotoImage(img)
                        
                        # Cria o label da miniatura
                        thumb_label = ctk.CTkLabel(miniatura_frame, image=photo)
                        thumb_label.image = photo  # Mantém referência
                        thumb_label.pack(side='left', padx=15, pady=12)
                        
                        # Informações do vídeo
                        info_frame = ctk.CTkFrame(miniatura_frame)
                        info_frame.pack(side='left', fill='x', expand=True, padx=15, pady=12)
                        
                        nome_arquivo = os.path.basename(video_path)
                        ctk.CTkLabel(info_frame, text=f"{numero}. {nome_arquivo}", 
                                 font=("Segoe UI", 9, "bold")).pack(anchor='w')
                        
                        # Duração do vídeo
                        duracao = self.get_video_duration(video_path)
                        if duracao:
                            ctk.CTkLabel(info_frame, text=f"⏱️ {duracao:.1f}s", 
                                     font=("Segoe UI", 8), text_color='gray').pack(anchor='w')
                        
                        # Botão de remoção
                        btn_remover = ctk.CTkButton(miniatura_frame, text="❌", 
                                               command=lambda f=miniatura_frame, p=video_path: self.remover_miniatura(f, p), width=3)
                        btn_remover.pack(side='right', padx=15, pady=12)
                        
                        # Armazena referência
                        self.miniaturas.append({
                            'frame': miniatura_frame,
                            'path': video_path,
                            'numero': numero,
                            'thumbnail': thumbnail_path
                        })
                        
                        print(f"✅ Miniatura criada com sucesso para: {nome_arquivo}")
                        return
                        
                    except Exception as e:
                        print(f"Erro ao carregar miniatura: {e}")
                        # Remove arquivo corrompido
                        if os.path.exists(thumbnail_path):
                            try:
                                os.remove(thumbnail_path)
                            except:
                                pass
            
            # Se chegou aqui, usa fallback
            self.criar_miniatura_fallback(video_path, numero, miniatura_frame)
                
        except Exception as e:
            print(f"Erro ao criar miniatura: {e}")
            self.criar_miniatura_fallback(video_path, numero, miniatura_frame)
    
    def extrair_miniatura_robusta(self, video_path, numero):
        """Extrai miniatura usando múltiplas estratégias"""
        import tempfile
        # Bug F Fix: salvar em pasta temp do sistema, não no CWD
        thumbnail_path = os.path.join(tempfile.gettempdir(), f"temp_thumb_transition_{numero}.jpg")
        
        # Estratégia 1: Frame no segundo 1
        if self.tentar_extrair_frame(video_path, thumbnail_path, '00:00:01'):
            return thumbnail_path
        
        # Estratégia 2: Frame no segundo 0.5
        if self.tentar_extrair_frame(video_path, thumbnail_path, '00:00:00.5'):
            return thumbnail_path
        
        # Estratégia 3: Frame no segundo 0.1
        if self.tentar_extrair_frame(video_path, thumbnail_path, '00:00:00.1'):
            return thumbnail_path
        
        # Estratégia 4: Primeiro frame disponível
        if self.tentar_extrair_frame(video_path, thumbnail_path, '00:00:00'):
            return thumbnail_path
        
        # Estratégia 5: Usar ffprobe para encontrar frame válido
        if self.tentar_extrair_com_ffprobe(video_path, thumbnail_path):
            return thumbnail_path
        
        return None
    
    def tentar_extrair_frame(self, video_path, thumbnail_path, tempo):
        """Tenta extrair frame em um tempo específico"""
        try:
            resultado = subprocess.run([
                'ffmpeg', '-i', video_path, '-ss', tempo,
                '-vframes', '1',
                '-vf', 'scale=160:90:force_original_aspect_ratio=decrease,pad=160:90:(ow-iw)/2:(oh-ih)/2:black',
                '-y', thumbnail_path
            ], capture_output=True, text=True, timeout=10,
               creationflags=subprocess.CREATE_NO_WINDOW)
            
            if resultado.returncode == 0 and os.path.exists(thumbnail_path):
                if os.path.getsize(thumbnail_path) > 1024:
                    return True
            return False
        except Exception as e:
            print(f"Erro ao tentar extrair frame em {tempo}: {e}")
            return False
    
    def tentar_extrair_com_ffprobe(self, video_path, thumbnail_path):
        """Usa ffprobe para encontrar frame válido"""
        try:
            resultado = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', video_path
            ], capture_output=True, text=True, timeout=5,
               creationflags=subprocess.CREATE_NO_WINDOW)
            if resultado.returncode == 0:
                duracao = float(resultado.stdout.strip())
                tempo_meio = duracao / 2
                if tempo_meio > 0:
                    tempo_str = f"00:00:{tempo_meio:.2f}"
                    if self.tentar_extrair_frame(video_path, thumbnail_path, tempo_str):
                        return True
            return False
        except Exception as e:
            print(f"Erro ao usar ffprobe: {e}")
            return False
    
    def criar_miniatura_fallback(self, video_path, numero, miniatura_frame):
        """Cria uma miniatura de fallback quando não consegue extrair frame"""
        # Frame para ícone e informações
        icon_frame = ctk.CTkFrame(miniatura_frame)
        icon_frame.pack(side='left', padx=15, pady=12)
        
        # Ícone de vídeo colorido
        thumb_label = ctk.CTkLabel(icon_frame, text="🎬", font=("Segoe UI", 32), text_color='#0066cc')
        thumb_label.pack()
        
        # Informações do vídeo
        info_frame = ctk.CTkFrame(miniatura_frame)
        info_frame.pack(side='left', fill='x', expand=True, padx=15, pady=12)
        
        nome_arquivo = os.path.basename(video_path)
        ctk.CTkLabel(info_frame, text=f"{numero}. {nome_arquivo}", 
                 font=("Segoe UI", 9, "bold")).pack(anchor='w')
        
        # Duração do vídeo
        duracao = self.get_video_duration(video_path)
        if duracao:
            ctk.CTkLabel(info_frame, text=f"⏱️ {duracao:.1f}s", 
                     font=("Segoe UI", 8), text_color='gray').pack(anchor='w')
        
        # Dimensões do vídeo
        dims = self.get_video_dimensions(video_path)
        if dims:
            width, height = dims
            ctk.CTkLabel(info_frame, text=f"📐 {width}x{height}", 
                     font=("Segoe UI", 8), text_color='blue').pack(anchor='w')
        
        # Status de miniatura
        ctk.CTkLabel(info_frame, text="🖼️ Miniatura não disponível", 
                 font=("Segoe UI", 7), text_color='orange').pack(anchor='w')
        
        # Botão de remoção
        btn_remover = ctk.CTkButton(miniatura_frame, text="❌", 
                               command=lambda f=miniatura_frame, p=video_path: self.remover_miniatura(f, p), width=3)
        btn_remover.pack(side='right', padx=15, pady=12)
        
        # Armazena referência
        self.miniaturas.append({
            'frame': miniatura_frame,
            'path': video_path,
            'numero': numero,
            'thumbnail': None
        })
        
        print(f"⚠️ Fallback usado para: {nome_arquivo}")
    
    def remover_miniatura(self, frame, video_path):
        """Remove uma miniatura e o vídeo correspondente"""
        try:
            # Remove da lista de vídeos
            if video_path in self.videos_selecionados:
                self.videos_selecionados.remove(video_path)
            
            # Remove a miniatura da lista
            for i, miniatura in enumerate(self.miniaturas):
                if miniatura['path'] == video_path:
                    # Remove o arquivo de thumbnail se existir
                    if miniatura['thumbnail'] and os.path.exists(miniatura['thumbnail']):
                        try:
                            os.remove(miniatura['thumbnail'])
                        except:
                            pass
                    # Remove da lista
                    self.miniaturas.pop(i)
                    break
            
            # Remove o frame da interface
            frame.destroy()
            
            # Atualiza números das miniaturas restantes
            self.renumerar_miniaturas()
            
            # Atualiza status
            self.status_label.config(text=f"Status: {len(self.videos_selecionados)} vídeos selecionados")
            
        except Exception as e:
            print(f"Erro ao remover miniatura: {e}")
    
    def renumerar_miniaturas(self):
        """Renumera as miniaturas após remoção"""
        for i, miniatura in enumerate(self.miniaturas, 1):
            numero_antigo = miniatura['numero']  # Bug H Fix: guarda o número antigo ANTES de atualizar
            miniatura['numero'] = i
            # Atualiza o texto da miniatura
            for widget in miniatura['frame'].winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        # Bug H Fix: busca pelo número antigo, não por (i-1)
                        if isinstance(child, ctk.CTkLabel) and child.cget('text').startswith(str(numero_antigo) + '.'):
                            nome_arquivo = os.path.basename(miniatura['path'])
                            child.configure(text=f"{i}. {nome_arquivo}")
                            break
    
    def get_video_duration(self, video_path):
        """Obtém a duração de um vídeo usando FFmpeg"""
        try:
            resultado = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', video_path
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if resultado.returncode == 0:
                return float(resultado.stdout.strip())
            return None
        except:
            return None
        

    

    
    def limpar_selecao(self):
        """Limpa a seleção de vídeos"""
        # Remove todas as miniaturas
        for miniatura in self.miniaturas:
            # Remove o arquivo de thumbnail se existir
            if miniatura['thumbnail'] and os.path.exists(miniatura['thumbnail']):
                try:
                    os.remove(miniatura['thumbnail'])
                except:
                    pass
            # Remove o frame da interface
            miniatura['frame'].destroy()
        
        # Limpa as listas
        self.videos_selecionados = []
        self.miniaturas = []
        
        self.status_label.config(text="Status: Aguardando seleção de vídeos...")
    
    def processar_videos(self):
        """Processa os vídeos selecionados em thread separada (Bug #9: não travar a UI)"""
        if not self.videos_selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um vídeo para processar!")
            return
        threading.Thread(target=self._processar_videos_worker, daemon=True).start()
    
    def _processar_videos_worker(self):
        """Worker de processamento executado em thread separada"""
        self.pastas_transicoes = {
            'horizontal': self.pasta_trans_h.get(),
            'vertical': self.pasta_trans_v.get()
        }
        self.pastas_cta = {
            'horizontal': self.pasta_cta_h.get(),
            'vertical': self.pasta_cta_v.get()
        }
        self.pastas_logomarcas = {
            'horizontal': self.pasta_logo_h.get(),
            'vertical': self.pasta_logo_v.get()
        }
        
        try:
            formato = self.formato_var.get()
            
            use_trans = self.var_transicao.get()
            use_cta = self.var_cta.get()
            use_logo = self.var_logomarca.get()
            
            if not any([use_trans, use_cta, use_logo]):
                self.after(0, lambda: messagebox.showerror("Erro", "Selecione pelo menos uma etapa (Transição, CTA ou Logomarca)."))
                return
                
            # Verifica pastas
            if use_trans:
                p = self.pastas_transicoes.get(formato)
                if not p or not os.path.exists(p):
                    self.after(0, lambda: messagebox.showerror("Erro", f"Pasta de transições não encontrada: {p}"))
                    return
            if use_cta:
                p = self.pastas_cta.get(formato)
                if not p or not os.path.exists(p):
                    self.after(0, lambda: messagebox.showerror("Erro", f"Pasta de CTA não encontrada: {p}"))
                    return
            if use_logo:
                p = self.pastas_logomarcas.get(formato)
                if not p or not os.path.exists(p):
                    self.after(0, lambda: messagebox.showerror("Erro", f"Pasta de logomarcas não encontrada: {p}"))
                    return
                    
            # Processa cada vídeo
            for i, video_path in enumerate(self.videos_selecionados):
                self.after(0, lambda i=i: self.status_label.config(
                    text=f"Processando vídeo {i+1}/{len(self.videos_selecionados)}..."
                ))
                
                current_video = video_path
                temp_files = []
                
                if use_trans:
                    new_vid = self._anexar_video_aleatorio(current_video, self.pastas_transicoes[formato], "_trans")
                    if new_vid:
                        if current_video != video_path: temp_files.append(current_video)
                        current_video = new_vid
                        
                if use_cta:
                    new_vid = self._anexar_video_aleatorio(current_video, self.pastas_cta[formato], "_cta")
                    if new_vid:
                        if current_video != video_path: temp_files.append(current_video)
                        current_video = new_vid
                        
                if use_logo:
                    new_vid = self._anexar_video_aleatorio(current_video, self.pastas_logomarcas[formato], "_logo")
                    if new_vid:
                        if current_video != video_path: temp_files.append(current_video)
                        current_video = new_vid
                
                # O último current_video já é o resultado final.
                # Renomear se quisermos um nome final limpo
                if current_video != video_path:
                    final_name = os.path.join(os.path.dirname(video_path), f"{os.path.splitext(os.path.basename(video_path))[0]}_processado.mp4")
                    # Se já existe _processado.mp4, tentar remover ou criar variante
                    if os.path.exists(final_name):
                        try: os.remove(final_name)
                        except: final_name = current_video # falhou, mantem o sufixo
                        
                    if current_video != final_name:
                        try:
                            os.rename(current_video, final_name)
                        except:
                            final_name = current_video
                            
                    print(f"✅ Vídeo final salvo: {final_name}")
                    
                # Cleanup temps
                for t in temp_files:
                    try:
                        if os.path.exists(t): os.remove(t)
                    except: pass
                    
            n = len(self.videos_selecionados)
            self.after(0, lambda n=n: (
                self.status_label.config(text=f"Status: {n} vídeos processados com sucesso!"),
                messagebox.showinfo("Sucesso", f"{n} vídeos processados com sucesso!")
            ))
            
        except Exception as e:
            self.after(0, lambda e=str(e): (
                messagebox.showerror("Erro", f"Erro ao processar vídeos: {e}"),
                self.status_label.config(text="Status: Erro no processamento")
            ))

    def _anexar_video_aleatorio(self, video_path, pasta_assets, sufixo):
        """Seleciona um mp4 aleatório da pasta_assets, redimensiona e anexa ao final de video_path."""
        try:
            import hardware_detector
            encoder = hardware_detector.detect_h264_encoder()
            
            # Escolhe o asset
            assets = [f for f in os.listdir(pasta_assets) if f.lower().endswith('.mp4')]
            if not assets:
                print(f"❌ Nenhum vídeo encontrado em: {pasta_assets}")
                return None
            asset_escolhido = random.choice(assets)
            asset_path = os.path.join(pasta_assets, asset_escolhido)
            print(f"🎬 Anexando: {asset_escolhido} (Etapa: {sufixo})")
            
            # Obtém as dimensões do vídeo base
            video_dims = self.get_video_dimensions(video_path)
            if not video_dims:
                video_width, video_height = 1080, 1920 # Fallback
            else:
                video_width, video_height = video_dims
                
            nome_base = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(os.path.dirname(video_path), f"{nome_base}{sufixo}.mp4")
            asset_temp_path = os.path.join(os.path.dirname(video_path), f"temp_asset{sufixo}_{nome_base}.mp4")
            
            # 1. Redimensionar asset para encaixar no vídeo base
            comando_redimensionar = [
                'ffmpeg', '-y', '-threads', '0',
                '-hwaccel', 'auto', '-i', asset_path,
                '-vf', f'scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2:black'
            ]
            if encoder == 'libx264':
                comando_redimensionar.extend(['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast'])
            else:
                comando_redimensionar.extend(['-c:v', encoder, '-b:v', '6M', '-pix_fmt', 'yuv420p'])
            comando_redimensionar.extend(['-c:a', 'aac', asset_temp_path])
            
            subprocess.run(comando_redimensionar, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if not os.path.exists(asset_temp_path):
                print(f"❌ Falha no redimensionamento: {asset_temp_path}")
                return None
                
            # 2. Concatenar
            cmd_final = [
                'ffmpeg', '-y', '-threads', '0',
                '-hwaccel', 'auto', '-i', video_path, 
                '-hwaccel', 'auto', '-i', asset_temp_path,
                '-filter_complex',
                f'[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1:unsafe=1[concatv][outa];'
                f'[concatv]scale={video_width}:{video_height}:force_original_aspect_ratio=decrease,pad={video_width}:{video_height}:(ow-iw)/2:(oh-ih)/2:black[outv]',
                '-map', '[outv]', '-map', '[outa]'
            ]
            if encoder == 'libx264':
                cmd_final.extend(['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast'])
            else:
                cmd_final.extend(['-c:v', encoder, '-b:v', '6M', '-pix_fmt', 'yuv420p'])
            cmd_final.extend(['-c:a', 'aac', output_path])
            
            resultado = subprocess.run(cmd_final, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            # Limpa asset temp
            try: os.remove(asset_temp_path)
            except: pass
            
            if resultado.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                print(f"❌ Erro ao concatenar {sufixo}: {resultado.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Exceção ao anexar {sufixo}: {e}")
            return None

    def get_video_dimensions(self, video_path):
        """Obtém as dimensões de um vídeo usando FFprobe"""
        try:
            resultado = subprocess.run([
                'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'csv=p=0', video_path
            ], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if resultado.returncode == 0:
                dimensoes = resultado.stdout.strip().split(',')
                if len(dimensoes) == 2:
                    return int(dimensoes[0]), int(dimensoes[1])
            return None
        except:
            return None
    

    
    def verificar_pastas_logomarcas(self):
        """Verifica e exibe informações sobre as pastas de transições e logomarcas"""
        try:
            # Lê os caminhos atuais dos StringVars (Fase 27)
            pastas = {
                'trans_h': self.pasta_trans_h.get(),
                'trans_v': self.pasta_trans_v.get(),
                'cta_h': self.pasta_cta_h.get(),
                'cta_v': self.pasta_cta_v.get(),
                'logo_h': self.pasta_logo_h.get(),
                'logo_v': self.pasta_logo_v.get(),
            }
            labels = {
                'trans_h': 'Transições Horizontal',
                'trans_v': 'Transições Vertical',
                'cta_h': 'Somente CTA Horizontal',
                'cta_v': 'Somente CTA Vertical',
                'logo_h': 'Logomarcas Horizontal',
                'logo_v': 'Logomarcas Vertical',
            }
            info_text = ""
            for key, pasta in pastas.items():
                if pasta and os.path.exists(pasta):
                    count = len([f for f in os.listdir(pasta) if f.lower().endswith('.mp4')])
                    info_text += f"✅ {labels[key]}: {count} arquivo(s)\n"
                elif pasta:
                    info_text += f"❌ {labels[key]}: pasta não encontrada\n"
                else:
                    info_text += f"⚪ {labels[key]}: não configurada\n"
            
            if hasattr(self, 'info_label'):
                self.info_label.config(text=info_text.strip())
        except Exception as e:
            if hasattr(self, 'info_label'):
                self.info_label.config(text=f"❌ Erro ao verificar pastas: {str(e)}")



# --- ABA 6: MONTAGEM AUTOMÁTICA (SISTEMA DE ROTEIRO) ---