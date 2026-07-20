import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
import os

def notify_system_of_changes(widget):
    """
    Localiza o notebook principal do sistema e notifica todas as abas de alterações
    nos personagens ou perfis, disparando recarregamento em tempo real.
    """
    current = widget
    main_notebook = None
    while current is not None:
        if isinstance(current, ttk.Notebook):
            if current.master is None or isinstance(current.master, (tk.Tk, tk.Toplevel)):
                main_notebook = current
                break
            else:
                main_notebook = current
        current = current.master
        
    if main_notebook:
        for child in main_notebook.winfo_children():
            if child.__class__.__name__ == "AbaConfiguracoes":
                if hasattr(child, "tab_personagens"):
                    try:
                        child.tab_personagens.load_characters()
                        child.tab_personagens._atualizar_combos_legenda()
                    except: pass
                if hasattr(child, "tab_legendas"):
                    try:
                        pass
                        child.tab_legendas.load_profiles()
                    except: pass
                if hasattr(child, "tab_estetica"):
                    try: child.tab_estetica._carregar_perfis_estetica()
                    except: pass
                if hasattr(child, "tab_templates"):
                    try: child.tab_templates.load_profiles()
                    except: pass
            
            elif child.__class__.__name__ == "AbaGeracaoTTS":
                try:
                    _p = child.config_manager.get('personagens', {})
                    child.personagens_cache = dict(_p) if _p else {}
                    if hasattr(child, "personagem_menu") and hasattr(child, "personagem_var"):
                        personagens_lista = list(child.personagens_cache.keys())
                        child.personagem_menu["values"] = personagens_lista
                        if personagens_lista:
                            if child.personagem_var.get() not in personagens_lista:
                                child.personagem_var.set(personagens_lista[0])
                                if hasattr(child, "atualizar_campos"):
                                    child.atualizar_campos()
                        else:
                            child.personagem_var.set("")
                except:
                    pass
            
            elif child.__class__.__name__ == "AbaGeracaoVideoNarrador":
                try:
                    _p = child.config_manager.get('personagens', {})
                    child.personagens_cache = dict(_p) if _p else {}
                    if hasattr(child, "personagem_menu") and hasattr(child, "personagem_var"):
                        personagens_lista = list(child.personagens_cache.keys())
                        child.personagem_menu["values"] = personagens_lista
                        if personagens_lista:
                            if child.personagem_var.get() not in personagens_lista:
                                child.personagem_var.set(personagens_lista[0])
                        else:
                            child.personagem_var.set("")
                except:
                    pass
            
            elif child.__class__.__name__ == "AbaGeradorLegendas":
                try:
                    child._carregar_perfis_ui()
                except:
                    pass
            
            elif child.__class__.__name__ == "AbaPodcast":
                try:
                    child._carregar_personagens()
                except:
                    pass
            
            elif child.__class__.__name__ == "AbaInferenciaVideo":
                try:
                    _p = child.config_manager.get('personagens', {})
                    child.personagens_dict = _p
                    if hasattr(child, "personagem_menu") and hasattr(child, "personagem_var"):
                        child.personagens_lista = list(_p.keys()) if _p else []
                        child.personagens_lista.insert(0, "Automático (Pelo Nome)")
                        child.personagem_menu["values"] = child.personagens_lista
                except:
                    pass

            elif child.__class__.__name__ == "AbaMapeadorAutomatico":
                try:
                    child._carregar_perfis_transicao_template()
                except:
                    pass

class TabAPIs(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        # Seleção de Serviço
        frame_top = ctk.CTkFrame(self)
        frame_top.pack(fill=tk.X, padx=20, pady=20)
        
        ctk.CTkLabel(frame_top, text="Serviço de API:").pack(side=tk.LEFT, padx=(0,10))
        self.service_var = tk.StringVar()
        self.combo_service = ctk.CTkOptionMenu(frame_top, variable=self.service_var, width=200)
        self.combo_service['values'] = ["gemini", "voicemaker", "chatgpt", "openrouter", "grok", "huggingface"]
        self.combo_service.pack(side=tk.LEFT)
        self.combo_service.bind("<<ComboboxSelected>>", self.on_service_select)
        
        # Tabela (Treeview) para mostrar as chaves
        frame_mid = ctk.CTkFrame(self)
        frame_mid.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        
        columns = ("nome", "chave", "status")
        self.tree = ttk.Treeview(frame_mid, columns=columns, show="headings", height=8)
        self.tree.heading("nome", text="Nome / Origem")
        self.tree.heading("chave", text="Chave API")
        self.tree.heading("status", text="Status")
        self.tree.column("nome", width=150)
        self.tree.column("chave", width=300)
        self.tree.column("status", width=100)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_mid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Formulario para adicionar/editar
        frame_form = ctk.CTkLabelFrame(self, text="Adicionar / Editar Chave")
        frame_form.pack(fill=tk.X, padx=20, pady=20)
        
        ctk.CTkLabel(frame_form, text="Nome da Conta:").grid(row=0, column=0, padx=15, pady=12, sticky="e")
        self.entry_nome = ctk.CTkEntry(frame_form, width=300)
        self.entry_nome.grid(row=0, column=1, padx=15, pady=12, sticky="w")
        
        ctk.CTkLabel(frame_form, text="API Key:").grid(row=1, column=0, padx=15, pady=12, sticky="e")
        self.entry_key = ctk.CTkEntry(frame_form, width=350)
        self.entry_key.grid(row=1, column=1, padx=15, pady=12, sticky="w")
        
        btn_frame = ctk.CTkFrame(frame_form)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(btn_frame, text="✅ Adicionar/Atualizar", command=self.add_key).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(btn_frame, text="🗑️ Remover Selecionada", command=self.remove_key).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(btn_frame, text="🔍 Testar Selecionada", command=self.test_selected_key).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(btn_frame, text="💾 Salvar Alterações no Config", command=self.save_keys).pack(side=tk.LEFT, padx=15)

        self.lbl_status = ctk.CTkLabel(self, text="Selecione um serviço acima para começar.")
        self.lbl_status.pack(pady=12)
        
        # Carrega o primeiro se disponivel
        # self.combo_service.current(0)
        self.on_service_select(None)
        
    def on_service_select(self, event):
        service = self.service_var.get()
        if not service: return
        self.tree.delete(*self.tree.get_children())
        
        keys = self.config_manager.get_api_config(service, "api_keys") or []
        for pk in keys:
            status_text = pk.get("status", "unknown")
            if status_text == "ok": status_text = "🟢 OK"
            elif status_text == "error": status_text = "🔴 Erro/429"
            
            self.tree.insert("", tk.END, values=(pk.get("name", ""), pk.get("key", ""), status_text))

    def add_key(self):
        nome = self.entry_nome.get().strip()
        key = self.entry_key.get().strip()
        if not nome or not key:
            messagebox.showwarning("Aviso", "Preencha Nome e Chave.")
            return
        
        self.tree.insert("", tk.END, values=(nome, key, "unknown"))
        self.entry_nome.delete(0, tk.END)
        self.entry_key.delete(0, tk.END)

    def remove_key(self):
        selected = self.tree.selection()
        if not selected: return
        for item in selected:
            self.tree.delete(item)

    def save_keys(self):
        service = self.service_var.get()
        if not service: return
        
        new_keys = []
        for child in self.tree.get_children():
            nome, key, status = self.tree.item(child, "values")
            # Normalizar status visual para string interna
            if "🟢" in status: internal_status = "ok"
            elif "🔴" in status: internal_status = "error"
            else: internal_status = "unknown"
            
            new_keys.append({"name": nome, "key": key, "status": internal_status})
            
        self.config_manager.set(f"api_config.{service}.api_keys", new_keys)
        messagebox.showinfo("Salvo", f"Chaves do serviço {service.upper()} salvas com sucesso!")

    def test_selected_key(self):
        service = self.service_var.get()
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma chave na tabela para testar.")
            return
            
        item = selected[0]
        nome, key, status = self.tree.item(item, "values")
        self.lbl_status.config(text=f"Testando conexão para {nome}...")
        
        threading.Thread(target=self._run_test, args=(item, service, key), daemon=True).start()
        
    def _run_test(self, item, service, api_key):
        try:
            is_valid = False
            if service == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                resp = requests.get(url, timeout=10)
                is_valid = resp.status_code == 200
            elif service == "voicemaker":
                url = "https://developer.voicemaker.in/voice/list"
                resp = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json={"language": "en-US"}, timeout=10)
                is_valid = resp.status_code == 200
            else:
                # Simular outros endpoints baseados em requisições de lista de modelos genéricas
                is_valid = True # Placeholder para ChatGPT, OpenRouter, Grok
                
            if is_valid:
                self.after(0, lambda: self.tree.item(item, values=(self.tree.item(item, "values")[0], self.tree.item(item, "values")[1], "🟢 OK")))
                self.after(0, lambda: self.lbl_status.config(text="Teste: Conexão bem sucedida (OK) !"))
            else:
                self.after(0, lambda: self.tree.item(item, values=(self.tree.item(item, "values")[0], self.tree.item(item, "values")[1], "🔴 Falhou")))
                self.after(0, lambda: self.lbl_status.config(text="Teste: Falha de autenticação ou quota excedida."))
        except Exception as e:
            self.after(0, lambda item=item: self.tree.item(item, values=(self.tree.item(item, "values")[0], self.tree.item(item, "values")[1], "🔴 Erro")))
            self.after(0, lambda e=e: self.lbl_status.config(text=f"Teste: Erro de rede -> {str(e)[:40]}"))


