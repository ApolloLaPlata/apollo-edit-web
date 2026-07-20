import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import webbrowser
import socket

class AbaTimelineWeb(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.server_process = None
        self.port = 8000
        
        self.setup_ui()
        self.start_server()
        # Vincula o shutdown do servidor ao fechamento do widget
        self.bind('<Destroy>', self._on_destroy)

    def setup_ui(self):
        # UI with modern styling matching the app
        self.configure()
        
        title = ctk.CTkLabel(self, text="🌐 Apollo Web Timeline Editor", font=("Segoe UI", 24, "bold"))
        title.pack(pady=(40, 10))
        
        desc = ctk.CTkLabel(self, text="O motor de edição não-linear avançado opera em uma interface web robusta.", 
                        font=("Segoe UI", 12))
        desc.pack(pady=5)
        
        self.status_lbl = ctk.CTkLabel(self, text="Status: Iniciando Servidor...", font=("Segoe UI", 10, "italic"))
        self.status_lbl.pack(pady=(5, 30))
        
        btn_open = ctk.CTkButton(self, text="Abrir Editor no Navegador 🌐", font=("Segoe UI", 16, "bold"), cursor="hand2",
                               command=self.open_browser)
        btn_open.pack(pady=(30, 20), ipadx=40, ipady=15)
        
        # Info about features
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(info_frame, text="✨ Recursos Habilitados:", font=("Segoe UI", 14, "bold")).pack(anchor='w', pady=(0, 10))
        features = [
            "• Múltiplas Trilhas (Video 1, B-Roll, Músicas, Narração)",
            "• Transições Visuais Nativas (Fade, Dissolve, Zoom)",
            "• Painel de Inspetor (Escala, Opacidade, Posição X/Y)",
            "• Serialização de Projetos (.json) para Backup Seguro",
            "• Fila de Renderização Python (Exportações não travam o PC)"
        ]
        for f in features:
            ctk.CTkLabel(info_frame, text=f, font=("Segoe UI", 12)).pack(anchor='w', pady=4)

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def start_server(self):
        if self.server_process:
            try:
                self.server_process.kill()
            except:
                pass
            
        if self.is_port_in_use(self.port):
            self.status_lbl.configure(text=f"Status: O Servidor Backend já está rodando na porta {self.port}! 🟢")
            return
            
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'servidor_web.py')
        if not os.path.exists(script_path):
            self.status_lbl.configure(text="Erro: arquivo servidor_web.py não encontrado!")
            return
            
        CREATE_NO_WINDOW = 0x08000000
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, script_path],
                creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.status_lbl.configure(text=f"Status: Motor Local Ativo na porta {self.port} 🟢")
        except Exception as e:
            self.status_lbl.configure(text=f"Erro ao iniciar servidor: {e}")

    def open_browser(self):
        webbrowser.open(f'http://localhost:{self.port}/timeline.html')

    def _on_destroy(self, event=None):
        """Chamado quando o widget é destruído — mata o servidor backend."""
        if self.server_process and self.server_process.poll() is None:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=3)
            except Exception:
                try:
                    self.server_process.kill()
                except Exception:
                    pass
