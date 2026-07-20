import subprocess
import requests
import json
import os
import hashlib
import customtkinter as ctk

class AuthManager:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.token_file = "auth_token.json"
        
    def get_hwid(self):
        try:
            # Captura o UUID da maquina no Windows
            output = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().split('\n')[1].strip()
            if output:
                # Retorna um hash do UUID para não enviar diretamente
                return hashlib.sha256(output.encode()).hexdigest()
        except Exception:
            pass
        return "UNKNOWN_HWID"
        
    def login(self, email, password):
        hwid = self.get_hwid()
        try:
            response = requests.post(f"{self.server_url}/login", json={
                "email": email,
                "password": password,
                "hwid": hwid
            }, timeout=10)
            
            if response.status_code == 200:
                self._save_token(email)
                return True, "Login aprovado."
            else:
                try:
                    err = response.json().get('detail', 'Erro desconhecido.')
                except:
                    err = response.text
                return False, err
        except requests.exceptions.RequestException as e:
            return False, f"Erro de conexão com o servidor: {str(e)}"
            
    def _save_token(self, email):
        # Em producao, isso deve ser encriptado
        with open(self.token_file, 'w') as f:
            json.dump({"email": email, "auth_status": "valid"}, f)
            
    def is_authenticated(self):
        if not os.path.exists(self.token_file):
            return False
            
        try:
            with open(self.token_file, 'r') as f:
                data = json.load(f)
                if data.get("auth_status") == "valid":
                    # TODO: Opcionalmente, pode checar com o servidor silenciosamente aqui
                    return True
        except:
            pass
            
        return False
        
    def logout(self):
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

def show_login_screen(root, on_success):
    auth = AuthManager()
    
    if auth.is_authenticated():
        on_success()
        return

    # Se não estiver autenticado, criamos a tela de login
    # Escondemos a janela principal temporariamente
    root.withdraw()
    
    login_win = ctk.CTkToplevel(root)
    login_win.title("Apollo Studio - Login")
    login_win.geometry("400x450")
    login_win.resizable(False, False)
    # Impede de fechar a janela pelo X para forcar o login
    login_win.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    
    # Manter a janela no topo e focar nela
    login_win.attributes("-topmost", True)
    login_win.grab_set()
    login_win.focus_force()
    
    ctk.CTkLabel(login_win, text="Apollo Studio", font=("Segoe UI", 24, "bold"), text_color="#FFD32A").pack(pady=(40, 10))
    ctk.CTkLabel(login_win, text="Autenticação Necessária", font=("Segoe UI", 14)).pack(pady=(0, 20))
    
    ctk.CTkLabel(login_win, text="E-mail:").pack(anchor="w", padx=50)
    ent_email = ctk.CTkEntry(login_win, width=300)
    ent_email.pack(pady=(0, 15))
    
    ctk.CTkLabel(login_win, text="Senha:").pack(anchor="w", padx=50)
    ent_password = ctk.CTkEntry(login_win, width=300, show="*")
    ent_password.pack(pady=(0, 20))
    
    lbl_error = ctk.CTkLabel(login_win, text="", text_color="#FF4757", font=("Segoe UI", 12))
    lbl_error.pack(pady=(0, 10))
    
    def attempt_login():
        email = ent_email.get().strip()
        pwd = ent_password.get().strip()
        if not email or not pwd:
            lbl_error.configure(text="Preencha todos os campos.")
            return
            
        btn_login.configure(state="disabled", text="Autenticando...")
        login_win.update()
        
        success, msg = auth.login(email, pwd)
        if success:
            login_win.destroy()
            root.deiconify()
            on_success()
        else:
            lbl_error.configure(text=msg)
            btn_login.configure(state="normal", text="Entrar")
            
    btn_login = ctk.CTkButton(login_win, text="Entrar", width=300, fg_color="#9B59B6", hover_color="#8E44AD", command=attempt_login)
    btn_login.pack(pady=10)
    
    hwid = auth.get_hwid()
    ctk.CTkLabel(login_win, text=f"HWID: {hwid[:8]}...", font=("Segoe UI", 10), text_color="gray").pack(side="bottom", pady=10)

