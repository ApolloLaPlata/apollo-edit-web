import customtkinter as ctk
import os
import threading
import subprocess
import shutil
import uuid
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from video_rvc_processor import VideoRVCProcessor
from audio_processor import AudioProcessor

class AbaInferenciaVideo(ctk.CTkFrame):
    def __init__(self, parent, config_manager, personagens_dict):
        super().__init__(parent)
        self.config_manager = config_manager
        self.personagens_dict = personagens_dict
        
        self.processor = VideoRVCProcessor(config_manager, logger=self.log)
        
        self.processing = False
        
        # A fila agora guarda dicts: {"id": str, "path": str, "char_var": tk.StringVar, "thumb_path": str, "img_ref": ImageTk, "ui_frame": Frame}
        self.queue_items = []
        
        # Temp dir for thumbnails
        self.thumb_dir = os.path.join(os.getcwd(), "Midias", "Thumbs_Temp")
        os.makedirs(self.thumb_dir, exist_ok=True)
        
        self.setup_ui()
        
    def setup_ui(self):
        self.configure()
        
        # Titulo
        ctk.CTkLabel(self, text="🎬 Dublagem Externa de Vídeo (RVC + Demucs)", font=("Segoe UI", 16, "bold"), text_color='#1E3A8A').pack(pady=10)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        left_frame = ctk.CTkLabelFrame(main_frame, text="⚙️ Configurações e Seleção")
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Tipo de Selecao
        ctk.CTkLabel(left_frame, text="Mídia de Entrada:").pack(anchor='w', pady=(5, 2))
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ctk.CTkButton(btn_frame, text="📄 Add Vídeo", command=self.add_single_video).pack(side='left', padx=(0,2), fill='x', expand=True)
        ctk.CTkButton(btn_frame, text="📁 Add Pasta", command=self.add_folder).pack(side='left', padx=(2,0), fill='x', expand=True)
        
        ctk.CTkButton(left_frame, text="🗑️ Limpar Fila", command=self.clear_queue).pack(fill='x', pady=5)
        
        # Personagem Fallback
        ctk.CTkLabel(left_frame, text="👤 Padrão Global (Fallback):", font=("Segoe UI", 9, "bold")).pack(anchor='w', pady=(15, 2))
        ctk.CTkLabel(left_frame, text="(Para novos itens na fila)", font=("Segoe UI", 8)).pack(anchor='w')
        
        self.personagem_var = tk.StringVar()
        self.personagens_lista = list(self.personagens_dict.keys()) if self.personagens_dict else ["Nenhum"]
        self.personagens_lista.insert(0, "Automático (Pelo Nome)")
        
        self.personagem_menu = ctk.CTkOptionMenu(left_frame, variable=self.personagem_var, values=self.personagens_lista)
        self.personagem_menu.pack(fill='x', pady=5)
        if self.personagens_lista:
            self.personagem_menu.set("Automático (Pelo Nome)")
            
        # Opções
        self.skip_demucs_var = tk.BooleanVar(value=False)
        ctk.CTkSwitch(left_frame, text="Pular Demucs (Vídeo Seco)", variable=self.skip_demucs_var).pack(anchor='w', pady=(15, 2))

        # Action Botao
        self.btn_process = ctk.CTkButton(left_frame, text="🚀 INICIAR DUBLAGEM", command=self.start_processing)
        self.btn_process.pack(fill='x', pady=(20, 0), ipady=10)

        # Right frame - Queue and Logs
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side='left', expand=True, fill='both')
        
        # Fila Rolável
        ctk.CTkLabel(right_frame, text="📋 Cenas para Processar:", font=("Segoe UI", 10, "bold")).pack(anchor='w')
        
        queue_container = ctk.CTkFrame(right_frame)
        queue_container.pack(fill='both', expand=True, pady=5)
        
        self.canvas = tk.Canvas(queue_container)
        scrollbar = ttk.Scrollbar(queue_container, orient="vertical", command=self.canvas.yview)
        
        self.queue_frame = ctk.CTkFrame(self.canvas)
        
        self.queue_window = self.canvas.create_window((0, 0), window=self.queue_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.queue_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.queue_window, width=e.width))

        # Configurar wheel event para scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Logs
        ctk.CTkLabel(right_frame, text="📝 Logs da Operação:").pack(anchor='w', pady=(10, 2))
        log_frame = ctk.CTkFrame(right_frame)
        log_frame.pack(fill='both', expand=True, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=200, font=("Consolas", 12), text_color="#00FF00")
        self.log_text.pack(side='left', fill='both', expand=True)
        self.log_text.configure(state='disabled')
        self.log_text.pack(side='left', fill='both', expand=True)
        
        # Init visual clear
        self._update_queue_ui()
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert('end', message + "\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        self.update_idletasks()

    def detect_character_from_name(self, filepath):
        filename = os.path.basename(filepath).lower()
        personagens_reais = [p for p in self.personagens_lista if p != "Automático (Pelo Nome)"]
        for p_name in personagens_reais:
            if p_name.lower() in filename or p_name.lower().replace(" ", "_") in filename:
                return p_name
        return None

    def create_thumbnail(self, video_path, item_id):
        thumb_path = os.path.join(self.thumb_dir, f"thumb_{item_id}.jpg")
        # Extract 1 frame at 00:00:01 (or 00:00:00) using ffmpeg invisibly!
        try:
            cmd = ["ffmpeg", "-y", "-i", video_path, "-vframes", "1", "-s", "120x120", "-f", "image2", thumb_path]
            subprocess.run(cmd, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            return thumb_path if os.path.exists(thumb_path) else None
        except Exception:
            return None

    def append_item_to_queue(self, video_path, forced_character=None, is_dupe=False):
        item_id = str(uuid.uuid4())[:8]
        
        # Decide initial char based on file name or global default
        initial_char = forced_character
        if not initial_char:
            global_fallback = self.personagem_var.get()
            if global_fallback == "Automático (Pelo Nome)":
                det = self.detect_character_from_name(video_path)
                initial_char = det if det else (self.personagens_lista[1] if len(self.personagens_lista)>1 else "")
            else:
                initial_char = global_fallback
                
        char_var = tk.StringVar(value=initial_char)
        
        # Cria a UI e adiciona à fila IMEDIATAMENTE (Sincrono)
        self._finalize_item_ui(item_id, video_path, char_var, None, is_dupe)
        
        # Só a capa vai pra thread em background
        def bg_thumb():
            t_path = self.create_thumbnail(video_path, item_id)
            if t_path:
                self.after(0, lambda: self._update_thumbnail_ui(item_id, t_path))
            
        threading.Thread(target=bg_thumb, daemon=True).start()

    def _update_thumbnail_ui(self, item_id, thumb_path):
        for item in self.queue_items:
            if item["id"] == item_id:
                try:
                    img = Image.open(thumb_path)
                    img.thumbnail((120, 80))
                    img_ref = ImageTk.PhotoImage(img)
                    item["img_ref"] = img_ref
                    if "thumb_label" in item:
                        item["thumb_label"].config(image=img_ref, text="")
                except:
                    pass
                break

    def _finalize_item_ui(self, item_id, video_path, char_var, thumb_path, is_dupe):
        # Create Card Frame
        card = ctk.CTkFrame(self.queue_frame)
        card.pack(fill='x', padx=5, pady=5)
        
        # Setup Thumbnail
        img_ref = None
        thumb_label = ctk.CTkLabel(card, width=120, height=80) 
        if thumb_path and os.path.exists(thumb_path):
            try:
                img = Image.open(thumb_path)
                img.thumbnail((120, 80))
                img_ref = ImageTk.PhotoImage(img)
                thumb_label.config(image=img_ref)
            except:
                thumb_label.config(text="Sem\nCapa")
        else:
            thumb_label.config(text="Gerando...")
            
        thumb_label.pack(side='left', padx=5, pady=5)
        
        # Cenas Info
        info_frame = ctk.CTkFrame(card)
        info_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        filename = os.path.basename(video_path)
        ctk.CTkLabel(info_frame, text=filename, font=("Segoe UI", 9, "bold"), anchor="w").pack(fill='x')
        
        if is_dupe:
            ctk.CTkLabel(info_frame, text="⚠️ Cena Duplicada: Ideal para segunda trilha ou segundo ator.", font=("Segoe UI", 8), anchor="w").pack(fill='x')
            
        # Character drop down for THIS specific video
        sel_frame = ctk.CTkFrame(info_frame)
        sel_frame.pack(fill='x', pady=(10,0))
        ctk.CTkLabel(sel_frame, text="Voz de Inferencia:").pack(side='left')
        
        opcoes = [p for p in self.personagens_lista if p != "Automático (Pelo Nome)"]
        combo = ctk.CTkOptionMenu(sel_frame, variable=char_var, values=opcoes, width=300)
        combo.pack(side='left', padx=5)
        
        multi_voice_info_lbl = ctk.CTkLabel(info_frame, text="", font=("Segoe UI", 8), anchor="w", justify="left")
        multi_voice_info_lbl.pack(fill='x', pady=5)
        
        # Append to master logic first so buttons can use it
        item_data = {
            "id": item_id,
            "path": video_path,
            "char_var": char_var,
            "thumb_path": thumb_path,
            "img_ref": img_ref,
            "ui_frame": card,
            "thumb_label": thumb_label,
            "multi_voice_lbl": multi_voice_info_lbl,
            "diarization_map": None,
            "diarization_segments": None,
            "diarization_vocals_path": None
        }
        self.queue_items.append(item_data)
        
        # Buttons
        btn_frame = ctk.CTkFrame(card)
        btn_frame.pack(side='right', fill='y', padx=10, pady=10)
        
        # Functions linking to this item dict
        def on_dupe():
            self.append_item_to_queue(video_path, forced_character=char_var.get(), is_dupe=True)
            
        def on_remove():
            card.destroy()
            self.queue_items = [i for i in self.queue_items if i["id"] != item_id]
            self._update_queue_ui()
            
        def on_detectar():
            self.open_diarization_modal(item_data)
            
        ctk.CTkButton(btn_frame, text="Duplicar ➕", command=on_dupe).pack(pady=2)
        ctk.CTkButton(btn_frame, text="Remover ❌", command=on_remove).pack(pady=2)
        ctk.CTkButton(btn_frame, text="Detectar Múltiplas Vozes 🕵️", command=on_detectar).pack(pady=2)
        
        self._update_queue_ui()

    def add_single_video(self):
        filenames = filedialog.askopenfilenames(title="Selecionar Vídeo(s)", filetypes=[("Video files", "*.mp4 *.mov *.mkv *.avi")])
        if filenames:
            import re
            def atoi(text):
                return int(text) if text.isdigit() else text.lower()
            def natural_keys(text):
                name, ext = os.path.splitext(os.path.basename(text))
                return [ atoi(c) for c in re.split(r'(\d+)', name) ] + [ext.lower()]
            
            lista_arquivos = list(filenames)
            lista_arquivos.sort(key=natural_keys)
            
            for filename in lista_arquivos:
                self.append_item_to_queue(filename)
                
    def add_folder(self):
        folder = filedialog.askdirectory(title="Selecionar Pasta com Vídeos")
        if folder:
            valid_exts = ['.mp4', '.mov', '.mkv', '.avi']
            arquivos_coletados = []
            
            for root, _, files in os.walk(folder):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in valid_exts:
                        full_path = os.path.join(root, file)
                        arquivos_coletados.append(full_path)
            
            import re
            def atoi(text):
                return int(text) if text.isdigit() else text.lower()
            def natural_keys(text):
                name, ext = os.path.splitext(os.path.basename(text))
                return [ atoi(c) for c in re.split(r'(\d+)', name) ] + [ext.lower()]
                
            arquivos_coletados.sort(key=natural_keys)
            
            for filepath in arquivos_coletados:
                self.append_item_to_queue(filepath)
            
    def clear_queue(self):
        for item in self.queue_items:
            item["ui_frame"].destroy()
        self.queue_items.clear()
        self._update_queue_ui()
        
    def _update_queue_ui(self):
        # Empty text if nothing
        if not hasattr(self, 'empty_lbl'):
            self.empty_lbl = ctk.CTkLabel(self.queue_frame, text="Nenhum vídeo na fila. Adicione pela esquerda.", font=("Segoe UI", 10, "italic"))
            
        if len(self.queue_items) > 0:
            self.empty_lbl.pack_forget()
        else:
            self.empty_lbl.pack(pady=50)

    def start_processing(self):
        if not len(self.queue_items):
            messagebox.showwarning("Aviso", "A fila está vazia!")
            return
        if self.processing:
            return
            
        self.processing = True
        self.btn_process.config(state="disabled")
        
        # Roda em thread pra nao congelar UI
        threading.Thread(target=self._process_loop, daemon=True).start()
        
    def _process_loop(self):
        self.log("INICIANDO PROCESSAMENTO EM LOTE (COM DUBLAGEM VISUAL)...")
        self.log("🔄 Recarregando configurações mestre globais...")
        self.config_manager.config = self.config_manager._load_config()
        self.personagens_dict = self.config_manager.get("personagens", {})
        
        try:
            # We iterate dynamically allowing Cena 1, Cena 2 ...
            cena_idx = 1
            
            for item in self.queue_items:
                video_path = item["path"]
                char_name = item["char_var"].get()
                
                self.log(f"\n======================================")
                self.log(f"🎬 [CENA {cena_idx}] Processando: {os.path.basename(video_path)}")
                self.log(f"🧠 Personagem RVC Selecionado no Card: [{char_name}]")
                
                # Fetch FULL config for this character
                personagens_full_config = self.config_manager.get("personagens", {})
                char_config = personagens_full_config.get(char_name, {})
                
                if not char_config.get("modelo_rvc"):
                    self.log(f"❌ ERRO: Personagem '{char_name}' sem 'modelo_rvc' configurado no Painel Mestre.")
                    cena_idx += 1
                    continue
                    
                # Pastas de saida
                base_dir = os.path.dirname(video_path)
                temp_dir = os.path.join(base_dir, "temp_rvc_processor")
                out_dir = os.path.join(base_dir, "OUTPUT_DUBLADOS")
                
                os.makedirs(temp_dir, exist_ok=True)
                os.makedirs(out_dir, exist_ok=True)
                
                # Numeração no arquivo final!
                file_basename = os.path.basename(video_path)
                final_output = os.path.join(out_dir, f"Cena {cena_idx}_{char_name}_{file_basename}")
                
                try:
                    if item.get("diarization_map") and item.get("diarization_segments"):
                        spk_names = list(set([v for v in item["diarization_map"].values() if v != "[Manter Voz Original]"]))
                        mult_str = "MultiVoice_" + "_".join(spk_names) if spk_names else "MultiVoice"
                        final_output = os.path.join(out_dir, f"Cena {cena_idx}_{mult_str}_{file_basename}")
                        
                        self.log(f"🎙️ MODO MULTI-VOZ DE ESTÚDIO ATIVADO PARA: {os.path.basename(video_path)}")
                        from diarization_engine import DiarizationEngine
                        engine = DiarizationEngine(logger=self.log)
                        
                        map_data = item["diarization_map"]
                        segments = item["diarization_segments"]
                        vocals_path = item["diarization_vocals_path"]
                        bg_path = item["diarization_bg_path"]
                        temp_dir = item["diarization_temp_dir"]
                        
                        # 1. Fatia (usa diretório separado para evitar conflitos)
                        fatias_dir = os.path.join(temp_dir, "fatias")
                        sliced_segments = engine.slice_vocals(vocals_path, segments, fatias_dir)
                        
                        # 2. Applio RVC em lote para cada fatia!
                        for idx, seg in enumerate(sliced_segments):
                            spk = seg["speaker_id"]
                            char_name_mapped = map_data.get(spk)
                            
                            if char_name_mapped == "[Manter Voz Original]":
                                self.log(f"   -> Mantendo voz original para [{spk}] (Ignorando RVC)...")
                                seg["rvc_file_path"] = seg["file_path"]
                                continue
                                
                            char_config_mapped = personagens_full_config.get(char_name_mapped)
                            
                            if char_config_mapped:
                                self.log(f"   -> Dublando fatia {idx+1}/{len(sliced_segments)} com a voz de [{char_name_mapped}]...")
                                rvc_fat_path = self.processor.process_rvc(seg["file_path"], temp_dir, char_config_mapped)
                                seg["rvc_file_path"] = rvc_fat_path
                        
                        # 3. Costurar as fatias traduzidas de volta para 1 arquivo de vocal inteiro
                        costurado_path = os.path.join(temp_dir, "vocals_costurados.wav")
                        engine.stitch_vocals(vocals_path, sliced_segments, costurado_path)
                        
                        # NOVIDADE: APLICAR RESTAURAÇÃO DE ÁUDIO NO VOCAL COSTURADO INTEIRO ANTES DO MIX
                        self.log("🔄 [HOOK IA] Aplicando Tratamento e Restauração Inteligente na trilha dublada...")
                        ap = AudioProcessor()
                        ap.run_pipeline(costurado_path, costurado_path, self.config_manager.config)
                        
                        # 4. Mixar sobre o fundo com volume normal e gerar vídeo final
                        self.processor.mix_and_replace_video(video_path, costurado_path, bg_path, temp_dir, final_output)
                        
                        cena_idx += 1
                        continue

                    else:
                        # MODO SIMPLES TRADICIONAL
                        # 1. Extrair
                        audio_raw = self.processor.extract_audio(video_path, temp_dir)
                    
                    # 2. Separar (ou nao)
                    if self.skip_demucs_var.get():
                        vocals_path, bg_path = audio_raw, audio_raw
                    else:
                        vocals_path, bg_path = self.processor.separate_vocals(audio_raw, temp_dir)
                        
                    # 3. Inferir RVC
                    rvc_audio = self.processor.process_rvc(vocals_path, temp_dir, char_config)
                    
                    # NOVIDADE: APLICAR RESTAURAÇÃO DE ÁUDIO NA VOZ DO RVC ANTES DO MIX
                    self.log("🔄 [HOOK IA] Aplicando Tratamento e Restauração Inteligente na voz isolada do vídeo...")
                    ap = AudioProcessor()
                    ap.run_pipeline(rvc_audio, rvc_audio, self.config_manager.config)
                    
                    # 4. Misturar e substituir
                    if self.skip_demucs_var.get() or not bg_path:
                        self.log("Ignorando fundo (swap de vocal seco)")
                        replace_cmd = [
                            "ffmpeg", "-y", "-i", video_path, "-i", rvc_audio,
                            "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", final_output
                        ]
                        subprocess.run(replace_cmd, check=True, capture_output=True)
                        self.log(f"Processo finalizado: {final_output}")
                    else:
                        self.processor.mix_and_replace_video(video_path, rvc_audio, bg_path, temp_dir, final_output)
                    
                except Exception as e:
                    self.log(f"Falha forte ao processar [Cena {cena_idx}]: {e}")
                finally:
                    # Limpeza Temp
                    if os.path.exists(temp_dir):
                        try: shutil.rmtree(temp_dir)
                        except: pass
                
                cena_idx += 1
                        
                        
            self.log("\n======================================")
            self.log("PROCESSAMENTO EM LOTE CONCLUÍDO COM SUCESSO!")
            messagebox.showinfo("Concluído", "Todas as cenas foram processadas!")
            
        finally:
            self.processing = False
            self.after(0, lambda: self.btn_process.config(state="normal"))

    def open_diarization_modal(self, item_data):
        top = tk.Toplevel(self)
        top.title(f"Mapeamento de Múltiplos Falantes: {os.path.basename(item_data['path'])}")
        top.geometry("600x400")
        top.transient(self)
        top.grab_set()
        
        lbl_status = ctk.CTkLabel(top, text="Status: Preparando ambiente Pyannote...", font=("Segoe UI", 10, "bold"))
        lbl_status.pack(pady=10)
        
        progress = ttk.Progressbar(top, mode="indeterminate")
        progress.pack(fill=tk.X, padx=20, pady=5)
        
        frame_falantes = ctk.CTkLabelFrame(top, text="Falantes Detectados")
        frame_falantes.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        def run_pyannote():
            progress.start()
            try:
                # Checa HF Token
                keys = self.config_manager.get_api_config("huggingface", "api_keys") or []
                hf_token = keys[0]["key"] if keys else ""
                
                if not hf_token:
                    self.after(0, lambda: messagebox.showerror("Erro", "Configure e Adicione o Token da plataforma HuggingFace na aba de Configurações (Aba APIs).", parent=top))
                    self.after(0, lambda: self._safe_destroy(top))
                    return
                    
                from diarization_engine import DiarizationEngine
                engine = DiarizationEngine(logger=self.log)
                
                self.after(0, lambda: lbl_status.config(text="Status: 1/2 Extraindo Vocais Nível Estúdio com Demucs (Pode demorar vários minutos)..."))
                
                temp_dir = os.path.join(os.path.dirname(item_data["path"]), "temp_diarize_" + str(uuid.uuid4())[:8])
                os.makedirs(temp_dir, exist_ok=True)
                
                # 1. Isolar vocal
                audio_raw = self.processor.extract_audio(item_data["path"], temp_dir)
                vocals_path, bg_path = self.processor.separate_vocals(audio_raw, temp_dir)
                item_data["diarization_vocals_path"] = vocals_path
                item_data["diarization_bg_path"] = bg_path
                item_data["diarization_temp_dir"] = temp_dir
                
                # 2. Pyannote
                self.after(0, lambda: lbl_status.config(text="Status: 2/2 Analisando Biometria com IA Pyannote (Lento)..."))
                segments = engine.diarize_vocals(vocals_path, hf_token)
                
                if not segments:
                    self.after(0, lambda: messagebox.showinfo("Info", "Nenhum falante claro ou vozes distanciadas foram encontrados. Faça o lote normal.", parent=top))
                    self.after(0, lambda: self._safe_destroy(top))
                    return
                    
                item_data["diarization_segments"] = segments
                
                samples_dir = os.path.join(temp_dir, "samples_preview")
                sample_map = engine.extract_samples(vocals_path, segments, samples_dir)
                
                self.after(0, lambda: self._build_diarization_ui(top, frame_falantes, segments, item_data, lbl_status, progress, sample_map))
            except Exception as e:
                self.log(f"Erro no Diarizer: {e}")
                self.after(0, lambda e=e: messagebox.showerror("Erro de Detecção", str(e), parent=top))
                self.after(0, lambda: self._safe_destroy(top))
            finally:
                self.after(0, lambda: self._safe_stop(progress))
                
        threading.Thread(target=run_pyannote, daemon=True).start()

    def _safe_destroy(self, top):
        try:
            top.destroy()
        except:
            pass

    def _safe_stop(self, progress):
        try:
            progress.stop()
        except:
            pass

    def _build_diarization_ui(self, top, container, segments, item_data, lbl_status, progress, sample_map=None):
        if sample_map is None: sample_map = {}
        import winsound
        def play_sample(path):
            if os.path.exists(path):
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)

        lbl_status.config(text="Status: Falantes Mapeados! Assinale os personagens:")
        progress.pack_forget()
        
        for widget in container.winfo_children():
            widget.destroy()
            
        unique_speakers = sorted(list(set([s["speaker_id"] for s in segments])))
        cb_dict = {}
        
        opcoes = ["[Manter Voz Original]"] + [p for p in self.personagens_lista if p != "Automático (Pelo Nome)"]
        
        for i, spk in enumerate(unique_speakers):
            row = ctk.CTkFrame(container)
            row.pack(fill=tk.X, pady=8, padx=5)
            ctk.CTkLabel(row, text=f"🎙️ Falante {i+1} ({spk}):", width=200, anchor="e", font=("Segoe UI", 9)).pack(side=tk.LEFT)
            
            spk_audio = sample_map.get(spk, "")
            btn_play = ctk.CTkButton(row, text="▶ Ouvir", width=100, command=lambda p=spk_audio: play_sample(p))
            if not spk_audio:
                btn_play.config(state="disabled")
            btn_play.pack(side=tk.LEFT, padx=5)
            
            cb_var = tk.StringVar(value=opcoes[i] if i < len(opcoes) else (opcoes[0] if opcoes else ""))
            cb = ctk.CTkOptionMenu(row, variable=cb_var, values=opcoes, width=300)
            cb.pack(side=tk.LEFT, padx=5)
            cb_dict[spk] = cb_var
            
        def on_save():
            mapped = {spk: var.get() for spk, var in cb_dict.items()}
            item_data["diarization_map"] = mapped
            
            qtd = len(mapped)
            info_text = f"🎙️ Modo Estúdio ({qtd} Falantes Mapeados):\n"
            for spk, ator in mapped.items():
                info_text += f"   • {spk}: {ator}\n"
                
            item_data["multi_voice_lbl"].config(text=info_text.strip())
            messagebox.showinfo("Sucesso", "Mapeamento Multi-falantes fixado! O processamento em lote priorizará este perfil de vozes.", parent=top)
            
            # Muda visualmente a indicacao no card principal para confirmar
            item_data["ui_frame"].configure(fg_color="#1E3A8A") # dark blue
            top.destroy()
            
        ctk.CTkButton(container, text="💾 Confirmar Escalação de Atores e Salvar", command=on_save).pack(pady=20)