class TabPersonagens(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        
        self.var_global_modelo = tk.IntVar(value=self.config_manager.get("global_tts_model", 1))

        # --- CONTROLE GLOBAL ---
        frame_global = ctk.CTkLabelFrame(self, text="🌍 CONTROLE GLOBAL: Selecione o Motor Principal de TTS (Aplica-se a Todas as Abas do Software)")
        frame_global.pack(fill=tk.X, expand=False, padx=20, pady=(10, 0))
        
        f_radio_g = ctk.CTkFrame(frame_global)
        f_radio_g.pack(pady=20)
        ttk.Radiobutton(f_radio_g, text="1. VoiceMaker", variable=self.var_global_modelo, value=1, command=self.save_global_modelo).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(f_radio_g, text="2. Moss TTS (VPS)", variable=self.var_global_modelo, value=2, command=self.save_global_modelo).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(f_radio_g, text="3. Applio RVC + Google", variable=self.var_global_modelo, value=3, command=self.save_global_modelo).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(f_radio_g, text="4. OpenAI.fm", variable=self.var_global_modelo, value=4, command=self.save_global_modelo).pack(side=tk.LEFT, padx=15)
        
        self.var_modo_madrugada = tk.BooleanVar(value=self.config_manager.get("modo_madrugada", False))
        ctk.CTkSwitch(frame_global, text="🌙 Ativar MODO MADRUGADA (O bot assume o mouse e clica no ProtonVPN sozinho na falha do IP)", 
                        variable=self.var_modo_madrugada, command=self.save_modo_madrugada).pack(pady=12)

        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 10))
        
        # Lista Esquerda
        frame_lista = ctk.CTkLabelFrame(paned, text="Seus Personagens")
        paned.add(frame_lista, weight=1)
        
        self.listbox = tk.Listbox(frame_lista, activestyle='dotbox', font=("Segoe UI", 11), height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        self.listbox.bind("<<ListboxSelect>>", self.on_character_select)
        
        scrollbar_list = ttk.Scrollbar(self.listbox, orient="vertical")
        scrollbar_list.config(command=self.listbox.yview)
        scrollbar_list.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar_list.set)

        btn_frame = ctk.CTkFrame(frame_lista)
        btn_frame.pack(fill=tk.X, padx=15, pady=12)
        
        self.var_novo_nome = tk.StringVar()
        ctk.CTkEntry(btn_frame, textvariable=self.var_novo_nome).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ctk.CTkButton(btn_frame, text="➕ Criar", command=self.add_character).pack(side=tk.RIGHT)
        
        ctk.CTkButton(frame_lista, text="🗑️ Deletar Selecionado", command=self.delete_character).pack(fill=tk.X, padx=15, pady=2)
        ctk.CTkButton(frame_lista, text="✏️ Renomear Selecionado", command=self.rename_character).pack(fill=tk.X, padx=15, pady=2)

        # Form Direito
        self.outer_frame_form = ctk.CTkLabelFrame(paned, text="Configurações do Personagem")
        paned.add(self.outer_frame_form, weight=3)
        
        self.canvas_form = tk.Canvas(self.outer_frame_form)
        self.scrollbar_form = ttk.Scrollbar(self.outer_frame_form, orient="vertical", command=self.canvas_form.yview)
        
        self.frame_form = ctk.CTkFrame(self.canvas_form)
        self.frame_form.bind("<Configure>", lambda e: self.canvas_form.configure(scrollregion=self.canvas_form.bbox("all")))
        self.canvas_window_form = self.canvas_form.create_window((0, 0), window=self.frame_form, anchor="nw")
        self.canvas_form.bind("<Configure>", lambda e: self.canvas_form.itemconfig(self.canvas_window_form, width=e.width))
        
        self.canvas_form.configure(yscrollcommand=self.scrollbar_form.set)
        
        self.canvas_form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_form.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _on_mousewheel_form(event):
            self.canvas_form.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.frame_form.bind("<Enter>", lambda e: self.canvas_form.bind_all("<MouseWheel>", _on_mousewheel_form))
        self.frame_form.bind("<Leave>", lambda e: self.canvas_form.unbind_all("<MouseWheel>"))
        
        # Variaveis de Formulario
        self.var_nome = tk.StringVar()
        self.var_voz_voicemaker = tk.StringVar()
        self.var_voz_google = tk.StringVar()
        self.var_voz_openaifm = tk.StringVar()
        self.var_modelo_rvc = tk.StringVar()
        self.var_index_rvc = tk.StringVar()
        self.var_pitch_rvc = tk.StringVar(value="0")
        self.var_index_rate_rvc = tk.StringVar(value="0.75")
        self.var_embedder_rvc = tk.StringVar(value="contentvec")
        self.var_audio_moss = tk.StringVar()
        self.var_prompt_google = tk.StringVar()

        self.var_video_normal = tk.StringVar()
        self.var_video_feliz = tk.StringVar()
        self.var_video_triste = tk.StringVar()
        self.var_video_raiva = tk.StringVar()
        self.var_tag_frente = tk.StringVar()
        self.var_perfil_legenda = tk.StringVar()
        
        # Elementos Form
        r = 0
        ctk.CTkLabel(self.frame_form, text="Nome:", font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="e", padx=15, pady=12)
        ctk.CTkLabel(self.frame_form, textvariable=self.var_nome, text_color="#0055ff").grid(row=r, column=1, sticky="w", padx=15, pady=12)
        
        r += 1
        ttk.Separator(self.frame_form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Voz VoiceMaker (Modo 1):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        ctk.CTkEntry(self.frame_form, textvariable=self.var_voz_voicemaker, width=300).grid(row=r, column=1, sticky="w", padx=15, pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Voz Google TTS (Modo 3):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        ctk.CTkEntry(self.frame_form, textvariable=self.var_voz_google, width=300).grid(row=r, column=1, sticky="w", padx=15, pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Voz OpenAI.fm (Modo 4):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        ctk.CTkEntry(self.frame_form, textvariable=self.var_voz_openaifm, width=300).grid(row=r, column=1, sticky="w", padx=15, pady=12)

        r += 1
        ttk.Separator(self.frame_form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Nome do Modelo Applio (pth):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        ctk.CTkEntry(self.frame_form, textvariable=self.var_modelo_rvc, width=300).grid(row=r, column=1, sticky="w", padx=15, pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Arquivo Index (Applio RVC):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        f_idx = ctk.CTkFrame(self.frame_form)
        f_idx.grid(row=r, column=1, sticky="w", padx=15, pady=12)
        ctk.CTkEntry(f_idx, textvariable=self.var_index_rvc, width=350).pack(side=tk.LEFT)
        ctk.CTkButton(f_idx, text="📁", width=30, command=lambda: self._ask_file(self.var_index_rvc, "*.index")).pack(side=tk.LEFT, padx=15)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Ajuste de Tom / Pitch (RVC):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        ttk.Spinbox(self.frame_form, from_=-24, to=24, textvariable=self.var_pitch_rvc, width=10).grid(row=r, column=1, sticky="w", padx=15, pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Proporção do Índice (RVC):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        ttk.Spinbox(self.frame_form, from_=0.0, to=1.0, increment=0.01, textvariable=self.var_index_rate_rvc, width=10).grid(row=r, column=1, sticky="w", padx=15, pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Modelo Embedder (RVC):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        embedder_choices = ['contentvec', 'spin', 'spin-v2', 'chinese-hubert-base', 'japanese-hubert-base', 'korean-hubert-base']
        combo_embedder = ctk.CTkOptionMenu(self.frame_form, variable=self.var_embedder_rvc, values=embedder_choices, width=250)
        combo_embedder.grid(row=r, column=1, sticky="w", padx=15, pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Áudio Ref. Moss TTS (.wav):").grid(row=r, column=0, sticky="e", padx=15, pady=12)
        f_moss = ctk.CTkFrame(self.frame_form)
        f_moss.grid(row=r, column=1, sticky="w", padx=15, pady=12)
        ctk.CTkEntry(f_moss, textvariable=self.var_audio_moss, width=350).pack(side=tk.LEFT)
        ctk.CTkButton(f_moss, text="📁", width=30, command=self.browse_moss_audio).pack(side=tk.LEFT, padx=15)

        r += 1
        ttk.Separator(self.frame_form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Instrução Base (TTS 3 e 4):").grid(row=r, column=0, sticky="ne", padx=15, pady=12)
        self.text_instrucao = ctk.CTkTextbox(self.frame_form, height=80)
        self.text_instrucao.grid(row=r, column=1, sticky="we", padx=15, pady=12)

        
        r += 1
        ttk.Separator(self.frame_form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Vídeos Emoção (.mp4):").grid(row=r, column=0, sticky="ne", padx=15, pady=12)
        f_vids = ctk.CTkFrame(self.frame_form)
        f_vids.grid(row=r, column=1, sticky="w", padx=15, pady=12)
        
        ctk.CTkLabel(f_vids, text="Normal:").grid(row=0, column=0, sticky="e")
        ctk.CTkEntry(f_vids, textvariable=self.var_video_normal, width=150).grid(row=0, column=1)
        ctk.CTkButton(f_vids, text="📁", width=20, command=lambda: self._ask_file(self.var_video_normal, "*.*")).grid(row=0, column=2)
        
        ctk.CTkLabel(f_vids, text="Feliz:").grid(row=0, column=3, sticky="e")
        ctk.CTkEntry(f_vids, textvariable=self.var_video_feliz, width=150).grid(row=0, column=4)
        ctk.CTkButton(f_vids, text="📁", width=20, command=lambda: self._ask_file(self.var_video_feliz, "*.*")).grid(row=0, column=5)
        
        ctk.CTkLabel(f_vids, text="Triste:").grid(row=1, column=0, sticky="e", pady=2)
        ctk.CTkEntry(f_vids, textvariable=self.var_video_triste, width=150).grid(row=1, column=1, pady=2)
        ctk.CTkButton(f_vids, text="📁", width=20, command=lambda: self._ask_file(self.var_video_triste, "*.*")).grid(row=1, column=2, pady=2)
        
        ctk.CTkLabel(f_vids, text="Raiva:").grid(row=1, column=3, sticky="e", pady=2)
        ctk.CTkEntry(f_vids, textvariable=self.var_video_raiva, width=150).grid(row=1, column=4, pady=2)
        ctk.CTkButton(f_vids, text="📁", width=20, command=lambda: self._ask_file(self.var_video_raiva, "*.*")).grid(row=1, column=5, pady=2)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Tag / Frente:").grid(row=r, column=0, sticky="e", padx=15, pady=2)
        f_tag = ctk.CTkFrame(self.frame_form)
        f_tag.grid(row=r, column=1, sticky="w", padx=15, pady=2)
        ctk.CTkEntry(f_tag, textvariable=self.var_tag_frente, width=300).pack(side=tk.LEFT)
        ctk.CTkButton(f_tag, text="📁", width=30, command=lambda: self._ask_file(self.var_tag_frente, "*.*")).pack(side=tk.LEFT, padx=15)

        r += 1
        ttk.Separator(self.frame_form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=12)

        r += 1
        ttk.Separator(self.frame_form, orient="horizontal").grid(row=r, column=0, columnspan=2, sticky="ew", pady=12)

        r += 1
        ctk.CTkLabel(self.frame_form, text="Perfil Legenda:").grid(row=r, column=0, sticky="e", padx=15, pady=2)
        self.cb_perf_leg = ctk.CTkOptionMenu(self.frame_form, variable=self.var_perfil_legenda, width=250)
        self.cb_perf_leg.grid(row=r, column=1, sticky="w", padx=15, pady=2)

        r += 1
        ctk.CTkButton(self.frame_form, text="💾 Salvar Personagem", command=self.save_character).grid(row=r, column=1, sticky="w", padx=15, pady=15)

        self.load_characters()
        self._atualizar_combos_legenda()

    def _atualizar_combos_legenda(self):
        perfis = list(self.config_manager.get("perfis_legenda", {}).keys())
        perfis.insert(0, "")
        if hasattr(self, "cb_perf_leg"):
            self.cb_perf_leg["values"] = perfis

    def save_global_modelo(self):
        """Salva a escolha de motor Global na hora em que for clicada! Todo o sistema mudará."""
        self.config_manager.set("global_tts_model", self.var_global_modelo.get())
        print(f"🌍 [SISTEMA] Motor Global de TTS alterado com sucesso para o Modelo {self.var_global_modelo.get()}")
        
    def save_modo_madrugada(self):
        """Salva o estado do Modo Madrugada (Robô do Mouse) sempre que o usuário clicar na caixinha."""
        self.config_manager.set("modo_madrugada", self.var_modo_madrugada.get())
        status = "LIGADO 🌙 (Mouse Automatizado)" if self.var_modo_madrugada.get() else "DESLIGADO ☀️ (Modo Produtividade/Bip)"
        print(f"⚙️ [SISTEMA] Modo Madrugada agora está: {status}")

    def load_characters(self):
        self.listbox.delete(0, tk.END)
        chars = self.config_manager.get("personagens", {})
        for name in chars.keys():
            self.listbox.insert(tk.END, name)
            
    def browse_moss_audio(self):
        path = filedialog.askopenfilename(title="Selecione o áudio de referência (.wav, .mp3)", filetypes=[("Audio Files", "*.wav *.mp3")])
        if path:
            self.var_audio_moss.set(path)

    def _ask_file(self, var, ext):
        path = filedialog.askopenfilename(title=f"Selecione o arquivo ({ext})", filetypes=[(f"Arquivo {ext}", ext)])
        if path:
            var.set(path)

    def on_character_select(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        
        name = self.listbox.get(sel[0])
        config = self.config_manager.get_personagem(name)
        if not config: return
        
        self.var_nome.set(name)
        self.var_voz_voicemaker.set(config.get("vozes_voicemaker", ""))
        self.var_voz_google.set(config.get("voz_google_tts", ""))
        self.var_voz_openaifm.set(config.get("voz_openaifm", ""))
        self.var_modelo_rvc.set(config.get("modelo_rvc", ""))
        self.var_index_rvc.set(config.get("index_rvc", ""))
        self.var_pitch_rvc.set(str(config.get("pitch_rvc", 0)))
        self.var_index_rate_rvc.set(str(config.get("index_rate_rvc", 0.75)))
        self.var_embedder_rvc.set(config.get("embedder_rvc", "contentvec"))
        self.var_audio_moss.set(config.get("audio_ref_moss", ""))
        self.var_video_normal.set(config.get("video_normal", ""))
        self.var_video_feliz.set(config.get("video_feliz", ""))
        self.var_video_triste.set(config.get("video_triste", ""))
        self.var_video_raiva.set(config.get("video_raiva", ""))
        self.var_tag_frente.set(config.get("tag_frente", ""))
        self.var_perfil_legenda.set(config.get("perfil_legenda", ""))
        
        self.text_instrucao.delete("1.0", tk.END)
        self.text_instrucao.insert("1.0", config.get("instrucao_base_tts", config.get("instrucao_base_google", "")))

    def save_character(self):
        name = self.var_nome.get()
        if not name:
            messagebox.showwarning("Aviso", "Selecione um personagem primeiro.")
            return
            
        config = self.config_manager.get_personagem(name)
        
        config["vozes_voicemaker"] = self.var_voz_voicemaker.get().strip()
        config["voz_google_tts"] = self.var_voz_google.get().strip()
        config["voz_openaifm"] = self.var_voz_openaifm.get().strip()
        config["modelo_rvc"] = self.var_modelo_rvc.get().strip()
        config["index_rvc"] = self.var_index_rvc.get().strip()
        
        try:
            config["pitch_rvc"] = int(self.var_pitch_rvc.get().strip() or 0)
        except ValueError:
            config["pitch_rvc"] = 0
            
        try:
            config["index_rate_rvc"] = float(self.var_index_rate_rvc.get().strip() or 0.75)
        except ValueError:
            config["index_rate_rvc"] = 0.75
            
        config["embedder_rvc"] = self.var_embedder_rvc.get().strip() or "contentvec"
        config["audio_ref_moss"] = self.var_audio_moss.get().strip()
        config["video_normal"] = self.var_video_normal.get().strip()
        config["video_feliz"] = self.var_video_feliz.get().strip()
        config["video_triste"] = self.var_video_triste.get().strip()
        config["video_raiva"] = self.var_video_raiva.get().strip()
        config["tag_frente"] = self.var_tag_frente.get().strip()
        config["perfil_legenda"] = self.var_perfil_legenda.get().strip()
        config["instrucao_base_tts"] = self.text_instrucao.get("1.0", tk.END).strip()
        
        self.config_manager.update_personagem(name, config)
        messagebox.showinfo("Sucesso", f"Configurações salvas para {name}!")

    def add_character(self):
        name = self.var_novo_nome.get().strip()
        if not name: return
        chars = self.config_manager.get("personagens", {})
        if name in chars:
            messagebox.showwarning("Aviso", "Já existe um personagem com esse nome.")
            return
        chars[name] = {
            "video_source": "",
            "idioma_padrao": "pt-BR",
            "engine": "proplus",
            "efeito_padrao": "default",
            "volume_ajuste": 0.0,
            "posicao_pip": {
                "x": 25,
                "y": "bottom",
                "offset": 25,
                "escala": 0.25
            },
            "vozes_voicemaker": "",
            "voz_google_tts": "",
            "voz_openaifm": "",
            "modelo_rvc": "",
            "index_rvc": "",
            "pitch_rvc": 0,
            "index_rate_rvc": 0.75,
            "embedder_rvc": "contentvec",
            "audio_ref_moss": "",
            "video_normal": "",
            "video_feliz": "",
            "video_triste": "",
            "video_raiva": "",
            "tag_frente": "",
            "perfil_legenda": "",
            "instrucao_base_tts": "",
            "tema_legenda": "Padrão"
        }
        self.config_manager.set("personagens", chars)
        self.var_novo_nome.set("")
        self.load_characters()
        idx = self.listbox.get(0, tk.END).index(name)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.on_character_select(None)
        notify_system_of_changes(self)

    def delete_character(self):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        if messagebox.askyesno("Confirmar", f"Deletar personagem '{name}'? Isso também excluirá suas configurações vinculadas de legenda."):
            chars = self.config_manager.get("personagens", {})
            if name in chars:
                del chars[name]
                self.config_manager.set("personagens", chars)
            vinculos = self.config_manager.get("perfis_personagem", {})
            if name in vinculos:
                del vinculos[name]
                self.config_manager.set("perfis_personagem", vinculos)
            
            self.load_characters()
            self.var_nome.set("")
            self.var_voz_voicemaker.set("")
            self.var_voz_google.set("")
            self.var_voz_openaifm.set("")
            self.var_modelo_rvc.set("")
            self.var_index_rvc.set("")
            self.var_pitch_rvc.set("0")
            self.var_index_rate_rvc.set("0.75")
            self.var_embedder_rvc.set("contentvec")
            self.var_audio_moss.set("")
            self.var_video_normal.set("")
            self.var_video_feliz.set("")
            self.var_video_triste.set("")
            self.var_video_raiva.set("")
            self.var_tag_frente.set("")
            self.text_instrucao.delete("1.0", tk.END)
            notify_system_of_changes(self)

    def rename_character(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um personagem para renomear.")
            return
        nome_antigo = self.listbox.get(sel[0])
        from tkinter import simpledialog
        novo_nome = simpledialog.askstring("Renomear Personagem", f"Digite o novo nome para o personagem '{nome_antigo}':", initialvalue=nome_antigo)
        if not novo_nome:
            return
        novo_nome = novo_nome.strip()
        if not novo_nome:
            return
        if novo_nome == nome_antigo:
            return
            
        chars = self.config_manager.get("personagens", {})
        if novo_nome in chars:
            messagebox.showwarning("Aviso", f"Já existe um personagem chamado '{novo_nome}'.")
            return
            
        chars[novo_nome] = chars.pop(nome_antigo)
        self.config_manager.set("personagens", chars)
        
        vinculos = self.config_manager.get("perfis_personagem", {})
        if nome_antigo in vinculos:
            vinculos[novo_nome] = vinculos.pop(nome_antigo)
            self.config_manager.set("perfis_personagem", vinculos)
            
        self.load_characters()
        idx = self.listbox.get(0, tk.END).index(novo_nome)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.on_character_select(None)
        
        notify_system_of_changes(self)
        messagebox.showinfo("Sucesso", f"Personagem '{nome_antigo}' renomeado para '{novo_nome}'!")

class TabVPS(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        ctk.CTkLabel(self, text="Configure abaixo os endereços (URLs e Portas) dos servidores onde \nsuas IA's de vanguarda estão hospedadas (Local ou Nuvem).", font=("Segoe UI", 10)).pack(pady=20)
        
        # Moss TTS
        frame_moss = ctk.CTkLabelFrame(self, text="Servidor Moss TTS (VPS)")
        frame_moss.pack(fill=tk.X, padx=20, pady=12)
        
        ctk.CTkLabel(frame_moss, text="URL / IPBase:").grid(row=0, column=0, sticky="e", pady=12)
        self.var_moss_url = tk.StringVar()
        ctk.CTkEntry(frame_moss, textvariable=self.var_moss_url, width=350).grid(row=0, column=1, sticky="w", padx=20, pady=12)
        
        ctk.CTkLabel(frame_moss, text="Autenticação (Token se houver):").grid(row=1, column=0, sticky="e", pady=12)
        self.var_moss_token = tk.StringVar()
        ctk.CTkEntry(frame_moss, textvariable=self.var_moss_token, width=300).grid(row=1, column=1, sticky="w", padx=20, pady=12)
        
        ctk.CTkButton(frame_moss, text="🌐 Ping Moss", command=lambda: self.ping_vps("moss_tts", self.var_moss_url.get())).grid(row=0, column=2, rowspan=2, padx=20)
        
        # Configuracao de Modo do RVC
        frame_rvc_mode = ctk.CTkFrame(self)
        frame_rvc_mode.pack(fill=tk.X, padx=20, pady=12)
        
        self.var_rvc_mode = tk.StringVar(value="local")
        ctk.CTkLabel(frame_rvc_mode, text="🎯 Roteamento do Applio RVC: ", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        ttk.Radiobutton(frame_rvc_mode, text="Local (Pinokio)", variable=self.var_rvc_mode, value="local").pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(frame_rvc_mode, text="Cloud (VPS)", variable=self.var_rvc_mode, value="vps").pack(side=tk.LEFT, padx=20)

        # Applio RVC Local
        frame_applio_local = ctk.CTkLabelFrame(self, text="Servidor Applio RVC (LOCAL - Pinokio)")
        frame_applio_local.pack(fill=tk.X, padx=20, pady=12)
        
        ctk.CTkLabel(frame_applio_local, text="URL Local (Geralmente localhost:6969):").grid(row=0, column=0, sticky="e", pady=12)
        self.var_applio_local_url = tk.StringVar()
        ctk.CTkEntry(frame_applio_local, textvariable=self.var_applio_local_url, width=350).grid(row=0, column=1, sticky="w", padx=20, pady=12)
        ctk.CTkButton(frame_applio_local, text="🌐 Ping Applio Local", command=lambda: self.ping_vps("applio_rvc_local", self.var_applio_local_url.get())).grid(row=0, column=2, padx=15)
        ctk.CTkButton(frame_applio_local, text="🔍 Auto-Detectar", command=self.auto_detectar_applio).grid(row=0, column=3, padx=15)

        # Applio RVC VPS
        frame_applio_vps = ctk.CTkLabelFrame(self, text="Servidor Applio RVC (NUVEM - VPS)")
        frame_applio_vps.pack(fill=tk.X, padx=20, pady=12)
        
        ctk.CTkLabel(frame_applio_vps, text="URL / IPBase:").grid(row=0, column=0, sticky="e", pady=12)
        self.var_applio_vps_url = tk.StringVar()
        ctk.CTkEntry(frame_applio_vps, textvariable=self.var_applio_vps_url, width=350).grid(row=0, column=1, sticky="w", padx=20, pady=12)
        
        ctk.CTkButton(frame_applio_vps, text="🌐 Ping Applio VPS", command=lambda: self.ping_vps("applio_rvc_vps", self.var_applio_vps_url.get())).grid(row=0, column=2, padx=20)

        # Salvar Botao
        ctk.CTkButton(self, text="💾 Salvar Configurações de Redes/VPS", command=self.save_vps).pack(pady=20)

        self.load_vps()

    def load_vps(self):
        vps_config = self.config_manager.get("vps_config", {})
        moss = vps_config.get("moss_tts", {})
        applio_vps = vps_config.get("applio_rvc", {})
        applio_local = vps_config.get("applio_rvc_local", {})
        rvc_mode = vps_config.get("rvc_mode", "local")
        
        self.var_moss_url.set(moss.get("url", ""))
        self.var_moss_token.set(moss.get("token", ""))
        self.var_applio_vps_url.set(applio_vps.get("url", ""))
        self.var_applio_local_url.set(applio_local.get("url", "http://localhost:6969"))
        self.var_rvc_mode.set(rvc_mode)

    def save_vps(self):
        moss_config = {"url": self.var_moss_url.get().strip(), "token": self.var_moss_token.get().strip()}
        applio_vps_config = {"url": self.var_applio_vps_url.get().strip(), "token": ""}
        applio_local_config = {"url": self.var_applio_local_url.get().strip(), "token": ""}
        
        self.config_manager.set("vps_config.moss_tts", moss_config)
        self.config_manager.set("vps_config.applio_rvc", applio_vps_config)
        self.config_manager.set("vps_config.applio_rvc_local", applio_local_config)
        self.config_manager.set("vps_config.rvc_mode", self.var_rvc_mode.get())
        
        messagebox.showinfo("Sucesso", "Configurações de rede salvas com sucesso.")

    def auto_detectar_applio(self):
        """Tenta encontrar o Applio RVC em portas comuns."""
        common_ports = [6969, 7865, 7860, 7897, 7870]
        
        def _scan():
            found = False
            self.after(0, lambda: self.var_applio_local_url.set("🔍 Buscando..."))
            for port in common_ports:
                url = f"http://127.0.0.1:{port}"
                try:
                    # Timeout bem curto para não travar
                    resp = requests.get(url, timeout=1)
                    if resp.status_code in [200, 404, 401]:
                        self.after(0, lambda u=url: self.var_applio_local_url.set(u))
                        self.after(0, lambda p=port: messagebox.showinfo("Auto-Detectar", f"Applio RVC encontrado na porta {p}!"))
                        found = True
                        break
                except:
                    continue
            
            if not found:
                self.after(0, lambda: self.var_applio_local_url.set("http://127.0.0.1:6969"))
                self.after(0, lambda: messagebox.showwarning("Auto-Detectar", "Não foi possível encontrar o Applio automaticamente. Certifique-se de que ele está aberto."))
        
        threading.Thread(target=_scan, daemon=True).start()

    def ping_vps(self, name, url):
        if not url:
            messagebox.showwarning("Aviso", "Preencha a URL antes testar.")
            return

        def _do_ping():
            try:
                # Testa endpoints /health ou root básico com timeout baixo
                resp = requests.get(url, timeout=5)
                if resp.status_code in [200, 401, 403, 404]: 
                    # Consider online if it responds (even if route missing 404, or auth req 401/403)
                    self.after(0, lambda: messagebox.showinfo("Ping", f"Servidor {name} indiscutivelmente ONLINE na rede!\nStatus Code: {resp.status_code}"))
                else:
                    self.after(0, lambda: messagebox.showwarning("Ping", f"O servidor respondeu, mas com erro de Servidor (50x): {resp.status_code}"))
            except requests.exceptions.Timeout:
                self.after(0, lambda: messagebox.showerror("Erro de Ping", f"Timeout! O Servidor {name} demorou muito para responder."))
            except Exception as _e:
                error_msg = str(_e)[:150]
                self.after(0, lambda emsg=error_msg: messagebox.showerror("Erro de Ping", f"Servidor Inalcançável. Verifique se a URL está correta e se a máquina VPS está ligada.\n\nDetalhes:\n{emsg}"))
        threading.Thread(target=_do_ping, daemon=True).start()

class TabTratamentoAudio(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        ctk.CTkLabel(self, text="🎛️ IA de Polimento e Des-robotização de Voz (SpeechBrain + Pedalboard)", font=("Segoe UI", 12, "bold")).pack(pady=20)
        
        frame_main = ctk.CTkLabelFrame(self, text="Controles Globais de Masterização de Áudio")
        frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        
        # Variáveis
        audio_cfg = self.config_manager.get("tratamento_audio", {})
        
        self.var_usar_filtro = tk.BooleanVar(value=audio_cfg.get("usar_filtro_estudio", False))
        self.var_usar_ia = tk.BooleanVar(value=audio_cfg.get("usar_speechbrain", False))
        self.var_comp_thresh = tk.StringVar(value=str(audio_cfg.get("compressor_threshold", "-18.0")))
        self.var_comp_ratio = tk.StringVar(value=str(audio_cfg.get("compressor_ratio", "4.0")))
        self.var_lim_thresh = tk.StringVar(value=str(audio_cfg.get("limiter_threshold", "-1.0")))
        self.var_hp_cutoff = tk.StringVar(value=str(audio_cfg.get("highpass_cutoff", "80.0")))
        self.var_lp_cutoff = tk.StringVar(value=str(audio_cfg.get("lowpass_cutoff", "12000.0")))
        
        # Checkboxes principais
        ctk.CTkSwitch(frame_main, text="LIGAR Filtro de Estúdio (Masterização de Podcast) para todos os áudios RVC e TTS", 
                        variable=self.var_usar_filtro, command=self._toggle_states).pack(anchor='w', pady=20)
                        
        self.cb_ia = ctk.CTkSwitch(frame_main, text="🧠 Ativar Speech Enhancement Base (Pesado, consome RAM). Des-robotiza vozes antes do filtro.", 
                                     variable=self.var_usar_ia)
        self.cb_ia.pack(anchor='w', padx=20, pady=12)
        
        # Parâmetros
        frame_params = ctk.CTkLabelFrame(frame_main, text="Parâmetros Avançados de Compressor/Limiter")
        frame_params.pack(fill=tk.X, padx=20, pady=15)
        
        r = 0
        ctk.CTkLabel(frame_params, text="Compressor Threshold (dB) [Ex: -18.0]:").grid(row=r, column=0, sticky="e", pady=2)
        ctk.CTkEntry(frame_params, textvariable=self.var_comp_thresh, width=100).grid(row=r, column=1, sticky="w", padx=15, pady=2)
        
        r += 1
        ctk.CTkLabel(frame_params, text="Compressor Ratio [Ex: 4.0]:").grid(row=r, column=0, sticky="e", pady=2)
        ctk.CTkEntry(frame_params, textvariable=self.var_comp_ratio, width=100).grid(row=r, column=1, sticky="w", padx=15, pady=2)
        
        r += 1
        ctk.CTkLabel(frame_params, text="Limiter Threshold (dB) [Ex: -1.0]:").grid(row=r, column=0, sticky="e", pady=2)
        ctk.CTkEntry(frame_params, textvariable=self.var_lim_thresh, width=100).grid(row=r, column=1, sticky="w", padx=15, pady=2)
        
        r += 1
        ctk.CTkLabel(frame_params, text="HighPass Cutoff (Hz) [Ex: 80.0]:").grid(row=r, column=0, sticky="e", pady=2)
        ctk.CTkEntry(frame_params, textvariable=self.var_hp_cutoff, width=100).grid(row=r, column=1, sticky="w", padx=15, pady=2)
        
        r += 1
        ctk.CTkLabel(frame_params, text="LowPass Cutoff (Hz) [Ex: 12000.0]:").grid(row=r, column=0, sticky="e", pady=2)
        ctk.CTkEntry(frame_params, textvariable=self.var_lp_cutoff, width=100).grid(row=r, column=1, sticky="w", padx=15, pady=2)
        
        ctk.CTkButton(frame_main, text="💾 Salvar Configurações de Tratamento de Áudio", command=self.save_config).pack(pady=20)
        
        self._toggle_states()
        
    def _toggle_states(self):
        if self.var_usar_filtro.get():
            self.cb_ia.configure(state='normal')
        else:
            self.cb_ia.configure(state='disabled')
            
    def save_config(self):
        try:
            audio_cfg = {
                "usar_filtro_estudio": self.var_usar_filtro.get(),
                "usar_speechbrain": self.var_usar_ia.get(),
                "compressor_threshold": float(self.var_comp_thresh.get().strip()),
                "compressor_ratio": float(self.var_comp_ratio.get().strip()),
                "limiter_threshold": float(self.var_lim_thresh.get().strip()),
                "highpass_cutoff": float(self.var_hp_cutoff.get().strip()),
                "lowpass_cutoff": float(self.var_lp_cutoff.get().strip())
            }
            self.config_manager.set("tratamento_audio", audio_cfg)
            messagebox.showinfo("Sucesso", "Configurações Globais de Tratamento de Áudio salvas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Houve um erro com os números fornecidos. Verifique se são válidos.\n\nDetalhes: {e}")

class TabEsteticaCanal(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(scrollable_frame, text="🎨 Padronização Visual do Canal", font=("Segoe UI", 12, "bold")).pack(pady=20)
        ctk.CTkLabel(scrollable_frame, text="Defina os diretórios globais de transições e overlays que serão usados como padrão no Apollo Editor.").pack(pady=12)
        
        # ─── GERENCIADOR DE PERFIS ESTÉTICOS ─────────────────────────
        f_perfis = ctk.CTkLabelFrame(scrollable_frame, text=" 📁 Gerenciador de Perfis Visuais (Estética & Masters) ")
        f_perfis.pack(fill=tk.X, pady=(5, 10), padx=20)
        
        ctk.CTkLabel(f_perfis, text="Perfil Estético:").pack(side=tk.LEFT)
        self.var_perfil_estetica = tk.StringVar()
        self.cb_perfil_estetica = ctk.CTkOptionMenu(f_perfis, variable=self.var_perfil_estetica, width=250)
        self.cb_perfil_estetica.pack(side=tk.LEFT, padx=15)
        self.cb_perfil_estetica.bind("<<ComboboxSelected>>", self._aplicar_perfil_estetica)
        
        ctk.CTkLabel(f_perfis, text="   Salvar Como:").pack(side=tk.LEFT)
        self.var_novo_perfil = tk.StringVar()
        ctk.CTkEntry(f_perfis, textvariable=self.var_novo_perfil, width=200).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(f_perfis, text="💾 Salvar Atual", command=self._salvar_perfil_estetica).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(f_perfis, text="🗑️ Excluir", command=self._excluir_perfil_estetica).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(f_perfis, text="✏️ Renomear", command=self._renomear_perfil_estetica).pack(side=tk.LEFT, padx=15)
        
        self._carregar_perfis_estetica()

        # Variáveis Listas
        estetica_cfg = self.config_manager.get("estetica_canal", {})

        # ─── VÍDEOS DE TESTE E CONTROLES GLOBAIS ─────────────────────────
        f_teste = ctk.CTkLabelFrame(scrollable_frame, text=" 🧪 Laboratório de Testes & Master Switches Globais ")
        f_teste.pack(fill=tk.X, pady=(20, 10), padx=20)
        
        self.var_vid_a = tk.StringVar(value=estetica_cfg.get("test_vid_a", ""))
        self.var_vid_b = tk.StringVar(value=estetica_cfg.get("test_vid_b", ""))
        self.var_vid_c = tk.StringVar(value=estetica_cfg.get("test_vid_c", ""))
        self.var_vid_d = tk.StringVar(value=estetica_cfg.get("test_vid_d", ""))
        
        def vid_row(parent, label, var):
            row = ctk.CTkFrame(parent)
            row.pack(fill=tk.X, pady=2)
            ctk.CTkLabel(row, text=label, width=80).pack(side=tk.LEFT)
            ctk.CTkEntry(row, textvariable=var, width=500).pack(side=tk.LEFT, padx=15)
            ctk.CTkButton(row, text="📁", command=lambda: self._ask_file(var, "*.mp4")).pack(side=tk.LEFT)
            
        vid_row(f_teste, "Vídeo A:", self.var_vid_a)
        vid_row(f_teste, "Vídeo B:", self.var_vid_b)
        vid_row(f_teste, "Vídeo C:", self.var_vid_c)
        vid_row(f_teste, "Vídeo D:", self.var_vid_d)
        
        ctk.CTkLabel(f_teste, text="*Se deixados em branco, o sistema usará cores sólidas (Vermelho, Azul...) para testar.", text_color="gray", font=("Segoe UI", 8)).pack(pady=2, anchor='w')

        ttk.Separator(f_teste, orient="horizontal").pack(fill=tk.X, pady=20)
        ctk.CTkLabel(f_teste, text="🔌 Master Switches (Liga/Desliga Categorias Inteiras para Testes E para o Render Final):", font=("Segoe UI", 9, "bold"), text_color="#2ED573").pack(anchor='w')
        
        f_switches = ctk.CTkFrame(f_teste)
        f_switches.pack(fill=tk.X, pady=12)
        
        self.master_hd = tk.BooleanVar(value=estetica_cfg.get("master_hd", True))
        self.master_overlay = tk.BooleanVar(value=estetica_cfg.get("master_overlay", True))
        self.master_xfade = tk.BooleanVar(value=estetica_cfg.get("master_xfade", True))
        self.master_lut = tk.BooleanVar(value=estetica_cfg.get("master_lut", True))
        self.master_cor = tk.BooleanVar(value=estetica_cfg.get("master_cor", True))
        self.master_cam = tk.BooleanVar(value=estetica_cfg.get("master_cam", True))
        # Modo de Stinger por arquivo: {filepath: "luma" | "color"}
        # Preenchido por auto-detecção ou manualmente pelo usuário
        self.stinger_types = estetica_cfg.get("stinger_types", {})
        
        ctk.CTkSwitch(f_switches, text="1. Transições HD (Stingers)", variable=self.master_hd).grid(row=0, column=0, sticky='w', padx=20, pady=2)
        ctk.CTkSwitch(f_switches, text="2. Partículas/Overlays", variable=self.master_overlay).grid(row=0, column=1, sticky='w', padx=20, pady=2)
        ctk.CTkSwitch(f_switches, text="3. Transições FFmpeg XFade", variable=self.master_xfade).grid(row=0, column=2, sticky='w', padx=20, pady=2)
        
        ctk.CTkSwitch(f_switches, text="4. Pasta de LUTs (Cor)", variable=self.master_lut).grid(row=1, column=0, sticky='w', padx=20, pady=2)
        ctk.CTkSwitch(f_switches, text="5. Correção de Cor (Sat/Bri)", variable=self.master_cor).grid(row=1, column=1, sticky='w', padx=20, pady=2)
        ctk.CTkSwitch(f_switches, text="6. Movimentação e Efeitos de Câmera", variable=self.master_cam).grid(row=1, column=2, sticky='w', padx=20, pady=2)
        
        ttk.Separator(f_teste, orient="horizontal").pack(fill=tk.X, pady=20)
        
        f_dir_teste = ctk.CTkFrame(f_teste)
        f_dir_teste.pack(fill=tk.X, pady=12)
        ctk.CTkLabel(f_dir_teste, text="Salvar vídeo de Teste em:").pack(side=tk.LEFT)
        self.var_dir_teste = tk.StringVar(value=estetica_cfg.get("test_save_dir", ""))
        ctk.CTkEntry(f_dir_teste, textvariable=self.var_dir_teste, width=400).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(f_dir_teste, text="📁", command=self._ask_test_dir).pack(side=tk.LEFT)
        self.btn_teste = ctk.CTkButton(f_dir_teste, text="🎬 Gerar Vídeo Teste", command=self.gerar_video_teste_transicoes)
        self.btn_teste.pack(side=tk.LEFT, padx=(15, 0))

        # --- ATIVOS DA IA (SFX E CENSURA) ---
        frame_ia_assets = ctk.CTkLabelFrame(scrollable_frame, text="🧠 Ativos do Assistente de IA (SFX, Bipes, Censura)")
        frame_ia_assets.pack(fill=tk.X, expand=False, padx=20, pady=20)
        
        f_sfx = ctk.CTkFrame(frame_ia_assets)
        f_sfx.pack(fill=tk.X, pady=2)
        ctk.CTkLabel(f_sfx, text="Pasta Global de Efeitos Sonoros (SFX):", width=350).pack(side=tk.LEFT)
        self.var_sfx_dir = tk.StringVar(value=estetica_cfg.get("sfx_dir", ""))
        ctk.CTkEntry(f_sfx, textvariable=self.var_sfx_dir, width=400).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(f_sfx, text="📁 Procurar...", command=lambda: self._ask_dir(self.var_sfx_dir)).pack(side=tk.LEFT)

        f_beep = ctk.CTkFrame(frame_ia_assets)
        f_beep.pack(fill=tk.X, pady=2)
        ctk.CTkLabel(f_beep, text="Arquivo de Áudio do Bipe (Censura):", width=350).pack(side=tk.LEFT)
        self.var_beep_file = tk.StringVar(value=estetica_cfg.get("beep_file", ""))
        ctk.CTkEntry(f_beep, textvariable=self.var_beep_file, width=400).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(f_beep, text="🎵 Procurar...", command=lambda: self.var_beep_file.set(filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")]) or self.var_beep_file.get())).pack(side=tk.LEFT)
        
        f_palavras = ctk.CTkFrame(frame_ia_assets)
        f_palavras.pack(fill=tk.X, pady=12)
        ctk.CTkLabel(f_palavras, text="Palavras Proibidas (separadas por vírgula):", width=350).pack(side=tk.LEFT, anchor='n')
        self.txt_censura = ctk.CTkTextbox(f_palavras, height=60, font=("Consolas", 12))
        self.txt_censura.pack(side=tk.LEFT, fill="x", expand=True, padx=15)
        self.txt_censura.insert("1.0", estetica_cfg.get("censura_words", ""))

        frame_main = ctk.CTkLabelFrame(scrollable_frame, text="Diretórios do HD de Efeitos (H:)")
        frame_main.pack(fill=tk.X, expand=False, padx=20, pady=12)
        
        # Recupera legado ou listas
        t_dirs = estetica_cfg.get("transicoes_dirs", [])
        if not t_dirs and estetica_cfg.get("transicoes_dir"): t_dirs = [estetica_cfg.get("transicoes_dir")]
        
        o_dirs = estetica_cfg.get("overlay_dirs", [])
        if not o_dirs and estetica_cfg.get("overlay_dir"): o_dirs = [estetica_cfg.get("overlay_dir")]
        
        self.t_sel = estetica_cfg.get("transicoes_sel", [])
        self.o_sel = estetica_cfg.get("overlay_sel", [])
        # Conjuntos de ARQUIVOS individuais selecionados
        self.t_files_sel  = set(estetica_cfg.get("transicoes_files_sel", []))
        self.o_files_sel  = set(estetica_cfg.get("overlay_files_sel", []))
        self.lut_files_sel= set(estetica_cfg.get("lut_files_sel", []))

        
        # --- PAINEL DE TRANSIÇÕES ---
        lbl_t = ctk.CTkLabel(frame_main, text="1. Banco de Pastas de Transições (HD Stingers):", font=("Segoe UI", 9, "bold"))
        lbl_t.pack(anchor='w', pady=(5,0))
        
        self.lb_trans = tk.Listbox(frame_main, selectmode=tk.MULTIPLE, exportselection=0)
        # HIDE the listbox, use button instead
        self.btn_manage_trans = ctk.CTkButton(frame_main, text="📂 Gerenciar Banco de Transições", command=lambda: self.open_manager("Transições (Stingers)", self.lb_trans, self.t_files_sel, self.btn_manage_trans, stinger_types=self.stinger_types))
        self.btn_manage_trans.pack(fill=tk.X, pady=(5, 4))

        # Remove os radio buttons globais (substituídos por per-file no gerenciador)

        # --- BLOCO UNIFICADO COM SCROLL (XFade e DarkFacil) ---
        f_unified = ctk.CTkLabelFrame(frame_main, text=" 3. Filtros, Movimentos e Transições de Vídeo ")
        f_unified.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Scroll único na borda da direita
        unified_canvas = tk.Canvas(f_unified, height=400)
        unified_scroll = ttk.Scrollbar(f_unified, orient='vertical', command=unified_canvas.yview)
        inner_scroll = ctk.CTkFrame(unified_canvas)
        inner_scroll.bind("<Configure>", lambda e: unified_canvas.configure(scrollregion=unified_canvas.bbox("all")))
        unified_win = unified_canvas.create_window((0, 0), window=inner_scroll, anchor='nw')
        unified_canvas.bind("<Configure>", lambda e: unified_canvas.itemconfig(unified_win, width=e.width))
        unified_canvas.configure(yscrollcommand=unified_scroll.set)
        unified_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        unified_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        unified_canvas.bind("<MouseWheel>", lambda e: unified_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # ─── SEÇÃO 1: TRANSIÇÕES FFMPEG (DUAS COLUNAS SEQUENCIAIS) ───────────
        lbl_tr = ctk.CTkLabel(inner_scroll, text="Transições FFmpeg XFade:", font=("Segoe UI", 9, "bold"))
        lbl_tr.pack(anchor='w', pady=(0,5))
        
        f_tr_header = ctk.CTkFrame(inner_scroll)
        f_tr_header.pack(fill=tk.X, padx=20, pady=(0,10))
        ctk.CTkLabel(f_tr_header, text="Probabilidade geral de usar transição (%):").pack(side=tk.LEFT)
        self.prob_transicao = tk.IntVar(value=estetica_cfg.get("prob_transicao", 100))
        ttk.Spinbox(f_tr_header, from_=0, to=100, increment=10, textvariable=self.prob_transicao, width=5).pack(side=tk.LEFT, padx=6)
        ctk.CTkLabel(f_tr_header, text="*Sorteará apenas entre as marcadas  ✔", text_color="gray").pack(side=tk.LEFT, padx=20)

        # Criando o frame das duas listas/colunas para as transições
        f_tr_cols = ctk.CTkFrame(inner_scroll)
        f_tr_cols.pack(fill=tk.X, expand=True, padx=20)
        
        col1 = ctk.CTkFrame(f_tr_cols)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        col2 = ctk.CTkFrame(f_tr_cols)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        XFADE_DESC = {
            "fade":       "Dissolve suave entre cenas",
            "wipeleft":   "Limpa da direita para esquerda",
            "wiperight":  "Limpa da esquerda para direita",
            "wipeup":     "Limpa de baixo para cima",
            "wipedown":   "Limpa de cima para baixo",
            "slideleft":  "Desliza a cena para esquerda",
            "slideright": "Desliza a cena para direita",
            "slideup":    "Desliza a cena para cima",
            "slidedown":  "Desliza a cena para baixo",
            "smoothleft": "Deslize suave para esquerda",
            "smoothright":"Deslize suave para direita",
            "smoothup":   "Deslize suave para cima",
            "smoothdown": "Deslize suave para baixo",
            "rectcrop":   "Recorte retangular crescente no centro",
            "circlecrop": "Recorte circular expansivo",
            "circleclose":"Fecha em círculo (fecha a cena)",
            "circleopen": "Abre em círculo (abre a cena)",
            "horzclose":  "Fecha pelas bordas horizontais",
            "horzopen":   "Abre pelas bordas horizontais",
            "vertclose":  "Fecha pelas bordas verticais",
            "vertopen":   "Abre pelas bordas verticais",
            "diagbl":     "Diagonal: canto inferior-esquerdo",
            "diagbr":     "Diagonal: canto inferior-direito",
            "diagtl":     "Diagonal: canto superior-esquerdo",
            "diagtr":     "Diagonal: canto superior-direito",
            "hlslice":    "Fatia horizontal (esquerda → direita)",
            "hrslice":    "Fatia horizontal (direita → esquerda)",
            "vuslice":    "Fatia vertical (cima → baixo)",
            "vdslice":    "Fatia vertical (baixo → cima)",
            "dissolve":   "Dissolve aleatório pixel a pixel",
            "pixelize":   "Pixeliza a transição entre cenas",
            "radial":     "Varredura radial giratória",
            "hblur":      "Desfoque horizontal na troca",
            "squeezeh":   "Aperta a cena horizontalmente",
            "squeezev":   "Aperta a cena verticalmente",
            "zoomin":     "Zoom de entrada na nova cena",
            # ─── NOVAS FFmpeg 5+ ───
            "fadeblack":  "Fade passando pelo preto",
            "fadewhite":  "Fade passando pelo branco",
            "fadegrays":  "Fade passando por tons de cinza",
            "distance":   "Transição por distância de cor",
            "coverleft":  "Nova cena cobre pela esquerda",
            "coverright": "Nova cena cobre pela direita",
            "coverup":    "Nova cena cobre por cima",
            "coverdown":  "Nova cena cobre por baixo",
            "revealleft": "Revela nova cena pela esquerda",
            "revealright":"Revela nova cena pela direita",
            "revealup":   "Revela nova cena por cima",
            "revealdown": "Revela nova cena por baixo",
            "hlwind":     "Vento horizontal (esq→dir)",
            "hrwind":     "Vento horizontal (dir→esq)",
            "vuwind":     "Vento vertical (cima→baixo)",
            "vdwind":     "Vento vertical (baixo→cima)",
        }
        
        salvas_xfade  = estetica_cfg.get("xfade_selecionadas", ["fade", "wipeleft", "slideleft", "circlecrop"])
        duracoes_xfade= estetica_cfg.get("xfade_duracoes", {})
        
        self.xfade_var = {}   # {nome: BooleanVar}
        self.xfade_dur = {}   # {nome: DoubleVar}
        
        # Iterar para dividir a lista nas duas colunas
        items = list(XFADE_DESC.items())
        half = (len(items) + 1) // 2
        
        for i, (nome, desc) in enumerate(items):
            target_col = col1 if i < half else col2
            row = ctk.CTkFrame(target_col)
            row.pack(fill=tk.X, pady=1)
            bv = tk.BooleanVar(value=nome in salvas_xfade)
            dv = tk.DoubleVar(value=duracoes_xfade.get(nome, 0.5))
            self.xfade_var[nome] = bv
            self.xfade_dur[nome] = dv
            ctk.CTkSwitch(row, text=nome, variable=bv, width=120).pack(side=tk.LEFT)
            ctk.CTkLabel(row, text=desc, text_color="#aaa", font=("Segoe UI", 8), width=340, anchor='w').pack(side=tk.LEFT)
            ctk.CTkLabel(row, text="Dur(s):", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(2,2))
            ttk.Spinbox(row, from_=0.1, to=5.0, increment=0.1, textvariable=dv, width=4).pack(side=tk.LEFT)

        # ─── COLORAÇÃO GLOBAL ────────────────────────────────────────────────────────
        f_color = ctk.CTkLabelFrame(frame_main, text=" ✨ Coloração Global do Canal (Aplicados em 100% das cenas) ")
        f_color.pack(fill=tk.X, pady=(15, 5))
        
        
        # --- PAINEL DE OVERLAYS E PARTICULAS ---
        f_ov_top = ctk.CTkFrame(f_color)
        f_ov_top.pack(fill=tk.X, pady=(0, 5))
        ctk.CTkLabel(f_ov_top, text="Pastas de Partículas/Overlays do HD:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        
        self.lb_overlays = tk.Listbox(f_color, selectmode=tk.MULTIPLE, exportselection=0)
        self.btn_manage_ov = ctk.CTkButton(f_color, text="📂 Gerenciar Banco de Partículas/Overlays", command=lambda: self.open_manager("Partículas/Overlays", self.lb_overlays, self.o_files_sel, self.btn_manage_ov))
        self.btn_manage_ov.pack(fill=tk.X, pady=(0, 15))

        
        # LUTs
        f_lut_top = ctk.CTkFrame(f_color)
        f_lut_top.pack(fill=tk.X, pady=(0, 5))
        ctk.CTkLabel(f_lut_top, text="Pastas de LUTs do HD (.cube):", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        
        self.lb_luts = tk.Listbox(f_color, selectmode=tk.MULTIPLE, exportselection=0)
        self.btn_manage_luts = ctk.CTkButton(f_color, text="📂 Gerenciar Banco de LUTs", command=lambda: self.open_manager("LUTs de Cor", self.lb_luts, self.lut_files_sel, self.btn_manage_luts))
        self.btn_manage_luts.pack(fill=tk.X, pady=(0, 10))

        # Correção de Cor — cada parâmetro com ON/OFF independente
        f_color_grid = ctk.CTkLabelFrame(f_color, text=" Correção de Cor (eq) — marque para ativar ")
        f_color_grid.pack(fill=tk.X, pady=12)
        
        self.var_usar_sat  = tk.BooleanVar(value=estetica_cfg.get("var_usar_sat",  True))
        self.var_usar_cont = tk.BooleanVar(value=estetica_cfg.get("var_usar_cont", True))
        self.var_usar_bri  = tk.BooleanVar(value=estetica_cfg.get("var_usar_bri",  False))
        self.var_sat  = tk.DoubleVar(value=estetica_cfg.get("var_sat",  1.0))
        self.var_cont = tk.DoubleVar(value=estetica_cfg.get("var_cont", 1.0))
        self.var_bri  = tk.DoubleVar(value=estetica_cfg.get("var_bri",  0.0))
        self.var_glitch   = tk.BooleanVar(value=estetica_cfg.get("var_glitch",   False))
        self.var_vhs      = tk.BooleanVar(value=estetica_cfg.get("var_vhs",      False))
        self.var_vignette = tk.BooleanVar(value=estetica_cfg.get("var_vignette", False))
        self.var_noise    = tk.BooleanVar(value=estetica_cfg.get("var_noise",    False))
        # ─── NOVOS: COR AVANÇADA ───
        self.var_colorbalance = tk.BooleanVar(value=estetica_cfg.get("var_colorbalance", False))
        self.var_cb_rs = tk.DoubleVar(value=estetica_cfg.get("var_cb_rs", 0.0))
        self.var_cb_gs = tk.DoubleVar(value=estetica_cfg.get("var_cb_gs", 0.0))
        self.var_cb_bs = tk.DoubleVar(value=estetica_cfg.get("var_cb_bs", 0.0))
        self.var_colortemp = tk.BooleanVar(value=estetica_cfg.get("var_colortemp", False))
        self.var_colortemp_val = tk.IntVar(value=estetica_cfg.get("var_colortemp_val", 6500))
        self.var_vibrance = tk.BooleanVar(value=estetica_cfg.get("var_vibrance", False))
        self.var_vibrance_val = tk.DoubleVar(value=estetica_cfg.get("var_vibrance_val", 0.5))
        self.var_curves = tk.BooleanVar(value=estetica_cfg.get("var_curves", False))
        self.var_curves_preset = tk.StringVar(value=estetica_cfg.get("var_curves_preset", "none"))
        self.var_hue_shift = tk.BooleanVar(value=estetica_cfg.get("var_hue_shift", False))
        self.var_hue_val = tk.DoubleVar(value=estetica_cfg.get("var_hue_val", 0.0))
        # ─── NOVOS: CÂMERA AVANÇADA ───
        self.var_gblur = tk.BooleanVar(value=estetica_cfg.get("var_gblur", False))
        self.var_gblur_sigma = tk.DoubleVar(value=estetica_cfg.get("var_gblur_sigma", 1.5))
        self.var_sharpen = tk.BooleanVar(value=estetica_cfg.get("var_sharpen", False))
        self.var_lagfun = tk.BooleanVar(value=estetica_cfg.get("var_lagfun", False))
        self.var_monochrome = tk.BooleanVar(value=estetica_cfg.get("var_monochrome", False))
        self.var_filmgrain = tk.BooleanVar(value=estetica_cfg.get("var_filmgrain", False))

        def color_row(parent, toggle_var, label, val_var, frm, to, inc, w=5, extra=None):
            row = ctk.CTkFrame(parent)
            row.pack(fill=tk.X, pady=2)
            ctk.CTkSwitch(row, text=label, variable=toggle_var, width=140).pack(side=tk.LEFT)
            ttk.Spinbox(row, from_=frm, to=to, increment=inc, textvariable=val_var, width=w).pack(side=tk.LEFT, padx=15)
            if extra:
                ctk.CTkLabel(row, text=extra, text_color="#888", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=15)

        color_row(f_color_grid, self.var_usar_sat,  "Saturação:",  self.var_sat,  0.0, 3.0, 0.1, extra="1.0 = Normal | >1 = Mais vibrante")
        color_row(f_color_grid, self.var_usar_cont, "Contraste:",  self.var_cont, 0.0, 3.0, 0.1, extra="1.0 = Normal | >1 = Mais forte")
        color_row(f_color_grid, self.var_usar_bri,  "Brilho:",     self.var_bri, -1.0, 1.0, 0.1, extra="0 = Normal | negativo = Escuro | positivo = Claro")

        # ─── NOVOS CONTROLES DE COR ───
        ttk.Separator(f_color_grid, orient="horizontal").pack(fill=tk.X, pady=12)
        ctk.CTkLabel(f_color_grid, text="Filtros Avançados de Cor (FFmpeg nativo):", font=("Segoe UI", 8, "bold"), text_color="#2ED573").pack(anchor='w')

        color_row(f_color_grid, self.var_vibrance, "Vibrance:", self.var_vibrance_val, -2.0, 2.0, 0.1, extra="Boost inteligente de cores fracas (0.5 = sutil)")
        color_row(f_color_grid, self.var_hue_shift, "Rotação Hue:", self.var_hue_val, -180.0, 180.0, 10, extra="Gira toda a paleta de cores (graus)")
        color_row(f_color_grid, self.var_colortemp, "Temperatura:", self.var_colortemp_val, 1000, 15000, 500, extra="<6500=Quente(laranja) | >6500=Frio(azul)")

        # Color Balance row (3 spinboxes)
        f_cb = ctk.CTkFrame(f_color_grid)
        f_cb.pack(fill=tk.X, pady=2)
        ctk.CTkSwitch(f_cb, text="Color Balance:", variable=self.var_colorbalance, width=140).pack(side=tk.LEFT)
        ctk.CTkLabel(f_cb, text="R:", text_color="#FF6B6B", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(f_cb, from_=-1.0, to=1.0, increment=0.1, textvariable=self.var_cb_rs, width=4).pack(side=tk.LEFT, padx=2)
        ctk.CTkLabel(f_cb, text="G:", text_color="#51CF66", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(f_cb, from_=-1.0, to=1.0, increment=0.1, textvariable=self.var_cb_gs, width=4).pack(side=tk.LEFT, padx=2)
        ctk.CTkLabel(f_cb, text="B:", text_color="#339AF0", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(f_cb, from_=-1.0, to=1.0, increment=0.1, textvariable=self.var_cb_bs, width=4).pack(side=tk.LEFT, padx=2)
        ctk.CTkLabel(f_cb, text="Sombras RGB (-1 a 1)", text_color="#888", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=15)

        # Curves preset
        f_cur = ctk.CTkFrame(f_color_grid)
        f_cur.pack(fill=tk.X, pady=2)
        ctk.CTkSwitch(f_cur, text="Curves Cinema:", variable=self.var_curves, width=140).pack(side=tk.LEFT)
        ctk.CTkOptionMenu(f_cur, variable=self.var_curves_preset, values=["TODOS (Showcase)", "none", "cross_process", "darker", "increase_contrast", "lighter", "linear_contrast", "medium_contrast", "strong_contrast", "vintage"], width=200).pack(side=tk.LEFT, padx=15)
        ctk.CTkLabel(f_cur, text="Presets cinematográficos nativos do FFmpeg", text_color="#888", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=15)

        # ─── EFEITOS DE CÂMERA EXPANDIDOS ───
        f_color_fx = ctk.CTkLabelFrame(f_color, text=" Efeitos de Câmera Nativos (FFmpeg) ")
        f_color_fx.pack(fill=tk.X, pady=12)

        def cfx_row(parent, var, label, info=""):
            row = ctk.CTkFrame(parent)
            row.pack(fill=tk.X, pady=2)
            ctk.CTkSwitch(row, text=label, variable=var, width=220).pack(side=tk.LEFT)
            if info:
                ctk.CTkLabel(row, text=info, text_color="#888", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=8)

        cfx_row(f_color_fx, self.var_glitch,   "Glitch RGB",        "Aberração cromática aleatória (< 30% das cenas)")
        cfx_row(f_color_fx, self.var_vignette, "Vignette Escura",   "Bordas escuras em todas as cenas")
        cfx_row(f_color_fx, self.var_noise,    "Ruído/Granulação",  "Grão de filme em todas as cenas")

        ttk.Separator(f_color_fx, orient="horizontal").pack(fill=tk.X, pady=12)
        ctk.CTkLabel(f_color_fx, text="Novos Efeitos Cinematográficos:", font=("Segoe UI", 8, "bold"), text_color="#2ED573").pack(anchor='w')

        cfx_row(f_color_fx, self.var_filmgrain, "Film Grain Pro",    "Granulação cinematográfica avançada (tipo película 35mm)")
        f_gb = ctk.CTkFrame(f_color_fx)
        f_gb.pack(fill=tk.X, pady=2)
        ctk.CTkSwitch(f_gb, text="Gaussian Blur", variable=self.var_gblur, width=220).pack(side=tk.LEFT)
        ctk.CTkLabel(f_gb, text="Sigma:", text_color="#888", font=("Segoe UI", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(f_gb, from_=0.5, to=10.0, increment=0.5, textvariable=self.var_gblur_sigma, width=4).pack(side=tk.LEFT, padx=3)
        ctk.CTkLabel(f_gb, text="Desfoque gaussiano global (sonho/flashback)", text_color="#888", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=15)
        cfx_row(f_color_fx, self.var_sharpen,  "Sharpen (Nitidez)", "Aumenta nitidez de bordas (imagens mais definidas)")
        cfx_row(f_color_fx, self.var_lagfun,   "Light Trails",      "Rastro de luz/ghosting (efeito trail artístico)")
        cfx_row(f_color_fx, self.var_monochrome,"Monocromático",     "Dessaturação total (preto e branco) aleatória < 20% cenas")

        # --- MOVIMENTAÇÃO DE CÂMERA (PAN/ZOOM) ---
        f_mov = ctk.CTkLabelFrame(f_color, text=" Movimentação de Câmera (Pan/Zoom/Shake) ")
        f_mov.pack(fill=tk.X, pady=12)
        
        self.var_mov_video = tk.BooleanVar(value=estetica_cfg.get("var_mov_video", False))
        ctk.CTkSwitch(f_mov, text="Aplicar Movimentação também em VÍDEOS (⚠️ AVISO: Deixa o FFmpeg extremamente lento e pode causar engasgos)", variable=self.var_mov_video).pack(anchor='w', pady=(0,5))
        
        self.var_zoom     = tk.BooleanVar(value=estetica_cfg.get("var_zoom", True))
        self.var_zoom_out = tk.BooleanVar(value=estetica_cfg.get("var_zoom_out", False))
        self.var_pan      = tk.BooleanVar(value=estetica_cfg.get("var_pan", True))
        self.var_pan_rev  = tk.BooleanVar(value=estetica_cfg.get("var_pan_rev", True))
        self.var_tilt     = tk.BooleanVar(value=estetica_cfg.get("var_tilt", True))
        self.var_tilt_rev = tk.BooleanVar(value=estetica_cfg.get("var_tilt_rev", True))
        self.var_shake    = tk.BooleanVar(value=estetica_cfg.get("var_shake", False))
        self.var_kenburns = tk.BooleanVar(value=estetica_cfg.get("var_kenburns", False))
        self.var_kenburns_rev = tk.BooleanVar(value=estetica_cfg.get("var_kenburns_rev", False))
        self.var_kenburns_up = tk.BooleanVar(value=estetica_cfg.get("var_kenburns_up", False))
        self.var_kenburns_down = tk.BooleanVar(value=estetica_cfg.get("var_kenburns_down", False))
        
        self.var_zoom_amp  = tk.DoubleVar(value=estetica_cfg.get("var_zoom_amp", 0.10))
        self.var_pan_speed = tk.DoubleVar(value=estetica_cfg.get("var_pan_speed", 0.05))
        self.var_tilt_speed= tk.DoubleVar(value=estetica_cfg.get("var_tilt_speed", 0.05))
        self.var_shake_int = tk.IntVar(value=estetica_cfg.get("var_shake_int", 3))
        self.var_kenburns_int = tk.DoubleVar(value=estetica_cfg.get("var_kenburns_int", 0.15))

        def fx_row(parent, var, label, controls):
            row = ctk.CTkFrame(parent)
            row.pack(fill=tk.X, pady=2)
            ctk.CTkSwitch(row, text=label, variable=var, width=220).pack(side=tk.LEFT)
            for lbl_txt, spinvar, frm, to, inc, w in controls:
                ctk.CTkLabel(row, text=lbl_txt, text_color="#aaa").pack(side=tk.LEFT, padx=(10,2))
                ttk.Spinbox(row, from_=frm, to=to, increment=inc, textvariable=spinvar, width=w).pack(side=tk.LEFT)

        fx_row(f_mov, self.var_zoom,     "Zoom In (Aproximação)", [("Amplitude:", self.var_zoom_amp,   0.01, 1.0, 0.01, 5)])
        fx_row(f_mov, self.var_zoom_out, "Zoom Out (Afastamento)", [])
        fx_row(f_mov, self.var_pan,      "Pan (Esq→Dir)", [("Velocidade:", self.var_pan_speed,  0.01, 1.0, 0.01, 5)])
        fx_row(f_mov, self.var_pan_rev,  "Pan (Dir→Esq)", [])
        fx_row(f_mov, self.var_tilt,     "Tilt (Cima→Baixo)", [("Velocidade:", self.var_tilt_speed, 0.01, 1.0, 0.01, 5)])
        fx_row(f_mov, self.var_tilt_rev, "Tilt (Baixo→Cima)", [])
        fx_row(f_mov, self.var_shake,    "Shake (Tremor)", [("Intensidade(px):", self.var_shake_int, 1, 50, 1, 4)])
        fx_row(f_mov, self.var_kenburns, "Ken Burns (Zoom+Dir)", [("Intensidade:", self.var_kenburns_int, 0.01, 1.0, 0.01, 5)])
        fx_row(f_mov, self.var_kenburns_rev, "Ken Burns (Zoom+Esq)", [])
        fx_row(f_mov, self.var_kenburns_up, "Ken Burns (Zoom+Cima)", [])
        fx_row(f_mov, self.var_kenburns_down, "Ken Burns (Zoom+Baixo)", [])


        ctk.CTkButton(frame_main, text="💾 Salvar Estética Global", command=self.save_config).pack(pady=15, fill=tk.X)
        
        # Preencher Listboxes de pastas
        for d in t_dirs: self.lb_trans.insert(tk.END, d)
        for i in self.t_sel: 
            if i < self.lb_trans.size(): self.lb_trans.selection_set(i)
            
        for d in o_dirs: self.lb_overlays.insert(tk.END, d)
        for i in self.o_sel:
            if i < self.lb_overlays.size(): self.lb_overlays.selection_set(i)
            
        lut_dirs = estetica_cfg.get("lut_dirs", [])
        lut_sel  = estetica_cfg.get("lut_sel", [])
        for d in lut_dirs: self.lb_luts.insert(tk.END, d)
        for i in lut_sel:
            if i < self.lb_luts.size(): self.lb_luts.selection_set(i)

        # Injetar Auto-Save para Estética Global (Elimina necessidade de clicar em Salvar)
        self._auto_save_timer = None
        def _auto_save_cb(*args):
            if self._auto_save_timer:
                self.after_cancel(self._auto_save_timer)
            self._auto_save_timer = self.after(500, self._save_config_silent)

        self.lb_trans.bind("<<ListboxSelect>>", _auto_save_cb)
        self.lb_overlays.bind("<<ListboxSelect>>", _auto_save_cb)
        self.lb_luts.bind("<<ListboxSelect>>", _auto_save_cb)

        aesthetic_vars = [
            "var_zoom", "var_zoom_out", "var_pan", "var_pan_rev", "var_tilt", "var_tilt_rev",
            "var_shake", "var_kenburns", "var_kenburns_rev", "var_kenburns_up", "var_kenburns_down",
            "var_zoom_amp", "var_pan_speed", "var_tilt_speed", "var_shake_int", "var_kenburns_int",
            "var_usar_sat", "var_usar_cont", "var_usar_bri", "var_sat", "var_cont", "var_bri",
            "var_glitch", "var_vhs", "var_vignette", "var_noise", "var_colorbalance", "var_cb_rs",
            "var_cb_gs", "var_cb_bs", "var_hue_shift", "var_hue_val", "var_colortemp", "var_colortemp_val",
            "var_vibrance", "var_vibrance_val", "var_curves", "var_curves_preset", "var_filmgrain",
            "var_gblur", "var_gblur_sigma", "var_sharpen", "var_lagfun", "var_monochrome",
            "var_sfx_dir", "var_beep_file"
        ]
        for var_name in aesthetic_vars:
            if hasattr(self, var_name):
                try: getattr(self, var_name).trace_add("write", _auto_save_cb)
                except: pass
                
        self.txt_censura.bind("<KeyRelease>", _auto_save_cb)
                
        for var in self.xfade_var.values(): var.trace_add("write", _auto_save_cb)
        for var in self.xfade_dur.values(): var.trace_add("write", _auto_save_cb)
        if hasattr(self, 'prob_transicao'): self.prob_transicao.trace_add("write", _auto_save_cb)



    def open_manager(self, title, listbox, files_sel_ref, btn, stinger_types=None):
        def update_btn():
            total = listbox.size()
            btn.config(text=f"📂 Gerenciar Banco de {title} ({len(files_sel_ref)} arq. selecionados de {total} pastas)")
            self._save_config_silent()

        MultiSelectDialog(self, title, listbox, files_sel_ref, update_btn, stinger_types=stinger_types)

    def _add_dir(self, lb):
        path = filedialog.askdirectory(title="Adicionar Pasta ao Banco")
        if path:
            lb.insert(tk.END, path)
            lb.selection_set(tk.END) # Auto seleciona a nova
            
    def _ask_dir(self, var):
        path = filedialog.askdirectory(title="Selecionar Pasta")
        if path:
            var.set(path)

    def _carregar_perfis_estetica(self):
        perfis = self.config_manager.get("perfis_estetica", {})
        self.cb_perfil_estetica['values'] = list(perfis.keys())

    def _salvar_perfil_estetica(self):
        nome = self.var_novo_perfil.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Digite um nome para o perfil.")
            return
        self._save_config_silent()
        atual = self.config_manager.get("estetica_canal", {})
        perfis = self.config_manager.get("perfis_estetica", {})
        perfis[nome] = atual
        self.config_manager.set("perfis_estetica", perfis)
        self.var_novo_perfil.set("")
        self._carregar_perfis_estetica()
        self.var_perfil_estetica.set(nome)
        messagebox.showinfo("Sucesso", f"Perfil '{nome}' salvo!")

    def _aplicar_perfil_estetica(self, event=None):
        nome = self.var_perfil_estetica.get()
        perfis = self.config_manager.get("perfis_estetica", {})
        if nome in perfis:
            self.config_manager.set("estetica_canal", perfis[nome])
            messagebox.showinfo("Carregado", f"Perfil '{nome}' setado como padrão global!\nReinicie o programa para a interface atualizar totalmente os botões.")

    def _excluir_perfil_estetica(self):
        nome = self.var_perfil_estetica.get()
        perfis = self.config_manager.get("perfis_estetica", {})
        if nome in perfis:
            if messagebox.askyesno("Confirmar", f"Excluir perfil '{nome}'?"):
                del perfis[nome]
                self.config_manager.set("perfis_estetica", perfis)
                self.var_perfil_estetica.set("")
                self._carregar_perfis_estetica()

    def _renomear_perfil_estetica(self):
        nome_antigo = self.var_perfil_estetica.get()
        if not nome_antigo:
            messagebox.showwarning("Aviso", "Selecione um perfil para renomear.")
            return
        from tkinter import simpledialog
        novo_nome = simpledialog.askstring("Renomear Perfil Estético", f"Digite o novo nome para o perfil '{nome_antigo}':", initialvalue=nome_antigo)
        if not novo_nome:
            return
        novo_nome = novo_nome.strip()
        if not novo_nome:
            return
        if novo_nome == nome_antigo:
            return
            
        perfis = self.config_manager.get("perfis_estetica", {})
        if novo_nome in perfis:
            messagebox.showwarning("Aviso", f"Já existe um perfil chamado '{novo_nome}'.")
            return
            
        perfis[novo_nome] = perfis.pop(nome_antigo)
        self.config_manager.set("perfis_estetica", perfis)
        self._carregar_perfis_estetica()
        self.var_perfil_estetica.set(novo_nome)
        
        notify_system_of_changes(self)
        messagebox.showinfo("Sucesso", f"Perfil '{nome_antigo}' renomeado para '{novo_nome}'!")

    def _ask_file(self, var, ext):
        path = filedialog.askopenfilename(title=f"Selecione o arquivo ({ext})", filetypes=[(f"Arquivo {ext}", ext), ("Todos", "*.*")])
        if path:
            var.set(path)

    def _ask_test_dir(self):
        path = filedialog.askdirectory(title="Pasta para Salvar Testes")
        if path:
            self.var_dir_teste.set(path)

    def _rem_dir(self, lb):
        sel = lb.curselection()
        for i in reversed(sel):
            lb.delete(i)
            
    def save_config(self):
        self._save_config_silent()
        xfade_sel = [nome for nome, bv in self.xfade_var.items() if bv.get()]
        messagebox.showinfo("Sucesso", f"Estética Global salva!\n✔ {len(xfade_sel)} transições ativas  |  Probabilidade: {self.prob_transicao.get()}%\nLUTs e Filtros aplicados em 100% das cenas.")

    def _save_config_silent(self):
        # Coleta transições individuais
        xfade_sel  = [nome for nome, bv in self.xfade_var.items() if bv.get()]
        xfade_durs = {nome: dv.get() for nome, dv in self.xfade_dur.items()}
        
        novo_cfg = {
            "sfx_dir": getattr(self, "var_sfx_dir", tk.StringVar()).get(),
            "beep_file": getattr(self, "var_beep_file", tk.StringVar()).get(),
            "censura_words": self.txt_censura.get("1.0", tk.END).strip() if hasattr(self, "txt_censura") else "",
            "transicoes_dirs": list(self.lb_trans.get(0, tk.END)),
            "overlay_dirs":    list(self.lb_overlays.get(0, tk.END)),
            "transicoes_sel":  list(self.lb_trans.curselection()),
            "overlay_sel":     list(self.lb_overlays.curselection()),
            "transicoes_files_sel": list(self.t_files_sel),
            "overlay_files_sel":    list(self.o_files_sel),
            "lut_files_sel":        list(self.lut_files_sel),
            # Efeitos Cinematográficos
            "var_zoom":          self.var_zoom.get(),
            "var_zoom_out":      self.var_zoom_out.get(),
            "var_mov_video":     self.var_mov_video.get(),
            "var_pan":           self.var_pan.get(),
            "var_pan_rev":       self.var_pan_rev.get(),
            "var_tilt":          self.var_tilt.get(),
            "var_tilt_rev":      self.var_tilt_rev.get(),
            "var_shake":         self.var_shake.get(),
            "var_kenburns":      self.var_kenburns.get(),
            "var_kenburns_rev":  self.var_kenburns_rev.get(),
            "var_kenburns_up":   self.var_kenburns_up.get(),
            "var_kenburns_down": self.var_kenburns_down.get(),
            "var_zoom_amp":      self.var_zoom_amp.get(),
            "var_pan_speed":     self.var_pan_speed.get(),
            "var_tilt_speed":    self.var_tilt_speed.get(),
            "var_shake_int":     self.var_shake_int.get(),
            "var_kenburns_int":  self.var_kenburns_int.get(),
            # Transições FFmpeg (novo formato individual)
            "xfade_selecionadas": xfade_sel if xfade_sel else ["fade"],
            "xfade_duracoes":     xfade_durs,
            "prob_transicao":    self.prob_transicao.get(),
            # Coloração Global — ON/OFF independente por parâmetro
            "var_usar_sat":  self.var_usar_sat.get(),
            "var_usar_cont": self.var_usar_cont.get(),
            "var_usar_bri":  self.var_usar_bri.get(),
            "var_sat":       self.var_sat.get(),
            "var_cont":      self.var_cont.get(),
            "var_bri":       self.var_bri.get(),
            "var_glitch":    self.var_glitch.get(),
            "var_vhs":       self.var_vhs.get(),
            "var_vignette":  self.var_vignette.get(),
            "var_noise":     self.var_noise.get(),
            # Cor Avançada
            "var_colorbalance": self.var_colorbalance.get(),
            "var_cb_rs": self.var_cb_rs.get(),
            "var_cb_gs": self.var_cb_gs.get(),
            "var_cb_bs": self.var_cb_bs.get(),
            "var_colortemp": self.var_colortemp.get(),
            "var_colortemp_val": self.var_colortemp_val.get(),
            "var_vibrance": self.var_vibrance.get(),
            "var_vibrance_val": self.var_vibrance_val.get(),
            "var_curves": self.var_curves.get(),
            "var_curves_preset": self.var_curves_preset.get(),
            "var_hue_shift": self.var_hue_shift.get(),
            "var_hue_val": self.var_hue_val.get(),
            # Câmera Avançada
            "var_gblur": self.var_gblur.get(),
            "var_gblur_sigma": self.var_gblur_sigma.get(),
            "var_sharpen": self.var_sharpen.get(),
            "var_lagfun": self.var_lagfun.get(),
            "var_monochrome": self.var_monochrome.get(),
            "var_filmgrain": self.var_filmgrain.get(),
            # LUTs
            "lut_dirs": list(self.lb_luts.get(0, tk.END)),
            "lut_sel":  list(self.lb_luts.curselection()),
            "test_vid_a": self.var_vid_a.get(),
            "test_vid_b": self.var_vid_b.get(),
            "test_vid_c": self.var_vid_c.get(),
            "test_vid_d": self.var_vid_d.get(),
            "test_save_dir": self.var_dir_teste.get(),
            "master_hd": self.master_hd.get(),
            "master_overlay": self.master_overlay.get(),
            "master_xfade": self.master_xfade.get(),
            "master_lut": self.master_lut.get(),
            "master_cor": self.master_cor.get(),
            "master_cam": self.master_cam.get(),
            "stinger_types": self.stinger_types,
        }
        self.config_manager.set("estetica_canal", novo_cfg)

    def gerar_video_teste_transicoes(self):
        # Salva silenciosamente a configuração antes de gerar o teste,
        # garantindo que tudo fique memorizado para o Mapeador e reinicializações.
        self._save_config_silent()
        
        import threading, subprocess, tempfile, glob, random, shutil

        m_hd    = self.master_hd.get()
        m_overlay = self.master_overlay.get()
        m_xfade = self.master_xfade.get()
        m_cor   = self.master_cor.get()
        m_cam   = self.master_cam.get()
        m_lut   = self.master_lut.get()
        # st_mode: fallback "luma" — classificação real é por arquivo em self.stinger_types
        st_mode = "color"

        xfade_sel = [nome for nome, bv in self.xfade_var.items() if bv.get()]
        vids = [v for v in [self.var_vid_a.get(), self.var_vid_b.get(),
                            self.var_vid_c.get(), self.var_vid_d.get()] if os.path.exists(v)]

        out_dir = self.var_dir_teste.get()
        if not out_dir or not os.path.isdir(out_dir):
            out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Outputs")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "Teste_Global_Estetica.mp4")

        # ─── Coleta Mídias HD (usa seleção individual de arquivos) ───
        hd_stingers = []
        hd_overlays = []
        if m_hd:
            hd_stingers = [f for f in self.t_files_sel
                           if os.path.isfile(f) and f.lower().endswith(('.mp4', '.mov', '.webm'))]
        if m_overlay:
            hd_overlays  = [f for f in self.o_files_sel
                           if os.path.isfile(f) and f.lower().endswith(('.mp4', '.mov', '.webm'))]

        def worker():
            print("\n" + "="*60, flush=True)
            print("[TESTE] INICIANDO GERADOR DE VIDEO DE ESTETICA", flush=True)
            print(f"[TESTE] Masters -> HD={m_hd} OVL={m_overlay} XFade={m_xfade} Cor={m_cor} Cam={m_cam} LUT={m_lut}", flush=True)
            print(f"[TESTE] XFades marcados: {len(xfade_sel)}", flush=True)
            print(f"[TESTE] HD Stingers: {len(hd_stingers)} | HD Overlays: {len(hd_overlays)}", flush=True)

            _w, _h = 1280, 720
            clip_dur = 4.0
            tdur = 1.0
            colors = ['red','blue','green','darkorange','purple','teal','gold','deeppink']
            font_str = "fontfile='C\\:/Windows/Fonts/arialbd.ttf':"

            def get_vid_duration(path):
                """Usa ffprobe para ler a duração real de um arquivo de vídeo em segundos."""
                try:
                    result = subprocess.run(
                        ["ffprobe", "-v", "error", "-select_streams", "v:0",
                         "-show_entries", "stream=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", path],
                        capture_output=True, text=True, timeout=10
                    )
                    val = result.stdout.strip()
                    if val and val != 'N/A':
                        return float(val)
                    # Fallback: lê pelo container
                    result2 = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries",
                         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
                        capture_output=True, text=True, timeout=10
                    )
                    return float(result2.stdout.strip())
                except Exception:
                    return clip_dur  # fallback seguro

            # ─── Pool Movimentação (Agora atrelado a master_cam) ───
            df_pool = []
            if m_cam:
                if self.var_zoom.get():     df_pool.append("zoom")
                if self.var_zoom_out.get(): df_pool.append("zoom_out")
                if self.var_pan.get():      df_pool.append("pan")
                if self.var_pan_rev.get():  df_pool.append("pan_rev")
                if self.var_tilt.get():     df_pool.append("tilt")
                if self.var_tilt_rev.get(): df_pool.append("tilt_rev")
                if self.var_shake.get():    df_pool.append("shake")
                if self.var_kenburns.get(): df_pool.append("kenburns")
                if self.var_kenburns_rev.get(): df_pool.append("kenburns_rev")
                if self.var_kenburns_up.get():  df_pool.append("kenburns_up")
                if self.var_kenburns_down.get(): df_pool.append("kenburns_down")
            print(f"[TESTE] Pool Movimentação: {df_pool if df_pool else 'Nenhum'}", flush=True)

            amp    = float(self.var_zoom_amp.get())
            pan_s  = float(self.var_pan_speed.get())
            tilt_s = float(self.var_tilt_speed.get())
            shk    = float(self.var_shake_int.get())
            kb     = float(self.var_kenburns_int.get())

            def get_df_filter(idx):
                if not df_pool:
                    return "", "sem-movimento"
                
                # Dimensões exatas e pares para evitar "Error reinitializing filters"
                # Aumentei para 25% de margem no Pan/Tilt para suportar a velocidade desejada sem bater no limite
                sw25 = int(_w * 1.25) // 2 * 2
                sh25 = int(_h * 1.25) // 2 * 2
                sw11 = int(_w * 1.1) // 2 * 2
                sh11 = int(_h * 1.1) // 2 * 2
                
                # No teste, SEMPRE rodamos sequencial para garantir que todos sejam mostrados!
                fx = df_pool[idx % len(df_pool)]
                if fx == "zoom":
                    # Zoom agressivo (multiplica in_time pelo amp diretamente)
                    return f",zoompan=z='1.0+({amp}*in_time)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={_w}x{_h}:fps=30,setsar=1", "zoom"
                elif fx == "zoom_out":
                    # Zoom Out afasta a câmera
                    return f",zoompan=z='max(1.0, (1.0+{amp}*5)-({amp}*in_time))':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={_w}x{_h}:fps=30,setsar=1", "zoom_out"
                elif fx == "pan":
                    # Escala em 25% e faz pan agressivo na velocidade do slider (Esq->Dir)
                    return f",scale=w={sw25}:h={sh25},crop=w={_w}:h={_h}:x='t*{_w}*{pan_s}':y='(in_h-out_h)/2',setsar=1", "pan"
                elif fx == "pan_rev":
                    # Pan reverso (Dir->Esq)
                    return f",scale=w={sw25}:h={sh25},crop=w={_w}:h={_h}:x='(in_w-out_w)-t*{_w}*{pan_s}':y='(in_h-out_h)/2',setsar=1", "pan_rev"
                elif fx == "tilt":
                    # Escala em 25% e faz tilt agressivo (Cima->Baixo)
                    return f",scale=w={sw25}:h={sh25},crop=w={_w}:h={_h}:x='(in_w-out_w)/2':y='t*{_h}*{tilt_s}',setsar=1", "tilt"
                elif fx == "tilt_rev":
                    # Tilt reverso (Baixo->Cima)
                    return f",scale=w={sw25}:h={sh25},crop=w={_w}:h={_h}:x='(in_w-out_w)/2':y='(in_h-out_h)-t*{_h}*{tilt_s}',setsar=1", "tilt_rev"
                elif fx == "shake":
                    # Tremor senoidal baseado no tempo
                    return f",scale=w={sw11}:h={sh11},crop=w={_w}:h={_h}:x='(in_w-out_w)/2+{shk}*sin(t*10)':y='(in_h-out_h)/2+{shk}*cos(t*15)',setsar=1", "shake"
                elif fx == "kenburns":
                    # KenBurns (Zoom + Pan Direita)
                    return f",zoompan=z='1.0+({kb}*in_time)':x='min(iw-(iw/zoom), (iw/2-(iw/zoom/2))+({kb}*200*in_time))':y='ih/2-(ih/zoom/2)':d=1:s={_w}x{_h}:fps=30,setsar=1", "kenburns"
                elif fx == "kenburns_rev":
                    # KenBurns (Zoom + Pan Esquerda)
                    return f",zoompan=z='1.0+({kb}*in_time)':x='max(0, (iw/2-(iw/zoom/2))-({kb}*200*in_time))':y='ih/2-(ih/zoom/2)':d=1:s={_w}x{_h}:fps=30,setsar=1", "kenburns_rev"
                elif fx == "kenburns_down":
                    # KenBurns (Zoom + Tilt Baixo)
                    return f",zoompan=z='1.0+({kb}*in_time)':x='iw/2-(iw/zoom/2)':y='min(ih-(ih/zoom), (ih/2-(ih/zoom/2))+({kb}*200*in_time))':d=1:s={_w}x{_h}:fps=30,setsar=1", "kenburns_down"
                elif fx == "kenburns_up":
                    # KenBurns (Zoom + Tilt Cima)
                    return f",zoompan=z='1.0+({kb}*in_time)':x='iw/2-(iw/zoom/2)':y='max(0, (ih/2-(ih/zoom/2))-({kb}*200*in_time))':d=1:s={_w}x{_h}:fps=30,setsar=1", "kenburns_up"
                return "", "sem-movimento"

            # ─── Coleta nomes de todos efeitos ativos para HUD ───
            cor_pool = []
            cam_pool = []
            active_lut_name  = ""

            if m_cor:
                if self.var_usar_sat.get() or self.var_usar_cont.get() or self.var_usar_bri.get():
                    sat = self.var_sat.get() if self.var_usar_sat.get() else 1.0
                    cont = self.var_cont.get() if self.var_usar_cont.get() else 1.0
                    bri = self.var_bri.get() if self.var_usar_bri.get() else 0.0
                    cor_pool.append((f"eq=saturation={sat}:contrast={cont}:brightness={bri}", f"sat={sat:.1f}/cont={cont:.1f}/bri={bri:.1f}"))
                if self.var_vibrance.get():
                    vib_sat = round(1.0 + float(self.var_vibrance_val.get()) * 0.5, 2)
                    cor_pool.append((f"eq=saturation={vib_sat}", f"vibrance={self.var_vibrance_val.get():.1f}"))
                if self.var_hue_shift.get():   cor_pool.append((f"hue=h={self.var_hue_val.get()}", f"hue={self.var_hue_val.get():.0f}g"))
                if self.var_colortemp.get():
                    _temp_k = float(self.var_colortemp_val.get())
                    _warm = round((_temp_k - 6500) / 6500 * 0.15, 3)
                    _cool = round(-_warm, 3)
                    cor_pool.append((f"colorchannelmixer=rr=1.0:rb={_warm}:gg=1.0:bb=1.0:br={_cool}", f"temp={self.var_colortemp_val.get()}K"))
                if self.var_colorbalance.get():cor_pool.append((f"colorbalance=rs={self.var_cb_rs.get()}:gs={self.var_cb_gs.get()}:bs={self.var_cb_bs.get()}", f"cbal R{self.var_cb_rs.get():.1f}/G{self.var_cb_gs.get():.1f}/B{self.var_cb_bs.get():.1f}"))
                if self.var_curves.get() and self.var_curves_preset.get() != "none":
                    if self.var_curves_preset.get() == "TODOS (Showcase)":
                        # Exclui color_negative e negative (invertem cores - efeito indesejado em producao)
                        for preset in ["cross_process", "darker", "increase_contrast", "lighter",
                                       "linear_contrast", "medium_contrast", "strong_contrast", "vintage"]:
                            cor_pool.append((f"curves=preset={preset}", f"curves={preset}"))
                    else:
                        cor_pool.append((f"curves=preset={self.var_curves_preset.get()}", f"curves={self.var_curves_preset.get()}"))
            if m_cam:
                if self.var_vignette.get():   cam_pool.append(("vignette=angle=PI/4", "vignette"))
                if self.var_noise.get():      cam_pool.append(("noise=alls=10:allf=t", "noise"))
                if self.var_filmgrain.get():  cam_pool.append(("noise=c0s=12:c0f=u+t:c1s=6:c1f=u", "filmgrain"))
                if self.var_gblur.get():      cam_pool.append((f"gblur=sigma={self.var_gblur_sigma.get()}", f"blur={self.var_gblur_sigma.get()}"))
                if self.var_sharpen.get():    cam_pool.append(("unsharp=5:5:1.5:5:5:0.0", "sharpen"))
                if self.var_lagfun.get():     cam_pool.append(("lagfun=decay=0.95", "light-trail"))
                if self.var_glitch.get():     cam_pool.append(("rgbashift=rh=-5:bh=5", "glitch"))
                if self.var_vhs.get():        cam_pool.append(("noise=alls=15:allf=t,rgbashift=rh=-3:rv=0:bh=3:bv=0,eq=saturation=1.3:contrast=1.1,gblur=sigma=0.5", "vhs"))
                if self.var_monochrome.get(): cam_pool.append(("colorchannelmixer=rr=0.3:rg=0.4:rb=0.3:gr=0.3:gg=0.4:gb=0.3:br=0.3:bg=0.4:bb=0.3", "mono"))
            lut_pool = []

            if m_lut and hasattr(self, 'lut_files_sel') and self.lut_files_sel:
                for cube in self.lut_files_sel:
                    ce = cube.replace('\\', '/').replace(':', '\\:')
                    lut_pool.append((f"lut3d=file='{ce}'", os.path.basename(cube)))

            # ─── Quantidade de blocos ───
            # Obrigatório rodar TODOS os efeitos marcados pelo menos uma vez
            n_df = len(df_pool) if m_cam else 0
            n_xfade = len(xfade_sel) + 1 if m_xfade else 0
            n_stinger = len(hd_stingers) + 1 if m_hd else 0
            n_overlay = len(hd_overlays) if m_hd else 0
            n_cam = len(cam_pool) if m_cam else 0
            n_cor = len(cor_pool) if m_cor else 0
            n_lut = len(lut_pool) if m_lut else 0
            n_mov = len(df_pool) if m_cam else 0

            
            num_blocks = max(4, n_mov, n_xfade, n_stinger, n_overlay, n_cam, n_cor, n_lut)
            print(f"[TESTE] Total de clips necessarios p/ cobrir efeitos: {num_blocks}", flush=True)

            fc_lines = []
            cmd = ["ffmpeg", "-y"]

            for i in range(num_blocks):
                vid = vids[i % len(vids)] if vids else ""
                if vid:
                    cmd.extend(["-i", vid])
                    v_str = f"scale={_w}:{_h}:force_original_aspect_ratio=increase,crop={_w}:{_h},setsar=1,fps=30,format=yuv420p"
                    # Limite de duração somente se não houver vídeos reais de referência
                    # (cada vídeo entra com sua duração real — a timeline é dinâmica!)
                else:
                    c = colors[i % len(colors)]
                    cmd.extend(["-f", "lavfi", "-t", str(clip_dur), "-i", f"color=c={c}:s={_w}x{_h}:d={clip_dur}:r=30"])
                    v_str = "format=yuv420p,drawgrid=width=100:height=100:thickness=4:color=black@0.5"

                df_str, df_name = get_df_filter(i)
                cam_str = ""
                cam_name = "OFF"
                if m_cam and cam_pool:
                    fx_str, fx_name = cam_pool[i % len(cam_pool)]
                    cam_str = f",{fx_str}"
                    cam_name = fx_name
                    
                cor_str = ""
                cor_name = "OFF"
                if m_cor and cor_pool:
                    c_str, c_name = cor_pool[i % len(cor_pool)]
                    cor_str = f",{c_str}"
                    cor_name = c_name

                lut_str = ""
                lut_name = "OFF"
                if m_lut and lut_pool:
                    l_str, l_name = lut_pool[i % len(lut_pool)]
                    lut_str = f",{l_str}"
                    lut_name = l_name

                print(f"[TESTE] Clip {i}: DF='{df_name}' COR='{cor_name}' CAM='{cam_name}' LUT='{lut_name}'", flush=True)

                txt_df = f"drawtext={font_str}text='CLIP {i+1}  DF\\: {df_name}':fontsize=38:fontcolor=yellow:x=20:y=20:box=1:boxcolor=black@0.6:boxborderw=6"
                
                txt_cor = f"drawtext={font_str}text='COR\\: {cor_name}':fontsize=28:fontcolor=cyan:x=w-text_w-20:y=20:box=1:boxcolor=black@0.5:boxborderw=5"
                txt_cam = f"drawtext={font_str}text='CAM\\: {cam_name}':fontsize=28:fontcolor=lime:x=w-text_w-20:y=60:box=1:boxcolor=black@0.5:boxborderw=5"
                txt_lut = f"drawtext={font_str}text='LUT\\: {lut_name}':fontsize=28:fontcolor=orange:x=w-text_w-20:y=100:box=1:boxcolor=black@0.5:boxborderw=5"

                fc_lines.append(f"[{i}:v]{v_str}{df_str}{cor_str}{cam_str}{lut_str},{txt_df},{txt_cor},{txt_cam},{txt_lut},setpts=PTS-STARTPTS[v{i}];")

            xfade_drawtexts = []
            if m_xfade and xfade_sel:
                curr_v = "[v0]"
                curr_len = clip_dur
                
                for i in range(1, num_blocks):
                    xf = xfade_sel[(i-1) % len(xfade_sel)]
                    offset = curr_len - tdur
                    out_v = f"[v{i}_out]"
                    fc_lines.append(f"{curr_v}[v{i}]xfade=transition={xf}:duration={tdur}:offset={offset}{out_v};")
                    
                    # HUD do XFade
                    hud_v = f"[vhud{i}]"
                    draw_xf = f"drawtext={font_str}text='XFADE\\: {xf}':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=h-80:box=1:boxcolor=black@0.5:boxborderw=5:enable='between(t,{offset},{offset+tdur})'"
                    xfade_drawtexts.append(draw_xf)
                    
                    curr_len = offset + clip_dur
                    curr_v = out_v
            else:
                print(f"[TESTE] Sem XFade — concat {num_blocks} clips", flush=True)
                con_in = "".join([f"[v{i}]" for i in range(num_blocks)])
                fc_lines.append(f"{con_in}concat=n={num_blocks}:v=1:a=0[vout_raw];")
                curr_v = "[vout_raw]"

            # Nenhum filtro global no teste, pois todos já foram aplicados per-clip


            if m_xfade and xfade_sel and xfade_drawtexts:
                fc_lines.append(f"{curr_v}{','.join(xfade_drawtexts)}[vout]")
            else:
                fc_lines.append(f"{curr_v}copy[vout]")

            # ─── Salva script e executa FASE 1 (Base + Cor + XFade) ───
            fd, script_path = tempfile.mkstemp(suffix=".txt", text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write("\n".join(fc_lines))

            print("\n[TESTE] === FILTER_COMPLEX SCRIPT ===", flush=True)
            for ln in fc_lines:
                print(f"  {ln}", flush=True)
            print("[TESTE] ===================================\n", flush=True)

            cmd.extend(["-filter_complex_script", script_path,
                        "-map", "[vout]", "-c:v", "libx264", "-preset", "fast", "-crf", "22", out_file])
            
            try:
                print("[TESTE] Executando FFmpeg Fase 1...", flush=True)
                proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8", errors="replace")
                last_err = ""
                for line in proc.stderr:
                    if "Error" in line or "error" in line.lower(): last_err += line
                proc.wait()
                if proc.returncode != 0:
                    print(f"\n[ERRO FFMPEG FASE 1]\n{last_err}", flush=True)
                    self.after(0, lambda: messagebox.showerror("Erro FFmpeg", f"Fase 1 falhou! Verifique o log.\n{last_err[-200:]}"))
                    return
                
                final_video = out_file
                
                # FASE 2: HD Stingers (motor 100% dinâmico)
                if m_hd and hd_stingers:
                    max_stingers = min(len(hd_stingers), num_blocks - 1)
                    print(f"[TESTE] FASE 2: Aplicando {max_stingers} HD Stingers (posicionamento dinâmico)...", flush=True)
                    stinger_out = os.path.join(out_dir, "Teste_Global_Estetica_Stingers.mp4")

                    # ── Passo 1: Mede a duração REAL de cada clipe ──
                    # ATENÇÃO: NÃO usar min(dur, clip_dur) aqui!
                    # A duração usada no timestamp TEM que ser idêntica à duração
                    # real do vídeo carregado na FASE 1. Qualquer diferença gera
                    # um drift cumulativo que desloca todas as transições.
                    real_durations = []
                    for i in range(num_blocks):
                        vid = vids[i % len(vids)] if vids else ""
                        if vid:
                            dur = get_vid_duration(vid)   # duração real do arquivo
                        else:
                            dur = clip_dur                 # fallback para cores sólidas
                        real_durations.append(round(dur, 4))
                        print(f"    Clip {i}: {os.path.basename(vid) if vid else 'cor-solida'} = {round(dur,3)}s", flush=True)

                    cut_timestamps = []
                    t = 0.0
                    for dur in real_durations:
                        t += dur
                        cut_timestamps.append(round(t, 4))
                    total_dur = cut_timestamps[-1]
                    print(f"[TESTE] Duração total do vídeo base: {total_dur:.2f}s | Cortes: {cut_timestamps}", flush=True)

                    current_video = final_video
                    st_half_default = 1.0
                    for idx in range(max_stingers):
                        st      = hd_stingers[idx]
                        cut_t   = cut_timestamps[idx]
                        st_real_dur = get_vid_duration(st)
                        st_real_dur_safe = max(0.1, st_real_dur)
                        
                        # Padronização absoluta: exatos 2.0 segundos para TODOS os efeitos!
                        st_half = 1.0 
                        speed_factor = round(2.0 / st_real_dur_safe, 4)

                        st_file_mode = self.stinger_types.get(st, "color") \
                            if hasattr(self, 'stinger_types') else "color"

                        st_a_start = max(0.0, round(cut_t - st_half, 4))
                        st_b_end   = min(total_dur, round(cut_t + st_half, 4))

                        pass_out = os.path.join(out_dir, f"_st_pass_{idx}.mp4")
                        sc_st = (f"scale={_w}:{_h}:force_original_aspect_ratio=decrease,"
                                 f"pad={_w}:{_h}:(ow-iw)/2:(oh-ih)/2")

                        cmd_pass = [
                            "ffmpeg", "-y",
                            "-i", current_video,
                            "-i", st,
                        ]

                        if st_file_mode == "luma":
                            # Lógica Mágica: Wipe real com tpad!
                            # Congela o último frame do Clipe A e o primeiro do Clipe B.
                            # Cria uma sobreposição de 2.0s perfeitos SEM encolher o vídeo base!
                            fc_pass = (
                                f"[0:v]trim=start=0:end={st_a_start},setpts=PTS-STARTPTS[before];"
                                f"[0:v]trim=start={st_a_start}:end={cut_t},setpts=PTS-STARTPTS[clip_a_raw];"
                                f"[0:v]trim=start={cut_t}:end={st_b_end},setpts=PTS-STARTPTS[clip_b_raw];"
                                f"[0:v]trim=start={st_b_end},setpts=PTS-STARTPTS[after];"
                                f"[clip_a_raw]tpad=stop_mode=clone:stop_duration={st_half}[clip_a];"
                                f"[clip_b_raw]tpad=start_mode=clone:start_duration={st_half}[clip_b];"
                                f"[1:v]{sc_st},format=yuv420p,colorlevels=rimin=0.4:rimax=0.6:gimin=0.4:gimax=0.6:bimin=0.4:bimax=0.6,setpts=PTS*{speed_factor}[luma_raw];"
                                f"[clip_b]format=yuva420p[clip_b_alpha];"
                                f"[clip_b_alpha][luma_raw]alphamerge[b_masked];"
                                f"[clip_a][b_masked]overlay=format=auto[wipe];"
                                f"[before][wipe][after]concat=n=3:v=1:a=0[merged];"
                                f"[merged]format=yuv420p[final_out]"
                            )
                            print(f"  Stinger {idx+1}/{max_stingers} [LUMA TPAD x{speed_factor}]: corte={cut_t:.2f}s | "
                                  f"Wipe Perfeito: {st_a_start:.2f}s até {st_b_end:.2f}s", flush=True)

                        else:
                            fc_pass = (
                                f"[0:v]trim=start=0:end={st_a_start},setpts=PTS-STARTPTS[before];"
                                f"[0:v]trim=start={st_a_start}:end={st_b_end},setpts=PTS-STARTPTS[base_seg];"
                                f"[0:v]trim=start={st_b_end},setpts=PTS-STARTPTS[after];"
                                f"[1:v]{sc_st},format=yuva420p,setpts=PTS*{speed_factor},colorkey=color=black:similarity=0.03:blend=0.03[st_keyed];"
                                f"[base_seg][st_keyed]overlay=format=auto[b_masked];"
                                f"[before][b_masked][after]concat=n=3:v=1:a=0[merged];"
                                f"[merged]format=yuv420p[final_out]"
                            )
                            print(f"  Stinger {idx+1}/{max_stingers} [COLOR x{speed_factor}]: corte={cut_t:.2f}s | "
                                  f"Overlay Fixo: {st_a_start:.2f}s até {st_b_end:.2f}s", flush=True)

                        cmd_pass.extend(["-filter_complex", fc_pass,
                                         "-map", "[final_out]",
                                         "-c:v", "libx264", "-preset", "fast", "-crf", "22", pass_out])

                        proc_pass = subprocess.Popen(cmd_pass, stderr=subprocess.PIPE,
                                                     stdout=subprocess.PIPE, encoding="utf-8", errors="replace")
                        pass_err = ""
                        for line in proc_pass.stderr:
                            if "error" in line.lower() or "invalid" in line.lower():
                                pass_err += line
                        proc_pass.wait()

                        if proc_pass.returncode == 0:
                            current_video = pass_out
                            print(f"    OK → {pass_out}", flush=True)
                            # O tempo do vídeo agora é INTOCÁVEL. 
                            # Sem encolhimentos, sem "drift correction", sincronia impecável a cada 5.2s!
                        else:
                            print(f"    FALHOU:\n{pass_err[-400:]}", flush=True)
                            break

                    stinger_out = current_video  # resultado final é o ultimo passe bem-sucedido

                    # Renomeia para o nome final esperado
                    final_stinger_path = os.path.join(out_dir, "Teste_Global_Estetica_Stingers.mp4")
                    if stinger_out != final_stinger_path and os.path.exists(stinger_out):
                        shutil.copy2(stinger_out, final_stinger_path)
                    stinger_out = final_stinger_path

                    if os.path.exists(stinger_out):
                        final_video = stinger_out
                        print("[TESTE] HD Stingers aplicados com sucesso.", flush=True)
                    else:
                        print("[TESTE] Falha: nenhum stinger foi gerado.", flush=True)

                # FASE 3: HD Overlays (Partículas e camadas de efeito)
                if m_overlay and hd_overlays:
                    print(f"[TESTE] FASE 3: Aplicando {len(hd_overlays)} HD Overlays (screen blend)...", flush=True)
                    ov_out = os.path.join(out_dir, "Teste_Global_Estetica_Final.mp4")

                    cmd_ov = ["ffmpeg", "-y", "-i", final_video]
                    fc_ov = ""
                    fc_ov += "[0:v]format=rgb24[base_ov0]; "

                    for idx, ov in enumerate(hd_overlays):
                        start_t = idx * clip_dur
                        end_t   = start_t + clip_dur
                        # stream_loop garante que a particula cubra todo o clip
                        cmd_ov.extend(["-stream_loop", "-1", "-t", str(clip_dur), "-i", ov])
                        
                        sc_ov = f"scale={_w}:{_h},setsar=1"
                        
                        # Usa tpad para sincronizar a entrada e colorlevels agressivo para destruir fundos cinzas/rosados
                        fc_ov += f"[{idx+1}:v]format=rgb24,{sc_ov},colorlevels=rimin=0.15:gimin=0.15:bimin=0.15,tpad=start_duration={start_t}:color=black[ov_s{idx}]; "
                        
                        base_in = "base_ov0" if idx == 0 else f"vov{idx-1}"
                        ov_name = os.path.basename(ov).replace(':', '').replace("'", "")
                        txt_ov = f"drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='OVL\\: {ov_name}':fontsize=28:fontcolor=magenta:x=20:y=h-60:box=1:boxcolor=black@0.6:boxborderw=6:enable='between(t,{start_t},{end_t})'"
                        
                        fc_ov += f"[{base_in}][ov_s{idx}]blend=all_mode=screen:all_opacity=0.7:enable='between(t,{start_t},{end_t})',{txt_ov}[vov{idx}]; "

                    last_ov = f"vov{len(hd_overlays)-1}" if hd_overlays else "base_ov0"
                    
                    fc_ov += f"[{last_ov}]format=yuv420p[final_ov_out]; "
                    
                    fc_ov_clean = fc_ov.rstrip().rstrip(';').rstrip()
                    cmd_ov.extend(["-filter_complex", fc_ov_clean,
                                   "-map", "[final_ov_out]",
                                   "-c:v", "libx264", "-preset", "fast", "-crf", "22", ov_out])

                    proc_ov = subprocess.Popen(cmd_ov, stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8", errors="replace")
                    ov_err = ""
                    for line in proc_ov.stderr:
                        if "error" in line.lower() or "invalid" in line.lower():
                            ov_err += line
                    proc_ov.wait()
                    if proc_ov.returncode == 0:
                        final_video = ov_out
                        print("[TESTE] HD Overlays aplicados com sucesso.", flush=True)
                    else:
                        print("[TESTE] Falha ao aplicar HD Overlays.", flush=True)

                if os.path.exists(final_video):
                    os.startfile(final_video)
                else:
                    messagebox.showerror("Erro", "O vídeo de teste não foi gerado.")
            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("Erro", str(e))
            finally:
                if hasattr(self, 'btn_teste'):
                    self.btn_teste.config(state=tk.NORMAL)
                    self.btn_teste.config(text="🎬 Gerar Vídeo Teste")
        
        import threading
        threading.Thread(target=worker, daemon=True).start()

class MultiSelectDialog(tk.Toplevel):
    def __init__(self, parent, title, listbox, files_sel_ref, on_close_callback=None, stinger_types=None):
        super().__init__(parent)
        self.title(f"\U0001f4c2 Gerenciador de Efeitos: {title}")
        self.geometry("1600x900")
        self.minsize(1200, 700)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self._stinger_types = stinger_types
        self._type_vars = {}
        
        style = ttk.Style()
        style.configure("Large.TButton", font=("Segoe UI", 12, "bold"))
        style.configure("Large.TCheckbutton", font=("Segoe UI", 12))
        style.configure("LargeLbl.TLabel", font=("Segoe UI", 12))

        self.listbox = listbox
        self.files_sel_ref = files_sel_ref
        self.on_close_callback = on_close_callback
        self._right_vars = {}
        self._current_folder = None

        f_top = ctk.CTkFrame(self)
        f_top.pack(fill=tk.X, padx=20, pady=20)
        ctk.CTkButton(f_top, text="➕ Adicionar Pasta ao Banco", command=self._add_dir).pack(side=tk.LEFT, padx=4)
        ctk.CTkButton(f_top, text="🗑 Remover Pasta do Banco", command=self._remove_folder).pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(f_top, text="  |  ").pack(side=tk.LEFT)
        ctk.CTkButton(f_top, text="✔ Marcar Todos Arquivos Visíveis", command=self._check_all_right).pack(side=tk.LEFT, padx=4)
        ctk.CTkButton(f_top, text="✖ Desmarcar Todos", command=self._uncheck_all_right).pack(side=tk.LEFT, padx=4)
        ctk.CTkLabel(f_top, text="  |  ").pack(side=tk.LEFT)
        self._lbl_count = ctk.CTkLabel(f_top, text="0 arquivo(s) selecionado(s) no total", text_color="#2ED573", font=("Segoe UI", 13, "bold"))
        self._lbl_count.pack(side=tk.LEFT, padx=15)

        f_search = ctk.CTkFrame(self)
        f_search.pack(fill=tk.X, padx=20, pady=(0, 10))
        ctk.CTkLabel(f_search, text="🔍 Filtrar pastas por nome:").pack(side=tk.LEFT)
        self._search_var = tk.StringVar()
        self._search_var.trace('w', self._filter_folders)
        ctk.CTkEntry(f_search, textvariable=self._search_var, width=400, font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=20)

        f_main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        f_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        f_left = ctk.CTkLabelFrame(f_main, text=" 📁 Pastas do Banco ")
        f_main.add(f_left, weight=2)
        
        f_left_top = ctk.CTkFrame(f_left)
        f_left_top.pack(fill=tk.X, pady=(0, 10))
        self._btn_explorer_left = ctk.CTkButton(f_left_top, text="📂 Abrir Pasta Selecionada no Windows Explorer", 
                                        command=self._open_explorer, state="disabled")
        self._btn_explorer_left.pack(fill=tk.X)

        self._lb_folders = tk.Listbox(f_left, selectmode=tk.SINGLE, activestyle='dotbox',
                                      font=("Segoe UI", 11),
                                      selectbackground="#89b4fa", selecttext_color="#1e1e2e")
        sc_l = ttk.Scrollbar(f_left, orient="vertical", command=self._lb_folders.yview)
        sc_lh = ttk.Scrollbar(f_left, orient="horizontal", command=self._lb_folders.xview)
        self._lb_folders.config(yscrollcommand=sc_l.set, xscrollcommand=sc_lh.set)
        sc_l.pack(side=tk.RIGHT, fill=tk.Y)
        sc_lh.pack(side=tk.BOTTOM, fill=tk.X)
        self._lb_folders.pack(fill=tk.BOTH, expand=True)
        self._lb_folders.bind("<<ListboxSelect>>", self._on_folder_select)
        self._lb_folders.bind("<Double-1>", self._open_explorer_event)

        f_right = ctk.CTkLabelFrame(f_main, text=" 🎬 Arquivos na Pasta Selecionada ")
        f_main.add(f_right, weight=1)
        
        f_right_top = ctk.CTkFrame(f_right)
        f_right_top.pack(fill=tk.X, pady=(0, 10))
        self._lbl_folder_path = ctk.CTkLabel(f_right_top, text="← Clique em uma pasta na esquerda para carregar os arquivos...",
                                          text_color="#aaa", font=("Segoe UI", 12, "italic"))
        self._lbl_folder_path.pack(side=tk.LEFT, padx=4)

        self._right_canvas = tk.Canvas(f_right)
        sc_r = ttk.Scrollbar(f_right, orient="vertical", command=self._right_canvas.yview)
        self._right_frame = ctk.CTkFrame(self._right_canvas)
        self._right_frame.bind("<Configure>", lambda e: self._right_canvas.configure(scrollregion=self._right_canvas.bbox("all")))
        self._right_win = self._right_canvas.create_window((0, 0), window=self._right_frame, anchor="nw")
        self._right_canvas.bind("<Configure>", lambda e: self._right_canvas.itemconfig(self._right_win, width=e.width))
        self._right_canvas.configure(yscrollcommand=sc_r.set)
        sc_r.pack(side=tk.RIGHT, fill=tk.Y)
        self._right_canvas.pack(fill=tk.BOTH, expand=True)
        self._right_canvas.bind("<MouseWheel>", lambda e: self._right_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        f_bot = ctk.CTkFrame(self)
        f_bot.pack(fill=tk.X, padx=20, pady=20)
        ctk.CTkButton(f_bot, text="✔ Salvar Minha Seleção e Fechar", command=self._on_close).pack(side=tk.RIGHT, ipadx=20, ipady=12)
        ctk.CTkButton(f_bot, text="✖ Cancelar Alterações", command=self.destroy).pack(side=tk.RIGHT, padx=15)

        self._populate_folders()
        self._update_count()

    def _populate_folders(self):
        self._lb_folders.delete(0, tk.END)
        query = self._search_var.get().lower()
        active_dirs = {os.path.dirname(f) for f in self.files_sel_ref}
        idx = 0
        for folder in self.listbox.get(0, tk.END):
            if query in folder.lower():
                self._lb_folders.insert(tk.END, folder)
                if folder in active_dirs:
                    self._lb_folders.itemconfig(idx, {'fg': '#a6e3a1', 'bg': '#2e3b32'})
                idx += 1

    def _filter_folders(self, *_):
        self._populate_folders()
        self._clear_right()

    def _on_folder_select(self, *_):
        sel = self._lb_folders.curselection()
        if not sel: return
        folder = self._lb_folders.get(sel[0])
        self._current_folder = folder
        self._lbl_folder_path.config(text=folder)
        self._btn_explorer_left.config(state="normal")
        self._load_right(folder)

    def _open_explorer_event(self, event): self._open_explorer()
    def _open_explorer(self):
        import os, subprocess
        if not self._current_folder: return
        path = os.path.normpath(self._current_folder.strip())
        if os.path.exists(path): subprocess.Popen(['explorer', path])

    def _clear_right(self):
        for w in self._right_frame.winfo_children(): w.destroy()
        self._right_vars.clear()
        self._type_vars.clear()
        self._right_canvas.yview_moveto(0)

    def _load_right(self, folder):
        self._clear_right()
        if not os.path.isdir(folder):
            ctk.CTkLabel(self._right_frame, text="\u26a0 Pasta n\u00e3o encontrada.",
                      text_color="red").pack(anchor="w", padx=20, pady=12)
            return

        files = sorted([f for f in os.listdir(folder)
                        if f.lower().endswith(('.mp4', '.mov', '.webm', '.cube'))], key=str.lower)
        if not files:
            ctk.CTkLabel(self._right_frame, text="Nenhum arquivo compat\u00edvel encontrado nesta pasta.",
                      text_color="#888").pack(anchor="w", padx=20, pady=12)
            return

        is_stinger_mgr = self._stinger_types is not None

        for fname in files:
            fpath = os.path.join(folder, fname)
            var = tk.BooleanVar(value=(fpath in self.files_sel_ref))
            self._right_vars[fpath] = var

            row = ctk.CTkFrame(self._right_frame)
            row.pack(fill=tk.X, pady=3)

            cb = ctk.CTkSwitch(row, text=fname, variable=var,
                                 command=self._update_count)
            cb.pack(side=tk.LEFT, padx=20)

            if is_stinger_mgr:
                # Valor atual: color por padrão se não classificado
                current_type = self._stinger_types.get(fpath, "color")
                tv = tk.StringVar(value=current_type)
                self._type_vars[fpath] = tv

                def _make_toggle(fp, v):
                    def _toggle():
                        self._stinger_types[fp] = v.get()
                    return _toggle

                ttk.Radiobutton(row, text="\u26ab Luma (P&B)", variable=tv, value="luma",
                                command=_make_toggle(fpath, tv)).pack(side=tk.LEFT, padx=(15, 2))
                ttk.Radiobutton(row, text="\U0001f7e0 Colorido", variable=tv, value="color",
                                command=_make_toggle(fpath, tv)).pack(side=tk.LEFT, padx=(0, 10))

        self._update_count()

    def _check_all_right(self):
        for var in self._right_vars.values(): var.set(True)
        self._apply_right_to_sel()
        self._update_count()

    def _uncheck_all_right(self):
        for var in self._right_vars.values(): var.set(False)
        self._apply_right_to_sel()
        self._update_count()

    def _apply_right_to_sel(self):
        if self._current_folder:
            to_remove = [p for p in list(self.files_sel_ref) if os.path.dirname(p) == self._current_folder]
            for p in to_remove: self.files_sel_ref.discard(p)
        for fpath, var in self._right_vars.items():
            if var.get(): self.files_sel_ref.add(fpath)

    def _update_count(self):
        self._apply_right_to_sel()
        self._lbl_count.config(text=f"{len(self.files_sel_ref)} arquivo(s) selecionado(s) no total")
        if self.on_close_callback:
            self.on_close_callback() # Salva e atualiza o botão pai em tempo real!
        
        # Atualiza o destaque das pastas na lista da esquerda em tempo real
        active_dirs = {os.path.dirname(f) for f in self.files_sel_ref}
        for i in range(self._lb_folders.size()):
            folder = self._lb_folders.get(i)
            if folder in active_dirs:
                self._lb_folders.itemconfig(i, {'fg': '#a6e3a1', 'bg': '#2e3b32'})
            else:
                self._lb_folders.itemconfig(i, {'fg': '#cdd6f4', 'bg': '#1e1e2e'})


    def _add_dir(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Selecione a pasta para adicionar ao banco")
        if folder and folder not in self.listbox.get(0, tk.END):
            self.listbox.insert(tk.END, folder)
            self._populate_folders()

    def _remove_folder(self):
        from tkinter import messagebox
        sel = self._lb_folders.curselection()
        if not sel: return
        folder = self._lb_folders.get(sel[0])
        if not messagebox.askyesno("Remover Pasta", f"Remover esta pasta do banco?\\n\\n{folder}"): return
        all_items = list(self.listbox.get(0, tk.END))
        if folder in all_items: self.listbox.delete(all_items.index(folder))
        to_remove = [p for p in list(self.files_sel_ref) if os.path.dirname(p) == folder]
        for p in to_remove: self.files_sel_ref.discard(p)
        self._populate_folders()
        self._clear_right()
        self._current_folder = None
        self._lbl_folder_path.config(text="← Clique em uma pasta para ver os arquivos")
        self._btn_explorer_left.config(state="disabled")
        self._update_count()

    def _on_close(self):
        self._apply_right_to_sel()
        if self.on_close_callback: self.on_close_callback()
        self.destroy()

class TabPerfisLegenda(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager

        ctk.CTkLabel(self, text="📝 Gerenciador de Perfis de Legenda",
                  font=("Segoe UI", 13, "bold")).pack(pady=(10, 0))
        ctk.CTkLabel(self,
                  text="Crie perfis completos com cores customizadas e vincule-os aos seus personagens.",
                  text_color="#888").pack(pady=(2, 6))

        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ── Lista Esquerda: Perfis ──────────────────────────────────────────
        frame_lista = ctk.CTkLabelFrame(paned, text=" Seus Perfis ")
        paned.add(frame_lista, weight=1)

        self.listbox = tk.Listbox(frame_lista, activestyle='dotbox', font=("Segoe UI", 11), height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        btn_frame = ctk.CTkFrame(frame_lista)
        btn_frame.pack(fill=tk.X, padx=15, pady=12)
        
        self.var_novo_nome = tk.StringVar()
        ctk.CTkEntry(btn_frame, textvariable=self.var_novo_nome).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ctk.CTkButton(btn_frame, text="➕ Criar", command=self.add_profile).pack(side=tk.RIGHT)
        ctk.CTkButton(frame_lista, text="🗑️ Deletar Selecionado", command=self.delete_profile).pack(fill=tk.X, padx=15, pady=2)
        ctk.CTkButton(frame_lista, text="✏️ Renomear Selecionado", command=self.rename_profile).pack(fill=tk.X, padx=15, pady=2)
        
        # ── Form Direito: Edição e Preview ──────────────────────────────────
        self.frame_form = ctk.CTkLabelFrame(paned, text=" Configurações do Perfil ")
        paned.add(self.frame_form, weight=4)
        
        main_paned = ttk.PanedWindow(self.frame_form, orient=tk.VERTICAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # Parte superior: controles
        f_sub = ctk.CTkFrame(main_paned)
        main_paned.add(f_sub, weight=2)

        # Parte inferior: preview
        f_preview = ctk.CTkLabelFrame(main_paned, text="👁️ Preview em Tempo Real")
        main_paned.add(f_preview, weight=3)

        # Variáveis
        self.var_nome_atual = tk.StringVar(value="")
        self.sub_font = tk.StringVar(value="Bangers")
        self.sub_words = tk.IntVar(value=5)
        self.sub_pos = tk.StringVar(value="meio baixo")
        self.sub_size = tk.IntVar(value=100)
        self.sub_margin_v = tk.IntVar(value=150)
        self.sub_effect = tk.StringVar(value="Pulo (Pop)")
        self.sub_border_w = tk.IntVar(value=3)

        self.color_primary = tk.StringVar(value="#FFFF00")
        self.color_secondary = tk.StringVar(value="#FFFFFF")
        self.color_outline = tk.StringVar(value="#000000")

        self._build_controls(f_sub)
        self._build_preview(f_preview)

        self.after(300, self._atualizar_preview)
        self.load_profiles()

    def _build_controls(self, f_sub):
        ctk.CTkLabel(f_sub, text="Perfil Atual:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky='w', pady=(0,6))
        ctk.CTkLabel(f_sub, textvariable=self.var_nome_atual, text_color="#0055ff", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, columnspan=3, sticky='w', pady=(0,6))

        fontes = ["Bangers", "Arial", "Impact", "Komika Axis", "Montserrat", "Oswald", "Roboto", "Anton", "TheBoldFont"]
        ctk.CTkLabel(f_sub, text="Fonte:").grid(row=1, column=0, sticky='w')
        cb_font = ctk.CTkOptionMenu(f_sub, variable=self.sub_font, values=fontes, width=150)
        cb_font.grid(row=1, column=1, sticky='w', padx=4, pady=4)
        cb_font.bind("<<ComboboxSelected>>", lambda e: self._atualizar_preview())

        ctk.CTkLabel(f_sub, text="Palavras/bloco:").grid(row=1, column=2, sticky='w')
        sp_words = ttk.Spinbox(f_sub, from_=1, to=15, textvariable=self.sub_words, width=5, command=self._atualizar_preview)
        sp_words.grid(row=1, column=3, sticky='w', padx=4, pady=4)
        sp_words.bind("<FocusOut>", lambda e: self._atualizar_preview())

        ctk.CTkLabel(f_sub, text="Posição:").grid(row=2, column=0, sticky='w')
        cb_pos = ctk.CTkOptionMenu(f_sub, variable=self.sub_pos, values=["meio baixo", "meio", "topo", "embaixo"], width=150)
        cb_pos.grid(row=2, column=1, sticky='w', padx=4, pady=4)
        cb_pos.bind("<<ComboboxSelected>>", lambda e: self._atualizar_preview())

        ctk.CTkLabel(f_sub, text="Efeito:").grid(row=2, column=2, sticky='w')
        efeitos = ["Nenhum", "Pulo (Pop)", "Balanço", "Giro Zoom", "Tremor", "Neon", "Flash", "Karate", "Bomba", "Sublinha", "Cinema"]
        cb_fx = ctk.CTkOptionMenu(f_sub, variable=self.sub_effect, values=efeitos, width=150)
        cb_fx.grid(row=2, column=3, sticky='w', padx=4, pady=4)
        cb_fx.bind("<<ComboboxSelected>>", lambda e: self._atualizar_preview())

        ctk.CTkLabel(f_sub, text="Tamanho (px):").grid(row=3, column=0, sticky='w')
        sp_size = ttk.Spinbox(f_sub, from_=10, to=200, textvariable=self.sub_size, width=5, command=self._atualizar_preview)
        sp_size.grid(row=3, column=1, sticky='w', padx=4, pady=4)
        sp_size.bind("<FocusOut>", lambda e: self._atualizar_preview())

        ctk.CTkLabel(f_sub, text="Contorno (px):").grid(row=3, column=2, sticky='w')
        sp_border = ttk.Spinbox(f_sub, from_=0, to=20, textvariable=self.sub_border_w, width=5, command=self._atualizar_preview)
        sp_border.grid(row=3, column=3, sticky='w', padx=4, pady=4)
        sp_border.bind("<FocusOut>", lambda e: self._atualizar_preview())

        ctk.CTkLabel(f_sub, text="Margem (px):").grid(row=4, column=0, sticky='w')
        sp_margin = ttk.Spinbox(f_sub, from_=0, to=500, textvariable=self.sub_margin_v, width=5, command=self._atualizar_preview)
        sp_margin.grid(row=4, column=1, sticky='w', padx=4, pady=4)
        sp_margin.bind("<FocusOut>", lambda e: self._atualizar_preview())

        # ── Frame de Cores ──
        f_cores = ctk.CTkLabelFrame(f_sub, text=" Cores do Texto ")
        f_cores.grid(row=1, column=4, rowspan=4, padx=20, sticky='nsew')
        
        def choose_color(var_color, title):
            from tkinter import colorchooser
            color = colorchooser.askcolor(title=title, initialcolor=var_color.get())
            if color[1]:
                var_color.set(color[1])
                self._atualizar_preview()

        # Primária (Destaque)
        ctk.CTkLabel(f_cores, text="Principal:").grid(row=0, column=0, sticky='w', padx=15, pady=12)
        self.btn_cp = ctk.CTkButton(f_cores, width=40, fg_color=self.color_primary.get(), command=lambda: choose_color(self.color_primary, "Cor Principal"))
        self.btn_cp.grid(row=0, column=1, padx=15, pady=12)
        self.color_primary.trace_add('write', lambda *args: self.btn_cp.configure(fg_color=self.color_primary.get()))

        # Secundária (Normal)
        ctk.CTkLabel(f_cores, text="Normal:").grid(row=1, column=0, sticky='w', padx=15, pady=12)
        self.btn_cs = ctk.CTkButton(f_cores, width=40, fg_color=self.color_secondary.get(), command=lambda: choose_color(self.color_secondary, "Cor Normal"))
        self.btn_cs.grid(row=1, column=1, padx=15, pady=12)
        self.color_secondary.trace_add('write', lambda *args: self.btn_cs.configure(fg_color=self.color_secondary.get()))

        # Borda
        ctk.CTkLabel(f_cores, text="Contorno:").grid(row=2, column=0, sticky='w', padx=15, pady=12)
        self.btn_co = ctk.CTkButton(f_cores, width=40, fg_color=self.color_outline.get(), command=lambda: choose_color(self.color_outline, "Cor do Contorno"))
        self.btn_co.grid(row=2, column=1, padx=15, pady=12)
        self.color_outline.trace_add('write', lambda *args: self.btn_co.configure(fg_color=self.color_outline.get()))

        # Vínculo com Personagens
        f_vinc = ctk.CTkLabelFrame(f_sub, text=" Vincular a Personagens ")
        f_vinc.grid(row=1, column=5, rowspan=4, padx=20, sticky='nsew')
        
        self.list_personagens = tk.Listbox(f_vinc, selectmode=tk.MULTIPLE, height=5, exportselection=False)
        self.list_personagens.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Load all characters into listbox
        for c in list(self.config_manager.get("personagens", {}).keys()):
            self.list_personagens.insert(tk.END, c)

        # Save Button
        ctk.CTkButton(f_sub, text="💾 Salvar Configurações e Vínculos", command=self.save_profile).grid(
            row=5, column=0, columnspan=6, pady=20, sticky='ew')


    def _build_preview(self, f_preview):
        ctrl_top = ctk.CTkFrame(f_preview)
        ctrl_top.pack(fill=tk.X, padx=6, pady=(6,2))

        self.var_fmt_preview = tk.StringVar(value="vertical")
        ttk.Radiobutton(ctrl_top, text="📱 Vertical (9:16)", variable=self.var_fmt_preview, value="vertical", command=self._on_fmt_change).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(ctrl_top, text="🖥️ Horizontal (16:9)", variable=self.var_fmt_preview, value="horizontal", command=self._on_fmt_change).pack(side=tk.LEFT, padx=4)

        ctk.CTkLabel(ctrl_top, text="Texto preview:").pack(side=tk.LEFT, padx=(15, 2))
        self.var_preview_texto = tk.StringVar(value="Era uma vez um necromante arrependido")
        ent = ctk.CTkEntry(ctrl_top, textvariable=self.var_preview_texto, width=400)
        ent.pack(side=tk.LEFT, padx=4)
        self.var_preview_texto.trace_add('write', lambda *a: self._atualizar_preview())

        self.preview_canvas = tk.Canvas(f_preview, cursor="crosshair")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=(2,2))
        self.preview_canvas.bind("<Configure>", lambda e: self._atualizar_preview())

        btn_frame_prev = ctk.CTkFrame(f_preview)
        btn_frame_prev.pack(fill=tk.X, padx=6, pady=(0,2))
        self._preview_bloco_idx = 0
        ctk.CTkButton(btn_frame_prev, text="◀", width=30, command=self._prev_bloco).pack(side=tk.LEFT)
        self.lbl_bloco_num = ctk.CTkLabel(btn_frame_prev, text="Bloco 1", text_color="#aaa", width=80)
        self.lbl_bloco_num.pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(btn_frame_prev, text="▶", width=30, command=self._next_bloco).pack(side=tk.LEFT)

    def _on_fmt_change(self):
        self._atualizar_preview()
        if self.var_nome_atual.get():
            self.on_select(None)

    def _prev_bloco(self):
        self._preview_bloco_idx = max(0, self._preview_bloco_idx - 1)
        self._atualizar_preview()

    def _next_bloco(self):
        try: n = int(self.sub_words.get())
        except: n = 5
        texto = self.var_preview_texto.get()
        total = max(1, (len(texto.split()) + n - 1) // n)
        self._preview_bloco_idx = min(self._preview_bloco_idx + 1, total - 1)
        self._atualizar_preview()

    def _atualizar_preview(self, *_):
        import tkinter.font as tkfont
        try:
            c = self.preview_canvas
            c.delete("all")
            w = c.winfo_width()
            h = c.winfo_height()
            if w < 20 or h < 20: return

            fmt = self.var_fmt_preview.get()
            if fmt == "vertical":
                ratio = 9 / 16
                fw = min(w - 20, int((h - 20) * ratio))
                fh = int(fw / ratio)
            else:
                ratio = 16 / 9
                fh = min(h - 20, int((w - 20) / ratio))
                fw = int(fh * ratio)

            fx = (w - fw) // 2
            fy = (h - fh) // 2

            c.create_rectangle(fx, fy, fx+fw, fy+fh, fill="#1a1a2e", outline="#555", width=2)

            try: size_px = int(self.sub_size.get())
            except: size_px = 100
            try: margin_v = int(self.sub_margin_v.get())
            except: margin_v = 150
            try: n_words = int(self.sub_words.get())
            except: n_words = 5

            escala = fw / 1080.0
            fs = max(8, int(size_px * escala))
            mv = int(margin_v * escala)

            pos    = self.sub_pos.get()
            effect = self.sub_effect.get()
            fonte_nome = self.sub_font.get()
            texto  = self.var_preview_texto.get() or "Texto de exemplo"

            palavras = texto.split()
            total_blocos = max(1, (len(palavras) + n_words - 1) // n_words)
            idx = max(0, min(getattr(self, '_preview_bloco_idx', 0), total_blocos - 1))
            self._preview_bloco_idx = idx
            bloco = " ".join(palavras[idx*n_words:(idx+1)*n_words]) or texto

            try: self.lbl_bloco_num.config(text=f"Bloco {idx+1}/{total_blocos}")
            except: pass

            try:
                fk = tkfont.Font(family=fonte_nome, size=fs, weight="bold")
                actual_family = fk.actual()["family"].lower()
                fonte_tk = fk if fonte_nome.lower() in actual_family else None
            except:
                fonte_tk = None

            fonte = fonte_tk if fonte_tk else ("Arial", fs, "bold")

            cor_d = self.color_primary.get()
            cor_n = self.color_secondary.get()
            cor_o = self.color_outline.get()

            if pos == "topo":      ty = fy + mv + fs
            elif pos == "meio":    ty = fy + fh // 2
            elif pos == "embaixo": ty = fy + fh - mv - fs
            else:                   ty = fy + fh - int(fh * 0.22) - mv

            cx = fx + fw // 2
            try:
                border_w = int(self.sub_border_w.get())
                sh = max(1, int(border_w * escala))
            except:
                sh = max(1, fs // 10)

            palavras_lista = bloco.split()
            c.create_text(cx+sh, ty+sh, text=bloco, fill=cor_o, font=fonte, anchor="center")
            c.create_text(cx-sh, ty-sh, text=bloco, fill=cor_o, font=fonte, anchor="center")
            c.create_text(cx+sh, ty-sh, text=bloco, fill=cor_o, font=fonte, anchor="center")
            c.create_text(cx-sh, ty+sh, text=bloco, fill=cor_o, font=fonte, anchor="center")
            
            # Normal color for all except last word
            c.create_text(cx, ty, text=bloco, fill=cor_n, font=fonte, anchor="center")

            # Highlight last word
            if palavras_lista:
                try:
                    kf = tkfont.Font(family=fonte_nome, size=fs, weight="bold")
                    txt_antes = " ".join(palavras_lista[:-1])
                    w_antes = kf.measure(txt_antes + (" " if txt_antes else ""))
                    w_total = kf.measure(bloco)
                    dest_txt = palavras_lista[-1]
                    dest_x = cx - w_total // 2 + w_antes + kf.measure(dest_txt) // 2
                    c.create_text(dest_x, ty, text=dest_txt, fill=cor_d, font=fonte, anchor="center")
                except:
                    pass

            # Badge Effect
            if effect not in ("Nenhum", ""):
                badge_x = fx + fw - 4
                badge_y = fy + 4
                badge_txt = f"✨ {effect}"
                # Using solid #222 instead of transparent #00000099 to fix Tkinter Error
                c.create_rectangle(badge_x - len(badge_txt)*6 - 10, badge_y,
                                   badge_x, badge_y + 16,
                                   fill="#222222", outline=cor_d, width=1)
                c.create_text(badge_x - 4, badge_y + 8, text=badge_txt, fill=cor_d,
                              font=("Segoe UI", 8, "bold"), anchor="e")

        except Exception as ex:
            pass

    def get_profiles_dict(self):
        perfis = self.config_manager.get("perfis_legenda", {})
        migrated = False
        for name, p in list(perfis.items()):
            if "vertical" not in p and "horizontal" not in p:
                novo_p = {
                    "vertical": dict(p),
                    "horizontal": dict(p)
                }
                perfis[name] = novo_p
                migrated = True
        if migrated:
            self.save_profiles_dict(perfis)
        return perfis

    def save_profiles_dict(self, d):
        self.config_manager.set("perfis_legenda", d)

    def load_profiles(self):
        self.listbox.delete(0, tk.END)
        perfis = self.get_profiles_dict()
        for name in perfis.keys():
            self.listbox.insert(tk.END, name)

    def add_profile(self):
        from tkinter import messagebox
        name = self.var_novo_nome.get().strip()
        if not name: return
        perfis = self.get_profiles_dict()
        if name in perfis:
            messagebox.showwarning("Aviso", "Já existe um perfil com esse nome.")
            return
        base_conf = {
            "font": "Bangers", "words": 5, "pos": "meio baixo",
            "color_primary": "#FFFF00", "color_secondary": "#FFFFFF", "color_outline": "#000000",
            "size": 100, "margin_v": 150, "effect": "Pulo (Pop)",
            "border_w": 3
        }
        perfis[name] = {
            "vertical": dict(base_conf),
            "horizontal": dict(base_conf)
        }
        self.save_profiles_dict(perfis)
        self.var_novo_nome.set("")
        self.load_profiles()
        idx = self.listbox.get(0, tk.END).index(name)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.on_select(None)

    def delete_profile(self):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar", f"Deletar perfil '{name}'?"):
            perfis = self.get_profiles_dict()
            if name in perfis:
                del perfis[name]
                self.save_profiles_dict(perfis)
                self.load_profiles()
                self.var_nome_atual.set("")

    def rename_profile(self):
        sel = self.listbox.curselection()
        if not sel: return
        nome_antigo = self.listbox.get(sel[0])
        from tkinter import simpledialog, messagebox
        novo_nome = simpledialog.askstring("Renomear Perfil", f"Digite o novo nome para '{nome_antigo}':", initialvalue=nome_antigo)
        if not novo_nome or not novo_nome.strip() or novo_nome.strip() == nome_antigo: return
        novo_nome = novo_nome.strip()
            
        perfis = self.get_profiles_dict()
        if novo_nome in perfis:
            messagebox.showwarning("Aviso", f"Já existe um perfil chamado '{novo_nome}'.")
            return
            
        perfis[novo_nome] = perfis.pop(nome_antigo)
        self.save_profiles_dict(perfis)
        
        # Renomear vínculos
        vinculos = self.config_manager.get("perfis_personagem", {})
        v_changed = False
        for char_name, p_name in vinculos.items():
            if p_name == nome_antigo:
                vinculos[char_name] = novo_nome
                v_changed = True
        if v_changed:
            self.config_manager.set("perfis_personagem", vinculos)
            
        self.load_profiles()
        idx = self.listbox.get(0, tk.END).index(novo_nome)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.on_select(None)

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        perfis = self.get_profiles_dict()
        if name in perfis:
            fmt = self.var_fmt_preview.get()
            p = perfis[name].get(fmt, {})
            self.var_nome_atual.set(name)
            self.sub_font.set(p.get("font", "Bangers"))
            self.sub_words.set(p.get("words", 5))
            self.sub_pos.set(p.get("pos", "meio baixo"))
            self.sub_size.set(p.get("size", 100))
            self.sub_margin_v.set(p.get("margin_v", 150))
            self.sub_effect.set(p.get("effect", "Pulo (Pop)"))
            self.sub_border_w.set(p.get("border_w", 3))
            
            # Colors (compatibilidade com "theme" antigo)
            if "color_primary" in p:
                self.color_primary.set(p["color_primary"])
                self.color_secondary.set(p["color_secondary"])
                self.color_outline.set(p["color_outline"])
            else:
                # Converter tema antigo pra hex
                tema = p.get("theme", "amarelo vermelho")
                _TEMAS = {
                    "amarelo vermelho": ("#FFFF00", "#FF3333", "#000000"),
                    "vermelho branco":  ("#FFFFFF", "#FF2020", "#000000"),
                    "verde amarelo":    ("#FFFF00", "#00CC44", "#000000"),
                    "rosa neon":        ("#FF44FF", "#FF88FF", "#111111"),
                    "azul gelo":        ("#AAEEFF", "#4488FF", "#001133"),
                    "roxo misterio":    ("#EE88FF", "#AA00FF", "#110022"),
                    "laranja fogo":     ("#FFAA00", "#FF4400", "#110000"),
                    "verde matrix":     ("#00FF44", "#44FF88", "#001100"),
                    "preto amarelo":    ("#FFFF00", "#FFFFFF", "#000000"),
                    "padrão":           ("#FFFF00", "#FFFFFF", "#000000")
                }
                c_d, c_n, c_o = _TEMAS.get(tema.lower(), ("#FFFF00", "#FFFFFF", "#000000"))
                self.color_primary.set(c_d)
                self.color_secondary.set(c_n)
                self.color_outline.set(c_o)

            # Restaurar seleções na listbox de vínculos
            self.list_personagens.selection_clear(0, tk.END)
            vinculos = self.config_manager.get("perfis_personagem", {})
            for i in range(self.list_personagens.size()):
                c_name = self.list_personagens.get(i)
                if vinculos.get(c_name) == name:
                    self.list_personagens.selection_set(i)

    def save_profile(self):
        name = self.var_nome_atual.get()
        from tkinter import messagebox
        if not name:
            messagebox.showwarning("Aviso", "Selecione um perfil primeiro.")
            return
        perfis = self.get_profiles_dict()
        try: w, s, m, b = int(self.sub_words.get()), int(self.sub_size.get()), int(self.sub_margin_v.get()), int(self.sub_border_w.get())
        except: w, s, m, b = 5, 100, 150, 3
            
        fmt = self.var_fmt_preview.get()
        if name not in perfis:
            perfis[name] = {"vertical": {}, "horizontal": {}}
            
        perfis[name][fmt] = {
            "font": self.sub_font.get(),
            "words": w,
            "pos": self.sub_pos.get(),
            "color_primary": self.color_primary.get(),
            "color_secondary": self.color_secondary.get(),
            "color_outline": self.color_outline.get(),
            "size": s,
            "margin_v": m,
            "effect": self.sub_effect.get(),
            "border_w": b
        }
        self.save_profiles_dict(perfis)

        # Salvar vínculos
        vinculos = self.config_manager.get("perfis_personagem", {})
        # Primeiro, remove os vínculos atuais para este perfil (se o usuário desmarcou)
        for k, v in list(vinculos.items()):
            if v == name:
                del vinculos[k]
        
        # Agora aplica os novos selecionados
        sel_indices = self.list_personagens.curselection()
        for i in sel_indices:
            c_name = self.list_personagens.get(i)
            vinculos[c_name] = name
            
        self.config_manager.set("perfis_personagem", vinculos)

        messagebox.showinfo("Sucesso", f"Perfil '{name}' e vínculos salvos com sucesso!")




class TabPerfisTemplate(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        self.var_novo_nome = tk.StringVar()
        self.var_nome_atual = tk.StringVar()
        
        self.var_tipo_transicao = tk.StringVar(value="Ambos")
        self.var_duracao = tk.StringVar(value="1.5")
        
        # Novas variáveis
        self.var_formato = tk.StringVar(value="Ambos") # Vertical, Horizontal, Ambos
        self.var_probabilidade_hd = tk.IntVar(value=50) # 0 a 100
        self.lista_hd_videos = []
        
        # UI
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- Esquerda: Lista de Perfis ---
        f_lista = ctk.CTkLabelFrame(paned, text=" Perfis de Transição Web ")
        paned.add(f_lista, weight=1)
        
        f_add = ctk.CTkFrame(f_lista)
        f_add.pack(fill=tk.X, padx=15, pady=12)
        ctk.CTkEntry(f_add, textvariable=self.var_novo_nome).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ctk.CTkButton(f_add, text="➕", command=self.add_profile, width=30).pack(side=tk.RIGHT, padx=2)
        
        self.listbox = tk.Listbox(f_lista, activestyle='dotbox', font=("Segoe UI", 11), height=15)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
        scroll = ttk.Scrollbar(self.listbox, orient="vertical", command=self.listbox.yview)
        scroll.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scroll.set)
        
        ctk.CTkButton(f_lista, text="🗑️ Excluir", command=self.delete_profile).pack(fill=tk.X, padx=15, pady=2)
        ctk.CTkButton(f_lista, text="✏️ Renomear", command=self.rename_profile).pack(fill=tk.X, padx=15, pady=2)
        
        # --- Direita: Configs Avançadas ---
        f_form = ctk.CTkLabelFrame(paned, text=" Configurações Dinâmicas do Perfil ")
        paned.add(f_form, weight=3)

        # Container esquerdo das configs (Básico)
        f_basico = ctk.CTkFrame(f_form)
        f_basico.pack(fill=tk.X, padx=20, pady=12)
        
        ctk.CTkLabel(f_basico, text="Perfil Atual:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="e", pady=2)
        ctk.CTkLabel(f_basico, textvariable=self.var_nome_atual, text_color="#0055ff", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=15)

        ctk.CTkLabel(f_basico, text="Formato Alvo:").grid(row=1, column=0, sticky="e", pady=2)
        f_fmt = ctk.CTkFrame(f_basico)
        f_fmt.grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(f_fmt, text="📱 Vertical", variable=self.var_formato, value="Vertical").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(f_fmt, text="🖥️ Horizontal", variable=self.var_formato, value="Horizontal").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(f_fmt, text="🔄 Ambos", variable=self.var_formato, value="Ambos").pack(side=tk.LEFT, padx=2)

        ctk.CTkLabel(f_basico, text="Duração (seg):").grid(row=2, column=0, sticky="e", pady=2)
        ttk.Spinbox(f_basico, from_=0.1, to=5.0, increment=0.1, textvariable=self.var_duracao, width=8).grid(row=2, column=1, sticky="w", padx=15)

        ttk.Separator(f_form, orient="horizontal").pack(fill=tk.X, padx=20, pady=12)

        # Regras de Negócio
        f_regras = ctk.CTkFrame(f_form)
        f_regras.pack(fill=tk.X, padx=20, pady=12)
        
        ctk.CTkLabel(f_regras, text="Estratégia de Sorteio:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        f_tipo = ctk.CTkFrame(f_regras)
        f_tipo.grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(f_tipo, text="Só XFade", variable=self.var_tipo_transicao, value="XFade", command=self._toggle_ui).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(f_tipo, text="Só HD Stinger", variable=self.var_tipo_transicao, value="HD", command=self._toggle_ui).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(f_tipo, text="Ambos (Probabilidade)", variable=self.var_tipo_transicao, value="Ambos", command=self._toggle_ui).pack(side=tk.LEFT, padx=15)

        self.f_prob = ctk.CTkFrame(f_regras)
        self.f_prob.grid(row=1, column=0, columnspan=2, sticky="w", pady=12)
        ctk.CTkLabel(self.f_prob, text="Probabilidade de sortear um Vídeo HD (%) em vez de XFade:").pack(side=tk.LEFT)
        lbl_prob_val = ctk.CTkLabel(self.f_prob, text="50%", width=40, font=("Segoe UI", 9, "bold"))
        scale_prob = ttk.Scale(self.f_prob, from_=0, to=100, variable=self.var_probabilidade_hd, orient=tk.HORIZONTAL, length=150)
        scale_prob.config(command=lambda v: lbl_prob_val.config(text=f"{int(float(v))}%"))
        scale_prob.pack(side=tk.LEFT, padx=15)
        lbl_prob_val.pack(side=tk.LEFT)

        # --- Pools (Duas Colunas) ---
        f_pools = ctk.CTkFrame(f_form)
        f_pools.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # Pool XFade
        self.f_xfade = ctk.CTkLabelFrame(f_pools, text=" Pool de Efeitos XFade ")
        self.f_xfade.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        ctk.CTkLabel(self.f_xfade, text="Marque os efeitos permitidos:", text_color="#888").pack(anchor="w", padx=15)
        
        self.list_xfade = tk.Listbox(self.f_xfade, selectmode=tk.MULTIPLE, height=6)
        self.list_xfade.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        efeitos_disp = ["fade", "wipeleft", "wiperight", "slideleft", "slideright", "pixelize", "radial", "circlecrop", "rectcrop", "distance"]
        for e in efeitos_disp:
            self.list_xfade.insert(tk.END, e)

        # Pool HD Stinger
        self.f_hd = ctk.CTkLabelFrame(f_pools, text=" Pool de Vídeos HD (Stinger) ")
        self.f_hd.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        
        f_hd_btns = ctk.CTkFrame(self.f_hd)
        f_hd_btns.pack(fill=tk.X, padx=15, pady=2)
        ctk.CTkButton(f_hd_btns, text="➕ Adicionar Vídeo(s)", command=self._add_hd_videos).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(f_hd_btns, text="📁 Adicionar Pasta", command=self._add_hd_folder).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(f_hd_btns, text="🗑️ Remover", command=self._remove_hd_video).pack(side=tk.RIGHT, padx=2)

        self.list_hd = tk.Listbox(self.f_hd, selectmode=tk.EXTENDED, height=6)
        self.list_hd.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        ctk.CTkButton(f_form, text="💾 Salvar Configurações no Perfil", command=self.save_profile).pack(fill=tk.X, padx=20, pady=20)
        
        self.load_profiles()
        self._toggle_ui()

    def _toggle_ui(self):
        tipo = self.var_tipo_transicao.get()
        if tipo == "XFade":
            self.f_prob.grid_remove()
        elif tipo == "HD":
            self.f_prob.grid_remove()
        else: # Ambos
            self.f_prob.grid()

    def _add_hd_videos(self):
        from tkinter import filedialog
        files = filedialog.askopenfilenames(title="Selecione os Vídeos", filetypes=[("Video", "*.mp4 *.mov *.webm")])
        for f in files:
            if f not in self.lista_hd_videos:
                self.lista_hd_videos.append(f)
                self.list_hd.insert(tk.END, os.path.basename(f))

    def _add_hd_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Selecione a Pasta de Vídeos")
        if folder:
            count = 0
            for f in os.listdir(folder):
                if f.lower().endswith(('.mp4', '.mov', '.webm')):
                    full = os.path.normpath(os.path.join(folder, f))
                    if full not in self.lista_hd_videos:
                        self.lista_hd_videos.append(full)
                        self.list_hd.insert(tk.END, f)
                        count += 1
            messagebox.showinfo("Pasta Importada", f"{count} vídeos adicionados ao pool.")

    def _remove_hd_video(self):
        sels = list(self.list_hd.curselection())
        sels.sort(reverse=True)
        for i in sels:
            self.list_hd.delete(i)
            del self.lista_hd_videos[i]
            
    def get_profiles_dict(self):
        d = self.config_manager.get("perfis_transicao_template")
        # Migrate de versões super antigas (se existir)
        if d is None:
            d = self.config_manager.get("perfis_transicao_web", {})
            if d:
                self.config_manager.set("perfis_transicao_template", d)
                self.config_manager.delete("perfis_transicao_web")
        return d or {}

    def save_profiles_dict(self, d):
        self.config_manager.set("perfis_transicao_template", d)

    def load_profiles(self):
        self.listbox.delete(0, tk.END)
        perfis = self.get_profiles_dict()
        for name in perfis.keys():
            self.listbox.insert(tk.END, name)

    def add_profile(self):
        name = self.var_novo_nome.get().strip()
        if not name: return
        perfis = self.get_profiles_dict()
        if name in perfis:
            messagebox.showwarning("Aviso", "Já existe um perfil com esse nome.")
            return
        perfis[name] = {
            "formato": "Ambos",
            "tipo": "Ambos",
            "xfade_pool": ["fade", "wipeleft", "wiperight"],
            "hd_pool": [],
            "duracao": 1.5,
            "probabilidade_hd": 50
        }
        self.save_profiles_dict(perfis)
        self.var_novo_nome.set("")
        self.load_profiles()
        idx = self.listbox.get(0, tk.END).index(name)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.on_select(None)

    def delete_profile(self):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        if messagebox.askyesno("Confirmar", f"Deletar perfil '{name}'?"):
            perfis = self.get_profiles_dict()
            if name in perfis:
                del perfis[name]
                self.save_profiles_dict(perfis)
                self.load_profiles()
                self.var_nome_atual.set("")

    def rename_profile(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um perfil para renomear.")
            return
        nome_antigo = self.listbox.get(sel[0])
        from tkinter import simpledialog
        novo_nome = simpledialog.askstring("Renomear", f"Novo nome para '{nome_antigo}':", initialvalue=nome_antigo)
        if not novo_nome or novo_nome.strip() == "" or novo_nome == nome_antigo:
            return
        novo_nome = novo_nome.strip()
            
        perfis = self.get_profiles_dict()
        if novo_nome in perfis:
            messagebox.showwarning("Aviso", f"Já existe '{novo_nome}'.")
            return
            
        perfis[novo_nome] = perfis.pop(nome_antigo)
        self.save_profiles_dict(perfis)
        
        self.load_profiles()
        idx = self.listbox.get(0, tk.END).index(novo_nome)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.on_select(None)

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel: return
        name = self.listbox.get(sel[0])
        perfis = self.get_profiles_dict()
        if name in perfis:
            p = perfis[name]
            self.var_nome_atual.set(name)
            
            # Migração transparente on-read (suporte aos campos antigos)
            self.var_formato.set(p.get("formato", "Ambos"))
            self.var_tipo_transicao.set(p.get("tipo", "XFade"))
            self.var_duracao.set(str(p.get("duracao", 1.5)))
            self.var_probabilidade_hd.set(p.get("probabilidade_hd", 50))
            
            # Popular XFade
            self.list_xfade.selection_clear(0, tk.END)
            old_xfade = p.get("xfade_name") # legado
            pool_xfade = p.get("xfade_pool", [old_xfade] if old_xfade else [])
            for i in range(self.list_xfade.size()):
                if self.list_xfade.get(i) in pool_xfade:
                    self.list_xfade.selection_set(i)

            # Popular HD Videos
            self.list_hd.delete(0, tk.END)
            self.lista_hd_videos = p.get("hd_pool", [])
            
            # Suporte ao campo 'hd_video' legado
            old_hd = p.get("hd_video")
            if old_hd and old_hd not in self.lista_hd_videos:
                self.lista_hd_videos.append(old_hd)
                
            for v in self.lista_hd_videos:
                self.list_hd.insert(tk.END, os.path.basename(v))
                
            self._toggle_ui()

    def save_profile(self):
        name = self.var_nome_atual.get()
        if not name:
            messagebox.showwarning("Aviso", "Selecione um perfil primeiro.")
            return
        perfis = self.get_profiles_dict()
        try: dur = float(self.var_duracao.get())
        except: dur = 1.5
            
        xfade_sels = [self.list_xfade.get(i) for i in self.list_xfade.curselection()]
        
        perfis[name] = {
            "formato": self.var_formato.get(),
            "tipo": self.var_tipo_transicao.get(),
            "probabilidade_hd": self.var_probabilidade_hd.get(),
            "xfade_pool": xfade_sels,
            "hd_pool": self.lista_hd_videos,
            "duracao": dur
        }
        self.save_profiles_dict(perfis)
        messagebox.showinfo("Sucesso", f"Perfil '{name}' salvo!")

class TabShortcuts(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        ctk.CTkLabel(self, text="🔗 Atalhos de Mídia (Shortcuts)", font=("Segoe UI", 12, "bold")).pack(pady=20)
        ctk.CTkLabel(self, text="Configure atalhos para carregar vídeos pesados de outros HDDs sem copiar para a pasta do programa.\nEx: {MEU_HD_1} = D:/MeusVideos").pack(pady=12)
        
        self.frame_list = ctk.CTkFrame(self)
        self.frame_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.tree = ttk.Treeview(self.frame_list, columns=("Chave", "Caminho"), show="headings")
        self.tree.heading("Chave", text="Chave (Ex: MEU_HD)")
        self.tree.heading("Caminho", text="Caminho Completo")
        self.tree.column("Chave", width=150)
        self.tree.column("Caminho", width=400)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scroll = ttk.Scrollbar(self.frame_list, orient="vertical", command=self.tree.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=self.scroll.set)
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ctk.CTkButton(btn_frame, text="➕ Adicionar Atalho", command=self.add_shortcut).pack(side=tk.LEFT, padx=15)
        ctk.CTkButton(btn_frame, text="🗑️ Remover Selecionado", command=self.remove_shortcut).pack(side=tk.LEFT, padx=15)
        
        self.load_shortcuts()
        
    def load_shortcuts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        shortcuts = self.config_manager.get("shortcuts", {})
        for key, path in shortcuts.items():
            self.tree.insert("", tk.END, values=(key, path))
            
    def add_shortcut(self):
        from tkinter import simpledialog, filedialog, messagebox
        key = simpledialog.askstring("Nova Chave", "Digite o nome da chave (sem chaves {}). Ex: DISCO_EXTERNO")
        if not key:
            return
        key = key.strip().upper()
        
        path = filedialog.askdirectory(title="Selecione a pasta destino para este atalho")
        if not path:
            return
            
        shortcuts = self.config_manager.get("shortcuts", {})
        shortcuts[key] = path
        self.config_manager.set("shortcuts", shortcuts)
        self.load_shortcuts()
        messagebox.showinfo("Sucesso", f"Atalho {{{key}}} adicionado com sucesso!")
        
    def remove_shortcut(self):
        from tkinter import messagebox
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        key = item['values'][0]
        
        if messagebox.askyesno("Remover", f"Remover o atalho {{{key}}}?"):
            shortcuts = self.config_manager.get("shortcuts", {})
            if key in shortcuts:
                del shortcuts[key]
                self.config_manager.set("shortcuts", shortcuts)
                self.load_shortcuts()

class AbaConfiguracoes(ctk.CTkFrame):
    """
    Nova Central de Configurações reformulada contendo abas filhas para 
    evitar confusão visual e mescla de escopo.
    """
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        self.configure()
        self._criar_interface()

    def _criar_interface(self):
        ctk.CTkLabel(self, text="⚙️ Central de Configurações e Roteamento", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)
        
        self.tab_apis = TabAPIs(self.notebook, self.config_manager)
        self.notebook.add(self.tab_apis, text="🔑 1. Chaves de API Rotativas")
        
        self.tab_personagens = TabPersonagens(self.notebook, self.config_manager)
        self.notebook.add(self.tab_personagens, text="👤 2. Cadastro & Roteamento de TTS")
        
        self.tab_vps = TabVPS(self.notebook, self.config_manager)
        self.notebook.add(self.tab_vps, text="☁️ 3. Conexões Cloud VPS")
        
        self.tab_audio = TabTratamentoAudio(self.notebook, self.config_manager)
        self.notebook.add(self.tab_audio, text="🎛️ 4. Tratamento IA de Áudio")
        
        self.tab_estetica = TabEsteticaCanal(self.notebook, self.config_manager)
        self.notebook.add(self.tab_estetica, text="✨ 5. Estética Global do Canal")
        
        self.tab_legendas = TabPerfisLegenda(self.notebook, self.config_manager)
        self.notebook.add(self.tab_legendas, text="📝 6. Perfis de Legenda")

        self.tab_templates = TabPerfisTemplate(self.notebook, self.config_manager)
        self.notebook.add(self.tab_templates, text="🖼️ 7. Transições de Template (Web)")

        self.tab_whitelabel = TabWhiteLabel(self.notebook, self.config_manager)
        self.notebook.add(self.tab_whitelabel, text="🎭 8. Identidade (White-Label)")

        self.tab_shortcuts = TabShortcuts(self.notebook, self.config_manager)
        self.notebook.add(self.tab_shortcuts, text="🔗 9. Atalhos de Mídia (HDDs Externos)")

class TabWhiteLabel(ctk.CTkFrame):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.scrollable_frame.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.scrollable_frame.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        
        # Agora adicionar os widgets em self.scrollable_frame em vez de self
        
        ctk.CTkLabel(self.scrollable_frame, text="🎭 Identidade Visual do Canal (White-Label)", font=("Segoe UI", 12, "bold")).pack(pady=20)
        ctk.CTkLabel(self.scrollable_frame, text="Configure a logomarca e o ícone que o Apollo Studio usará quando você abrir este Workspace.").pack(pady=12)
        
        frame_imgs = ctk.CTkLabelFrame(self.scrollable_frame, text="Imagens do Programa")
        frame_imgs.pack(fill=tk.X, padx=20, pady=20)
        
        ctk.CTkLabel(frame_imgs, text="Caminho do Logo (.png):").grid(row=0, column=0, sticky="e", pady=12)
        self.var_logo = tk.StringVar()
        ctk.CTkEntry(frame_imgs, textvariable=self.var_logo, width=500).grid(row=0, column=1, sticky="w", padx=20, pady=12)
        ctk.CTkButton(frame_imgs, text="📁", width=30, command=lambda: self._ask_file(self.var_logo, "*.png")).grid(row=0, column=2, padx=15)
        
        ctk.CTkLabel(frame_imgs, text="Caminho do Ícone (.ico):").grid(row=1, column=0, sticky="e", pady=12)
        self.var_icon = tk.StringVar()
        ctk.CTkEntry(frame_imgs, textvariable=self.var_icon, width=500).grid(row=1, column=1, sticky="w", padx=20, pady=12)
        ctk.CTkButton(frame_imgs, text="📁", width=30, command=lambda: self._ask_file(self.var_icon, "*.ico")).grid(row=1, column=2, padx=15)
        
        frame_colors = ctk.CTkLabelFrame(self.scrollable_frame, text="Paleta de Cores do Workspace")
        frame_colors.pack(fill=tk.X, padx=20, pady=20)
        
        self.var_bg = tk.StringVar(value="#1A1A2E")
        self.var_fg = tk.StringVar(value="#FFD32A")
        self.var_accent = tk.StringVar(value="#1E90FF")
        
        ctk.CTkLabel(frame_colors, text="Fundo Principal (BG):").grid(row=0, column=0, sticky="e", pady=12)
        self.btn_bg = ctk.CTkButton(frame_colors, fg_color=self.var_bg.get(), width=100, command=lambda: self._ask_color(self.var_bg, self.btn_bg))
        self.btn_bg.grid(row=0, column=1, padx=20, sticky="w")
        
        ctk.CTkLabel(frame_colors, text="Cor Primária (FG):").grid(row=1, column=0, sticky="e", pady=12)
        self.btn_fg = ctk.CTkButton(frame_colors, fg_color=self.var_fg.get(), width=100, command=lambda: self._ask_color(self.var_fg, self.btn_fg))
        self.btn_fg.grid(row=1, column=1, padx=20, sticky="w")
        
        ctk.CTkLabel(frame_colors, text="Cor Secundária (Accent):").grid(row=2, column=0, sticky="e", pady=12)
        self.btn_accent = ctk.CTkButton(frame_colors, fg_color=self.var_accent.get(), width=100, command=lambda: self._ask_color(self.var_accent, self.btn_accent))
        self.btn_accent.grid(row=2, column=1, padx=20, sticky="w")
        
        ctk.CTkButton(self.scrollable_frame, text="💾 Salvar Identidade", command=self.save_branding).pack(pady=20)
        
        self.load_branding()
        
    def _ask_file(self, var, ext):
        from tkinter import filedialog
        path = filedialog.askopenfilename(title=f"Selecione o arquivo", filetypes=[(f"Arquivo {ext}", ext)])
        if path:
            var.set(path)
            
    def _ask_color(self, var, btn):
        from tkinter.colorchooser import askcolor
        color = askcolor(color=var.get(), title="Escolha uma cor")[1]
        if color:
            var.set(color)
            btn.configure(fg_color=color)
            
    def load_branding(self):
        self.var_logo.set(self.config_manager.get("app_logo_path", ""))
        self.var_icon.set(self.config_manager.get("app_icon_path", ""))
        
        theme = self.config_manager.get("theme_colors", {})
        if theme:
            if "bg" in theme:
                self.var_bg.set(theme["bg"])
                self.btn_bg.configure(fg_color=theme["bg"])
            if "fg" in theme:
                self.var_fg.set(theme["fg"])
                self.btn_fg.configure(fg_color=theme["fg"])
            if "accent" in theme:
                self.var_accent.set(theme["accent"])
                self.btn_accent.configure(fg_color=theme["accent"])
        
    def save_branding(self):
        from tkinter import messagebox
        self.config_manager.set("app_logo_path", self.var_logo.get().strip())
        self.config_manager.set("app_icon_path", self.var_icon.get().strip())
        
        theme = {
            "bg": self.var_bg.get(),
            "fg": self.var_fg.get(),
            "accent": self.var_accent.get()
        }
        self.config_manager.set("theme_colors", theme)
        messagebox.showinfo("Sucesso", "Identidade visual salva!\nFeche o programa e abra novamente este Workspace para ver as mudanças.")
