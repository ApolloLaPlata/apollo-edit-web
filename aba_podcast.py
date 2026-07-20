import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
from gerador_podcast import PodcastGenerator


# ── Utilitário de formatação de timestamp SRT ─────────────────────────────────
def _fmt_srt_ts(seconds: float) -> str:
    """Converte segundos float para formato SRT HH:MM:SS,mmm"""
    ms = int((seconds % 1) * 1000)
    s  = int(seconds)
    h  = s // 3600; s %= 3600
    m  = s // 60;   s %= 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class AbaPodcast(ctk.CTkFrame):
    """
    Aba do Gerador de Podcast.
    Permite colar roteiro e gerar áudio/vídeo/tags.
    """
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager

        # Inicializa o gerador internamente OU recebe do init
        self.generator = PodcastGenerator()

        self.configure()
        self._criar_interface()

    def _criar_interface(self):
        """Cria os elementos da interface"""
        # Título
        lbl_titulo = ctk.CTkLabel(self, text="🎙️ Gerador de Podcast - VoiceMaker & Tags",
                               font=("Segoe UI", 14, "bold"))
        lbl_titulo.pack(pady=10)

        # Container Principal (PanedWindow)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Lado Esquerdo: Lista de Personagens + LOG ---
        frame_left_container = ctk.CTkFrame(paned)
        paned.add(frame_left_container, weight=1)

        # 1. Lista de Personagens (Topo)
        frame_chars = ctk.CTkLabelFrame(frame_left_container, text="Personagens")
        frame_chars.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))

        self.listbox_chars = tk.Listbox(frame_chars, font=("Segoe UI", 10), height=10, bg="#1e1e2e", fg="#ffffff", selectbackground="#4a4a6a")
        self.listbox_chars.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_chars.bind("<Double-1>", self._on_char_double_click)

        croll_chars = ttk.Scrollbar(frame_chars, orient="vertical", command=self.listbox_chars.yview)
        croll_chars.pack(side=tk.RIGHT, fill="y")
        self.listbox_chars.configure(yscrollcommand=croll_chars.set)

        self._carregar_personagens()

        # 2. Janela de Log (Baixo)
        frame_log = ctk.CTkLabelFrame(frame_left_container, text="Log de Execução")
        frame_log.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.txt_log = scrolledtext.ScrolledText(frame_log, height=10, font=("Consolas", 8), state='disabled', bg="#1e1e2e", fg="#ffffff")
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        # --- Lado Direito: Roteiro e Controles ---
        frame_right = ctk.CTkFrame(paned)
        paned.add(frame_right, weight=3)

        # Área de Roteiro
        ctk.CTkLabel(frame_right, text="Cole seu roteiro aqui:").pack(anchor="w")
        self.txt_script = scrolledtext.ScrolledText(frame_right, height=15, font=("Consolas", 10), bg="#1e1e2e", fg="#ffffff", insertbackground="white")
        self.txt_script.pack(fill=tk.BOTH, expand=True, pady=5)

        hint_text = "DICA: Formato Base -> 'Nome Personagem (Estado Visual): Texto' | Formatos mais avançados serão suportados."
        ctk.CTkLabel(frame_right, text=hint_text, text_color="gray", justify=tk.LEFT).pack(anchor="w", pady=(0, 5))

        # ── Opções de Saída ────────────────────────────────────────────────────
        frame_opts = ctk.CTkLabelFrame(frame_right, text="Opções de Geração")
        frame_opts.pack(fill=tk.X, pady=10)

        self.var_audio      = tk.BooleanVar(value=True)
        self.var_video      = tk.BooleanVar(value=False)
        self.var_tags       = tk.BooleanVar(value=False)
        self.var_normalize  = tk.BooleanVar(value=True)
        self.var_mapa_cores = tk.BooleanVar(value=False)

        ctk.CTkSwitch(frame_opts, text="Gerar Áudio (MP3)",            variable=self.var_audio).pack(side=tk.LEFT, padx=8)
        ctk.CTkSwitch(frame_opts, text="Gerar Vídeo LOOP (MP4)",       variable=self.var_video).pack(side=tk.LEFT, padx=8)
        ctk.CTkSwitch(frame_opts, text="Gerar TAGS (MOV Alpha)",       variable=self.var_tags).pack(side=tk.LEFT, padx=8)
        ctk.CTkSwitch(frame_opts, text="Normalizar Áudio (-10 LUFS)",  variable=self.var_normalize).pack(side=tk.LEFT, padx=8)
        ctk.CTkSwitch(frame_opts, text="🎨 Gerar Mapa de Cores (.json)", variable=self.var_mapa_cores).pack(side=tk.LEFT, padx=8)

        # ── Linha SRT (própria linha para destaque) ────────────────────────────
        frame_srt = ctk.CTkFrame(frame_right)
        frame_srt.pack(fill=tk.X, pady=(0, 4))

        self.var_gerar_srt = tk.BooleanVar(value=False)
        ctk.CTkSwitch(
            frame_srt,
            text="📝 Gerar SRT após áudio  (Whisper — word-level timestamps)",
            variable=self.var_gerar_srt
        ).pack(side=tk.LEFT, padx=8)
        ctk.CTkLabel(
            frame_srt,
            text="O arquivo .srt ficará na mesma pasta do áudio gerado.",
            text_color="#888", font=("Segoe UI", 8)
        ).pack(side=tk.LEFT)

        # ── Botão principal ────────────────────────────────────────────────────
        frame_actions = ctk.CTkFrame(frame_right)
        frame_actions.pack(fill=tk.X, pady=5)

        self.btn_gerar = ctk.CTkButton(frame_actions, text="🚀 GERAR PODCAST",
                                    command=self._iniciar_geracao)
        self.btn_gerar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # ── Configurações de Áudio Pro ─────────────────────────────────────────
        self.frame_audio_pro = ctk.CTkLabelFrame(frame_right, text="🎚️ Configurações de Áudio (Pro)")
        self.frame_audio_pro.pack(fill=tk.BOTH, expand=True, pady=10)

        notebook_pro = ttk.Notebook(self.frame_audio_pro)
        notebook_pro.pack(fill=tk.BOTH, expand=True)

        self.tab_volumes = ctk.CTkFrame(notebook_pro)
        notebook_pro.add(self.tab_volumes, text="Volumes")
        self._criar_painel_volumes(self.tab_volumes)

        self.tab_processamento = ctk.CTkFrame(notebook_pro)
        notebook_pro.add(self.tab_processamento, text="Processamento")
        self._criar_painel_processamento(self.tab_processamento)

        # Status
        self.lbl_status = ctk.CTkLabel(frame_right, text="Aguardando...", text_color="blue")
        self.lbl_status.pack(pady=5)

    # ── LOG ────────────────────────────────────────────────────────────────────
    def log(self, message):
        """Adiciona mensagem ao log"""
        def _append():
            if hasattr(self, 'txt_log'):
                self.txt_log.config(state='normal')
                self.txt_log.insert(tk.END, f"{message}\n")
                self.txt_log.see(tk.END)
                self.txt_log.config(state='disabled')
        self.after(0, _append)

    # ── PAINÉIS ────────────────────────────────────────────────────────────────
    def _criar_painel_volumes(self, parent):
        """Cria sliders de volume dentro do painel"""
        canvas = tk.Canvas(parent, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.volume_vars = {}
        chars = self.config_manager.get("personagens", {})

        for name, data in chars.items():
            current_vol  = data.get("volume_ajuste", 0.0)

            frame_char = ctk.CTkFrame(scrollable_frame)
            frame_char.pack(fill=tk.X, padx=5, pady=5)

            ctk.CTkLabel(frame_char, text=f"{name[:12]}:", width=150, anchor="w",
                      font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

            var = tk.DoubleVar(value=current_vol)
            self.volume_vars[name] = var

            lbl_val = ctk.CTkLabel(frame_char, text=f"{current_vol:.1f} dB", width=60, font=("Segoe UI", 9))

            def on_release(event, n=name, v=var, l=lbl_val):
                val  = v.get()
                self._salvar_config_personagem(n, val)
                self.log(f"💾 {n}: {val:.1f} dB")
                orig_color = l.cget("foreground")
                l.config(text_color="green", text="Salvo!")
                self.after(1000, lambda label=l, value=val, color=orig_color:
                           label.config(text_color=color, text=f"{value:.1f} dB"))

            scale = ttk.Scale(frame_char, from_=-20, to=20, variable=var,
                              orient=tk.HORIZONTAL, length=180)
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            scale.bind("<ButtonRelease-1>", on_release)
            scale.configure(command=lambda val, label=lbl_val: label.config(text=f"{float(val):.1f} dB"))

            lbl_val.pack(side=tk.LEFT)

    def _criar_painel_processamento(self, parent):
        """Cria controles de Smart Pacing, Compressor, Ducking e LUFS"""
        parent_frame = ctk.CTkFrame(parent)
        parent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. LUFS
        frame_lufs = ctk.CTkLabelFrame(parent_frame, text="Normalização (LUFS)")
        frame_lufs.pack(fill=tk.X, pady=5)

        current_lufs = self.config_manager.get("target_lufs", -10.0)
        self.var_lufs = tk.DoubleVar(value=current_lufs)

        scale_lufs = ttk.Scale(frame_lufs, from_=-30, to=-5, variable=self.var_lufs, orient=tk.HORIZONTAL)
        scale_lufs.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        lbl_lufs = ctk.CTkLabel(frame_lufs, text=f"{current_lufs:.1f} LUFS", width=80)
        lbl_lufs.pack(side=tk.LEFT)

        def save_lufs(event):
            val = round(self.var_lufs.get(), 1)
            self.config_manager.set("target_lufs", val)

        scale_lufs.bind("<ButtonRelease-1>", save_lufs)
        scale_lufs.configure(command=lambda v: lbl_lufs.config(text=f"{float(v):.1f} LUFS"))

        # 2. Compressor
        frame_comp = ctk.CTkLabelFrame(parent_frame, text="Compressor (Rádio Voice)")
        frame_comp.pack(fill=tk.X, pady=5)

        self.var_compressor = tk.BooleanVar(value=self.config_manager.get("use_compressor", True))
        ctk.CTkSwitch(frame_comp, text="Ativar Compressor", variable=self.var_compressor,
                        command=lambda: self.config_manager.set("use_compressor", self.var_compressor.get())
                        ).pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(frame_comp, text="Intensidade:").pack(side=tk.LEFT, padx=5)
        current_ratio = self.config_manager.get("compressor_intensity", 50.0)
        self.var_comp_intensity = tk.DoubleVar(value=current_ratio)
        scale_comp = ttk.Scale(frame_comp, from_=0, to=100, variable=self.var_comp_intensity, orient=tk.HORIZONTAL)
        scale_comp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        scale_comp.bind("<ButtonRelease-1>", lambda e: self.config_manager.set(
            "compressor_intensity", round(self.var_comp_intensity.get(), 0)))

        # 3. Smart Pacing
        frame_pacing = ctk.CTkLabelFrame(parent_frame, text="Smart Pacing (Remover Silêncios)")
        frame_pacing.pack(fill=tk.X, pady=5)

        self.var_pacing = tk.BooleanVar(value=self.config_manager.get("use_smart_pacing", True))
        ctk.CTkSwitch(frame_pacing, text="Ativar Trimming", variable=self.var_pacing,
                        command=lambda: self.config_manager.set("use_smart_pacing", self.var_pacing.get())
                        ).pack(side=tk.LEFT, padx=5)

        # 4. Audio Ducking
        frame_duck = ctk.CTkLabelFrame(parent_frame, text="Audio Ducking (Música de Fundo)")
        frame_duck.pack(fill=tk.X, pady=5)

        self.var_ducking = tk.BooleanVar(value=self.config_manager.get("use_ducking", False))
        ctk.CTkSwitch(frame_duck, text="Ativar Ducking (Baixar Música)", variable=self.var_ducking,
                        command=lambda: self.config_manager.set("use_ducking", self.var_ducking.get())
                        ).pack(side=tk.LEFT, padx=5)

    # ── PERSONAGENS ───────────────────────────────────────────────────────────
    def _carregar_personagens(self):
        """Carrega lista de personagens do config.json"""
        self.listbox_chars.delete(0, tk.END)
        for name in self.config_manager.get("personagens", {}).keys():
            self.listbox_chars.insert(tk.END, name)

    def _on_char_double_click(self, event):
        """Adiciona personagem ao roteiro ao clicar duas vezes"""
        selection = self.listbox_chars.curselection()
        if selection:
            char_name = self.listbox_chars.get(selection[0])
            pos = self.txt_script.index(tk.INSERT)
            self.txt_script.insert(pos, f"[{char_name}] (Normal): \n")
            self.txt_script.focus()

    def _salvar_config_personagem(self, name, volume_val):
        """Salva volume de um personagem específico"""
        chars = self.config_manager.get("personagens", {})
        if name in chars:
            chars[name]["volume_ajuste"] = round(volume_val, 1)
            self.config_manager.set("personagens", chars)

    # ── GERAÇÃO ───────────────────────────────────────────────────────────────
    def _iniciar_geracao(self):
        """Valida e inicia a geração em thread"""
        # 0. Sanitizar caminhos de arquivos (remover aspas duplas do Windows)
        for attr_name in dir(self):
            if 'path' in attr_name or 'dir' in attr_name or 'audio' in attr_name or 'musica' in attr_name or 'fundo' in attr_name:
                attr = getattr(self, attr_name)
                if hasattr(attr, 'get') and hasattr(attr, 'set'):
                    try:
                        val = attr.get()
                        if isinstance(val, str) and ('"' in val or "'" in val):
                            attr.set(val.strip().strip('"').strip("'"))
                    except Exception:
                        pass
                        
        script_content = self.txt_script.get("1.0", tk.END).strip()
        if not script_content:
            messagebox.showwarning("Aviso", "O roteiro está vazio!")
            return

        modes = []
        if self.var_audio.get():     modes.append("audio")
        if self.var_video.get():     modes.append("video")
        if self.var_tags.get():      modes.append("tags")

        if not modes:
            messagebox.showwarning("Aviso", "Selecione pelo menos um modo de geração.")
            return

        normalize        = self.var_normalize.get()
        gerar_mapa_cores = self.var_mapa_cores.get()
        gerar_srt        = self.var_gerar_srt.get()

        temp_script = "temp_podcast_script.txt"
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(script_content)

        self.btn_gerar.config(state="disabled")
        self.lbl_status.config(text="⏳ Gerando... Por favor aguarde.", text_color="orange")

        threading.Thread(
            target=self._processar_geracao,
            args=(temp_script, modes, normalize, gerar_mapa_cores, gerar_srt),
            daemon=True
        ).start()

    def _processar_geracao(self, script_path, modes, normalize,
                           gerar_mapa_cores=False, gerar_srt=False):
        """Executa a geração no backend"""
        try:
            audio_path = self.generator.generate_podcast(
                script_path, modes=modes,
                normalize_audio=normalize,
                gerar_mapa_cores=gerar_mapa_cores,
                log_callback=self.log
            )

            # ── SRT opcional ─────────────────────────────────────────────────
            if gerar_srt and "audio" in modes:
                self._gerar_srt_do_audio(audio_path)

            self.after(0, self._finalizar_sucesso)
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self._finalizar_erro(err_msg))

    # ── SRT HELPER ────────────────────────────────────────────────────────────
    def _gerar_srt_do_audio(self, audio_path=None):
        """
        Roda Whisper (modelo base) no áudio final do podcast e salva .srt
        com timestamps word-level na mesma pasta do áudio.
        Se audio_path for None, usa o MP3 mais recente em output_podcast/.
        """
        try:
            import whisper

            # Descobre o arquivo de áudio
            if not audio_path or not os.path.exists(str(audio_path)):
                out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_podcast")
                if not os.path.isdir(out_dir):
                    self.log("⚠️ [SRT] Pasta output_podcast não encontrada.")
                    return
                mp3s = sorted(
                    [os.path.join(out_dir, f) for f in os.listdir(out_dir) if f.endswith(".mp3")],
                    key=os.path.getmtime, reverse=True
                )
                if not mp3s:
                    self.log("⚠️ [SRT] Nenhum MP3 encontrado em output_podcast/.")
                    return
                audio_path = mp3s[0]

            self.log(f"📝 [SRT] Iniciando Whisper em: {os.path.basename(audio_path)}")
            self.after(0, lambda: self.lbl_status.config(
                text="⏳ Gerando SRT via Whisper...", text_color="orange"))

            model  = whisper.load_model("base")
            result = model.transcribe(audio_path, fp16=False, language="pt", word_timestamps=True)

            # Garante que todos os segmentos têm 'words'
            for seg in result.get("segments", []):
                if not seg.get("words"):
                    seg["words"] = [{"word": seg["text"].strip(),
                                     "start": seg["start"], "end": seg["end"]}]

            # Escreve o SRT palavra a palavra
            srt_path = os.path.splitext(audio_path)[0] + ".srt"
            with open(srt_path, "w", encoding="utf-8") as f:
                idx = 1
                for seg in result.get("segments", []):
                    for w in seg.get("words", []):
                        word = w["word"].strip()
                        if not word:
                            continue
                        f.write(f"{idx}\n")
                        f.write(f"{_fmt_srt_ts(w['start'])} --> {_fmt_srt_ts(w['end'])}\n")
                        f.write(f"{word}\n\n")
                        idx += 1

            self.log(f"✅ [SRT] Gerado: {os.path.basename(srt_path)}")
            self.after(0, lambda p=srt_path: self.lbl_status.config(
                text=f"✅ SRT gerado: {os.path.basename(p)}", text_color="green"))

        except ImportError:
            self.log("⚠️ [SRT] Whisper não instalado. Rode: pip install openai-whisper")
        except Exception as ex:
            self.log(f"❌ [SRT] Erro: {ex}")

    # ── FINALIZAÇÃO ──────────────────────────────────────────────────────────
    def _finalizar_sucesso(self):
        self.btn_gerar.config(state="normal")
        self.lbl_status.config(text="✅ Geração Concluída! Verifique a pasta output_podcast.",
                               text_color="green")
        messagebox.showinfo("Sucesso", "Podcast gerado com sucesso!")

    def _finalizar_erro(self, msg):
        self.btn_gerar.config(state="normal")
        self.lbl_status.config(text=f"❌ Erro: {msg}", text_color="red")
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{msg}")
