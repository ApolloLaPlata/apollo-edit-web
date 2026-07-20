import customtkinter as ctk
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import time

class AbaBiblioteca(ctk.CTkFrame):
    """
    Tanque de Combustível (Biblioteca).
    Uma aba simples para listar, pré-visualizar e copiar caminhos 
    das mídias do workspace para enviar à Aba Diretor.
    """
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.arquivos = []
        self._build_ui()
        self._carregar_lista()

    def _build_ui(self):
        main = ctk.CTkFrame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        ctk.CTkLabel(main, text="📚 Tanque de Combustível (Biblioteca)",
                  font=("Segoe UI", 16, "bold"), text_color="#FFD32A").pack(anchor="w")
        ctk.CTkLabel(main,
                  text="Explore suas mídias geradas no Workspace. Dê duplo-clique para tocar ou clique em 'Copiar Caminho'.",
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 12))

        # Toolbar
        tb = ctk.CTkFrame(main)
        tb.pack(fill=tk.X, pady=(0, 8))
        
        ctk.CTkButton(tb, text="🔄 Atualizar Lista", command=self._carregar_lista).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="📋 Copiar Caminho", command=self._copiar_caminho).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="▶ Reproduzir", command=self._reproduzir).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(tb, text="📂 Abrir Pasta", command=self._abrir_pasta).pack(side=tk.LEFT, padx=2)

        # Treeview
        cols = ("nome", "tipo", "tamanho", "caminho")
        self.tree = ttk.Treeview(main, columns=cols, show="headings", height=15)
        self.tree.heading("nome", text="Nome do Arquivo")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("tamanho", text="Tamanho (MB)")
        self.tree.heading("caminho", text="Caminho Completo")

        self.tree.column("nome", width=250)
        self.tree.column("tipo", width=80, anchor=tk.CENTER)
        self.tree.column("tamanho", width=100, anchor=tk.CENTER)
        self.tree.column("caminho", width=500)

        sb_v = ttk.Scrollbar(main, orient="vertical", command=self.tree.yview)
        sb_h = ttk.Scrollbar(main, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        
        sb_v.pack(side=tk.RIGHT, fill=tk.Y)
        sb_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", lambda e: self._reproduzir())

    def _carregar_lista(self):
        self.tree.delete(*self.tree.get_children())
        self.arquivos.clear()
        
        if not self.config_manager or not self.config_manager.workspace_dir:
            return

        pastas_alvo = [
            os.path.join(self.config_manager.workspace_dir, "outputs"),
            os.path.join(self.config_manager.workspace_dir, "audio"),
            self.config_manager.workspace_dir
        ]
        
        tipos_validos = ('.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.m4a', '.png', '.jpg', '.jpeg', '.json')

        arquivos_encontrados = []
        for pasta in pastas_alvo:
            if not os.path.exists(pasta):
                continue
            for f in os.listdir(pasta):
                if f.lower().endswith(tipos_validos):
                    caminho_abs = os.path.join(pasta, f)
                    if os.path.isfile(caminho_abs):
                        try:
                            tamanho_mb = os.path.getsize(caminho_abs) / (1024 * 1024)
                        except:
                            tamanho_mb = 0
                            
                        ext = os.path.splitext(f)[1].lower()
                        tipo = "Vídeo" if ext in ['.mp4', '.mkv', '.avi', '.mov'] else "Áudio" if ext in ['.mp3', '.wav', '.m4a'] else "Imagem" if ext in ['.png', '.jpg', '.jpeg'] else "Template"
                        
                        arquivos_encontrados.append({
                            "nome": f,
                            "tipo": tipo,
                            "tamanho": f"{tamanho_mb:.2f}",
                            "caminho": caminho_abs
                        })
                        
        # Remover duplicatas baseadas no caminho absoluto
        vistos = set()
        for arq in arquivos_encontrados:
            if arq["caminho"] not in vistos:
                vistos.add(arq["caminho"])
                self.arquivos.append(arq)

        for arq in self.arquivos:
            self.tree.insert("", "end", values=(arq["nome"], arq["tipo"], arq["tamanho"], arq["caminho"]))

    def _copiar_caminho(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        caminho = item["values"][3]
        self.clipboard_clear()
        self.clipboard_append(caminho)
        messagebox.showinfo("Copiado", "Caminho absoluto copiado para a área de transferência!\nVocê pode colar na Aba Diretor agora.")

    def _reproduzir(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        caminho = item["values"][3]
        try:
            if os.name == 'nt':
                os.startfile(caminho)
            else:
                subprocess.Popen(["xdg-open", caminho])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{e}")

    def _abrir_pasta(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        caminho = item["values"][3]
        pasta = os.path.dirname(caminho)
        try:
            if os.name == 'nt':
                os.startfile(pasta)
            else:
                subprocess.Popen(["xdg-open", pasta])
        except:
            pass
