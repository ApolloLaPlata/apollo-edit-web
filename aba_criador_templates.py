import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import webbrowser
import os
import sys

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Ensure Web UI server can be loaded
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import servidor_web

class AbaCriadorTemplates(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.perfis_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis_templates")
        self.photo_cache = {} # To prevent garbage collection of PhotoImages
        
        container = ctk.CTkFrame(self)
        container.pack(expand=True, fill='both')
        
        # UI
        ctk.CTkLabel(container, text="🎨 Criador de Templates Visual", font=("Segoe UI", 24, "bold"), text_color="#FFD32A").pack(pady=(20, 10))
        
        ctk.CTkLabel(container, text="Acesse o Estúdio Apollo pelo seu navegador para desenhar as camadas livremente.", font=("Segoe UI", 12)).pack(pady=5)
        ctk.CTkLabel(container, text="O servidor local fará a ponte entre o seu browser e as pastas do computador.", font=("Segoe UI", 12)).pack(pady=5)
        
        btn = ctk.CTkButton(container, text="🚀 INICIAR ESTÚDIO VISUAL (Web)", command=self._abrir_estudio)
        btn.pack(pady=15, ipadx=30, ipady=15)
        
        self.status_lbl = ctk.CTkLabel(container, text="", font=("Segoe UI", 10, "italic"), text_color="#2ED573")
        self.status_lbl.pack(pady=5)
        
        # Gestão de Perfis de Template Web
        f_perfis = ctk.CTkLabelFrame(container, text=" 📂 Templates Web Salvos ")
        f_perfis.pack(fill='both', expand=True, padx=40, pady=20)
        
        btn_frame = ctk.CTkFrame(f_perfis)
        btn_frame.pack(fill='x', pady=(0, 5))
        
        ctk.CTkButton(btn_frame, text="🔄 Atualizar Lista", command=self._atualizar_lista).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="✏️ Renomear Selecionado", command=self._renomear_perfil).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="🗑️ Excluir Selecionado", command=self._excluir_perfil).pack(side='left', padx=2)
        
        style = ttk.Style()
        style.configure("ThumbTemplate.Treeview", rowheight=120, background="#1e1e2e", foreground="#ffffff", fieldbackground="#1e1e2e")
        
        self.tree = ttk.Treeview(f_perfis, columns=("nome",), show="tree", style="ThumbTemplate.Treeview")
        self.tree.column("#0", width=250, stretch=tk.YES)
        self.tree.pack(side='left', fill='both', expand=True)
        
        scroll = ttk.Scrollbar(f_perfis, orient="vertical", command=self.tree.yview)
        scroll.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=scroll.set)
        
        self._atualizar_lista()

    def _atualizar_lista(self):
        self.tree.delete(*self.tree.get_children())
        self.photo_cache.clear()
        
        if not os.path.exists(self.perfis_dir):
            return
            
        for f in os.listdir(self.perfis_dir):
            if f.endswith('.json'):
                nome = f.replace('.json', '')
                
                # Setup item info
                img_path = os.path.join(self.perfis_dir, f"{nome}.jpg")
                photo = None
                
                if PIL_AVAILABLE and os.path.exists(img_path):
                    try:
                        img = Image.open(img_path)
                        # Redimensionar mantendo a proporção para caber em 100px de altura
                        ratio = 100.0 / float(img.size[1])
                        new_width = int((float(img.size[0]) * float(ratio)))
                        img = img.resize((new_width, 100), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.photo_cache[nome] = photo
                    except Exception as e:
                        print(f"Erro ao carregar thumbnail para {nome}: {e}")
                
                if photo:
                    self.tree.insert("", "end", iid=nome, text=f"  {nome}", image=photo)
                else:
                    self.tree.insert("", "end", iid=nome, text=f"  {nome}")

    def _renomear_perfil(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um perfil para renomear.")
            return
            
        nome_antigo = sel[0]
        
        novo_nome = simpledialog.askstring("Renomear Template", "Novo nome do template:", initialvalue=nome_antigo)
        if not novo_nome or not novo_nome.strip() or novo_nome.strip() == nome_antigo:
            return
            
        novo_nome = novo_nome.strip()
        
        # Remove caracteres inválidos para o Windows (como dois pontos, barras, etc)
        novo_nome = "".join(c for c in novo_nome if c.isalnum() or c in (' ', '_', '-')).strip()
        
        if not novo_nome:
            messagebox.showerror("Erro", "O nome fornecido é inválido ou contém apenas caracteres proibidos.")
            return
            
        old_json = os.path.join(self.perfis_dir, f"{nome_antigo}.json")
        old_jpg = os.path.join(self.perfis_dir, f"{nome_antigo}.jpg")
        
        new_json = os.path.join(self.perfis_dir, f"{novo_nome}.json")
        new_jpg = os.path.join(self.perfis_dir, f"{novo_nome}.jpg")
        
        if os.path.exists(new_json):
            messagebox.showerror("Erro", f"Já existe um template chamado '{novo_nome}'.")
            return
            
        try:
            if os.path.exists(old_json):
                os.rename(old_json, new_json)
            if os.path.exists(old_jpg):
                os.rename(old_jpg, new_jpg)
                
            self._atualizar_lista()
            
            # Tenta atualizar a lista de perfis do app principal
            _app = getattr(self.master, "master", None)
            if _app and hasattr(_app, "aba_mapeador"):
                try:
                    _app.aba_mapeador._atualizar_lista_perfis()
                except:
                    pass
                    
            messagebox.showinfo("Sucesso", f"Template renomeado para '{novo_nome}'.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao renomear: {e}")

    def _excluir_perfil(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um perfil para excluir.")
            return
            
        nome = sel[0]
        path_json = os.path.join(self.perfis_dir, f"{nome}.json")
        path_jpg = os.path.join(self.perfis_dir, f"{nome}.jpg")
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o template '{nome}'?"):
            try:
                if os.path.exists(path_json):
                    os.remove(path_json)
                if os.path.exists(path_jpg):
                    os.remove(path_jpg)
                    
                self._atualizar_lista()
                messagebox.showinfo("Sucesso", "Template excluído com sucesso!")
                
                # Se o App principal (Aba 1) existir, tenta atualizar a lista de perfis lá também
                _app = getattr(self.master, "master", None)
                if _app and hasattr(_app, "aba_mapeador"):
                    try:
                        _app.aba_mapeador._atualizar_lista_perfis()
                    except:
                        pass
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")

    def _abrir_estudio(self):
        self.status_lbl.config(text="Ligando servidor Apollo (Porta 8080) e abrindo navegador...")
        
        def run_server():
            try: 
                servidor_web.start_server(8080)
            except Exception as e:
                print("Servidor possivelmente já está rodando:", e)
                
        threading.Thread(target=run_server, daemon=True).start()
        webbrowser.open("http://localhost:8080")
