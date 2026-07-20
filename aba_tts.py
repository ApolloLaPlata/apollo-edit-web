import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import subprocess

class AbaGeracaoTTS(ctk.CTkFrame):
    def __init__(self, parent, api, config_manager=None):
        super().__init__(parent)
        # Cache de personagens carregado via config_manager
        if config_manager is not None:
            _p = config_manager.get('personagens', {})
            self.personagens_cache = dict(_p) if _p else {}
        else:
            self.personagens_cache = {}
        
        # Armazena a API
        self.api = api
        
        # Aplica cor azul piscina ao fundo da aba
        self.configure()

        # Adiciona tratamento de erro para evitar KeyboardInterrupt
        try:
            ctk.CTkLabel(self, text="🎤 Gerador de Voz (TTS) - VoiceMaker API", font=("Segoe UI", 16, "bold")).pack(pady=10)
        except KeyboardInterrupt:
            print("⚠️ KeyboardInterrupt durante criação do título TTS - continuando...")
            return
        except Exception as e:
            print(f"⚠️ Erro ao criar label do título TTS: {e}")
            return

        # Frame principal com scroll
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Frame esquerdo - Configurações
        left_frame = ctk.CTkLabelFrame(main_frame, text="⚙️ Configurações")
        left_frame.pack(side='left', fill='y', padx=(0, 10))

        # Seleção de Personagem
        ctk.CTkLabel(left_frame, text="👤 Personagem:").pack(anchor='w', pady=2)
        self.personagem_var = tk.StringVar()
        
        # Verifica se há personagens disponíveis
        if self.personagens_cache:
            personagens_lista = list(self.personagens_cache.keys())
            self.personagem_menu = ctk.CTkOptionMenu(left_frame, variable=self.personagem_var, values=personagens_lista)
            self.personagem_menu.pack(fill='x', pady=(0, 10))
            self.personagem_menu.set(personagens_lista[0] if personagens_lista else "")
            self.personagem_menu.bind('<<ComboboxSelected>>', self.atualizar_configuracoes_personagem)
        else:
            # Fallback se não houver personagens
            self.personagem_menu = ctk.CTkOptionMenu(left_frame, variable=self.personagem_var, values=["Nenhum personagem disponível"], state='disabled')
            self.personagem_menu.pack(fill='x', pady=(0, 10))
            self.personagem_var.set("Nenhum personagem disponível")

        # Configurações de Voz
        ctk.CTkLabel(left_frame, text="🎵 Configurações de Voz:", font=("Segoe UI", 10, "bold")).pack(anchor='w', pady=(10, 5))

        # Engine
        ctk.CTkLabel(left_frame, text="Engine:").pack(anchor='w')
        self.engine_var = tk.StringVar(value="proplus")
        engine_frame = ctk.CTkFrame(left_frame)
        engine_frame.pack(fill='x', pady=2)
        ttk.Radiobutton(engine_frame, text="Pro+", variable=self.engine_var, value="proplus").pack(side='left')
        ttk.Radiobutton(engine_frame, text="Neural", variable=self.engine_var, value="neural").pack(side='left')
        ttk.Radiobutton(engine_frame, text="Standard", variable=self.engine_var, value="standard").pack(side='left')

        # Idioma
        ctk.CTkLabel(left_frame, text="🌍 Idioma:").pack(anchor='w', pady=(10, 2))
        self.idioma_var = tk.StringVar(value="pt-BR")
        idiomas = ["pt-BR", "en-US", "es-ES", "fr-FR", "de-DE", "it-IT", "ja-JP", "ko-KR", "zh-CN", "ar-SA"]
        self.idioma_menu = ctk.CTkOptionMenu(left_frame, variable=self.idioma_var, values=idiomas)
        self.idioma_menu.pack(fill='x', pady=(0, 10))

        # Efeito
        ctk.CTkLabel(left_frame, text="🎭 Efeito:").pack(anchor='w')
        self.efeito_var = tk.StringVar(value="news")
        efeitos = ["default", "news", "conversational", "assistant", "happy", "breathing", "soft", "whispered"]
        self.efeito_menu = ctk.CTkOptionMenu(left_frame, variable=self.efeito_var, values=efeitos)
        self.efeito_menu.pack(fill='x', pady=(0, 10))

        # Controles de Áudio
        ctk.CTkLabel(left_frame, text="🎛️ Controles de Áudio:", font=("Segoe UI", 10, "bold")).pack(anchor='w', pady=(10, 5))

        # Volume
        ctk.CTkLabel(left_frame, text="🔊 Volume (-20 a 20):").pack(anchor='w')
        self.volume_var = tk.IntVar(value=0)
        self.volume_scale = ttk.Scale(left_frame, from_=-20, to=20, variable=self.volume_var, orient='horizontal')
        self.volume_scale.pack(fill='x', pady=(0, 5))
        self.volume_label = ctk.CTkLabel(left_frame, text="0")
        self.volume_label.pack()
        self.volume_scale.configure(command=lambda v: self.volume_label.configure(text=str(int(float(v)))))

        # Velocidade
        ctk.CTkLabel(left_frame, text="⚡ Velocidade (-100 a 100):").pack(anchor='w', pady=(10, 2))
        self.velocidade_var = tk.IntVar(value=0)
        self.velocidade_scale = ttk.Scale(left_frame, from_=-100, to=100, variable=self.velocidade_var, orient='horizontal')
        self.velocidade_scale.pack(fill='x', pady=(0, 5))
        self.velocidade_label = ctk.CTkLabel(left_frame, text="0")
        self.velocidade_label.pack()
        self.velocidade_scale.configure(command=lambda v: self.velocidade_label.configure(text=str(int(float(v)))))

        # Pitch
        ctk.CTkLabel(left_frame, text="🎵 Pitch (-100 a 100):").pack(anchor='w', pady=(10, 2))
        self.pitch_var = tk.IntVar(value=0)
        self.pitch_scale = ttk.Scale(left_frame, from_=-100, to=100, variable=self.pitch_var, orient='horizontal')
        self.pitch_scale.pack(fill='x', pady=(0, 5))
        self.pitch_label = ctk.CTkLabel(left_frame, text="0")
        self.pitch_label.pack()
        self.pitch_scale.configure(command=lambda v: self.pitch_label.configure(text=str(int(float(v)))))

        # Sample Rate
        ctk.CTkLabel(left_frame, text="📊 Sample Rate:").pack(anchor='w', pady=(10, 2))
        self.sample_rate_var = tk.StringVar(value="48000")
        sample_rates = ["48000", "44100", "24000", "22050", "16000", "8000"]
        self.sample_rate_menu = ctk.CTkOptionMenu(left_frame, variable=self.sample_rate_var, values=sample_rates)
        self.sample_rate_menu.pack(fill='x', pady=(0, 10))

        # Frame direito - Área de texto e controles
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)

        # Campo de Texto para o Roteiro
        ctk.CTkLabel(right_frame, text="📝 Cole o roteiro aqui:").pack(anchor='w', pady=5)
        self.roteiro_text = ctk.CTkTextbox(right_frame, height=250, wrap='word', font=("Consolas", 14))
        self.roteiro_text.pack(fill='both', expand=True, pady=(0, 10))

        # Novo Campo: Emoção / Instrução Adicional (Modelo 3 e 4)
        ctk.CTkLabel(right_frame, text="🧠 Emoção / Instrução Adicional (Apenas Google Gemini / OpenAI):", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(5, 2))
        self.emocao_adicional_texto = ctk.CTkTextbox(right_frame, height=60, wrap='word', font=("Consolas", 14))
        self.emocao_adicional_texto.pack(fill='x', pady=(0, 10))
        
        # Opcional label explicativa
        ctk.CTkLabel(right_frame, text="Exemplo: Fale sussurrando com medo, ou Fale dando gargalhadas.", font=("Segoe UI", 8, "italic"), text_color="gray").pack(anchor='w', pady=(0, 10))

        # Frame de botões
        btn_frame = ctk.CTkFrame(right_frame)
        btn_frame.pack(fill='x', pady=10)

        # Botão para gerar o áudio
        self.btn_gerar = ctk.CTkButton(btn_frame, text="🎤 Gerar Áudio TTS", command=self.gerar_audio)
        self.btn_gerar.pack(side='left', padx=(0, 10))

        # Botão para testar voz (do modelo global atual)
        self.btn_testar = ctk.CTkButton(btn_frame, text="🔊 Testar Voz (Padrão)", command=self.testar_voz)
        self.btn_testar.pack(side='left', padx=(0, 10))

        # Botão para testar EXCLUSIVAMENTE o Gemini/Google TTS
        self.btn_testar_google = ctk.CTkButton(btn_frame, text="🤖 Testar Voz do Google TTS", command=self.testar_google_tts)
        self.btn_testar_google.pack(side='left', padx=(0, 10))

        # Botão para limpar
        self.btn_limpar = ctk.CTkButton(btn_frame, text="🧹 Limpar", command=self.limpar_campos)
        self.btn_limpar.pack(side='left')

        # Status bar
        self.status_var = tk.StringVar(value="✅ Pronto para gerar áudio TTS")
        self.status_label = ctk.CTkLabel(right_frame, textvariable=self.status_var, text_color='green')
        self.status_label.pack(pady=5)

        # Inicializa configurações do personagem (se houver personagens disponíveis)
        if self.personagens_cache:
            self.atualizar_configuracoes_personagem()
        else:
            print("⚠️  Nenhum personagem disponível para inicializar configurações")

    def atualizar_configuracoes_personagem(self, event=None):
        """Atualiza as configurações baseadas no personagem selecionado"""
        personagem = self.personagem_var.get()
        if personagem in self.personagens_cache:
            config = self.personagens_cache[personagem]
            print(f"🔄 Atualizando configurações para: {personagem}")
            
            # Atualiza engine se disponível
            if 'engine' in config:
                self.engine_var.set(config['engine'])
            
            # Atualiza idioma se disponível
            if 'idioma' in config:
                self.idioma_var.set(config['idioma'])
            
            # Atualiza efeito se disponível
            if 'efeito' in config:
                self.efeito_var.set(config['efeito'])
            
            print(f"✅ Configurações atualizadas: Engine={self.engine_var.get()}, Idioma={self.idioma_var.get()}, Efeito={self.efeito_var.get()}")
        else:
            print(f"⚠️  Personagem '{personagem}' não encontrado na configuração")

    def gerar_audio(self):
        """Gera áudio TTS usando as configurações selecionadas"""
        if self.api is None:
            messagebox.showerror("Erro", "API VoiceMaker não disponível")
            return
        
        texto = self.roteiro_text.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "Digite um texto para gerar o áudio")
            return
        
        # Configurações do TTS
        personagem = self.personagem_var.get()
        if personagem not in self.personagens_cache:
            messagebox.showerror("Erro", "Selecione um personagem válido")
            return
            
        voice_id = self.personagens_cache[personagem].get('vozes_voicemaker', '')
        if not voice_id:
            messagebox.showerror("Erro", "Personagem não possui voz configurada")
            return
        
        # Seleciona local para salvar
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
            title="Salvar Áudio TTS Como...",
            initialfile=f"tts_{personagem.lower().replace(' ', '_')}.mp3"
        )
        
        if not output_path:
            return
        
        try:
            self.status_var.set("🔄 Gerando áudio TTS...")
            self.btn_gerar.configure(state='disabled')
            
            # Verifica se a API está disponível
            if self.api is None:
                print("❌ API não disponível, tentando criar nova instância...")
                try:
                    from tts_manager import TTSManager
                    from config_manager import ConfigManager
                    config = ConfigManager()
                    self.api = TTSManager(config)
                    print("✅ Nova instância da API criada")
                except Exception as e:
                    print(f"❌ Erro ao criar API: {e}")
                    self.status_var.set("❌ API não disponível")
                    messagebox.showerror("Erro", "API do VoiceMaker não está disponível. Verifique a configuração.")
                    return
            
            # Parâmetros da API
            params = {
                "Engine": self.engine_var.get(),
                "LanguageCode": self.idioma_var.get(),
                "Effect": self.efeito_var.get(),
                "MasterVolume": str(self.volume_var.get()),
                "MasterSpeed": str(self.velocidade_var.get()),
                "MasterPitch": str(self.pitch_var.get()),
                "SampleRate": self.sample_rate_var.get(),
                "emocao_adicional": self.emocao_adicional_texto.get("1.0", tk.END).strip()
            }
            
            # Gera o áudio
            print(f"🎤 Gerando TTS com voz: {voice_id}")
            print(f"📝 Texto: {texto[:50]}...")
            print(f"⚙️ Parâmetros: {params}")
            
            success = self.api.generate_audio(personagem, texto, output_path, **params)
            
            if success:
                try:
                    from database_manager import db
                    # Puxa o ID do canal se disponível (via ConfigManager singleton)
                    canal_id = None
                    try:
                        from config_manager import ConfigManager
                        config = ConfigManager()
                        if config.workspace_dir:
                            canal_id = db.get_canal_id(os.path.basename(config.workspace_dir))
                    except:
                        pass
                    db.set_memoria("ultimo_audio_tts", output_path, canal_id=canal_id)
                except Exception as db_err:
                    print(f"⚠️ Erro ao salvar na Memória Ativa: {db_err}")

                self.status_var.set(f"✅ Áudio gerado com sucesso: {os.path.basename(output_path)}")
                messagebox.showinfo("Sucesso", f"Áudio TTS gerado com sucesso!\nSalvo em: {output_path}")
            else:
                self.status_var.set("❌ Erro ao gerar áudio TTS")
                messagebox.showerror("Erro", "Falha ao gerar áudio TTS")
                
        except Exception as e:
            self.status_var.set(f"❌ Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao gerar áudio: {str(e)}")
        finally:
            self.btn_gerar.configure(state='normal')

    def testar_google_tts(self):
        """Testa explicitamente o Google/Gemini TTS consultando as configurações"""
        try:
            from gemini_tts_api import GeminiTTSProvider
            from config_manager import ConfigManager
        except ImportError:
            messagebox.showerror("Erro", "Módulo Gemini TTS não encontrado.")
            return
            
        texto = self.roteiro_text.get("1.0", tk.END).strip()
        if not texto:
            texto = "Olá! Este é um teste da voz nativa sendo injetada pela chave de API do Gemini."
            self.roteiro_text.delete("1.0", tk.END)
            self.roteiro_text.insert("1.0", texto)
            
        personagem = self.personagem_var.get()
        if personagem not in self.personagens_cache:
            messagebox.showerror("Erro", "Selecione um personagem válido na aba")
            return
            
        config = ConfigManager()
        char_config = config.get_personagem(personagem)
        
        voice_id = char_config.get('voz_google_tts', '')
        if not voice_id:
            messagebox.showerror("Aviso", "Personagem não possui 'Voz Google TTS' (Modo 3) configurada.\n\nVá na Aba de Configurações > Cadastro de Personagens, selecione este personagem e crie o cadastro da voz Gemini (ex: Puck, Aoede).")
            return

        instruction = char_config.get('instrucao_base_tts', '')

        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")],
            title="Salvar Teste Google TTS Como...",
            initialfile=f"teste_google_{personagem.lower().replace(' ', '_')}.mp3"
        )
        if not output_path:
            return
            
        self.status_var.set("🔄 Checando chaves e baixando áudio do Google API...")
        if hasattr(self, 'btn_testar_google'):
            self.btn_testar_google.configure(state='disabled')
        self.update()
        
        def _thread_test():
            try:
                gemini_provider = GeminiTTSProvider(config)
                success = gemini_provider.generate_tts(
                    text=texto,
                    voice_id=voice_id,
                    output_path=output_path,
                    instruction_prompt=instruction
                )
                if success:
                    try:
                        from database_manager import db
                        canal_id = None
                        try:
                            if config.workspace_dir:
                                canal_id = db.get_canal_id(os.path.basename(config.workspace_dir))
                        except: pass
                        db.set_memoria("ultimo_audio_tts", output_path, canal_id=canal_id)
                    except: pass
                    
                    self.after(0, lambda: self.status_var.set(f"✅ Áudio Google gerado com sucesso!"))
                    self.after(0, lambda: messagebox.showinfo("Sucesso", f"Áudio gerado diretamente pela API do Gemini!\nSalvo em: {output_path}\n\nO cérebro de rotação tentou buscar e faturar a chave automaticamente. Verifique no terminal os logs de cotas (429) caso tenhamos falhado de início, mas como você viu, conseguimos tirar áudio dessa API!"))
                else:
                    self.after(0, lambda: self.status_var.set("❌ Falha na API do Google TTS"))
                    self.after(0, lambda: messagebox.showerror("Erro", "Falha ao requisitar áudio do Gemini TTS. Todas as chaves falharam com erro, ou há problema de Cota/Saldo. Verifique o console."))
            except Exception as e:
                self.after(0, lambda e=e: self.status_var.set(f"❌ Erro Crítico: {str(e)}"))
                self.after(0, lambda e=e: messagebox.showerror("Erro Crítico", str(e)))
            finally:
                if hasattr(self, 'btn_testar_google'):
                    self.after(0, lambda: self.btn_testar_google.configure(state='normal'))
                    
        import threading
        threading.Thread(target=_thread_test, daemon=True).start()

    def testar_voz(self):
        """Testa a voz com um texto de exemplo"""
        texto_teste = "Olá! Este é um teste da voz selecionada."
        self.roteiro_text.delete("1.0", tk.END)
        self.roteiro_text.insert("1.0", texto_teste)
        self.gerar_audio()

    def limpar_campos(self):
        """Limpa todos os campos da interface"""
        self.roteiro_text.delete("1.0", tk.END)
        self.volume_var.set(0)
        self.velocidade_var.set(0)
        self.pitch_var.set(0)
        self.status_var.set("✅ Pronto para gerar áudio TTS")


# --- ABA 2: VÍDEO DO NARRADOR ---