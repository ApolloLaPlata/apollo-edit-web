import customtkinter as ctk
# -*- coding: utf-8 -*-
"""
Módulo: media_adjuster.py
Função: Ajustador de Mídia para o Descarga News Editor.
  - Recebe imagens e vídeos de qualquer tamanho/proporção
  - Padroniza para 720p (1280x720) ou 1080p (1920x1080)
  - Preserva proporção original (sem deformar)
  - Preenche o fundo com blur da própria mídia (ou vídeo customizado)
  - Garante duração mínima de 5s (configurável)
  - Nomeia saída como cena_1.mp4, cena_2.mp4, ...
  - Integra como ctk.CTkFrame dentro de qualquer Notebook Tkinter
"""

import os
import re
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from config_manager import ConfigManager


# ─────────────────────────────────────────────────────────────────
# Ordenação natural (0 dependências externas)
# ─────────────────────────────────────────────────────────────────
def _natural_sort_key(s):
    """Chave para ordenação natural: arquivo2 < arquivo10."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', os.path.basename(s))]


def natural_sort(file_list):
    return sorted(file_list, key=_natural_sort_key)


# ─────────────────────────────────────────────────────────────────
# Extensões suportadas
# ─────────────────────────────────────────────────────────────────
IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')
VIDEO_EXTS = ('.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv', '.webm')


def is_image(path: str) -> bool:
    return path.lower().endswith(IMAGE_EXTS)


def is_video(path: str) -> bool:
    return path.lower().endswith(VIDEO_EXTS)


# ─────────────────────────────────────────────────────────────────
# MediaProcessor — núcleo FFmpeg
# ─────────────────────────────────────────────────────────────────
class MediaProcessor:
    """
    Constrói e executa comandos FFmpeg para padronização de mídia.
    Pode ser instanciado de forma independente da UI.
    """

    def __init__(self):
        self.width = 1280
        self.height = 720
        self.min_duration = 5
        self.blur_strength = 20
        self.use_background_video = False
        self.background_video_path = None
        self.bitrate = "4M"
        self.fps = 30

    # ── Presets ──────────────────────────────────────────────────
    def set_preset(self, preset: str):
        if preset == "1080p":
            self.width, self.height = 1920, 1080
        else:  # padrão: 720p
            self.width, self.height = 1280, 720

    # ── Duração com ffprobe ───────────────────────────────────────
    def get_duration(self, path: str) -> float:
        """Retorna duração em segundos via ffprobe. Retorna 0.0 em erro."""
        try:
            config = ConfigManager()
            result = subprocess.run(
                [
                    config.get_ffprobe_path(), '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    path
                ],
                capture_output=True, text=True
            )
            return float(result.stdout.strip())
        except Exception:
            return 0.0

    # ── Construção do comando FFmpeg ──────────────────────────────
    def get_dims(self, path: str) -> tuple:
        try:
            config = ConfigManager()
            r = subprocess.run([config.get_ffprobe_path(), '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path], capture_output=True, text=True)
            parts = r.stdout.strip().split(',')
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        except: pass
        return None, None

    def build_command(self, input_path: str, output_path: str) -> list:
        """
        Gera o comando FFmpeg completo para processar um arquivo.
        Lógica:
          - Imagem  → vídeo de min_duration segundos
          - Vídeo curto (< min_duration) → estica até min_duration com setpts
          - Vídeo longo (≥ min_duration) → mantém duração original
        Fundo: blur da própria mídia OU vídeo externo.
        NOTA: fg NÃO usa pad (pad black cobria o blur). 
              O overlay posiciona o fg centralizado sobre o bg.
        """
        w, h = self.width, self.height
        
        # FORCAR PADRAO REDES SOCIAIS DINAMICAMENTE
        vw, vh = self.get_dims(input_path)
        if vw and vh:
            if vh > vw:
                w, h = 1080, 1920
            elif vw > vh:
                w, h = 1920, 1080
            else:
                w, h = 1080, 1080
        
        arquivo_e_imagem = is_image(input_path)

        # ── Filtro de fundo ──
        if self.use_background_video and self.background_video_path:
            # Fundo: vídeo externo (input 1) — não precisa de split
            bg_filter = (
                f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}[bg]"
            )
            # Foreground: apenas escala proporcional SEM pad (blur fica visível nas bordas)
            fg_filter = (
                f"[0:v]scale={w}:{h}:force_original_aspect_ratio=decrease[fg_raw]"
            )
            extra_inputs = ['-hwaccel', 'auto', '-i', self.background_video_path]
            split_filter = ""
        else:
            # Fundo: blur da própria mídia — precisa de split pois [0:v] é usado 2x
            split_filter = f"[0:v]split=2[src_bg][src_fg];"
            bg_filter = (
                f"[src_bg]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"boxblur={self.blur_strength}:10,crop={w}:{h}[bg]"
            )
            # Foreground: apenas escala proporcional SEM pad (blur fica visível nas bordas)
            fg_filter = (
                f"[src_fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fg_raw]"
            )
            extra_inputs = []

        # ── Esticamento de vídeo curto ──
        stretch_filter = ""
        duration_flag = []

        if arquivo_e_imagem:
            duration_flag = ['-t', str(self.min_duration)]
            final_fg = "fg_raw"
        else:
            duracao = self.get_duration(input_path)
            if 0 < duracao < self.min_duration:
                fator = round(self.min_duration / duracao, 6)
                stretch_filter = f";[fg_raw]setpts={fator}*PTS[fg]"
                final_fg = "fg"
            else:
                final_fg = "fg_raw"

        # ── Overlay: fg centralizado sobre bg, blur aparece nas bordas ──
        filter_complex = (
            f"{split_filter}"
            f"{bg_filter};"
            f"{fg_filter}"
            f"{stretch_filter};"
            f"[bg][{final_fg}]overlay=(W-w)/2:(H-h)/2[out]"
        )


        # ── Montagem do comando ──
        config = ConfigManager()
        cmd = [config.get_ffmpeg_path(), "-y", "-threads", "0"]

        if arquivo_e_imagem:
            cmd += ["-loop", "1"]
        else:
            cmd += ["-hwaccel", "auto"]

        cmd += ["-i", input_path]
        cmd += extra_inputs
        cmd += duration_flag

        import hardware_detector
        encoder = hardware_detector.detect_h264_encoder()

        if encoder == 'libx264':
            cmd += [
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-r", str(self.fps),
                "-b:v", self.bitrate,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-movflags", "+faststart",
                output_path
            ]
        else:
            if 'nvenc' in encoder:
                cmd += [
                    "-filter_complex", filter_complex,
                    "-map", "[out]",
                    "-r", str(self.fps),
                    "-b:v", self.bitrate,
                    "-c:v", encoder,
                    "-preset", "p4", "-tune", "hq", "-rc", "vbr", "-cq", "24", "-spatial-aq", "1",
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    output_path
                ]
            else:
                cmd += [
                    "-filter_complex", filter_complex,
                    "-map", "[out]",
                    "-r", str(self.fps),
                    "-b:v", self.bitrate,
                    "-c:v", encoder,
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart",
                    output_path
                ]

        return cmd


    # ── Processamento de um arquivo ──────────────────────────────
    def process_file(self, input_path: str, output_path: str,
                     log_callback=None):
        """Executa o FFmpeg para um arquivo. Retorna True se OK."""
        def log(msg):
            if log_callback:
                log_callback(msg)

        cmd = self.build_command(input_path, output_path)
        log(f"   🔧 FFmpeg: {os.path.basename(input_path)} → {os.path.basename(output_path)}")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True
            )
            if result.returncode != 0:
                log(f"   ❌ Erro FFmpeg: código {result.returncode}")
                return False
            return True
        except FileNotFoundError:
            log("   ❌ FFmpeg não encontrado! Verifique se está no PATH.")
            return False
        except Exception as e:
            log(f"   ❌ Erro inesperado: {e}")
            return False


# ─────────────────────────────────────────────────────────────────
# AbaAjustadorMidia — Frame Tkinter (aba do Notebook)
# ─────────────────────────────────────────────────────────────────
class AbaAjustadorMidia(ctk.CTkFrame):
    """
    Aba de Ajustador de Mídia para o Descarga News Editor.
    Uso:
        aba = AbaAjustadorMidia(notebook)
        notebook.add(aba, text="🎬 Ajustador de Mídia")
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.configure()

        self.processor = MediaProcessor()
        self.files = []          # lista de caminhos selecionados (em ordem)
        self.output_dir = None   # pasta de saída

        self._criar_interface()

    # ── Construção da Interface ───────────────────────────────────
    def _criar_interface(self):
        # ── Título ──
        ctk.CTkLabel(
            self,
            text="🎬 Ajustador de Mídia",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            self,
            text="Padroniza imagens e vídeos para 720p/1080p com fundo blur • Saída: cena_1.mp4, cena_2.mp4...",
            font=("Segoe UI", 9),
            text_color="#888"
        ).pack(pady=(0, 8))

        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10, pady=4)

        # ── Configurações (linha única) ──
        cfg_frame = ctk.CTkLabelFrame(self, text="⚙️ Configurações")
        cfg_frame.pack(fill='x', padx=12, pady=4)

        # Preset
        ctk.CTkLabel(cfg_frame, text="Preset:").grid(row=0, column=0, padx=(0, 4), sticky='e')
        self.preset_var = tk.StringVar(value="720p")
        ctk.CTkOptionMenu(
            cfg_frame, variable=self.preset_var,
            values=["720p", "1080p"], width=8
        ).grid(row=0, column=1, padx=(0, 12))

        # Blur
        ctk.CTkLabel(cfg_frame, text="Blur fundo:").grid(row=0, column=2, padx=(0, 4), sticky='e')
        self.blur_var = tk.IntVar(value=20)
        ttk.Spinbox(cfg_frame, textvariable=self.blur_var,
                    from_=0, to=80, width=5).grid(row=0, column=3, padx=(0, 12))

        # Bitrate
        ctk.CTkLabel(cfg_frame, text="Bitrate:").grid(row=0, column=4, padx=(0, 4), sticky='e')
        self.bitrate_var = tk.StringVar(value="4M")
        ctk.CTkEntry(cfg_frame, textvariable=self.bitrate_var, width=6).grid(row=0, column=5, padx=(0, 12))

        # FPS
        ctk.CTkLabel(cfg_frame, text="FPS:").grid(row=0, column=6, padx=(0, 4), sticky='e')
        self.fps_var = tk.IntVar(value=30)
        ttk.Spinbox(cfg_frame, textvariable=self.fps_var,
                    from_=15, to=60, width=5).grid(row=0, column=7, padx=(0, 12))

        # Duração mínima
        ctk.CTkLabel(cfg_frame, text="Mín. (s):").grid(row=0, column=8, padx=(0, 4), sticky='e')
        self.min_dur_var = tk.IntVar(value=5)
        ttk.Spinbox(cfg_frame, textvariable=self.min_dur_var,
                    from_=1, to=30, width=5).grid(row=0, column=9)

        # ── Painel de seleção de arquivos ──
        sel_frame = ctk.CTkLabelFrame(self, text="📁 Arquivos de Entrada")
        sel_frame.pack(fill='both', expand=True, padx=12, pady=4)

        btn_row = ctk.CTkFrame(sel_frame)
        btn_row.pack(fill='x', pady=(0, 6))

        ctk.CTkButton(btn_row, text="➕ Adicionar Arquivos",
                   command=self._adicionar_arquivos).pack(side='left', padx=4)
        ctk.CTkButton(btn_row, text="🗑️ Limpar Lista",
                   command=self._limpar_lista).pack(side='left', padx=4)
        ctk.CTkButton(btn_row, text="⬆ Mover Cima",
                   command=self._mover_cima).pack(side='left', padx=4)
        ctk.CTkButton(btn_row, text="⬇ Mover Baixo",
                   command=self._mover_baixo).pack(side='left', padx=4)

        self.lista_label = ctk.CTkLabel(btn_row, text="0 arquivos selecionados",
                                     text_color="#888")
        self.lista_label.pack(side='right', padx=8)

        # Listbox com scrollbar
        list_frame = ctk.CTkFrame(sel_frame)
        list_frame.pack(fill='both', expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            activestyle='dotbox',
            height=6,
            selectbackground='#3B82F6',
            font=("Segoe UI", 9)
        )
        self.listbox.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical',
                                  command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)

        # ── Saída ──
        out_frame = ctk.CTkLabelFrame(self, text="💾 Saída")
        out_frame.pack(fill='x', padx=12, pady=4)

        out_row = ctk.CTkFrame(out_frame)
        out_row.pack(fill='x')

        ctk.CTkButton(out_row, text="📂 Selecionar Pasta de Saída",
                   command=self._selecionar_saida).pack(side='left', padx=4)
        ctk.CTkButton(out_row, text="🎞️ Vídeo de Fundo (Opcional)",
                   command=self._selecionar_bg_video).pack(side='left', padx=4)

        self.saida_label = ctk.CTkLabel(out_row, text="Nenhuma pasta selecionada",
                                     text_color="#888")
        self.saida_label.pack(side='left', padx=12)

        # ── Progresso e Log ──
        ctrl_frame = ctk.CTkFrame(self)
        ctrl_frame.pack(fill='x', padx=12, pady=4)

        self.progress = ttk.Progressbar(ctrl_frame, orient='horizontal',
                                        mode='determinate', length=400)
        self.progress.pack(side='left', fill='x', expand=True, padx=(0, 8))

        self.status_label = ctk.CTkLabel(ctrl_frame, text="Aguardando...",
                                      text_color="#888", width=22)
        self.status_label.pack(side='left')

        # Área de log
        log_frame = ctk.CTkLabelFrame(self, text="📋 Log")
        log_frame.pack(fill='both', expand=True, padx=12, pady=4)

        self.log_box = tk.Text(
            log_frame, height=6, wrap='word',
            font=("Consolas", 8),
            state='disabled'
        )
        log_scroll = ttk.Scrollbar(log_frame, orient='vertical',
                                   command=self.log_box.yview)
        self.log_box.config(yscrollcommand=log_scroll.set)
        log_scroll.pack(side='right', fill='y')
        self.log_box.pack(fill='both', expand=True)

        # ── Botão Processar ──
        self.btn_processar = ctk.CTkButton(
            self,
            text="▶  PROCESSAR MÍDIA",
            command=self._iniciar_processamento
        )
        self.btn_processar.pack(pady=8)

    # ── Métodos de UI ─────────────────────────────────────────────

    def _log(self, msg: str):
        """Adiciona linha ao log (thread-safe via after)."""
        def _append():
            self.log_box.configure(state='normal')
            self.log_box.insert(tk.END, msg + "\n")
            self.log_box.see(tk.END)
            self.log_box.configure(state='disabled')
        try:
            self.after(0, _append)
        except Exception:
            pass

    def _atualizar_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, f in enumerate(self.files, start=1):
            self.listbox.insert(tk.END, f"  {i:02d}. {os.path.basename(f)}")
        n = len(self.files)
        self.lista_label.config(
            text=f"{n} arquivo{'s' if n != 1 else ''} selecionado{'s' if n != 1 else ''}"
        )

    def _adicionar_arquivos(self):
        exts = " ".join(
            [f"*{e}" for e in IMAGE_EXTS] + [f"*{e}" for e in VIDEO_EXTS]
        )
        files = filedialog.askopenfilenames(
            title="Selecione imagens ou vídeos",
            filetypes=[("Mídia", exts), ("Todos os arquivos", "*.*")]
        )
        if files:
            novos = natural_sort(list(files))
            self.files.extend([f for f in novos if f not in self.files])
            self._atualizar_listbox()
            self._log(f"✅ {len(novos)} arquivo(s) adicionado(s).")

    def _limpar_lista(self):
        self.files.clear()
        self._atualizar_listbox()
        self.progress['value'] = 0
        self.status_label.config(text="Aguardando...")
        self._log("🗑️ Lista limpa.")

    def _mover_cima(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        i = sel[0]
        self.files[i - 1], self.files[i] = self.files[i], self.files[i - 1]
        self._atualizar_listbox()
        self.listbox.selection_set(i - 1)

    def _mover_baixo(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] >= len(self.files) - 1:
            return
        i = sel[0]
        self.files[i], self.files[i + 1] = self.files[i + 1], self.files[i]
        self._atualizar_listbox()
        self.listbox.selection_set(i + 1)

    def _selecionar_saida(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta de saída")
        if pasta:
            self.output_dir = pasta
            nome = pasta if len(pasta) < 55 else "..." + pasta[-52:]
            self.saida_label.config(text=nome, text_color="#60A5FA")
            self._log(f"📂 Pasta de saída: {pasta}")

    def _selecionar_bg_video(self):
        exts = " ".join([f"*{e}" for e in VIDEO_EXTS])
        f = filedialog.askopenfilename(
            title="Selecione vídeo de fundo",
            filetypes=[("Vídeo", exts)]
        )
        if f:
            self.processor.use_background_video = True
            self.processor.background_video_path = f
            self._log(f"🎞️ Vídeo de fundo: {os.path.basename(f)}")
        else:
            self.processor.use_background_video = False
            self.processor.background_video_path = None
            self._log("🎞️ Vídeo de fundo removido — usando blur.")

    # ── Processamento ─────────────────────────────────────────────

    def _iniciar_processamento(self):
        if not self.files:
            messagebox.showwarning("Atenção", "Adicione pelo menos um arquivo antes de processar.")
            return
        if not self.output_dir:
            messagebox.showwarning("Atenção", "Selecione a pasta de saída.")
            return

        # Atualiza parâmetros do processor com valores da UI
        self.processor.set_preset(self.preset_var.get())
        self.processor.blur_strength = self.blur_var.get()
        self.processor.bitrate = self.bitrate_var.get()
        self.processor.fps = self.fps_var.get()
        self.processor.min_duration = self.min_dur_var.get()

        self.btn_processar.config(state='disabled')
        t = threading.Thread(target=self._processar_em_thread, daemon=True)
        t.start()

    def _processar_em_thread(self):
        total = len(self.files)
        erros = 0

        try:
            self.after(0, lambda: self.progress.config(maximum=total, value=0))

            for i, caminho in enumerate(self.files, start=1):
                nome_saida = f"cena_{i}.mp4"
                caminho_saida = os.path.join(self.output_dir, nome_saida)

                self._log(f"\n📎 [{i}/{total}] {os.path.basename(caminho)}")
                self.after(0, lambda nm=nome_saida: self.status_label.config(
                    text=f"Processando {nm}..."))

                ok = self.processor.process_file(
                    caminho, caminho_saida, log_callback=self._log
                )

                if ok:
                    self._log(f"   ✅ Salvo como {nome_saida}")
                else:
                    erros += 1
                    self._log(f"   ⚠️ Falha ao processar {os.path.basename(caminho)}")

                idx = i
                self.after(0, lambda v=idx: self.progress.config(value=v))

            # Finalização
            if erros == 0:
                msg = f"✅ Concluído! {total} arquivo(s) processado(s)."
                self._log(f"\n{msg}")
                self.after(0, lambda: messagebox.showinfo("Concluído", msg))
            else:
                msg = f"⚠️ Concluído com {erros} erro(s). Verifique o log."
                self._log(f"\n{msg}")
                self.after(0, lambda: messagebox.showwarning("Aviso", msg))

            self.after(0, lambda: self.status_label.config(text="Finalizado ✅"))

        finally:
            self.after(0, lambda: self.btn_processar.config(state='normal'))
