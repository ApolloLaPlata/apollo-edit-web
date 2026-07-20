import customtkinter as ctk
import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import random
import threading
from pathlib import Path
import json

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

def get_atempo_chain(speed_factor):
    tempo = 1.0 / speed_factor
    if tempo == 1.0:
        return "atempo=1.0"
    chain = []
    while tempo > 2.0:
        chain.append("atempo=2.0")
        tempo /= 2.0
    while tempo < 0.5:
        chain.append("atempo=0.5")
        tempo /= 0.5
    if tempo != 1.0:
        chain.append(f"atempo={tempo:.4f}")
    return ",".join(chain)

def ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def hex_to_ass_color(hex_color):
    if not hex_color:
        return "&H00FFFFFF"
    hex_color = str(hex_color).strip()
    if hex_color.startswith('#') and len(hex_color) == 7:
        r = hex_color[1:3]
        g = hex_color[3:5]
        b = hex_color[5:7]
        return f"&H00{b}{g}{r}"
    if hex_color.startswith('&H'):
        return hex_color.strip('&')
    return hex_color

def ass_colors(theme):
    themes = {}
    import json
    import os
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temas_legendas.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in data.items():
                    # Suporta o formato novo e fallback pro antigo
                    p_c = v.get("cor_primaria", "&H00FFFFFF")
                    s_c = v.get("cor_secundaria", p_c) # fallback se não existir
                    o_c = v.get("cor_borda", "&H00000000")
                    themes[k.lower()] = (p_c, s_c, o_c)
                    themes[k] = (p_c, s_c, o_c)
        except Exception as e:
            print(f"Erro lendo temas_legendas.json: {e}")
            
    # Fallback se falhar ou theme nao encontrado
    if not themes:
        themes = {
            "padrao": ("&H00FFFFFF", "&H00000000", "&H00000000"),
            "rosa neon": ("&H00FFFFFF", "&H00FF00FF", "&H00000000"),
            "amarelo queimado": ("&H00FFFFFF", "&H0000FFFF", "&H00000000")
        }
    return themes.get(theme, themes.get(theme.lower(), ("&H00FFFFFF", "&H0000FFFF", "&H00000000")))

def get_temas_disponiveis():
    import json
    import os
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temas_legendas.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return list(data.keys())
        except:
            pass
    return ["Padrão", "Rosa Neon", "Amarelo Queimado"]


def _make_txt_ass(blk_ctx, anchor_ctx, pos_tag_ctx, p_color_ctx, s_color_ctx, o_color_ctx, effect_ctx, hidx=None):
    """Monta o texto de um evento Dialogue ASS com destaque karaoke na palavra hidx."""
    parts = [anchor_ctx, pos_tag_ctx]
    
    # As tags de override (\\c e \\3c) no ASS exigem 6 digitos hex e '&' no final (ex: &H00FF00&)
    # As cores vêm em 8 dígitos com alpha (ex: &H0000FF00), então cortamos o alpha (&H00) e adicionamos &
    p_tag = f"&H{p_color_ctx[4:]}&" if p_color_ctx.startswith("&H") and len(p_color_ctx) == 10 else p_color_ctx
    s_tag = f"&H{s_color_ctx[4:]}&" if s_color_ctx.startswith("&H") and len(s_color_ctx) == 10 else s_color_ctx
    o_tag = f"&H{o_color_ctx[4:]}&" if o_color_ctx.startswith("&H") and len(o_color_ctx) == 10 else o_color_ctx

    for j, w in enumerate(blk_ctx):
        t = w['word'].strip().upper()
        
        # [ETAPA 11] Se a palavra tiver uma cor dinâmica definida pela IA (Legendas por emoção)
        # ASS usa formato BGR (ex: &H00FF00FF&), mas o Gemini pode mandar o nome da cor em português
        # Então mapeamos cores comuns para os códigos hexadecimais do formato ASS
        w_color_override = p_tag
        if 'legenda_cor' in w and w['legenda_cor'] != "":
            c_str = w['legenda_cor'].lower()
            if 'vermelho' in c_str or 'red' in c_str or 'raiva' in c_str or 'agressivo' in c_str: w_color_override = "&H000000FF&"
            elif 'verde' in c_str or 'green' in c_str or 'esperança' in c_str: w_color_override = "&H0000FF00&"
            elif 'azul' in c_str or 'blue' in c_str or 'triste' in c_str or 'calmo' in c_str: w_color_override = "&H00FF0000&"
            elif 'amarelo' in c_str or 'yellow' in c_str or 'atenção' in c_str: w_color_override = "&H0000FFFF&"
            elif 'roxo' in c_str or 'purple' in c_str or 'misterioso' in c_str: w_color_override = "&H00FF0080&"
            elif 'rosa' in c_str or 'pink' in c_str or 'amor' in c_str: w_color_override = "&H00FF00FF&"
            elif 'laranja' in c_str or 'orange' in c_str or 'energia' in c_str: w_color_override = "&H00008CFF&"
            elif 'branco' in c_str or 'white' in c_str: w_color_override = "&H00FFFFFF&"
            elif 'preto' in c_str or 'black' in c_str: w_color_override = "&H00000000&"
            elif 'ciano' in c_str or 'cyan' in c_str: w_color_override = "&H00FFFF00&"
            elif 'magenta' in c_str: w_color_override = "&H00FF00FF&"
            elif 'lima' in c_str or 'lime' in c_str: w_color_override = "&H0000FF00&"
            elif 'ouro' in c_str or 'gold' in c_str: w_color_override = "&H0000D7FF&"
            elif 'cinza' in c_str or 'gray' in c_str: w_color_override = "&H00808080&"
            elif 'marrom' in c_str or 'brown' in c_str: w_color_override = "&H002A2AFF&"
        
        if j == hidx:
            c_tag = f"\\c{s_tag}\\3c{o_tag}"
            if effect_ctx == 'Pulo (Pop)':
                style = rf'{{{c_tag}\fscx112\fscy112\shad6\bord3\t(0,120,\fscx100\fscy100\shad1\bord2)}}'
            elif effect_ctx == 'Balanço':
                style = rf'{{{c_tag}\frz12\t(0,50,\frz-12)\t(50,100,\frz0)\fscx100\fscy100}}'
            elif effect_ctx == 'Giro Zoom':
                style = rf'{{{c_tag}\frz-20\fscx120\fscy120\t(0,120,\frz0\fscx100\fscy100)}}'
            elif effect_ctx == 'Tremor':
                style = rf'{{{c_tag}\frz4\t(0,20,\frz-4)\t(20,40,\frz4)\t(40,60,\frz-4)\t(60,80,\frz0)\fscx100\fscy100}}'
            elif effect_ctx == 'Neon':
                style = rf'{{{c_tag}\bord5\shad0\blur3\t(0,100,\bord2\blur1)}}'
            elif effect_ctx == 'Flash':
                style = rf'{{{c_tag}\alpha&H00&\t(0,60,\alpha&H80&)\t(60,120,\alpha&H00&)\fscx100\fscy100}}'
            elif effect_ctx == 'Karate':
                style = rf'{{{c_tag}\frz-25\fscx108\fscy108\t(0,80,\frz8)\t(80,140,\frz0\fscx100\fscy100)}}'
            elif effect_ctx == 'Bomba':
                style = rf'{{{c_tag}\fscx118\fscy118\shad8\t(0,80,\fscx100\fscy100\shad2)}}'
            elif effect_ctx == 'Sublinha':
                style = rf'{{{c_tag}\bord0\shad5\blur0\t(0,100,\shad2)\fscx100\fscy100}}'
            elif effect_ctx == 'Cinema':
                style = rf'{{{c_tag}\alpha&H60&\bord4\t(0,120,\alpha&H00&\bord2)\fscx100\fscy100}}'
            else:
                style = rf'{{{c_tag}\fscx100\fscy100\frz0}}'
        else:
            c_tag = f"\\c{w_color_override}\\3c{o_tag}"
            style = rf'{{{c_tag}\fscx100\fscy100\frz0}}'
        parts.append(style)
        parts.append(t)
        if j < len(blk_ctx) - 1:
            parts.append(' ')
    return ''.join(parts)



