import os
import asyncio
import json
import re
import logging
from pathlib import Path

logger = logging.getLogger("AudioEngine")

class AsyncAudioEngine:
    """
    Motor Assíncrono de Áudio.
    Refatoração do antigo `audio_pipeline.py`.
    Executa processos FFmpeg em background sem bloquear o Event Loop (FastAPI).
    """
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path

    async def remover_silencio_ffmpeg(self, audio_path: str, noise: str = "-40dB", min_dur: float = 0.3) -> str:
        """
        [E5] Remove silêncios do áudio usando FFmpeg silencedetect + aselect.
        """
        try:
            out_path = str(Path(audio_path).with_suffix('')) + f"_paced_{os.getpid()}.wav"

            logger.info(f"🔍 [AudioEngine] Detectando silêncios (limiar={noise}, dur>={min_dur}s) em {Path(audio_path).name}")
            detect_cmd = [
                self.ffmpeg, "-y", "-i", audio_path,
                "-af", f"silencedetect=noise={noise}:d={min_dur}",
                "-f", "null", "-"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *detect_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()
            stderr_out = stderr.decode(errors="replace")

            starts = [float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", stderr_out)]
            ends   = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)",   stderr_out)]

            if not starts:
                logger.info("[AudioEngine] Nenhum silêncio detectado. Áudio inalterado.")
                return audio_path

            logger.info(f"✂️ [AudioEngine] {len(starts)} trecho(s) silencioso(s) encontrado(s). Cortando...")

            keep_parts = []
            prev_end = 0.0
            for s, e in zip(starts, ends):
                if s > prev_end + 0.05:
                    keep_parts.append(f"between(t,{prev_end:.3f},{s:.3f})")
                prev_end = e
            keep_parts.append(f"gte(t,{prev_end:.3f})")

            aselect_expr = "+".join(keep_parts)

            cut_cmd = [
                self.ffmpeg, "-y", "-i", audio_path,
                "-af", f"aselect='{aselect_expr}',asetpts=N/SR/TB",
                "-ar", "16000", "-ac", "1",
                out_path
            ]
            
            p2 = await asyncio.create_subprocess_exec(
                *cut_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, err2 = await p2.communicate()
            
            if p2.returncode != 0:
                logger.error(f"[AudioEngine] Erro FFmpeg ao cortar silêncio: {err2.decode()[-300:]}")
                return audio_path

            logger.info(f"✅ [AudioEngine] Áudio processado: {Path(out_path).name}")
            return out_path

        except Exception as e:
            logger.error(f"[AudioEngine] Erro em remover_silencio_ffmpeg: {e}")
            return audio_path

    async def normalize_lufs_output(self, video_path: str, target_lufs: float = -14.0) -> str:
        """
        [E8] Normalização LUFS two-pass no vídeo final gerado.
        """
        try:
            out_path = str(Path(video_path).with_suffix('')) + f"_lufs_{os.getpid()}.mp4"
            tp_max   = -1.5
            lra_max  = 11.0

            logger.info(f"📊 [AudioEngine] Medindo LUFS do vídeo final: {Path(video_path).name}")
            meas_cmd = [
                self.ffmpeg, "-y", "-i", video_path,
                "-af", f"loudnorm=I={target_lufs:.1f}:TP={tp_max:.1f}:LRA={lra_max:.1f}:print_format=json",
                "-f", "null", "-"
            ]
            
            p1 = await asyncio.create_subprocess_exec(
                *meas_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await p1.communicate()
            stderr_text = stderr.decode(errors="replace")

            json_match = re.search(r'\{[^{}]*"input_i"[^{}]*\}', stderr_text, re.DOTALL)
            measured = {}
            if json_match:
                try:
                    measured = json.loads(json_match.group())
                except Exception:
                    pass

            if not measured:
                logger.warning("⚠️ [AudioEngine] Não foi possível medir LUFS. Usando modo simples.")
                simple_cmd = [
                    self.ffmpeg, "-y", "-i", video_path,
                    "-c:v", "copy",
                    "-af", f"loudnorm=I={target_lufs:.1f}:TP={tp_max:.1f}:LRA={lra_max:.1f}",
                    "-c:a", "aac", "-b:a", "192k",
                    out_path
                ]
                p_s = await asyncio.create_subprocess_exec(*simple_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                await p_s.communicate()
                return out_path if p_s.returncode == 0 else video_path

            input_i   = measured.get("input_i",   str(target_lufs))
            input_tp  = measured.get("input_tp",  str(tp_max))
            input_lra = measured.get("input_lra", str(lra_max))
            input_thr = measured.get("input_thresh", "-70.0")
            offset    = measured.get("target_offset", "0.0")

            measured_lufs = float(input_i) if input_i != "-inf" else target_lufs
            logger.info(f"📈 [AudioEngine] LUFS medido: {measured_lufs:.1f} → alvo: {target_lufs:.1f}")

            loudnorm_filter = (
                f"loudnorm=I={target_lufs:.1f}:TP={tp_max:.1f}:LRA={lra_max:.1f}"
                f":measured_I={input_i}"
                f":measured_TP={input_tp}"
                f":measured_LRA={input_lra}"
                f":measured_thresh={input_thr}"
                f":offset={offset}"
                f":linear=true:print_format=none"
            )

            apply_cmd = [
                self.ffmpeg, "-y", "-i", video_path,
                "-c:v", "copy",
                "-af", loudnorm_filter,
                "-c:a", "aac", "-b:a", "192k",
                out_path
            ]
            
            p2 = await asyncio.create_subprocess_exec(
                *apply_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, err2 = await p2.communicate()

            if p2.returncode != 0:
                logger.error(f"[AudioEngine] Erro FFmpeg passo 2: {err2.decode()[-300:]}")
                return video_path

            logger.info(f"✅ [AudioEngine] Normalização concluída ({measured_lufs:.1f} → {target_lufs:.1f} LUFS)")
            return out_path

        except Exception as e:
            logger.error(f"[AudioEngine] Erro em normalize_lufs_output: {e}")
            return video_path

    def build_audio_filter_chain(self, config, fc, cmd, broll_windows=None):
        """
        Monta a cadeia de filtros de áudio do FFmpeg (Síncrono pois só constrói strings).
        - [E6] Radio Voice (Compressor/EQ)
        - [E9] SFX de Transição sincronizados
        - Mix de áudio de clips
        - [E7] Ducking de Trilha (Sidechain compress)
        """
        atempo = config.get("narr_atempo", 1.0)
        narr_vol = config.get("narr_vol", 1.0)
        narr_vol_str = f",volume={narr_vol:.3f}" if abs(narr_vol - 1.0) > 1e-3 else ""

        if abs(atempo - 1.0) < 1e-3:
            fc.append(f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,asetpts=PTS-STARTPTS{narr_vol_str}[narra]")
        else:
            fc.append(f"[1:a]atempo={max(0.5, min(2.0, atempo)):.3f},aformat=sample_rates=44100:channel_layouts=stereo,asetpts=PTS-STARTPTS{narr_vol_str}[narra]")

        # [E6] Radio Voice
        if config.get("rv_active", False):
            try:
                _preset_val = config.get("rv_preset", "Médio")
                _rv_presets = {
                    "Suave":  dict(thr="-24dB", ratio=3,  att=10,  rel=200),
                    "Médio": dict(thr="-20dB", ratio=4,  att=5,   rel=100),
                    "Forte":  dict(thr="-16dB", ratio=6,  att=3,   rel=60),
                }
                p = _rv_presets.get(_preset_val, _rv_presets["Médio"])
                rv_filter = (
                    f"[narra]acompressor="
                    f"threshold={p['thr']}:"
                    f"ratio={p['ratio']}:"
                    f"attack={p['att']}:"
                    f"release={p['rel']}:"
                    f"makeup=2dB,"
                    f"highpass=f=80,"
                    f"lowpass=f=12000,"
                    f"equalizer=f=200:t=o:w=100:g=3"
                    f"[narra_rv]"
                )
                fc.append(rv_filter)
                out_a = "narra_rv"
            except Exception as _erv:
                out_a = "narra"
        else:
            out_a = "narra"

        # [E9] SFX de Transição (B-Roll)
        if config.get("sfx_trans_active", False) and broll_windows:
            try:
                sfx_file = config.get("sfx_trans_path")
                vol_val = config.get("sfx_trans_vol", 0.5)
                next_idx = config.get("next_idx")

                if sfx_file and Path(sfx_file).exists():
                    sfx_labels = []
                    for i, win in enumerate(broll_windows):
                        bst_ms = int(win["start"] * 1000)
                        sfx_label = f"sfxtr{i}"
                        cmd += ["-i", sfx_file]
                        fc.append(
                            f"[{next_idx}:a]"
                            f"adelay={bst_ms}|{bst_ms},"
                            f"volume={vol_val:.2f},"
                            f"aformat=sample_rates=44100:channel_layouts=stereo"
                            f"[{sfx_label}]"
                        )
                        sfx_labels.append(sfx_label)
                        next_idx += 1

                    if sfx_labels:
                        all_inputs = f"[{out_a}]" + "".join(f"[{l}]" for l in sfx_labels)
                        n_inputs = 1 + len(sfx_labels)
                        mixed_label = "sfxtr_out"
                        fc.append(
                            f"{all_inputs}amix=inputs={n_inputs}:duration=longest:dropout_transition=0"
                            f"[{mixed_label}]"
                        )
                        out_a = mixed_label
                        config["next_idx"] = next_idx
            except Exception as _e9:
                pass

        # Mix de áudio de clips (vca)
        clips_audio_idx = config.get("clips_audio_idx")
        if clips_audio_idx:
            fc.append(f"[{clips_audio_idx}:a]aformat=sample_rates=44100:channel_layouts=stereo,asetpts=PTS-STARTPTS[vca]")
            fc.append(f"[{out_a}][vca]amix=inputs=2:duration=longest:dropout_transition=0[narra_mix]")
            out_a = "narra_mix"

        # [E7] Efeitos sonoros / Ducking de Trilha Sonora
        have_sfx = config.get("have_sfx", False)
        sfx_idx = config.get("sfx_idx")
        if have_sfx and sfx_idx is not None:
            vol = config.get("sfx_vol", 0.35)
            dur = config.get("dur", 0.0)
            fc.append(
                f"[{sfx_idx}:a]atrim=0:{dur:.6f},asetpts=PTS-STARTPTS,"
                f"aformat=sample_rates=44100:channel_layouts=stereo,"
                f"volume={vol:.3f}[sfx0]"
            )

            _duck_val = config.get("sfx_duck_mode", "Médio")
            _duck_presets = {
                "Suave":  dict(thr=0.03, ratio=3,  att=200, rel=1000),
                "Médio": dict(thr=0.05, ratio=5,  att=150, rel=800),
                "Forte":  dict(thr=0.07, ratio=8,  att=100, rel=600),
            }

            if _duck_val in _duck_presets:
                dp = _duck_presets[_duck_val]
                try:
                    fc.append(f"[{out_a}]asplit=2[narra_main][narra_sc]")
                    fc.append(
                        f"[sfx0][narra_sc]sidechaincompress="
                        f"threshold={dp['thr']:.3f}:"
                        f"ratio={dp['ratio']}:"
                        f"attack={dp['att']}:"
                        f"release={dp['rel']}:"
                        f"makeup=1[sfx_ducked]"
                    )
                    fc.append("[narra_main][sfx_ducked]amix=inputs=2:duration=longest:dropout_transition=0[aout]")
                except Exception as _ed:
                    fc.append(f"[{out_a}][sfx0]amix=inputs=2:duration=longest:dropout_transition=0[aout]")
            else:
                fc.append(f"[{out_a}][sfx0]amix=inputs=2:duration=longest:dropout_transition=0[aout]")
            out_a = "aout"

        return fc, cmd, out_a
