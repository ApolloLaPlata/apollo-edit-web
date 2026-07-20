import os
import json
import subprocess
import re
import sys
from pathlib import Path
from config_manager import ConfigManager

# Bug E Fix: garantir suporte a emojis no console do Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass  # Python < 3.7 nao tem reconfigure

# Configurações Base
BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "timeline_export.json"
OUTPUT_PATH = BASE_DIR / "timeline_final_render.mp4"

# Resolução Final do Projeto (Pode vir do JSON no futuro)
RESOLUTION = "1080x1920"
FPS = 30

def has_audio_stream(file_path):
    config = ConfigManager()
    try:
        CREATE_NO_WINDOW = 0x08000000
        result = subprocess.run(
            [config.get_ffprobe_path(), '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_type', '-of', 'default=nw=1:nk=1', file_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return 'audio' in result.stdout
    except Exception as e:
        print(f"[Aviso] has_audio_stream falhou para {file_path}: {e}")
        return False

def build_ffmpeg_timeline(json_data):
    config = ConfigManager()
    clips = json_data.get('clips', [])
    transitions = json_data.get('transitions', [])
    draft_mode = json_data.get('draft_mode', False)
    
    project_ratio = json_data.get('projectRatio', '16:9')
    exp_res = json_data.get('export_resolution', '1080')
    exp_fps = json_data.get('export_fps', '30')
    
    if draft_mode:
        RESOLUTION = "540x960" if project_ratio == '9:16' else "960x540" if project_ratio == '16:9' else "540x540"
        FPS = 24
    else:
        FPS = int(exp_fps)
        if project_ratio == '16:9':
            if exp_res == '720': RESOLUTION = "1280x720"
            elif exp_res == '1080': RESOLUTION = "1920x1080"
            elif exp_res == '2160': RESOLUTION = "3840x2160"
            else: RESOLUTION = "1920x1080"
        elif project_ratio == '9:16':
            if exp_res == '720': RESOLUTION = "720x1280"
            elif exp_res == '1080': RESOLUTION = "1080x1920"
            elif exp_res == '2160': RESOLUTION = "2160x3840"
            else: RESOLUTION = "1080x1920"
        elif project_ratio == '1:1':
            if exp_res == '720': RESOLUTION = "720x720"
            elif exp_res == '1080': RESOLUTION = "1080x1080"
            elif exp_res == '2160': RESOLUTION = "2160x2160"
            else: RESOLUTION = "1080x1080"
        else:
            RESOLUTION = "1080x1920"  # fallback
        
    if not clips:
        print("Erro: A timeline está vazia.")
        return

    # Descobrir a duração total do projeto
    total_duration = 0
    for c in clips:
        end_t = float(c['start_time']) + float(c['duration'])
        if end_t > total_duration:
            total_duration = end_t

    print(f"🎬 Iniciando Renderização da Timeline Web | Duração Total: {total_duration:.2f}s")
    print(f"⚡ Transições detectadas: {len(transitions)}")
    for t in transitions:
        print(f"   -> [{t['type']}] L:{t['left_clip_id']} R:{t['right_clip_id']} Dur:{t['duration']}s")

    # Comando base do FFmpeg
    cmd = [config.get_ffmpeg_path(), '-y']
    inputs = []
    filter_complex = []

    # Validação antecipada de mídias para erro mais amigável
    missing_media = []
    for c in clips:
        if c.get('type') not in ('video', 'audio'):
            continue
        file_path = c.get('name', '')
        file_path = config.resolve_path(file_path)
        real_path = os.path.join(BASE_DIR, "Midias", file_path)
        if not os.path.exists(real_path):
            real_path = file_path
        if not os.path.exists(real_path):
            missing_media.append(file_path)

    if missing_media:
        STATUS_PATH = BASE_DIR / "render_status.json"
        with open(STATUS_PATH, 'w', encoding='utf-8') as f:
            json.dump(
                {
                    "state": "error",
                    "progress": 0,
                    "message": "Arquivos de mídia ausentes: " + ", ".join(missing_media[:5])
                },
                f
            )
        print("❌ Erro: arquivos de mídia ausentes na timeline:")
        for m in missing_media:
            print(f" - {m}")
        return
    
    # 1. Criar o Canvas Preto de Fundo [base]
    # Usando o gerador "color" do ffmpeg
    inputs.extend(['-f', 'lavfi', '-i', f'color=c=black:s={RESOLUTION}:r={FPS}:d={total_duration}'])
    
    video_clips = [c for c in clips if c['type'] == 'video']
    audio_clips  = [c for c in clips if c['type'] == 'audio']
    text_clips   = [c for c in clips if c['type'] == 'text']
    
    overlay_chains = []
    current_bg = "0:v" # O canvas

    # --- PASSO 18: PROCESSAR VÍDEOS COM TRANSIÇÕES (XFADE) ---
    trans_map = {t['left_clip_id']: t for t in transitions}
    
    tracks = {}
    for c in video_clips:
        tracks.setdefault(c['track'], []).append(c)
        
    current_bg = "0:v"
    
    # Bug D Fix: usar contador explícito em vez de list.count('-i') que é frágil
    input_counter = [1]  # Começa em 1 porque o índice 0 é o canvas preto

    for track_id, t_clips in tracks.items():
        t_clips.sort(key=lambda x: float(x['start_time']))
        
        # Agrupar em ilhas (chunks conectados por transições)
        islands = []
        current_island = []
        for i, c in enumerate(t_clips):
            current_island.append(c)
            has_trans = False
            if i + 1 < len(t_clips):
                next_c = t_clips[i+1]
                if c['id'] in trans_map and trans_map[c['id']]['right_clip_id'] == next_c['id']:
                    has_trans = True
            if not has_trans:
                islands.append(current_island)
                current_island = []
                
        # Renderizar cada ilha
        for island in islands:
            island_streams = []
            
            for c in island:
                file_path = c['name']
                file_path = config.resolve_path(file_path)
                real_path = os.path.join(BASE_DIR, "Midias", file_path)
                if not os.path.exists(real_path):
                    real_path = file_path
                
                start_t = float(c['start_time'])
                dur = float(c['duration'])
                trim_in = float(c.get('trim_in', 0.0))
                
                inputs.extend(['-ss', str(trim_in), '-t', str(dur), '-i', real_path])
                input_num = input_counter[0]
                input_counter[0] += 1
                c['ffmpeg_input_num'] = input_num
                
                scale_pct = float(c.get('scale', 100)) / 100.0
                opacity = float(c.get('opacity', 100)) / 100.0
                res_w, res_h = map(int, RESOLUTION.split('x'))
                target_w = int(res_w * scale_pct)
                target_h = int(res_h * scale_pct)
                
                stream_name = f"v_raw_{c['id']}"
                fc_video = (
                    f"[{input_num}:v]"
                    f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
                    f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:color=black,"
                    f"format=rgba,"
                    f"colorchannelmixer=aa={opacity},"
                    f"setpts=PTS-STARTPTS[{stream_name}]"
                )
                filter_complex.append(fc_video)
                
                island_streams.append({
                    'clip': c, 'stream': stream_name, 'dur': dur, 'start_t': start_t
                })
            
            # Se for só um clipe
            if len(island) == 1:
                st = island_streams[0]
                island_start = st['start_t']
                island_end = island_start + st['dur']
                final_stream = st['stream']
            else:
                # Múltiplos clipes com transições
                island_start = island_streams[0]['start_t']
                current_merged_stream = island_streams[0]['stream']
                current_acc_dur = island_streams[0]['dur'] 
                
                for i in range(len(island_streams) - 1):
                    left_c = island_streams[i]['clip']
                    right_c = island_streams[i+1]['clip']
                    right_stream = island_streams[i+1]['stream']
                    trans = trans_map[left_c['id']]
                    t_dur = float(trans['duration'])
                    t_type = trans['type']
                    
                    type_map = {
                        'fade': 'fade', 'dissolve': 'fade', 'zoom-in': 'zoomin',
                        'slide-left': 'slideleft', 'wipe': 'wiperight',
                        'fadeblack': 'fadeblack', 'fadewhite': 'fadewhite',
                        'smoothleft': 'smoothleft', 'smoothright': 'smoothright',
                        'circlecrop': 'circlecrop', 'pixelize': 'pixelize',
                        'distance': 'distance'
                    }
                    ff_type = type_map.get(t_type, 'fade')
                    
                    offset = current_acc_dur - t_dur
                    out_stream = f"xfade_{left_c['id']}_{right_c['id']}"
                    
                    fc_xfade = f"[{current_merged_stream}][{right_stream}]xfade=transition={ff_type}:duration={t_dur}:offset={offset}[{out_stream}]"
                    filter_complex.append(fc_xfade)
                    
                    current_merged_stream = out_stream
                    current_acc_dur = (current_acc_dur + island_streams[i+1]['dur']) - t_dur
                    
                final_stream = current_merged_stream
                island_end = island_start + current_acc_dur
            
            # Reposiciona na timeline real
            ready_stream = f"{final_stream}_ready"
            fc_ready = f"[{final_stream}]setpts=PTS-STARTPTS+{island_start}/TB[{ready_stream}]"
            filter_complex.append(fc_ready)
            
            # Overlay (usando configs do primeiro clipe da ilha como âncora)
            base_c = island[0]
            pos_x = int(base_c.get('pos_x', 0))
            pos_y = int(base_c.get('pos_y', 0))
            overlay_x = f"(W-w)/2 + {pos_x}"
            overlay_y = f"(H-h)/2 + {pos_y}"
            
            out_bg = f"[bg_{base_c['id']}]"
            fc_overlay = f"[{current_bg}][{ready_stream}]overlay=x='{overlay_x}':y='{overlay_y}':enable='between(t,{island_start},{island_end})':eof_action=pass{out_bg}"
            filter_complex.append(fc_overlay)
            current_bg = out_bg
    
    windir = os.environ.get("WINDIR", "C:\\Windows").replace("\\", "/")
    font_path = f"{windir}/Fonts/arial.ttf".replace(":/", "\\:/") if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    for c in text_clips:
        start_t = float(c['start_time'])
        end_t = start_t + float(c['duration'])
        
        text_str = str(c.get('text_content', 'TEXTO')).replace(":", "\\\\:").replace("'", "")
        if not text_str.strip():
            continue
            
        font_size = int(c.get('font_size', 48))
        color = c.get('font_color', '#ffffff')
        
        # O scale foi removido do JSON do text_clip mas garantimos o pos_x e pos_y
        pos_x = int(c.get('pos_x', 0))
        pos_y = int(c.get('pos_y', 0))
        
        x_expr = f"(w-text_w)/2+{pos_x}"
        y_expr = f"(h-text_h)/2+{pos_y}"
        
        out_bg = f"[bg_text_{c['id']}]"
        
        current_bg_brackets = current_bg if current_bg.startswith('[') else f'[{current_bg}]'
        fc_text = f"{current_bg_brackets}drawtext=fontfile='{font_path}':text='{text_str}':fontcolor={color}:fontsize={font_size}:x={x_expr}:y={y_expr}:enable='between(t,{start_t},{end_t})'{out_bg}"
        
        filter_complex.append(fc_text)
        current_bg = out_bg

    # Fim dos Vídeos - format para yuv420p sem canal alpha
    last_bg = current_bg if current_bg.startswith('[') else f'[{current_bg}]'
    
    project_settings = json_data.get('project_settings', {})
    global_filter = project_settings.get('global_filter')
    
    if global_filter:
        ff_filter_str = ""
        if global_filter == "bw":
            ff_filter_str = "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3:0"
        elif global_filter == "sepia":
            ff_filter_str = "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:0"
        elif global_filter == "high_contrast":
            ff_filter_str = "eq=contrast=1.3:brightness=-0.05:saturation=1.2"
        elif global_filter == "cinematic":
            ff_filter_str = "colorbalance=rs=.1:bs=-.1:rm=.1:bm=-.1,eq=contrast=1.15:saturation=1.1"
            
        if ff_filter_str:
            filter_complex.append(f"{last_bg}format=yuv420p,{ff_filter_str}[outv]")
        else:
            filter_complex.append(f"{last_bg}format=yuv420p[outv]")
    else:
        filter_complex.append(f"{last_bg}format=yuv420p[outv]")

    # --- PROCESSAR ÁUDIOS (Parte 7) ---
    voice_inputs = []
    bgm_inputs = []
    
    for a_clip in audio_clips:
        file_path = config.resolve_path(a_clip['name'])
        real_path = os.path.join(BASE_DIR, "Midias", file_path)
        if not os.path.exists(real_path):
            real_path = file_path
        
        trim_in = float(a_clip.get('trim_in', 0.0))
        dur = float(a_clip['duration'])
        inputs.extend(['-ss', str(trim_in), '-t', str(dur), '-i', real_path])
        a_clip['ffmpeg_input_num'] = input_counter[0]
        input_counter[0] += 1
    
    for clip in video_clips + audio_clips:
        input_num = clip.get('ffmpeg_input_num')
        if input_num is None: continue
        
        # Recupera o path do arquivo original para checar
        file_path = clip['name']
        file_path = config.resolve_path(file_path)
        real_path = os.path.join(BASE_DIR, "Midias", file_path)
        if not os.path.exists(real_path):
            real_path = file_path
            
        # PULA se o arquivo for uma imagem (.png) ou um vídeo sem áudio
        if not has_audio_stream(real_path):
            continue
        
        start_t_ms = int(float(clip['start_time']) * 1000)
        
        # Passo 14: Controle de Volume (0.0 a 2.0)
        vol = float(clip.get('volume', 100)) / 100.0

        # Cria um canal de áudio ajustado e atrasado (delay) para começar no momento certo
        # O 'apad' evita que o áudio acabe de repente e desincronize o amix
        a_out = f"[a{input_num}]"
        fc_audio = f"[{input_num}:a]volume={vol},adelay={start_t_ms}|{start_t_ms},apad{a_out}"
        filter_complex.append(fc_audio)
        
        # Separar voz principal de músicas/SFX
        if clip.get('track') == 'a1':
            voice_inputs.append(a_out)
        else:
            bgm_inputs.append(a_out)

    cmd.extend(inputs)
    
    if voice_inputs or bgm_inputs:
        # 1. Mix Voice
        if len(voice_inputs) > 1:
            voice_mix = "".join(voice_inputs)
            filter_complex.append(f"{voice_mix}amix=inputs={len(voice_inputs)}:duration=first:dropout_transition=0[voice_mix]")
        elif len(voice_inputs) == 1:
            filter_complex.append(f"{voice_inputs[0]}anull[voice_mix]")
            
        # 2. Mix BGM
        if len(bgm_inputs) > 1:
            bgm_mix = "".join(bgm_inputs)
            filter_complex.append(f"{bgm_mix}amix=inputs={len(bgm_inputs)}:duration=first:dropout_transition=0[bgm_raw]")
        elif len(bgm_inputs) == 1:
            filter_complex.append(f"{bgm_inputs[0]}anull[bgm_raw]")
            
        # 3. Apply Sidechain Compress (Auto-Ducking)
        if bgm_inputs and voice_inputs:
            # Splita a voz: uma vai pro compressor guiar o ducking, outra vai pra mix final
            filter_complex.append("[voice_mix]asplit=2[voice_master][voice_ctrl]")
            filter_complex.append("[bgm_raw][voice_ctrl]sidechaincompress=threshold=0.08:ratio=4:attack=50:release=400[bgm_ducked]")
            # Mixa a voz intacta com o fundo mixado e "duckado"
            filter_complex.append("[voice_master][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=0[outa]")
        elif voice_inputs:
            filter_complex.append("[voice_mix]anull[outa]")
        elif bgm_inputs:
            filter_complex.append("[bgm_raw]anull[outa]")

        cmd.extend(['-filter_complex', ";".join(filter_complex)])
        cmd.extend(['-map', '[outv]', '-map', '[outa]'])
        cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
    else:
        cmd.extend(['-filter_complex', ";".join(filter_complex)])
        cmd.extend(['-map', '[outv]'])

    import hardware_detector
    encoder = hardware_detector.detect_h264_encoder()
    
    quality = json_data.get('export_quality', 'standard')
    # Ajustar bitrate baseando-se na resolução (4k precisa de mais banda)
    is_4k = ('2160' in RESOLUTION)
    
    # Perfil CRF para CPU
    crf_map = {'fast': '26', 'standard': '22', 'max': '18'}
    
    # Perfil Bitrate para GPU (ex: RX 580)
    if is_4k:
        bv_map = {'fast': '15M', 'standard': '30M', 'max': '60M'}
    else:
        bv_map = {'fast': '4M', 'standard': '10M', 'max': '20M'}
        
    crf_val = crf_map.get(quality, '22')
    bv_val = bv_map.get(quality, '10M')
    
    if encoder == 'libx264':
        if draft_mode:
            cmd.extend(['-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '32'])
        else:
            preset = 'fast' if quality == 'fast' else ('medium' if quality == 'standard' else 'slow')
            cmd.extend(['-c:v', 'libx264', '-preset', preset, '-crf', crf_val])
    else:
        if 'nvenc' in encoder:
            if draft_mode:
                cmd.extend(['-c:v', encoder, '-preset', 'p1', '-cq', '32', '-spatial-aq', '1'])
            else:
                nvenc_preset = 'p2' if quality == 'fast' else ('p4' if quality == 'standard' else 'p6')
                cmd.extend(['-c:v', encoder, '-preset', nvenc_preset, '-tune', 'hq', '-rc', 'vbr', '-cq', crf_val, '-spatial-aq', '1', '-b:v', bv_val])
        else:
            if draft_mode:
                cmd.extend(['-c:v', encoder, '-b:v', '2M'])
            else:
                cmd.extend(['-c:v', encoder, '-b:v', bv_val])
    cmd.extend(['-t', str(total_duration)])
    cmd.append(str(OUTPUT_PATH))
    
    print("\nExecutando Comando FFmpeg:")
    
    print(" ".join(cmd))
    
    STATUS_PATH = BASE_DIR / "render_status.json"
    
    def write_status(state, progress, message):
        with open(STATUS_PATH, 'w', encoding='utf-8') as f:
            json.dump({"state": state, "progress": progress, "message": message}, f)
    
    write_status("rendering", 0, "Iniciando FFmpeg...")
    
    # Roda o FFmpeg capturando stderr para ler o progresso
    # FFmpeg escreve "time=HH:MM:SS.xx" no stderr
    proc = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        errors='replace',
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
    
    stderr_output = []
    for line in proc.stderr:
        stderr_output.append(line)
        match = time_pattern.search(line)
        if match and total_duration > 0:
            h, m, s = int(match.group(1)), int(match.group(2)), float(match.group(3))
            current_s = h * 3600 + m * 60 + s
            pct = min(99, int((current_s / total_duration) * 100))
            write_status("rendering", pct, f"Processando... {current_s:.1f}s / {total_duration:.1f}s ({pct}%)")
    
    proc.wait()
    
    if proc.returncode == 0:
        write_status("done", 100, f"✅ Vídeo gerado: {OUTPUT_PATH.name}")
        print("\n✅ Sucesso! O FFmpeg acaba de gerar o seu arquivo final em:", OUTPUT_PATH)
    else:
        write_status("error", 0, "❌ Erro no FFmpeg. Verifique o terminal.")
        print("❌ Erro no FFmpeg! returncode:", proc.returncode)
        print("".join(stderr_output))


if __name__ == "__main__":
    import sys
    target_json = JSON_PATH
    if len(sys.argv) > 1:
        target_json = Path(sys.argv[1])
        
    if target_json.exists():
        with open(target_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        build_ffmpeg_timeline(data)
    else:
        print(f"Arquivo não encontrado: {target_json}. Exporte pela interface Web primeiro.")
