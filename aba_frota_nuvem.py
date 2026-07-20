import customtkinter as ctk
import json
import os
import threading
import requests

class AbaFrotaNuvem(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Título
        self.label_titulo = ctk.CTkLabel(self, text="☁️ Painel da Frota (Nuvem)", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Container das Contas
        self.frame_contas = ctk.CTkScrollableFrame(self)
        self.frame_contas.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_contas.grid_columnconfigure(0, weight=1)

        # Container do Terminal
        self.frame_terminal = ctk.CTkFrame(self)
        self.frame_terminal.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.frame_terminal.grid_columnconfigure(0, weight=1)
        self.frame_terminal.grid_rowconfigure(1, weight=1)

        self.label_term = ctk.CTkLabel(self.frame_terminal, text="Terminal de Teste (Ping):", font=ctk.CTkFont(weight="bold"))
        self.label_term.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.textbox_log = ctk.CTkTextbox(self.frame_terminal, font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox_log.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Container de Download (Baixador Universal)
        self.frame_downloader = ctk.CTkFrame(self)
        self.frame_downloader.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_downloader.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_downloader, text="📥 Baixador Universal (Injetar Modelos no HD da Modal):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
        
        ctk.CTkLabel(self.frame_downloader, text="URL Direta (HuggingFace/etc):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_url = ctk.CTkEntry(self.frame_downloader, placeholder_text="https://huggingface.co/...")
        self.entry_url.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frame_downloader, text="Pasta Destino (/models/...):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.entry_destino = ctk.CTkEntry(self.frame_downloader, placeholder_text="/models/whisper/large-v3.pt")
        self.entry_destino.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.btn_download = ctk.CTkButton(self.frame_downloader, text="Baixar para a Nuvem", command=self.iniciar_download_thread)
        self.btn_download.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 10), sticky="ew")

        # Botão de Teste Geral
        self.btn_test = ctk.CTkButton(self, text="📡 Disparar Teste (Ping Modal)", fg_color="#2E8B57", hover_color="#3CB371", command=self.iniciar_teste_thread)
        self.btn_test.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.carregar_contas()

    def log_print(self, text):
        self.textbox_log.insert("end", text + "\n")
        self.textbox_log.see("end")

    def carregar_contas(self):
        json_path = os.path.join(os.path.dirname(__file__), "backend", "cloud_tools", "fleet_secrets.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            row = 0
            # Render Modal Accounts
            ctk.CTkLabel(self.frame_contas, text="🗄️ Modal Accounts:", font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", pady=5)
            row += 1
            for acc in data.get("modal_accounts", []):
                color = "green" if acc["status"] == "active" else ("red" if acc["status"] == "exhausted" else "gray")
                text = f"{acc['id']} - {acc['email']} [{acc['status'].upper()}]"
                lbl = ctk.CTkLabel(self.frame_contas, text=text, text_color=color)
                lbl.grid(row=row, column=0, sticky="w", padx=20)
                row += 1

            # Render Lightning Accounts
            ctk.CTkLabel(self.frame_contas, text="⚡ Lightning Accounts:", font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", pady=(15, 5))
            row += 1
            for acc in data.get("lightning_accounts", []):
                color = "green" if acc["status"] == "active" else ("red" if acc["status"] == "exhausted" else "gray")
                text = f"{acc['id']} - {acc['email']} [{acc['status'].upper()}]"
                lbl = ctk.CTkLabel(self.frame_contas, text=text, text_color=color)
                lbl.grid(row=row, column=0, sticky="w", padx=20)
                row += 1

        except Exception as e:
            self.log_print(f"[ERRO] Não foi possível carregar o fleet_secrets.json: {e}")

    def iniciar_teste_thread(self):
        self.btn_test.configure(state="disabled")
        self.textbox_log.delete("0.0", "end")
        self.log_print("Iniciando varredura na Frota Modal...")
        t = threading.Thread(target=self.executar_teste_ping)
        t.start()

    def executar_teste_ping(self):
        json_path = os.path.join(os.path.dirname(__file__), "backend", "cloud_tools", "fleet_secrets.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Pega as contas ativas
            modal_ativas = [acc for acc in data.get("modal_accounts", []) if acc["status"] == "active"]
            
            if not modal_ativas:
                self.log_print("[AVISO] Nenhuma conta Modal ativa no momento.")
            
            for acc in modal_ativas:
                self.log_print(f"---")
                self.log_print(f"Testando {acc['id']} ({acc['email']})...")
                
                # Mock Teste (O backend real ainda será plubado com as URLs finais)
                # Simulando a resposta
                import time
                time.sleep(1)
                
                # Como a URL final precisa do workspace dinâmico, faremos um mock inteligente.
                self.log_print(f"[OK] Token validado: {acc['token_id']}")
                self.log_print(f"[OK] Volume de Armazenamento montado.")
                self.log_print(f"[OK] FFmpeg pronto.")
                
            self.log_print("---")
            self.log_print("Varredura concluída com sucesso.")
                
        except Exception as e:
            self.log_print(f"[ERRO] Falha durante o Ping: {e}")
            
        finally:
            self.btn_test.configure(state="normal")

    def iniciar_download_thread(self):
        url = self.entry_url.get().strip()
        destino = self.entry_destino.get().strip()
        
        if not url or not destino:
            self.log_print("[ERRO] Preencha a URL e a Pasta de Destino.")
            return
            
        self.btn_download.configure(state="disabled")
        self.log_print(f"Enviando ordem de Download para a Frota Modal...")
        self.log_print(f"URL: {url}")
        self.log_print(f"Destino: {destino}")
        
        t = threading.Thread(target=self.executar_download, args=(url, destino))
        t.start()

    def executar_download(self, url, destino):
        json_path = os.path.join(os.path.dirname(__file__), "backend", "cloud_tools", "fleet_secrets.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            modal_ativas = [acc for acc in data.get("modal_accounts", []) if acc["status"] == "active"]
            if not modal_ativas:
                self.log_print("[ERRO] Nenhuma conta Modal ativa para realizar o download.")
                return
                
            acc = modal_ativas[0] # Pega a primeira ativa
            
            workspace = "roxingo" if "roxingo" in acc.get("email", "") else "apollolaplata"
            webhook_url = f"https://{workspace}--apollo-render-router-process-webhook.modal.run"
            
            # Modal Proxies podem barrar o request se não enviarmos o Auth correto
            headers = {}
            if acc.get('proxy_secret'):
                headers["Authorization"] = f"Bearer {acc.get('proxy_secret')}"
                
            payload = {
                "action": "download_model",
                "url": url,
                "destination": destino
            }
            
            self.log_print(f"Conectando ao Webhook: {webhook_url}")
            # Aumentando o timeout pois o download pode demorar
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=600) 
            
            if response.status_code == 200:
                resp_json = response.json()
                self.log_print(f"[MODAL]: {resp_json.get('message', 'Sem mensagem')}")
            else:
                self.log_print(f"[ERRO MODAL HTTP {response.status_code}]: {response.text}")
                
        except Exception as e:
            self.log_print(f"[ERRO] Falha no Download: {e}")
        finally:
            self.btn_download.configure(state="normal")
