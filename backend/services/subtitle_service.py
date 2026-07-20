import os
import json
import wave
import subprocess
import re

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except Exception:
    VOSK_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

def hex_to_ass_color(hex_color):
    if not hex_color:
        return '&H00FFFFFF'
    hex_color = str(hex_color).strip()
    if hex_color.startswith('#') and len(hex_color) == 7:
        r = hex_color[1:3]
        g = hex_color[3:5]
        b = hex_color[5:7]
        return f'&H00{b}{g}{r}'
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
                    p_c = v.get('cor_primaria', '&H00FFFFFF')
                    s_c = v.get('cor_secundaria', p_c)
                    o_c = v.get('cor_borda', '&H00000000')
                    themes[k.lower()] = (p_c, s_c, o_c)
                    themes[k] = (p_c, s_c, o_c)
        except Exception as e:
            print(f'Erro lendo temas_legendas.json: {e}')
    if not themes:
        themes = {'padrao': ('&H00FFFFFF', '&H00000000', '&H00000000'), 'rosa neon': ('&H00FFFFFF', '&H00FF00FF', '&H00000000'), 'amarelo queimado': ('&H00FFFFFF', '&H0000FFFF', '&H00000000')}
    return themes.get(theme, themes.get(theme.lower(), ('&H00FFFFFF', '&H0000FFFF', '&H00000000')))

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
    return ['Padrão', 'Rosa Neon', 'Amarelo Queimado']

def _make_txt_ass(blk_ctx, anchor_ctx, pos_tag_ctx, p_color_ctx, s_color_ctx, o_color_ctx, effect_ctx, hidx=None):
    """Monta o texto de um evento Dialogue ASS com destaque karaoke na palavra hidx."""
    parts = [anchor_ctx, pos_tag_ctx]
    p_tag = f'&H{p_color_ctx[4:]}&' if p_color_ctx.startswith('&H') and len(p_color_ctx) == 10 else p_color_ctx
    s_tag = f'&H{s_color_ctx[4:]}&' if s_color_ctx.startswith('&H') and len(s_color_ctx) == 10 else s_color_ctx
    o_tag = f'&H{o_color_ctx[4:]}&' if o_color_ctx.startswith('&H') and len(o_color_ctx) == 10 else o_color_ctx
    for j, w in enumerate(blk_ctx):
        t = w['word'].strip().upper()
        w_color_override = p_tag
        if 'legenda_cor' in w and w['legenda_cor'] != '':
            c_str = w['legenda_cor'].lower()
            if 'vermelho' in c_str or 'red' in c_str or 'raiva' in c_str or ('agressivo' in c_str):
                w_color_override = '&H000000FF&'
            elif 'verde' in c_str or 'green' in c_str or 'esperança' in c_str:
                w_color_override = '&H0000FF00&'
            elif 'azul' in c_str or 'blue' in c_str or 'triste' in c_str or ('calmo' in c_str):
                w_color_override = '&H00FF0000&'
            elif 'amarelo' in c_str or 'yellow' in c_str or 'atenção' in c_str:
                w_color_override = '&H0000FFFF&'
            elif 'roxo' in c_str or 'purple' in c_str or 'misterioso' in c_str:
                w_color_override = '&H00FF0080&'
            elif 'rosa' in c_str or 'pink' in c_str or 'amor' in c_str:
                w_color_override = '&H00FF00FF&'
            elif 'laranja' in c_str or 'orange' in c_str or 'energia' in c_str:
                w_color_override = '&H00008CFF&'
            elif 'branco' in c_str or 'white' in c_str:
                w_color_override = '&H00FFFFFF&'
            elif 'preto' in c_str or 'black' in c_str:
                w_color_override = '&H00000000&'
            elif 'ciano' in c_str or 'cyan' in c_str:
                w_color_override = '&H00FFFF00&'
            elif 'magenta' in c_str:
                w_color_override = '&H00FF00FF&'
            elif 'lima' in c_str or 'lime' in c_str:
                w_color_override = '&H0000FF00&'
            elif 'ouro' in c_str or 'gold' in c_str:
                w_color_override = '&H0000D7FF&'
            elif 'cinza' in c_str or 'gray' in c_str:
                w_color_override = '&H00808080&'
            elif 'marrom' in c_str or 'brown' in c_str:
                w_color_override = '&H002A2AFF&'
        if j == hidx:
            c_tag = f'\\c{s_tag}\\3c{o_tag}'
            if effect_ctx == 'Pulo (Pop)':
                style = f'{{{c_tag}\\fscx112\\fscy112\\shad6\\bord3\\t(0,120,\\fscx100\\fscy100\\shad1\\bord2)}}'
            elif effect_ctx == 'Balanço':
                style = f'{{{c_tag}\\frz12\\t(0,50,\\frz-12)\\t(50,100,\\frz0)\\fscx100\\fscy100}}'
            elif effect_ctx == 'Giro Zoom':
                style = f'{{{c_tag}\\frz-20\\fscx120\\fscy120\\t(0,120,\\frz0\\fscx100\\fscy100)}}'
            elif effect_ctx == 'Tremor':
                style = f'{{{c_tag}\\frz4\\t(0,20,\\frz-4)\\t(20,40,\\frz4)\\t(40,60,\\frz-4)\\t(60,80,\\frz0)\\fscx100\\fscy100}}'
            elif effect_ctx == 'Neon':
                style = f'{{{c_tag}\\bord5\\shad0\\blur3\\t(0,100,\\bord2\\blur1)}}'
            elif effect_ctx == 'Flash':
                style = f'{{{c_tag}\\alpha&H00&\\t(0,60,\\alpha&H80&)\\t(60,120,\\alpha&H00&)\\fscx100\\fscy100}}'
            elif effect_ctx == 'Karate':
                style = f'{{{c_tag}\\frz-25\\fscx108\\fscy108\\t(0,80,\\frz8)\\t(80,140,\\frz0\\fscx100\\fscy100)}}'
            elif effect_ctx == 'Bomba':
                style = f'{{{c_tag}\\fscx118\\fscy118\\shad8\\t(0,80,\\fscx100\\fscy100\\shad2)}}'
            elif effect_ctx == 'Sublinha':
                style = f'{{{c_tag}\\bord0\\shad5\\blur0\\t(0,100,\\shad2)\\fscx100\\fscy100}}'
            elif effect_ctx == 'Cinema':
                style = f'{{{c_tag}\\alpha&H60&\\bord4\\t(0,120,\\alpha&H00&\\bord2)\\fscx100\\fscy100}}'
            else:
                style = f'{{{c_tag}\\fscx100\\fscy100\\frz0}}'
        else:
            c_tag = f'\\c{w_color_override}\\3c{o_tag}'
            style = f'{{{c_tag}\\fscx100\\fscy100\\frz0}}'
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
        s, e = (entrada['start'], entrada['end'])
        if s <= t < e:
            return entrada.get('tema')
    last = voice_color_map[-1]
    if t >= last['start']:
        return last.get('tema')
    return None

