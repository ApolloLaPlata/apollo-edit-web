import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import threading

class AbaDiretorIA(ctk.CTkFrame):
    def __init__(self, parent, app_core=None, config_manager=None, log_queue=None):
        super().__init__(parent)
        self.app_core = app_core
        self.config_manager = config_manager
        self.log_queue = log_queue
        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Scroll container ──────────────────────────────────────────────
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        main_frame = ctk.CTkFrame(canvas)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        main_frame.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=canvas.winfo_width()))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ── HEADER ────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(main_frame)
        hdr.pack(fill=tk.X, padx=0, pady=0)

        ctk.CTkLabel(hdr, text="Diretor de IA",
                 font=("Segoe UI", 20, "bold")
                 ).pack(side=tk.LEFT, padx=20, pady=14)
        ctk.CTkLabel(hdr, text="Motor semantico de decisoes criativas via Gemini",
                 font=("Segoe UI", 10)
                 ).pack(side=tk.LEFT, padx=0, pady=14)

        # ── STATUS GEMINI ─────────────────────────────────────────────────
        frm_gem = ctk.CTkLabelFrame(main_frame, text=" Conexao Gemini ")
        frm_gem.pack(fill=tk.X, padx=15, pady=(10, 0))

        row_gem = ctk.CTkFrame(frm_gem)
        row_gem.pack(fill=tk.X, padx=10, pady=8)
        self.lbl_gemini_status = ctk.CTkLabel(row_gem,
            text="Status desconhecido - clique em Testar para verificar",
            font=("Segoe UI", 10), text_color="#AAAAAA")
        self.lbl_gemini_status.pack(side=tk.LEFT, expand=True, anchor="w")
        ctk.CTkButton(row_gem, text="Testar Conexao",
                   command=self._testar_gemini_thread).pack(side=tk.RIGHT, padx=5)

        # ── [E20] SELETOR DE LLM PROVIDER ────────────────────────────────
        lf_llm = ctk.CTkLabelFrame(main_frame, text=" [E20] Provider de Inteligencia Artificial ")
        lf_llm.pack(fill=tk.X, padx=15, pady=(8, 0))

        row_prov = ctk.CTkFrame(lf_llm)
        ctk.CTkLabel(row_prov, text="LLM Ativo:", font=("Segoe UI", 10)).pack(side=tk.LEFT)

        self.var_llm_provider = tk.StringVar(value="gemini")
        providers = ["gemini", "openai", "openrouter", "grok"]
        self.cmb_prov = ctk.CTkOptionMenu(row_prov, variable=self.var_llm_provider,
                                values=providers, width=14)
        self.cmb_prov.pack(side=tk.LEFT, padx=(8, 20))
        self.cmb_prov.bind("<<ComboboxSelected>>", self._on_provider_change)

        ctk.CTkButton(row_prov, text="Salvar Provider",
                   command=self._salvar_llm_provider).pack(side=tk.LEFT)

        self.lbl_llm_status = ctk.CTkLabel(lf_llm, text="(As chaves de API sao carregadas automaticamente da Configuracao Global)",
            font=("Segoe UI", 9), text_color="#AAAAAA")
        self.lbl_llm_status.pack(anchor="w", padx=10, pady=(0, 6))

        # ── MÓDULOS PRÉ-PRODUÇÃO ──────────────────────────────────────────
        self.var_ia_ativa          = tk.BooleanVar(value=True)
        self.var_limpeza_semantica = tk.BooleanVar(value=False)
        self.var_broll_contextual  = tk.BooleanVar(value=False)
        self.var_sfx_inteligente   = tk.BooleanVar(value=False)
        self.var_punch_in          = tk.BooleanVar(value=False)
        self.var_motion_design     = tk.BooleanVar(value=False)
        self.var_censura           = tk.BooleanVar(value=False)
        self.var_vision_ativo      = tk.BooleanVar(value=False)
        self.var_cores_por_falante = tk.BooleanVar(value=False)
        self.var_thumb_auto        = tk.BooleanVar(value=False)

        lf_pre = ctk.CTkLabelFrame(main_frame, text=" Pre-Producao — Modulos Ativos ")
        lf_pre.pack(fill=tk.X, padx=15, pady=(10, 0))

        _checks_pre = [
            ("LIGAR DIRETOR IA (Chave Geral)",
             self.var_ia_ativa, "#FFFFFF"),
            ("Limpeza Semantica  (Remove gaguejos e falsos inicios via IA)",
             self.var_limpeza_semantica, "#64B5F6"),
            ("B-Roll Contextual  (Injeta videos baseados em tags do texto)",
             self.var_broll_contextual, "#81C784"),
            ("SFX Automatico  (Efeitos sonoros por categoria semantica — E13)",
             self.var_sfx_inteligente, "#FFB74D"),
            ("Punch-In Dinamico  (Zoom automatico em frases de enfase)",
             self.var_punch_in, "#CE93D8"),
            ("Motion Design  (Palavras flutuantes e textos animados — E12)",
             self.var_motion_design, "#F06292"),
            ("Censura Automatica  (Bipes e mute em palavras proibidas)",
             self.var_censura, "#FF8A65"),
        ]

        for i, (text, var, color) in enumerate(_checks_pre):
            row = ctk.CTkFrame(lf_pre)
            row.pack(fill=tk.X, padx=8, pady=2)
            indicator = ctk.CTkLabel(row, text="  ", fg_color=color, width=10)
            indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
            ctk.CTkSwitch(row, text=text, variable=var).pack(
                side=tk.LEFT, anchor="w", pady=5)

        # ── MÓDULOS AVANÇADOS ─────────────────────────────────────────────
        lf_adv = ctk.CTkLabelFrame(main_frame, text=" Avancado ")
        lf_adv.pack(fill=tk.X, padx=15, pady=(8, 0))

        _checks_adv = [
            ("[E15] Gemini Vision  (Analisa frames do video antes de editar — usa mais cota)",
             self.var_vision_ativo, "#4FC3F7"),
            ("[E22] Cores por Falante  (Detecta multiplos falantes e colore cada voz)",
             self.var_cores_por_falante, "#FFD54F"),
            ("[E17] Gerar Thumbnail Automaticamente  (Extrai melhor cena como capa)",
             self.var_thumb_auto, "#FF8A65"),
        ]
        for text, var, color in _checks_adv:
            row = ctk.CTkFrame(lf_adv)
            row.pack(fill=tk.X, padx=8, pady=2)
            ctk.CTkLabel(row, text="  ", fg_color=color, width=10).pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
            ctk.CTkSwitch(row, text=text, variable=var).pack(side=tk.LEFT, anchor="w", pady=5)

        # ── PROMPT IDENTIDADE CANAL ───────────────────────────────────────
        lf_canal = ctk.CTkLabelFrame(main_frame,
            text=" Identidade do Canal  (Contexto permanente — carregado em todo render) ")
        lf_canal.pack(fill=tk.BOTH, expand=False, padx=15, pady=(10, 0))

        ctk.CTkLabel(lf_canal,
            text="Descreva o canal: nome, publico, tom, formato, estilo visual.",
            font=("Segoe UI", 9), text_color="#888888").pack(anchor="w", padx=10, pady=(5, 0))

        self.txt_prompt_canal = ctk.CTkTextbox(
            lf_canal, height=80, font=("Segoe UI", 14)
        )
        self.txt_prompt_canal.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 0))

        frm_bc = ctk.CTkFrame(lf_canal)
        frm_bc.pack(fill=tk.X, padx=10, pady=(4, 8))
        ctk.CTkButton(frm_bc, text="Salvar Identidade",
                   command=self._salvar_prompt_canal).pack(side=tk.LEFT)
        self.lbl_canal_status = ctk.CTkLabel(frm_bc, text="",
            font=("Segoe UI", 9), text_color="#00E676")
        self.lbl_canal_status.pack(side=tk.LEFT, padx=10)

        # ── PROMPT ESTRATÉGICO ────────────────────────────────────────────
        lf_prompt = ctk.CTkLabelFrame(main_frame,
            text=" Prompt Estrategico do Diretor  (Guia a IA em TODO o render) ")
        lf_prompt.pack(fill=tk.BOTH, expand=False, padx=15, pady=(8, 0))

        ctk.CTkLabel(lf_prompt,
            text="Descreva a estrategia de edicao deste video especifico.",
            font=("Segoe UI", 9), text_color="#888888").pack(anchor="w", padx=10, pady=(5, 0))

        self.txt_prompt = ctk.CTkTextbox(
            lf_prompt, height=120, font=("Segoe UI", 14)
        )
        self.txt_prompt.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 0))

        frm_bp = ctk.CTkFrame(lf_prompt)
        frm_bp.pack(fill=tk.X, padx=10, pady=(4, 8))
        ctk.CTkButton(frm_bp, text="Salvar Prompt",
                   command=self._salvar_prompt).pack(side=tk.LEFT)
        ctk.CTkButton(frm_bp, text="Limpar",
                   command=lambda: self.txt_prompt.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=5)
        self.lbl_prompt_status = ctk.CTkLabel(frm_bp, text="",
            font=("Segoe UI", 9), text_color="#00E676")
        self.lbl_prompt_status.pack(side=tk.LEFT, padx=10)

        # ── LOG DA IA ─────────────────────────────────────────────────────
        lf_log = ctk.CTkLabelFrame(main_frame, text=" Log de Decisoes da IA (Tempo Real) ")
        lf_log.pack(fill=tk.BOTH, expand=True, padx=15, pady=(8, 0))

        self.txt_log = ctk.CTkTextbox(lf_log, height=150, font=("Consolas", 12))
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=(10, 10), pady=5)
        self.txt_log.configure(state=tk.DISABLED)

        # ── BOTÃO SALVAR ──────────────────────────────────────────────────
        frm_save = ctk.CTkFrame(main_frame)
        frm_save.pack(fill=tk.X, padx=15, pady=12)
        ctk.CTkButton(frm_save, text="Salvar Configuracoes da IA",
                  font=("Segoe UI", 11, "bold"),
                  padx=20, pady=8,
                  command=self.salvar_configs).pack(fill=tk.X)

        self._carregar_estado()

    # ─────────────────────────────────────────────────────────────────────────
    # LOG
    # ─────────────────────────────────────────────────────────────────────────
    def log(self, msg):
        self.txt_log.config(state=tk.NORMAL)
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state=tk.DISABLED)

    # ─────────────────────────────────────────────────────────────────────────
    # PERSISTÊNCIA
    # ─────────────────────────────────────────────────────────────────────────
    def _carregar_estado(self):
        if not self.config_manager: return
        cfg = self.config_manager.get("diretor_ia", {})
        self.var_ia_ativa.set(cfg.get("ia_ativa", True))
        self.var_limpeza_semantica.set(cfg.get("limpeza_semantica", False))
        self.var_broll_contextual.set(cfg.get("broll_contextual",  False))
        self.var_sfx_inteligente.set(cfg.get("sfx_inteligente",    False))
        self.var_punch_in.set(cfg.get("punch_in",                  False))
        self.var_motion_design.set(cfg.get("motion_design",        False))
        self.var_censura.set(cfg.get("censura",                    False))
        self.var_vision_ativo.set(cfg.get("vision_ativo",          False))
        self.var_cores_por_falante.set(cfg.get("cores_por_falante", False))
        self.var_thumb_auto.set(cfg.get("thumb_auto", True))
        # [E20] Carrega provider LLM salvo
        self.var_llm_provider.set(cfg.get("llm_provider", "gemini"))

        prompt_canal = cfg.get("prompt_canal", "")
        prompt_salvo = cfg.get("prompt_estrategico", "")
        if prompt_canal:
            self.txt_prompt_canal.delete("1.0", tk.END)
            self.txt_prompt_canal.insert("1.0", prompt_canal)
        if prompt_salvo:
            self.txt_prompt.delete("1.0", tk.END)
            self.txt_prompt.insert("1.0", prompt_salvo)

        self.log("[SISTEMA] Diretor de IA inicializado em modo Standby.")
        if prompt_salvo:
            preview = prompt_salvo[:80] + ("..." if len(prompt_salvo) > 80 else "")
            self.log(f"[PROMPT] Estrategia carregada: {preview}")

        # Popula o campo de API Key com a chave do provider atual
        self._on_provider_change()

    def _on_provider_change(self, event=None):
        if not self.config_manager: return
        pass # Apenas atualizamos a variavel interna, as chaves sao puxadas em tempo de execucao pelo pipeline

    def _salvar_prompt(self):
        if not self.config_manager:
            self.lbl_prompt_status.config(text="(sem config_manager)")
            return
        prompt = self.txt_prompt.get("1.0", tk.END).strip()
        cfg = self.config_manager.get("diretor_ia", {})
        cfg["prompt_estrategico"] = prompt
        self.config_manager.set("diretor_ia", cfg)
        self.lbl_prompt_status.config(text="Salvo!")
        self.log(f"[PROMPT] Estrategia salva ({len(prompt)} chars).")
        self.after(3000, lambda: self.lbl_prompt_status.config(text=""))

    def _salvar_llm_provider(self):
        """[E20] Salva o provider LLM selecionado."""
        if not self.config_manager:
            return
        provider = self.var_llm_provider.get()
        # Salva provider no diretor_ia
        cfg = self.config_manager.get("diretor_ia", {})
        cfg["llm_provider"] = provider
        self.config_manager.set("diretor_ia", cfg)
        
        self.lbl_llm_status.config(
            text=f"Provider '{provider.upper()}' salvo como ativo. As chaves serao lidas da config global.", text_color="#00E676")
        self.log(f"[E20] LLM Provider alterado para: {provider.upper()}")
        self.after(4000, lambda: self.lbl_llm_status.config(text="(As chaves de API sao carregadas automaticamente da Configuracao Global)", text_color="#AAAAAA"))

    def get_prompt_estrategico(self):
        return self.txt_prompt.get("1.0", tk.END).strip()

    def _salvar_prompt_canal(self):
        if not self.config_manager:
            self.lbl_canal_status.config(text="(sem config_manager)")
            return
        prompt = self.txt_prompt_canal.get("1.0", tk.END).strip()
        cfg = self.config_manager.get("diretor_ia", {})
        cfg["prompt_canal"] = prompt
        self.config_manager.set("diretor_ia", cfg)
        self.lbl_canal_status.config(text="Salvo!")
        self.log(f"[CANAL] Identidade atualizada ({len(prompt)} chars).")
        self.after(3000, lambda: self.lbl_canal_status.config(text=""))

    def get_prompt_canal(self):
        return self.txt_prompt_canal.get("1.0", tk.END).strip()

    def salvar_configs(self):
        if not self.config_manager: return
        cfg = self.config_manager.get("diretor_ia", {})
        cfg.update({
            "ia_ativa":          self.var_ia_ativa.get(),
            "limpeza_semantica": self.var_limpeza_semantica.get(),
            "broll_contextual":  self.var_broll_contextual.get(),
            "sfx_inteligente":   self.var_sfx_inteligente.get(),
            "punch_in":          self.var_punch_in.get(),
            "motion_design":     self.var_motion_design.get(),
            "censura":           self.var_censura.get(),
            "vision_ativo":      self.var_vision_ativo.get(),
            "modo_economico":    False,  # REMOVIDO — IA sempre usa API quando disponivel
            "cores_por_falante": self.var_cores_por_falante.get(),
            "thumb_auto":        self.var_thumb_auto.get(),
            "llm_provider":      self.var_llm_provider.get(),
        })
        self.config_manager.set("diretor_ia", cfg)
        messagebox.showinfo("Diretor IA", "Configuracoes salvas com sucesso!")
        self.log("[SISTEMA] Configuracoes de IA salvas.")

    def get_config(self):
        return {
            "ia_ativa":          self.var_ia_ativa.get(),
            "limpeza_semantica": self.var_limpeza_semantica.get(),
            "broll_contextual":  self.var_broll_contextual.get(),
            "sfx_inteligente":   self.var_sfx_inteligente.get(),
            "punch_in":          self.var_punch_in.get(),
            "motion_design":     self.var_motion_design.get(),
            "censura":           self.var_censura.get(),
            "vision_ativo":      self.var_vision_ativo.get(),
            "modo_economico":    False,  # REMOVIDO — IA sempre usa API quando disponivel
            "cores_por_falante": self.var_cores_por_falante.get(),
            "thumb_auto":        self.var_thumb_auto.get(),
            # Pos-producao (sempre ativo quando Diretor IA esta ligado)
            "lufs_normalizar":   True,
            "lufs_target":       -14,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # GEMINI STATUS
    # ─────────────────────────────────────────────────────────────────────────
    def _checar_chave_local(self):
        if not self.config_manager: return
        try:
            keys = self.config_manager.get_api_config("gemini", "api_keys")
            tem_chave = bool(keys and (
                isinstance(keys, list) and keys[0] or
                isinstance(keys, str) and keys.strip()
            ))
            if tem_chave:
                self.lbl_gemini_status.config(
                    text="Chave detectada — clique em Testar para validar a conexao",
                    text_color="#FFD700")
            else:
                self.lbl_gemini_status.config(
                    text="Nenhuma API Key configurada. Va em Configuracoes Globais > Gemini",
                    text_color="#FF4444")
        except Exception:
            pass

    def _testar_gemini_thread(self):
        self.lbl_gemini_status.config(text="Testando conexao...", text_color="#AAAAAA")
        threading.Thread(target=self._testar_gemini, daemon=True).start()

    def _testar_gemini(self):
        try:
            from ai_director_pipeline import AIDirectorPipeline
            pipeline = AIDirectorPipeline(self.config_manager)
            ok, msg = pipeline.testar_conexao_gemini()
            color = "#00E676" if ok else "#FF4444"
            self.after(0, lambda: self.lbl_gemini_status.config(text=msg, text_color=color))
            self.after(0, lambda: self.log(f"[GEMINI] {msg}"))
        except Exception as e:
            self.after(0, lambda e=e: self.lbl_gemini_status.config(
                text=f"Erro: {e}", text_color="#FF4444"))

    # ─────────────────────────────────────────────────────────────────────────
    # JANELA DE REVISÃO PRÉ-RENDER  [E9 + E16]
    # ─────────────────────────────────────────────────────────────────────────
    def show_preview_window(self, blocos):
        """
        [E9 + E16] Revisao Pre-Render automatizada.
        Aprova as decisoes da IA instantaneamente sem bloquear o fluxo com interface grafica.
        """
        self.log("[SISTEMA] Modo automatico ativado: Janela de aprovacao manual pulada.")
        for b in blocos:
            if b.get('corte_acao'):
                b['corte_confirmado'] = True
        return True
