import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
import json
import os
import base64
import uuid

try:
    from PIL import Image, ImageTk
except ImportError:
    pass

class AbaGeradorIA(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.output_dir = os.path.join(os.getcwd(), "Midias", "Geradas_IA")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Variáveis da UI
        self.var_tipo = tk.StringVar(value="Imagem") # "Imagem" ou "Vídeo"
        self.var_modelo = tk.StringVar(value="flux-schnell")
        self.var_formato = tk.StringVar(value="horizontal")
        self.var_seed = tk.IntVar(value=42)
        
        self.image_ref_paths = []
        self.is_processing = False
        
        self._setup_ui()
        self._atualizar_modelos()
        
    def _setup_ui(self):
        # Cabeçalho
        ctk.CTkLabel(self, text="🎨 Estúdio Visual (Gerador IA Modal)", font=("Segoe UI", 24, "bold"), text_color="#2ED573").pack(pady=(20, 10))
        ctk.CTkLabel(self, text="Gere imagens com FLUX e vídeos com LTX/Wan2.1 usando a infraestrutura Cloud da Modal", font=("Segoe UI", 12)).pack(pady=5)
        
        # Container Principal Dividido (Esquerda: Configurações, Direita: Preview)
        main_container = ctk.CTkFrame(self)
        main_container.pack(expand=True, fill='both', padx=20, pady=10)
        
        # == ESQUERDA: Configurações ==
        left_frame = ctk.CTkFrame(main_container, width=400)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        # Tipo de Mídia
        f_tipo = ctk.CTkFrame(left_frame, fg_color="transparent")
        f_tipo.pack(fill='x', pady=5)
        ctk.CTkLabel(f_tipo, text="O que vamos criar?", font=("Segoe UI", 12, "bold")).pack(anchor='w')
        ctk.CTkRadioButton(f_tipo, text="Imagem (Flux)", variable=self.var_tipo, value="Imagem", command=self._atualizar_modelos).pack(side='left', padx=10, pady=5)
        ctk.CTkRadioButton(f_tipo, text="Vídeo (LTX/Wan)", variable=self.var_tipo, value="Vídeo", command=self._atualizar_modelos).pack(side='left', padx=10, pady=5)
        
        # Modelo
        f_mod = ctk.CTkFrame(left_frame, fg_color="transparent")
        f_mod.pack(fill='x', pady=5)
        ctk.CTkLabel(f_mod, text="Modelo de IA:").pack(anchor='w')
        self.cb_modelo = ctk.CTkOptionMenu(f_mod, variable=self.var_modelo, values=[], width=250)
        self.cb_modelo.pack(anchor='w', pady=2)
        
        # Aspect Ratio
        f_fmt = ctk.CTkFrame(left_frame, fg_color="transparent")
        f_fmt.pack(fill='x', pady=5)
        ctk.CTkLabel(f_fmt, text="Formato (Aspect Ratio):").pack(anchor='w')
        self.cb_formato = ctk.CTkOptionMenu(f_fmt, variable=self.var_formato, values=["horizontal", "vertical", "square"], width=250)
        self.cb_formato.pack(anchor='w', pady=2)
        
        # Seed
        f_seed = ctk.CTkFrame(left_frame, fg_color="transparent")
        f_seed.pack(fill='x', pady=5)
        ctk.CTkLabel(f_seed, text="Semente (Seed aleatório = -1):").pack(anchor='w')
        ctk.CTkEntry(f_seed, textvariable=self.var_seed, width=150).pack(anchor='w', pady=2)
        
        # Prompt
        f_prompt = ctk.CTkFrame(left_frame, fg_color="transparent")
        f_prompt.pack(fill='x', pady=5)
        ctk.CTkLabel(f_prompt, text="Prompt Principal:", font=("Segoe UI", 12, "bold")).pack(anchor='w')
        self.txt_prompt = ctk.CTkTextbox(f_prompt, height=120, font=("Segoe UI", 12), wrap="word")
        self.txt_prompt.pack(fill='both', expand=True, pady=2)
        
        # Referência
        f_ref = ctk.CTkFrame(left_frame, fg_color="transparent")
        f_ref.pack(fill='x', pady=5)
        ctk.CTkLabel(f_ref, text="Imagem Base (Flux Redux e Vídeo):").pack(anchor='w')
        
        btn_ref_frame = ctk.CTkFrame(f_ref, fg_color="transparent")
        btn_ref_frame.pack(fill='x')
        self.btn_ref = ctk.CTkButton(btn_ref_frame, text="Adicionar", command=self._selecionar_referencia, width=80)
        self.btn_ref.pack(side='left', pady=2)
        
        self.btn_clear_ref = ctk.CTkButton(btn_ref_frame, text="Limpar", command=self._limpar_referencias, width=60, fg_color="#C0392B", hover_color="#922B21")
        self.btn_clear_ref.pack(side='left', padx=5, pady=2)
        
        self.lbl_ref_path = ctk.CTkLabel(btn_ref_frame, text="0 imagens anexadas", font=("Segoe UI", 9, "italic"))
        self.lbl_ref_path.pack(side='left', padx=5)
        
        # Botão Gerar
        self.btn_gerar = ctk.CTkButton(left_frame, text="🚀 GERAR (MODAL CLOUD)", command=self._gerar_conteudo, height=50, font=("Segoe UI", 14, "bold"), fg_color="#1E3A8A")
        self.btn_gerar.pack(fill='x', pady=20)
        
        self.lbl_status = ctk.CTkLabel(left_frame, text="", text_color="#F1C40F")
        self.lbl_status.pack()

        # == DIREITA: Preview e Logs ==
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(right_frame, text="Preview da Geração", font=("Segoe UI", 12, "bold")).pack(pady=5)
        
        self.lbl_preview = ctk.CTkLabel(right_frame, text="Nenhuma mídia gerada ainda.", width=400, height=300, fg_color="#1E1E2E")
        self.lbl_preview.pack(pady=10)
        
        ctk.CTkButton(right_frame, text="📂 Abrir Pasta de Mídias", command=lambda: os.startfile(self.output_dir)).pack(pady=5)
        
        ctk.CTkLabel(right_frame, text="Logs do Sistema Modal:").pack(anchor='w', pady=(10,0))
        self.txt_logs = ctk.CTkTextbox(right_frame, height=200, font=("Consolas", 12), text_color="#00FF00", fg_color="#1E1E2E")
        self.txt_logs.pack(fill='both', expand=True, pady=5)
        self.txt_logs.configure(state="disabled")

    def _atualizar_modelos(self):
        tipo = self.var_tipo.get()
        if tipo == "Imagem":
            modelos = ["flux-schnell", "flux-dev"]
            self.cb_modelo.configure(values=modelos)
            if self.var_modelo.get() not in modelos:
                self.var_modelo.set("flux-schnell")
        else:
            modelos = ["wan", "ltx"]
            self.cb_modelo.configure(values=modelos)
            if self.var_modelo.get() not in modelos:
                self.var_modelo.set("wan")
            
    def _selecionar_referencia(self):
        caminhos = filedialog.askopenfilenames(title="Selecionar Imagens de Referência", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if caminhos:
            if not getattr(self, 'image_ref_paths', None):
                self.image_ref_paths = []
            
            if len(self.image_ref_paths) + len(caminhos) > 4:
                messagebox.showwarning("Aviso", "Máximo de 4 imagens de referência permitidas.")
                return
                
            self.image_ref_paths.extend(caminhos)
            self.lbl_ref_path.configure(text=f"{len(self.image_ref_paths)} imagens anexadas")

    def _limpar_referencias(self):
        self.image_ref_paths = []
        self.lbl_ref_path.configure(text="0 imagens anexadas")
            
    def _log(self, mensagem):
        self.txt_logs.configure(state='normal')
        self.txt_logs.insert('end', mensagem + "\n")
        self.txt_logs.see('end')
        self.txt_logs.configure(state='disabled')
        self.update_idletasks()
        
    def _gerar_conteudo(self):
        if self.is_processing:
            return
            
        prompt = self.txt_prompt.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning("Aviso", "O prompt não pode estar vazio!")
            return
            
        self.is_processing = True
        self.btn_gerar.configure(state="disabled", text="Gerando... Aguarde")
        self.lbl_status.configure(text="Conectando à Modal Cloud...")
        self.txt_logs.configure(state='normal')
        self.txt_logs.delete('1.0', 'end')
        self.txt_logs.configure(state='disabled')
        self.lbl_preview.configure(image=None, text="⏳ Processando na nuvem...")
        
        threading.Thread(target=self._tarefa_background, args=(prompt,), daemon=True).start()
        
    def _tarefa_background(self, prompt):
        tipo = self.var_tipo.get()
        modelo = self.var_modelo.get()
        formato = self.var_formato.get()
        seed = self.var_seed.get()
        
        if seed == -1:
            import random
            seed = random.randint(1, 999999)
            self._log(f"Seed aleatório gerado: {seed}")
            
        try:
            if tipo == "Imagem":
                self._log(f"Iniciando requisição Imagem -> {modelo} ({formato})")
                url = "http://127.0.0.1:8080/api/studio/modal/generate/image"
                
                img_b64_list = []
                if getattr(self, 'image_ref_paths', None):
                    for p in self.image_ref_paths:
                        with open(p, "rb") as img_file:
                            img_b64_list.append(base64.b64encode(img_file.read()).decode("utf-8"))
                    if len(img_b64_list) > 0:
                        self._log(f"Enviando {len(img_b64_list)} imagens para o FLUX.1 Redux")
                
                payload = {
                    "prompt": prompt,
                    "model": modelo,
                    "format": formato,
                    "seed": seed,
                    "reference_images_base64": img_b64_list
                }
            else:
                self._log(f"Iniciando requisição Vídeo -> {modelo} ({formato})")
                url = "http://127.0.0.1:8080/api/studio/modal/generate/video"
                img_b64 = None
                if getattr(self, 'image_ref_paths', None) and len(self.image_ref_paths) > 0:
                    with open(self.image_ref_paths[0], "rb") as img_file:
                        img_b64 = base64.b64encode(img_file.read()).decode("utf-8")
                        self._log(f"Imagem de referência carregada ({len(img_b64)} bytes)")
                        
                payload = {
                    "prompt": prompt,
                    "model": modelo,
                    "aspect_ratio": formato,
                    "preset": "fast",
                    "duration": 5,
                    "seed": seed,
                    "image_base64": img_b64
                }

            # Envia a requisição via proxy
            self._log(f"Enviando POST para: {url}")
            # Habilitar stream para ler pedaços de progresso
            response = requests.post(url, json=payload, stream=True, timeout=600)
            
            if response.status_code != 200:
                self._log(f"❌ Erro HTTP {response.status_code}: {response.text}")
                self._finalizar_erro()
                return

            resultado_final = None
            for chunk in response.iter_lines():
                if chunk:
                    decoded = chunk.decode("utf-8").strip()
                    if decoded:
                        self._log(f"[Modal] Recebeu chunck: {decoded[:100]}...")
                        try:
                            dados = json.loads(decoded)
                            if "status" in dados:
                                if dados["status"] == "success":
                                    resultado_final = dados
                                elif dados["status"] == "error":
                                    self._log(f"❌ Erro retornado pela Modal: {dados.get('message')}")
                                    self._finalizar_erro()
                                    return
                        except Exception:
                            # Ignorar linhas mal formatadas (ex: ping messages)
                            pass

            if not resultado_final:
                self._log("❌ Nenhum resultado válido retornado pela API.")
                self._finalizar_erro()
                return

            url_midia = resultado_final.get("url") or resultado_final.get("video_url")
            img_b64_retorno = resultado_final.get("image_base64")

            if not url_midia and not img_b64_retorno:
                self._log("❌ URL de mídia ou imagem base64 não encontrada na resposta final.")
                self._finalizar_erro()
                return
                
            self._log(f"✅ Geração concluída!")
            self._log("Iniciando salvamento da mídia para o computador...")
            
            extensao = ".mp4" if tipo == "Vídeo" else ".jpg"
            filename = f"{modelo}_{uuid.uuid4().hex[:8]}{extensao}"
            filepath = os.path.join(self.output_dir, filename)
            
            if img_b64_retorno:
                # É imagem retornada em base64
                with open(filepath, 'wb') as f:
                    f.write(base64.b64decode(img_b64_retorno))
                self._log(f"💾 Mídia salva em: {filepath}")
                self.after(0, lambda: self._finalizar_sucesso(filepath, tipo))
            else:
                # Fazer download do arquivo gerado
                r_download = requests.get(url_midia, stream=True)
                if r_download.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in r_download.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self._log(f"💾 Mídia salva em: {filepath}")
                    
                    # Atualizar UI
                    self.after(0, lambda: self._finalizar_sucesso(filepath, tipo))
                else:
                    self._log(f"❌ Erro ao baixar a mídia: {r_download.status_code}")
                    self._finalizar_erro()

        except Exception as e:
            self._log(f"❌ Erro crasso de requisição: {str(e)}")
            self._finalizar_erro()
            
    def _finalizar_erro(self):
        self.is_processing = False
        self.after(0, lambda: self.btn_gerar.configure(state="normal", text="🚀 GERAR (MODAL CLOUD)"))
        self.after(0, lambda: self.lbl_status.configure(text="Erro ao gerar mídia. Verifique os logs."))
        self.after(0, lambda: self.lbl_preview.configure(text="Erro na geração"))
        
    def _finalizar_sucesso(self, filepath, tipo):
        self.is_processing = False
        self.btn_gerar.configure(state="normal", text="🚀 GERAR (MODAL CLOUD)")
        self.lbl_status.configure(text=f"Mídia salva com sucesso!")
        
        if tipo == "Imagem":
            try:
                img = Image.open(filepath)
                # Resize para preview
                img.thumbnail((400, 300))
                self.photo_img = ImageTk.PhotoImage(img)
                self.lbl_preview.configure(image=self.photo_img, text="")
            except:
                self.lbl_preview.configure(text="Imagem gerada (Sem preview suportado)")
        else:
            self.lbl_preview.configure(text="Vídeo MP4 gerado!\nAbra a pasta para assistir.")
