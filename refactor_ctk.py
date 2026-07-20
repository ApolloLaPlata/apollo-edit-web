import re
import os

with open("apollo_studio.py.bak", "r", encoding="utf-8") as f:
    content = f.read()

# Replace tkinter imports
content = content.replace("import tkinter as tk", "import tkinter as tk\nimport customtkinter as ctk")

# Let's replace the WorkspaceLauncher and ApolloStudio classes completely, as they handle the main UI.
# It's safer to just provide the new code for them.

new_launcher_code = """
class WorkspaceLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Hub de Produção - Selecione o Canal")
        self.root.geometry("1000x750")
        self.root.resizable(False, False)
        
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apollo_logo_padrao.ico")
            self.root.iconbitmap(icon_path)
        except Exception: pass
        
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.workspaces_dir = os.path.join(self.base_dir, "Workspaces")
        self._ensure_migration()
        
        # main frame
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho com Logo
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill=tk.X, pady=(20, 10))
        
        try:
            from PIL import Image, ImageTk
            logo_path = os.path.join(self.base_dir, "apollo_logo_padrao.png")
            if os.path.exists(logo_path):
                img = Image.open(logo_path).convert("RGBA").resize((200, 200), Image.Resampling.LANCZOS)
                self.hub_logo = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
                ctk.CTkLabel(header, image=self.hub_logo, text="").pack()
        except: pass
        
        ctk.CTkLabel(header, text="🌈 Módulo Central do Apollo", font=("Segoe UI", 24, "bold"), text_color="#FFD32A").pack(pady=(10, 0))
        ctk.CTkLabel(header, text="Selecione a logomarca do canal para carregar a configuração isolada.", font=("Segoe UI", 14), text_color="gray").pack(pady=(5,0))
        
        # Área dividida: Grade à Esquerda e Analytics à Direita
        split_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        split_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Lado Esquerdo (Grade)
        canvas_frame = ctk.CTkFrame(split_frame, fg_color="transparent")
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        btn_frame = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="🔄 Atualizar Lista", command=self.atualizar_lista, width=120).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(btn_frame, text="➕ Criar Novo Canal", command=self.abrir_criador_canal, width=120, fg_color="#2ED573", hover_color="#27AE60", text_color="black").pack(side=tk.RIGHT, padx=5)
        
        # Tkinter Canvas for scrolling
        self.canvas = tk.Canvas(canvas_frame)
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        
        self.grid_frame = ctk.CTkFrame(self.canvas)
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.grid_frame, anchor="n")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Lado Direito (Dashboard / Analytics)
        self.analytics_frame = ctk.CTkFrame(split_frame, width=250, corner_radius=10, fg_color="#2B2B2B")
        self.analytics_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.analytics_frame.pack_propagate(False)
        
        ctk.CTkLabel(self.analytics_frame, text="📊 Produtividade", font=("Segoe UI", 16, "bold"), text_color="#FFD32A").pack(pady=(20, 10))
        
        self.lbl_total_canais = ctk.CTkLabel(self.analytics_frame, text="Canais: 0", font=("Segoe UI", 14))
        self.lbl_total_canais.pack(pady=5)
        
        self.lbl_total_midias = ctk.CTkLabel(self.analytics_frame, text="Arquivos Gerados: 0", font=("Segoe UI", 14))
        self.lbl_total_midias.pack(pady=5)
        
        ctk.CTkLabel(self.analytics_frame, text="\\nDica: Clique com o\\nbotão direito em um\\ncanal para Cloná-lo.", font=("Segoe UI", 12, "italic"), text_color="gray").pack(pady=20)
        
        self._photo_cache = []
        self.atualizar_lista()

    def _on_canvas_resize(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _ensure_migration(self):
        if not os.path.exists(self.workspaces_dir):
            os.makedirs(self.workspaces_dir)
            default_ws = os.path.join(self.workspaces_dir, "Tutorial das Coisas")
            os.makedirs(default_ws)
            
            old_config = os.path.join(self.base_dir, "config.json")
            if os.path.exists(old_config):
                import shutil
                try: shutil.move(old_config, os.path.join(default_ws, "config.json"))
                except: pass

    def atualizar_lista(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self._photo_cache.clear()
        
        if not os.path.exists(self.workspaces_dir):
            return
            
        pastas = [d for d in os.listdir(self.workspaces_dir) if os.path.isdir(os.path.join(self.workspaces_dir, d))]
        pastas = sorted(pastas)
        
        colunas = 3
        from PIL import Image, ImageTk
        import json
        
        default_logo_path = os.path.join(self.base_dir, "apollo_logo_padrao.png")
        total_midias = 0
        
        for idx, nome in enumerate(pastas):
            row = idx // colunas
            col = idx % colunas
            
            ws_path = os.path.join(self.workspaces_dir, nome)
            cfg_path = os.path.join(ws_path, "config.json")
            
            out_path = os.path.join(ws_path, "outputs")
            if os.path.exists(out_path):
                for r, d, f in os.walk(out_path):
                    for file in f:
                        if file.endswith((".mp3", ".wav", ".mp4", ".mkv", ".srt")):
                            total_midias += 1
            
            img_path = default_logo_path
            if os.path.exists(cfg_path):
                try:
                    with open(cfg_path, 'r', encoding='utf-8') as f:
                        cfg = json.load(f)
                    ws_logo = cfg.get("app_logo_path")
                    if ws_logo and os.path.exists(ws_logo):
                        img_path = ws_logo
                except: pass
                
            try:
                if os.path.exists(img_path):
                    im = Image.open(img_path).convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(im)
                else:
                    photo = tk.PhotoImage(width=160, height=160)
            except:
                photo = tk.PhotoImage(width=160, height=160)
                
            self._photo_cache.append(photo)
            
            item_frame = ctk.CTkFrame(self.grid_frame)
            self.grid_frame.grid_columnconfigure(col, weight=1)
            item_frame.grid(row=row, column=col, padx=30, pady=20)
            
            btn = ctk.CTkButton(item_frame, image=photo, cursor="hand2",
                            command=lambda n=nome: self.iniciar_workspace(n))
            
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="🔄 Clonar Canal", command=lambda n=nome: self.clonar_canal(n))
            menu.add_command(label="🎨 Editar Identidade", command=lambda n=nome: self.editar_identidade(n))
            
            def show_menu(e, m=menu):
                m.tk_popup(e.x_root, e.y_root)
                
            btn.bind("<Button-3>", show_menu)
            btn.pack()
            
            ctk.CTkLabel(item_frame, text=nome, font=("Segoe UI", 14, "bold")).pack(pady=(8,0))
            
        self.lbl_total_canais.configure(text=f"Canais Ativos: {len(pastas)}")
        self.lbl_total_midias.configure(text=f"Mídias Geradas: {total_midias}")

    def clonar_canal(self, nome_origem):
        import tkinter.simpledialog as sd
        import shutil
        novo_nome = sd.askstring("Clonar Workspace", f"Clonando '{nome_origem}'.\\nDigite o nome do novo Canal:")
        if novo_nome:
            novo_nome = "".join(c for c in novo_nome if c.isalnum() or c in " _-").strip()
            if novo_nome:
                origem_path = os.path.join(self.workspaces_dir, nome_origem)
                destino_path = os.path.join(self.workspaces_dir, novo_nome)
                
                if os.path.exists(destino_path):
                    messagebox.showerror("Erro", "Já existe um canal com esse nome.")
                    return
                
                try:
                    shutil.copytree(origem_path, destino_path, ignore=shutil.ignore_patterns("outputs"))
                    from database_manager import db
                    db.registrar_canal(novo_nome, os.path.join(destino_path, "config.json"))
                    self.atualizar_lista()
                    messagebox.showinfo("Sucesso", f"Canal '{nome_origem}' clonado perfeitamente para '{novo_nome}'!")
                except Exception as e:
                    messagebox.showerror("Erro", f"Falha ao clonar: {e}")

    def editar_identidade(self, nome_canal):
        top = ctk.CTkToplevel(self.root)
        top.title(f"Editar Identidade - {nome_canal}")
        top.geometry("600x500")
        top.grab_set()
        
        ctk.CTkLabel(top, text=f"🎨 Identidade Visual: {nome_canal}", font=("Segoe UI", 18, "bold"), text_color="#FFD32A").pack(pady=15)
        
        cfg_path = os.path.join(self.workspaces_dir, nome_canal, "config.json")
        cfg = {}
        if os.path.exists(cfg_path):
            import json
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except: pass
            
        frame_logo = ctk.CTkFrame(top)
        frame_logo.pack(fill=tk.X, padx=20, pady=5)
        var_logo = tk.StringVar(value=cfg.get("app_logo_path", ""))
        
        def _procurar_logo():
            from tkinter import filedialog
            p = filedialog.askopenfilename(filetypes=[("Imagens PNG", "*.png")])
            if p: var_logo.set(p)
            
        ctk.CTkEntry(frame_logo, textvariable=var_logo, width=350).pack(side=tk.LEFT, padx=(10, 5), pady=10)
        ctk.CTkButton(frame_logo, text="Procurar", command=_procurar_logo, width=100).pack(side=tk.LEFT, pady=10)
        
        frame_cores = ctk.CTkFrame(top)
        frame_cores.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tc = cfg.get("theme_colors", {})
        
        def add_color_field(parent, label, var, r):
            ctk.CTkLabel(parent, text=label).grid(row=r, column=0, padx=10, pady=5, sticky='w')
            ctk.CTkEntry(parent, textvariable=var, width=150).grid(row=r, column=1, padx=10, pady=5)
            
        var_hbg = tk.StringVar(value=tc.get("header_bg", tc.get("bg", "#1A1A2E")))
        add_color_field(frame_cores, "Cor do Cabeçalho (Hex):", var_hbg, 0)
        
        var_hfg = tk.StringVar(value=tc.get("header_fg", tc.get("fg", "#FFD32A")))
        add_color_field(frame_cores, "Cor Letras Cabeçalho (Hex):", var_hfg, 1)
        
        var_abg = tk.StringVar(value=tc.get("app_bg", tc.get("bg", "#16213E")))
        add_color_field(frame_cores, "Cor do Fundo App (Hex):", var_abg, 2)
        
        var_afg = tk.StringVar(value=tc.get("app_fg", tc.get("fg", "#F0F0F0")))
        add_color_field(frame_cores, "Cor Letras App (Hex):", var_afg, 3)
        
        var_accent = tk.StringVar(value=tc.get("accent", "#9B59B6"))
        add_color_field(frame_cores, "Cor de Destaque/Botões (Hex):", var_accent, 4)
        
        def _salvar_identidade():
            cfg["app_logo_path"] = var_logo.get().strip()
            cfg["theme_colors"] = {
                "header_bg": var_hbg.get().strip(),
                "header_fg": var_hfg.get().strip(),
                "app_bg": var_abg.get().strip(),
                "app_fg": var_afg.get().strip(),
                "accent": var_accent.get().strip()
            }
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=4)
            self.atualizar_lista()
            top.destroy()
            messagebox.showinfo("Sucesso", "Identidade visual atualizada com sucesso!\\nAbrindo o canal para ver as alterações...")
            
        ctk.CTkButton(top, text="✔ Salvar Identidade", command=_salvar_identidade).pack(pady=20)

    def abrir_criador_canal(self):
        top = ctk.CTkToplevel(self.root)
        top.title("Novo Canal (Workspace)")
        top.geometry("650x550")
        top.grab_set()
        
        ctk.CTkLabel(top, text="🚀 Criar Novo Canal Apollo", font=("Segoe UI", 18, "bold"), text_color="#FFD32A").pack(pady=15)
        
        frame_nome = ctk.CTkFrame(top)
        frame_nome.pack(fill=tk.X, padx=20, pady=5)
        ctk.CTkLabel(frame_nome, text="Nome do Canal:").pack(anchor='w', padx=10, pady=(5,0))
        var_nome = tk.StringVar()
        
        sub_nome = ctk.CTkFrame(frame_nome, fg_color="transparent")
        sub_nome.pack(fill=tk.X, pady=5, padx=10)
        
        ctk.CTkEntry(sub_nome, textvariable=var_nome, width=350).pack(side=tk.LEFT, padx=(0, 5))
        
        def _sugerir_nome():
            import random
            prefixos = ["Mentes", "Código", "Frequência", "Descarga", "Oceano", "Universo", "Mestre", "Lendas", "Projeto", "Sombra"]
            sufixos = ["de Ouro", "Sombrio(a)", "Tech", "Viral", "Alfa", "Infinito", "do Asfalto", "Zero", "Pro", "X"]
            nome_sorteado = f"{random.choice(prefixos)} {random.choice(sufixos)}"
            var_nome.set(nome_sorteado)
            
        ctk.CTkButton(sub_nome, text="🎲 Sugerir Nome", command=_sugerir_nome, width=120).pack(side=tk.LEFT)
        
        frame_cores = ctk.CTkFrame(top)
        frame_cores.pack(fill=tk.X, padx=20, pady=10)
        ctk.CTkLabel(frame_cores, text="Paleta Rápida:").pack(anchor='w', padx=10, pady=(5,0))
        
        temas = {
            "Apollo Padrão (Roxo/Dourado)": {"header_bg": "#1A1A2E", "header_fg": "#FFD32A", "app_bg": "#1A1A2E", "app_fg": "#F0F0F0", "accent": "#9B59B6"},
            "Oceano Profundo (Azul)": {"header_bg": "#0B1D3A", "header_fg": "#00B4D8", "app_bg": "#0A1128", "app_fg": "#E0E0E0", "accent": "#03045E"},
            "Cyberpunk (Preto/Neon)": {"header_bg": "#0D0D0D", "header_fg": "#39FF14", "app_bg": "#111111", "app_fg": "#FFFFFF", "accent": "#FF00FF"},
            "Dark Trap (Preto/Vermelho)": {"header_bg": "#121212", "header_fg": "#FF4757", "app_bg": "#1A1A1A", "app_fg": "#E0E0E0", "accent": "#FF0000"},
            "Clean (Branco/Preto)": {"header_bg": "#FFFFFF", "header_fg": "#000000", "app_bg": "#F5F5F5", "app_fg": "#333333", "accent": "#555555"}
        }
        
        var_tema = ctk.StringVar(value="Apollo Padrão (Roxo/Dourado)")
        cb = ctk.CTkComboBox(frame_cores, variable=var_tema, values=list(temas.keys()), width=350)
        cb.pack(pady=10, padx=10, anchor='w')
        
        frame_logo = ctk.CTkFrame(top)
        frame_logo.pack(fill=tk.X, padx=20, pady=5)
        ctk.CTkLabel(frame_logo, text="Logomarca (.png):").pack(anchor='w', padx=10, pady=(5,0))
        var_logo = tk.StringVar()
        
        def _procurar_logo():
            from tkinter import filedialog
            p = filedialog.askopenfilename(filetypes=[("Imagens PNG", "*.png")])
            if p: var_logo.set(p)
            
        sub_logo = ctk.CTkFrame(frame_logo, fg_color="transparent")
        sub_logo.pack(fill=tk.X, pady=5, padx=10)
        ctk.CTkEntry(sub_logo, textvariable=var_logo, width=350).pack(side=tk.LEFT, padx=(0, 5))
        ctk.CTkButton(sub_logo, text="Procurar", command=_procurar_logo, width=120).pack(side=tk.LEFT)
        
        def _salvar():
            nome = var_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Nome inválido!")
                return
            nome_dir = "".join(c for c in nome if c.isalnum() or c in " _-").strip()
            caminho = os.path.join(self.workspaces_dir, nome_dir)
            
            if os.path.exists(caminho):
                messagebox.showerror("Erro", "Canal já existe!")
                return
            
            os.makedirs(caminho)
            
            import json
            cfg = {}
            if var_logo.get().strip():
                cfg["app_logo_path"] = var_logo.get().strip()
            
            t = var_tema.get()
            if t in temas:
                cfg["theme_colors"] = temas[t]
                
            with open(os.path.join(caminho, "config.json"), 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=4)
                
            from database_manager import db
            db.registrar_canal(nome_dir, os.path.join(caminho, "config.json"))
                
            self.atualizar_lista()
            top.destroy()
            messagebox.showinfo("Sucesso", f"Canal '{nome}' criado!\\nVocê pode configurar ainda mais os ícones e cores pela aba 'Identidade' dentro dele.")
            
        ctk.CTkButton(top, text="✔ Criar Canal", command=_salvar).pack(pady=20)

    def iniciar_workspace(self, nome):
        import subprocess
        try:
            cmd = [sys.executable, "apollo_studio.py", "--workspace", nome]
            subprocess.Popen(cmd, cwd=self.base_dir)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao iniciar {nome}:\\n{e}")

class ApolloStudio:
    def __init__(self, root, workspace_name="Default", workspace_path=None):
        self.root = root
        self.workspace_name = workspace_name
        self.workspace_path = workspace_path
        self.root.title(f"🚀 Apollo Studio - [Workspace: {workspace_name}]")
        self.root.geometry("1600x950")
        self.root.minsize(1200, 850)
        self.root.resizable(True, True)
        
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apollo_logo_padrao.ico")
            if self.workspace_path:
                cfg_path = os.path.join(self.workspace_path, "config.json")
                if os.path.exists(cfg_path):
                    import json
                    with open(cfg_path, 'r', encoding='utf-8') as f:
                        cfg = json.load(f)
                    ws_icon = cfg.get("app_icon_path")
                    if ws_icon and os.path.exists(ws_icon):
                        icon_path = ws_icon
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

        # Criação do layout Sidebar + Main View
        self.sidebar_frame = ctk.CTkFrame(self.root, width=220, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)
        
        self.main_view = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_view.pack(side="right", fill="both", expand=True)
        
        self.frames = {}
        self.buttons = {}
        self.current_frame = None

        # Logo na Sidebar
        try:
            from PIL import Image, ImageTk
            _lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apollo_logo_padrao.png")
            if self.workspace_path:
                cfg_path = os.path.join(self.workspace_path, "config.json")
                if os.path.exists(cfg_path):
                    import json
                    try:
                        with open(cfg_path, 'r', encoding='utf-8') as f:
                            cfg = json.load(f)
                        ws_logo = cfg.get("app_logo_path")
                        if ws_logo and os.path.exists(ws_logo):
                            _lp = ws_logo
                    except: pass
            img = Image.open(_lp).convert("RGBA").resize((100, 100), Image.Resampling.LANCZOS)
            self.sidebar_logo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            ctk.CTkLabel(self.sidebar_frame, image=self.sidebar_logo, text="").pack(pady=(20, 10))
        except Exception:
            ctk.CTkLabel(self.sidebar_frame, text="🚀", font=("Segoe UI", 40)).pack(pady=(20, 10))
            
        app_title = "APOLLO STUDIO"
        if self.workspace_name and self.workspace_name != "Default":
             app_title = self.workspace_name.upper()
        ctk.CTkLabel(self.sidebar_frame, text=app_title, font=("Segoe UI", 16, "bold"), text_color="#FFD32A").pack(pady=(0, 20))

        if MODULES_AVAILABLE:
            if self.workspace_path:
                config_file = os.path.join(self.workspace_path, "config.json")
                self.config_manager = ConfigManager(config_file=config_file)
                self.config_manager.workspace_dir = self.workspace_path
            else:
                self.config_manager = ConfigManager()
                self.config_manager.workspace_dir = os.path.dirname(os.path.abspath(__file__))
                
            self._patch_filedialog()
            self.tts_manager = TTSManager(self.config_manager)
        else:
            self.config_manager = None
            self.tts_manager = None

        self.aba_dashboard = AbaDashboard(
            self.main_view,
            config_manager=self.config_manager,
            app_ref=self
        )
        self.add_tab("📊 1. Dashboard Principal", self.aba_dashboard)

        if MODULES_AVAILABLE:
            self.create_apollo_tabs()

        self.aba_mapeador = AbaMapeadorAutomatico(self.main_view, self.config_manager)
        self.aba_mapeador._app_ref = self
        self.add_tab("🎬 2. O Diretor (Motor Clássico)", self.aba_mapeador)
        
        self.aba_criador = AbaCriadorTemplates(self.main_view)
        self.add_tab("🎨 3. Estúdio Visual", self.aba_criador)

        self.aba_fila_render = AbaFilaRender(
            self.main_view,
            config_manager=self.config_manager,
            app_ref=self
        )
        self.add_tab("⚡ 4. Fila Autônoma", self.aba_fila_render)

        if MONTADOR_AVAILABLE:
            self.aba_montador = AbaTransition(self.main_view)
            self.add_tab("🎥 5. O Montador (Macros)", self.aba_montador)
            
        try:
            from aba_timeline_web import AbaTimelineWeb
            self.aba_timeline_web = AbaTimelineWeb(self.main_view)
            self.add_tab("✂️ 6. Apollo Web Editor", self.aba_timeline_web)
        except Exception as e:
            print(f"Erro ao carregar Apollo Web Editor: {e}")

    def add_tab(self, title, frame_instance):
        btn = ctk.CTkButton(self.sidebar_frame, text=title, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.select_tab(title), font=("Segoe UI", 13))
        btn.pack(pady=3, padx=10, fill="x")
        self.buttons[title] = btn
        self.frames[title] = frame_instance
        if self.current_frame is None:
            self.select_tab(title)

    def select_tab(self, title):
        if self.current_frame:
            self.current_frame.pack_forget()
            for b in self.buttons.values():
                b.configure(fg_color="transparent")
                
        self.frames[title].pack(fill="both", expand=True)
        self.buttons[title].configure(fg_color=("gray75", "gray25"))
        self.current_frame = self.frames[title]

    def _patch_filedialog(self):
        import tkinter.filedialog as fd
        import os
        import inspect
        
        orig_askopenfilename = fd.askopenfilename
        orig_askopenfilenames = fd.askopenfilenames
        orig_askdirectory = fd.askdirectory
        orig_asksaveasfilename = fd.asksaveasfilename
        
        cm = self.config_manager
        
        def _get_key(kwargs):
            title = kwargs.get('title', '')
            if title:
                return "fd_" + "".join(c for c in str(title) if c.isalnum() or c in " _-").replace(" ", "_")
            try:
                caller = inspect.stack()[2]
                func_name = getattr(caller, 'function', 'unknown')
                lineno = getattr(caller, 'lineno', 0)
                fname = os.path.basename(getattr(caller, 'filename', 'unknown')).replace('.py', '')
                return f"fd_{fname}_{func_name}_{lineno}"
            except Exception:
                return "fd_default"

        def wrap_askopenfilename(**kwargs):
            k = _get_key(kwargs)
            ld = cm.get(f"last_dirs.{k}")
            if ld and os.path.exists(ld) and 'initialdir' not in kwargs:
                kwargs['initialdir'] = ld
            res = orig_askopenfilename(**kwargs)
            if res:
                cm.set(f"last_dirs.{k}", os.path.dirname(res))
            return res

        def wrap_askopenfilenames(**kwargs):
            k = _get_key(kwargs)
            ld = cm.get(f"last_dirs.{k}")
            if ld and os.path.exists(ld) and 'initialdir' not in kwargs:
                kwargs['initialdir'] = ld
            res = orig_askopenfilenames(**kwargs)
            if not res:
                res = ()
            elif isinstance(res, str):
                try:
                    res = self.root.tk.splitlist(res)
                except Exception:
                    res = (res,)
            if res and isinstance(res, (list, tuple)) and len(res) > 0:
                cm.set(f"last_dirs.{k}", os.path.dirname(res[0]))
            return res

        def wrap_askdirectory(**kwargs):
            k = _get_key(kwargs)
            ld = cm.get(f"last_dirs.{k}")
            if ld and os.path.exists(ld) and 'initialdir' not in kwargs:
                kwargs['initialdir'] = ld
            res = orig_askdirectory(**kwargs)
            if res:
                cm.set(f"last_dirs.{k}", res)
            return res

        def wrap_asksaveasfilename(**kwargs):
            k = _get_key(kwargs)
            ld = cm.get(f"last_dirs.{k}")
            if ld and os.path.exists(ld) and 'initialdir' not in kwargs:
                kwargs['initialdir'] = ld
            res = orig_asksaveasfilename(**kwargs)
            if res:
                cm.set(f"last_dirs.{k}", os.path.dirname(res))
            return res

        fd.askopenfilename = wrap_askopenfilename
        fd.askopenfilenames = wrap_askopenfilenames
        fd.askdirectory = wrap_askdirectory
        fd.asksaveasfilename = wrap_asksaveasfilename

    def create_apollo_tabs(self):
        import traceback
        def add_tab_internal(constructor, text, *args):
            try:
                aba = constructor(*args)
                self.add_tab(text, aba)
                safe_text = text.encode('ascii', 'ignore').decode('ascii')
                print(f"[OK] Aba carregada: {safe_text}")
            except Exception:
                safe_text = text.encode('ascii', 'ignore').decode('ascii')
                print(f"[ERRO] Falha ao carregar aba '{safe_text}':")
                traceback.print_exc()

        add_tab_internal(AbaGeracaoTTS,          "🎤 Gerar Áudio (TTS)",    self.main_view, self.tts_manager, self.config_manager)
        add_tab_internal(AbaGeracaoVideoNarrador,"🎥 Gerar Vídeo do Narrador", self.main_view, self.config_manager)
        add_tab_internal(AbaControleVolume,      "🔊 Controle de Volume",    self.main_view)
        add_tab_internal(AbaFerramentas,         "🛠️ Ferramentas (Apollo)",  self.main_view)
        add_tab_internal(AbaGeradorLegendas,     "📝 Gerador de Legendas",   self.main_view, self.config_manager)
        add_tab_internal(AbaPodcast,             "🎙️ Podcast",               self.main_view, self.config_manager)
        add_tab_internal(AbaAjustadorMidia,      "🎬 Ajustador de Mídia",    self.main_view)
        add_tab_internal(AbaInferenciaVideo,     "🎙️ Dublagem Externa",      self.main_view, self.config_manager, {})
        add_tab_internal(AbaConfiguracoes,       "⚙️ Configurações globais", self.main_view, self.config_manager)
        add_tab_internal(AbaFabricaClipes,       "🎬 Fábrica de Músicas",   self.main_view, self.config_manager)
        add_tab_internal(AbaBiblioteca,          "📚 Tanque de Combustível", self.main_view, self.config_manager)
"""

# Extract the beginning of the file up to class ApolloStudio
start_match = re.search(r"class ApolloStudio:", content)
start_pos = start_match.start()

# Extract the if __name__ == '__main__': block
end_match = re.search(r"if __name__ == [\"']__main__[\"']:", content)
end_pos = end_match.start()
main_block = content[end_pos:]

# Replace tk.Tk() with ctk.CTk()
main_block = main_block.replace("root = tk.Tk()", "ctk.set_appearance_mode('dark')\\n    ctk.set_default_color_theme('blue')\\n    root = ctk.CTk()")

final_content = content[:start_pos] + new_launcher_code + "\n" + main_block

with open("apollo_studio.py", "w", encoding="utf-8") as f:
    f.write(final_content)
