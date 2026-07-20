import tkinter as tk
from config_manager import ConfigManager
from tkinter import ttk, filedialog, messagebox
import os
import json
import re
import threading
import subprocess
import queue
import logging

from functools import lru_cache

@lru_cache(maxsize=512)
def check_has_audio(filepath):
    try:
        probe_cmd = [FFPROBE_EXE, '-i', filepath, '-show_streams', '-select_streams', 'a', '-loglevel', 'error']
        res = subprocess.run(probe_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        return len(res.stdout.strip()) > 0
    except Exception:
        return False

def get_atempo_chain(speed):
    chain = []
    while speed < 0.5:
        chain.append("atempo=0.5")
        speed /= 0.5
    while speed > 100.0:
        chain.append("atempo=100.0")
        speed /= 100.0
    chain.append(f"atempo={speed:.6f}")
    return ",".join(chain)

try:
    from aba_edicao_basica import generate_karaoke_ass, get_temas_disponiveis
    KARAOKE_AVAILABLE = True
except ImportError:
    KARAOKE_AVAILABLE = False
    generate_karaoke_ass = None

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _parse_srt_to_whisper_words(srt_path: str) -> list:
    """
    Converte um arquivo .srt padrão em lista de dicts
    {'word': str, 'start': float, 'end': float}
    compatíveis com o formato do Whisper word-level.

    Aceita tanto SRT com uma palavra por bloco (gerado pelo nosso sistema)
    quanto SRT com frases inteiras por bloco (gerado por ferramentas externas).
    No segundo caso, distribui as palavras proporcionalmente no intervalo do bloco.
    """
    import re

    def _ts_to_sec(ts: str) -> float:
        """HH:MM:SS,mmm → float segundos"""
        ts = ts.replace(',', '.')
        parts = ts.split(':')
        h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
        return h * 3600 + m * 60 + s

    words = []
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Separa blocos por linha em branco
        blocks = re.split(r'\n\s*\n', content.strip())
        for block in blocks:
            lines = block.strip().splitlines()
            if len(lines) < 3:
                continue
            # Linha 2 contém os timestamps
            ts_line = lines[1]
            ts_match = re.match(
                r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}[,\.]\d{3})',
                ts_line
            )
            if not ts_match:
                continue
            start = _ts_to_sec(ts_match.group(1))
            end   = _ts_to_sec(ts_match.group(2))
            text  = ' '.join(lines[2:]).strip()

            # Se for apenas uma palavra: adiciona diretamente
            toks = text.split()
            if len(toks) == 1:
                words.append({'word': text, 'start': start, 'end': end})
            else:
                # Distribui palavras proporcionalmente no intervalo do bloco
                dur = max(0.01, end - start)
                step = dur / len(toks)
                for i, tok in enumerate(toks):
                    words.append({
                        'word':  tok,
                        'start': round(start + i * step, 3),
                        'end':   round(start + (i + 1) * step, 3)
                    })
    except Exception as ex:
        print(f"[SRT-PARSER] Erro ao ler {srt_path}: {ex}", flush=True)

    return words



_config_global = ConfigManager()
FFMPEG_EXE = _config_global.get_ffmpeg_path()
FFPROBE_EXE = _config_global.get_ffprobe_path()


import customtkinter as ctk