def _get_personagem_para_tempo(t, voice_color_map):
    """Retorna o nome do personagem ativo no tempo t, ou None."""
    if not voice_color_map:
        return None
    for entrada in voice_color_map:
        s, e = (entrada['start'], entrada['end'])
        if s <= t < e:
            return entrada.get('personagem') or entrada.get('speaker')
    last = voice_color_map[-1]
    if t >= last['start']:
        return last.get('personagem') or last.get('speaker')
    return None

def generate_karaoke_ass(whisper_result, srt_path, font='Bangers', size=100, theme='amarelo vermelho', pos='meio baixo', margin_v=80, words_per_block=5, video_format='vertical', effect='Pulo (Pop)', voice_color_map=None, border_w=3, perfis_personagem=None, colors=None):
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
    if video_format == 'horizontal':
        W, H = (1920, 1080)
    else:
        W, H = (1080, 1920)
    align = 5
    if pos == 'meio baixo' or pos == 'meio-baixo':
        y = int(H * 0.75)
    elif pos == 'topo':
        y = margin_v
    elif pos == 'meio':
        y = H // 2
    else:
        y = H - margin_v
    x = W // 2
    anchor = '{\\an5}'
    pos_tag = f'{{\\pos({x},{y})}}'
    perfis = perfis_personagem or {}
    personagens_presentes = set()
    if voice_color_map:
        for entrada in voice_color_map:
            p = entrada.get('personagem') or entrada.get('speaker')
            if p:
                personagens_presentes.add(p)

    def _get_format_for_char(char_name):
        f_font, f_size, f_bw = (font, size, border_w)
        f_pos, f_mar = (pos, margin_v)
        f_effect = effect
        if colors and len(colors) >= 3:
            f_pc, f_sc, f_oc = (hex_to_ass_color(colors[0]), hex_to_ass_color(colors[1]), hex_to_ass_color(colors[2]))
        else:
            f_pc, f_sc, f_oc = ass_colors(theme)
        if char_name and char_name in perfis:
            p_data = perfis[char_name]
            p_data_fmt = p_data.get(video_format, {})
            if p_data_fmt:
                f_font = p_data_fmt.get('font', f_font)
                f_size = p_data_fmt.get('size', f_size)
                f_bw = p_data_fmt.get('border_w', f_bw)
                f_pos = p_data_fmt.get('pos', f_pos)
                f_mar = p_data_fmt.get('margin_v', f_mar)
                f_effect = p_data_fmt.get('effect', f_effect)
                if 'color_primary' in p_data_fmt:
                    f_pc = hex_to_ass_color(p_data_fmt['color_primary'])
                    f_sc = hex_to_ass_color(p_data_fmt['color_secondary'])
                    f_oc = hex_to_ass_color(p_data_fmt['color_outline'])
                elif p_data_fmt.get('colors') and len(p_data_fmt['colors']) >= 3:
                    f_pc = hex_to_ass_color(p_data_fmt['colors'][0])
                    f_sc = hex_to_ass_color(p_data_fmt['colors'][1])
                    f_oc = hex_to_ass_color(p_data_fmt['colors'][2])
        return (f_font, f_size, f_bw, f_pc, f_sc, f_oc, f_pos, f_mar, f_effect)
    style_fmt = 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding'
    styles = []
    styles.append(f'Style: SubK,{font},{size},{p_color},{s_color},{o_color},&H00000000,-1,0,0,0,100,100,0,0,1,{border_w},{max(0, border_w - 1)},{align},20,20,0,1')
    _persona_style_map = {}
    for nome in personagens_presentes:
        f_font, f_size, f_bw, f_pc, f_sc, f_oc, _, _, _ = _get_format_for_char(nome)
        style_name = f"SubK_{nome.replace(' ', '_')}"
        styles.append(f'Style: {style_name},{f_font},{f_size},{f_pc},{f_sc},{f_oc},&H00000000,-1,0,0,0,100,100,0,0,1,{f_bw},{max(0, f_bw - 1)},{align},20,20,0,1')
        _persona_style_map[nome] = style_name
    header = f'[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\n\n[V4+ Styles]\n{style_fmt}\n' + '\n'.join(styles) + '\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    words_flat = [w for seg in whisper_result.get('segments', []) for w in seg.get('words', [])]
    blocks = [words_flat[i:i + words_per_block] for i in range(0, len(words_flat), words_per_block)]
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
    dialogue_lines = []
    for bi, blk in enumerate(blocks):
        if not blk:
            continue
        blk_end = end_map.get(bi, float(blk[-1]['end']))
        blk_mid = float(blk[0]['start'])
        tm_nome = _get_tema_para_tempo(blk_mid, voice_color_map)
        if tm_nome:
            blk_p, blk_s, blk_o = ass_colors(tm_nome)
        else:
            blk_p, blk_s, blk_o = (p_color, s_color, o_color)
        nome_personagem = _get_personagem_para_tempo(blk_mid, voice_color_map)
        blk_effect = effect
        if nome_personagem and nome_personagem in perfis:
            p_data = perfis[nome_personagem]
            if p_data.get('colors') and len(p_data['colors']) >= 3:
                blk_p = hex_to_ass_color(p_data['colors'][0])
                blk_s = hex_to_ass_color(p_data['colors'][1])
                blk_o = hex_to_ass_color(p_data['colors'][2])
            elif p_data.get('theme'):
                blk_p, blk_s, blk_o = ass_colors(p_data['theme'])
        blk_style = _persona_style_map.get(nome_personagem, 'SubK') if nome_personagem else 'SubK'
        for k, w in enumerate(blk):
            wst = float(w['start'])
            wen = float(blk[k + 1]['start']) if k < len(blk) - 1 else blk_end
            txt = _make_txt_ass(blk_ctx=blk, anchor_ctx=anchor, pos_tag_ctx=pos_tag, p_color_ctx=blk_p, s_color_ctx=blk_s, o_color_ctx=blk_o, effect_ctx=blk_effect, hidx=k)
            dialogue_lines.append(f'Dialogue: 0,{ass_time(wst)},{ass_time(wen)},{blk_style},,0,0,0,,{txt}')
    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write(header + '\n'.join(dialogue_lines) + '\n')