def _get_tema_para_tempo(t, voice_color_map):
    """Retorna o nome do tema do personagem ativo no tempo t, ou None se sem mapa."""
    if not voice_color_map:
        return None
    for entrada in voice_color_map:
        s, e = entrada['start'], entrada['end']
        if s <= t < e:
            return entrada.get('tema')
    # Fallback: última entrada cobre o fim do áudio
    last = voice_color_map[-1]
    if t >= last['start']:
        return last.get('tema')
    return None


def _get_personagem_para_tempo(t, voice_color_map):
    """Retorna o nome do personagem ativo no tempo t, ou None."""
    if not voice_color_map:
        return None
    for entrada in voice_color_map:
        s, e = entrada['start'], entrada['end']
        if s <= t < e:
            return entrada.get('personagem') or entrada.get('speaker')
    last = voice_color_map[-1]
    if t >= last['start']:
        return last.get('personagem') or last.get('speaker')
    return None

def generate_karaoke_ass(whisper_result, srt_path, font="Bangers", size=100, theme="amarelo vermelho", pos="meio baixo", margin_v=80, words_per_block=5, video_format='vertical', effect="Pulo (Pop)", voice_color_map=None, border_w=3, perfis_personagem=None, colors=None):
    """
    Gera arquivo ASS de karaoke.
    Se perfis_personagem for fornecido (dict nome→{font,theme,colors,effect,size,border_w}),
    cada personagem recebe seu próprio estilo ASS (fonte, cor e borda únicos).
    """
    if colors and len(colors) >= 3:
        p_color = hex_to_ass_color(colors[0])
        s_color = hex_to_ass_color(colors[1])
        o_color = hex_to_ass_color(colors[2])
    else:
        p_color, s_color, o_color = ass_colors(theme)

    # Ajusta resolução do canvas ASS conforme o formato do vídeo
    if video_format == 'horizontal':
        W, H = 1920, 1080
    else:
        W, H = 1080, 1920

    align = 5  # \an5 = centralizado

    if pos == "meio baixo" or pos == "meio-baixo":
        y = int(H * 0.75)
    elif pos == "topo":
        y = margin_v
    elif pos == "meio":
        y = H // 2
    else:  # embaixo
        y = H - margin_v

    x = W // 2
    anchor = r"{\an5}"
    pos_tag = rf"{{\pos({x},{y})}}"

    # ── Coleta personagens únicos para gerar um Style por personagem ────────
    perfis = perfis_personagem or {}
    # Descobre personagens presentes no voice_color_map
    personagens_presentes = set()
    if voice_color_map:
        for entrada in voice_color_map:
            p = entrada.get('personagem') or entrada.get('speaker')
            if p:
                personagens_presentes.add(p)

    # Função Helper para extrair as variáveis de formatação baseado no personagem
    def _get_format_for_char(char_name):
        # Fallbacks globais
        f_font, f_size, f_bw = font, size, border_w
        f_pos, f_mar = pos, margin_v
        f_effect = effect
        if colors and len(colors) >= 3:
            f_pc, f_sc, f_oc = hex_to_ass_color(colors[0]), hex_to_ass_color(colors[1]), hex_to_ass_color(colors[2])
        else:
            f_pc, f_sc, f_oc = ass_colors(theme)

        if char_name and char_name in perfis:
            p_data = perfis[char_name]
            p_data_fmt = p_data.get(video_format, {})
            if p_data_fmt:
                f_font = p_data_fmt.get('font', f_font)
                f_size = p_data_fmt.get('size', f_size)
                f_bw   = p_data_fmt.get('border_w', f_bw)
                f_pos  = p_data_fmt.get('pos', f_pos)
                f_mar  = p_data_fmt.get('margin_v', f_mar)
                f_effect = p_data_fmt.get('effect', f_effect)
                
                if "color_primary" in p_data_fmt:
                    f_pc = hex_to_ass_color(p_data_fmt["color_primary"])
                    f_sc = hex_to_ass_color(p_data_fmt["color_secondary"])
                    f_oc = hex_to_ass_color(p_data_fmt["color_outline"])
                elif p_data_fmt.get('colors') and len(p_data_fmt['colors']) >= 3:
                    f_pc = hex_to_ass_color(p_data_fmt['colors'][0])
                    f_sc = hex_to_ass_color(p_data_fmt['colors'][1])
                    f_oc = hex_to_ass_color(p_data_fmt['colors'][2])
        return f_font, f_size, f_bw, f_pc, f_sc, f_oc, f_pos, f_mar, f_effect

    # ── Monta estilos ASS ────────────────────────────────────────────────────
    style_fmt = "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
    styles = []
    
    # Global / fallback style
    styles.append(
        f"Style: SubK,{font},{size},{p_color},{s_color},{o_color},"
        f"&H00000000,-1,0,0,0,100,100,0,0,1,{border_w},{max(0, border_w - 1)},{align},20,20,0,1"
    )
    
    _persona_style_map = {}  # nome → nome_estilo_ASS
    for nome in personagens_presentes:
        f_font, f_size, f_bw, f_pc, f_sc, f_oc, _, _, _ = _get_format_for_char(nome)
        style_name = f"SubK_{nome.replace(' ','_')}"
        styles.append(
            f"Style: {style_name},{f_font},{f_size},{f_pc},{f_sc},{f_oc},"
            f"&H00000000,-1,0,0,0,100,100,0,0,1,{f_bw},{max(0, f_bw - 1)},{align},20,20,0,1"
        )
        _persona_style_map[nome] = style_name

    header = f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\n\n[V4+ Styles]\n{style_fmt}\n" + "\n".join(styles) + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

    # Achata palavras de todos os segmentos
    words_flat = [w for seg in whisper_result.get('segments', []) for w in seg.get('words', [])]
    blocks = [words_flat[i:i + words_per_block] for i in range(0, len(words_flat), words_per_block)]

    # Calcula fim real de cada bloco (fecha gap curto com o proximo)
    end_map = {}
    for bi, blk in enumerate(blocks):
        if not blk:
            continue
        end = float(blk[-1]['end'])
        if bi < len(blocks) - 1 and blocks[bi + 1]:
            next_st = float(blocks[bi + 1][0]['start'])
            if max(0.0, next_st - end) <= 2.0:
                end = max(float(blk[0]['start']), next_st - 0.01)
        end_map[bi] = end

    # Gera eventos ASS — UMA linha por palavra, com estilo do personagem ativo
    dialogue_lines = []
    for bi, blk in enumerate(blocks):
        if not blk:
            continue
        blk_end = end_map.get(bi, float(blk[-1]['end']))
        blk_mid = float(blk[0]['start'])

        # Cores do bloco (por tema)
        tm_nome = _get_tema_para_tempo(blk_mid, voice_color_map)
        if tm_nome:
            blk_p, blk_s, blk_o = ass_colors(tm_nome)
        else:
            blk_p, blk_s, blk_o = p_color, s_color, o_color

        # Efeito do personagem (pode variar por personagem)
        nome_personagem = _get_personagem_para_tempo(blk_mid, voice_color_map)
        blk_effect = effect
        
        # Override se tiver perfil
        if nome_personagem and nome_personagem in perfis:
            p_data = perfis[nome_personagem]
            if p_data.get('colors') and len(p_data['colors']) >= 3:
                blk_p = hex_to_ass_color(p_data['colors'][0])
                blk_s = hex_to_ass_color(p_data['colors'][1])
                blk_o = hex_to_ass_color(p_data['colors'][2])
            elif p_data.get('theme'):
                blk_p, blk_s, blk_o = ass_colors(p_data['theme'])
                
        blk_style = _persona_style_map.get(nome_personagem, "SubK") if nome_personagem else "SubK"

        for k, w in enumerate(blk):
            wst = float(w['start'])
            wen = float(blk[k + 1]['start']) if k < len(blk) - 1 else blk_end
            
            txt = _make_txt_ass(
                blk_ctx=blk,
                anchor_ctx=anchor,
                pos_tag_ctx=pos_tag,
                p_color_ctx=blk_p,
                s_color_ctx=blk_s,
                o_color_ctx=blk_o,
                effect_ctx=blk_effect,
                hidx=k
            )
            
            dialogue_lines.append(
                f'Dialogue: 0,{ass_time(wst)},{ass_time(wen)},{blk_style},,0,0,0,,{txt}'
            )

    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write(header + '\n'.join(dialogue_lines) + '\n')


