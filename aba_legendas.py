import customtkinter as ctk
import os
import json
import wave
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from aba_edicao_basica import generate_karaoke_ass, _get_tema_para_tempo, get_temas_disponiveis

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except Exception:
    VOSK_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    pass
except Exception:
    WHISPER_AVAILABLE = False
else:
    WHISPER_AVAILABLE = True

class AbaGeradorLegendas(ctk.CTkFrame):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager

        self.configure()
        ctk.CTkLabel(self, text="📝 Gerador de Legendas", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Variáveis de arquivo
        self.video_path  = tk.StringVar()
        self.srt_path    = tk.StringVar()
        self.output_path = tk.StringVar()
        self.mapa_temas_path = tk.StringVar()   # Mapa de cores do Podcast

        # Transcrição
        self.auto_transcribe      = tk.BooleanVar(value=True)
        self.transcription_engine = tk.StringVar(value='vosk')

        default_model = self._discover_default_vosk_model()
        self.vosk_model_path = tk.StringVar(value=default_model or '')

        # Estilo/legenda — variáveis independentes (não dependem só do perfil)
        self.preset_selecionado = tk.StringVar()
        self.formato_video      = tk.StringVar(value='vertical')
        self.sub_font           = tk.StringVar(value='Bangers')
        self.sub_words          = tk.IntVar(value=5)
        self.sub_pos            = tk.StringVar(value='meio baixo')
        self.sub_theme          = tk.StringVar(value='amarelo vermelho')
        self.sub_size           = tk.IntVar(value=100)
        self.sub_margin_v       = tk.IntVar(value=150)
        self.sub_effect         = tk.StringVar(value='Pulo (Pop)')
        self.sub_border_w       = tk.IntVar(value=3)

        self.status = tk.StringVar(value='Pronto')

        self._build_ui()
        self._carregar_perfis_ui()

    # ── descoberta do modelo Vosk ──────────────────────────────────────────────
    def _discover_default_vosk_model(self):
        target = r"E:/MEUS PROGRAMAS/HISTORIAS DE 7 DIAS CODIGOS/pre_edicao/vosk-model-pt-fb-v0.1.1-20220516_2113"
        if os.path.isdir(target): return target
        candidates = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pre_edicao', 'vosk-model-small-pt-0.3'),
            'vosk-model-small-pt-0.3',
        ]
        for c in candidates:
            if os.path.isdir(c): return c
        return ''

    def _make_temp_dir(self):
        temp_dir = os.path.join(os.getcwd(), 'temp', 'gerador_legendas')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        frm = ctk.CTkFrame(self)
        frm.pack(fill='both', expand=True)

        # 1. Arquivos
        grid_frame = ctk.CTkFrame(frm)
        grid_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(grid_frame, text='Vídeo/Áudio de entrada:').grid(row=0, column=0, sticky='w', pady=5)
        ctk.CTkEntry(grid_frame, textvariable=self.video_path, width=60).grid(row=0, column=1, sticky='we', padx=8, pady=5)
        ctk.CTkButton(grid_frame, text='Selecionar...', command=self._pick_video).grid(row=0, column=2, sticky='e', pady=5)

        ctk.CTkLabel(grid_frame, text='Legenda SRT (Opcional):').grid(row=1, column=0, sticky='w', pady=5)
        ctk.CTkEntry(grid_frame, textvariable=self.srt_path, width=60).grid(row=1, column=1, sticky='we', padx=8, pady=5)
        ctk.CTkButton(grid_frame, text='Selecionar...', command=self._pick_srt).grid(row=1, column=2, sticky='e', pady=5)

        ctk.CTkLabel(grid_frame, text='Arquivo de saída (mp4):').grid(row=2, column=0, sticky='w', pady=5)
        ctk.CTkEntry(grid_frame, textvariable=self.output_path, width=60).grid(row=2, column=1, sticky='we', padx=8, pady=5)
        ctk.CTkButton(grid_frame, text='Salvar como...', command=self._pick_output).grid(row=2, column=2, sticky='e', pady=5)
        grid_frame.columnconfigure(1, weight=1)

        ttk.Separator(frm).pack(fill='x', pady=10)

        # 2. Transcrição
        trans_frame = ctk.CTkLabelFrame(frm, text=' Transcrição Automática (Se SRT não for enviado) ')
        trans_frame.pack(fill='x', pady=5)
        ctk.CTkSwitch(trans_frame, text='Gerar SRT automaticamente', variable=self.auto_transcribe).pack(anchor='w')
        eng_frame = ctk.CTkFrame(trans_frame)
        eng_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(eng_frame, text="Engine:").pack(side='left')
        ttk.Radiobutton(eng_frame, text='Vosk (Rápido)',              variable=self.transcription_engine, value='vosk').pack(side='left', padx=10)
        ttk.Radiobutton(eng_frame, text='Whisper (Preciso - demora mais)', variable=self.transcription_engine, value='whisper').pack(side='left', padx=10)

        ttk.Separator(frm).pack(fill='x', pady=8)

        # 3. Estilo & Renderização
        style_frame = ctk.CTkLabelFrame(frm, text=' Estilo e Renderização (Karaoke Mode) ')
        style_frame.pack(fill='x', pady=5)

        # Linha A: Perfil + Formato
        rowA = ctk.CTkFrame(style_frame)
        rowA.pack(fill='x', pady=4)
        ctk.CTkLabel(rowA, text='Perfil de Legenda:').pack(side='left')
        self.cb_perfis = ctk.CTkOptionMenu(rowA, variable=self.preset_selecionado, width=280)
        self.cb_perfis.pack(side='left', padx=6)
        self.cb_perfis.bind('<<ComboboxSelected>>', self._aplicar_perfil)
        ctk.CTkButton(rowA, text='🔄 Atualizar Lista', command=self._carregar_perfis_ui).pack(side='left', padx=4)
        ctk.CTkLabel(rowA, text='Formato:').pack(side='left', padx=(20, 6))
        ttk.Radiobutton(rowA, text='📱 Vertical',   variable=self.formato_video, value='vertical').pack(side='left', padx=4)
        ttk.Radiobutton(rowA, text='🖥️ Horizontal', variable=self.formato_video, value='horizontal').pack(side='left', padx=4)

        # Grid de controles manuais
        ctrl = ctk.CTkFrame(style_frame)
        ctrl.pack(fill='x', pady=4)

        fontes = ["Bangers","Arial","Impact","Komika Axis","Montserrat","Oswald","Roboto","Anton","TheBoldFont"]
        temas  = get_temas_disponiveis()
        efeitos = ["Nenhum","Pulo (Pop)","Balanço","Giro Zoom","Tremor","Neon","Flash","Karate","Bomba","Sublinha","Cinema"]
        posicoes = ["meio baixo","meio","topo","embaixo"]

        # Linha 1
        ctk.CTkLabel(ctrl, text="Fonte:").grid(row=0, column=0, sticky='w', padx=4, pady=3)
        self.ctrl_font = ctk.CTkOptionMenu(ctrl, variable=self.sub_font, values=fontes, width=140)
        self.ctrl_font.grid(row=0, column=1, sticky='w', padx=4, pady=3)

        ctk.CTkLabel(ctrl, text="Palavras/bloco:").grid(row=0, column=2, sticky='w', padx=4)
        self.ctrl_words = ttk.Spinbox(ctrl, from_=1, to=15, textvariable=self.sub_words, width=5)
        self.ctrl_words.grid(row=0, column=3, sticky='w', padx=4)

        ctk.CTkLabel(ctrl, text="Tamanho (px):").grid(row=0, column=4, sticky='w', padx=4)
        self.ctrl_size = ttk.Spinbox(ctrl, from_=10, to=300, textvariable=self.sub_size, width=5)
        self.ctrl_size.grid(row=0, column=5, sticky='w', padx=4)

        # Linha 2
        ctk.CTkLabel(ctrl, text="Posição:").grid(row=1, column=0, sticky='w', padx=4, pady=3)
        self.ctrl_pos = ctk.CTkOptionMenu(ctrl, variable=self.sub_pos, values=posicoes, width=140)
        self.ctrl_pos.grid(row=1, column=1, sticky='w', padx=4, pady=3)

        ctk.CTkLabel(ctrl, text="Tema:").grid(row=1, column=2, sticky='w', padx=4)
        self.ctrl_theme = ctk.CTkOptionMenu(ctrl, variable=self.sub_theme, values=temas, width=180)
        self.ctrl_theme.grid(row=1, column=3, sticky='w', padx=4)

        ctk.CTkLabel(ctrl, text="MargemV (px):").grid(row=1, column=4, sticky='w', padx=4)
        self.ctrl_margin_v = ttk.Spinbox(ctrl, from_=0, to=500, textvariable=self.sub_margin_v, width=5)
        self.ctrl_margin_v.grid(row=1, column=5, sticky='w', padx=4)

        # Linha 3
        ctk.CTkLabel(ctrl, text="Efeito:").grid(row=2, column=0, sticky='w', padx=4, pady=3)
        self.ctrl_effect = ctk.CTkOptionMenu(ctrl, variable=self.sub_effect, values=efeitos, width=140)
        self.ctrl_effect.grid(row=2, column=1, sticky='w', padx=4, pady=3)

        ctk.CTkLabel(ctrl, text="Contorno:").grid(row=2, column=2, sticky='w', padx=4)
        self.ctrl_border_w = ttk.Spinbox(ctrl, from_=0, to=20, textvariable=self.sub_border_w, width=5)
        self.ctrl_border_w.grid(row=2, column=3, sticky='w', padx=4)

        # 4. Mapa de Cores do Podcast
        ttk.Separator(frm).pack(fill='x', pady=8)
        mapa_frame = ctk.CTkLabelFrame(frm, text=' 🎨 Mapa de Cores por Personagem (Podcast) ')
        mapa_frame.pack(fill='x', pady=5)

        rowM = ctk.CTkFrame(mapa_frame)
        rowM.pack(fill='x')
        ctk.CTkEntry(rowM, textvariable=self.mapa_temas_path, width=500).pack(side='left', padx=(0,6))
        ctk.CTkButton(rowM, text='📂 Carregar', command=self._pick_mapa).pack(side='left')
        ctk.CTkButton(rowM, text='✖ Limpar',   command=lambda: [self.mapa_temas_path.set(''), self._toggle_tema_ctrl()]).pack(side='left', padx=4)
        self.mapa_temas_path.trace_add('write', lambda *_: self._toggle_tema_ctrl())
        ctk.CTkLabel(mapa_frame,
                  text="Quando um mapa de cores for carregado, o campo 'Tema' acima fica desabilitado "
                       "(as cores vêm do mapa por personagem).",
                  text_color='gray', font=("Segoe UI", 8)).pack(anchor='w', pady=(4,0))

        # Botão gerar + status
        ctk.CTkButton(frm, text='🎬 GERAR VÍDEO LEGENDADO', command=self._gerar).pack(fill='x', pady=16)
        ctk.CTkLabel(frm, textvariable=self.status, anchor='w').pack(fill='x', side='bottom')

    def _toggle_tema_ctrl(self):
        """Desabilita o combobox de Tema quando um mapa de cores está carregado."""
        if self.mapa_temas_path.get().strip():
            self.ctrl_theme.config(state='disabled')
        else:
            self.ctrl_theme.config(state='readonly')

    # ── helpers de arquivo ─────────────────────────────────────────────────────
    def _pick_video(self):
        p = filedialog.askopenfilename(filetypes=[('Mídia','*.mp4;*.mov;*.mkv;*.avi;*.webm;*.mp3;*.wav;*.m4a'),('Todos','*.*')])
        if p: self.video_path.set(p)

    def _pick_srt(self):
        p = filedialog.askopenfilename(filetypes=[('SubRip','*.srt'),('Todos','*.*')])
        if p: self.srt_path.set(p)

    def _pick_output(self):
        p = filedialog.asksaveasfilename(defaultextension='.mp4', filetypes=[('MP4','*.mp4')])
        if p: self.output_path.set(p)

    def _pick_mapa(self):
        p = filedialog.askopenfilename(filetypes=[('Mapa de Temas JSON','*.json'),('Todos','*.*')])
        if p: self.mapa_temas_path.set(p)

    # ── perfis ─────────────────────────────────────────────────────────────────
    def _carregar_perfis_ui(self):
        if not self.config_manager: return
        perfis = self.config_manager.get("perfis_legenda", {})
        nomes = ["[Personalizado]"] + list(perfis.keys())
        self.cb_perfis['values'] = nomes
        if nomes and self.preset_selecionado.get() not in nomes:
            self.preset_selecionado.set(nomes[0])
            self._aplicar_perfil()

    def _aplicar_perfil(self, event=None):
        if not self.config_manager: return
        nome = self.preset_selecionado.get()
        
        def set_state(st):
            for c in [self.ctrl_font, self.ctrl_words, self.ctrl_size,
                      self.ctrl_pos, self.ctrl_theme, self.ctrl_margin_v,
                      self.ctrl_effect, self.ctrl_border_w]:
                if hasattr(self, 'ctrl_font'):
                    c.configure(state=st)
        
        if nome == "[Personalizado]":
            set_state("normal")
            return
            
        perfis = self.config_manager.get("perfis_legenda", {})
        p = perfis.get(nome, {})
        if not p: return
        self.sub_font.set(p.get("font",     "Bangers"))
        self.sub_words.set(p.get("words",   5))
        self.sub_pos.set(p.get("pos",       "meio baixo"))
        self.sub_theme.set(p.get("theme",   "amarelo vermelho"))
        self.sub_size.set(p.get("size",     100))
        self.sub_margin_v.set(p.get("margin_v", 150))
        self.sub_effect.set(p.get("effect", "Pulo (Pop)"))
        self.sub_border_w.set(p.get("border_w", 3))
        set_state("disabled")

    # ── transcrição ────────────────────────────────────────────────────────────
    def _extract_audio_wav(self, media_path, wav_path):
        cmd = ['ffmpeg','-y','-i',media_path,'-vn','-ac','1','-ar','16000','-f','wav',wav_path]
        subprocess.run(cmd, check=True, capture_output=True)

    @staticmethod
    def _format_timestamp(sec):
        msec = int((sec - int(sec)) * 1000)
        s = int(sec); h = s // 3600; s %= 3600; m = s // 60; s %= 60
        return f"{h:02d}:{m:02d}:{s:02d},{msec:03d}"

    def _parse_srt_to_whisper_result(self, srt_path):
        with open(srt_path,'r',encoding='utf-8') as f: content = f.read()
        words = []
        for blk in content.strip().split('\n\n'):
            lines = blk.strip().split('\n')
            if len(lines) >= 3:
                try:
                    s_str, e_str = lines[1].split(' --> ')
                    def t2s(ts):
                        pts = ts.replace(',','.').split(':')
                        return float(pts[0])*3600 + float(pts[1])*60 + float(pts[2])
                    words.append({'word': " ".join(lines[2:]), 'start': t2s(s_str), 'end': t2s(e_str)})
                except Exception: pass
        return {'segments': [{'words': words}]}

    def _transcrever_para_srt(self, media_path, model_dir, out_dir):
        if not VOSK_AVAILABLE: raise RuntimeError('Biblioteca Vosk não instalada.')
        wav_path = os.path.join(out_dir, 'audio_for_vosk.wav')
        self._extract_audio_wav(media_path, wav_path)
        model = Model(model_dir)
        rec   = KaldiRecognizer(model, 16000); rec.SetWords(True)
        wf    = wave.open(wav_path, 'rb')
        results = []
        while True:
            data = wf.readframes(4000)
            if not data: break
            if rec.AcceptWaveform(data): results.append(json.loads(rec.Result()))
        results.append(json.loads(rec.FinalResult())); wf.close()
        words = [w for r in results if 'result' in r for w in r['result']]
        srt_path = os.path.join(out_dir, 'auto_subs.srt')
        with open(srt_path,'w',encoding='utf-8') as f:
            for i,w in enumerate(words,1):
                f.write(f"{i}\n{self._format_timestamp(w['start'])} --> {self._format_timestamp(w['end'])}\n{w['word']}\n\n")
        return srt_path, {'segments': [{'words': words}]}

    def _transcrever_com_whisper(self, media_path, out_dir):
        if not WHISPER_AVAILABLE: raise RuntimeError('Whisper não instalado.')
        model = whisper.load_model("base")
        try:
            result = model.transcribe(media_path, fp16=False, language='pt', word_timestamps=True)
        except Exception:
            result = model.transcribe(media_path, fp16=False, language='pt')
        for seg in result.get('segments', []):
            if 'words' not in seg:
                seg['words'] = [{'word': seg['text'], 'start': seg['start'], 'end': seg['end']}]
        srt_path = os.path.join(out_dir, 'auto_subs_whisper.srt')
        with open(srt_path,'w',encoding='utf-8') as f:
            for i,seg in enumerate(result['segments'],1):
                f.write(f"{i}\n{self._format_timestamp(seg['start'])} --> {self._format_timestamp(seg['end'])}\n{seg['text'].strip()}\n\n")
        return srt_path, result

    # ── carregamento do mapa de temas ─────────────────────────────────────────
    def _carregar_voice_color_map(self):
        mapa_file = self.mapa_temas_path.get().strip()
        if not mapa_file or not os.path.exists(mapa_file):
            return None
        try:
            with open(mapa_file,'r',encoding='utf-8') as f:
                mapa_raw = json.load(f)
            print(f'[TEMAS GL] {len(mapa_raw)} falas mapeadas.')
            return mapa_raw
        except Exception as e:
            print(f'[AVISO TEMAS GL] {e}')
            return None

    # ── geração ────────────────────────────────────────────────────────────────
    def _gerar(self):
        vp = self.video_path.get().strip()
        sp = self.srt_path.get().strip()
        op = self.output_path.get().strip()

        if not vp or not os.path.exists(vp):
            messagebox.showerror('Erro', 'Selecione um vídeo/áudio válido.')
            return

        import threading
        def run():
            try:
                self.status.set('Preparando...')
                temp_dir     = self._make_temp_dir()
                whisper_result = None

                # 1. OBTER RESULTADO DE TRANSCRIÇÃO
                if sp and os.path.exists(sp):
                    self.status.set('Fazendo parse do SRT fornecido...')
                    whisper_result = self._parse_srt_to_whisper_result(sp)
                elif self.auto_transcribe.get():
                    self.status.set('Transcrevendo áudio... aguarde.')
                    engine = self.transcription_engine.get()
                    if engine == 'whisper':
                        srt_generated, whisper_result = self._transcrever_com_whisper(vp, temp_dir)
                    else:
                        model_dir = self.vosk_model_path.get().strip()
                        if not model_dir or not os.path.isdir(model_dir):
                            raise Exception("Modelo Vosk não encontrado.")
                        srt_generated, whisper_result = self._transcrever_para_srt(vp, model_dir, temp_dir)
                else:
                    raise Exception('Forneça um SRT ou habilite a transcrição automática.')

                if not op:
                    base, _ = os.path.splitext(vp)
                    op_path = f"{base}_legendado.mp4"
                else:
                    op_path = op

                # 2. CARREGAR MAPA DE CORES (opcional)
                voice_color_map = self._carregar_voice_color_map()

                # 2b. CARREGAR PERFIS POR PERSONAGEM do config_manager
                perfis_personagem = None
                if self.config_manager:
                    perfis_personagem = self.config_manager.get("perfis_personagem", {}) or None

                # 2c. Extrair cores do perfil atual
                sub_colors_ui = None
                perfil_nome_ui = self.preset_selecionado.get()
                if perfil_nome_ui and perfil_nome_ui != "[Personalizado]":
                    perfis = self.config_manager.get("perfis_legenda", {}) if self.config_manager else {}
                    if perfil_nome_ui in perfis and 'colors' in perfis[perfil_nome_ui]:
                        sub_colors_ui = perfis[perfil_nome_ui]['colors']

                # 3. GERAR ASS
                self.status.set('Gerando efeitos e montando legendas ASS...')
                ass_path = os.path.join(temp_dir, 'master_legendas.ass')

                generate_karaoke_ass(
                    whisper_result  = whisper_result,
                    srt_path        = ass_path,
                    font            = self.sub_font.get(),
                    size            = self.sub_size.get(),
                    theme           = self.sub_theme.get(),
                    colors          = sub_colors_ui,
                    pos             = self.sub_pos.get(),
                    margin_v        = self.sub_margin_v.get(),
                    effect          = self.sub_effect.get(),
                    video_format    = self.formato_video.get(),
                    words_per_block = self.sub_words.get(),
                    voice_color_map = voice_color_map,
                    border_w        = self.sub_border_w.get(),
                    perfis_personagem = perfis_personagem
                )

                # 4. QUEIMAR NO VÍDEO
                self.status.set('Queimando legendas no vídeo (FFmpeg)...')
                esc_ass = ass_path.replace('\\','/').replace(':','\\:')
                cmd = [
                    'ffmpeg','-y','-i', vp,
                    '-vf', f"ass='{esc_ass}'",
                    '-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium',
                    '-c:a','copy', op_path
                ]
                r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
                if r.returncode != 0:
                    raise Exception(f"Erro no FFmpeg:\n{r.stderr[-400:]}")

                self.status.set(f'Pronto! Arquivo: {op_path}')
                self.after(0, lambda: messagebox.showinfo('Sucesso', f'Vídeo legendado com sucesso:\n{op_path}'))

            except Exception as e:
                self.status.set('Erro na operação.')
                self.after(0, lambda e=e: messagebox.showerror('Erro', str(e)))

        threading.Thread(target=run, daemon=True).start()