def _extract_audio_wav(media_path, wav_path):
    cmd = ['ffmpeg', '-y', '-i', media_path, '-vn', '-ac', '1', '-ar', '16000', '-f', 'wav', wav_path]
    subprocess.run(cmd, check=True, capture_output=True)

@staticmethod
def _format_timestamp(sec):
    msec = int((sec - int(sec)) * 1000)
    s = int(sec)
    h = s // 3600
    s %= 3600
    m = s // 60
    s %= 60
    return f'{h:02d}:{m:02d}:{s:02d},{msec:03d}'

def _parse_srt_to_whisper_result(srt_path):
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    words = []
    for blk in content.strip().split('\n\n'):
        lines = blk.strip().split('\n')
        if len(lines) >= 3:
            try:
                s_str, e_str = lines[1].split(' --> ')

                def t2s(ts):
                    pts = ts.replace(',', '.').split(':')
                    return float(pts[0]) * 3600 + float(pts[1]) * 60 + float(pts[2])
                words.append({'word': ' '.join(lines[2:]), 'start': t2s(s_str), 'end': t2s(e_str)})
            except Exception:
                pass
    return {'segments': [{'words': words}]}

def _transcrever_para_srt(media_path, model_dir, out_dir):
    if not VOSK_AVAILABLE:
        raise RuntimeError('Biblioteca Vosk não instalada.')
    wav_path = os.path.join(out_dir, 'audio_for_vosk.wav')
    _extract_audio_wav(media_path, wav_path)
    model = Model(model_dir)
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    wf = wave.open(wav_path, 'rb')
    results = []
    while True:
        data = wf.readframes(4000)
        if not data:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
    results.append(json.loads(rec.FinalResult()))
    wf.close()
    words = [w for r in results if 'result' in r for w in r['result']]
    srt_path = os.path.join(out_dir, 'auto_subs.srt')
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, w in enumerate(words, 1):
            f.write(f"{i}\n{_format_timestamp(w['start'])} --> {_format_timestamp(w['end'])}\n{w['word']}\n\n")
    return (srt_path, {'segments': [{'words': words}]})