class AbaEdicaoBasica(ctk.CTkFrame):
    def __init__(self, parent, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        
        self.cache_file = os.path.join(os.path.dirname(__file__), 'cache_edicao_basica.json')
        self.thumbnail_cache = {}
        self.video_paths = []
        
        # Variables Setup
        self.audio_narrador = tk.StringVar()
        self.capa = tk.StringVar()
        self.logo = tk.StringVar()
        self.logo_scale = tk.IntVar(value=100)
        self.logo_x = tk.IntVar(value=20)
        self.logo_y = tk.IntVar(value=20)
        self.musica = tk.StringVar()
        self.vol_musica = tk.IntVar(value=-12)
        self.vol_narrador = tk.IntVar(value=5)
        self.vol_video = tk.IntVar(value=-5)
        self.var_coloracao = tk.BooleanVar(value=True)
        self.nivel_cor = tk.IntVar(value=3)
        self.var_legenda = tk.BooleanVar(value=True)
        self.vinhetas_dir = tk.StringVar()
        self.saida_dir = tk.StringVar()
        self.nome_final = tk.StringVar(value="video_completo")
        
        # Legenda Vars (Estilo DarkFacil)
        self.sub_font = tk.StringVar(value="Bangers")
        self.sub_words = tk.IntVar(value=5)
        self.sub_pos = tk.StringVar(value="meio baixo")
        self.sub_theme = tk.StringVar(value="amarelo vermelho")
        self.sub_size = tk.IntVar(value=100)
        self.sub_margin_v = tk.IntVar(value=150)
        self.sub_effect = tk.StringVar(value="Pulo (Pop)")
        
        # 6. Camadas Extras (Overlays Avançados)
        self.lay0_bg_path = tk.StringVar()
        self.lay0_scale = tk.IntVar(value=100)
        self.lay0_x = tk.IntVar(value=0)
        self.lay0_y = tk.IntVar(value=0)
        self.lay0_random = tk.BooleanVar(value=True)

        self.base_scale = tk.IntVar(value=100)
        self.base_x = tk.IntVar(value=0)
        self.base_y = tk.IntVar(value=0)
        self.base_loop = tk.BooleanVar(value=False)

        self.lay1_fundo_path = tk.StringVar()
        self.lay1_scale = tk.IntVar(value=100)
        self.lay1_x = tk.IntVar(value=0)
        self.lay1_y = tk.IntVar(value=0)
        self.lay1_chroma = tk.BooleanVar(value=False)
        self.lay1_random = tk.BooleanVar(value=False)

        self.lay2_narrador_path = tk.StringVar()
        self.lay2_scale = tk.IntVar(value=30)
        self.lay2_x = tk.IntVar(value=50)
        self.lay2_y = tk.IntVar(value=1500)
        self.lay2_chroma = tk.BooleanVar(value=True)
        self.lay2_random = tk.BooleanVar(value=False)

        self.lay3_frente_path = tk.StringVar()
        self.lay3_scale = tk.IntVar(value=30)
        self.lay3_x = tk.IntVar(value=50)
        self.lay3_y = tk.IntVar(value=1500)
        self.lay3_chroma = tk.BooleanVar(value=True)
        self.lay3_random = tk.BooleanVar(value=False)

        self.lay4_moldura_dir = tk.StringVar()
        self.lay4_random = tk.BooleanVar(value=True)

        self.lay5_extra_path = tk.StringVar()
        self.lay5_scale = tk.IntVar(value=50)
        self.lay5_x = tk.IntVar(value=50)
        self.lay5_y = tk.IntVar(value=50)
        self.lay5_chroma = tk.BooleanVar(value=False)
        self.lay5_random = tk.BooleanVar(value=False)
        
        self.perfil_selecionado = tk.StringVar()
        self.video_format = tk.StringVar(value='vertical')
        self.mapa_temas_path = tk.StringVar()   # Mapa de cores do Podcast
        
        # UI Setup
        header = ctk.CTkFrame(self)
        header.pack(fill='x', padx=20, pady=10)
        ctk.CTkLabel(header, text="EDIÇÃO BÁSICA (Sincronizada & Dinâmica)", font=("Segoe UI", 18, "bold")).pack(anchor='w')

        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill='both', expand=True, padx=20, pady=5)
        
        left_container = ctk.CTkFrame(main_pane)
        right_frame = ctk.CTkFrame(main_pane)
        main_pane.add(left_container, weight=3)
        main_pane.add(right_frame, weight=2)
        
        canvas = tk.Canvas(left_container)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        left_frame = ctk.CTkFrame(canvas)
        
        left_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=left_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        row = 0
        
        # 1. Audio
        ctk.CTkLabel(left_frame, text="1. ÁUDIO DO NARRADOR").grid(row=row, column=0, sticky='w', pady=4); row+=1
        ctk.CTkEntry(left_frame, textvariable=self.audio_narrador, width=500).grid(row=row, column=0, sticky='we', padx=8)
        ctk.CTkButton(left_frame, text="Procurar...", command=lambda: self._pick_file(self.audio_narrador, [("Áudio", "*.mp3;*.wav;*.aac;*.m4a;*.flac;*.ogg"), ("Todos", "*.*")])).grid(row=row, column=1, sticky='w'); row+=1

        # 2. Capa e Logo (Oculto - Fase 15 - Agora integrado aos Templates Visuais)
        # A lógica permanece no background caso arquivos antigos dependam disso, 
        # mas a interface fica limpa.
        # 3. Masterização e Cor
        ctk.CTkLabel(left_frame, text="3. MASTERIZAÇÃO E COR").grid(row=row, column=0, sticky='w', pady=(10,4)); row+=1
        f_vols = ctk.CTkFrame(left_frame)
        f_vols.grid(row=row, column=0, columnspan=2, sticky='we', padx=8); row+=1
        
        ctk.CTkLabel(f_vols, text="Música (dB):").grid(row=0, column=0, sticky='w')
        ttk.Scale(f_vols, from_=-60, to=20, variable=self.vol_musica).grid(row=0, column=1, sticky='we', padx=(5,0))
        ttk.Spinbox(f_vols, from_=-60, to=20, textvariable=self.vol_musica, width=4).grid(row=0, column=2, padx=(2,10))
        
        ctk.CTkLabel(f_vols, text="Narrador (dB):").grid(row=0, column=3, sticky='w')
        ttk.Scale(f_vols, from_=-60, to=20, variable=self.vol_narrador).grid(row=0, column=4, sticky='we', padx=(5,0))
        ttk.Spinbox(f_vols, from_=-60, to=20, textvariable=self.vol_narrador, width=4).grid(row=0, column=5, padx=(2,10))
        
        ctk.CTkLabel(f_vols, text="Cenas (dB):").grid(row=0, column=6, sticky='w')
        ttk.Scale(f_vols, from_=-60, to=20, variable=self.vol_video).grid(row=0, column=7, sticky='we', padx=(5,0))
        ttk.Spinbox(f_vols, from_=-60, to=20, textvariable=self.vol_video, width=4).grid(row=0, column=8, padx=(2,0))

        ctk.CTkSwitch(f_vols, text="Coloração Vívida:", variable=self.var_coloracao).grid(row=1, column=0, sticky='w', pady=8)
        ctk.CTkLabel(f_vols, text="Nível (1-10):").grid(row=1, column=1, sticky='w')
        ttk.Spinbox(f_vols, from_=1, to=10, textvariable=self.nivel_cor, width=5).grid(row=1, column=2, sticky='w')

        # 4. Legendas Estilo DarkFacil
        ctk.CTkLabel(left_frame, text="4. LEGENDAS VOZ & KARAOKÊ (DarkFacil Clone)").grid(row=row, column=0, sticky='w', pady=(10,4)); row+=1
        f_sub = ctk.CTkFrame(left_frame)
        f_sub.grid(row=row, column=0, columnspan=2, sticky='we', padx=8); row+=1
        
        ctk.CTkSwitch(f_sub, text="Gerar & Queimar legendas Karaokê", variable=self.var_legenda).grid(row=0, column=0, columnspan=4, sticky='w', pady=2)
        
        f_prof = ctk.CTkFrame(f_sub)
        f_prof.grid(row=1, column=0, columnspan=4, sticky='we', pady=(5,10))
        ctk.CTkLabel(f_prof, text="📁 Carregar Perfil:").pack(side='left', padx=(0,5))
        self.var_perfil_legenda = tk.StringVar()
        self.cb_perfil_legenda = ctk.CTkOptionMenu(f_prof, variable=self.var_perfil_legenda, width=250)
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
        
        temas = get_temas_disponiveis()
        ctk.CTkLabel(f_sub, text="Tema:").grid(row=3, column=2, sticky='w')
        self.ctrl_sub_theme = ctk.CTkOptionMenu(f_sub, variable=self.sub_theme, values=temas, width=150)
        self.ctrl_sub_theme.grid(row=3, column=3, sticky='w')

        ctk.CTkLabel(f_sub, text="Tamanho (px):").grid(row=4, column=0, sticky='w')
        self.ctrl_sub_size = ttk.Spinbox(f_sub, from_=10, to=200, textvariable=self.sub_size, width=5)
        self.ctrl_sub_size.grid(row=4, column=1, sticky='w', padx=5)
        
        ctk.CTkLabel(f_sub, text="MargemV (px):").grid(row=4, column=2, sticky='w')
        self.ctrl_sub_margin_v = ttk.Spinbox(f_sub, from_=0, to=500, textvariable=self.sub_margin_v, width=5)
        self.ctrl_sub_margin_v.grid(row=4, column=3, sticky='w')

        efeitos = ["Nenhum", "Pulo (Pop)", "Balanço", "Giro Zoom", "Tremor"]
        ctk.CTkLabel(f_sub, text="Efeito Animação:").grid(row=5, column=0, sticky='w')
        self.ctrl_sub_effect = ctk.CTkOptionMenu(f_sub, variable=self.sub_effect, values=efeitos, width=150)
        self.ctrl_sub_effect.grid(row=5, column=1, sticky='w', padx=5)

        # Mapa de Temas do Podcast (gerado pela Aba Podcast)
        f_mapa_eb = ctk.CTkFrame(f_sub)
        f_mapa_eb.grid(row=6, column=0, columnspan=4, sticky='we', pady=(8, 2))
        ctk.CTkLabel(f_mapa_eb, text="🎨 Mapa de Cores (Podcast):", font=("Segoe UI", 9, "bold")).pack(side='left')
        ctk.CTkEntry(f_mapa_eb, textvariable=self.mapa_temas_path, width=300).pack(side='left', padx=5)
        ctk.CTkButton(f_mapa_eb, text="📂 Carregar",
                   command=lambda: self._pick_file(self.mapa_temas_path,
                   [("Mapa de Temas JSON", "*.json"), ("Todos", "*.*")])).pack(side='left')
        ctk.CTkButton(f_mapa_eb, text="✖ Limpar",
                   command=lambda: [self.mapa_temas_path.set(''), self._toggle_tema_ctrl_eb()]).pack(side='left', padx=3)
        ctk.CTkLabel(f_mapa_eb, text="(Opcional - gerado pela Aba de Podcast)",
                  text_color="gray", font=("Segoe UI", 8)).pack(side='left', padx=5)
        self.mapa_temas_path.trace_add('write', lambda *_: self._toggle_tema_ctrl_eb())

        # 5. Extras: Saida
        ctk.CTkLabel(left_frame, text="5. DIRETÓRIO DE SAÍDA").grid(row=row, column=0, sticky='w', pady=(10,4)); row+=1
        f_files = ctk.CTkFrame(left_frame)
        f_files.grid(row=row, column=0, columnspan=2, sticky='we', padx=8); row+=1

        ctk.CTkLabel(f_files, text="Pasta Saída:").grid(row=3, column=0, sticky='w', pady=8)
        ctk.CTkEntry(f_files, textvariable=self.saida_dir, width=300).grid(row=3, column=1, sticky='we')
        ctk.CTkButton(f_files, text="Abrir", command=lambda: self._pick_dir(self.saida_dir)).grid(row=3, column=2)
        
        ctk.CTkLabel(f_files, text="Nome Vídeo:").grid(row=4, column=0, sticky='w')
        ctk.CTkEntry(f_files, textvariable=self.nome_final, width=300).grid(row=4, column=1, sticky='we')

        # Formato do vídeo (H/V) — antes do perfil
        ctk.CTkLabel(left_frame, text="FORMATO DO VÍDEO").grid(row=row, column=0, sticky='w', pady=(10,2)); row+=1
        f_fmt = ctk.CTkFrame(left_frame)
        f_fmt.grid(row=row, column=0, columnspan=2, sticky='we', padx=8, pady=2); row+=1
        ttk.Radiobutton(f_fmt, text="📱 Vertical (1080x1920)",  variable=self.video_format, value='vertical').pack(side='left', padx=(0,20))
        ttk.Radiobutton(f_fmt, text="🖥️ Horizontal (1920x1080)", variable=self.video_format, value='horizontal').pack(side='left')

        # Música de fundo
        ctk.CTkLabel(left_frame, text="MÚSÍCA DE FUNDO (Opcional):").grid(row=row, column=0, sticky='w', pady=(8,2)); row+=1
        f_mus = ctk.CTkFrame(left_frame)
        f_mus.grid(row=row, column=0, columnspan=2, sticky='we', padx=8, pady=2); row+=1
        ctk.CTkEntry(f_mus, textvariable=self.musica, width=400).pack(side='left', fill='x', expand=True)
        ctk.CTkButton(f_mus, text="Arquivo", command=lambda: self._pick_file(self.musica, [("Música", "*.mp3;*.wav;*.aac"), ("Todos", "*.*")])).pack(side='left', padx=(5,0))

        # 6. PERFIL DE TEMPLATE E VARIÁVEIS
        ctk.CTkLabel(left_frame, text="6. PERFIL DE TEMPLATE E VARIÁVEIS").grid(row=row, column=0, sticky='w', pady=(12,4)); row+=1
        f_ov = ctk.CTkFrame(left_frame)
        f_ov.grid(row=row, column=0, columnspan=2, sticky='we', padx=8); row+=1
        
        ctk.CTkLabel(f_ov, text="Selecione o Perfil:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky='w')
        
        self.combo_perfil = ctk.CTkOptionMenu(f_ov, variable=self.perfil_selecionado, width=250)
        self.combo_perfil.grid(row=0, column=1, sticky='we', padx=2)
        ctk.CTkButton(f_ov, text="🔄 Recarregar", command=self._atualizar_lista_perfis).grid(row=0, column=2, padx=2)
        
        def add_layer_ui(parent, title, path_var, r, is_folder=False):
            ctk.CTkLabel(parent, text=title).grid(row=r, column=0, sticky='w', pady=2)
            ctk.CTkEntry(parent, textvariable=path_var, width=400).grid(row=r, column=1, columnspan=2, sticky='we', padx=2, pady=2)
            if is_folder:
                ctk.CTkButton(parent, text="Pasta", command=lambda: self._pick_dir(path_var)).grid(row=r, column=3, pady=2)
            else:
                ctk.CTkButton(parent, text="Arquivo", command=lambda: self._pick_file(path_var, [("Media", "*.mp4;*.mov;*.webm;*.png;*.webp;*.jpg"), ("Todos", "*.*")])).grid(row=r, column=3, pady=2)

        # Apenas as variáveis principais que podem mudar a cada vídeo:
        # Vídeo Base fica exclusivamente na lista direita (Treeview)
        add_layer_ui(f_ov, "1. Narrador (Avatar):",        self.lay2_narrador_path, 1)
        add_layer_ui(f_ov, "2. Tag / Frente:",             self.lay3_frente_path,  2)
        add_layer_ui(f_ov, "3. Moldura (Diretório):",      self.lay4_moldura_dir,  3, is_folder=True)
        
        self._atualizar_lista_perfis()

        left_frame.columnconfigure(0, weight=1)

        # Botão GERAR e Progresso
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(left_frame, variable=self.progress_var, maximum=100)
        self.progressbar.grid(row=row, column=0, columnspan=2, sticky='we', padx=8, pady=(10,0)); row+=1

        self.btn_gerar = ctk.CTkButton(left_frame, text="🚀 GERAR VÍDEO COMPLETO", command=self._gerar_video)
        self.btn_gerar.grid(row=row, column=0, columnspan=2, pady=(10,20), ipadx=20, ipady=10); row+=1
        
        self.status = tk.StringVar(value="Pronto.")
        ctk.CTkLabel(left_frame, textvariable=self.status, font=("Segoe UI", 12, "bold"), text_color="#00FF00").grid(row=row, column=0, columnspan=2, pady=5); row+=1

        # --- RIGHT FRAME (Videos List with THUMBNAILS) ---
        f_title_right = ctk.CTkFrame(right_frame)
        f_title_right.pack(fill='x', pady=5)
        ctk.CTkLabel(f_title_right, text="Vídeos Base (Com Thumbnails)").pack(side='left', anchor='w')
        ctk.CTkSwitch(f_title_right, text="Em Loop (Repetir Lista)", variable=self.base_loop).pack(side='right', padx=10)
        
        btn_frame = ctk.CTkFrame(right_frame)
        btn_frame.pack(fill='x', pady=5)
        
        ctk.CTkButton(btn_frame, text="+ Adicionar", command=self._add_videos).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="- Remover", command=self._remove_videos).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="Cima", command=self._move_up).pack(side='left', padx=2)
        ctk.CTkButton(btn_frame, text="Baixo", command=self._move_down).pack(side='left', padx=2)
        
        # Estilo para suportar a altura da thumbnail
        style = ttk.Style()
        style.configure("Thumb.Treeview", rowheight=90)
        
        # Use Treeview to support images and text
        self.tree = ttk.Treeview(right_frame, columns=("path"), show="tree")
        self.tree.pack(fill='both', expand=True)
        scroll_tree = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        scroll_tree.pack(side=tk.RIGHT, fill='y')
        self.tree.config(yscrollcommand=scroll_tree.set)
        
        self._carregar_cache()
        self._setup_auto_save()
        
        if self.config_manager:
            self._carregar_perfis_ui()
            
    def _carregar_perfis_ui(self):
        if not self.config_manager: return
        perfis = self.config_manager.get("perfis_legenda", {})
        self.cb_perfil_legenda['values'] = ["[Personalizado]"] + list(perfis.keys())

    def _toggle_tema_ctrl_eb(self):
        if hasattr(self, 'cb_perfil_legenda'):
            state = 'disabled' if self.mapa_temas_path.get().strip() else 'normal'
            for ctrl in [self.cb_perfil_legenda, self.ctrl_sub_font, self.ctrl_sub_words, 
                         self.ctrl_sub_pos, self.ctrl_sub_theme, self.ctrl_sub_size, 
                         self.ctrl_sub_margin_v, self.ctrl_sub_effect]:
                if hasattr(ctrl, 'config'):
                    try:
                        ctrl.config(state=state)
                    except Exception:
                        pass

    def _aplicar_perfil_legenda(self, event=None):
        name = self.var_perfil_legenda.get()
        if not name or not self.config_manager: return
        
        def set_state(st):
            for c in [self.ctrl_sub_font, self.ctrl_sub_words, self.ctrl_sub_pos,
                      self.ctrl_sub_theme, self.ctrl_sub_size, self.ctrl_sub_margin_v,
                      self.ctrl_sub_effect]:
                if hasattr(self, 'ctrl_sub_font'):
                    try:
                        c.config(state=st)
                    except Exception:
                        pass
                    
        if name == "[Personalizado]":
            set_state("normal")
            return
            
        perfis = self.config_manager.get("perfis_legenda", {})
        if name in perfis:
            p = perfis[name]
            self.sub_font.set(p.get("font", "Bangers"))
            self.sub_words.set(p.get("words", 5))
            self.sub_pos.set(p.get("pos", "meio baixo"))
            self.sub_theme.set(p.get("theme", "amarelo vermelho"))
            self.sub_size.set(p.get("size", 100))
            self.sub_margin_v.set(p.get("margin_v", 150))
            self.sub_effect.set(p.get("effect", "Pulo (Pop)"))
            self._salvar_cache()
            set_state("disabled")

    def _atualizar_lista_perfis(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tpl_dir = os.path.join(base_dir, "perfis_templates")
        if not os.path.exists(tpl_dir): return
        
        perfis = [f.replace('.json', '') for f in os.listdir(tpl_dir) if f.endswith('.json')]
        self.combo_perfil['values'] = perfis

    def _setup_auto_save(self):
        vars_to_trace = [
            self.capa, self.logo, self.logo_scale, self.logo_x, self.logo_y, self.musica, 
            self.vol_musica, self.vol_narrador, self.vol_video,
            self.var_coloracao, self.nivel_cor, self.var_legenda,
            self.vinhetas_dir, self.saida_dir,
            self.sub_font, self.sub_words, self.sub_pos, self.sub_theme, self.sub_size, self.sub_margin_v, self.sub_effect,
            self.perfil_selecionado, self.video_format, self.lay0_bg_path, self.lay1_fundo_path, self.lay2_narrador_path,
            self.lay3_frente_path, self.lay4_moldura_dir, self.lay5_extra_path
        ]
        for v in vars_to_trace:
            v.trace_add('write', lambda *args: self._salvar_cache())

    def _salvar_cache(self):
        data = {
            'capa': self.capa.get(), 'logo': self.logo.get(),
            'logo_scale': self.logo_scale.get(), 'logo_x': self.logo_x.get(), 'logo_y': self.logo_y.get(),
            'musica': self.musica.get(), 'vol_musica': self.vol_musica.get(),
            'vol_narrador': self.vol_narrador.get(), 'vol_video': self.vol_video.get(),
            'var_coloracao': self.var_coloracao.get(), 'nivel_cor': self.nivel_cor.get(),
            'var_legenda': self.var_legenda.get(), 'vinhetas_dir': self.vinhetas_dir.get(),
            'saida_dir': self.saida_dir.get(),
            'sub_font': self.sub_font.get(), 'sub_words': self.sub_words.get(),
            'sub_pos': self.sub_pos.get(), 'sub_theme': self.sub_theme.get(),
            'sub_size': self.sub_size.get(), 'sub_margin_v': self.sub_margin_v.get(), 'sub_effect': self.sub_effect.get(),
            'perfil_selecionado': self.perfil_selecionado.get(),
            'video_format': self.video_format.get(),
            'lay0_bg_path': self.lay0_bg_path.get(), 'lay0_scale': self.lay0_scale.get(), 'lay0_x': self.lay0_x.get(), 'lay0_y': self.lay0_y.get(), 'lay0_random': self.lay0_random.get(),
            'base_scale': self.base_scale.get(), 'base_x': self.base_x.get(), 'base_y': self.base_y.get(),
            'lay1_fundo_path': self.lay1_fundo_path.get(), 'lay1_scale': self.lay1_scale.get(), 'lay1_x': self.lay1_x.get(), 'lay1_y': self.lay1_y.get(), 'lay1_chroma': self.lay1_chroma.get(), 'lay1_random': self.lay1_random.get(),
            'lay2_narrador_path': self.lay2_narrador_path.get(), 'lay2_scale': self.lay2_scale.get(), 'lay2_x': self.lay2_x.get(), 'lay2_y': self.lay2_y.get(), 'lay2_chroma': self.lay2_chroma.get(), 'lay2_random': self.lay2_random.get(),
            'lay3_frente_path': self.lay3_frente_path.get(), 'lay3_scale': self.lay3_scale.get(), 'lay3_x': self.lay3_x.get(), 'lay3_y': self.lay3_y.get(), 'lay3_chroma': self.lay3_chroma.get(), 'lay3_random': self.lay3_random.get(),
            'lay4_moldura_dir': self.lay4_moldura_dir.get(), 'lay4_random': self.lay4_random.get(),
            'lay5_extra_path': self.lay5_extra_path.get(), 'lay5_scale': self.lay5_scale.get(), 'lay5_x': self.lay5_x.get(), 'lay5_y': self.lay5_y.get(), 'lay5_chroma': self.lay5_chroma.get(), 'lay5_random': self.lay5_random.get()
        }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except: pass

    def _carregar_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.capa.set(data.get('capa', ''))
                self.logo.set(data.get('logo', ''))
                self.logo_scale.set(data.get('logo_scale', 100))
                self.logo_x.set(data.get('logo_x', 20))
                self.logo_y.set(data.get('logo_y', 20))
                self.musica.set(data.get('musica', ''))
                self.vol_musica.set(data.get('vol_musica', -12))
                self.vol_narrador.set(data.get('vol_narrador', 5))
                self.vol_video.set(data.get('vol_video', -5))
                self.var_coloracao.set(data.get('var_coloracao', True))
                self.nivel_cor.set(data.get('nivel_cor', 3))
                self.var_legenda.set(data.get('var_legenda', True))
                self.vinhetas_dir.set(data.get('vinhetas_dir', ''))
                self.saida_dir.set(data.get('saida_dir', ''))
                
                self.sub_font.set(data.get('sub_font', 'Bangers'))
                self.sub_words.set(data.get('sub_words', 5))
                self.sub_pos.set(data.get('sub_pos', 'meio baixo'))
                self.sub_theme.set(data.get('sub_theme', 'amarelo vermelho'))
                self.sub_size.set(data.get('sub_size', 100))
                self.sub_margin_v.set(data.get('sub_margin_v', 150))
                self.sub_effect.set(data.get('sub_effect', 'Pulo (Pop)'))
                
                self.perfil_selecionado.set(data.get('perfil_selecionado', ''))
                self.video_format.set(data.get('video_format', 'vertical'))
                
                self.lay0_bg_path.set(data.get('lay0_bg_path', ''))
                self.lay0_scale.set(data.get('lay0_scale', 100))
                self.lay0_x.set(data.get('lay0_x', 0))
                self.lay0_y.set(data.get('lay0_y', 0))
                self.lay0_random.set(data.get('lay0_random', True))

                self.base_scale.set(data.get('base_scale', 100))
                self.base_x.set(data.get('base_x', 0))
                self.base_y.set(data.get('base_y', 0))
                
                self.lay1_fundo_path.set(data.get('lay1_fundo_path', ''))
                self.lay1_scale.set(data.get('lay1_scale', 100))
                self.lay1_x.set(data.get('lay1_x', 0))
                self.lay1_y.set(data.get('lay1_y', 0))
                self.lay1_chroma.set(data.get('lay1_chroma', False))
                self.lay1_random.set(data.get('lay1_random', False))

                self.lay2_narrador_path.set(data.get('lay2_narrador_path', ''))
                self.lay2_scale.set(data.get('lay2_scale', 30))
                self.lay2_x.set(data.get('lay2_x', 50))
                self.lay2_y.set(data.get('lay2_y', 1500))
                self.lay2_chroma.set(data.get('lay2_chroma', True))
                self.lay2_random.set(data.get('lay2_random', False))

                self.lay3_frente_path.set(data.get('lay3_frente_path', ''))
                self.lay3_scale.set(data.get('lay3_scale', 30))
                self.lay3_x.set(data.get('lay3_x', 50))
                self.lay3_y.set(data.get('lay3_y', 1500))
                self.lay3_chroma.set(data.get('lay3_chroma', True))
                self.lay3_random.set(data.get('lay3_random', False))

                self.lay4_moldura_dir.set(data.get('lay4_moldura_dir', ''))
                self.lay4_random.set(data.get('lay4_random', True))

                self.lay5_extra_path.set(data.get('lay5_extra_path', ''))
                self.lay5_scale.set(data.get('lay5_scale', 50))
                self.lay5_x.set(data.get('lay5_x', 50))
                self.lay5_y.set(data.get('lay5_y', 50))
                self.lay5_chroma.set(data.get('lay5_chroma', False))
                self.lay5_random.set(data.get('lay5_random', False))
                
            except: pass

    def _pick_file(self, var, types):
        path = filedialog.askopenfilename(filetypes=types)
        if path: var.set(path)
        
    def _pick_dir(self, var):
        path = filedialog.askdirectory()
        if path: var.set(path)

    def _extract_thumb(self, video_path):
        thumb_path = os.path.join(os.path.dirname(video_path), "thumb_cache_" + os.path.basename(video_path) + ".jpg")
        if not os.path.exists(thumb_path):
            cmd = ['ffmpeg', '-y', '-i', video_path, '-ss', '00:00:01', '-vframes', '1', '-s', '160x90', thumb_path]
            subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if os.path.exists(thumb_path) and PIL_AVAILABLE:
            img = Image.open(thumb_path)
            img.thumbnail((160, 90))
            photo = ImageTk.PhotoImage(img)
            return photo
        return None

    def _add_videos(self):
        paths = filedialog.askopenfilenames(filetypes=[("Vídeos", "*.mp4;*.mov;*.mkv;*.avi")])
        for p in paths:
            if p not in self.video_paths:
                self.video_paths.append(p)
                item_id = self.tree.insert("", tk.END, text=" " + os.path.basename(p), values=(p,))
                
                # Load thumb async
                def load_thumb(path, iid):
                    photo = self._extract_thumb(path)
                    if photo:
                        self.thumbnail_cache[path] = photo
                        # update treeview image in main thread
                        self.after(0, lambda: self.tree.item(iid, image=self.thumbnail_cache[path]))
                        
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
                # update array
                self.video_paths.insert(idx - 1, self.video_paths.pop(idx))
                
    def _move_down(self):
        items = self.tree.selection()
        for item in reversed(items):
            idx = self.tree.index(item)
            if idx < len(self.tree.get_children()) - 1:
                self.tree.move(item, self.tree.parent(item), idx + 1)
                # update array
                self.video_paths.insert(idx + 1, self.video_paths.pop(idx))

    def _probe_duration(self, filepath):
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filepath]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(r.stdout.strip())
        except: return 0.0

    def _gerar_video(self):
        audio_narrador = self.audio_narrador.get()
        videos = self.video_paths
        saida_dir = self.saida_dir.get()
        nome_final = self.nome_final.get()
        capa = self.capa.get()
        logo = self.logo.get()
        musica = self.musica.get()
        vinhetas_dir = self.vinhetas_dir.get()
        
        if not audio_narrador or not os.path.exists(audio_narrador):
            messagebox.showerror("Erro", "Selecione o Áudio do Narrador válido.")
            return
        if not videos:
            messagebox.showerror("Erro", "Adicione pelo menos um vídeo base.")
            return
        if not saida_dir:
            messagebox.showerror("Erro", "Selecione a pasta de saída.")
            return
        if self.var_legenda.get() and not WHISPER_AVAILABLE:
            messagebox.showerror("Erro", "A biblioteca whisper não está instalada no Python!")
            return

        # 0. Sanitizar caminhos de arquivos (remover aspas duplas do Windows)
        for attr_name in dir(self):
            if 'path' in attr_name or 'dir' in attr_name or 'audio' in attr_name or 'musica' in attr_name or 'fundo' in attr_name or 'narrador' in attr_name or 'frente' in attr_name:
                attr = getattr(self, attr_name)
                if hasattr(attr, 'get') and hasattr(attr, 'set'):
                    try:
                        val = attr.get()
                        if isinstance(val, str) and ('"' in val or "'" in val):
                            attr.set(val.strip().strip('"').strip("'"))
                    except Exception:
                        pass
        
        self.btn_gerar.config(state='disabled')
        
        def worker():
            def set_status(text, progress):
                self.after(0, lambda: self.status.set(text))
                self.after(0, lambda: self.progress_var.set(progress))
                
            try:
                set_status("Carregando Perfil de Template...", 2)
                
                layers = {}
                
                # Injetor de Dependência JSON (Fase 7)
                perfil_nome = self.perfil_selecionado.get()
                if perfil_nome:
                    base_dir_p = os.path.dirname(os.path.abspath(__file__))
                    perfil_file = os.path.join(base_dir_p, "perfis_templates", f"{perfil_nome}.json")
                    if os.path.exists(perfil_file):
                        try:
                            with open(perfil_file, 'r', encoding='utf-8') as f:
                                pd = json.load(f)
                            
                            layers = pd.get('layers', {})
                            
                            def injetar_layer(layer_id, scale_var, x_var, y_var, chroma_var, random_var, path_var):
                                ld = layers.get(layer_id)
                                if not ld: return
                                
                                # Se a UI estiver vazia, e o JSON tem um arquivo padrão salvo (ex: moldura fixa), a gente puxa do JSON
                                if not path_var.get().strip() and ld.get('path'):
                                    path_var.set(ld.get('path'))
                                
                                # Sobrescreve as matemáticas ocultas da Classe
                                if scale_var is not None: scale_var.set(ld.get('scale', 100))
                                if x_var is not None: x_var.set(ld.get('x', 0))
                                if y_var is not None: y_var.set(ld.get('y', 0))
                                
                                # Se a camada foi "ocultada" (desligada) no Web UI, limpamos o path pra o FFmpeg ignorar!
                                if ld.get('visible') is False:
                                    path_var.set('')
                                
                                if chroma_var is not None: chroma_var.set(ld.get('chroma', False))
                                if random_var is not None: random_var.set(ld.get('random', False))
                            
                            self.video_format.set(pd.get('format', 'vertical'))
                            
                            # Injeta as regras do Web UI -> nas variáveis internas
                            injetar_layer('lay0_bg', self.lay0_scale, self.lay0_x, self.lay0_y, None, self.lay0_random, self.lay0_bg_path)
                            injetar_layer('base', self.base_scale, self.base_x, self.base_y, None, None, tk.StringVar())
                            injetar_layer('lay1_fundo', self.lay1_scale, self.lay1_x, self.lay1_y, self.lay1_chroma, self.lay1_random, self.lay1_fundo_path)
                            injetar_layer('lay2_narrador', self.lay2_scale, self.lay2_x, self.lay2_y, self.lay2_chroma, self.lay2_random, self.lay2_narrador_path)
                            injetar_layer('lay3_frente', self.lay3_scale, self.lay3_x, self.lay3_y, self.lay3_chroma, self.lay3_random, self.lay3_frente_path)
                            injetar_layer('lay4_moldura', None, None, None, None, self.lay4_random, self.lay4_moldura_dir)
                            injetar_layer('lay5_extra', self.lay5_scale, self.lay5_x, self.lay5_y, self.lay5_chroma, self.lay5_random, self.lay5_extra_path)
                            
                        except Exception as e:
                            print("Erro ao carregar perfil JSON:", e)

                set_status("Analisando durações...", 5)
                
                audio_dur = self._probe_duration(audio_narrador)
                if audio_dur <= 0: raise Exception("Não foi possível ler a duração do áudio.")
                    
                target_per_video = audio_dur / len(videos)
                temp_dir = os.path.join(saida_dir, "temp_render_basico")
                os.makedirs(temp_dir, exist_ok=True)
                
                srt_path = ""
                if self.var_legenda.get():
                    set_status("Transcrevendo áudio com Whisper (Karaokê)...", 10)
                    model = whisper.load_model("base")
                    result = model.transcribe(audio_narrador, fp16=False, language='pt', word_timestamps=True)
                    srt_path = os.path.join(temp_dir, 'auto_karaoke.ass')
                    
                    # --- Carregar Mapa de Temas do Podcast ---
                    _voice_color_map_eb = None
                    _mapa_file_eb = self.mapa_temas_path.get().strip()
                    if _mapa_file_eb and os.path.exists(_mapa_file_eb):
                        try:
                            with open(_mapa_file_eb, 'r', encoding='utf-8') as _mf:
                                _voice_color_map_eb = json.load(_mf)
                        except: pass
                    
                    perfis_dic_completo = self.config_manager.get("perfis_legenda", {}) if self.config_manager else {}
                    
                    generate_karaoke_ass(
                        result, srt_path,
                        font=self.sub_font.get(),
                        size=self.sub_size.get(),
                        theme=self.sub_theme.get(),
                        pos=self.sub_pos.get(),
                        margin_v=self.sub_margin_v.get(),
                        words_per_block=self.sub_words.get(),
                        video_format=self.video_format.get(),
                        effect=self.sub_effect.get(),
                        voice_color_map=_voice_color_map_eb,
                        perfis_personagem=perfis_dic_completo
                    )
                
                processed_videos = []
                for i, vid in enumerate(videos):
                    set_status(f"Processando vídeo {i+1}/{len(videos)}...", 30 + (40 * (i/len(videos))))
                    
                    orig_dur = self._probe_duration(vid)
                    if orig_dur <= 0.5: orig_dur = 1.0
                    
                    speed_factor = target_per_video / orig_dur
                    atempo_chain = get_atempo_chain(speed_factor)
                    out_vid = os.path.join(temp_dir, f"vid_{i}.mp4")
                    
                    inputs = ['-i', vid]
                    v_filters = []
                    v_filters.append(f"setpts=({speed_factor:.4f})*PTS")
                    if self.var_coloracao.get():
                        n = self.nivel_cor.get()
                        sat = 1.0 + (n * 0.1)
                        con = 1.0 + (n * 0.02)
                        v_filters.append(f"eq=saturation={sat:.2f}:contrast={con:.2f}")
                        
                    if self.video_format.get() == 'horizontal':
                        v_filters.append("scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black")
                    else:
                        v_filters.append("scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black")
                    
                    fc = f"[0:v]{','.join(v_filters)}[vbase];"
                    
                    if logo and os.path.exists(logo):
                        inputs.extend(['-i', logo])
                        scale = self.logo_scale.get() / 100.0
                        # scale the logo proportionally
                        fc += f"[1:v]scale=iw*{scale}:ih*{scale}[vlogo];"
                        lx = self.logo_x.get()
                        ly = self.logo_y.get()
                        fc += f"[vbase][vlogo]overlay=W-w-{lx}:H-h-{ly}[vout];"
                        map_v = "[vout]"
                    else:
                        fc += "[vbase]copy[vout];"
                        map_v = "[vout]"
                        
                    a_filters = f"[0:a]{atempo_chain}[aout]"
                    fc += a_filters
                    
                    cmd_part = [
                        'ffmpeg', '-y'
                    ] + inputs + [
                        '-filter_complex', fc,
                        '-map', map_v, '-map', '[aout]?', 
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.2',
                        '-preset', 'fast', '-crf', '22',
                        '-c:a', 'aac', '-b:a', '192k', '-r', '30', out_vid
                    ]
                    subprocess.run(cmd_part, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    processed_videos.append(out_vid)
                set_status("Aplicando Camadas, Legendas e Masterizando áudio (Pipeline Único)...", 75)
                
                list_txt = os.path.join(temp_dir, "list_videos.txt")
                with open(list_txt, 'w', encoding='utf-8') as f:
                    for p in processed_videos: f.write(f"file '{p.replace(chr(92), '/')}'\n")
                        
                video_only_concat = os.path.join(temp_dir, "videos_concat.mp4")
                cmd_concat_v = [
                    'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_txt, '-c', 'copy', video_only_concat
                ]
                subprocess.run(cmd_concat_v, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                mix_out = os.path.join(temp_dir, "mix_final.mp4")
                
                ffmpeg_cmd = ['ffmpeg', '-y']
                filter_complex = ""
                import random
                _probe_cache = {}
                def get_input_args(path, is_random):
                    ext = path.lower().split('.')[-1]
                    is_img = ext in ['png', 'jpg', 'jpeg', 'webp', 'gif']
                    args = []
                    
                    if is_random and not is_img:
                        if path not in _probe_cache:
                            _probe_cache[path] = self._probe_duration(path)
                        vdur = _probe_cache[path]
                        
                        if vdur > audio_dur:
                            st = random.uniform(0, vdur - audio_dur)
                            args.extend(['-ss', f"{st:.2f}"])
                            
                    if is_img:
                        args.extend(['-loop', '1', '-framerate', '30', '-i', path])
                    else:
                        args.extend(['-stream_loop', '-1', '-i', path])
                    return args

                input_idx = 0
                curr_v = ""

                # Check if BG is provided
                bg_path = self.lay0_bg_path.get()
                if bg_path and os.path.exists(bg_path):
                    ffmpeg_cmd.extend(get_input_args(bg_path, self.lay0_random.get()))
                    sc = self.lay0_scale.get()
                    filter_complex += f"[{input_idx}:v]scale=iw*({sc}/100):ih*({sc}/100)[bg]; "
                    curr_v = "bg"
                    input_idx += 1

                # Input: Base Video (Lista)
                if self.base_loop.get():
                    ffmpeg_cmd.extend(['-stream_loop', '-1', '-i', video_only_concat])
                else:
                    ffmpeg_cmd.extend(['-i', video_only_concat])
                
                base_idx = input_idx
                input_idx += 1
                
                b_sc = self.base_scale.get()
                if b_sc != 100:
                    filter_complex += f"[{base_idx}:v]scale=iw*({b_sc}/100):ih*({b_sc}/100)[base_scaled]; "
                    base_v = "base_scaled"
                else:
                    base_v = f"{base_idx}:v"
                    
                if curr_v:
                    # We have a BG, overlay base video on top!
                    bx, by = self.base_x.get(), self.base_y.get()
                    filter_complex += f"[{curr_v}][{base_v}]overlay=x={bx}:y={by}:shortest=1[v_base_on_bg]; "
                    curr_v = "v_base_on_bg"
                else:
                    curr_v = base_v

                def add_layer(layer_id, path, scale_pct, x, y, chroma, is_random=False, fullscreen=False):
                    nonlocal curr_v, input_idx, filter_complex
                    if not path or not os.path.exists(path): return
                    
                    ffmpeg_cmd.extend(get_input_args(path, is_random))
                        
                    idx_str = f"{input_idx}:v"
                    ck = "colorkey=0x00FF00:0.3:0.2," if chroma else ""
                    if fullscreen:
                        if self.video_format.get() == 'horizontal': sc = "scale=1920:1080"
                        else: sc = "scale=1080:1920"
                        x, y = 0, 0
                    else:
                        ld = layers.get(layer_id, {})
                        if ld.get('w') is not None and ld.get('h') is not None:
                            sc = f"scale={ld.get('w')}:{ld.get('h')}"
                        else:
                            sc = f"scale=iw*({scale_pct}/100):ih*({scale_pct}/100)"
                        
                    filter_complex += f"[{idx_str}]{ck}{sc}[lay{input_idx}]; "
                    filter_complex += f"[{curr_v}][lay{input_idx}]overlay=x={x}:y={y}:shortest=1[v{input_idx}]; "
                    curr_v = f"v{input_idx}"
                    input_idx += 1

                # Layer 1
                add_layer('lay1_fundo', self.lay1_fundo_path.get(), self.lay1_scale.get(), self.lay1_x.get(), self.lay1_y.get(), self.lay1_chroma.get(), self.lay1_random.get())
                # Layer 2
                add_layer('lay2_narrador', self.lay2_narrador_path.get(), self.lay2_scale.get(), self.lay2_x.get(), self.lay2_y.get(), self.lay2_chroma.get(), self.lay2_random.get())
                # Layer 3
                add_layer('lay3_frente', self.lay3_frente_path.get(), self.lay3_scale.get(), self.lay3_x.get(), self.lay3_y.get(), self.lay3_chroma.get(), self.lay3_random.get())
                
                # Layer 4 Moldura
                moldura_dir = self.lay4_moldura_dir.get()
                if moldura_dir and os.path.isdir(moldura_dir):
                    molduras = [os.path.join(moldura_dir, f) for f in os.listdir(moldura_dir) if f.lower().endswith(('.mov', '.mp4', '.webm', '.png'))]
                    if molduras:
                        add_layer('lay4_moldura', random.choice(molduras), 100, 0, 0, False, self.lay4_random.get(), fullscreen=True)
                        
                # Layer 5
                add_layer('lay5_extra', self.lay5_extra_path.get(), self.lay5_scale.get(), self.lay5_x.get(), self.lay5_y.get(), self.lay5_chroma.get(), self.lay5_random.get())
                
                # Processar camadas extras infinitas
                for key in sorted(layers.keys()):
                    if key.startswith('lay_extra_'):
                        ld = layers[key]
                        path = ld.get('path', '')
                        if path and ld.get('visible', True) is not False:
                            add_layer(key, path, 50, ld.get('x', 50), ld.get('y', 50), ld.get('chroma', True), ld.get('random', True))

                # Logo Anti-IA
                if self.logo.get() and os.path.exists(self.logo.get()):
                    ffmpeg_cmd.extend(['-loop', '1', '-framerate', '30', '-i', self.logo.get()])
                    scale_pct = self.logo_scale.get()
                    sc = f"scale=iw*({scale_pct}/100):ih*({scale_pct}/100)"
                    filter_complex += f"[{input_idx}:v]{sc}[lay{input_idx}]; "
                    mx = self.logo_x.get()
                    my = self.logo_y.get()
                    filter_complex += f"[{curr_v}][lay{input_idx}]overlay=x=W-w-{mx}:y=H-h-{my}:shortest=1[v{input_idx}]; "
                    curr_v = f"v{input_idx}"
                    input_idx += 1

                # Burn Subtitle (ASS)
                if self.var_legenda.get() and srt_path:
                    esc_ass = srt_path.replace('\\', '\\\\').replace(':', '\\:')
                    filter_complex += f"[{curr_v}]ass='{esc_ass}'[v_legenda]; "
                    curr_v = "v_legenda"

                # Audio Inputs
                audio_narrador_idx = input_idx
                ffmpeg_cmd.extend(['-i', audio_narrador])
                input_idx += 1

                musica_idx = None
                if musica and os.path.exists(musica):
                    musica_idx = input_idx
                    ffmpeg_cmd.extend(['-i', musica])
                    input_idx += 1
                
                a_mix = f"[{audio_narrador_idx}:a]volume={self.vol_narrador.get()}dB[a_n]; [{base_idx}:a]volume={self.vol_video.get()}dB[a_v]; "
                if musica_idx is not None:
                    a_mix += f"[{musica_idx}:a]volume={self.vol_musica.get()}dB[a_m]; [a_n][a_v][a_m]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[a_out]"
                else:
                    a_mix += "[a_n][a_v]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a_out]"

                if filter_complex:
                    filter_complex += a_mix
                else:
                    filter_complex = a_mix

                self.progress_var.set(85)
                
                # Arrumar o map caso curr_v não seja de um filter_complex
                map_v = f"[{curr_v}]" if not curr_v.startswith("0:v") and not curr_v.endswith(":v") else curr_v
                
                ffmpeg_cmd.extend([
                    '-filter_complex', filter_complex,
                    '-map', map_v, '-map', '[a_out]',
                    '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', mix_out
                ])
                try:
                    subprocess.run(ffmpeg_cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    with open(os.path.join(saida_dir, "erro_ffmpeg.txt"), "w") as f:
                        f.write(e.stderr)
                    messagebox.showerror("Erro FFmpeg", f"Ocorreu um erro no motor de vídeo.\nUm log foi salvo em:\n{os.path.join(saida_dir, 'erro_ffmpeg.txt')}\n\nDetalhes:\n{e.stderr[-500:]}")
                    raise Exception("Falha no FFmpeg.")
                
                set_status("Adicionando Capa e Vinheta...", 95)
                
                final_parts = []
                if capa and os.path.exists(capa):
                    seg_capa = os.path.join(temp_dir, "capa.mp4")
                    cmd_capa = [
                        'ffmpeg', '-y', '-loop', '1', '-i', capa,
                        '-f', 'lavfi', '-t', '0.0334', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
                        '-shortest', '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.2',
                        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', seg_capa
                    ]
                    subprocess.run(cmd_capa, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    final_parts.append(seg_capa)
                    
                final_parts.append(mix_out)
                
                if vinhetas_dir and os.path.isdir(vinhetas_dir):
                    vinhetas = [os.path.join(vinhetas_dir, f) for f in os.listdir(vinhetas_dir) if f.lower().endswith(('.mp4', '.mov'))]
                    if vinhetas:
                        vinheta_escolhida = random.choice(vinhetas)
                        seg_vinheta = os.path.join(temp_dir, "vinheta.mp4")
                        cmd_v = [
                            'ffmpeg', '-y', '-i', vinheta_escolhida,
                            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,fps=30',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.2',
                            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', seg_vinheta
                        ]
                        subprocess.run(cmd_v, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        final_parts.append(seg_vinheta)

                saida_final = os.path.join(saida_dir, f"{nome_final}.mp4")
                if len(final_parts) > 1:
                    list_final = os.path.join(temp_dir, "list_final.txt")
                    with open(list_final, 'w', encoding='utf-8') as f:
                        for p in final_parts: f.write(f"file '{p.replace(chr(92), '/')}'\n")
                            
                    cmd_concat_final = [
                        'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_final, '-c:v', 'copy', '-c:a', 'copy', saida_final
                    ]
                    subprocess.run(cmd_concat_final, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    import shutil
                    shutil.copy(mix_out, saida_final)
                    
                set_status("Sucesso! Vídeo concluído.", 100)
                self.after(0, lambda: messagebox.showinfo("Sucesso", f"Vídeo finalizado com sucesso:\n{saida_final}"))
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                set_status("Erro!", 0)
                self.after(0, lambda e=e: messagebox.showerror("Erro", str(e)))
            finally:
                self.after(0, lambda: self.btn_gerar.config(state='normal'))
                
        threading.Thread(target=worker, daemon=True).start()
