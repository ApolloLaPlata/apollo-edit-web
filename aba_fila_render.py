import customtkinter as ctk
"""
[PARTE 10] Fila de Renderização em Lote (Batch Queue).
Permite enfileirar múltiplos projetos (audio + roteiro + configuração) e
renderizá-los em sequência de forma autônoma, sem intervenção manual.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import os
import time
import logging
import datetime


class AbaFilaRender(ctk.CTkFrame):
    """
    Gerenciador de Fila de Renderização Autônoma.
    Cada item da fila é um "projeto" com: áudio, roteiro, pasta de saída e perfil de canal.
    O sistema processa cada projeto em sequência, delegando ao motor do Mapeador.
    """

    STATUS_PENDENTE   = "⏳ Pendente"
    STATUS_RENDERANDO = "🔄 Renderizando..."
    STATUS_CONCLUIDO  = "✅ Concluído"
    STATUS_ERRO       = "❌ Erro"
    STATUS_CANCELADO  = "🚫 Cancelado"

    def __init__(self, parent, config_manager=None, app_ref=None):
        super().__init__(parent)
        self.config_manager  = config_manager
        self.app_ref         = app_ref
        self._fila           = []          # Lista de dicts de projeto
        self._rodando        = False
        self._cancelar_flag  = False
        self._thread         = None
        self._hotfolder_thread = None
        self._hotfolder_ativo = False
        self._build_ui()

    # ─────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────

    def _build_ui(self):
        main = ctk.CTkFrame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(main, text="⚡ Fila de Renderização Autônoma (Batch Queue)",
                  font=("Segoe UI", 16, "bold"), text_color="#FFD32A").pack(anchor="w")
        ctk.CTkLabel(main,
                  text="Adicione múltiplos projetos à fila. O sistema renderiza tudo em sequência, sem intervenção.",
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 12))

        # ── Toolbar ───────────────────────────────────────────
        tb = ctk.CTkFrame(main)
        tb.pack(fill=tk.X, pady=(0, 8))

        ctk.CTkButton(tb, text="➕ Adicionar Projeto",     command=self._adicionar_projeto ).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="📂 Adicionar em Lote",      command=self._adicionar_em_lote  ).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="📁 Importar JSON",         command=self._importar_json      ).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="🗑️ Remover Selecionado",  command=self._remover_selecionado).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="🔝 Mover para Cima",       command=lambda: self._mover(-1)  ).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="🔽 Mover para Baixo",      command=lambda: self._mover(1)   ).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="🧹 Limpar Concluídos",     command=self._limpar_concluidos  ).pack(side=tk.LEFT, padx=2)

        # ── Abas de Modos ────────────────────────────────────
        self.notebook_modos = ttk.Notebook(main)
        self.notebook_modos.pack(fill=tk.BOTH, expand=True, pady=6)

        # Aba 1: Modo Short (Lotes Individuais)
        f_shorts = ctk.CTkFrame(self.notebook_modos)
        self.notebook_modos.add(f_shorts, text="📱 Modo Short (Lotes Individuais)")
        
        cols = ("ordem", "nome", "audio", "perfil", "status", "duracao")
        self.tree = ttk.Treeview(f_shorts, columns=cols, show="headings", height=8)
        self.tree.heading("ordem",   text="#")
        self.tree.heading("nome",    text="Nome do Projeto")
        self.tree.heading("audio",   text="Áudio")
        self.tree.heading("perfil",  text="Perfil de Canal")
        self.tree.heading("status",  text="Status")
        self.tree.heading("duracao", text="Tempo")

        self.tree.column("ordem",   width=40,  anchor=tk.CENTER)
        self.tree.column("nome",    width=200)
        self.tree.column("audio",   width=220)
        self.tree.column("perfil",  width=130)
        self.tree.column("status",  width=140, anchor=tk.CENTER)
        self.tree.column("duracao", width=70,  anchor=tk.CENTER)

        sb_v = ttk.Scrollbar(f_shorts, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(f_shorts, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        sb_v.pack(side=tk.RIGHT, fill=tk.Y)
        sb_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Aba 2: Modo Filme (Blocos Sequenciais)
        f_filme = ctk.CTkFrame(self.notebook_modos)
        self.notebook_modos.add(f_filme, text="🎬 Modo Filme (Composição Complexa)")
        
        tb_filme = ctk.CTkFrame(f_filme)
        tb_filme.pack(fill=tk.X, pady=4, padx=4)
        ctk.CTkButton(tb_filme, text="➕ Adicionar Bloco", command=self._adicionar_bloco_filme).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb_filme, text="🗑️ Remover Selecionado", command=self._remover_bloco_selecionado).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb_filme, text="🔝 Subir", command=lambda: self._mover_bloco(-1)).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb_filme, text="🔽 Descer", command=lambda: self._mover_bloco(1)).pack(side=tk.LEFT, padx=2)
        
        # Opções de saída do filme
        f_filme_out = ctk.CTkFrame(f_filme)
        f_filme_out.pack(fill=tk.X, pady=4, padx=4)
        ctk.CTkLabel(f_filme_out, text="Output Filme:").pack(side=tk.LEFT, padx=(0,5))
        self.v_saida_filme = tk.StringVar()
        ctk.CTkEntry(f_filme_out, textvariable=self.v_saida_filme, width=400).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ctk.CTkButton(f_filme_out, text="📁", width=30, command=lambda: self.v_saida_filme.set(filedialog.askdirectory())).pack(side=tk.LEFT, padx=(2,0))
        
        cols_filme = ("ordem", "perfil", "audio", "roteiro")
        self.tree_filme = ttk.Treeview(f_filme, columns=cols_filme, show="headings", height=8)
        self.tree_filme.heading("ordem", text="Bloco")
        self.tree_filme.heading("perfil", text="Perfil do Diretor")
        self.tree_filme.heading("audio", text="Áudio do Bloco")
        self.tree_filme.heading("roteiro", text="Roteiro Preview")
        
        self.tree_filme.column("ordem", width=50, anchor=tk.CENTER)
        self.tree_filme.column("perfil", width=150)
        self.tree_filme.column("audio", width=250)
        self.tree_filme.column("roteiro", width=250)
        
        sb_vf = ttk.Scrollbar(f_filme, orient="vertical", command=self.tree_filme.yview)
        self.tree_filme.configure(yscrollcommand=sb_vf.set)
        sb_vf.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_filme.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        self._fila_blocos = [] # Lista de dicionários de blocos do filme

        # ── Progresso Geral ───────────────────────────────────
        lf_prog = ctk.CTkLabelFrame(main, text=" 📊 Progresso Geral ")
        lf_prog.pack(fill=tk.X, pady=6)

        self.lbl_progresso = ctk.CTkLabel(lf_prog, text="Fila vazia.", font=("Segoe UI", 10))
        self.lbl_progresso.pack(anchor="w", padx=10, pady=4)

        self.progress_bar = ttk.Progressbar(lf_prog, mode="determinate", length=600)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 6))

        # ── Log da Fila ───────────────────────────────────────
        lf_log = ctk.CTkLabelFrame(main, text=" 📟 Log da Fila ")
        lf_log.pack(fill=tk.BOTH, expand=True, pady=6)

        self.txt_log = ctk.CTkTextbox(lf_log, height=150, font=("Consolas", 12), wrap=tk.WORD)
        self.txt_log.pack(fill=tk.BOTH, expand=True, padx=(10, 10), pady=5)
        self.txt_log.configure(state=tk.DISABLED)

        # ── Controles de Execução ─────────────────────────────
        ctrl = ctk.CTkFrame(main)
        ctrl.pack(fill=tk.X, pady=(8, 0))

        self.btn_iniciar  = ctk.CTkButton(ctrl, text="▶ INICIAR FILA",
                                      font=("Segoe UI", 12, "bold"),
                                      command=self._iniciar_fila)
        self.btn_iniciar.pack(side=tk.LEFT, padx=6, pady=4)

        self.btn_parar = ctk.CTkButton(ctrl, text="⏹ PARAR",
                                   font=("Segoe UI", 12, "bold"),
                                   state=tk.DISABLED,
                                   command=self._parar_fila)
        self.btn_parar.pack(side=tk.LEFT, padx=6, pady=4)

        self.enviar_timeline_lote = tk.BooleanVar(value=True)
        ctk.CTkSwitch(ctrl, text="Enviar para Timeline Web ao concluir", variable=self.enviar_timeline_lote).pack(side=tk.LEFT, padx=15)

        self.monitorar_hotfolder = tk.BooleanVar(value=False)
        ctk.CTkSwitch(ctrl, text="🤖 Piloto Automático (Hot-Folder)", variable=self.monitorar_hotfolder, command=self._toggle_hotfolder).pack(side=tk.LEFT, padx=15)

        self.lbl_eta = ctk.CTkLabel(ctrl, text="", font=("Segoe UI", 10), text_color="#AAAAAA")
        self.lbl_eta.pack(side=tk.RIGHT, padx=10)

    # ─────────────────────────────────────────────────────────
    # GERENCIAMENTO DE PROJETOS
    # ─────────────────────────────────────────────────────────

    def _adicionar_projeto(self):
        """Abre o diálogo de configuração de um novo projeto para a fila."""
        dlg = _DialogNovoProjeto(self, self.config_manager)
        self.wait_window(dlg)
        if dlg.resultado:
            self._fila.append(dlg.resultado)
            self._atualizar_tree()
            self._log(f"[FILA] Projeto '{dlg.resultado['nome']}' adicionado.")

    def _adicionar_em_lote(self):
        """[PARTE 14] Permite selecionar múltiplos áudios de uma vez e enviá-los para a Fila."""
        audios = filedialog.askopenfilenames(
            title="Selecione múltiplos áudios para render em lote",
            filetypes=[("Áudio", "*.mp3 *.wav *.m4a *.aac")]
        )
        if not audios:
            return
            
        saida = filedialog.askdirectory(title="Selecione a Pasta de Saída Geral")
        if not saida:
            messagebox.showinfo("Cancelado", "A adição em lote foi cancelada pois nenhuma pasta de saída foi escolhida.")
            return
            
        perfis = []
        if self.config_manager:
            perfis = list((self.config_manager.get("perfis_diretor") or {}).keys())
            
        dlg = tk.Toplevel(self)
        dlg.title("Perfil de Diretor para o Lote")
        dlg.geometry("350x150")
        dlg.configure()
        dlg.transient(self)
        dlg.grab_set()
        
        ctk.CTkLabel(dlg, text="Deseja aplicar um Perfil de Diretor em todos?").pack(pady=10)
        v_perfil = tk.StringVar(value="(nenhum)")
        cb = ctk.CTkOptionMenu(dlg, variable=v_perfil, values=["(nenhum)"] + perfis, width=300)
        cb.pack(pady=5)
        
        resultado = {"perfil": "(nenhum)"}
        def _ok():
            resultado["perfil"] = v_perfil.get()
            dlg.destroy()
            
        ctk.CTkButton(dlg, text="Confirmar Lote", command=_ok, font=("Segoe UI", 10, "bold")).pack(pady=10)
        self.wait_window(dlg)
        
        perfil = resultado["perfil"]
        if perfil == "(nenhum)": perfil = ""
        
        for idx, audio in enumerate(audios):
            nome = os.path.splitext(os.path.basename(audio))[0]
            proj = {
                "nome":    f"[Lote] {nome}",
                "audio":   audio,
                "saida":   saida,
                "roteiro": "",
                "musica":  "",
                "perfil":  perfil,
                "status":  self.STATUS_PENDENTE,
                "duracao": "—",
            }
            self._fila.append(proj)
            
        self._atualizar_tree()
        self._log(f"[FILA] {len(audios)} projetos adicionados em lote com sucesso.")

    def _importar_json(self):
        """Importa um projeto salvo em JSON externo."""
        caminhos = filedialog.askopenfilenames(
            title="Importar Projeto(s) da Fila",
            filetypes=[("JSON de Projeto", "*.json"), ("Todos", "*.*")]
        )
        for caminho in caminhos:
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    proj = json.load(f)
                # Valida campos mínimos
                if "audio" not in proj:
                    self._log(f"[AVISO] JSON inválido (sem campo 'audio'): {os.path.basename(caminho)}")
                    continue
                proj.setdefault("nome",   os.path.splitext(os.path.basename(caminho))[0])
                proj.setdefault("status", self.STATUS_PENDENTE)
                proj.setdefault("perfil", "")
                self._fila.append(proj)
                self._log(f"[FILA] Projeto importado: '{proj['nome']}'")
            except Exception as e:
                self._log(f"[ERRO] Falha ao importar '{os.path.basename(caminho)}': {e}")
        self._atualizar_tree()

    def _remover_selecionado(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        nome = self._fila[idx]["nome"]
        if messagebox.askyesno("Remover", f"Remover '{nome}' da fila?"):
            self._fila.pop(idx)
            self._atualizar_tree()

    def _mover(self, direcao):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        novo = idx + direcao
        if 0 <= novo < len(self._fila):
            self._fila[idx], self._fila[novo] = self._fila[novo], self._fila[idx]
            self._atualizar_tree()
            # Reseleciona o item movido
            children = self.tree.get_children()
            if children and novo < len(children):
                self.tree.selection_set(children[novo])

    def _limpar_concluidos(self):
        antes = len(self._fila)
        self._fila = [p for p in self._fila
                      if p.get("status") not in (self.STATUS_CONCLUIDO, self.STATUS_ERRO, self.STATUS_CANCELADO)]
        self._atualizar_tree()
        removidos = antes - len(self._fila)
        if removidos > 0:
            self._log(f"[FILA] {removidos} projeto(s) concluído(s) removido(s).")

    # ─────────────────────────────────────────────────────────
    # GERENCIAMENTO DE MODO FILME (BLOCOS)
    # ─────────────────────────────────────────────────────────

    def _adicionar_bloco_filme(self):
        dlg = _DialogNovoBlocoFilme(self, self.config_manager)
        self.wait_window(dlg)
        if hasattr(dlg, 'resultado') and dlg.resultado:
            self._fila_blocos.append(dlg.resultado)
            self._atualizar_tree_filme()
            self._log(f"[FILME] Bloco '{dlg.resultado['perfil']}' adicionado ao filme.")

    def _remover_bloco_selecionado(self):
        sel = self.tree_filme.selection()
        if not sel: return
        idx = int(self.tree_filme.item(sel[0], "values")[0]) - 1
        del self._fila_blocos[idx]
        self._atualizar_tree_filme()
        self._log("[FILME] Bloco removido.")

    def _mover_bloco(self, direcao):
        sel = self.tree_filme.selection()
        if not sel: return
        idx = int(self.tree_filme.item(sel[0], "values")[0]) - 1
        novo_idx = idx + direcao
        if 0 <= novo_idx < len(self._fila_blocos):
            self._fila_blocos.insert(novo_idx, self._fila_blocos.pop(idx))
            self._atualizar_tree_filme()
            # Reselect
            for item in self.tree_filme.get_children():
                if int(self.tree_filme.item(item, "values")[0]) - 1 == novo_idx:
                    self.tree_filme.selection_set(item)
                    break

    def _atualizar_tree_filme(self):
        for item in self.tree_filme.get_children():
            self.tree_filme.delete(item)
        for i, b in enumerate(self._fila_blocos):
            rot_preview = b.get("roteiro", "").replace("\n", " ")[:40] + "..." if b.get("roteiro") else ""
            val = (i + 1, b.get("perfil", "Default"), os.path.basename(b.get("audio", "")), rot_preview)
            self.tree_filme.insert("", tk.END, values=val)
        self._log("[FILME] Árvore de blocos atualizada.")

    def _atualizar_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self._fila, 1):
            audio_nome = os.path.basename(p.get("audio", "")) or "—"
            self.tree.insert("", "end", values=(
                i,
                p.get("nome",   "Sem nome"),
                audio_nome,
                p.get("perfil", "—"),
                p.get("status", self.STATUS_PENDENTE),
                p.get("duracao","—"),
            ))
        total    = len(self._fila)
        concl    = sum(1 for p in self._fila if p.get("status") == self.STATUS_CONCLUIDO)
        self.lbl_progresso.config(
            text=f"{concl} / {total} projetos concluídos." if total else "Fila vazia."
        )
        if total:
            self.progress_bar["value"] = (concl / total) * 100

    # ─────────────────────────────────────────────────────────
    # HOT FOLDER (PILOTO AUTOMÁTICO)
    # ─────────────────────────────────────────────────────────

    def _toggle_hotfolder(self):
        if self.monitorar_hotfolder.get():
            self._hotfolder_ativo = True
            self._log("[HOT-FOLDER] 🤖 Piloto Automático ATIVADO. Monitorando pasta...")
            if not self._hotfolder_thread or not self._hotfolder_thread.is_alive():
                self._hotfolder_thread = threading.Thread(target=self._hotfolder_worker, daemon=True)
                self._hotfolder_thread.start()
        else:
            self._hotfolder_ativo = False
            self._log("[HOT-FOLDER] ⏹ Piloto Automático DESATIVADO.")

    def _hotfolder_worker(self):
        import shutil
        if not self.config_manager or not self.config_manager.workspace_dir:
            return
            
        hf_dir = os.path.join(self.config_manager.workspace_dir, "HotFolder")
        proc_dir = os.path.join(hf_dir, "Processados")
        saida_dir = os.path.join(self.config_manager.workspace_dir, "outputs")
        
        for d in [hf_dir, proc_dir, saida_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

        audio_exts = ('.mp3', '.wav', '.m4a')
        
        while self._hotfolder_ativo:
            try:
                # Procura pares de arquivos (audio + txt)
                arquivos = os.listdir(hf_dir)
                audios = [f for f in arquivos if f.lower().endswith(audio_exts)]
                textos = [f for f in arquivos if f.lower().endswith('.txt')]
                
                for aud in audios:
                    base_nome = os.path.splitext(aud)[0]
                    txt_correspondente = base_nome + ".txt"
                    
                    if txt_correspondente in textos:
                        # Achou um par!
                        aud_path = os.path.join(hf_dir, aud)
                        txt_path = os.path.join(hf_dir, txt_correspondente)
                        
                        # Verifica se os arquivos não estão sendo gravados agora
                        try:
                            s1 = os.path.getsize(aud_path)
                            s2 = os.path.getsize(txt_path)
                            time.sleep(1)
                            if s1 != os.path.getsize(aud_path) or s2 != os.path.getsize(txt_path):
                                continue # Arquivo crescendo, espera o próximo ciclo
                        except:
                            continue
                            
                        # Move para Processados
                        new_aud_path = os.path.join(proc_dir, aud)
                        new_txt_path = os.path.join(proc_dir, txt_correspondente)
                        shutil.move(aud_path, new_aud_path)
                        shutil.move(txt_path, new_txt_path)
                        
                        with open(new_txt_path, 'r', encoding='utf-8') as f:
                            roteiro = f.read()
                            
                        # Enfileira
                        self._log(f"[HOT-FOLDER] Par detectado: {base_nome}. Enfileirando automático...")
                        self.enfileirar(audio=new_aud_path, saida=saida_dir, roteiro=roteiro, nome=base_nome)
                        
                        # Inicia fila se não estiver rodando (Modo Short)
                        self.after(500, self._auto_iniciar_se_parado)
            except Exception as e:
                pass
            time.sleep(3)
            
    def _auto_iniciar_se_parado(self):
        tab_idx = self.notebook_modos.index(self.notebook_modos.select())
        if not self._rodando and tab_idx == 0:
            self._iniciar_fila()

    # ─────────────────────────────────────────────────────────
    # MOTOR DE EXECUÇÃO DA FILA
    # ─────────────────────────────────────────────────────────

    def _iniciar_fila(self):
        tab_idx = self.notebook_modos.index(self.notebook_modos.select())
        if tab_idx == 0:
            pendentes = [p for p in self._fila if p.get("status") == self.STATUS_PENDENTE]
            if not pendentes:
                messagebox.showinfo("Fila", "Nenhum projeto pendente na fila do Modo Short.")
                return
            if self._rodando:
                messagebox.showwarning("Aviso", "A fila já está em execução.")
                return

            self._cancelar_flag = False
            self._rodando       = True
            self.btn_iniciar.config(state=tk.DISABLED)
            self.btn_parar.config(state=tk.NORMAL)
            self._log(f"[FILA] ▶ Iniciando fila com {len(pendentes)} projeto(s) pendente(s).")

            self._thread = threading.Thread(target=self._worker_fila, daemon=True)
            self._thread.start()
        elif tab_idx == 1:
            if not self._fila_blocos:
                messagebox.showinfo("Filme", "Nenhum bloco adicionado ao Modo Filme.")
                return
            
            saida_filme = self.v_saida_filme.get().strip()
            if not saida_filme:
                messagebox.showwarning("Aviso", "Selecione uma pasta de saída para o filme final.")
                return
                
            if self._rodando:
                messagebox.showwarning("Aviso", "A fila já está em execução.")
                return

            self._cancelar_flag = False
            self._rodando       = True
            self.btn_iniciar.config(state=tk.DISABLED)
            self.btn_parar.config(state=tk.NORMAL)
            self._log(f"[FILME] ▶ Iniciando composição do Filme com {len(self._fila_blocos)} blocos.")

            self._thread = threading.Thread(target=self._worker_filme, args=(saida_filme,), daemon=True)
            self._thread.start()

    def _parar_fila(self):
        self._cancelar_flag = True
        self._log("[FILA] ⏹ Sinal de parada enviado. Aguardando projeto atual finalizar...")
        self.btn_parar.config(state=tk.DISABLED)

    def _worker_filme(self, saida_filme):
        """Thread que processa blocos sequencialmente e os concatena no final."""
        import tempfile
        import subprocess
        inicio_filme = time.time()
        temp_dir = tempfile.mkdtemp(prefix="apollo_filme_")
        
        blocos_mp4 = []
        erros = 0
        blocos_alvo = list(self._fila_blocos)
        total_blocos = len(blocos_alvo)
        
        for idx, bloco in enumerate(blocos_alvo):
            if self._cancelar_flag:
                break
                
            proj = {
                "nome": f"Bloco {idx+1}",
                "audio": bloco.get("audio"),
                "saida": temp_dir,
                "roteiro": bloco.get("roteiro"),
                "musica": "",
                "perfil": bloco.get("perfil"),
                "status": self.STATUS_PENDENTE,
            }
            
            self._log(f"[FILME] 🎬 Renderizando Bloco {idx+1}/{total_blocos}...")
            
            # Limpa temp antes de renderizar para identificar o arquivo facilmente
            for f in os.listdir(temp_dir):
                if f.endswith(".mp4"):
                    os.remove(os.path.join(temp_dir, f))
                    
            ok = self._renderizar_projeto(proj)
            if ok:
                # Procura o mp4 gerado
                mp4_gerado = None
                for f in os.listdir(temp_dir):
                    if f.endswith(".mp4") and "Apollo" in f:
                        mp4_gerado = os.path.join(temp_dir, f)
                        break
                
                if mp4_gerado:
                    # Move para um nome seguro sequencial
                    safe_path = os.path.join(temp_dir, f"bloco_{idx:03d}.mp4")
                    import shutil
                    shutil.move(mp4_gerado, safe_path)
                    blocos_mp4.append(safe_path)
                    self._log(f"[FILME] ✅ Bloco {idx+1} concluído.")
                else:
                    self._log(f"[FILME] ❌ Falha: MP4 do Bloco {idx+1} não encontrado.")
                    erros += 1
            else:
                self._log(f"[FILME] ❌ Erro ao renderizar Bloco {idx+1}.")
                erros += 1
                
            self.after(0, lambda c=idx+1, t=total_blocos: self.progress_bar.config(value=(c/t)*100))
            self.after(0, lambda c=idx+1, t=total_blocos: self.lbl_progresso.config(text=f"Bloco {c} / {t} renderizado."))

        if self._cancelar_flag:
            self._log("[FILME] 🚫 Renderização do Filme cancelada pelo usuário.")
        elif erros == 0 and blocos_mp4:
            self._log(f"[FILME] ⏳ Todos os blocos renderizados. Concatenando {len(blocos_mp4)} partes...")
            # Usa ffmpeg concat demuxer
            lista_txt = os.path.join(temp_dir, "lista.txt")
            with open(lista_txt, "w", encoding="utf-8") as f:
                for mp4 in blocos_mp4:
                    # Escape para ffmpeg: path absoluto precisa trocar barras ou formatar corretamente
                    # Mais seguro colocar apenas o nome do arquivo se estiver no mesmo dir
                    f.write(f"file '{os.path.basename(mp4)}'\n")
            
            output_final = os.path.join(saida_filme, f"Filme_Apollo_{int(time.time())}.mp4")
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", "lista.txt",
                "-c", "copy",
                output_final
            ]
            
            try:
                subprocess.run(cmd, cwd=temp_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                duracao_total = time.time() - inicio_filme
                self._log(f"[FILME] 🎉 Filme finalizado com sucesso em {duracao_total:.0f}s: {output_final}")
                if self.enviar_timeline_lote.get():
                    self._enviar_para_timeline(output_final)
                self.after(0, lambda out=output_final: messagebox.showinfo("Filme Concluído", f"✅ Filme renderizado com sucesso!\n\nSalvo em:\n{out}"))
            except subprocess.CalledProcessError as e:
                self._log(f"[FILME] ❌ Erro ao concatenar vídeos: {e}")
        else:
            self._log("[FILME] ❌ Filme abortado devido a erros nos blocos.")
            
        self._rodando = False
        self.after(0, lambda: self.btn_iniciar.config(state=tk.NORMAL))
        self.after(0, lambda: self.btn_parar.config(state=tk.DISABLED))
        self.after(0, lambda: self.progress_bar.config(value=0))
        self.after(0, lambda: self.lbl_progresso.config(text="Pronto."))

    def _enviar_para_timeline(self, filepath):
        """Envia o arquivo renderizado para a Web Timeline via endpoint REST."""
        try:
            import urllib.request
            import urllib.parse
            import json
            data = json.dumps({"file": filepath}).encode("utf-8")
            req = urllib.request.Request(
                "http://localhost:8000/api/send_to_timeline",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as res:
                if res.status == 200:
                    self._log(f"[INTEGRAÇÃO] ✅ Mídia enviada para a Timeline Web: {os.path.basename(filepath)}")
        except Exception as e:
            self._log(f"[AVISO] Não foi possível enviar para a Timeline Web: {e}")

    def _worker_fila(self):
        """Thread principal que processa os projetos em sequência."""
        inicio_fila = time.time()
        total_pendentes = sum(1 for p in self._fila if p.get("status") == self.STATUS_PENDENTE)
        processados = 0

        for proj in self._fila:
            if proj.get("status") != self.STATUS_PENDENTE:
                continue
            if self._cancelar_flag:
                proj["status"] = self.STATUS_CANCELADO
                self.after(0, self._atualizar_tree)
                continue

            proj["status"] = self.STATUS_RENDERANDO
            self.after(0, self._atualizar_tree)
            self._log(f"[RENDER] 🎬 Iniciando: '{proj['nome']}'")

            inicio_proj = time.time()
            ok = self._renderizar_projeto(proj)
            duracao = time.time() - inicio_proj

            proj["duracao"] = f"{duracao:.0f}s"
            proj["status"]  = self.STATUS_CONCLUIDO if ok else self.STATUS_ERRO
            processados    += 1

            # [E12] Limpeza de Memória e Temp Render entre Projetos (Batch Safe)
            try:
                import gc
                gc.collect()
                # Limpar temp_render para liberar disco se tiver sido preenchido
                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_render")
                if os.path.exists(temp_dir):
                    import shutil
                    for f in os.listdir(temp_dir):
                        path_f = os.path.join(temp_dir, f)
                        if os.path.isfile(path_f):
                            try: os.remove(path_f)
                            except: pass
                # Resetar arrays do mapeador para não vazar RAM
                if self.app_ref and hasattr(self.app_ref, "aba_mapeador"):
                    self.app_ref.aba_mapeador.images = []
                    self.app_ref.aba_mapeador.video_clips = []
                    # THREAD-SAFE: Tkinter widgets must be updated from the UI thread
                    def _limpar_listbox():
                        try:
                            self.app_ref.aba_mapeador.listbox.delete(0, tk.END)
                        except Exception:
                            pass
                    self.after(0, _limpar_listbox)
                    if hasattr(self.app_ref.aba_mapeador, "_last_ia_words"):
                        self.app_ref.aba_mapeador._last_ia_words = []
            except Exception as e_gc:
                self._log(f"[AVISO] Erro na limpeza pós-render: {e_gc}")

            self.after(0, self._atualizar_tree)
            self._log(
                f"[RENDER] {'✅' if ok else '❌'} '{proj['nome']}' — "
                f"{'Concluído' if ok else 'Falhou'} em {duracao:.0f}s"
            )

            if ok and proj.get('output_path') and self.enviar_timeline_lote.get():
                self._enviar_para_timeline(proj['output_path'])



            # ETA estimado para os próximos
            if processados < total_pendentes:
                media = (time.time() - inicio_fila) / processados
                restantes = total_pendentes - processados
                eta_s = media * restantes
                eta_str = str(datetime.timedelta(seconds=int(eta_s)))
                self.after(0, lambda s=eta_str: self.lbl_eta.config(
                    text=f"ETA restante: ~{s}"))

        # Finalização
        duracao_total = time.time() - inicio_fila
        concl  = sum(1 for p in self._fila if p.get("status") == self.STATUS_CONCLUIDO)
        erros  = sum(1 for p in self._fila if p.get("status") == self.STATUS_ERRO)

        self._log(
            f"[FILA] 🏁 Fila finalizada em {duracao_total:.0f}s — "
            f"{concl} concluído(s), {erros} erro(s)."
        )
        self._rodando = False
        self.after(0, lambda: self.btn_iniciar.config(state=tk.NORMAL))
        self.after(0, lambda: self.btn_parar.config(state=tk.DISABLED))
        self.after(0, lambda: self.lbl_eta.config(text=""))
        self.after(0, self._atualizar_tree)

        # Notificação de conclusão
        if not self._cancelar_flag:
            self.after(0, lambda: messagebox.showinfo(
                "Fila Concluída",
                f"✅ Fila finalizada!\n\n"
                f"✔ {concl} projeto(s) renderizado(s) com sucesso\n"
                f"✗ {erros} projeto(s) com erro\n"
                f"⏱ Tempo total: {datetime.timedelta(seconds=int(duracao_total))}"
            ))

    def _renderizar_projeto(self, proj):
        """
        Delega o render ao motor do Mapeador Automático.
        Preenche os campos da UI do mapeador e dispara o render de forma síncrona.
        Retorna True em sucesso, False em erro.
        """
        try:
            mapeador = None
            if self.app_ref and hasattr(self.app_ref, "aba_mapeador"):
                mapeador = self.app_ref.aba_mapeador

            if not mapeador:
                self._log(f"[ERRO] Mapeador não encontrado. Verifique a inicialização do app.")
                return False

            import queue as _queue
            resultado_q = _queue.Queue()

            def _setup_e_render():
                """Roda na thread da UI para configurar os campos e iniciar o render."""
                try:
                    # Aplica perfil de diretor se especificado
                    if proj.get("perfil") and self.config_manager:
                        self._aplicar_perfil_silencioso(proj["perfil"], mapeador)

                    # Configura os campos do mapeador com os dados do projeto
                    mapeador.audio_path.set(proj.get("audio", ""))
                    mapeador.saida_dir.set(proj.get("saida", ""))

                    if proj.get("roteiro"):
                        mapeador.text_mapeamento.delete("1.0", tk.END)
                        mapeador.text_mapeamento.insert("1.0", proj["roteiro"])

                    if proj.get("musica"):
                        mapeador.musica_path.set(proj["musica"])

                    # Monitora a conclusão via status do mapeador
                    t0 = time.time()
                    max_espera = 7200  # 2 horas no máximo
                    
                    def _check_status():
                        status_txt = mapeador.status.get() if hasattr(mapeador, "status") else ""
                        if any(k in status_txt.lower() for k in ["concluído", "finalizado", "vídeo final", "erro", "cancelado"]):
                            ok = "erro" not in status_txt.lower() and "cancelado" not in status_txt.lower()
                            resultado_q.put(ok)
                            return
                        if self._cancelar_flag:
                            if hasattr(mapeador, "cancelar_flag"):
                                mapeador.cancelar_flag = True
                            resultado_q.put(False)
                            return
                        if time.time() - t0 < max_espera:
                            self.after(2000, _check_status)
                        else:
                            resultado_q.put(False)
                    
                    mapeador._iniciar_mapeamento()
                    self.after(2000, _check_status)

                except Exception as e:
                    self._log(f"[ERRO] Falha ao configurar projeto: {e}")
                    resultado_q.put(False)

            self.after(0, _setup_e_render)

            # Aguarda resultado (timeout de 2 horas)
            try:
                return resultado_q.get(timeout=7200)
            except _queue.Empty:
                self._log(f"[ERRO] Timeout ao aguardar '{proj['nome']}'")
                return False

        except Exception as e:
            self._log(f"[ERRO] Exceção no render de '{proj.get('nome', '?')}': {e}")
            return False

    def _aplicar_perfil_silencioso(self, nome_perfil, mapeador):
        """Aplica um perfil de diretor sem exibir popups, injetando direto no mapeador."""
        try:
            perfis = self.config_manager.get("perfis_diretor") or {}
            p = perfis.get(nome_perfil)
            if not p:
                return
            if mapeador and hasattr(mapeador, '_set_diretor_config'):
                mapeador._set_diretor_config(p)
                self._log(f"[PERFIL] Perfil do Diretor '{nome_perfil}' aplicado no Mapeador.")
        except Exception as e:
            self._log(f"[AVISO] Falha ao aplicar perfil '{nome_perfil}': {e}")

    def _log(self, msg):
        """Log thread-safe no painel da fila."""
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        linha = f"[{ts}] {msg}"
        logging.info(linha)
        def _inserir():
            self.txt_log.config(state=tk.NORMAL)
            self.txt_log.insert(tk.END, linha + "\n")
            self.txt_log.see(tk.END)
            self.txt_log.config(state=tk.DISABLED)
        self.after(0, _inserir)

    # ─────────────────────────────────────────────────────────
    # API PÚBLICA: Adicionar projeto via código
    # ─────────────────────────────────────────────────────────

    def enfileirar(self, audio, saida, roteiro="", nome="", perfil="", musica=""):
        """
        Adiciona um projeto à fila programaticamente.
        Pode ser chamado de qualquer outro módulo (ex: loop de automação).
        """
        proj = {
            "nome":    nome or os.path.splitext(os.path.basename(audio))[0],
            "audio":   audio,
            "saida":   saida,
            "roteiro": roteiro,
            "musica":  musica,
            "perfil":  perfil,
            "status":  self.STATUS_PENDENTE,
            "duracao": "—",
        }
        self._fila.append(proj)
        self.after(0, self._atualizar_tree)
        self._log(f"[FILA] Projeto '{proj['nome']}' enfileirado via API.")


# ─────────────────────────────────────────────────────────────
# Diálogo para criar novo projeto
# ─────────────────────────────────────────────────────────────

class _DialogNovoProjeto(tk.Toplevel):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        self.title("Novo Projeto para a Fila")
        self.geometry("600x420")
        self.configure()
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.config_manager = config_manager
        self.resultado = None
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Configurar Novo Projeto",
                  font=("Segoe UI", 13, "bold"), text_color="#FFD32A").pack(pady=(14, 8))

        f = ctk.CTkFrame(self)
        f.pack(fill=tk.BOTH, expand=True, padx=20)

        def row(label, var, browse=None, filetypes=None):
            fr = ctk.CTkFrame(f)
            fr.pack(fill=tk.X, pady=4)
            ctk.CTkLabel(fr, text=label, width=220, anchor="w").pack(side=tk.LEFT)
            e = ctk.CTkEntry(fr, textvariable=var, width=380)
            e.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
            if browse:
                def _cmd(v=var, ft=filetypes):
                    if ft:
                        p = filedialog.askopenfilename(filetypes=ft)
                    else:
                        p = filedialog.askdirectory()
                    if p: v.set(p)
                ctk.CTkButton(fr, text="📁", width=30, command=_cmd).pack(side=tk.LEFT)

        self.v_nome   = tk.StringVar()
        self.v_audio  = tk.StringVar()
        self.v_saida  = tk.StringVar()
        self.v_musica = tk.StringVar()
        self.v_perfil = tk.StringVar()

        row("Nome do Projeto:",    self.v_nome)
        row("Áudio Principal:",    self.v_audio,  browse=True,
            filetypes=[("Áudio", "*.mp3 *.wav *.m4a *.aac")])
        row("Pasta de Saída:",     self.v_saida,  browse=True)
        row("Música de Fundo:",    self.v_musica, browse=True,
            filetypes=[("Áudio", "*.mp3 *.wav *.m4a")])

        # Perfil de canal (dropdown dos perfis salvos)
        fr_p = ctk.CTkFrame(f)
        fr_p.pack(fill=tk.X, pady=4)
        ctk.CTkLabel(fr_p, text="Perfil de Canal:", width=220, anchor="w").pack(side=tk.LEFT)
        perfis_nomes = []
        if self.config_manager:
            perfis_nomes = list((self.config_manager.get("perfis_diretor") or {}).keys())
        cb = ctk.CTkOptionMenu(fr_p, variable=self.v_perfil,
                          values=["(nenhum)"] + perfis_nomes, width=36)
        cb.pack(side=tk.LEFT, padx=4)
        cb.set("(nenhum)")

        # Roteiro inline
        ctk.CTkLabel(f, text="Roteiro (opcional):", anchor="w").pack(anchor="w", pady=(8, 2))
        self.txt_roteiro = ctk.CTkTextbox(f, height=100, font=("Consolas", 12))
        self.txt_roteiro.pack(fill=tk.BOTH, expand=True)

        # Botões
        btn_f = ctk.CTkFrame(self)
        btn_f.pack(fill=tk.X, padx=20, pady=10)
        ctk.CTkButton(btn_f, text="✅ Adicionar à Fila",
                  font=("Segoe UI", 11, "bold"),
                  command=self._confirmar).pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(btn_f, text="❌ Cancelar",
                  font=("Segoe UI", 11),
                  command=self.destroy).pack(side=tk.LEFT, padx=6)

    def _confirmar(self):
        audio = self.v_audio.get().strip()
        saida = self.v_saida.get().strip()
        if not audio or not os.path.exists(audio):
            messagebox.showerror("Erro", "Selecione um áudio válido.", parent=self)
            return
        if not saida:
            messagebox.showerror("Erro", "Selecione a pasta de saída.", parent=self)
            return
        perfil = self.v_perfil.get()
        if perfil == "(nenhum)": perfil = ""
        self.resultado = {
            "nome":    self.v_nome.get().strip() or os.path.splitext(os.path.basename(audio))[0],
            "audio":   audio,
            "saida":   saida,
            "musica":  self.v_musica.get().strip(),
            "perfil":  perfil,
            "roteiro": self.txt_roteiro.get("1.0", tk.END).strip(),
            "status":  "⏳ Pendente",
            "duracao": "—",
        }
        self.destroy()


# ─────────────────────────────────────────────────────────────
# Diálogo para criar novo bloco de filme
# ─────────────────────────────────────────────────────────────

class _DialogNovoBlocoFilme(tk.Toplevel):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        self.title("Novo Bloco do Filme")
        self.geometry("600x380")
        self.configure()
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.config_manager = config_manager
        self.resultado = None
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Configurar Bloco",
                  font=("Segoe UI", 13, "bold"), text_color="#FFD32A").pack(pady=(14, 8))

        f = ctk.CTkFrame(self)
        f.pack(fill=tk.BOTH, expand=True, padx=20)

        def row(label, var, browse=None, filetypes=None):
            fr = ctk.CTkFrame(f)
            fr.pack(fill=tk.X, pady=4)
            ctk.CTkLabel(fr, text=label, width=220, anchor="w").pack(side=tk.LEFT)
            e = ctk.CTkEntry(fr, textvariable=var, width=380)
            e.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
            if browse:
                def _cmd(v=var, ft=filetypes):
                    if ft:
                        p = filedialog.askopenfilename(filetypes=ft)
                    else:
                        p = filedialog.askdirectory()
                    if p: v.set(p)
                ctk.CTkButton(fr, text="📁", width=30, command=_cmd).pack(side=tk.LEFT)

        self.v_audio  = tk.StringVar()
        self.v_perfil = tk.StringVar()

        row("Áudio do Bloco:", self.v_audio, browse=True,
            filetypes=[("Áudio", "*.mp3 *.wav *.m4a *.aac")])

        # Perfil de canal (dropdown dos perfis salvos)
        fr_p = ctk.CTkFrame(f)
        fr_p.pack(fill=tk.X, pady=4)
        ctk.CTkLabel(fr_p, text="Perfil do Diretor:", width=220, anchor="w").pack(side=tk.LEFT)
        perfis_nomes = []
        if self.config_manager:
            perfis_nomes = list((self.config_manager.get("perfis_diretor") or {}).keys())
        cb = ctk.CTkOptionMenu(fr_p, variable=self.v_perfil,
                          values=["(nenhum)"] + perfis_nomes, width=36)
        cb.pack(side=tk.LEFT, padx=4)
        cb.set("(nenhum)")

        # Roteiro inline
        ctk.CTkLabel(f, text="Roteiro (obrigatório):", anchor="w").pack(anchor="w", pady=(8, 2))
        self.txt_roteiro = ctk.CTkTextbox(f, height=100, font=("Consolas", 12))
        self.txt_roteiro.pack(fill=tk.BOTH, expand=True)

        # Botões
        btn_f = ctk.CTkFrame(self)
        btn_f.pack(fill=tk.X, padx=20, pady=10)
        ctk.CTkButton(btn_f, text="✅ Adicionar Bloco",
                  font=("Segoe UI", 11, "bold"),
                  command=self._confirmar).pack(side=tk.LEFT, padx=6)
        ctk.CTkButton(btn_f, text="❌ Cancelar",
                  font=("Segoe UI", 11),
                  command=self.destroy).pack(side=tk.LEFT, padx=6)

    def _confirmar(self):
        audio = self.v_audio.get().strip()
        if not audio or not os.path.exists(audio):
            messagebox.showerror("Erro", "Selecione um áudio válido.", parent=self)
            return
        perfil = self.v_perfil.get()
        if perfil == "(nenhum)": perfil = ""
        self.resultado = {
            "audio":   audio,
            "perfil":  perfil,
            "roteiro": self.txt_roteiro.get("1.0", tk.END).strip()
        }
        self.destroy()