def _transcrever_com_whisper(media_path, out_dir):
    if not WHISPER_AVAILABLE:
        raise RuntimeError('Whisper não instalado.')
    model = whisper.load_model('base')
    try:
        result = model.transcribe(media_path, fp16=False, language='pt', word_timestamps=True)
    except Exception:
        result = model.transcribe(media_path, fp16=False, language='pt')
    for seg in result.get('segments', []):
        if 'words' not in seg:
            seg['words'] = [{'word': seg['text'], 'start': seg['start'], 'end': seg['end']}]
    srt_path = os.path.join(out_dir, 'auto_subs_whisper.srt')
    with open(srt_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(result['segments'], 1):
            f.write(f"{i}\n{_format_timestamp(seg['start'])} --> {_format_timestamp(seg['end'])}\n{seg['text'].strip()}\n\n")
    return (srt_path, result)

def gerar_legendas_ass_e_queimar(media_path, srt_path=None, output_path=None, vosk_model_dir='', engine='vosk',
                                 font='Bangers', size=100, theme='amarelo vermelho', pos='meio baixo',
                                 margin_v=150, words_per_block=5, video_format='vertical', effect='Pulo (Pop)',
                                 border_w=3, voice_color_map=None, perfis_personagem=None):
    temp_dir = os.path.join(os.getcwd(), 'temp', 'gerador_legendas')
    os.makedirs(temp_dir, exist_ok=True)
    
    if srt_path and os.path.exists(srt_path):
        whisper_result = _parse_srt_to_whisper_result(srt_path)
    elif engine == 'whisper':
        if not WHISPER_AVAILABLE: raise Exception('Whisper não disponível')
        _, whisper_result = _transcrever_com_whisper(media_path, temp_dir)
    else:
        if not VOSK_AVAILABLE: raise Exception('Vosk não disponível')
        _, whisper_result = _transcrever_para_srt(media_path, vosk_model_dir, temp_dir)

    ass_path = os.path.join(temp_dir, 'master_legendas.ass')
    generate_karaoke_ass(
        whisper_result=whisper_result,
        srt_path=ass_path,
        font=font, size=size, theme=theme, pos=pos,
        margin_v=margin_v, words_per_block=words_per_block,
        video_format=video_format, effect=effect,
        colors=None, voice_color_map=voice_color_map,
        border_w=border_w, perfis_personagem=perfis_personagem
    )

    if not output_path:
        base, _ = os.path.splitext(media_path)
        output_path = f"{base}_legendado.mp4"

    esc_ass = ass_path.replace('\\', '/').replace(':', '\\:')
    cmd = [
        'ffmpeg', '-y', '-i', media_path,
        '-vf', f"ass='{esc_ass}'",
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium',
        '-c:a', 'copy', output_path
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        raise Exception(f"Erro no FFmpeg: {r.stderr[-400:]}")
    return output_path