class CTkLabelFrame(ctk.CTkFrame):
    def __init__(self, master, text="", **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        if text:
            self.lbl = ctk.CTkLabel(self, text=text, font=("Segoe UI", 13, "bold"), text_color="#0A84FF")
            self.lbl.place(x=15, y=5)
            
            # Create a dummy frame to occupy space at the top using place, wait place doesn't occupy space.
            # We will just rely on the first element having pady.

ctk.CTkLabelFrame = CTkLabelFrame


class AbaMapeadorAutomatico(ctk.CTkFrame):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent, fg_color="transparent")
        self.config_manager = config_manager
        
        self.audio_path = tk.StringVar()
        self.saida_dir = tk.StringVar()
        self.transicoes_dir = tk.StringVar()
        self.srt_externo_path = tk.StringVar()   # SRT opcional — pula o Whisper se preenchido
        
        self.video_format = tk.StringVar(value='vertical')  # Novo: formato global
        self.prob_transicao = tk.IntVar(value=70)           # Novo: Probabilidade unificada de transição
        
        self.cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_mapeador.json")
        
        # Audio Global
        self.musica_path = tk.StringVar()
        self.vol_musica = tk.IntVar(value=-15)
        self.usar_audio_base = tk.BooleanVar(value=False)
        self.vol_audio_base = tk.IntVar(value=0)
        
        # Legenda Vars (Cópia da Aba 1)
        self.var_legenda = tk.BooleanVar(value=True)
        self.sub_font = tk.StringVar(value="Bangers")
        self.sub_words = tk.IntVar(value=5)
        self.sub_pos = tk.StringVar(value="meio baixo")
        self.sub_theme = tk.StringVar(value="amarelo vermelho")
        self.sub_size = tk.IntVar(value=100)
        self.sub_margin_v = tk.IntVar(value=150)
        self.sub_effect = tk.StringVar(value="Pulo (Pop)")
        
        # UI Setup
        header = ctk.CTkFrame(self)
        header.pack(fill='x', padx=20, pady=10)
        ctk.CTkLabel(header, text="O DIRETOR (Mapeamento Automático)", font=("Segoe UI", 18, "bold")).pack(anchor='w')
        ctk.CTkLabel(header, text="Fatie a narração e aplique múltiplos perfis visuais automaticamente.", font=("Segoe UI", 10)).pack(anchor='w')

        main_pane = ctk.CTkFrame(self, fg_color="transparent")
        main_pane.pack(fill='both', expand=True, padx=20, pady=5)
        
        left_container = ctk.CTkFrame(main_pane)
        right_frame = ctk.CTkFrame(main_pane)
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        canvas = tk.Canvas(left_container)
        scrollbar = ctk.CTkScrollbar(left_container, orientation="vertical", command=canvas.yview)
        left_frame = ctk.CTkFrame(canvas)
        
        left_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=left_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.f_bot = ctk.CTkFrame(left_container)
        self.f_bot.pack(side=tk.BOTTOM, fill='x', pady=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._left_canvas = canvas
        left_frame.bind("<Enter>", self._bind_mousewheel)
        left_frame.bind("<Leave>", self._unbind_mousewheel)
        
        # --- CONSOLE DE LOGS (Terminal) NA PARTE INFERIOR ---
        f_console = ctk.CTkLabelFrame(self, text=" 📜 Terminal de Renderização ")
        f_console.pack(side='bottom', fill='x', padx=20, pady=(0, 10))
        self.console_log = ctk.CTkTextbox(f_console, height=120, font=("Consolas", 12))
        self.console_log.pack(side='left', fill='both', expand=True)

        self.video_paths = []
        self.thumbnail_cache = {}
        self._thumb_queue = queue.Queue()  # Fila thread-safe para thumbnails
        self._poll_thumb_queue()           # Inicia polling na main thread
        
        # Section 0: Perfis do Diretor
        f_perfil_dir = ctk.CTkLabelFrame(left_frame, text=" 0. Perfil de Configuração do Diretor ")
        f_perfil_dir.pack(fill='x', pady=(0, 5))
        
        ctk.CTkLabel(f_perfil_dir, text="🎬 Carregar Perfil:").pack(side='left', padx=(0,5))
        self.var_perfil_diretor = tk.StringVar()
        self.cb_perfil_diretor = ctk.CTkOptionMenu(f_perfil_dir, variable=self.var_perfil_diretor, state="normal", width=300)
        self.cb_perfil_diretor.pack(side='left')
        
        ctk.CTkButton(f_perfil_dir, text="💾 Salvar Config Atual", command=self._salvar_perfil_diretor).pack(side='left', padx=5)
        ctk.CTkButton(f_perfil_dir, text="🗑️ Deletar", command=self._deletar_perfil_diretor).pack(side='left')
        
        self.cb_perfil_diretor.bind("<<ComboboxSelected>>", self._aplicar_perfil_diretor)
        
        # Section 1: Inputs de Arquivos
        f_files = ctk.CTkLabelFrame(left_frame, text=" 1. Entradas e Saídas ")
        f_files.pack(fill='x', pady=5)
        
        # Formato do vídeo H/V
        f_fmt = ctk.CTkFrame(f_files)
        f_fmt.grid(row=0, column=0, columnspan=3, sticky='we', pady=(0,5))
        ctk.CTkLabel(f_fmt, text="Formato:", font=("Segoe UI", 9, "bold")).pack(side='left', padx=(0,8))
        ctk.CTkRadioButton(f_fmt, text="📱 Vertical",   variable=self.video_format, value='vertical').pack(side='left', padx=(0,12))
        ctk.CTkRadioButton(f_fmt, text="🖥️ Horizontal", variable=self.video_format, value='horizontal').pack(side='left')
        
        # MODO DE RITMO (TTS vs Lip Sync)
        f_modo = ctk.CTkFrame(f_files)
        f_modo.grid(row=1, column=0, columnspan=3, sticky='we', pady=(0,5))
        ctk.CTkLabel(f_modo, text="Modo de Ritmo:", font=("Segoe UI", 9, "bold")).pack(side='left', padx=(0,8))
        
        self.modo_ritmo = tk.StringVar(value="tts")
        
        def _on_modo_ritmo_change():
            if self.modo_ritmo.get() == "lipsync":
                self.ent_audio.configure(state='disabled')
                self.btn_audio_proc.configure(state='disabled')
                self.btn_audio_tts.configure(state='disabled')
                self.usar_audio_base.set(True) # Força o uso do áudio original
            else:
                self.ent_audio.configure(state='normal')
                self.btn_audio_proc.configure(state='normal')
                self.btn_audio_tts.configure(state='normal')
                
        ctk.CTkRadioButton(f_modo, text="🗣️ Guiado por Narração (TTS)", variable=self.modo_ritmo, value='tts', command=_on_modo_ritmo_change).pack(side='left', padx=(0,12))
        ctk.CTkRadioButton(f_modo, text="🎥 Lip Sync (Duração Exata do Vídeo Base)", variable=self.modo_ritmo, value='lipsync', command=_on_modo_ritmo_change).pack(side='left')

        ctk.CTkLabel(f_files, text="Áudio Narração (Completo):").grid(row=2, column=0, sticky='w', pady=2)
        self.ent_audio = ctk.CTkEntry(f_files, textvariable=self.audio_path, width=500)
        self.ent_audio.grid(row=2, column=1, sticky='we', padx=5, pady=2)
        f_btn_audio = ctk.CTkFrame(f_files)
        f_btn_audio.grid(row=2, column=2, pady=2, sticky='w')
        self.btn_audio_proc = ctk.CTkButton(f_btn_audio, text="Procurar", command=lambda: self._pick_file(self.audio_path, [("Áudio", "*.wav;*.mp3;*.m4a")]))
        self.btn_audio_proc.pack(side='left', padx=2)
        self.btn_audio_tts = ctk.CTkButton(f_btn_audio, text="🪄 Puxar TTS", command=self._puxar_ultimo_tts)
        self.btn_audio_tts.pack(side='left', padx=2)

        # SRT opcional — se fornecido, pula o Whisper no render
        f_srt = ctk.CTkFrame(f_files)
        f_srt.grid(row=3, column=0, columnspan=3, sticky='we', pady=(0, 4))
        ctk.CTkLabel(f_srt, text="📝 SRT pré-gerado (opcional):",
                  font=("Segoe UI", 8, "bold")).pack(side='left', padx=(0, 4))
        ctk.CTkEntry(f_srt, textvariable=self.srt_externo_path, width=380).pack(side='left', fill='x', expand=True)
        ctk.CTkButton(f_srt, text="📂",  width=30,
                   command=lambda: self._pick_file(self.srt_externo_path, [("SRT", "*.srt")])
                   ).pack(side='left', padx=(3, 0))
        ctk.CTkButton(f_srt, text="❌", width=30,
                   command=lambda: self.srt_externo_path.set("")
                   ).pack(side='left', padx=(2, 0))
        ctk.CTkLabel(f_srt,
                  text="Se vazio, o Whisper gera automaticamente.",
                  text_color="#888", font=("Segoe UI", 7)).pack(side='left', padx=(6, 0))

        ctk.CTkLabel(f_files, text="Pasta de Saída:").grid(row=4, column=0, sticky='w', pady=2)
        ctk.CTkEntry(f_files, textvariable=self.saida_dir, width=500).grid(row=4, column=1, sticky='we', padx=5, pady=2)
        ctk.CTkButton(f_files, text="Procurar", command=lambda: self._pick_dir(self.saida_dir)).grid(row=4, column=2, pady=2)
        
        ctk.CTkLabel(f_files, text="Música de Fundo (Opcional):").grid(row=5, column=0, sticky='w', pady=2)
        f_mus = ctk.CTkFrame(f_files)
        f_mus.grid(row=5, column=1, sticky='we', padx=5, pady=2)
        ctk.CTkEntry(f_mus, textvariable=self.musica_path, width=350).pack(side='left', fill='x', expand=True)
        ctk.CTkLabel(f_mus, text="Vol(dB):").pack(side='left', padx=(5,0))
        ttk.Spinbox(f_mus, from_=-60, to=10, textvariable=self.vol_musica, width=4).pack(side='left')
        ctk.CTkButton(f_files, text="Procurar", command=lambda: self._pick_multiple_files(self.musica_path, [("Áudio", "*.mp3;*.wav;*.m4a;*.flac")])).grid(row=5, column=2, pady=2)
        
        ctk.CTkLabel(f_files, text="Áudio Base Nativo (Opcional):").grid(row=6, column=0, sticky='w', pady=2)
        f_base_aud = ctk.CTkFrame(f_files)
        f_base_aud.grid(row=6, column=1, sticky='we', padx=5, pady=2)
        ctk.CTkSwitch(f_base_aud, text="Ativar", variable=self.usar_audio_base).pack(side='left')
        ctk.CTkLabel(f_base_aud, text="Vol(dB):").pack(side='left', padx=(15,0))
        ttk.Spinbox(f_base_aud, from_=-60, to=10, textvariable=self.vol_audio_base, width=4).pack(side='left')
        
        # Indicador visual e controles dos Master Switches (Estética Global)
        f_trans_ctrl = ctk.CTkFrame(f_files)
        f_trans_ctrl.grid(row=6, column=0, columnspan=3, sticky='we', pady=5)
        
        ctk.CTkLabel(f_trans_ctrl, text="🔌 Masters:", text_color="#2ED573", font=("Segoe UI", 9, "bold")).pack(side='left', padx=(0,5))
        
        est = self.config_manager.get("estetica_canal", {}) if self.config_manager else {}
        self.master_hd    = tk.BooleanVar(value=est.get("master_hd", True))
        self.master_overlay = tk.BooleanVar(value=est.get("master_overlay", True))
        self.master_xfade = tk.BooleanVar(value=est.get("master_xfade", True))
        self.master_lut   = tk.BooleanVar(value=est.get("master_lut", True))
        self.master_cor   = tk.BooleanVar(value=est.get("master_cor", True))
        self.master_cam   = tk.BooleanVar(value=est.get("master_cam", True))
        
        def save_masters(*args):
            if not self.config_manager: return
            cfg = self.config_manager.get("estetica_canal", {})
            cfg["master_hd"]    = self.master_hd.get()
            cfg["master_overlay"] = self.master_overlay.get()
            cfg["master_xfade"] = self.master_xfade.get()
            cfg["master_lut"]   = self.master_lut.get()
            cfg["master_cor"]   = self.master_cor.get()
            cfg["master_cam"]   = self.master_cam.get()
            self.config_manager.set("estetica_canal", cfg)
            
        for v in [self.master_hd, self.master_overlay, self.master_xfade, self.master_lut, self.master_cor, self.master_cam]:
            v.trace_add("write", save_masters)

        self.ctrl_master_hd = ctk.CTkSwitch(f_trans_ctrl, text="HD", variable=self.master_hd)
        self.ctrl_master_hd.pack(side='left', padx=2)
        
        self.ctrl_master_overlay = ctk.CTkSwitch(f_trans_ctrl, text="Poeira", variable=self.master_overlay)
        self.ctrl_master_overlay.pack(side='left', padx=2)
        
        self.ctrl_master_xfade = ctk.CTkSwitch(f_trans_ctrl, text="XFade", variable=self.master_xfade)
        self.ctrl_master_xfade.pack(side='left', padx=2)
        
        self.ctrl_master_lut = ctk.CTkSwitch(f_trans_ctrl, text="LUT", variable=self.master_lut)
        self.ctrl_master_lut.pack(side='left', padx=2)
        
        self.ctrl_master_cor = ctk.CTkSwitch(f_trans_ctrl, text="Cor", variable=self.master_cor)
        self.ctrl_master_cor.pack(side='left', padx=2)
        
        self.ctrl_master_cam = ctk.CTkSwitch(f_trans_ctrl, text="Cam/Mov", variable=self.master_cam)
        self.ctrl_master_cam.pack(side='left', padx=(2,15))
        
        ctk.CTkLabel(f_trans_ctrl, text="| Probabilidade XFade/HD (%):").pack(side='left', padx=(5,3))
        self.ctrl_prob_transicao = ttk.Spinbox(f_trans_ctrl, from_=0, to=100, textvariable=self.prob_transicao, width=4)
        self.ctrl_prob_transicao.pack(side='left')
        
        f_perf_est = ctk.CTkFrame(f_files)
        f_perf_est.grid(row=7, column=0, columnspan=3, sticky='we', pady=(0,5))
        ctk.CTkLabel(f_perf_est, text="📁 Perfil Estético:").pack(side='left', padx=(0,5))
        self.var_perfil_estetica = tk.StringVar()
        self.cb_perfil_estetica = ctk.CTkOptionMenu(f_perf_est, variable=self.var_perfil_estetica, state="normal", width=250)
        self.cb_perfil_estetica.pack(side='left')
        ctk.CTkButton(f_perf_est, text="🔄 Recarregar", command=self._carregar_perfis_estetica_ui).pack(side='left', padx=5)
        self.cb_perfil_estetica.bind("<<ComboboxSelected>>", self._aplicar_perfil_estetica)

        # Section 2: Legendas
        f_sub = ctk.CTkLabelFrame(left_frame, text=" 2. Legendas Karaokê Dinâmicas ")
        f_sub.pack(fill='x', pady=5)
        
        ctk.CTkSwitch(f_sub, text="Gerar & Queimar legendas Karaokê no Master Final", variable=self.var_legenda).grid(row=0, column=0, columnspan=4, sticky='w', pady=2)
        
        f_prof = ctk.CTkFrame(f_sub)
        f_prof.grid(row=1, column=0, columnspan=4, sticky='we', pady=(5,10))
        ctk.CTkLabel(f_prof, text="📁 Carregar Perfil:").pack(side='left', padx=(0,5))
        self.var_perfil_legenda = tk.StringVar()
        self.cb_perfil_legenda = ctk.CTkOptionMenu(f_prof, variable=self.var_perfil_legenda, state="normal", width=250)
        self.cb_perfil_legenda.pack(side='left')
        ctk.CTkButton(f_prof, text="🔄 Recarregar", command=self._carregar_perfis_ui).pack(side='left', padx=5)
        self.cb_perfil_legenda.bind("<<ComboboxSelected>>", self._aplicar_perfil_legenda)
        
        fontes = ["Bangers", "Arial", "Impact", "Komika Axis", "Montserrat", "Oswald", "Roboto", "Anton", "TheBoldFont"]
        ctk.CTkLabel(f_sub, text="Fonte:").grid(row=2, column=0, sticky='w')
        self.ctrl_sub_font = ctk.CTkOptionMenu(f_sub, variable=self.sub_font, values=fontes, width=150)
        self.ctrl_sub_font.grid(row=2, column=1, sticky='w', padx=5)
        
        ctk.CTkLabel(f_sub, text="Palavras/bloco:").grid(row=2, column=2, sticky='w')
        self.ctrl_sub_words = ttk.Spinbox(f_sub, from_=1, to=15, textvariable=self.sub_words, width=5)
        self.ctrl_sub_words.grid(row=2, column=3, sticky='w')

        ctk.CTkLabel(f_sub, text="Posição:").grid(row=3, column=0, sticky='w')
        self.ctrl_sub_pos = ctk.CTkOptionMenu(f_sub, variable=self.sub_pos, values=["meio baixo", "meio", "topo", "embaixo"], width=150)
        self.ctrl_sub_pos.grid(row=3, column=1, sticky='w', padx=5)
        
        temas  = get_temas_disponiveis()
        ctk.CTkLabel(f_sub, text="Tema:").grid(row=3, column=2, sticky='w')
        self.ctrl_sub_theme = ctk.CTkOptionMenu(f_sub, variable=self.sub_theme, values=temas, width=150)
        self.ctrl_sub_theme.grid(row=3, column=3, sticky='w')

        ctk.CTkLabel(f_sub, text="Tamanho (px):").grid(row=4, column=0, sticky='w')
        self.ctrl_sub_size = ttk.Spinbox(f_sub, from_=10, to=200, textvariable=self.sub_size, width=5)
        self.ctrl_sub_size.grid(row=4, column=1, sticky='w', padx=5)
        
        ctk.CTkLabel(f_sub, text="MargemV (px):").grid(row=4, column=2, sticky='w')
        self.ctrl_sub_margin_v = ttk.Spinbox(f_sub, from_=0, to=500, textvariable=self.sub_margin_v, width=5)
        self.ctrl_sub_margin_v.grid(row=4, column=3, sticky='w')

        efeitos = ["Nenhum", "Pulo (Pop)", "Balanço", "Giro Zoom", "Tremor", "Neon", "Flash", "Karate", "Bomba", "Sublinha", "Cinema"]
        ctk.CTkLabel(f_sub, text="Efeito Animação:").grid(row=5, column=0, sticky='w')
        self.ctrl_sub_effect = ctk.CTkOptionMenu(f_sub, variable=self.sub_effect, values=efeitos, width=150)
        self.ctrl_sub_effect.grid(row=5, column=1, sticky='w', padx=5)

        # Mapa de Temas de Podcast (gerado pela Aba Podcast)
        self.mapa_temas_path = tk.StringVar()
        f_mapa_temas = ctk.CTkFrame(f_sub)
        f_mapa_temas.grid(row=6, column=0, columnspan=4, sticky='we', pady=(8, 2))
        ctk.CTkLabel(f_mapa_temas, text="🎨 Mapa de Cores (Podcast):", font=("Segoe UI", 9, "bold")).pack(side='left')
        ctk.CTkEntry(f_mapa_temas, textvariable=self.mapa_temas_path, width=300).pack(side='left', padx=5)
        ctk.CTkButton(f_mapa_temas, text="📂 Carregar",
                   command=lambda: self._pick_file(self.mapa_temas_path,
                   [("Mapa de Temas JSON", "*.json"), ("Todos", "*.*")])).pack(side='left')
        ctk.CTkButton(f_mapa_temas, text="✖ Limpar",
                   command=lambda: [self.mapa_temas_path.set(''), self._toggle_tema_ctrl_mapeador()]).pack(side='left', padx=3)
        ctk.CTkLabel(f_mapa_temas, text="(Opcional - gerado pela Aba de Podcast)",
                  text_color="gray", font=("Segoe UI", 8)).pack(side='left', padx=5)

        self.mapa_temas_path.trace_add('write', lambda *_: self._toggle_tema_ctrl_mapeador())

        # Section 3: Variáveis Globais
        f_vars = ctk.CTkLabelFrame(left_frame, text=" 3. Variáveis Globais (Sobrescrevem os Templates) ")
        f_vars.pack(fill='x', pady=5)
        
        self.lay1_fundo_path = tk.StringVar()
        self.base_loop_count = tk.IntVar(value=0) # 0 = sem loop, 1 = 1 repetição
        self.tipo_midia_upload = tk.StringVar(value="Fotos e Vídeos")
        self.lay2_narrador_path = tk.StringVar()
        self.lay3_frente_path = tk.StringVar()
        self.lay4_moldura_dir = tk.StringVar()

        def add_layer_ui(parent, title, path_var, r, is_folder=False):
            ctk.CTkLabel(parent, text=title).grid(row=r, column=0, sticky='w', pady=2)
            ctk.CTkEntry(parent, textvariable=path_var, width=450).grid(row=r, column=1, sticky='we', padx=5, pady=2)
            if is_folder:
                ctk.CTkButton(parent, text="Pasta", command=lambda: self._pick_dir(path_var)).grid(row=r, column=2, pady=2)
            else:
                ctk.CTkButton(parent, text="Arquivo", command=lambda: self._pick_file(path_var, [("Media", "*.mp4;*.mov;*.webm;*.png;*.webp;*.jpg"), ("Todos", "*.*")])).grid(row=r, column=2, pady=2)

        # A lista de Vídeos Base fica exclusivamente no painel direito (Treeview)
        add_layer_ui(f_vars, "1. Narrador (Avatar):", self.lay2_narrador_path, 0)
        add_layer_ui(f_vars, "2. Tag / Frente:", self.lay3_frente_path, 1)
        add_layer_ui(f_vars, "3. Elemento Extra (Top):", self.lay4_moldura_dir, 2, is_folder=True)

        # Section 4: Modo de Template Web (NLE)
        self.perfil_unico = tk.StringVar(value="[Sem Template - Apenas Vídeo Base]")

        f_modo = ctk.CTkLabelFrame(left_frame, text=" 4. Modo de Template Web (NLE) ")
        f_modo.pack(fill='x', pady=5)
        
        self.f_unico = ctk.CTkFrame(f_modo)
        self.f_unico.pack(fill='x')
        ctk.CTkLabel(self.f_unico, text="Modo / Template:").pack(side='left')
        self.combo_perfil = ctk.CTkOptionMenu(self.f_unico, variable=self.perfil_unico, state="normal", width=450)
        self.combo_perfil.pack(side='left', padx=5)
        self.combo_perfil.bind("<<ComboboxSelected>>", self._toggle_modo)
        ctk.CTkButton(self.f_unico, text="🔄 Atualizar", command=self._atualizar_lista_perfis).pack(side='left')

        # Section 5.1: Texto de Mapeamento (Vídeo Base)
        self.f_map_base = ctk.CTkLabelFrame(left_frame, text=" 5.1 Roteiro do Vídeo Base (Cenas de Fundo) ")
        self.f_map_base.pack(fill='both', expand=True, pady=(5, 2))
        
        f_base_ctrl = ctk.CTkFrame(self.f_map_base)
        f_base_ctrl.pack(fill='x', pady=(0, 5))
        
        self.usar_roteiro_base = tk.BooleanVar(value=False)
        ctk.CTkSwitch(f_base_ctrl, text="Ativar Mapeamento de Vídeo Base em Roteiro", variable=self.usar_roteiro_base, command=self._toggle_roteiro_base).pack(side='left')
        
        lbl_hint_base = ctk.CTkLabel(self.f_map_base, text="Sintaxe: Cada linha é um corte de vídeo. (Sincronizado via Whisper)\n*Se desativado: Os vídeos base serão cortados igualmente pelo tamanho do áudio.")
        lbl_hint_base.pack(anchor='w')
        
        self.text_map_base = ctk.CTkTextbox(self.f_map_base, wrap='word', height=100, font=("Consolas", 12))
        self.text_map_base.pack(fill='both', expand=True, pady=5)
        
        exemplo_base = "Cena 1 - O carro acelera na pista\nCena 2 - A polícia vem logo atrás"
        self.text_map_base.insert(tk.END, exemplo_base)

        # Section 5.2: Texto de Mapeamento (Templates)
        self.f_map = ctk.CTkLabelFrame(left_frame, text=" 5.2 Roteiro Gráfico (Templates/Perfis) ")
        self.f_map.pack(fill='both', expand=True, pady=(2, 5))
        
        f_trans = ctk.CTkFrame(self.f_map)
        f_trans.pack(fill='x', pady=(0, 5))
        ctk.CTkLabel(f_trans, text="Transição entre Templates:").pack(side='left')
        self.var_transicao_template = tk.StringVar(value="[Corte Seco]")
        self.cb_transicao_template = ctk.CTkOptionMenu(f_trans, variable=self.var_transicao_template, state="normal", width=250)
        self.cb_transicao_template.pack(side='left', padx=5)
        ctk.CTkButton(f_trans, text="🔄 Recarregar", command=self._carregar_perfis_transicao_template).pack(side='left')

        lbl_hint = ctk.CTkLabel(self.f_map, text="Sintaxe esperada: [Nome_do_Perfil_Sem_JSON] Quebra de frase do áudio...")
        lbl_hint.pack(anchor='w')
        
        self.text_mapeamento = ctk.CTkTextbox(self.f_map, wrap='word', height=120, font=("Consolas", 12))
        self.text_mapeamento.pack(fill='both', expand=True, pady=5)
        
        # Texto Padrão de Exemplo
        exemplo = "[perfil_horizontal_1] Bem-vindos ao Tutorial das Coisas!\n[perfil_horizontal_2] Hoje vamos aprender a dominar o FFmpeg."
        self.text_mapeamento.insert(tk.END, exemplo)
        
        # Fase 29: Botões Import/Export do Roteiro
        f_rot_btn = ctk.CTkFrame(self.f_map)
        f_rot_btn.pack(fill='x')
        ctk.CTkButton(f_rot_btn, text="💾 Salvar Roteiro (.txt)", command=self._salvar_roteiro).pack(side='left', padx=2)
        ctk.CTkButton(f_rot_btn, text="📂 Carregar Roteiro (.txt)", command=self._carregar_roteiro).pack(side='left', padx=2)
        ctk.CTkButton(f_rot_btn, text="🧹 Limpar Tudo", command=lambda: self.text_mapeamento.delete('1.0', tk.END)).pack(side='right', padx=2)
        
        self._atualizar_lista_perfis()
        self._toggle_modo()
        self._toggle_roteiro_base()
        
        # Section 6: Gerar (Movido para self.f_bot)
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(self.f_bot, variable=self.progress_var, maximum=100)
        self.progressbar.pack(fill='x', pady=5)
        
        self.status = tk.StringVar(value="Pronto.")
        ctk.CTkLabel(self.f_bot, textvariable=self.status, font=("Segoe UI", 12, "bold"), text_color="#00FF00").pack(pady=5)
        
        # --- RIGHT FRAME (Videos List with THUMBNAILS) ---
        f_title_right = ctk.CTkFrame(right_frame)
        f_title_right.pack(fill='x', pady=5)
        
        row1 = ctk.CTkFrame(f_title_right)
        row1.pack(fill='x')
        ctk.CTkLabel(row1, text="Vídeos Base", font=("Segoe UI", 11, "bold")).pack(side='left', anchor='w')
        self.var_sincronizar_base = tk.BooleanVar(value=True)
        ctk.CTkSwitch(row1, text="Sincronizar Cortes (Padrão Dark Fácil)", variable=self.var_sincronizar_base).pack(side='right', padx=5)
        
        row2 = ctk.CTkFrame(f_title_right)
        row2.pack(fill='x', pady=2)
        ttk.OptionMenu(row2, self.tipo_midia_upload, self.tipo_midia_upload.get(), "Fotos e Vídeos", "Somente Fotos", "Somente Vídeos").pack(side='right', padx=5)
        ttk.Spinbox(row2, from_=0, to=100, textvariable=self.base_loop_count, width=4).pack(side='right', padx=2)
        ctk.CTkLabel(row2, text="Qtd. Loops:").pack(side='right', padx=2)
        
        btn_frame = ctk.CTkFrame(right_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ctk.CTkButton(btn_frame, text="+ Adicionar", command=self._add_videos).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="- Remover", command=self._remove_videos).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="Cima", command=self._move_up).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="Baixo", command=self._move_down).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="🗑 Limpar Todos", command=self._limpar_todos_videos).pack(side='right', padx=2)
        
        style = ttk.Style()
        style.configure("Thumb.Treeview", rowheight=90)
        
        self.tree = ttk.Treeview(right_frame, columns=("path"), show="tree", height=4)
        self.tree.column("#0", width=250, stretch=tk.YES)
        self.tree.pack(fill='both', expand=True)
        scroll_tree = ctk.CTkScrollbar(right_frame, orientation="vertical", command=self.tree.yview)
        scroll_tree.pack(side=tk.RIGHT, fill='y')
        self.tree.configure(yscrollcommand=scroll_tree.set)
        


        self.btn_iniciar = ctk.CTkButton(self.f_bot, text="🚀 INICIAR GERAÇÃO DE VÍDEO", command=self._iniciar_mapeamento)
        self.btn_iniciar.pack(side='left', padx=10, pady=10, ipadx=20, ipady=10)

        self.btn_cancelar = ctk.CTkButton(self.f_bot, text="🛑 CANCELAR", command=self._cancelar_mapeamento, state='disabled')
        self.btn_cancelar.pack(side='left', padx=10, pady=10, ipadx=10, ipady=10)

        # Fase 26: Botão de Limpar Cache do Whisper
        ctk.CTkButton(self.f_bot, text="🧹 Limpar Cache Whisper", command=self._limpar_cache_whisper).pack(side='left', padx=10)
        
        self.enviar_timeline = tk.BooleanVar(value=True)
        ctk.CTkSwitch(self.f_bot, text="Enviar para Timeline Web ao concluir", variable=self.enviar_timeline).pack(side='left', padx=10)

        self.cancelar_flag = False
        
        self._carregar_cache()
        self._setup_auto_save()
        
        if self.config_manager:
            self._carregar_perfis_ui()
            self._carregar_perfis_estetica_ui()
            self._carregar_perfis_transicao_template()
            self._carregar_perfis_diretor_ui()

    def _carregar_perfis_diretor_ui(self):
        if not self.config_manager: return
        perfis = self.config_manager.get("perfis_diretor", {})
        self.cb_perfil_diretor['values'] = list(perfis.keys())

    def _salvar_perfil_diretor(self):
        from tkinter.simpledialog import askstring
        if not self.config_manager: return
        nome = askstring("Salvar Perfil do Diretor", "Nome do Perfil:")
        if not nome: return
        
        cfg = self._get_current_diretor_config()
        perfis = self.config_manager.get("perfis_diretor", {})
        perfis[nome] = cfg
        self.config_manager.set("perfis_diretor", perfis)
        self.config_manager.save_config()
        self._carregar_perfis_diretor_ui()
        self.var_perfil_diretor.set(nome)
        messagebox.showinfo("Sucesso", f"Perfil do Diretor '{nome}' salvo!")

    def _deletar_perfil_diretor(self):
        nome = self.var_perfil_diretor.get()
        if not nome or not self.config_manager: return
        if messagebox.askyesno("Confirmar", f"Deletar perfil '{nome}'?"):
            perfis = self.config_manager.get("perfis_diretor", {})
            if nome in perfis:
                del perfis[nome]
                self.config_manager.set("perfis_diretor", perfis)
                self.config_manager.save_config()
                self.var_perfil_diretor.set("")
                self._carregar_perfis_diretor_ui()

    def _get_current_diretor_config(self):
        def safe_int(var, default=0):
            try: return int(var.get())
            except: return default
        
        return {
            'saida_dir': self.saida_dir.get(),
            'transicoes_dir': self.transicoes_dir.get(),
            'prob_transicao': safe_int(self.prob_transicao, 70),
            'video_format': self.video_format.get(),
            'musica_path': self.musica_path.get(),
            'vol_musica': safe_int(self.vol_musica, -15),
            'var_legenda': self.var_legenda.get(),
            'sub_font': self.sub_font.get(),
            'sub_words': safe_int(self.sub_words, 5),
            'sub_pos': self.sub_pos.get(),
            'sub_theme': self.sub_theme.get(),
            'sub_size': safe_int(self.sub_size, 100),
            'sub_margin_v': safe_int(self.sub_margin_v, 150),
            'sub_effect': self.sub_effect.get(),
            'var_perfil_estetica': self.var_perfil_estetica.get(),
            'var_perfil_legenda': self.var_perfil_legenda.get(),
            'var_transicao_template': self.var_transicao_template.get(),
            'perfil_unico': self.perfil_unico.get(),
            'roteiro': self.text_mapeamento.get("1.0", tk.END).strip(),
            'base_loop_count': safe_int(self.base_loop_count, 0),
            'tipo_midia_upload': self.tipo_midia_upload.get(),
            'var_sincronizar_base': self.var_sincronizar_base.get(),
            'usar_roteiro_base': self.usar_roteiro_base.get(),
            'roteiro_base': self.text_map_base.get("1.0", tk.END).strip(),
            'lay1_fundo_path': self.lay1_fundo_path.get(),
            'lay2_narrador_path': self.lay2_narrador_path.get(),
            'lay3_frente_path': self.lay3_frente_path.get(),
            'lay4_moldura_dir': self.lay4_moldura_dir.get(),
        }

    def _set_diretor_config(self, cfg):
        if not cfg: return
        
        if 'saida_dir' in cfg: self.saida_dir.set(cfg['saida_dir'])
        if 'transicoes_dir' in cfg: self.transicoes_dir.set(cfg['transicoes_dir'])
        if 'prob_transicao' in cfg: self.prob_transicao.set(cfg['prob_transicao'])
        if 'video_format' in cfg: self.video_format.set(cfg['video_format'])
        if 'musica_path' in cfg: self.musica_path.set(cfg['musica_path'])
        if 'vol_musica' in cfg: self.vol_musica.set(cfg['vol_musica'])
        if 'var_legenda' in cfg: self.var_legenda.set(cfg['var_legenda'])
        if 'sub_font' in cfg: self.sub_font.set(cfg['sub_font'])
        if 'sub_words' in cfg: self.sub_words.set(cfg['sub_words'])
        if 'sub_pos' in cfg: self.sub_pos.set(cfg['sub_pos'])
        if 'sub_theme' in cfg: self.sub_theme.set(cfg['sub_theme'])
        if 'sub_size' in cfg: self.sub_size.set(cfg['sub_size'])
        if 'sub_margin_v' in cfg: self.sub_margin_v.set(cfg['sub_margin_v'])
        if 'sub_effect' in cfg: self.sub_effect.set(cfg['sub_effect'])
        if 'var_perfil_estetica' in cfg: self.var_perfil_estetica.set(cfg['var_perfil_estetica'])
        if 'var_perfil_legenda' in cfg: self.var_perfil_legenda.set(cfg['var_perfil_legenda'])
        if 'var_transicao_template' in cfg: self.var_transicao_template.set(cfg['var_transicao_template'])
        if 'perfil_unico' in cfg: self.perfil_unico.set(cfg['perfil_unico'])
        if 'base_loop_count' in cfg: self.base_loop_count.set(cfg['base_loop_count'])
        if 'tipo_midia_upload' in cfg: self.tipo_midia_upload.set(cfg['tipo_midia_upload'])
        if 'var_sincronizar_base' in cfg: self.var_sincronizar_base.set(cfg['var_sincronizar_base'])
        if 'usar_roteiro_base' in cfg: self.usar_roteiro_base.set(cfg['usar_roteiro_base'])
        if 'lay1_fundo_path' in cfg: self.lay1_fundo_path.set(cfg['lay1_fundo_path'])
        if 'lay2_narrador_path' in cfg: self.lay2_narrador_path.set(cfg['lay2_narrador_path'])
        if 'lay3_frente_path' in cfg: self.lay3_frente_path.set(cfg['lay3_frente_path'])
        if 'lay4_moldura_dir' in cfg: self.lay4_moldura_dir.set(cfg['lay4_moldura_dir'])
        
        if 'roteiro' in cfg:
            self.text_mapeamento.delete("1.0", tk.END)
            self.text_mapeamento.insert("1.0", cfg['roteiro'])
            
        if 'roteiro_base' in cfg:
            self.text_map_base.delete("1.0", tk.END)
            self.text_map_base.insert("1.0", cfg['roteiro_base'])

        self._aplicar_perfil_estetica()
        self._aplicar_perfil_legenda()
        self._toggle_roteiro_base()
        self._toggle_modo()

    def _aplicar_perfil_diretor(self, event=None):
        nome = self.var_perfil_diretor.get()
        if not nome or not self.config_manager: return
        perfis = self.config_manager.get("perfis_diretor", {})
        if nome in perfis:
            self._set_diretor_config(perfis[nome])

    def _puxar_ultimo_tts(self):
        """Puxa o caminho do último áudio gerado na aba TTS (Memória Ativa)."""
        try:
            from database_manager import db
            # Opcional: puxar apenas do canal ativo, mas como é TTS global, o default get funciona bem.
            ultimo = db.get_memoria("ultimo_audio_tts")
            if ultimo and os.path.exists(ultimo):
                self.audio_path.set(ultimo)
                messagebox.showinfo("Memória Ativa", f"Áudio puxado com sucesso:\n{ultimo}")
                self._salvar_cache()
            else:
                messagebox.showwarning("Aviso", "Nenhum áudio encontrado na Memória Ativa ou o arquivo não existe mais.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao acessar Memória Ativa: {e}")

    def _toggle_tema_ctrl_mapeador(self):
        """Desabilita edição global de legenda quando um mapa de cores de Podcast está carregado, pois o mapa puxará individualmente por personagem."""
        if hasattr(self, 'cb_perfil_legenda'):
            state = 'disabled' if self.mapa_temas_path.get().strip() else 'normal'
            for ctrl in [self.cb_perfil_legenda, self.ctrl_sub_font, self.ctrl_sub_words, 
                         self.ctrl_sub_pos, self.ctrl_sub_theme, self.ctrl_sub_size, 
                         self.ctrl_sub_margin_v, self.ctrl_sub_effect]:
                if hasattr(ctrl, 'config'):
                    ctrl.configure(state=state)
                
            
    def _carregar_perfis_transicao_template(self):
        if not self.config_manager: return
        perfis = self.config_manager.get("perfis_transicao_template", {})
        self.cb_transicao_template['values'] = ["[Corte Seco]"] + list(perfis.keys())
        if not self.var_transicao_template.get():
            self.var_transicao_template.set("[Corte Seco]")

    def _carregar_perfis_estetica_ui(self):
        if not self.config_manager: return
        perfis = self.config_manager.get("perfis_estetica", {})
        self.cb_perfil_estetica['values'] = ["[Personalizado]"] + list(perfis.keys())

    def _aplicar_perfil_estetica(self, event=None):
        nome = self.var_perfil_estetica.get()
        if not nome or not self.config_manager: return
        
        def set_state(st):
            for c in [self.ctrl_master_hd, self.ctrl_master_overlay, 
                      self.ctrl_master_xfade, self.ctrl_master_lut, self.ctrl_master_cor, 
                      self.ctrl_master_cam, self.ctrl_prob_transicao]:
                if hasattr(self, 'ctrl_master_hd'):  # Check if UI is already created
                    c.configure(state=st)
        
        if nome == "[Personalizado]":
            set_state("normal")
            return
            
        perfis = self.config_manager.get("perfis_estetica", {})
        if nome in perfis:
            est = perfis[nome]
            self.config_manager.set("estetica_canal", est)
            self.master_hd.set(est.get("master_hd", True))
            self.master_overlay.set(est.get("master_overlay", True))
            self.master_xfade.set(est.get("master_xfade", True))
            self.master_lut.set(est.get("master_lut", True))
            self.master_cor.set(est.get("master_cor", True))
            self.master_cam.set(est.get("master_cam", True))
            self.prob_transicao.set(est.get("prob_transicao", 100))
            self._salvar_cache()
            set_state("disabled")
            
    def _carregar_perfis_ui(self):
        if not self.config_manager: return
        perfis = self.config_manager.get("perfis_legenda", {})
        self.cb_perfil_legenda['values'] = ["[Personalizado]"] + list(perfis.keys())

    def _aplicar_perfil_legenda(self, event=None):
        nome = self.var_perfil_legenda.get()
        if not nome or not self.config_manager: return
        
        def set_state(st):
            for c in [self.ctrl_sub_font, self.ctrl_sub_words, self.ctrl_sub_pos,
                      self.ctrl_sub_theme, self.ctrl_sub_size, self.ctrl_sub_margin_v,
                      self.ctrl_sub_effect]:
                if hasattr(self, 'ctrl_sub_font'):
                    c.configure(state=st)
                    
        if nome == "[Personalizado]":
            set_state("normal")
            return
            
        perfis = self.config_manager.get("perfis_legenda", {})
        if nome in perfis:
            p = perfis[nome]
            self.sub_font.set(p.get("font", "Bangers"))
            self.sub_words.set(p.get("words", 5))
            self.sub_pos.set(p.get("pos", "meio baixo"))
            self.sub_theme.set(p.get("theme", "amarelo vermelho"))
            self.sub_size.set(p.get("size", 100))
            self.sub_margin_v.set(p.get("margin_v", 150))
            self.sub_effect.set(p.get("effect", "Pulo (Pop)"))
            self._salvar_cache()
            set_state("disabled")
        
    def _poll_thumb_queue(self):
        """Roda exclusivamente na main thread. Consome a fila de thumbnails e cria PhotoImages com segurança."""
        try:
            while True:
                path, iid, pil_img = self._thumb_queue.get_nowait()
                try:
                    if PIL_AVAILABLE:
                        photo = ImageTk.PhotoImage(pil_img)
                        self.thumbnail_cache[path] = photo
                        self.tree.item(iid, image=photo)
                except Exception:
                    pass
        except queue.Empty:
            pass
        # Re-agenda o próximo poll daqui 200ms (sem criar novos registros do Tkinter)
        self.after(200, self._poll_thumb_queue)

    def _limpar_todos_videos(self):
        """Remove todos os vídeos da lista de uma vez."""
        if not self.video_paths:
            return
        if not messagebox.askyesno("Confirmar", f"Remover todos os {len(self.video_paths)} vídeos da lista?"):
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.video_paths.clear()
        self.thumbnail_cache.clear()
        self._salvar_cache()

    def log(self, msg):
        def _append_log():
            try:
                self.console_log.configure(state='normal')
                self.console_log.insert(tk.END, msg + "\n")
                self.console_log.see(tk.END)
                self.console_log.configure(state='disabled')
                self.update_idletasks()
            except Exception:
                pass
        self.after(0, _append_log)

    def _ui_call(self, fn, *args, **kwargs):
        self.after(0, lambda: fn(*args, **kwargs))

    def _ui_call_result(self, fn, *args, **kwargs):
        """[ETAPA 16] Executa uma função na thread da UI e aguarda o resultado (síncrono)."""
        import queue
        result_q = queue.Queue()
        def _run():
            try:
                result_q.put(fn(*args, **kwargs))
            except Exception as e:
                result_q.put(True)  # Em caso de erro, não bloqueia o render
        self.after(0, _run)
        try:
            return result_q.get(timeout=600)  # Aguarda até 10 minutos pelo usuário
        except Exception:
            return True  # Timeout = continua renderizando

    def _ui_status(self, msg):
        self._ui_call(self.status.set, msg)
        self._ui_call(self.log, msg)

    def _ui_progress(self, value):
        self._ui_call(self.progress_var.set, value)

    def _ui_error(self, msg):
        self._ui_call(messagebox.showerror, "Erro", msg)

    def _ui_info(self, title, msg):
        self._ui_call(messagebox.showinfo, title, msg)

    # Função _log_ia removida para desativar telemetria antiga do Gemini

    def _registrar_historico(self, saida, audio, status="sucesso", detalhe=""):
        """
        [PARTE 11] Registra o resultado de um render no histórico global de produção usando SQLite.
        """
        import uuid
        import os
        try:
            from database_manager import db
            
            # Descobre o perfil ativo
            _cm = getattr(self, "config_manager", None)
            perfil_ativo = ""
            if _cm:
                _app = getattr(self, "_app_ref", None)
                if _app and hasattr(_app, "aba_perfis_canal"):
                    # Tenta pegar o perfil selecionado
                    lb = _app.aba_perfis_canal.lb_perfis
                    sel = lb.curselection()
                    if sel:
                        perfil_ativo = lb.get(sel[0])

            if perfil_ativo:
                canal_id = db.registrar_canal(perfil_ativo, "")
            else:
                canal_id = db.registrar_canal("Legado_Geral", "")

            job_id = f"render_{uuid.uuid4().hex[:8]}"
            titulo = os.path.basename(saida) if saida else "Render Diretor"
            
            db.registrar_video(canal_id, job_id, titulo, "{}", "pendente")
            db.atualizar_status_video(job_id, status, filepath=saida, erro=detalhe[:200] if detalhe else "")
        except Exception as e:
            import logging
            logging.warning(f"[HISTORICO DB] Falha ao registrar: {e}")

    def _bind_mousewheel(self, _event=None):
        self.canvas_form.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event=None):
        self.canvas_form.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        # Scroll vertical do painel esquerdo (Windows: delta em múltiplos de 120)
        self._left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _setup_auto_save(self):
        vars_to_trace = [
            self.audio_path, self.saida_dir, self.transicoes_dir, 
            self.prob_transicao, self.video_format,
            self.musica_path, self.vol_musica, self.var_legenda,
            self.sub_font, self.sub_words, self.sub_pos, self.sub_theme, self.sub_size, self.sub_margin_v, self.sub_effect,
            self.base_loop_count, self.tipo_midia_upload, self.var_sincronizar_base, self.usar_roteiro_base,
            self.lay1_fundo_path, self.lay2_narrador_path, self.lay3_frente_path, self.lay4_moldura_dir
        ]
        for v in vars_to_trace:
            v.trace_add('write', lambda *args: self._salvar_cache())
            
        self.text_mapeamento.bind('<KeyRelease>', lambda e: self._salvar_cache())

    def _salvar_cache(self):
        def safe_int(var, default=0):
            try:
                return int(var.get())
            except (ValueError, tk.TclError):
                return default

        data = {
            'enviar_timeline': getattr(self, 'enviar_timeline', tk.BooleanVar(value=True)).get(),
            'audio_path': self.audio_path.get(),
            'saida_dir': self.saida_dir.get(),
            'transicoes_dir': self.transicoes_dir.get(),
            'prob_transicao': safe_int(self.prob_transicao, 70),
            'video_format': self.video_format.get(),
            'musica_path': self.musica_path.get(),
            'vol_musica': safe_int(self.vol_musica, -15),
            'var_legenda': self.var_legenda.get(),
            'sub_font': self.sub_font.get(),
            'sub_words': safe_int(self.sub_words, 5),
            'sub_pos': self.sub_pos.get(),
            'sub_theme': self.sub_theme.get(),
            'sub_size': safe_int(self.sub_size, 100),
            'sub_margin_v': safe_int(self.sub_margin_v, 150),
            'sub_effect': self.sub_effect.get(),
            'var_perfil_estetica': self.var_perfil_estetica.get(),
            'var_perfil_legenda': self.var_perfil_legenda.get(),
            'var_transicao_template': self.var_transicao_template.get(),
            'perfil_unico': self.perfil_unico.get(),
            'roteiro': self.text_mapeamento.get("1.0", tk.END).strip(),
            'base_loop_count': safe_int(self.base_loop_count, 0),
            'tipo_midia_upload': self.tipo_midia_upload.get(),
            'var_sincronizar_base': self.var_sincronizar_base.get(),
            'usar_roteiro_base': self.usar_roteiro_base.get(),
            'roteiro_base': self.text_map_base.get("1.0", tk.END).strip(),
            'lay1_fundo_path': self.lay1_fundo_path.get(),
            'lay2_narrador_path': self.lay2_narrador_path.get(),
            'lay3_frente_path': self.lay3_frente_path.get(),
            'lay4_moldura_dir': self.lay4_moldura_dir.get(),
            'video_paths': self.video_paths
        }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e: print(e)

    def _carregar_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'enviar_timeline' in data and hasattr(self, 'enviar_timeline'): self.enviar_timeline.set(data['enviar_timeline'])
                if 'audio_path' in data: self.audio_path.set(data['audio_path'])
                if 'saida_dir' in data: self.saida_dir.set(data['saida_dir'])
                if 'transicoes_dir' in data: self.transicoes_dir.set(data['transicoes_dir'])
                if 'prob_transicao' in data: self.prob_transicao.set(data['prob_transicao'])
                if 'video_format' in data: self.video_format.set(data['video_format'])
                if 'musica_path' in data: self.musica_path.set(data['musica_path'])
                if 'vol_musica' in data: self.vol_musica.set(data['vol_musica'])
                if 'var_legenda' in data: self.var_legenda.set(data['var_legenda'])
                if 'sub_font' in data: self.sub_font.set(data['sub_font'])
                if 'sub_words' in data: self.sub_words.set(data['sub_words'])
                if 'sub_pos' in data: self.sub_pos.set(data['sub_pos'])
                if 'sub_theme' in data: self.sub_theme.set(data['sub_theme'])
                if 'sub_size' in data: self.sub_size.set(data['sub_size'])
                if 'sub_margin_v' in data: self.sub_margin_v.set(data['sub_margin_v'])
                if 'sub_effect' in data: self.sub_effect.set(data['sub_effect'])
                if 'var_transicao_template' in data: self.var_transicao_template.set(data['var_transicao_template'])
                if 'perfil_unico' in data: self.perfil_unico.set(data['perfil_unico'])
                if 'base_loop_count' in data: self.base_loop_count.set(data['base_loop_count'])
                if 'tipo_midia_upload' in data: self.tipo_midia_upload.set(data['tipo_midia_upload'])
                if 'var_sincronizar_base' in data: self.var_sincronizar_base.set(data['var_sincronizar_base'])
                if 'usar_roteiro_base' in data: self.usar_roteiro_base.set(data['usar_roteiro_base'])
                if 'lay1_fundo_path' in data: self.lay1_fundo_path.set(data['lay1_fundo_path'])
                if 'lay2_narrador_path' in data: self.lay2_narrador_path.set(data['lay2_narrador_path'])
                if 'lay3_frente_path' in data: self.lay3_frente_path.set(data['lay3_frente_path'])
                if 'lay4_moldura_dir' in data: self.lay4_moldura_dir.set(data['lay4_moldura_dir'])
                
                self._toggle_modo()
                self._toggle_roteiro_base()
                
                if 'var_perfil_estetica' in data and data['var_perfil_estetica']:
                    self.var_perfil_estetica.set(data['var_perfil_estetica'])
                    self._aplicar_perfil_estetica()
                else:
                    self.var_perfil_estetica.set("[Personalizado]")
                    self._aplicar_perfil_estetica()
                    
                if 'var_perfil_legenda' in data and data['var_perfil_legenda']:
                    self.var_perfil_legenda.set(data['var_perfil_legenda'])
                    self._aplicar_perfil_legenda()
                else:
                    self.var_perfil_legenda.set("[Personalizado]")
                    self._aplicar_perfil_legenda()
                
                if 'roteiro' in data and data['roteiro']:
                    self.text_mapeamento.delete("1.0", tk.END)
                    self.text_mapeamento.insert(tk.END, data['roteiro'])
                
                if 'roteiro_base' in data and data['roteiro_base']:
                    self.text_map_base.configure(state='normal')
                    self.text_map_base.delete("1.0", tk.END)
                    self.text_map_base.insert(tk.END, data['roteiro_base'])
                    self._toggle_roteiro_base()
                    
                if 'video_paths' in data and data['video_paths']:
                    # Limpa primeiro
                    for item in self.tree.get_children():
                        self.tree.delete(item)
                    self.video_paths = []
                    # Reconstrói
                    for p in data['video_paths']:
                        if os.path.exists(p):
                            self.video_paths.append(p)
                            item_id = self.tree.insert("", tk.END, text=" " + os.path.basename(p), values=(p,))
                            def load_thumb(path, iid):
                                pil_img = self._extract_thumb_pil(path)
                                if pil_img:
                                    self._thumb_queue.put((path, iid, pil_img))
                            threading.Thread(target=load_thumb, args=(p, item_id), daemon=True).start()
                            
            except Exception as e:
                print(f"Erro ao carregar cache: {e}")

    def _toggle_modo(self, event=None):
        modo = self.perfil_unico.get()
        if modo == "[Mapeamento Automático - Roteiro 5.2]":
            # Habilita 5.2
            for child in self.f_map.winfo_children():
                try: child.configure(state='normal')
                except Exception: pass
            if hasattr(self, 'cb_transicao_template'):
                self.cb_transicao_template.configure(state='normal')
            self.text_mapeamento.configure(state='normal')
        else:
            # Desabilita 5.2
            for child in self.f_map.winfo_children():
                try: child.configure(state='disabled')
                except Exception: pass
            if hasattr(self, 'cb_transicao_template'):
                self.cb_transicao_template.configure(state='disabled')
            self.text_mapeamento.configure(state='disabled')

    def _toggle_roteiro_base(self):
        if self.usar_roteiro_base.get():
            self.text_map_base.configure(state='normal')
        else:
            self.text_map_base.configure(state='disabled')

    def _atualizar_lista_perfis(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tpl_dir = os.path.join(base_dir, "perfis_templates")
        perfis = []
        if os.path.exists(tpl_dir):
            perfis = [f.replace('.json', '') for f in os.listdir(tpl_dir) if f.endswith('.json')]
        
        opcoes = ["[Sem Template - Apenas Vídeo Base]", "[Mapeamento Automático - Roteiro 5.2]"] + perfis
        self.combo_perfil['values'] = opcoes
        
        if self.perfil_unico.get() not in opcoes:
            self.perfil_unico.set(opcoes[0])
            self._toggle_modo()

    def _extract_thumb_pil(self, video_path):
        """Extrai thumbnail como PIL Image (thread-safe). A conversão para PhotoImage deve ser feita na main thread."""
        is_image = video_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        thumb_path = os.path.join(os.path.dirname(video_path), "thumb_cache_" + os.path.basename(video_path) + ".jpg")
        
        if is_image:
            if PIL_AVAILABLE:
                try:
                    img = Image.open(video_path)
                    img.thumbnail((160, 90))
                    return img
                except Exception: return None
            return None
            
        if not os.path.exists(thumb_path):
            try:
                cmd = [FFMPEG_EXE, '-y', '-threads', '0', '-i', video_path, '-ss', '00:00:01', '-vframes', '1', '-s', '160x90', thumb_path]
                subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
            except Exception: return None
        
        if os.path.exists(thumb_path) and PIL_AVAILABLE:
            try:
                img = Image.open(thumb_path)
                img.thumbnail((160, 90))
                return img
            except Exception: return None
        return None

    def _add_videos(self):
        tipo = self.tipo_midia_upload.get()
        if tipo == "Somente Fotos":
            ft = [("Fotos", "*.png;*.jpg;*.jpeg;*.webp")]
        elif tipo == "Somente Vídeos":
            ft = [("Vídeos", "*.mp4;*.mov;*.mkv;*.avi")]
        else:
            ft = [("Mídias Base", "*.mp4;*.mov;*.mkv;*.avi;*.png;*.jpg;*.jpeg;*.webp")]
            
        paths = filedialog.askopenfilenames(filetypes=ft)
        for p in paths:
            if p not in self.video_paths:
                self.video_paths.append(p)
                item_id = self.tree.insert("", tk.END, text=" " + os.path.basename(p), values=(p,))
                def load_thumb(path, iid):
                    pil_img = self._extract_thumb_pil(path)
                    if pil_img:
                        self._thumb_queue.put((path, iid, pil_img))
                threading.Thread(target=load_thumb, args=(p, item_id), daemon=True).start()

    def _remove_videos(self):
        for item in self.tree.selection():
            val = self.tree.item(item, "values")[0]
            if val in self.video_paths:
                self.video_paths.remove(val)
            self.tree.delete(item)

    def _move_up(self):
        for item in self.tree.selection():
            idx = self.tree.index(item)
            if idx > 0:
                self.tree.move(item, self.tree.parent(item), idx - 1)
                self.video_paths.insert(idx - 1, self.video_paths.pop(idx))

    def _move_down(self):
        items = self.tree.selection()
        for item in reversed(items):
            idx = self.tree.index(item)
            if idx < len(self.tree.get_children()) - 1:
                self.tree.move(item, self.tree.parent(item), idx + 1)
                self.video_paths.insert(idx + 1, self.video_paths.pop(idx))

    def _pick_file(self, var, types):
        path = filedialog.askopenfilename(filetypes=types)
        if path: var.set(path)
        
    def _pick_multiple_files(self, var, types):
        paths = filedialog.askopenfilenames(filetypes=types)
        if paths: var.set("|".join(paths))
        
    def _pick_dir(self, var):
        path = filedialog.askdirectory()
        if path: var.set(path)

    def _limpar_cache_whisper(self):
        """Fase 26: Apaga o cache .json do áudio atual para forçar nova transcrição."""
        audio = self.audio_path.get()
        if not audio:
            messagebox.showwarning("Aviso", "Nenhum áudio selecionado para limpar o cache.")
            return
        cache_path = audio + ".whisper_cache.json"
        if os.path.exists(cache_path):
            os.remove(cache_path)
            messagebox.showinfo("Cache Limpo", f"Cache removido.\nPróximo render vai retranscrever o áudio.")
        else:
            messagebox.showinfo("Aviso", "Nenhum cache encontrado para este áudio.")

    def _salvar_roteiro(self):
        """Fase 29: Exporta o roteiro do textbox como .txt"""
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Texto", "*.txt")], title="Salvar Roteiro")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.text_mapeamento.get("1.0", tk.END))
            messagebox.showinfo("Salvo", f"Roteiro salvo em:\n{path}")

    def _carregar_roteiro(self):
        """Fase 29: Importa um roteiro .txt para o textbox"""
        path = filedialog.askopenfilename(filetypes=[("Texto", "*.txt")], title="Carregar Roteiro")
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            self.text_mapeamento.delete("1.0", tk.END)
            self.text_mapeamento.insert(tk.END, conteudo)



    def _cancelar_mapeamento(self):
        if messagebox.askyesno("Confirmar", "Deseja cancelar o processo em andamento?"):
            self.cancelar_flag = True
            self.status.set("Cancelando... (Aguarde os processos atuais finalizarem)")

    def _iniciar_mapeamento(self):
        # 0. Sanitizar caminhos de arquivos (remover aspas duplas do Windows)
        for attr_name in dir(self):
            if 'path' in attr_name or 'dir' in attr_name or 'audio' in attr_name or 'musica' in attr_name:
                attr = getattr(self, attr_name)
                if hasattr(attr, 'get') and hasattr(attr, 'set'):
                    try:
                        val = attr.get()
                        if isinstance(val, str) and ('"' in val or "'" in val):
                            attr.set(val.strip().strip('"').strip("'"))
                    except Exception:
                        pass

        def _safe_int_now(var, default):
            try:
                return int(var.get())
            except (ValueError, tk.TclError):
                return default

        self.cancelar_flag = False
        audio = self.audio_path.get()
        saida = self.saida_dir.get()
        roteiro = self.text_mapeamento.get("1.0", tk.END).strip()
        usar_roteiro_base_ui = self.usar_roteiro_base.get()
        roteiro_base_ui = self.text_map_base.get("1.0", tk.END).strip()
        video_paths_ui = list(self.video_paths)
        perfil_unico_ui = self.perfil_unico.get()
        usar_mapeamento_ui = (perfil_unico_ui == "[Mapeamento Automático - Roteiro 5.2]")
        var_legenda_ui = self.var_legenda.get()
        var_transicao_template_ui = self.var_transicao_template.get() if hasattr(self, 'var_transicao_template') else "[Corte Seco]"
        prob_transicao_ui = _safe_int_now(self.prob_transicao, 70)
        sincronizar_base_ui = self.var_sincronizar_base.get()
        base_loop_count_ui = _safe_int_now(self.base_loop_count, -1)
        video_format_ui = self.video_format.get()
        lay2_narrador_path_ui = self.lay2_narrador_path.get()
        lay3_frente_path_ui = self.lay3_frente_path.get()
        lay4_moldura_dir_ui = self.lay4_moldura_dir.get()
        musica_ui = self.musica_path.get()
        vol_musica_ui = _safe_int_now(self.vol_musica, -15)
        sub_font_ui = self.sub_font.get()
        sub_size_ui = _safe_int_now(self.sub_size, 100)
        sub_theme_ui = self.sub_theme.get()
        sub_colors_ui = None
        perfil_nome_ui = self.var_perfil_legenda.get() if hasattr(self, 'var_perfil_legenda') else "[Personalizado]"
        if perfil_nome_ui and perfil_nome_ui != "[Personalizado]":
            perfis = self.config_manager.get("perfis_legenda", {}) if self.config_manager else {}
            if perfil_nome_ui in perfis and 'colors' in perfis[perfil_nome_ui]:
                sub_colors_ui = perfis[perfil_nome_ui]['colors']
        sub_pos_ui = self.sub_pos.get()
        sub_margin_v_ui = _safe_int_now(self.sub_margin_v, 150)
        sub_words_ui = _safe_int_now(self.sub_words, 5)
        sub_effect_ui = self.sub_effect.get() if hasattr(self, 'sub_effect') else 'Pulo (Pop)'
        
        modo_ritmo_ui = getattr(self, 'modo_ritmo', tk.StringVar(value="tts")).get()
        
        if modo_ritmo_ui != "lipsync" and (not audio or not os.path.exists(audio)):
            messagebox.showerror("Erro", "Selecione o arquivo de áudio principal.")
            return
        if not saida:
            messagebox.showerror("Erro", "Selecione a pasta de saída.")
            return
        if not roteiro:
            messagebox.showerror("Erro", "Digite o roteiro com as marcações de perfil. (Para Lip Sync, basta listar os perfis por linha).")
            return
        
        # ─── PRÉ-VALIDAÇÃO COMPLETA ─────────────────────────────────────────
        erros = []
        avisos = []
        base_dir_check = os.path.dirname(os.path.abspath(__file__))
        
        if usar_mapeamento_ui:
            # Verifica cada perfil citado no roteiro
            perfis_citados = set()
            for part in roteiro.split('['):
                if ']' in part:
                    tag = part.split(']')[0].strip().split('|')[0].strip()
                    if tag and tag != 'SEM_PERFIL':
                        perfis_citados.add(tag)
            for p in perfis_citados:
                pf = os.path.join(base_dir_check, 'perfis_templates', f'{p}.json')
                if not os.path.exists(pf):
                    erros.append(f'Perfil não encontrado: [{p}]')
            
            if not perfis_citados and '[' not in roteiro:
                erros.append('Nenhuma tag [Perfil] encontrada no roteiro. Use o formato [NomePerfil] Texto...')
        
        if not self.video_paths and not self.text_map_base.get('1.0', tk.END).strip():
            avisos.append('Nenhum vídeo na lista e nenhum roteiro base. Fundo será preto.')
        
        for v in self.video_paths:
            if not os.path.exists(v):
                erros.append(f'Vídeo não encontrado: {os.path.basename(v)}')
        
        musica_val = self.musica_path.get()
        if musica_val:
            for m in musica_val.split('|'):
                if m.strip() and not os.path.exists(m.strip()):
                    avisos.append(f'Música não encontrada: {os.path.basename(m.strip())}')
        
        if erros:
            messagebox.showerror('Erro de Validação', '❌ CORRIJA ANTES DE RENDERIZAR:·········\n\n' + '\n'.join(f'  • {e}' for e in erros))
            return
        if avisos:
            if not messagebox.askyesno('Avisos', '⚠️ AVISOS (continuar mesmo assim?):\n\n' + '\n'.join(f'  • {a}' for a in avisos) + '\n\nDeseja continuar?'):
                return
        # ─── FIM DA PRÉ-VALIDAÇÃO ─────────────────────────────────────────

        self.btn_iniciar.configure(state='disabled')
        self.btn_cancelar.configure(state='normal')
        self.status.set("Preparando Mapeamento...")
        self.progress_var.set(0)
        self.console_log.configure(state='normal')
        self.console_log.delete('1.0', tk.END)
        self.console_log.configure(state='disabled')
        self.log("=== INICIANDO GERAÇÃO DE VÍDEO ===")
        
        # [DIRETOR IA - PRÉ-PRODUÇÃO] Lê o estado atual da aba Diretor IA
        _app_ref = getattr(self, '_app_ref', None)
        _ia_cfg = {}
        _prompt_estrategico = ""
        _prompt_canal = ""
        if _app_ref and hasattr(_app_ref, 'aba_diretor_ia'):
            try:
                _ia_cfg = _app_ref.aba_diretor_ia.get_config()
                _prompt_estrategico = _app_ref.aba_diretor_ia.get_prompt_estrategico()
                _prompt_canal = _app_ref.aba_diretor_ia.get_prompt_canal()
                _mods_ativos = [k for k,v in _ia_cfg.items() if v is True]
                if _mods_ativos:
                    self.log(f"[DIRETOR IA] Pre-producao ativa: {', '.join(_mods_ativos)}")
                else:
                    self.log("[DIRETOR IA] Nenhum modulo de IA ativado. Render padrao.")
                if _prompt_estrategico:
                    self.log(f"[DIRETOR IA] Estrategia: {_prompt_estrategico[:100]}{'...' if len(_prompt_estrategico) > 100 else ''}")
                    _app_ref.aba_diretor_ia.log(f"[RENDER INICIADO] Pipeline ativa com estrategia de {len(_prompt_estrategico)} chars.")
                if _prompt_canal:
                    self.log(f"[DIRETOR IA] Identidade Canal: {_prompt_canal[:50]}...")
            except Exception as _e:
                self.log(f"[DIRETOR IA] Erro ao ler config da aba IA: {_e}")
        
        self._render_log_path = os.path.join(saida, "render.log")  # LOG PERSISTENTE
        try:
            os.makedirs(saida, exist_ok=True)
            with open(self._render_log_path, 'w', encoding='utf-8') as _f:
                import datetime
                _f.write(f"=== RENDER LOG - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        except Exception as e: print(e)
        
        def worker():
            _cm = getattr(self, 'config_manager', None)
            estetica_cfg = _cm.get("estetica_canal", {}) if _cm else {}
            _ia_pipeline_obj = None  # Será inicializado na secao IA abaixo
            
            # Master Switches Globais — lê direto dos BooleanVars da UI (fonte primária)
            # Fallback para estetica_cfg caso os vars nao existam (robustez)
            def _get_master(var_name, cfg_key):
                v = getattr(self, var_name, None)
                if v is not None:
                    try: return bool(v.get())
                    except Exception as e: print(e)
                return estetica_cfg.get(cfg_key, True)

            m_hd      = _get_master('master_hd',      'master_hd')
            m_overlay  = _get_master('master_overlay', 'master_overlay')
            m_xfade   = _get_master('master_xfade',    'master_xfade')
            m_lut     = _get_master('master_lut',      'master_lut')
            m_cor     = _get_master('master_cor',      'master_cor')
            m_cam     = _get_master('master_cam',      'master_cam')
            
            usar_transicoes_hd_ui = m_hd
            usar_particulas_hd_ui = m_overlay
            usar_transicoes_ffmpeg_ui = m_xfade
            
            profile_data = None
            p_tipo = "XFade"
            p_xfade = "fade"
            p_dur = 1.5
            p_hd_video = ""
            if usar_mapeamento_ui and var_transicao_template_ui and var_transicao_template_ui != "[Corte Seco]":
                perfis_trans = _cm.get("perfis_transicao_template", {}) if _cm else {}
                profile_data = perfis_trans.get(var_transicao_template_ui)
                if profile_data:
                    p_tipo = profile_data.get("tipo", "XFade")
                    p_xfade = profile_data.get("xfade_name", "fade")
                    try:
                        p_dur = float(profile_data.get("duracao", 1.5))
                    except Exception as e:
                        p_dur = 1.5
                    p_hd_video = profile_data.get("hd_video", "")
                    
                    if p_tipo == "XFade":
                        usar_transicoes_ffmpeg_ui = m_xfade
                        usar_transicoes_hd_ui = False
                    elif p_tipo == "HD":
                        usar_transicoes_ffmpeg_ui = False
                        usar_transicoes_hd_ui = m_hd
                    elif p_tipo == "Ambos":
                        usar_transicoes_ffmpeg_ui = m_xfade
                        usar_transicoes_hd_ui = m_hd
            elif usar_mapeamento_ui and var_transicao_template_ui == "[Corte Seco]":
                usar_transicoes_hd_ui = False
                usar_transicoes_ffmpeg_ui = False
            usar_filtros_luz_ui = m_cor or m_cam or m_lut

            # Variáveis de UI capturadas dentro do worker para evitar UnboundLocalError
            # (necessário pois o Bug 17 criou uma atribuição local de var_legenda_ui
            # mais abaixo no worker, o que torna a variável local em todo o escopo)
            var_legenda_ui = bool(getattr(self.var_legenda, 'get', lambda: False)())
            
            self.active_transition_points_hd = []

            self.log(f"🎬 Masters: HD={m_hd} | OVL={m_overlay} | XFade={m_xfade} | LUT={m_lut} | Cor={m_cor} | Cam={m_cam}")
            
            nonlocal audio
            orig_zoom = estetica_cfg.get("var_zoom", True) and m_cam
            orig_pan = estetica_cfg.get("var_pan", True) and m_cam
            orig_tilt = estetica_cfg.get("var_tilt", True) and m_cam
            orig_shake = estetica_cfg.get("var_shake", True) and m_cam
            if m_cam and not any([orig_zoom, orig_pan, orig_tilt, orig_shake]):
                orig_zoom = orig_pan = orig_tilt = orig_shake = True
            orig_sinc = sincronizar_base_ui
            sincronizar_base_local = orig_sinc
            aplicar_fx_local = True
            audio_local = audio
            try:
                import random
                import concurrent.futures
                import os as _os
                import time
                import hardware_detector
                
                inicio_geracao = time.time()
                _hw_enc = hardware_detector.detect_h264_encoder()
                _vc_high_default = ['-c:v', 'libx264', '-crf', '18', '-preset', 'slower', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.2']
                _vc_base_default = ['-c:v', 'libx264', '-crf', '23', '-preset', 'medium', '-pix_fmt', 'yuv420p']
                _vc_high = [*_vc_high_default] if _hw_enc == 'libx264' else ['-c:v', _hw_enc, '-b:v', '8M', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.2']
                _vc_base = [*_vc_base_default] if _hw_enc == 'libx264' else ['-c:v', _hw_enc, '-b:v', '6M', '-pix_fmt', 'yuv420p']
                
                _cpu_count = _os.cpu_count() or 4
                _max_workers = max(2, min(_cpu_count - 1, 6))  # OTM: usa até N-1 núcleos (máx 6)

                def run_cmd_checked(cmd, step_name, cwd=None):
                    print(f"\n========================================", flush=True)
                    print(f"[EXEC] {step_name}", flush=True)
                    safe_cmd_str = ' '.join(str(c) for c in cmd)
                    print(f"Comando: {safe_cmd_str}", flush=True)
                    print(f"========================================\n", flush=True)
                    self._ui_call(self.log, f">>> {step_name}")  # OTM: log thread-safe na UI
                    # Grava no log persistente
                    try:
                        with open(getattr(self, '_render_log_path', ''), 'a', encoding='utf-8') as _lf:
                            _lf.write(f"\n[EXEC] {step_name}\n{safe_cmd_str}\n")
                    except Exception as e: print(e)
                    try:
                        process = subprocess.Popen(
                            cmd,
                            cwd=cwd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            encoding='utf-8',
                            errors='replace',
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        output_log = []
                        for line in process.stdout:
                            print(line, end='', flush=True)
                            output_log.append(line)
                        process.wait()
                        if process.returncode != 0:
                            err_text = "".join(output_log[-20:])
                            # Grava erro no log persistente
                            try:
                                with open(getattr(self, '_render_log_path', ''), 'a', encoding='utf-8') as _lf:
                                    _lf.write(f"[ERRO] {step_name}\n{err_text}\n")
                            except Exception as e: print(e)
                            raise Exception(f"{step_name} falhou.\n{err_text}")
                        return None
                    except Exception as e:
                        self._ui_status(f"[ERRO] {step_name}")
                        raise e

                def normalize_xfade_name(raw_name):
                    if not raw_name:
                        return "fade"
                    key = str(raw_name).strip().lower().replace(" ", "").replace("_", "").replace("-", "")
                    alias_map = {
                        "fade": "fade",
                        "dissolve": "fade",
                        "zoomin": "zoomin",
                        "zoomout": "zoomout",
                        "slideleft": "slideleft",
                        "slideright": "slideright",
                        "slideup": "slideup",
                        "slidedown": "slidedown",
                        "wipeleft": "wipeleft",
                        "wiperight": "wiperight",
                        "wipeup": "wipeup",
                        "wipedown": "wipedown",
                        "smoothleft": "smoothleft",
                        "smoothright": "smoothright",
                        "smoothup": "smoothup",
                        "smoothdown": "smoothdown",
                        "circlecrop": "circlecrop",
                        "rectcrop": "rectcrop",
                        "distance": "distance",
                        "fadeblack": "fadeblack",
                        "fadewhite": "fadewhite",
                        "radial": "radial",
                        "hblur": "hblur",
                        "pixelize": "pixelize",
                        "diagtl": "diagtl",
                        "diagtr": "diagtr",
                        "diagbl": "diagbl",
                        "diagbr": "diagbr",
                        "hlslice": "hlslice",
                        "hrslice": "hrslice",
                        "vuslice": "vuslice",
                        "vdslice": "vdslice",
                    }
                    return alias_map.get(key, "fade")
                
                # 1. Obter Blocos de Geração (Múltiplos ou Único)
                self.active_transition_points_hd = []
                blocos = []
                
                def set_status(msg):
                    self._ui_status(msg)

                def set_progress(value):
                    self._ui_progress(value)
                
                def get_dur_audio_simples(p):
                    try:
                        r = subprocess.run([FFPROBE_EXE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding='utf-8', errors='replace')
                        return float(r.stdout.strip())
                    except: return 0.0

                if modo_ritmo_ui == 'lipsync':
                    if not video_paths_ui:
                        raise Exception("Para o modo Lip Sync, adicione os vídeos base na lista!")
                    set_status("Calculando durações dos vídeos (Lip Sync)...")
                    audio_dur = 0.0
                    blocos = []
                    _temp_audio_lipsync = os.path.join(saida, "temp_lipsync_audio.wav")
                    
                    for v in video_paths_ui:
                        vdur = get_dur_audio_simples(v)
                        if vdur <= 0.1: vdur = 2.0
                        blocos.append({'start': audio_dur, 'end': audio_dur + vdur, 'texto': f"Video: {os.path.basename(v)}", 'override_path': ""})
                        audio_dur += vdur
                    
                    perfis_lista = []
                    import re
                    for line in roteiro.split('['):
                        if not line.strip(): continue
                        parts = line.split(']', 1)
                        if len(parts) == 2:
                            pstr = parts[0].strip().split('|')[0].strip()
                            pstr = re.sub(r'^(T|TEMPLATE|PERFIL)\s*:\s*', '', pstr, flags=re.IGNORECASE).strip()
                            perfis_lista.append(pstr if pstr else "SEM_PERFIL")
                    
                    for i, b in enumerate(blocos):
                        if i < len(perfis_lista):
                            b['perfil'] = perfis_lista[i]
                        else:
                            b['perfil'] = perfis_lista[-1] if perfis_lista else "SEM_PERFIL"

                    set_status("Extraindo áudio unificado dos vídeos...")
                    list_path = os.path.join(saida, "concat_audio.txt")
                    try:
                        with open(list_path, 'w', encoding='utf-8') as lf:
                            for v in video_paths_ui:
                                lf.write(f"file '{os.path.abspath(v).replace(chr(92), '/')}'\n")
                        subprocess.run([FFMPEG_EXE, '-y', '-f', 'concat', '-safe', '0', '-i', list_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', _temp_audio_lipsync], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        audio = _temp_audio_lipsync
                    except Exception as e:
                        self.log(f"[Lip Sync] Erro ao extrair áudio: {e}")
                        audio = ""
                        if var_legenda_ui:
                            raise Exception("Erro ao extrair áudio para a legenda no Modo Lip Sync.")
                else:
                    audio_dur = get_dur_audio_simples(audio)
                    if audio_dur <= 0:
                        raise Exception("Não foi possível ler a duração do áudio principal. Verifique se o arquivo está íntegro.")
                    
                    if usar_mapeamento_ui:
                        set_status("Analisando roteiro...")
                        for line in roteiro.split('['):
                            if not line.strip(): continue
                            parts = line.split(']', 1)
                            if len(parts) == 2:
                                perfil_str = parts[0].strip()
                                texto = parts[1].strip()
                                
                                perfil_str_limpo = perfil_str.split('|')[0].strip() if '|' in perfil_str else perfil_str
                                import re
                                perfil_str_limpo = re.sub(r'^(T|TEMPLATE|PERFIL)\s*:\s*', '', perfil_str_limpo, flags=re.IGNORECASE).strip()
                                
                                override_path = ""
                                
                                if '|' in perfil_str:
                                    candidatos = [x.strip() for x in perfil_str.split('|')]
                                    caminhos = [c for c in candidatos if os.sep in c or '/' in c or '\\' in c]
                                    perfis = [c for c in candidatos if c not in caminhos]
                                    if perfis:
                                        perfil_str_limpo = re.sub(r'^(T|TEMPLATE|PERFIL)\s*:\s*', '', random.choice(perfis), flags=re.IGNORECASE).strip()
                                    else:
                                        perfil_str_limpo = re.sub(r'^(T|TEMPLATE|PERFIL)\s*:\s*', '', candidatos[0], flags=re.IGNORECASE).strip()
                                    if caminhos: override_path = caminhos[0].strip('"').strip("'")
                                
                                perfil = perfil_str_limpo
                                if not perfil: perfil = "SEM_PERFIL"
                                if texto:
                                    blocos.append({'perfil': perfil, 'override_path': override_path, 'texto': texto, 'start': 0.0, 'end': 0.0})

                        if not blocos:
                            raise Exception("Nenhuma tag [perfil] encontrada no roteiro.")
                    else:
                        perfil = perfil_unico_ui
                        if not perfil or perfil == "[Sem Template - Apenas Vídeo Base]": 
                            perfil = "SEM_PERFIL"
                        blocos = [{'perfil': perfil, 'override_path': "", 'texto': "Video completo", 'start': 0.0, 'end': audio_dur}]
                
                whisper_words = []
                
                # 2. Carregar Whisper SE FOR NECESSÁRIO (Mapeamento ON ou Legenda ON)
                precisa_whisper = usar_mapeamento_ui or var_legenda_ui
                
                if precisa_whisper:
                    set_status("Carregando inteligência Whisper...")
                    set_progress(10)

                    # ── SRT EXTERNO: pula o Whisper se um arquivo .srt foi fornecido ─────────
                    _srt_externo = self.srt_externo_path.get().strip()
                    if _srt_externo and os.path.exists(_srt_externo):
                        set_status(f"⚡ Usando SRT externo: {os.path.basename(_srt_externo)}")
                        set_progress(55)
                        whisper_words = _parse_srt_to_whisper_words(_srt_externo)
                        whisper_result = {
                            'segments': [{'words': whisper_words,
                                          'text': ' '.join(w['word'] for w in whisper_words),
                                          'start': whisper_words[0]['start'] if whisper_words else 0.0,
                                          'end':   whisper_words[-1]['end']  if whisper_words else 0.0}]
                        } if whisper_words else {'segments': []}
                        self.log(f"✅ SRT externo carregado: {len(whisper_words)} palavras.")
                    else:
                        # ── WHISPER NORMAL ────────────────────────────────────────────────
                        try:
                            import whisper
                        except ImportError:
                            raise Exception("A biblioteca whisper não está instalada.")
                        import os as _os_w
                        _os_w.environ.setdefault('OMP_NUM_THREADS', str(_os_w.cpu_count() or 4))
                        model = whisper.load_model("base")

                        # 3. Transcrever Áudio com timestamps
                        cache_path = audio + ".whisper_cache.json"
                        if os.path.exists(cache_path):
                            set_status("⚡ Cache Whisper encontrado! Carregando (0 segundos de espera)...")
                            set_progress(55)
                            with open(cache_path, 'r', encoding='utf-8') as f:
                                whisper_result = json.load(f)
                        else:
                            set_status("Ouvindo e mapeando áudio com Whisper (Isso pode levar um minuto)...")
                            set_progress(30)
                            whisper_result = model.transcribe(audio, fp16=False, language='pt', word_timestamps=True)
                            try:
                                with open(cache_path, 'w', encoding='utf-8') as f:
                                    json.dump(whisper_result, f, ensure_ascii=False)
                            except Exception: pass

                        for seg in whisper_result.get('segments', []):
                            for w in seg.get('words', []):
                                whisper_words.append(w)

                        if not whisper_words:
                            raise Exception("O Whisper não conseguiu ouvir nenhuma palavra no áudio.")

                # 4. Alinhamento de Fatias (Se mapeamento ativo e NÃO Lip Sync)
                if usar_mapeamento_ui and modo_ritmo_ui != 'lipsync':
                    set_status("Alinhando timestamps dos blocos...")
                    
                    w_idx = 0
                    for b in blocos:
                        # Remove prefixos como "Cena 1 -", "1:", "01 -", "1.", etc.
                        texto_limpo = re.sub(r'^(Cena\s*\d+\s*[-:.]|\d+\s*[-:.])\s*', '', b['texto'], flags=re.IGNORECASE)
                        b_words = [re.sub(r'[^\w]', '', tok.lower()) for tok in texto_limpo.split() if re.sub(r'[^\w]', '', tok.lower())]
                        if not b_words: continue
                        
                        if w_idx >= len(whisper_words): break
                            
                        start_time = whisper_words[w_idx]['start']
                        end_idx = min(w_idx + len(b_words) - 1, len(whisper_words) - 1)
                        
                        target_last = b_words[-1]
                        expected_offset = len(b_words) - 1
                        best_offset = None
                        
                        # Busca mais ampla (± 30 palavras) para ignorar prefixos ("Cena 1 -") e falhas de TTS
                        for offset in range(max(0, len(b_words) - 30), len(b_words) + 30):
                            test_idx = w_idx + offset
                            if test_idx < len(whisper_words):
                                w_clean = re.sub(r'[^\w]', '', whisper_words[test_idx]['word'].lower())
                                if w_clean == target_last:
                                    # Pega o match mais próximo do tamanho esperado do bloco
                                    if best_offset is None or abs(offset - expected_offset) < abs(best_offset - expected_offset):
                                        best_offset = offset
                        
                        if best_offset is not None:
                            end_idx = w_idx + best_offset
                        
                        end_time = whisper_words[end_idx]['end']
                        b['start'] = start_time
                        b['end'] = end_time
                        w_idx = end_idx + 1

                    if len(blocos) > 0:
                        for i in range(len(blocos) - 1):
                            blocos[i]['end'] = blocos[i+1]['start']
                        blocos[-1]['end'] = max(blocos[-1]['end'], audio_dur)

                # Lógica IA removida do mapeador automático

                # 5. Salvar o Plano de Batalha (JSON)
                set_status("Salvando plano de voo...")
                set_progress(90)
                
                plano = {
                    'audio_path': audio,
                    'saida_dir': saida,
                    'usar_estetica_hd': usar_transicoes_hd_ui,
                    'usar_estetica_overlay': usar_particulas_hd_ui,
                    'usar_estetica_ffmpeg': usar_transicoes_ffmpeg_ui,
                    'blocos': blocos
                }
                
                os.makedirs(saida, exist_ok=True)
                plan_file = os.path.join(saida, "plano_mapeamento.json")
                with open(plan_file, 'w', encoding='utf-8') as f:
                    json.dump(plano, f, indent=4, ensure_ascii=False)
                
                set_status(f"Plano salvo em {plan_file}. Iniciando Motor de Renderização...")
                
                # --- PRÉ-PROCESSAMENTO: VÍDEOS BASE DA LISTA ---
                video_only_concat = ""
                temp_dir = os.path.join(saida, "temp_render")
                os.makedirs(temp_dir, exist_ok=True)
                
                roteiro_base = roteiro_base_ui
                original_video_paths = list(video_paths_ui)
                video_paths_to_use = list(video_paths_ui)
                


                if video_paths_to_use:
                    set_status("Gerando Vídeo Base Contínuo (Motor Elástico de Mapeamento)...")
                    set_progress(92)
                    temp_dir = os.path.join(saida, "temp_render")
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # 1. Determinar Blocos de Áudio para o Vídeo Base
                    blocos_base = []
                    
                    if usar_roteiro_base_ui and roteiro_base_ui:
                        linhas = [l.strip() for l in roteiro_base_ui.splitlines() if l.strip()]
                        w_idx = 0
                        for i, linha in enumerate(linhas):
                            # Remove prefixos como "Cena 1 -", "1:", "01 -", "1.", etc.
                            linha_limpa = re.sub(r'^(Cena\s*\d+\s*[-:.]|\d+\s*[-:.])\s*', '', linha, flags=re.IGNORECASE)
                            b_words = [re.sub(r'[^\w]', '', tok.lower()) for tok in linha_limpa.split() if re.sub(r'[^\w]', '', tok.lower())]
                            if not b_words: continue
                            if w_idx >= len(whisper_words): break
                                
                            start_time = whisper_words[w_idx]['start']
                            end_idx = min(w_idx + len(b_words) - 1, len(whisper_words) - 1)
                            
                            target_last = b_words[-1]
                            expected_offset = len(b_words) - 1
                            best_offset = None
                            
                            for offset in range(max(0, len(b_words) - 30), len(b_words) + 30):
                                test_idx = w_idx + offset
                                if test_idx < len(whisper_words):
                                    w_clean = re.sub(r'[^\w]', '', whisper_words[test_idx]['word'].lower())
                                    if w_clean == target_last:
                                        if best_offset is None or abs(offset - expected_offset) < abs(best_offset - expected_offset):
                                            best_offset = offset
                            
                            if best_offset is not None:
                                end_idx = w_idx + best_offset
                            
                            end_time = whisper_words[end_idx]['end']
                            blocos_base.append({'texto': linha, 'start': start_time, 'end': end_time})
                            w_idx = end_idx + 1
                            
                        if blocos_base:
                            for i in range(len(blocos_base) - 1):
                                blocos_base[i]['end'] = blocos_base[i+1]['start']
                            blocos_base[-1]['end'] = max(blocos_base[-1]['end'], audio_dur)
                    else:
                        mult = base_loop_count_ui + 1
                        if mult < 1: mult = 1
                        total_slots = len(video_paths_to_use) * mult
                        slot_dur = audio_dur / max(1, total_slots)
                        curr_time = 0.0
                        for i in range(total_slots):
                            blocos_base.append({'texto': f'Slot {i+1}', 'start': curr_time, 'end': min(audio_dur, curr_time + slot_dur)})
                            curr_time += slot_dur
                            
                    if not blocos_base:
                        blocos_base.append({'texto': 'Fallback', 'start': 0.0, 'end': audio_dur})
                    
                    # Lógica de propagação da IA removida
                        
                    if profile_data:
                        xfade_sels_raw = [p_xfade]
                        tdur = p_dur
                    else:
                        xfade_sels_raw = estetica_cfg.get("xfade_selecionadas", ["fade", "slideleft", "slideright", "wipeleft", "wiperight", "fadeblack", "smoothleft", "smoothright"])
                        tdur = float(estetica_cfg.get("var_transicao_dur", 2.0) or 2.0)
                        
                    xfade_sels = [normalize_xfade_name(x) for x in xfade_sels_raw]
                    if not xfade_sels: xfade_sels = ["fade"]
                    trans_bag = list(xfade_sels)
                    random.shuffle(trans_bag)
                    
                    if not usar_transicoes_ffmpeg_ui or len(blocos_base) <= 1:
                        tdur = 0.0
                        
                    prob_transicao = prob_transicao_ui
                    
                    def _safe_float(v, default):
                        try:
                            if isinstance(v, str): v = v.replace(',', '.')
                            return float(v)
                        except: return float(default)

                    var_glitch = estetica_cfg.get("var_glitch", False) and m_cam
                    var_vhs = estetica_cfg.get("var_vhs", False) and m_cam
                    var_vignette = estetica_cfg.get("var_vignette", False) and m_cam
                    var_noise = estetica_cfg.get("var_noise", False) and m_cam
                    
                    # Redução de ~17% na intensidade padrão dos efeitos de câmera para movimento mais suave
                    var_zoom_amp   = _safe_float(estetica_cfg.get("var_zoom_amp",   0.083), 0.083)
                    var_pan_speed  = _safe_float(estetica_cfg.get("var_pan_speed",  0.042), 0.042)
                    var_tilt_speed = _safe_float(estetica_cfg.get("var_tilt_speed", 0.042), 0.042)
                    var_shake_int  = _safe_float(estetica_cfg.get("var_shake_int",  2.5), 2.5)
                    _int_mult      = {"leve": 0.5, "medio": 1.0, "intenso": 1.8}.get(str(estetica_cfg.get("var_intensidade", "medio")).lower(), 1.0)
                    
                    # [E21] IA tem precedencia: se IA ativa, Ken Burns ignora o switch manual m_cam
                    var_kenburns   = estetica_cfg.get("var_kenburns",   False)
                    if not m_cam:
                        # Se m_cam off, so ativa Ken Burns se for via IA (decidido bloco a bloco)
                        # Entao aqui deixamos como False para o aleatorio, mas permitimos no loop individual
                        var_kenburns = False
                    
                    var_kenburns_int = _safe_float(estetica_cfg.get("var_kenburns_int", 0.125), 0.125)
                    
                    var_sat = _safe_float(estetica_cfg.get("var_sat", 1.0), 1.0) if m_cor else 1.0
                    var_cont = _safe_float(estetica_cfg.get("var_cont", 1.0), 1.0) if m_cor else 1.0
                    var_bri = _safe_float(estetica_cfg.get("var_bri", 0.0), 0.0) if m_cor else 0.0
                    
                    lut_files_sel = estetica_cfg.get("lut_files_sel", [])
                    lut_paths = [f for f in lut_files_sel if os.path.exists(f)]
                    
                    if not lut_paths and m_lut and usar_filtros_luz_ui:
                        lut_dirs = estetica_cfg.get("lut_dirs", [])
                        lut_sel = estetica_cfg.get("lut_sel", [])
                        for idx in lut_sel:
                            if idx < len(lut_dirs):
                                d = lut_dirs[idx]
                                if os.path.exists(d):
                                    lut_paths.extend([os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith('.cube')])
                                    
                    global_lut_escaped = ""
                    if m_lut and lut_paths:
                        _lut_raw = random.choice(lut_paths)
                        global_lut_escaped = _lut_raw.replace('\\', '/').replace(':', '\\:').replace("'", "'\\''")
                        
                    self.active_transition_points_hd = []
                    fc_lines = []
                    inputs = []
                    video_format_base = video_format_ui
                    _w = 1920 if video_format_base == 'horizontal' else 1080
                    _h = 1080 if video_format_base == 'horizontal' else 1920
                    
                    usar_ab = self.usar_audio_base.get()
                    v_base_vol = self.vol_audio_base.get()
                    if usar_ab:
                        anull_idx = len(blocos_base)
                    sc_pad = f"format=yuv420p,scale={_w}:{_h}:force_original_aspect_ratio=increase,crop={_w}:{_h},fps=30"
                    

                    for i, b in enumerate(blocos_base):
                        # Se a IA designou um B-Roll especifico, ele tem precedencia absoluta sobre o loop de videos base
                        v_path = video_paths_to_use[i % len(video_paths_to_use)]
                        if b.get('broll_path') and os.path.exists(b['broll_path']):
                            v_path = b['broll_path']
                            print(f"[IA-BROLL] Motor Elastico injetando B-Roll: {os.path.basename(v_path)} na cena {i}", flush=True)

                        b['path'] = v_path
                        b['is_image'] = v_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
                        
                        dur_audio = max(0.1, b['end'] - b['start'])
                        dur_render = dur_audio + tdur if i < len(blocos_base) - 1 else dur_audio
                        b['dur_render'] = dur_render
                        
                        dur_natural = get_dur_audio_simples(v_path) if not b['is_image'] else dur_render
                        if dur_natural <= 0.1: dur_natural = dur_render
                        
                        ia_speed_factor = b.get("speed_factor", 1.0)
                        
                        if ia_speed_factor != 1.0:
                            # Se a IA decidiu acelerar/desacelerar (Etapa 6), sobrescrevemos o fit-to-audio
                            speed_mult = 1.0 / ia_speed_factor
                        else:
                            # Comportamento clássico: esmaga/estica o vídeo levemente para caber no bloco
                            speed_mult = dur_render / dur_natural
                            speed_mult = max(0.25, min(4.0, speed_mult))
                            
                        required_raw_dur = dur_render / speed_mult
                        
                        if b['is_image']:
                            inputs.extend(['-loop', '1', '-t', str(dur_render), '-i', v_path])
                        else:
                            if required_raw_dur > dur_natural:
                                # Precisa de mais vídeo cru do que temos (loop infinito e corta no tempo necessário)
                                inputs.extend(['-stream_loop', '-1', '-t', str(required_raw_dur), '-i', v_path])
                            else:
                                inputs.extend(['-t', str(required_raw_dur), '-i', v_path])
                        fx_choices = []
                        if m_cam: # Fase A: Câmera nativa ativa em tudo se Master Cam estiver ligado
                            if orig_zoom:    fx_choices.append("zoom")
                            if orig_pan:     fx_choices.append("pan")
                            if orig_tilt:    fx_choices.append("tilt")
                            if orig_shake:   fx_choices.append("shake")
                            if var_kenburns: fx_choices.append("kenburns")
                        
                        chosen_fx = random.choice(fx_choices) if fx_choices else None
                        
                        # Efeitos de IA de câmera removidos

                        fx_str = ""
                        if chosen_fx == "zoom":
                            amp = 1.0 + var_zoom_amp * 2.0
                            z_spd = (var_zoom_amp * 2.0) / dur_render
                            fx_str = f",zoompan=z='min(1.0+{z_spd:.4f}*time,{amp:.3f})':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={_w}x{_h}"
                        elif chosen_fx == "pan":
                            pan_spd = 0.45 / dur_render
                            fx_str = f",scale=w='iw*1.45':h='ih*1.45',crop=w='iw/1.45':h='ih/1.45':x='(t*{_w}*{pan_spd:.4f})':y='(ih-ih/1.45)/2'"
                        elif chosen_fx == "tilt":
                            tilt_spd = 0.45 / dur_render
                            fx_str = f",scale=w='iw*1.45':h='ih*1.45',crop=w='iw/1.45':h='ih/1.45':x='(iw-iw/1.45)/2':y='(t*{_h}*{tilt_spd:.4f})'"
                        elif chosen_fx == "shake":
                            si = var_shake_int * 1.5 * _int_mult
                            fx_str = f",scale=w='iw*1.15':h='ih*1.15',crop=w='iw/1.15':h='ih/1.15':x='(iw-iw/1.15)/2+{si:.1f}*sin(t*12)':y='(ih-ih/1.15)/2+{si:.1f}*cos(t*18)'"
                        elif chosen_fx == "kenburns":
                            kb_z = 1.0 + var_kenburns_int * _int_mult
                            z_spd = (var_kenburns_int * _int_mult) / dur_render
                            fx_str = f",zoompan=z='if(lte(on,1),1.0,min(1.0+{z_spd:.4f}*time,{kb_z:.3f}))':x='if(lte(on,1),iw/4,x+{z_spd:.4f}*iw)':y='ih/2-(ih/zoom/2)':d=1:s={_w}x{_h}"
                        elif chosen_fx == "kenburns_out":
                            kb_z = 1.0 + var_kenburns_int * _int_mult
                            z_spd = (var_kenburns_int * _int_mult) / dur_render
                            fx_str = f",zoompan=z='max(1.0,{kb_z:.3f}-time*{z_spd:.4f})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={_w}x{_h}"
                        elif chosen_fx == "drift":
                            d_spd = 0.15 / dur_render
                            fx_str = f",scale=w='iw*1.15':h='ih*1.15',crop=w='iw/1.15':h='ih/1.15':x='(t*{_w}*{d_spd:.4f})':y='(t*{_h}*{d_spd:.4f})'"
                        
                        eq_str = ""
                        if m_cor and (var_sat != 1.0 or var_cont != 1.0 or var_bri != 0.0):
                            eq_str = f",eq=saturation={var_sat}:contrast={var_cont}:brightness={var_bri}"
                        if global_lut_escaped:
                            eq_str += f",lut3d=file='{global_lut_escaped}'"
                        fx_str += eq_str
                        
                        if m_cor:
                            if estetica_cfg.get("var_vibrance", False):
                                vib_val = _safe_float(estetica_cfg.get("var_vibrance_val", 0.5), 0.5)
                                # vibrance nao existe no FFmpeg padrao.
                                # Aproximacao: boost de saturacao via eq (vibrance = sat elevada seletivamente)
                                vib_sat = max(0.1, min(3.0, 1.0 + float(vib_val)))
                                fx_str += f",eq=saturation={vib_sat:.2f}"
                            if estetica_cfg.get("var_hue_shift", False):
                                hue_val = _safe_float(estetica_cfg.get("var_hue_val", 0), 0)
                                fx_str += f",hue=h={hue_val}"
                            if estetica_cfg.get("var_colortemp", False):
                                ct_val = int(_safe_float(estetica_cfg.get("var_colortemp_val", 6500), 6500))
                                # colortemperature nao existe no FFmpeg nativo.
                                # Aproximacao: desvia canais via colorchannelmixer baseado na temperatura
                                if ct_val < 5000:  # frio -> mais azul
                                    fx_str += ",colorchannelmixer=rr=0.9:bb=1.1"
                                elif ct_val > 7000:  # quente -> mais vermelho/amarelo
                                    fx_str += ",colorchannelmixer=rr=1.1:gg=1.05:bb=0.9"
                                # entre 5000-7000: neutro, nao aplica
                            if estetica_cfg.get("var_colorbalance", False):
                                cb_r = _safe_float(estetica_cfg.get("var_cb_rs", 0), 0)
                                cb_g = _safe_float(estetica_cfg.get("var_cb_gs", 0), 0)
                                cb_b = _safe_float(estetica_cfg.get("var_cb_bs", 0), 0)
                                fx_str += f",colorbalance=rs={cb_r}:gs={cb_g}:bs={cb_b}"
                            if estetica_cfg.get("var_curves", False):
                                preset = estetica_cfg.get("var_curves_preset", "none")
                                # Presets validos do FFmpeg curves filter (sem negativos para evitar inversões indesejadas)
                                _curves_validos = [
                                    "cross_process", "darker",
                                    "increase_contrast", "lighter", "linear_contrast",
                                    "medium_contrast", "strong_contrast", "vintage"
                                ]
                                # Se invalido, usa um neutro/seguro
                                if preset not in _curves_validos:
                                    preset = "vintage"
                                fx_str += f",curves=preset={preset}"
                                    
                        if var_vhs: fx_str += ',eq=saturation=1.5,hue=s=1.2' 
                        if var_vignette: fx_str += ',vignette=angle=PI/4'
                        if var_noise: fx_str += ',noise=alls=10:allf=t'
                        if var_glitch: fx_str += ',rgbashift=rh=-5:rv=0:bh=5:bv=0'
                        
                        if m_cam:
                            if estetica_cfg.get("var_filmgrain", False):
                                fx_str += f",noise=c0s=12:c0f=u+t:c1s=6:c1f=u:c2s=6:c2f=u"
                            if estetica_cfg.get("var_tiltshift", False):
                                # tiltandshift com parametros corretos (FFmpeg 8.0)
                                fx_str += ",tiltandshift"
                            if estetica_cfg.get("var_gblur", False):
                                sigma = _safe_float(estetica_cfg.get("var_gblur_sigma", 1.5), 1.5)
                                fx_str += f",gblur=sigma={sigma}"
                            if estetica_cfg.get("var_sharpen", False):
                                fx_str += f",unsharp=5:5:1.5:5:5:0.0"
                            if estetica_cfg.get("var_lagfun", False):
                                fx_str += f",lagfun=decay=0.95"
                            if estetica_cfg.get("var_monochrome", False):
                                fx_str += f",hue=s=0"

                        if b['is_image']:
                            elast_str = f"setpts=PTS-STARTPTS,trim=0:{dur_render:.3f}"
                            audio_speed = 1.0
                        else:
                            elast_str = f"setpts=(PTS-STARTPTS)*{speed_mult:.6f},trim=0:{dur_render:.3f}"
                            audio_speed = 1.0 / max(0.001, speed_mult)
                            
                        _fx_label = chosen_fx if chosen_fx else "nenhum"
                        print(f"[MOTOR-BASE] Clip {i}: cam_fx={_fx_label} | lut={'sim' if global_lut_escaped else 'nao'} | eq={'sim' if eq_str else 'nao'}", flush=True)
                        fc_lines.append(f"[{i}:v]{sc_pad}{fx_str},{elast_str},fps=30[v{i}];")
                        
                        if usar_ab:
                            has_aud = not b['is_image'] and check_has_audio(v_path)
                            if has_aud:
                                atempos = get_atempo_chain(audio_speed)
                                fc_lines.append(f"[{i}:a]{atempos},atrim=0:{dur_render:.3f},asetpts=PTS-STARTPTS[a{i}];")
                            else:
                                fc_lines.append(f"[{anull_idx}:a]atrim=0:{dur_render:.3f},asetpts=PTS-STARTPTS[a{i}];")

                    if usar_ab:
                        inputs.extend(['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo'])

                    if len(blocos_base) > 1:
                        if usar_transicoes_ffmpeg_ui:
                            curr_v = "v0"
                            curr_len = blocos_base[0]['dur_render']  # OTM: usa duração real, não clip_dur fixo
                            if usar_ab: curr_a = "a0"
                            for i in range(1, len(blocos_base)):
                                next_v = f"v{i}"
                                out_v = f"xf{i}" if i < len(blocos_base)-1 else "vout_raw"
                                if usar_ab:
                                    next_a = f"a{i}"
                                    out_a = f"xa{i}" if i < len(blocos_base)-1 else "aout_raw"
                                
                                offset = max(0.0, curr_len - tdur)  # OTM: O(1) usando curr_len acumulado
                                
                                vencedor = "nenhum"
                                if random.randint(1, 100) <= prob_transicao:
                                    opcoes = []
                                    if usar_transicoes_ffmpeg_ui and xfade_sels: opcoes.append("xfade")
                                    if usar_transicoes_hd_ui: opcoes.append("hd")
                                    if opcoes: vencedor = random.choice(opcoes)

                                if vencedor == "hd":
                                    self.active_transition_points_hd.append(offset)
                                    trans = "fade"
                                elif vencedor == "xfade":
                                    if not trans_bag:
                                        trans_bag = list(xfade_sels)
                                        random.shuffle(trans_bag)
                                    trans = trans_bag.pop()
                                else:
                                    trans = "fade"
                                
                                fc_lines.append(f"[{curr_v}][{next_v}]xfade=transition={trans}:duration={tdur:.3f}:offset={offset:.3f}[{out_v}];")
                                curr_v = out_v
                                curr_len = offset + blocos_base[i]['dur_render']  # avança cursor com duração real
                                
                                if usar_ab:
                                    fc_lines.append(f"[{curr_a}][{next_a}]acrossfade=d={tdur:.3f}[{out_a}];")
                                    curr_a = out_a
                        else:
                            curr_len = 0.0
                            for i in range(len(blocos_base) - 1):
                                curr_len += blocos_base[i]['dur_render']
                                if usar_transicoes_hd_ui and random.randint(1, 100) <= prob_transicao:
                                    self.active_transition_points_hd.append(curr_len)
                                
                            if usar_ab:
                                concat_ins = "".join([f"[v{i}][a{i}]" for i in range(len(blocos_base))])
                                fc_lines.append(f"{concat_ins}concat=n={len(blocos_base)}:v=1:a=1[vout_raw][aout_raw];")
                            else:
                                concat_ins = "".join([f"[v{i}]" for i in range(len(blocos_base))])
                                fc_lines.append(f"{concat_ins}concat=n={len(blocos_base)}:v=1:a=0[vout_raw];")
                    else:
                        fc_lines.append(f"[v0]copy[vout_raw];")
                        if usar_ab:
                            fc_lines.append(f"[a0]acopy[aout_raw];")
                        
                    fc_lines.append(f"[vout_raw]trim=0:{audio_dur:.3f},setpts=PTS-STARTPTS[vout]")
                    if usar_ab:
                        fc_lines.append(f"[aout_raw]atrim=0:{audio_dur:.3f},asetpts=PTS-STARTPTS[aout]")

                    script_path = os.path.join(temp_dir, "base_filter.txt")
                    with open(script_path, "w", encoding="utf-8") as f:
                        # BUG FIX: normaliza ';' sobrante de cada linha e separa filterchains
                        # com ';\n' — obrigatorio no FFmpeg filter_complex. Sem isso,
                        # [vout] e [aout] ficam na mesma filterchain causando
                        # "Trailing garbage" / "Invalid argument".
                        clean = [l.rstrip().rstrip(';') for l in fc_lines if l.strip()]
                        f.write(";\n".join(clean) + "\n")
                    
                    video_only_concat = os.path.join(temp_dir, "master_bruto_fundo_base.mp4")
                    cmd_base = [FFMPEG_EXE, '-y', '-threads', '0', '-threads', '0'] + inputs + ['-filter_complex_script', script_path, '-map', '[vout]']
                    if usar_ab:
                        cmd_base.extend(['-map', '[aout]', '-c:a', 'aac', '-b:a', '192k'])
                    cmd_base.extend(_vc_base + [video_only_concat])
                    run_cmd_checked(cmd_base, "Renderização Completa do Vídeo Base (Motor Elástico)")
                    
                    set_status("Vídeo Base Contínuo finalizado! Iniciando overlays...")
                    
                    sincronizar_base_local = False
                    aplicar_fx_local = False
                    video_paths_to_use = [video_only_concat]
                
                # 6. Renderização em Lote Paralela (Fase 16)
                base_dir_p = os.path.dirname(os.path.abspath(__file__))
                
                tasks_cmd = []
                _global_probe_cache = {}
                
                def get_dur_global(p):
                    if p not in _global_probe_cache:
                        try:
                            r = subprocess.run([FFPROBE_EXE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding='utf-8', errors='replace')
                            _global_probe_cache[p] = float(r.stdout.strip())
                        except: _global_probe_cache[p] = 0.0
                    return _global_probe_cache[p]
                
                # Closure Bug Fix: make_add_layer definida ANTES do for loop
                def make_add_layer(layers_ctx, video_format_ctx, ffmpeg_cmd_ref, dur_ctx, b_ctx):
                    fc = [""]
                    idx = [0]
                    def _safe_float(v, default):
                        try:
                            return float(v)
                        except (TypeError, ValueError):
                            return float(default)

                    def _safe_int(v, default):
                        try:
                            return int(float(v))
                        except (TypeError, ValueError):
                            return int(default)

                    def _to_even(n, min_value=2):
                        n = int(max(min_value, n))
                        return n if n % 2 == 0 else n + 1

                    def add_layer(layer_id, is_fullscreen=False, default_scale=100, default_x=0, default_y=0):
                        ld = layers_ctx.get(layer_id)
                        if not ld or ld.get('visible') is False: return
                        path = ld.get('path', '')
                        
                        # Aplica Overrides Globais da Aba 3
                        if layer_id == 'lay2_narrador' and lay2_narrador_path_ui: path = lay2_narrador_path_ui
                        if layer_id == 'lay3_frente' and lay3_frente_path_ui: path = lay3_frente_path_ui
                        if layer_id == 'lay4_moldura':
                            moldura_dir = lay4_moldura_dir_ui
                            if moldura_dir and os.path.isdir(moldura_dir):
                                molduras = [os.path.join(moldura_dir, f) for f in os.listdir(moldura_dir) if f.lower().endswith(('.mov', '.mp4', '.webm', '.png'))]
                                if molduras: path = random.choice(molduras)
                        
                        if b_ctx.get('override_path') and layer_id in ['lay0_bg', 'lay1_fundo']:
                            path = b_ctx['override_path']
                        
                        if not path or not os.path.exists(path): return
                        
                        is_img = path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))
                        
                        # Se não for imagem e for base_loop:
                        if is_img:
                            ffmpeg_cmd_ref.extend(['-loop', '1', '-framerate', '30', '-i', path])
                        else:
                            if layer_id == 'lay1_fundo' and base_loop_count_ui != 0:
                                ffmpeg_cmd_ref.extend(['-stream_loop', '-1', '-i', path])
                            else:
                                if ld.get('random'):
                                    vdur = get_dur_global(path)
                                    if vdur > dur_ctx:
                                        st = random.uniform(0, vdur - dur_ctx)
                                        ffmpeg_cmd_ref.extend(['-ss', f"{st:.2f}"])
                                else:
                                    vdur = get_dur_global(path)
                                    if vdur > 0:
                                        st = b_ctx.get('start', 0.0) % vdur
                                        ffmpeg_cmd_ref.extend(['-ss', f"{st:.2f}"])
                                ffmpeg_cmd_ref.extend(['-stream_loop', '-1', '-i', path])
                        idx_str = f"{idx[0]}:v"
                        ck = "colorkey=0x00FF00:0.3:0.2," if ld.get('chroma') else ""
                        sc_pad_h = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black"
                        sc_pad_v = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
                        if is_fullscreen:
                            sc_pad = sc_pad_h if video_format_ctx == 'horizontal' else sc_pad_v
                            if idx[0] == 0:
                                fc[0] += f"[{idx_str}]{ck}{sc_pad}[v{idx[0]}]; "
                            else:
                                fc[0] += f"[{idx_str}]{ck}{sc_pad}[lay{idx[0]}]; "
                                fc[0] += f"[v{idx[0]-1}][lay{idx[0]}]overlay=x=0:y=0:shortest=1[v{idx[0]}]; "
                        else:
                            scale_pct = _safe_float(ld.get('scale', default_scale), default_scale)
                            if scale_pct <= 0:
                                scale_pct = float(default_scale)
                            if ld.get('w') is not None and ld.get('h') is not None:
                                w = _to_even(_safe_int(ld.get('w'), 320))
                                h = _to_even(_safe_int(ld.get('h'), 320))
                                sc = f"scale={w}:{h}"
                            else:
                                sc = f"scale=trunc(iw*({scale_pct}/100)/2)*2:trunc(ih*({scale_pct}/100)/2)*2"
                            
                            x = _safe_int(ld.get('x', default_x), default_x)
                            y = _safe_int(ld.get('y', default_y), default_y)
                            if idx[0] == 0:
                                sc_pad = sc_pad_h if video_format_ctx == 'horizontal' else sc_pad_v
                                fc[0] += f"[{idx_str}]{ck}{sc_pad}[v{idx[0]}]; "
                            else:
                                fc[0] += f"[{idx_str}]{ck}{sc}[lay{idx[0]}]; "
                                fc[0] += f"[v{idx[0]-1}][lay{idx[0]}]overlay=x={x}:y={y}:shortest=1[v{idx[0]}]; "
                        idx[0] += 1
                    return add_layer, fc, idx

                # Valor padrão de video_format para evitar NameError caso perfil não seja lido ainda
                video_format = video_format_ui
                
                for i, b in enumerate(blocos):
                    set_status(f"Preparando cena {i+1}/{len(blocos)}...")
                    set_progress(75 + (5 * (i / max(len(blocos), 1))))
                    
                    chunk_audio = os.path.join(saida, f"chunk_{i}.wav")
                    dur = b['end'] - b['start']
                    if b['start'] == 0.0 and b['end'] == 0.0:
                        set_status(f"Aviso: Bloco {i} ('{b['perfil']}') sem timestamp, pulando.")
                        continue
                    if dur < 0.5: dur = 0.5

                    # [ETAPA 16] Corte Automático — bloco marcado pela IA para ser removido
                    if b.get('corte_acao') and b.get('corte_confirmado', True):
                        # Trava de seguranca: Nao permite cortar o bloco se ele for o único ou se a IA mandou cortar todos
                        _total_cortes = sum(1 for bl in blocos if bl.get('corte_acao') and bl.get('corte_confirmado', True))
                        if _total_cortes >= len(blocos):
                            self.log(f"[E16] Bloco {i}: Corte Inteligente IGNORADO (IA tentou deletar todas as cenas do video).")
                        else:
                            motivo = b['corte_acao']
                            self.log(f"[E16] Bloco {i} CORTADO pela IA: '{motivo}' — cena ignorada no render.")
                            continue

                    beep_file = estetica_cfg.get("beep_file", "")
                    sfx_dir = estetica_cfg.get("sfx_dir", "")
                    sfx_file = ""
                    
                    if sfx_dir and os.path.exists(sfx_dir):
                        # SFX ativado apenas por decisao da IA (sfx_trigger/zoom/motion)
                        # NAO deve disparar para todos os blocos aleatoriamente via aplicar_fx_local
                        if b.get('sfx_trigger') or b.get('zoom_trigger') or b.get('motion_trigger'):
                            target_sfx_dir = sfx_dir
                            # [ETAPA 13] Tenta usar a categoria semântica para buscar numa subpasta
                            cat_name = b.get('sfx_category', '')
                            if cat_name:
                                cat_dir = os.path.join(sfx_dir, cat_name)
                                if os.path.exists(cat_dir) and os.path.isdir(cat_dir):
                                    target_sfx_dir = cat_dir

                            sfx_list = [f for f in os.listdir(target_sfx_dir) if f.lower().endswith(('.mp3', '.wav'))]
                            if not sfx_list and target_sfx_dir != sfx_dir:
                                # Fallback para diretório raiz se a subpasta estiver vazia
                                sfx_list = [f for f in os.listdir(sfx_dir) if f.lower().endswith(('.mp3', '.wav'))]
                                target_sfx_dir = sfx_dir

                            if sfx_list:
                                import random
                                sfx_file = os.path.join(target_sfx_dir, random.choice(sfx_list))
                                
                    if b.get('is_censored') and beep_file and os.path.exists(beep_file):
                        # FASE 2: Injeção de Censura Automática
                        run_cmd_checked(
                            [FFMPEG_EXE, '-y', '-threads', '0', '-ss', str(b['start']), '-t', str(dur), '-i', audio, '-i', beep_file, 
                             '-filter_complex', '[0:a]volume=0[a_mut];[1:a]volume=1.0[a_beep];[a_mut][a_beep]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_out]', 
                             '-map', '[a_out]', '-c:a', 'pcm_s16le', chunk_audio],
                            f"Extração do chunk CENSURADO da cena {i+1}"
                        )
                    elif sfx_file:
                        # FASE 2: Injeção de SFX Sincronizado
                        run_cmd_checked(
                            [FFMPEG_EXE, '-y', '-threads', '0', '-ss', str(b['start']), '-t', str(dur), '-i', audio, '-i', sfx_file, 
                             '-filter_complex', '[0:a]volume=1.0[a_voz];[1:a]volume=0.6[a_sfx];[a_voz][a_sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_out]', 
                             '-map', '[a_out]', '-c:a', 'pcm_s16le', chunk_audio],
                            f"Extração do chunk COM SFX da cena {i+1}"
                        )
                    else:
                        run_cmd_checked(
                            [FFMPEG_EXE, '-y', '-threads', '0', '-ss', str(b['start']), '-t', str(dur), '-i', audio, '-c:a', 'pcm_s16le', chunk_audio],
                            f"Extração do chunk de áudio da cena {i+1}"
                        )

                    perfil_file = os.path.join(base_dir_p, "perfis_templates", f"{b['perfil']}.json")
                    if b['perfil'] != "SEM_PERFIL" and not os.path.exists(perfil_file):
                        print(f"Aviso: Perfil {b['perfil']} não encontrado.")
                        continue

                    if b['perfil'] == "SEM_PERFIL":
                        perfil_data = {}
                        layers = {}
                        video_format_cena = video_format_ui
                    else:
                        with open(perfil_file, 'r', encoding='utf-8') as f:
                            perfil_data = json.load(f)
                        layers = perfil_data.get('layers', {})
                        video_format_cena = perfil_data.get('format', 'vertical')

                    ffmpeg_cmd = [FFMPEG_EXE, '-y', '-threads', '0', '-threads', '0']
                    
                    # 1. Injetar Vídeo Base (Sincronizado ou Concatenado)
                    fc_base = ""
                    input_idx = 0
                    
                    # Constrói o sufixo de efeitos cinematográficos (Dark Fácil Clone)
                    fx_filter = ""
                    _w = 1920 if video_format_cena == 'horizontal' else 1080
                    _h = 1080 if video_format_cena == 'horizontal' else 1920
                    
                    fx_choices = []
                    chosen_fx = None  # BUG FIX: garante que chosen_fx sempre existe
                    if aplicar_fx_local and m_cam: # So faz sorteio aleatorio se o switch Master Cam estiver ON
                        if orig_zoom: fx_choices.append("zoom")
                        if orig_pan: fx_choices.append("pan")
                        if orig_tilt: fx_choices.append("tilt")
                        if orig_shake: fx_choices.append("shake")
                        if var_kenburns: fx_choices.append("kenburns")
                        chosen_fx = random.choice(fx_choices) if fx_choices else None
                    
                    # [E21] Diretor IA não substitui mais a escolha de Câmera da UI (Fase A)
                    # A IA usará apenas efeitos não-destrutivos e overlay visuais
                    ia_camera = "" 
                    ia_fx_valid = ["zoom", "pan", "tilt", "shake", "kenburns", "kenburns_out", "drift"]
                    
                    # [E21] Multiplicador de intensidade
                    _ia_intensity = b.get("camera_fx_intensity", "medio")
                    _int_mult = {"leve": 0.5, "medio": 1.0, "intenso": 1.8}.get(
                        _ia_intensity.lower() if _ia_intensity else "medio", 1.0)
                        
                    if b.get('zoom_trigger') and chosen_fx not in ia_fx_valid:
                        chosen_fx = "punch_in"
                    
                    if chosen_fx == "punch_in":
                        fx_filter += f",scale=w='iw*1.25':h='ih*1.25',crop=w='iw/1.25':h='ih/1.25':x='(iw-ow)/2':y='(ih-oh)/2'"
                    elif chosen_fx == "zoom":
                        amp = 1.0 + var_zoom_amp * 2.0 * _int_mult
                        z_spd = (var_zoom_amp * 2.0 * _int_mult) / dur
                        fx_filter += f",zoompan=z='min(1.0+{z_spd:.4f}*time,{amp:.3f})':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={_w}x{_h}"
                    elif chosen_fx == "pan":
                        pan_spd = 0.45 / dur
                        fx_filter += f",scale=w='iw*1.45':h='ih*1.45',crop=w='iw/1.45':h='ih/1.45':x='(t*{_w}*{pan_spd:.4f})':y='(ih-ih/1.45)/2'"
                    elif chosen_fx == "tilt":
                        tilt_spd = 0.45 / dur
                        fx_filter += f",scale=w='iw*1.45':h='ih*1.45',crop=w='iw/1.45':h='ih/1.45':x='(iw-iw/1.45)/2':y='(t*{_h}*{tilt_spd:.4f})'"
                    elif chosen_fx == "shake":
                        si = var_shake_int * 1.5 * _int_mult
                        fx_filter += f",scale=w='iw*1.15':h='ih*1.15',crop=w='iw/1.15':h='ih/1.15':x='(iw-iw/1.15)/2+{si:.1f}*sin(t*12)':y='(ih-ih/1.15)/2+{si:.1f}*cos(t*18)'"
                    elif chosen_fx == "kenburns":
                        kb_z = 1.0 + var_kenburns_int * _int_mult
                        z_spd = (var_kenburns_int * _int_mult) / dur
                        fx_filter += f",zoompan=z='if(lte(on,1),1.0,min(1.0+{z_spd:.4f}*time,{kb_z:.3f}))':x='if(lte(on,1),iw/4,x+{z_spd:.4f}*iw)':y='ih/2-(ih/zoom/2)':d=1:s={_w}x{_h}"
                    elif chosen_fx == "kenburns_out":
                        kb_z = 1.0 + var_kenburns_int * _int_mult
                        z_spd = (var_kenburns_int * _int_mult) / dur
                        fx_filter += f",zoompan=z='max(1.0,{kb_z:.3f}-time*{z_spd:.4f})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={_w}x{_h}"
                    elif chosen_fx == "drift":
                        d_spd = 0.15 / dur
                        fx_filter += f",scale=w='iw*1.15':h='ih*1.15',crop=w='iw/1.15':h='ih/1.15':x='(t*{_w}*{d_spd:.4f})':y='(t*{_h}*{d_spd:.4f})'"
                        
                    if b.get('motion_trigger'):
                        motion_word = b.get('motion_word', '')
                        if not motion_word: motion_word = b.get('word', 'IMPACTO')
                        motion_word = re.sub(r'[^\w]', '', motion_word).upper() or 'IMPACTO'
                        
                        m_anim = b.get('motion_animation', 'float')
                        # NOTA: SEM ESPACOS nas expressoes — FFmpeg 8.0 quebra com espacos em filter_complex
                        anim_y = "(h-text_h)/2-50*sin(t*5)"  # float default
                        anim_x = "(w-text_w)/2"
                        if m_anim == 'shake':
                            anim_x = "(w-text_w)/2+20*sin(t*15)"
                            anim_y = "(h-text_h)/2+20*cos(t*20)"
                        elif m_anim == 'pop':
                            anim_y = "(h-text_h)/2-100*sin(t*3)"

                        # FASE 3: Motion Design - Palavra flutuante animada
                        _fontfile = "C\\\\:/Windows/Fonts/arialbd.ttf"
                        # Escapa caracteres que quebram o filter_complex do FFmpeg
                        _safe_word = re.sub(r"[:'\\]", '', motion_word)  # remove ', :, \
                        fx_filter += (
                            f",drawtext="
                            f"fontfile={_fontfile}:"
                            f"text={_safe_word}:"
                            f"fontcolor=yellow:"
                            f"fontsize=120:"
                            f"x={anim_x}:"
                            f"y={anim_y}:"
                            f"borderw=5:"
                            f"bordercolor=black"
                        )
                    
                    # [ETAPA 10] Infográficos e contadores automáticos
                    if b.get('infografico_text'):
                        info_txt = b['infografico_text'].replace("'", "\\'").replace(":", "\\:")
                        _fontfile = "C\\\\:/Windows/Fonts/arial.ttf"
                        # Posicionamento baseado no tipo (bottom = barra na parte inferior, center = grande no centro, top = cabeçalho)
                        info_y = "h-text_h-80" if b.get('infografico_type') == "bottom" else ("100" if b.get('infografico_type') == "top" else "(h-text_h)/2")
                        fx_filter += (
                            f",drawtext="
                            f"fontfile={_fontfile}:"
                            f"text='{info_txt}':"
                            f"fontcolor=white:"
                            f"fontsize=60:"
                            f"x=(w-text_w)/2:"
                            f"y={info_y}:"
                            f"box=1:"
                            f"boxcolor=black@0.6:"
                            f"boxborderw=10"
                        )
                    
                    if video_paths_to_use and sincronizar_base_local:
                        v_idx = i % len(video_paths_to_use)
                        v_path = video_paths_to_use[v_idx]
                        
                        # FASE 3: B-Roll Contextual (Substitui o vídeo de fundo pelo vídeo sugerido pela IA)
                        if b.get('broll_path') and os.path.exists(b['broll_path']):
                            v_path = b['broll_path']
                            
                        is_image = v_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
                        
                        if is_image:
                            ffmpeg_cmd.extend(['-loop', '1', '-t', str(dur), '-i', v_path])
                        else:
                            vdur = get_dur_global(v_path)
                            st = random.uniform(0, max(0, vdur - dur))
                            if base_loop_count_ui != 0:
                                ffmpeg_cmd.extend(['-stream_loop', '-1'])
                            ffmpeg_cmd.extend(['-ss', f"{st:.2f}", '-t', str(dur), '-i', v_path])
                        
                        sc_pad_h = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black"
                        sc_pad_v = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
                        sc_pad = sc_pad_h if video_format_cena == 'horizontal' else sc_pad_v
                        
                        fc_base += f"[0:v]{sc_pad}{fx_filter}[v0]; "
                        input_idx = 1
                        
                    elif video_only_concat and os.path.exists(video_only_concat):
                        # Removido stream_loop aqui para evitar que 1 frame residual cause o vídeo base a piscar de volta ao início
                        ffmpeg_cmd.extend(['-ss', str(b['start']), '-i', video_only_concat])
                        sc_pad_h = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black"
                        sc_pad_v = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
                        sc_pad = sc_pad_h if video_format_cena == 'horizontal' else sc_pad_v
                        
                        fc_base += f"[0:v]{sc_pad}{fx_filter}[v0]; "
                        input_idx = 1
                    
                    add_layer_fn, fc_ref, idx_ref = make_add_layer(layers, video_format_cena, ffmpeg_cmd, dur, b)
                    # Sincroniza o idx do closure com o input_idx base
                    idx_ref[0] = input_idx
                    fc_ref[0] = fc_base

                    add_layer_fn('lay0_bg', is_fullscreen=True)
                    add_layer_fn('lay1_fundo', default_scale=100)
                    add_layer_fn('lay2_narrador', default_scale=30, default_x=50, default_y=1500)
                    add_layer_fn('lay3_frente', default_scale=30, default_x=50, default_y=1500)
                    add_layer_fn('lay4_moldura', is_fullscreen=True)
                    add_layer_fn('lay4_extra', default_scale=50, default_x=50, default_y=50)
                    add_layer_fn('lay5_extra', default_scale=50, default_x=50, default_y=50)
                    
                    # Processar camadas extras infinitas
                    for key in sorted(layers.keys()):
                        if key.startswith('lay_extra_'):
                            add_layer_fn(key, default_scale=50, default_x=50, default_y=50)

                    filter_complex = fc_ref[0]
                    input_idx = idx_ref[0]

                    if input_idx == 0:
                        if video_format_cena == 'horizontal':
                            ffmpeg_cmd.extend(['-f', 'lavfi', '-i', f'color=c=black:s=1920x1080:d={dur}'])
                        else:
                            ffmpeg_cmd.extend(['-f', 'lavfi', '-i', f'color=c=black:s=1080x1920:d={dur}'])
                        filter_complex += "[0:v]copy[v0]; "
                        input_idx = 1

                    ffmpeg_cmd.extend(['-i', chunk_audio])
                    audio_idx = input_idx

                    out_vid = os.path.join(saida, f"cena_{i:03d}_{b['perfil']}.mov")
                    fc_clean = filter_complex.rstrip().rstrip(';').rstrip()

                    if usar_ab:
                        amix_str = f"[0:a]volume={v_base_vol}dB[a_base]; [a_base][{audio_idx}:a]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_mix]"
                        if fc_clean:
                            fc_clean += "; " + amix_str
                        else:
                            fc_clean = amix_str
                        audio_map = "[a_mix]"
                    else:
                        audio_map = f"{audio_idx}:a"

                    if fc_clean:
                        ffmpeg_cmd.extend(['-filter_complex', fc_clean])

                    ffmpeg_cmd.extend([
                        '-map', f"[v{input_idx-1}]", '-map', audio_map,
                        *_vc_high,
                        '-c:a', 'pcm_s16le', '-r', '30', '-t', str(dur), out_vid
                    ])

                    tasks_cmd.append((i, b['perfil'], ffmpeg_cmd, out_vid, b))

                # Executando Motor NVENC/Paralelo
                set_status(f"Motor disparado! Renderizando {len(tasks_cmd)} cenas simultaneamente...")
                total_cenas = len(tasks_cmd)
                concluidas = 0
                _t_inicio_render = __import__('time').time()
                
                _render_lock = __import__('threading').Lock()
                
                def render_task(t_data):
                    idx, perfil, cmd, ov, bk = t_data
                    if self.cancelar_flag: return idx
                    run_cmd_checked(cmd, f"Render da cena {idx+1} ({perfil})")
                    with _render_lock:  # OTM: race condition - escrita segura em dict compartilhado
                        bk['out_vid'] = ov
                    return idx
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=_max_workers) as executor:
                    futures = [executor.submit(render_task, t) for t in tasks_cmd]
                    for future in concurrent.futures.as_completed(futures):
                        if self.cancelar_flag: break
                        future.result()  # propaga exceção se houver
                        concluidas += 1
                        pct = 80 + (15 * (concluidas / max(total_cenas, 1)))
                        set_progress(pct)
                        # ETA: estima tempo restante com base na vazão atual
                        _elapsed = __import__('time').time() - _t_inicio_render
                        _taxa = concluidas / max(_elapsed, 0.1)
                        _restantes = total_cenas - concluidas
                        _eta_s = int(_restantes / max(_taxa, 0.01))
                        _eta_str = f"{_eta_s//60}m{_eta_s%60:02d}s" if _eta_s >= 60 else f"{_eta_s}s"
                        set_status(f"Cenas: {concluidas}/{total_cenas} | ETA ~{_eta_str} | {_max_workers} núcleos ativos")
                        
                if self.cancelar_flag:
                    set_status("Processo abortado pelo usuário.")
                    self._ui_call(self.btn_iniciar.config, state='normal')
                    self._ui_call(self.btn_cancelar.config, state='disabled')
                    return
                
                rendered_count = sum(1 for b in blocos if 'out_vid' in b and os.path.exists(b['out_vid']))
                if rendered_count == 0:
                    raise Exception("Nenhuma cena válida foi renderizada. Verifique perfis, roteiro e mídias de entrada.")
                
                
                # 7. Concatenador e Transições (Fase 14)
                set_status("Juntando as cenas no Master Bruto...")
                set_progress(95)
                
                list_txt = os.path.join(saida, "list_cenas.txt")
                with open(list_txt, 'w', encoding='utf-8') as f:
                    for b in blocos:
                        if 'out_vid' in b:
                            # Bug #3: Caminho entre aspas simples para suportar espaços
                            p_abs = os.path.abspath(b['out_vid']).replace('\\', '/').replace("'", "'\\''")
                            f.write(f"file '{p_abs}'\n")
                            
                master_bruto = os.path.join(saida, "MASTER_BRUTO.mp4")
                
                _cm = getattr(self, 'config_manager', None)
                estetica = _cm.get("estetica_canal", {}) if _cm else {}
                
                if profile_data:
                    xfade_selecionadas = [p_xfade]
                    xfade_duracoes = {p_xfade: p_dur}
                else:
                    xfade_selecionadas = estetica.get("xfade_selecionadas", ["fade", "slideleft", "slideright", "wipeleft", "wiperight", "fadeblack", "smoothleft", "smoothright"])
                    xfade_duracoes = estetica.get("xfade_duracoes", {"fade": 0.5})
                
                valid_blocks = [b for b in blocos if 'out_vid' in b]
                
                if (usar_transicoes_ffmpeg_ui and xfade_selecionadas or usar_transicoes_hd_ui) and len(valid_blocks) > 1:
                    set_status("Aplicando XFade nas transições de blocos...")
                    cmd_xfade = [FFMPEG_EXE, '-y', '-threads', '0', '-threads', '0']
                    for b in valid_blocks:
                        cmd_xfade.extend(['-i', b['out_vid']])
                        
                    fc_lines = []
                    curr_v = "[0:v]"
                    curr_a = "[0:a]"
                    curr_len = get_dur_global(valid_blocks[0]['out_vid'])
                    
                    for i in range(1, len(valid_blocks)):
                        vencedor = "nenhum"
                        if random.randint(1, 100) <= prob_transicao:
                            opcoes = []
                            if usar_transicoes_ffmpeg_ui and xfade_selecionadas: opcoes.append("xfade")
                            if usar_transicoes_hd_ui: opcoes.append("hd")
                            if opcoes: vencedor = random.choice(opcoes)

                        if vencedor == "xfade":
                            xf = xfade_selecionadas[(i-1) % len(xfade_selecionadas)]
                            tdur = float(xfade_duracoes.get(xf, 2.0))
                        else:
                            xf = "fade"
                            tdur = p_dur if profile_data else 2.0
                            
                                
                        clip_dur = get_dur_global(valid_blocks[i]['out_vid'])
                        max_tdur = min(curr_len, clip_dur) - 0.1
                        if max_tdur <= 0: max_tdur = min(curr_len, clip_dur) / 2.0
                        if tdur > max_tdur: tdur = max_tdur
                        
                        offset = curr_len - tdur
                        if vencedor == "hd":
                            self.active_transition_points_hd.append(offset)
                        out_v = f"[v{i}_out]"
                        out_a = f"[a{i}_out]"
                        
                        fc_lines.append(f"{curr_v}[{i}:v]xfade=transition={xf}:duration={tdur:.3f}:offset={offset:.3f}{out_v};")
                        fc_lines.append(f"{curr_a}[{i}:a]acrossfade=d={tdur:.3f}{out_a};")
                        
                        curr_v = out_v
                        curr_a = out_a
                        
                        curr_len = offset + clip_dur
                        
                    fc_lines.append(f"{curr_v}format=yuv420p[vout];")
                    fc_lines.append(f"{curr_a}aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[aout]")
                    
                    import tempfile
                    fd, script_path = tempfile.mkstemp(suffix=".txt", text=True)
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        # BUG FIX: mesmo separador ';\n' do motor base
                        clean = [l.rstrip().rstrip(';') for l in fc_lines if l.strip()]
                        f.write(";\n".join(clean) + "\n")
                        
                    cmd_xfade.extend([
                        '-filter_complex_script', script_path,
                        '-map', '[vout]', '-map', '[aout]',
                        *_vc_base,
                        '-c:a', 'aac', '-b:a', '192k',
                        master_bruto
                    ])
                    run_cmd_checked(cmd_xfade, "XFade Concatenação do MASTER_BRUTO")
                else:
                    curr_time = 0.0
                    for i in range(len(valid_blocks) - 1):
                        curr_time += get_dur_global(valid_blocks[i]['out_vid'])
                        if usar_transicoes_hd_ui and random.randint(1, 100) <= prob_transicao:
                            self.active_transition_points_hd.append(curr_time)
                            
                    run_cmd_checked(
                        [FFMPEG_EXE, '-y', '-threads', '0', '-threads', '0', '-f', 'concat', '-safe', '0', '-i', list_txt, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', master_bruto],
                        "Concatenação final do MASTER_BRUTO"
                    )
                
                final_video = master_bruto
                
                # Acesso seguro ao config_manager (pode não estar disponível)
                _cm = getattr(self, 'config_manager', None)
                estetica = _cm.get("estetica_canal", {}) if _cm else {}
                
                transicoes_files = estetica.get("transicoes_files_sel", [])
                transicoes = [f for f in transicoes_files if os.path.exists(f)]
                t_dirs_all = estetica.get("transicoes_dirs", [])
                t_sel = estetica.get("transicoes_sel", [])
                # BUG FIX: usa 'idx_t' ao inves de 'i' para evitar re-uso da variavel do loop de cenas
                t_dirs = [t_dirs_all[idx_t] for idx_t in t_sel if idx_t < len(t_dirs_all)]
                
                # Se o perfil tiver um video HD de transicao valido, usa apenas ele
                if profile_data and p_hd_video and os.path.exists(p_hd_video):
                    transicoes = [p_hd_video]

                overlays_files = estetica.get("overlay_files_sel", [])
                overlays = [f for f in overlays_files if os.path.exists(f)]
                o_dirs_all = estetica.get("overlay_dirs", [])
                o_sel = estetica.get("overlay_sel", [])
                # BUG FIX: usa 'idx_o' ao inves de 'i'
                o_dirs = [o_dirs_all[idx_o] for idx_o in o_sel if idx_o < len(o_dirs_all)]
                
                self.log(f"[ESTETICA] HD Stingers: {len(transicoes)} arq. selecionados | {len(t_dirs)} pastas ativas")
                self.log(f"[ESTETICA] Overlays/Poeira: {len(overlays)} arq. selecionados | {len(o_dirs)} pastas ativas")
                if not (overlays or o_dirs):
                    self.log("[AVISO] Overlay/Poeira: Nenhum arquivo ou pasta configurado. Vá em Configuracoes > Banco de Particulas e adicione/selecione arquivos.")
                    
                if usar_transicoes_hd_ui and (transicoes or t_dirs) and (len(blocos) > 1 or getattr(self, 'active_transition_points_hd', [])):
                    set_status("Injetando Estética Global (Stingers Multi-Bancos)...")
                    
                    # Busca recursiva blindada em múltiplas pastas (caso nao tenha files_sel direto)
                    if not transicoes:
                        for tdir in t_dirs:
                            if os.path.exists(tdir):
                                for root_d, dirs, files in os.walk(tdir):
                                    for f in files:
                                        if f.lower().endswith(('.mov', '.webm', '.mp4')):
                                            transicoes.append(os.path.join(root_d, f))
                                    
                    if transicoes:
                        ffmpeg_t = [FFMPEG_EXE, '-y', '-threads', '0', '-threads', '0', '-hwaccel', 'auto', '-i', master_bruto]
                        fc_t = ""
                        curr_time = 0.0
                        last_stinger = None
                        
                        # Bug #4: Calcular primeiro_perfil UMA VEZ, fora do loop de stingers
                        _pf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'perfis_templates', f"{blocos[0]['perfil']}.json")
                        primeiro_perfil = None
                        if os.path.exists(_pf_path):
                            with open(_pf_path, 'r', encoding='utf-8') as f_pf:
                                primeiro_perfil = json.load(f_pf)
                        
                        _stinger_input_idx = 1  # OTM: contador real de inputs adicionados (input 0 = master_bruto)
                        
                        trans_pontos = self.active_transition_points_hd
                        
                        # ---- Motor de Stingers Iterativo (igual ao motor de Teste) ----
                        # Luma  → alphamerge com tpad: wipe real por segmentação de timeline
                        # Color → colorkey: remove fundo preto e sobrepõe
                        _cm = getattr(self, 'config_manager', None)
                        estetica_local = _cm.get("estetica_canal", {}) if _cm else {}
                        stinger_types_cfg = estetica_local.get("stinger_types", {})
                        
                        current_video = master_bruto
                        for pass_idx, cut_time in enumerate(trans_pontos):
                            if self.cancelar_flag: break
                            
                            stinger = random.choice(transicoes)
                            if len(transicoes) > 1 and stinger == last_stinger:
                                stinger = random.choice([x for x in transicoes if x != last_stinger])
                            last_stinger = stinger
                            
                            # Detecta modo: Luma ou Color via normpath (ignora diferença de barras)
                            st_file_mode = "color"  # fallback
                            st_norm = os.path.normcase(os.path.normpath(stinger))
                            for k, v in stinger_types_cfg.items():
                                if os.path.normcase(os.path.normpath(k)) == st_norm:
                                    st_file_mode = v
                                    break
                            
                            # Mede duração real do stinger para ajuste de velocidade
                            try:
                                _probe_st = subprocess.run(
                                    [FFPROBE_EXE, '-v', 'error', '-select_streams', 'v:0',
                                     '-show_entries', 'stream=duration',
                                     '-of', 'default=noprint_wrappers=1:nokey=1', stinger],
                                    capture_output=True, text=True, timeout=10,
                                    creationflags=subprocess.CREATE_NO_WINDOW
                                )
                                st_real_dur = float(_probe_st.stdout.strip()) if _probe_st.stdout.strip() not in ('', 'N/A') else 2.0
                            except Exception:
                                st_real_dur = 2.0
                            
                            target_dur = p_dur if profile_data else 2.0
                            speed_factor = round(target_dur / max(0.1, st_real_dur), 4)
                            st_half = target_dur / 2.0
                            st_a_start = max(0.0, round(cut_time - st_half, 4))
                            st_b_end   = round(cut_time + st_half, 4)
                            
                            if primeiro_perfil and primeiro_perfil.get('format') == 'horizontal':
                                sc_st = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
                            else:
                                sc_st = "transpose=1,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
                            
                            pass_out = os.path.join(saida, f"_st_pass_{pass_idx}.mp4")
                            
                            if st_file_mode == "luma":
                                # Wipe real: congela frame A, revela frame B com a máscara Luma
                                fc_pass = (
                                    f"[0:v]trim=start=0:end={st_a_start},setpts=PTS-STARTPTS[before];"
                                    f"[0:v]trim=start={st_a_start}:end={cut_time},setpts=PTS-STARTPTS[clip_a_raw];"
                                    f"[0:v]trim=start={cut_time}:end={st_b_end},setpts=PTS-STARTPTS[clip_b_raw];"
                                    f"[0:v]trim=start={st_b_end},setpts=PTS-STARTPTS[after];"
                                    f"[clip_a_raw]tpad=stop_mode=clone:stop_duration={st_half}[clip_a];"
                                    f"[clip_b_raw]tpad=start_mode=clone:start_duration={st_half}[clip_b];"
                                    f"[1:v]{sc_st},format=yuv420p,colorlevels=rimin=0.4:rimax=0.6:gimin=0.4:gimax=0.6:bimin=0.4:bimax=0.6,setpts=PTS*{speed_factor}[luma_raw];"
                                    f"[clip_b]format=yuva420p[clip_b_alpha];"
                                    f"[clip_b_alpha][luma_raw]alphamerge[b_masked];"
                                    f"[clip_a][b_masked]overlay=format=auto[wipe];"
                                    f"[before][wipe][after]concat=n=3:v=1:a=0[merged];"
                                    f"[merged]format=yuv420p[final_out]"
                                )
                                self.log(f"[STINGER {pass_idx+1}] LUMA alphamerge x{speed_factor}: corte={cut_time:.2f}s")
                            else:
                                # Color: remove fundo preto e faz overlay no segmento
                                fc_pass = (
                                    f"[0:v]trim=start=0:end={st_a_start},setpts=PTS-STARTPTS[before];"
                                    f"[0:v]trim=start={st_a_start}:end={st_b_end},setpts=PTS-STARTPTS[base_seg];"
                                    f"[0:v]trim=start={st_b_end},setpts=PTS-STARTPTS[after];"
                                    f"[1:v]{sc_st},format=yuva420p,setpts=PTS*{speed_factor},colorkey=color=black:similarity=0.03:blend=0.03[st_keyed];"
                                    f"[base_seg][st_keyed]overlay=format=auto[b_masked];"
                                    f"[before][b_masked][after]concat=n=3:v=1:a=0[merged];"
                                    f"[merged]format=yuv420p[final_out]"
                                )
                                self.log(f"[STINGER {pass_idx+1}] COLOR x{speed_factor}: corte={cut_time:.2f}s")
                            
                            cmd_pass = [
                                FFMPEG_EXE, '-y', '-threads', '0',
                                '-i', current_video,
                                '-i', stinger,
                                '-filter_complex', fc_pass,
                                '-map', '[final_out]', '-map', '0:a',
                                *_vc_base,
                                '-c:a', 'copy', pass_out
                            ]
                            run_cmd_checked(cmd_pass, f"Aplicação de transição HD (stinger {pass_idx+1}/{len(trans_pontos)})")
                            if os.path.exists(pass_out):
                                current_video = pass_out
                            else:
                                self.log(f"[AVISO] Stinger {pass_idx+1} falhou, mantendo video anterior.")
                        
                        if current_video != master_bruto and os.path.exists(current_video):
                            out_final = os.path.join(saida, "MASTER_FINAL_COM_TRANSICOES.mp4")
                            import shutil as _st_shutil
                            _st_shutil.copy2(current_video, out_final)
                            final_video = out_final
                        else:
                            self.log("[AVISO] Nenhum stinger foi aplicado com sucesso.")

                
                # Overlay Global (Blend Screen) — controlado pelo toggle OVL e aplica 100% das vezes se existir pasta/arquivo
                if usar_particulas_hd_ui and (overlays or o_dirs):
                    if not overlays:
                        for odir in o_dirs:
                            if os.path.exists(odir):
                                for root_d, dirs, files in os.walk(odir):
                                    for f in files:
                                        if f.lower().endswith(('.mov', '.webm', '.mp4')):
                                            overlays.append(os.path.join(root_d, f))
                                    
                    if overlays:
                        set_status("Aplicando Overlay Global (Blend Screen)...")
                        ov_escolhido = random.choice(overlays)
                        ov_out = os.path.join(saida, "MASTER_OVERLAY_FINAL.mp4")
                        
                        # Correção: Lendo formato do perfil para escala do overlay
                        _pf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'perfis_templates', f"{blocos[0]['perfil']}.json")
                        pf = {}
                        if os.path.exists(_pf_path):
                            with open(_pf_path, 'r', encoding='utf-8') as f_pf:
                                pf = json.load(f_pf)
                        # Ajusta resolução com Transpose se necessário
                        sc_ov = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1" if pf.get('format') == 'horizontal' else "transpose=1,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"

                        # Usa ColorKey de preto no lugar de blend, com o overlay por cima
                        ffmpeg_ov = [
                            FFMPEG_EXE, '-y', '-threads', '0', '-i', final_video,
                            '-stream_loop', '-1', '-i', ov_escolhido,
                            '-filter_complex', f'[1:v]{sc_ov},colorkey=0x000000:0.3:0.2[ov_scaled]; [0:v][ov_scaled]overlay=eof_action=pass[v_out]',
                            '-map', '[v_out]', '-map', '0:a',
                            *_vc_high,
                            '-c:a', 'copy', '-shortest', ov_out
                        ]
                        run_cmd_checked(ffmpeg_ov, "Aplicação de overlay global")
                        final_video = ov_out

                # 8. Mixagem de Áudio Global (Fase 17)
                musica_ui_val = musica_ui
                if musica_ui_val:
                    # Pode ser um ou múltiplos caminhos separados por '|'
                    musicas_raw = musica_ui_val.split("|")
                    musicas = [m for m in musicas_raw if os.path.exists(m)]
                    
                    if musicas:
                        set_status(f"Masterizando Áudio Global ({len(musicas)} músicas em loop)...")
                        v_mus = vol_musica_ui
                        out_mixado = os.path.join(saida, "MASTER_FINAL_COMPLETO.mp4")
                        
                        if len(musicas) == 1:
                            # FASE 2: Ducking Avançado (Sidechain Compress)
                            cmd_mix = [
                                FFMPEG_EXE, '-y', '-threads', '0', '-i', final_video, '-stream_loop', '-1', '-i', musicas[0],
                                '-filter_complex', f"[1:a]volume={v_mus}dB[a_mus_vol];[a_mus_vol][0:a]sidechaincompress=threshold=0.015:ratio=4:attack=5:release=200[a_ducked];[0:a][a_ducked]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_out]",
                                '-map', '0:v', '-map', '[a_out]',
                                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', out_mixado
                            ]
                        else:
                            # Múltiplas músicas: cria txt concat
                            playlist_txt = os.path.join(saida, "playlist_musicas.txt")
                            with open(playlist_txt, 'w', encoding='utf-8') as f:
                                for m in musicas:
                                    m_abs = os.path.abspath(m).replace('\\', '/').replace("'", "'\\''")
                                    f.write(f"file '{m_abs}'\n")
                            
                            cmd_mix = [
                                FFMPEG_EXE, '-y', '-threads', '0', '-i', final_video, '-stream_loop', '-1', '-f', 'concat', '-safe', '0', '-i', playlist_txt,
                                '-filter_complex', f"[0:a]volume=1.0[a_voz];[1:a]volume={v_mus}dB[a_mus];[a_voz][a_mus]amix=inputs=2:duration=shortest:normalize=0[a_out]",
                                '-map', '0:v', '-map', '[a_out]',
                                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', out_mixado
                            ]

                        run_cmd_checked(cmd_mix, "Mixagem de áudio global")
                        final_video = out_mixado
                    
                # 9. Queimar Legendas Karaokê (Fase 18)
                if var_legenda_ui:
                    set_status("Gerando e queimando legendas dinâmicas no Master...")
                    
                    if not KARAOKE_AVAILABLE:
                        raise Exception("A função generate_karaoke_ass não foi encontrada na aba_edicao_basica.py")
                    # Bug #17: whisper_result pode ser None se Whisper nao rodou
                    if not whisper_result or not whisper_result.get('segments'):
                        self.log("[AVISO] Whisper nao gerou resultado — pulando legendas.")
                        var_legenda_ui = False
                        
                    # Detecta formato do primeiro bloco renderizado
                    fmt_karaoke = 'vertical'
                    if blocos:
                        pf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'perfis_templates', f"{blocos[0]['perfil']}.json")
                        if os.path.exists(pf):
                            with open(pf, 'r', encoding='utf-8') as f_pf:
                                fmt_karaoke = json.load(f_pf).get('format', 'vertical')
                    
                    ass_file = os.path.join(saida, "master_legendas.ass")

                    # ─── Carregar Mapa de Temas de Podcast (se disponível) ───────────────
                    _voice_color_map = None
                    _mapa_path_ui = getattr(self, 'mapa_temas_path', None)
                    _mapa_file = _mapa_path_ui.get() if _mapa_path_ui else ''
                    if _mapa_file and os.path.exists(_mapa_file):
                        try:
                            with open(_mapa_file, 'r', encoding='utf-8') as _mf:
                                _mapa_raw = json.load(_mf)
                            _voice_color_map = _mapa_raw
                            self.log(f'[TEMAS] Mapa de vozes carregado: {len(_voice_color_map)} falas mapeadas.')
                        except Exception as _e_mapa:
                            self.log(f'[AVISO] Falha ao carregar mapa de temas: {_e_mapa}')
                    # ────────────────────────────────────────────────────────────────────

                    generate_karaoke_ass(
                        whisper_result, ass_file, 
                        font=sub_font_ui, 
                        size=sub_size_ui, 
                        theme=sub_theme_ui, 
                        colors=sub_colors_ui,
                        pos=sub_pos_ui, 
                        margin_v=sub_margin_v_ui, 
                        words_per_block=sub_words_ui,
                        video_format=fmt_karaoke,
                        effect=sub_effect_ui,
                        voice_color_map=_voice_color_map
                    )
                    
                    out_legendado = os.path.join(saida, "MASTER_FINAL_LEGENDADO.mp4")
                    # BUG FIX: path do ass precisa de barras forward e escape de : e espaços p/ Windows
                    ass_path_ffmpeg = ass_file.replace('\\', '/').replace(':', '\\:')
                    cmd_legenda = [
                        FFMPEG_EXE, '-y', '-threads', '0', '-i', final_video,
                        '-vf', f"ass='{ass_path_ffmpeg}'",
                        *_vc_base,
                        '-c:a', 'copy', out_legendado
                    ]
                    run_cmd_checked(cmd_legenda, "Queima de legendas no vídeo final", cwd=saida)
                    final_video = out_legendado
                    
                # Renomear vídeo final para um nome limpo
                try:
                    dir_name = os.path.basename(os.path.normpath(saida))
                    final_name = f"{dir_name}_RENDER_FINAL.mp4"
                    final_path = os.path.join(saida, final_name)
                    # Bug #16: garantir que arquivo fonte existe antes de renomear
                    if os.path.exists(final_video) and final_video != final_path:
                        if os.path.exists(final_path):
                            try: os.remove(final_path)
                            except Exception as e: print(e)
                        os.rename(final_video, final_path)
                        final_video = final_path
                    elif not os.path.exists(final_video):
                        self.log(f"[AVISO] Arquivo final nao encontrado para renomear: {final_video}")
                    
                    # [PARTE 11] Registra render bem-sucedido no histórico de produção
                    self._registrar_historico(saida, audio, status="sucesso")
                    
                    # [ETAPA 14] Normalizacao LUFS profissional (2 passes)
                    _app_ref2 = getattr(self, '_app_ref', None)
                    if _app_ref2 and hasattr(_app_ref2, 'aba_diretor_ia') and os.path.exists(final_video):
                       try:
                           _ia_cfg_pos = _app_ref2.aba_diretor_ia.get_config()
                           _fazer_lufs  = _ia_cfg_pos.get('lufs_normalizar', False)
                           _target_lufs = _ia_cfg_pos.get('lufs_target', -14)
                           if _fazer_lufs:
                               set_status(f'[E14] Normalizando audio LUFS ({_target_lufs} LUFS)...')
                               self.log(f'[LUFS] Iniciando 2 passes. Alvo: {_target_lufs} LUFS...')
                               import json as _json_lufs
                               _probe = subprocess.run(
                                   [FFMPEG_EXE, '-y', '-threads', '0', '-i', final_video,
                                    '-af', f'loudnorm=I={_target_lufs}:TP=-1.5:LRA=11:print_format=json',
                                    '-f', 'null', '-'],
                                   capture_output=True, text=True, encoding='utf-8', errors='replace',
                                   creationflags=subprocess.CREATE_NO_WINDOW
                               )
                               _lufs_json = {}
                               try:
                                   _stderr = _probe.stderr
                                   _js = _stderr.rfind('{'); _je = _stderr.rfind('}') + 1
                                   if _js >= 0 and _je > _js:
                                       _lufs_json = _json_lufs.loads(_stderr[_js:_je])
                               except Exception:
                                   pass
                               _out_lufs = final_video.replace('.mp4', '_LUFS.mp4')
                               if _lufs_json.get('input_i'):
                                   _af = (
                                       "loudnorm=I=" + str(_target_lufs) + ":TP=-1.5:LRA=11"
                                       ":measured_I=" + _lufs_json['input_i']
                                       + ":measured_LRA=" + _lufs_json.get('input_lra', '11.0')
                                       + ":measured_TP=" + _lufs_json.get('input_tp', '-1.5')
                                       + ":measured_thresh=" + _lufs_json.get('input_thresh', '-14.0')
                                       + ":offset=" + _lufs_json.get('target_offset', '0.0')
                                       + ":linear=true:print_format=none"
                                   )
                                   self.log('[LUFS] Passo 1 OK. Aplicando correcao linear...')
                               else:
                                   _af = 'loudnorm=I=' + str(_target_lufs) + ':TP=-1.5:LRA=11'
                                   self.log('[LUFS] Passe unico (analise sem JSON).')
                               _r = subprocess.run(
                                   [FFMPEG_EXE, '-y', '-threads', '0', '-i', final_video,
                                    '-af', _af, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', _out_lufs],
                                   capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                               )
                               if _r.returncode == 0 and os.path.exists(_out_lufs):
                                   os.replace(_out_lufs, final_video)
                                   self.log('[LUFS] Audio normalizado. OK.')
                               else:
                                   self.log('[LUFS] Falha, audio original mantido.')
                                   if os.path.exists(_out_lufs):
                                       try: os.remove(_out_lufs)
                                       except Exception as e: print(e)
                       except Exception as _elufs:
                           self.log('[LUFS] Erro: ' + str(_elufs))


                except Exception as ex_ren:
                    print("Nao foi possivel renomear o arquivo final:", ex_ren)
                 
                # [ETAPA 17] Thumbnail Inteligente
                try:
                    gerar_thumb = self.config_manager.get("diretor_ia", {}).get("thumb_auto", True)
                    if gerar_thumb and os.path.exists(final_video):
                        set_status('[E17] Gerando thumbnail inteligente...')
                        self.log('[THUMB] Extraindo frames candidatos para thumbnail...')
                        _dur_probe = subprocess.run(
                            [FFPROBE_EXE, '-v', 'error', '-show_entries', 'format=duration',
                             '-of', 'default=noprint_wrappers=1:nokey=1', final_video],
                            capture_output=True, text=True, encoding='utf-8', errors='replace',
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        _dur_total = 30.0
                        try: _dur_total = float(_dur_probe.stdout.strip())
                        except Exception: pass
                        _thumb_dir = os.path.join(saida, '_thumb_candidates')
                        os.makedirs(_thumb_dir, exist_ok=True)
                        _times = [_dur_total * p for p in [0.10, 0.25, 0.40, 0.55, 0.70]]
                        _candidates = []
                        for _ci, _ct in enumerate(_times):
                            _cf = os.path.join(_thumb_dir, 'cand_' + str(_ci) + '.jpg')
                            _re = subprocess.run(
                                [FFMPEG_EXE, '-y', '-threads', '0', '-ss', str(_ct), '-i', final_video,
                                 '-vframes', '1', '-q:v', '2', _cf],
                                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                            )
                            if _re.returncode == 0 and os.path.exists(_cf):
                                _candidates.append((_ci, _cf))
                        
                        duracao_total = time.time() - inicio_geracao
                        set_status(f"Geração concluída em {duracao_total:.0f}s! Arquivo: {final_video}")
                        self.log(f"[SUCESSO] Vídeo gerado: {final_video}")
                        
                        if self.enviar_timeline.get():
                            self._enviar_para_timeline(final_video)
                        
                        self.after(0, lambda: messagebox.showinfo("Concluído", f"✅ Vídeo gerado com sucesso!\n\nSalvo em:\n{final_video}"))
                        self.after(0, self._limpar_interface_pos_geracao)

                        _best_idx = 2  # Fallback mais sensato: frame do meio (40% do video)
                        try:
                            from ai_director_pipeline import AIDirectorPipeline
                            _ia_th = AIDirectorPipeline(self.config_manager)
                            if _ia_th.has_llm() and _candidates:
                                import base64 as _b64th, json as _jth
                                _imgs = []
                                for _, _cf in _candidates:
                                    with open(_cf, 'rb') as _f:
                                        _imgs.append(_b64th.b64encode(_f.read()).decode('utf-8'))
                                
                                # Injeta contexto do canal para ajudar na escolha
                                _ctx_thumb = f"Canal: {_prompt_canal}\nEstrategia: {_prompt_estrategico}"
                                _ptxt = (
                                    "Voce e um diretor de arte especializado em thumbnails de alto engajamento.\n"
                                    "Analise estes " + str(len(_imgs)) + " frames candidatos (numerados de 0 a " + str(len(_imgs)-1) + ") e escolha o que melhor representa o video.\n"
                                    "CONTEXTO DO VIDEO:\n" + _ctx_thumb + "\n\n"
                                    "CRITERIOS DE ESCOLHA:\n"
                                    "- Impacto visual e clareza do assunto\n"
                                    "- Expressao marcante ou momento epico\n"
                                    "- Composicao atraente para clicar\n"
                                    "- Evitar frames escuros, borrados ou sem rosto\n\n"
                                    "Responda APENAS com JSON valido: {\"melhor_frame\": N, \"motivo\": \"...\"}\n"
                                    "Onde N e um numero inteiro de 0 a " + str(len(_imgs)-1)
                                )
                                print(f"[THUMB] Enviando {len(_imgs)} frames para analise do LLM...", flush=True)
                                # Agora usa o roteador central _chamar_llm (E20)
                                _resp = _ia_th._chamar_llm(_ptxt, images_b64=_imgs)
                                if _resp:
                                    _res_limpa = re.sub(r'```(?:json)?\s*|\s*```', '', _resp).strip()
                                    try:
                                        _js_res = _jth.loads(_res_limpa)
                                        _frame_escolhido = int(_js_res.get('melhor_frame', 2))
                                        _motivo = _js_res.get('motivo', 'Sem motivo')
                                        # Valida que o indice e valido
                                        if 0 <= _frame_escolhido < len(_candidates):
                                            _best_idx = _frame_escolhido
                                            self.log('[THUMB] IA escolheu frame #' + str(_best_idx) + ' (tempo: ~' + f"{_times[_best_idx]:.1f}s) como melhor thumbnail.")
                                            self.log('[THUMB] Motivo: ' + _motivo)
                                            print(f"[THUMB] Frame escolhido: #{_best_idx} | Motivo: {_motivo}", flush=True)
                                        else:
                                            self.log(f'[THUMB] Indice {_frame_escolhido} invalido (max={len(_candidates)-1}). Usando frame central.')
                                    except Exception as _jparse:
                                        self.log(f'[THUMB] Erro ao parsear resposta da IA: {_jparse}. Usando frame central.')
                                else:
                                    self.log('[THUMB] LLM nao retornou resposta. Usando frame central.')
                            else:
                                self.log('[THUMB] LLM nao disponivel. Usando frame central (fallback heuristico).')
                        except Exception as _eth:
                            self.log('[THUMB] Erro no LLM Vision: ' + str(_eth) + '. Usando frame central.')
                        if _candidates:
                            _best_idx = max(0, min(_best_idx, len(_candidates) - 1))
                            _dst = os.path.join(saida, 'THUMB.jpg')
                            import shutil as _shu
                            _shu.copy2(_candidates[_best_idx][1], _dst)
                            self.log('[THUMB] Thumbnail salva em: ' + _dst)
                        try:
                            import shutil as _shu2
                            _shu2.rmtree(_thumb_dir, ignore_errors=True)
                        except Exception: pass
                except Exception as _e17:
                    self.log('[THUMB] Erro: ' + str(_e17))

                set_status('Super-producao finalizada!')
                self._ui_info('Sucesso Absoluto', 'Sua super-producao foi concluida!\nO arquivo final e o:\n' + os.path.basename(final_video))
                
            except Exception as e:
                import traceback
                _tb = traceback.format_exc()
                print(f"\n{'='*60}", flush=True)
                print(f"[ERRO FATAL] {e}", flush=True)
                print(_tb, flush=True)
                print(f"{'='*60}\n", flush=True)
                self._ui_call(self.log, f"[ERRO FATAL] {e}")
                self._ui_call(self.log, _tb)
                # Salva no render.log para diagnóstico
                try:
                    with open(getattr(self, '_render_log_path', ''), 'a', encoding='utf-8') as _lf:
                        _lf.write(f"\n[ERRO FATAL]\n{_tb}\n")
                except Exception as e: print(e)
                set_status("Erro no mapeamento.")
                self._ui_error(f"{type(e).__name__}: {e}")
                # [PARTE 11] Registra render com erro no histórico
                self._registrar_historico(saida if 'saida' in dir() else '', audio if 'audio' in dir() else '', status="erro", detalhe=str(e))
            finally:
                # CLEANUP FORÇADO SEMPRE NO FINALLY
                set_status("Limpando lixo digital...")
                import shutil
                if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
                    try: shutil.rmtree(temp_dir)
                    except Exception as e: print(e)
                
                # Limpeza de resíduos na pasta de saída
                if 'saida' in locals() and os.path.exists(saida):
                    final_vid_path = os.path.abspath(final_video) if 'final_video' in locals() and final_video else ""
                    # Nomes de arquivos intermediários que devem ser apagados após a render
                    _lixo_names = {
                        "MASTER_BRUTO.mp4",
                        "MASTER_FINAL_COMPLETO.mp4",
                        "MASTER_FINAL_LEGENDADO.mp4",
                        "MASTER_FINAL_COM_TRANSICOES.mp4",
                        "MASTER_OVERLAY_FINAL.mp4",
                        "master_legendas.ass",
                        "list_cenas.txt",
                        "playlist_musicas.txt",
                        "plano_mapeamento.json",
                        "render.log",
                        "render_IA.log",
                    }
                    for f_name in os.listdir(saida):
                        f_path = os.path.join(saida, f_name)
                        if final_vid_path and os.path.abspath(f_path) == final_vid_path:
                            continue  # preserva o arquivo final
                        # Deleta intermediários pelo nome exato
                        if f_name in _lixo_names:
                            try: os.remove(f_path)
                            except Exception as e: print(e)
                        # Deleta cenas, chunks e passes intermediários de stingers pelo prefixo
                        elif f_name.startswith(("cena_", "chunk_", "_st_pass_")):
                            try: os.remove(f_path)
                            except Exception as e: print(e)

                # Remover cache do Whisper da pasta do áudio
                try:
                    if 'audio' in locals() and audio:
                        audio_cache = audio + ".whisper_cache.json"
                        if os.path.exists(audio_cache):
                            os.remove(audio_cache)
                except Exception as e: print(e)
                
                # Remover thumbnails cacheadas das pastas dos vídeos originais
                try:
                    if 'video_paths_ui' in locals():
                        for v_path in video_paths_ui:
                            try:
                                t_path = os.path.join(os.path.dirname(v_path), "thumb_cache_" + os.path.basename(v_path) + ".jpg")
                                if os.path.exists(t_path):
                                    os.remove(t_path)
                            except Exception as e: print(e)
                except Exception as e: print(e)

                def restore_ui():
                    self.btn_iniciar.configure(state='normal')
                    self.btn_cancelar.configure(state='disabled')
                self.after(0, restore_ui)

        threading.Thread(target=worker, daemon=True).start()
