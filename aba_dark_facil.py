import customtkinter as ctk
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===========================================================
# Dark fácil by Enoch – V2 completa com Mapeamento texto→VÍDEO
# - Aba "Mapeamento" para colar blocos numerados ou com chave "Original:"
# - Parser que prioriza a linha "Original:" (inclusive multi-linha) e liga bloco N -> imagem N
# - Gera mapping.json e usa um timeline por imagem (start/end) com base nas palavras da voz, quando houver
# - Fallback mantém seu fluxo original
# Execute com: python APP_100.py
# ===========================================================

import os
import sys
import json
import cv2
import wave
import shutil
import numpy as np
import subprocess
import threading
import ctypes
import time
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageFont, ImageDraw
from pydub import AudioSegment
from audio_pipeline import AudioPipeline
import math
import gc
import re


def _ensure_std_streams():
    """Evita falhas de libs que chamam print/tqdm em modo --noconsole.

    No executável GUI do PyInstaller, sys.stdout/sys.stderr podem ser None.
    Isso causa: 'NoneType' object has no attribute 'write'.
    """
    try:
        import io

        class _NullWriter(io.TextIOBase):
            def write(self, s):
                return 0 if s is None else len(str(s))

            def flush(self):
                return None

            def isatty(self):
                return False

        for name in ("stdout", "stderr"):
            stream = getattr(sys, name, None)
            if stream is None or not hasattr(stream, "write"):
                setattr(sys, name, _NullWriter())
    except Exception:
        pass


_ensure_std_streams()

try:
    import license_check
except Exception:
    license_check = None


def _ensure_license_check_importable():
    """Garante que `license_check` possa ser importado (principalmente no executável).

    Quando a V2 é carregada via `spec_from_file_location`, o sys.path pode não incluir
    a pasta correta do bundle (`_internal`/`_MEIPASS`). Isso faria o TRIAL não funcionar.
    """
    global license_check
    if license_check is not None:
        return
    try:
        # As variáveis BASE_DIR/BUNDLE_DIR são definidas logo no início do arquivo.
        for p in (str(getattr(sys, "_MEIPASS", "") or ""), str(Path(sys.executable).resolve().parent)):
            if p and p not in sys.path:
                sys.path.insert(0, p)
    except Exception:
        pass
    try:
        import importlib
        license_check = importlib.import_module('license_check')
    except Exception:
        license_check = None

# ---------- Opcional: Vosk ----------
try:
    from vosk import Model, KaldiRecognizer
    VOSK_OK = True
except Exception:
    Model = None
    KaldiRecognizer = None
    VOSK_OK = False

# ---------- Opcional: Whisper (openai-whisper) ----------
try:
    import whisper
    WHISPER_OK = True
except Exception:
    whisper = None
    WHISPER_OK = False

# ---------- Opcional: faster-whisper (melhor para word-level) ----------
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_OK = True
except Exception:
    WhisperModel = None
    FASTER_WHISPER_OK = False

# ---------- Constantes & pastas ----------
APP_TITLE = "Dark fácil by Enoch (V2 - Vídeos)"

def app_base_dir() -> Path:
    # Quando empacotado pelo PyInstaller (onedir/onefile), __file__ aponta para _internal;
    # usamos a pasta do executável para ler/escrever arquivos do usuário.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

BASE_DIR  = app_base_dir()
# Pasta de recursos empacotados: no PyInstaller (onedir/onefile), aponta para _internal.
BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", BASE_DIR)) if getattr(sys, "frozen", False) else BASE_DIR

MODELS_DIR = BUNDLE_DIR / "models"
FONTS_DIR  = BUNDLE_DIR / "fonts"
OUT_DIR    = BASE_DIR / "videos_gerados"
IMAGEM_DIR = BASE_DIR / "imagem"
AUDIO_DIR  = BASE_DIR / "audio"
IMAGEM_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_JSON = BASE_DIR / "app_settings.json"
MAPPING_DIR = BASE_DIR / "mapeing"
MAPPING_DIR.mkdir(parents=True, exist_ok=True)
MAPPING_JSON = MAPPING_DIR / "mapping.json"
MAPPING_HISTORY_DIR = MAPPING_DIR / "historico_mapping"

# Se estivermos empacotados, tenta “seedar” o mapeing local com os arquivos padrão do bundle.
try:
    if getattr(sys, "frozen", False):
        _src_map_dir = BUNDLE_DIR / "mapeing"
        if _src_map_dir.exists() and _src_map_dir.is_dir():
            for _fn in ("mapping.json", "mapping_verification.json"):
                _src = _src_map_dir / _fn
                _dst = MAPPING_DIR / _fn
                if (not _dst.exists()) and _src.exists() and _src.is_file():
                    try:
                        shutil.copy2(str(_src), str(_dst))
                    except Exception:
                        pass
except Exception:
    pass

# [E1] Importar o Cérebro IA (com fallback seguro se o módulo não for encontrado)
try:
    from ai_director_pipeline import AIDirectorPipeline
    AI_DIRECTOR_OK = True
except ImportError:
    AI_DIRECTOR_OK = False

DEFAULT_MODEL_NAME = "vosk-model-small-pt-0.3"
DEFAULT_MODEL_DIR  = MODELS_DIR / DEFAULT_MODEL_NAME

# Mínimo aceitável para duração de uma cena/segmento (em segundos).
# Aumente este valor se encontrar muitas imagens com durações muito curtas.
MIN_SCENE_DURATION = 0.01

# ---------- Flags de UI (ocultar se True) ----------
# Oculta o grupo "MP4 com fundo preto — até 2 camadas"
HIDE_FX_UI = False
# Oculta o grupo "Gerador inteligente" e "Importar 'Originals' (TXT)" na aba Mapeamento
HIDE_GENERATOR_UI = False

# ---------- Utilidades ----------
def get_ffmpeg():
    cand = shutil.which("ffmpeg.exe") or shutil.which("ffmpeg")
    if cand: return cand
    for p in (
        os.environ.get("FFMPEG") or "",
        BASE_DIR / "ffmpeg" / "bin" / "ffmpeg.exe",
        BASE_DIR / "ffmpeg-8.0-essentials_build" / "bin" / "ffmpeg.exe",
        BUNDLE_DIR / "ffmpeg" / "bin" / "ffmpeg.exe",
        BUNDLE_DIR / "ffmpeg-8.0-essentials_build" / "bin" / "ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ):
        p = str(p)
        if p and Path(p).exists():
            return p
    return "ffmpeg"

def get_ffprobe(ffmpeg_path):
    p = Path(ffmpeg_path)
    for name in ("ffprobe.exe","ffprobe"):
        c = p.with_name(name)
        if c.exists(): return str(c)
        c2 = p.parent / name
        if c2.exists(): return str(c2)
        c3 = p.parent.parent / name
        if c3.exists(): return str(c3)
    return shutil.which("ffprobe.exe") or shutil.which("ffprobe") or "ffprobe"

def win_short_path(path_str: str) -> str:
    try:
        if os.name != "nt":
            return path_str
        _GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
        _GetShortPathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
        _GetShortPathNameW.restype = ctypes.c_uint
        buf = ctypes.create_unicode_buffer(260)
        ret = _GetShortPathNameW(path_str, buf, 260)
        return buf.value if ret else path_str
    except Exception:
        return path_str

def escape_subs(p: Path) -> str:
    s = Path(str(p)).as_posix()
    if os.name == "nt":
        s = s.replace(":", r"\:")
    return s

def _natural_key(path_or_name: str):
    import re as _re
    s = str(path_or_name)
    return [int(text) if text.isdigit() else text.lower() for text in _re.split(r"(\d+)", s)]

def run_call(cmd, silent=True):
    creationflags = 0x08000000 if os.name == "nt" else 0
    return subprocess.call(
        cmd,
        stdout=(subprocess.DEVNULL if silent else None),
        stderr=(subprocess.DEVNULL if silent else None),
        creationflags=creationflags
    )

def convert_to_wav16k(ffmpeg, in_audio: Path, out_wav: Path):
    try:
        rc = run_call([ffmpeg,"-y","-i",str(in_audio),"-ar","16000","-ac","1","-acodec","pcm_s16le",str(out_wav)], True)
        if rc == 0 and out_wav.exists():
            return
        audio = AudioSegment.from_file(str(in_audio))
        audio.set_frame_rate(16000).set_channels(1).export(str(out_wav), format="wav")
    except Exception:
        audio = AudioSegment.from_file(str(in_audio))
        audio.set_frame_rate(16000).set_channels(1).export(str(out_wav), format="wav")

# ---------- Vosk helpers ----------
def validate_vosk_dir(dirname: Path) -> bool:
    if not dirname or not dirname.exists():
        return False
    try:
        if VOSK_OK and Model is not None:
            try:
                # tenta carregar brevemente o modelo para validar
                m = Model(win_short_path(str(dirname)))
                del m
                return True
            except Exception:
                return False
        else:
            names = [p.name.lower() for p in dirname.iterdir() if p.exists()]
            if "final.mdl" in names:
                return True
            if any(n.startswith("am") for n in names):
                return True
            if (dirname / "model").exists():
                return True
            if any(n.endswith(".fst") or n.endswith(".int") for n in names):
                return True
            return False
    except Exception:
        return False

def vosk_transcribe(wav_path: Path, model_dir: Path, log_fn=print):
    if not VOSK_OK:
        raise RuntimeError("Biblioteca Vosk não instalada. Execute: pip install vosk.")
    if not model_dir or not model_dir.exists():
        raise RuntimeError("Pasta do modelo Vosk inválida.")
    safe_path = win_short_path(str(model_dir))
    log_fn(f"[voz] Carregando modelo em: {safe_path}")
    try:
        model = Model(safe_path)
    except Exception as e:
        raise RuntimeError(f"Falha ao criar o modelo Vosk: {e}.")
    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    result_words = []
    try:
        with wave.open(str(wav_path), "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    try:
                        j = json.loads(rec.Result())
                        result_words += j.get("result", [])
                    except Exception:
                        pass
            try:
                j = json.loads(rec.FinalResult())
                result_words += j.get("result", [])
            except Exception:
                pass
    except Exception as e:
        raise RuntimeError(f"Erro ao abrir WAV para transcrição: {e}")
    words = [{"word": w["word"], "start": float(w["start"]), "end": float(w["end"])} for w in result_words if "word" in w]
    log_fn(f"✅ {len(words)} palavras reconhecidas.")
    return words

def whisper_transcribe(audio_path: str, log_fn=print, chunk_duration: int = 120, language: str = "pt"):
    """
    Transcreve áudio usando openai/whisper com word-level timestamps.
    
    Para áudios acima de 1.5 minutos, divide em chunks de 2 minutos (120s)
    para maior precisão na transcrição.
    
    Args:
        audio_path: Caminho do arquivo de áudio
        log_fn: Função de log
        chunk_duration: Duração de cada chunk em segundos (padrão: 120s = 2 min)
    """
    if not WHISPER_OK:
        raise RuntimeError("Biblioteca Whisper não instalada. Execute: pip install openai-whisper")
    
    try:
        # Obter duração do áudio
        audio_duration = 0.0
        try:
            ffprobe = shutil.which("ffprobe") or "ffprobe"
            cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            if result.returncode == 0 and result.stdout:
                audio_duration = float(result.stdout.strip())
        except Exception:
            audio_duration = 0.0
        
        log_fn(f"[voz] Duração do áudio: {audio_duration:.1f}s ({int(audio_duration)//60}m {int(audio_duration)%60}s)")
        
        # OTIMIZAÇÃO: Carregar modelo UMA VEZ para todos os chunks
        log_fn("[voz] Carregando modelo Whisper (modelo: base, device: cpu)...")
        model = whisper.load_model("base", device="cpu")  # "base" é 2x mais rápido que "small"
        log_fn("[voz] Modelo carregado!")
        
        # Se áudio é curto (< 90 segundos), transcrever direto
        if audio_duration < 90:
            log_fn("[voz] Áudio curto - transcrevendo direto...")
            return _whisper_transcribe_single_with_model(audio_path, model, log_fn, language=language)
        
        # Para áudios longos, dividir em chunks de 2 minutos
        log_fn(f"[voz] Áudio longo - dividindo em chunks de {chunk_duration}s para maior precisão...")
        
        # Calcular número de chunks
        num_chunks = int(audio_duration / chunk_duration) + 1
        log_fn(f"[voz] Total de chunks: {num_chunks}")
        
        all_words = []
        ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, audio_duration)
            
            if start_time >= audio_duration:
                break
            
            chunk_dur = end_time - start_time
            log_fn(f"[voz] Processando chunk {i+1}/{num_chunks}: {start_time:.1f}s - {end_time:.1f}s ({chunk_dur:.1f}s)")
            
            # Extrair chunk do áudio
            chunk_path = Path(audio_path).parent / f"_temp_chunk_{i}.wav"
            try:
                cmd = [ffmpeg, "-y", "-ss", str(start_time), "-t", str(chunk_dur),
                       "-i", str(audio_path), "-ar", "16000", "-ac", "1", str(chunk_path)]
                subprocess.run(cmd, capture_output=True, timeout=60)
                
                if not chunk_path.exists():
                    log_fn(f"[voz] ⚠️ Falha ao extrair chunk {i+1}")
                    continue
                
                # Transcrever chunk REUTILIZANDO o modelo já carregado
                chunk_words = _whisper_transcribe_single_with_model(str(chunk_path), model, log_fn, silent=True, language=language)
                
                # Ajustar timestamps (adicionar offset do chunk)
                for word in chunk_words:
                    word["start"] = word["start"] + start_time
                    word["end"] = word["end"] + start_time
                    all_words.append(word)
                
                log_fn(f"[voz] Chunk {i+1}: {len(chunk_words)} palavras encontradas")
                
            except Exception as e:
                log_fn(f"[voz] ⚠️ Erro no chunk {i+1}: {e}")
            finally:
                # Limpar arquivo temporário
                try:
                    if chunk_path.exists():
                        chunk_path.unlink()
                except Exception:
                    pass
        
        log_fn(f"✅ Total: {len(all_words)} palavras reconhecidas em {num_chunks} chunks")
        return all_words
        
    except Exception as e:
        raise RuntimeError(f"Erro ao transcrever com Whisper: {e}")


def _whisper_transcribe_single_with_model(audio_path: str, model, log_fn=print, silent: bool = False, language: str = "pt"):
    """Transcreve um único arquivo de áudio com Whisper REUTILIZANDO modelo já carregado (RÁPIDO)."""
    if not silent:
        log_fn("[voz] Transcrevendo áudio com Whisper (word-level timestamps)...")
    
    # Usar a sintaxe CORRETA: word_timestamps=True
    # Importante: para suportar inglês, permitir sobrescrever o idioma.
    # Se language for vazio/None, omitimos o parâmetro para auto-detecção.
    transcribe_kwargs = dict(
        word_timestamps=True,
        verbose=False,
        no_speech_threshold=0.10,
        logprob_threshold=-1.0,
        compression_ratio_threshold=2.4,
    )
    if language:
        transcribe_kwargs["language"] = language
    result = model.transcribe(str(audio_path), **transcribe_kwargs)
    
    words = []
    # Extrair word-level timestamps dos segmentos
    for segment in result.get("segments", []):
        if "words" in segment:
            for word_info in segment.get("words", []):
                word_text = word_info.get("word", "").strip()
                if not word_text:
                    continue
                words.append({
                    "word": word_text,
                    "start": float(word_info.get("start", 0.0)),
                    "end": float(word_info.get("end", 0.0))
                })
    
    if words:
        return words
    
    # Fallback: distribuir palavras dentro dos segmentos
    for segment in result.get("segments", []):
        text = segment.get("text", "").strip()
        if not text:
            continue
        seg_words = text.split()
        start_seg = float(segment.get("start", 0.0))
        end_seg = float(segment.get("end", start_seg + 0.1))
        dur_seg = end_seg - start_seg
        for j, w in enumerate(seg_words):
            word_start = start_seg + (j / len(seg_words)) * dur_seg
            word_end = start_seg + ((j + 1) / len(seg_words)) * dur_seg
            words.append({"word": w, "start": word_start, "end": word_end})
    
    return words


def _whisper_transcribe_single(audio_path: str, log_fn=print, silent: bool = False, language: str = "pt"):
    """Transcreve um único arquivo de áudio com Whisper (função interna - carrega modelo)."""
    if not silent:
        log_fn("[voz] Carregando modelo Whisper (modelo: base, device: cpu)...")
    
    model = whisper.load_model("base", device="cpu")  # "base" é mais rápido que "small"
    
    if not silent:
        log_fn("[voz] Transcrevendo áudio com Whisper (word-level timestamps)...")
    
    # Usar a sintaxe CORRETA: word_timestamps=True
    transcribe_kwargs = dict(
        word_timestamps=True,
        verbose=False,
        no_speech_threshold=0.10,
        logprob_threshold=-1.0,
        compression_ratio_threshold=2.4,
    )
    if language:
        transcribe_kwargs["language"] = language
    result = model.transcribe(str(audio_path), **transcribe_kwargs)
    
    words = []
    # Extrair word-level timestamps dos segmentos
    for segment in result.get("segments", []):
        # Verificar se há 'words' (disponível com word_timestamps=True)
        if "words" in segment:
            for word_info in segment.get("words", []):
                word_text = word_info.get("word", "").strip()
                if not word_text:
                    continue
                words.append({
                    "word": word_text,
                    "start": float(word_info.get("start", 0.0)),
                    "end": float(word_info.get("end", 0.0))
                })
    
    if words:
        if not silent:
            log_fn(f"✅ {len(words)} palavras reconhecidas com Whisper (word-level).")
        return words
    
    # Fallback: distribuir palavras dentro dos segmentos usando timestamps do segmento
    if not silent:
        log_fn("[voz] Word-level não disponível, distribuindo por segmento...")
    for segment in result.get("segments", []):
        text = segment.get("text", "").strip()
        if not text:
            continue
        seg_words = text.split()
        start_seg = float(segment.get("start", 0.0))
        end_seg = float(segment.get("end", start_seg + 0.1))
        seg_dur = max(0.01, end_seg - start_seg)
        for i, word in enumerate(seg_words):
            word_start = start_seg + (i / max(1, len(seg_words))) * seg_dur
            word_end = start_seg + ((i + 1) / max(1, len(seg_words))) * seg_dur
            words.append({"word": word, "start": word_start, "end": word_end})
    
    if not silent:
        log_fn(f"✅ {len(words)} palavras extraídas de segmentos (distribuição).")
    
    return words


def faster_whisper_transcribe(audio_path: str, log_fn=print, chunk_duration: int = 120, language: str = "pt"):
    """
    Transcreve áudio usando faster-whisper com word-level timestamps.
    
    Para áudios acima de 1.5 minutos, divide em chunks de 2 minutos (120s)
    para maior precisão na transcrição.
    """
    if not FASTER_WHISPER_OK:
        raise RuntimeError("Biblioteca faster-whisper não instalada. Execute: pip install faster-whisper")
    
    try:
        # Obter duração do áudio
        audio_duration = 0.0
        try:
            ffprobe = shutil.which("ffprobe") or "ffprobe"
            cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            if result.returncode == 0 and result.stdout:
                audio_duration = float(result.stdout.strip())
        except Exception:
            audio_duration = 0.0
        
        log_fn(f"[voz] Duração do áudio: {audio_duration:.1f}s ({int(audio_duration)//60}m {int(audio_duration)%60}s)")
        
        # Se áudio é curto (< 90 segundos), transcrever direto
        if audio_duration < 90:
            log_fn("[voz] Áudio curto - transcrevendo direto...")
            return _faster_whisper_transcribe_single(audio_path, log_fn, language=language)
        
        # Para áudios longos, dividir em chunks de 2 minutos
        log_fn(f"[voz] Áudio longo - dividindo em chunks de {chunk_duration}s para maior precisão...")
        
        num_chunks = int(audio_duration / chunk_duration) + 1
        log_fn(f"[voz] Total de chunks: {num_chunks}")
        
        all_words = []
        ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
        
        for i in range(num_chunks):
            start_time = i * chunk_duration
            end_time = min((i + 1) * chunk_duration, audio_duration)
            
            if start_time >= audio_duration:
                break
            
            chunk_dur = end_time - start_time
            log_fn(f"[voz] Processando chunk {i+1}/{num_chunks}: {start_time:.1f}s - {end_time:.1f}s ({chunk_dur:.1f}s)")
            
            # Extrair chunk do áudio
            chunk_path = Path(audio_path).parent / f"_temp_chunk_fw_{i}.wav"
            try:
                cmd = [ffmpeg, "-y", "-ss", str(start_time), "-t", str(chunk_dur),
                       "-i", str(audio_path), "-ar", "16000", "-ac", "1", str(chunk_path)]
                subprocess.run(cmd, capture_output=True, timeout=60)
                
                if not chunk_path.exists():
                    log_fn(f"[voz] ⚠️ Falha ao extrair chunk {i+1}")
                    continue
                
                # Transcrever chunk
                chunk_words = _faster_whisper_transcribe_single(str(chunk_path), log_fn, silent=True, language=language)
                
                # Ajustar timestamps (adicionar offset do chunk)
                for word in chunk_words:
                    word["start"] = word["start"] + start_time
                    word["end"] = word["end"] + start_time
                    all_words.append(word)
                
                log_fn(f"[voz] Chunk {i+1}: {len(chunk_words)} palavras encontradas")
                
            except Exception as e:
                log_fn(f"[voz] ⚠️ Erro no chunk {i+1}: {e}")
            finally:
                try:
                    if chunk_path.exists():
                        chunk_path.unlink()
                except Exception:
                    pass
        
        log_fn(f"✅ Total: {len(all_words)} palavras reconhecidas em {num_chunks} chunks")
        return all_words
        
    except Exception as e:
        raise RuntimeError(f"Erro ao transcrever com faster-whisper: {e}")


def _faster_whisper_transcribe_single(audio_path: str, log_fn=print, silent: bool = False, language: str = "pt"):
    """Transcreve um único arquivo de áudio com faster-whisper (função interna)."""
    if not silent:
        log_fn("[voz] Carregando modelo faster-whisper (modelo: small, device: cpu)...")
    
    model = WhisperModel("small", device="cpu", compute_type="int8")
    
    if not silent:
        log_fn("[voz] Transcrevendo áudio com faster-whisper...")
    
    # faster-whisper retorna automaticamente word-level timestamps
    segments, info = model.transcribe(str(audio_path), language=(language or None), word_timestamps=True)
    
    words = []
    for segment in segments:
        # faster-whisper já inclui word-level timestamps por padrão
        if hasattr(segment, 'words') and segment.words:
            for word_info in segment.words:
                word_text = word_info.word.strip() if hasattr(word_info, 'word') else word_info.get('word', '').strip()
                if not word_text:
                    continue
                start = word_info.start if hasattr(word_info, 'start') else word_info.get('start', 0.0)
                end = word_info.end if hasattr(word_info, 'end') else word_info.get('end', 0.0)
                words.append({
                    "word": word_text,
                    "start": float(start),
                    "end": float(end)
                })
    
    if words:
        if not silent:
            log_fn(f"✅ {len(words)} palavras reconhecidas com faster-whisper (word-level).")
        return words
    
    # Fallback: se não houver words, distribuir pelos segmentos
    if not silent:
        log_fn("[voz] Word-level não disponível em faster-whisper, distribuindo por segmento...")
    
    # Re-transcrever para obter segmentos (generator já foi consumido)
    segments, info = model.transcribe(str(audio_path), language=(language or None))
    for segment in segments:
        text = segment.text.strip() if hasattr(segment, 'text') else segment.get('text', '').strip()
        if not text:
            continue
        seg_words = text.split()
        start_seg = segment.start if hasattr(segment, 'start') else segment.get('start', 0.0)
        end_seg = segment.end if hasattr(segment, 'end') else segment.get('end', start_seg + 0.1)
        seg_dur = max(0.01, end_seg - start_seg)
        for i, word in enumerate(seg_words):
            word_start = start_seg + (i / max(1, len(seg_words))) * seg_dur
            word_end = start_seg + ((i + 1) / max(1, len(seg_words))) * seg_dur
            words.append({"word": word, "start": word_start, "end": word_end})
    
    if not silent:
        log_fn(f"✅ {len(words)} palavras extraídas de segmentos (distribuição).")
    
    return words

# ---------- Remoção de fundo - watermark ----------
def preprocess_wm_image(src_path: str, remove_opt: str, tol: int, log_fn=print) -> str:
    """Remove fundo preto/verde de imagem de marca d'água para torná-la transparente.
    
    MÉTODO MELHORADO:
    - Para preto: usa threshold de luminância + suavização de bordas com gradiente alpha
    - Expande ligeiramente a máscara para pegar pixels semi-pretos nas bordas
    - Aplica suavização gaussiana na borda para transição mais natural
    """
    try:
        if remove_opt == "nenhum":
            return src_path
        
        im = Image.open(src_path).convert("RGBA")
        arr = np.array(im, dtype=np.float32)
        r, g, b, a = arr[..., 0], arr[..., 1], arr[..., 2], arr[..., 3]
        
        total_pixels = r.size
        mask = np.zeros(r.shape, dtype=bool)
        
        # Tolerância base do usuário + mínimo para funcionar bem
        effective_tol = max(tol, 40)  # mínimo 40 para pegar tons escuros
        
        if remove_opt in ("preto", "ambos"):
            # MÉTODO 1: Luminância (pega todos os tons de cinza escuro)
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            black_mask_lum = luminance <= effective_tol
            
            # MÉTODO 2: Valor máximo RGB (pega preto "puro" mesmo com ruído)
            max_rgb = np.maximum(np.maximum(r, g), b)
            black_mask_max = max_rgb <= effective_tol * 1.2
            
            # MÉTODO 3: Saturação baixa + escuro (cinzas muito escuros)
            min_rgb = np.minimum(np.minimum(r, g), b)
            saturation = np.where(max_rgb > 0, (max_rgb - min_rgb) / max_rgb, 0)
            dark_gray_mask = (luminance <= effective_tol * 1.5) & (saturation <= 0.3)
            
            # Combinar todos os métodos
            black_mask = black_mask_lum | black_mask_max | dark_gray_mask
            mask |= black_mask
            log_fn(f"[preprocess] Pixels pretos detectados: {np.sum(black_mask)} ({100*np.sum(black_mask)/total_pixels:.1f}%)")
        
        if remove_opt in ("verde", "ambos"):
            # Remover verde (chroma key) - verde puro é R=0, G=255, B=0
            # Usar distância no espaço de cor
            green_dist = np.sqrt((r - 0)**2 + (g - 255)**2 + (b - 0)**2)
            green_tol = effective_tol * 4  # verde precisa de tolerância maior
            green_mask = green_dist <= green_tol
            
            # Também detectar verde médio (não tão saturado)
            is_greenish = (g > r * 1.3) & (g > b * 1.3) & (g > 80)
            green_mask |= is_greenish
            
            mask |= green_mask
            log_fn(f"[preprocess] Pixels verdes detectados: {np.sum(green_mask)} ({100*np.sum(green_mask)/total_pixels:.1f}%)")
        
        # Aplicar máscara básica
        removed_count = np.sum(mask & (a > 0))
        
        # SUAVIZAÇÃO DE BORDAS: criar gradiente alpha nas bordas
        # Usar scipy ou numpy para dilatar a máscara e criar transição suave
        try:
            from scipy import ndimage
            # Dilatar a máscara um pouco para pegar bordas
            dilated = ndimage.binary_dilation(mask, iterations=2)
            # Criar máscara de borda (pixels que estão na dilatação mas não na máscara original)
            border = dilated & ~mask
            # Aplicar alpha parcial nas bordas (50% transparente)
            arr[border, 3] = arr[border, 3] * 0.3
            log_fn(f"[preprocess] Bordas suavizadas: {np.sum(border)} pixels")
        except ImportError:
            # Se scipy não disponível, pular suavização
            pass
        
        # Aplicar máscara principal - tornar pixels transparentes
        arr[mask, 3] = 0
        
        log_fn(f"[preprocess] Total removido: {removed_count} pixels ({100*removed_count/total_pixels:.1f}%)")
        
        out_im = Image.fromarray(arr.astype(np.uint8), mode="RGBA")
        out_fn = str(BASE_DIR / f"_wm_proc_{os.getpid()}.png")
        out_im.save(out_fn, "PNG")  # Forçar PNG para preservar alpha
        log_fn(f"Marca d'água pré-processada (remoção: {remove_opt}, tol={tol}) -> {out_fn}")
        return out_fn
    except Exception as e:
        log_fn(f"⚠️ Falha ao preprocessar marca d'água: {e}")
        return src_path

# ---------- Mapeamento: parser e timeline builder ----------
def parse_manual_text_blocks(raw_text):
    """
    Retorna lista de tuples (num_or_None, text)

    Regras:
    - Delimitadores de blocos: linha em branco ou linha iniciada com '---'.
    - Dentro de cada bloco procura linha com 'Original:' (case-insensitive).
      Se encontrada, extrai texto após 'Original:' e também linhas subsequentes
      até antes de:
          * linha que começa com 'PROMPT:' (case-insensitive)
          * linha em branco
          * linha iniciada por '---'
      Essas linhas são concatenadas.
    - Remove aspas simples/duplas e tipográficas no início/fim.
    - Detecta numeração (ex: 1 "texto..." ou 12 texto...) na primeira linha do bloco.
    - Se não houver 'Original:' no bloco, usa fallback da lógica anterior.
    """
    if not raw_text:
        return []

    lines = raw_text.splitlines()
    raw_blocks = []
    cur = []

    def flush():
        if cur:
            raw_blocks.append(cur.copy())
            cur.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('---') or stripped == '':
            flush()
            continue
        cur.append(line)
    flush()

    blocks = []
    # Regex corrigido para detectar numeração com opcional de aspas após o número
    num_re = re.compile(r"^\s*(\d+)\s*[\"“”'’]?\s*(.*)$")

    for block in raw_blocks:
        if not block:
            continue

        # Detecta número na primeira linha (para associação opcional)
        first_line = block[0]
        mnum = num_re.match(first_line)
        num = int(mnum.group(1)) if mnum else None

        # Procura linha com 'Original:'
        original_idx = None
        for i, l in enumerate(block):
            if 'original:' in l.lower():
                original_idx = i
                break

        if original_idx is not None:
            # Conteúdo da linha 'Original:' após ':'
            line_original = block[original_idx]
            after = line_original.split(':', 1)[1].strip()

            # Remove aspas iniciais/finais (comuns e tipográficas)
            after = after.strip('“”"\'‘’ ')

            original_parts = [after] if after else []

            # Linhas subsequentes até PROMPT:, linha vazia ou '---'
            for j in range(original_idx + 1, len(block)):
                nxt = block[j].strip()
                if (not nxt) or nxt.lower().startswith('prompt:') or nxt.startswith('---'):
                    break
                if 'original:' in nxt.lower():
                    break
                original_parts.append(nxt)

            original_text = " ".join(original_parts).strip()
            blocks.append((num, original_text))
            continue

        # Fallback sem 'Original:' -> tenta numeração
        if mnum:
            rest_first = mnum.group(2).strip()
            other_lines = []
            if rest_first:
                other_lines.append(rest_first)
            if len(block) > 1:
                other_lines += [l.strip() for l in block[1:] if l.strip()]
            text = " ".join(other_lines).strip()
            blocks.append((num, text))
        else:
            all_text = " ".join([l.strip() for l in block if l.strip()]).strip()
            blocks.append((None, all_text))

    return blocks

def find_resource(relname: str) -> Path:
    """Localiza um arquivo empacotado tanto no modo fonte quanto congelado.
    Procura em BASE_DIR, BASE_DIR/scripts, _internal e _MEIPASS variantes.
    """
    base = BASE_DIR
    cands = []
    try:
        cands.extend([
            base / relname,
            base / "scripts" / relname,
            base / "_internal" / relname,
            base / "_internal" / "scripts" / relname,
        ])
    except Exception:
        pass
    try:
        meipass = Path(getattr(sys, "_MEIPASS", ""))
        if meipass and str(meipass):
            cands.extend([
                meipass / relname,
                meipass / "scripts" / relname,
            ])
    except Exception:
        pass
    for p in cands:
        try:
            if p.exists():
                return p
        except Exception:
            continue
    return base / relname

def build_image_timeline_from_words_and_manual(blocks_parsed, media_items, words, audio_duration=None, intro_offset=0.0, intro_file=None):
    """
    Retorna timeline list [{'file','block_index','text','start','end'}].
    
    LÓGICA COM INTRO (exemplo: intro de 8s, 5 blocos, 5 cenas):
    ==============================================================
    - CENA 1 (intro/vídeo): 0s → 8s - Bloco 1 sendo narrado
    - CENA 2 (imagem): 8s → fim Bloco 2 - Bloco 2 sendo narrado
    - CENA 3 (imagem): fim Bloco 2 → fim Bloco 3
    - CENA 4 (imagem): fim Bloco 3 → fim Bloco 4  
    - CENA 5 (imagem): fim Bloco 4 → fim do áudio
    
    O INTRO AGORA É INCLUÍDO NO TIMELINE!
    """
    if audio_duration is None:
        audio_duration = (words[-1]["end"] if words else 0.0)
    
    has_intro = intro_offset > 0.5 and intro_file  # Considera intro se > 0.5s E tem arquivo
    
    # Calcular quantas palavras cada bloco tem
    block_word_counts = []
    for num, txt in blocks_parsed:
        wc = len(txt.split()) if txt else 0
        block_word_counts.append(wc)
    
    # Índice da última palavra de cada bloco na lista de words
    # end_word_indices[i] = índice da última palavra do bloco i (0-indexed)
    end_word_indices = []
    word_idx = -1
    for wc in block_word_counts:
        word_idx += wc
        end_word_indices.append(word_idx)
    
    # Criar timeline
    timeline = []
    
    # ========== ADICIONAR O INTRO COMO PRIMEIRA CENA ==========
    if has_intro:
        # Texto do Bloco 1 (índice 0)
        intro_text = blocks_parsed[0][1] if len(blocks_parsed) > 0 else ""
        
        timeline.append({
            "file": intro_file,
            "block_index": 1,
            "text": intro_text,
            "start": 0.0,
            "end": round(intro_offset, 3),
            "is_intro": True
        })
    
    # ========== ADICIONAR AS IMAGENS ==========
    n_images = len(media_items)
    if n_images == 0 and not has_intro:
        return []
    
    prev_end = intro_offset if has_intro else 0.0
    
    for img_idx in range(n_images):
        # Determinar qual bloco de texto corresponde a esta imagem
        # COM intro: imagem 0 -> bloco 1 (índice 1), imagem 1 -> bloco 2 (índice 2)
        # SEM intro: imagem 0 -> bloco 0, imagem 1 -> bloco 1
        if has_intro:
            block_idx = img_idx + 1  # Pula o bloco 0 (que é do intro)
        else:
            block_idx = img_idx
        
        # Texto do bloco
        block_text = ""
        if block_idx < len(blocks_parsed):
            block_text = blocks_parsed[block_idx][1]
        
        # Tempo de início
        start_time = prev_end
        
        # Tempo de fim = END da última palavra do bloco correspondente
        if block_idx < len(end_word_indices) and words:
            last_word_idx = end_word_indices[block_idx]
            
            # Garantir índice válido
            if last_word_idx >= 0 and last_word_idx < len(words):
                end_time = float(words[last_word_idx].get("end", audio_duration))
            else:
                end_time = audio_duration
        else:
            end_time = audio_duration
        
        # Garantir end > start
        if end_time <= start_time:
            end_time = min(audio_duration, start_time + MIN_SCENE_DURATION)
        
        # Última imagem vai até o fim do áudio
        if img_idx == n_images - 1:
            end_time = audio_duration
        
        timeline.append({
            "file": media_items[img_idx],
            "block_index": block_idx + 1,  # 1-indexed para exibição
            "text": block_text,
            "start": round(start_time, 3),
            "end": round(end_time, 3)
        })
        
        prev_end = end_time
    
    return timeline


def generate_mapping_integrated(
    audio_file: str,
    texto_file: str,
    imagens_files: list,
    output_file: str,
    intro_file: str = None,
    intro_duration: float = 0.0,
    audio_duration: float = None,
    words: list = None,
    log_fn = print
):
    """
    Gera mapping.json de forma integrada (sem dependência de script externo).
    
    LÓGICA INTELIGENTE:
    ===================
    1. Se há INTRO: intro vai de 0s até intro_duration, mostrando texto do Bloco 1
    2. A primeira IMAGEM (cena_2) começa em intro_duration e vai até o FIM do Bloco 2
    3. Cada imagem subsequente cobre seu bloco correspondente até a última palavra
    4. A última imagem vai até o fim do áudio
    
    Parâmetros:
    - audio_file: caminho do áudio
    - texto_file: caminho do TXT com blocos "Original: ..."
    - imagens_files: lista de caminhos das imagens (SEM o intro)
    - output_file: onde salvar o mapping.json
    - intro_file: caminho do vídeo intro (ou None)
    - intro_duration: duração do intro em segundos
    - audio_duration: duração total do áudio (se já conhecida)
    - words: lista de palavras transcritas (se já disponível)
    - log_fn: função de log
    """
    from datetime import datetime
    
    log_fn("\n" + "="*70)
    log_fn("GERANDO MAPPING.JSON (INTEGRADO)")
    log_fn("="*70)
    
    # 1. Obter duração do áudio se não fornecida
    if not audio_duration:
        try:
            ffprobe = shutil.which("ffprobe") or "ffprobe"
            cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
            if result.returncode == 0 and result.stdout:
                audio_duration = float(result.stdout.strip())
        except Exception as e:
            log_fn(f"[ERRO] Não foi possível obter duração do áudio: {e}")
            return False
    
    log_fn(f"[1/4] Duração do áudio: {audio_duration:.1f}s ({int(audio_duration)//60}m {int(audio_duration)%60}s)")
    
    # 2. Transcrever áudio se palavras não fornecidas
    if not words:
        log_fn("[2/4] Transcrevendo áudio com Whisper...")
        try:
            if WHISPER_OK:
                words = whisper_transcribe(str(audio_file), log_fn=log_fn)
            elif FASTER_WHISPER_OK:
                words = faster_whisper_transcribe(str(audio_file), log_fn=log_fn)
            else:
                log_fn("[ERRO] Nenhum transcritor disponível (Whisper/faster-whisper)")
                return False
        except Exception as e:
            log_fn(f"[ERRO] Falha na transcrição: {e}")
            return False
    else:
        log_fn(f"[2/4] Usando {len(words)} palavras já transcritas")
    
    if not words:
        log_fn("[ERRO] Nenhuma palavra foi transcrita")
        return False
    
    # 3. Ler blocos de texto do arquivo
    log_fn("[3/4] Lendo blocos de texto...")
    scenes = []
    try:
        content = Path(texto_file).read_text(encoding="utf-8")
    except:
        try:
            content = Path(texto_file).read_text(encoding="cp1252")
        except:
            content = Path(texto_file).read_text(encoding="latin-1")
    
    # DEBUG: mostra primeiras linhas do arquivo
    log_fn(f"       [DEBUG] Arquivo lido: {len(content)} caracteres")
    preview_lines = content.splitlines()[:5]
    for idx, pl in enumerate(preview_lines):
        log_fn(f"       [DEBUG] Linha {idx}: {pl[:80]}...")
    
    # Parser para "Original:" ou "Origina:" (aceita typo sem L)
    # Regex: origina seguido opcionalmente de 'l', depois ':'
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        lower_line = line.lower()
        # Aceita "original:", "origina:", "cena:", "parte:", "bloco:", "scene:", "1.", etc.
        # Regex explicado: (chave opcional) + : ou apenas numero + ponto/espaço
        marker_match = re.search(r'(original|origina|cena|parte|bloco|scene|texto):', lower_line)
        if not marker_match:
             # Tenta formato numerado explícito no inicio da linha ex: "1. Texto"
             marker_match = re.search(r'^\s*\d+[\.\)\-]\s+', lower_line)
        
        if marker_match:
            # Encontra posição do marcador no texto original
            marker_end = marker_match.end()
            # Pega TUDO após o marcador
            raw_text = line[marker_end:]
            # Remove número opcional no início (ex: "1 texto" -> "texto")
            raw_text = re.sub(r'^\s*\d+\s*', '', raw_text).strip()
            
            log_fn(f"       [DEBUG] Marcador encontrado na linha {i}, texto: {raw_text[:50]}...")
            
            buffer = [raw_text] if raw_text else []
            
            # Continua lendo linhas seguintes até encontrar outro marcador ou linha vazia
            j = i + 1
            while j < len(lines):
                nxt_line = lines[j].strip()
                nxt_lower = nxt_line.lower()
                # Para se encontrar outro marcador ou linha vazia
                if not nxt_line or re.search(r'(original|origina):', nxt_lower) or nxt_lower.startswith('prompt:') or nxt_lower.startswith('---'):
                    break
                buffer.append(nxt_line)
                j += 1
            
            joined = " ".join(buffer)
            # CORREÇÃO: Usar o texto COMPLETO, não apenas falas entre aspas
            # O código antigo extraía só os textos entre aspas, ignorando a narração
            # Agora pegamos o texto inteiro do bloco
            text = joined.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
            text = re.sub(r'\s+', ' ', text).strip().strip('"\'')
            if text:
                scenes.append({"text": text})
                log_fn(f"       Bloco {len(scenes)}: {text[:60]}... ({len(text.split())} palavras)")
            i = j
            continue
        i += 1
    
    # Fallback: formato numerado "1. texto"
    if not scenes:
        numbered = re.findall(r"^\s*\d+\.\s*(.+)$", content, flags=re.MULTILINE)
        for txt in numbered:
            txt = re.sub(r'\s+', ' ', txt).strip().strip('"\'')
            if txt:
                scenes.append({"text": txt})
    
    if not scenes:
        log_fn("[ERRO] Nenhum bloco de texto encontrado")
        return False
    
    log_fn(f"       {len(scenes)} blocos de texto detectados")
    
    # 4. Verificar se há intro
    has_intro = intro_file and intro_duration > 0.5
    if has_intro:
        log_fn(f"\n[INTRO] Detectado: {Path(intro_file).name} ({intro_duration:.1f}s)")
    
    # ========== NOVA LÓGICA: DISTRIBUIÇÃO PROPORCIONAL + FUZZY MATCHING ==========
    # O problema anterior: contava palavras do TXT e assumia que transcrição tinha as mesmas
    # Isso falha porque Whisper pode ter mais ou menos palavras que o TXT
    #
    # NOVA SOLUÇÃO:
    # 1. Calcular proporção de cada bloco (palavras do bloco / total palavras TXT)
    # 2. Aplicar essa proporção ao tempo ÚTIL do áudio (após intro)
    # 3. Usar busca fuzzy para refinar os pontos de corte
    
    log_fn(f"\n[4/4] Correlacionando cenas com tempos (BUSCA FUZZY EXATA)...")
    
    # ========== FUNÇÕES DE MATCHING FUZZY ==========
    def normalize_word(w):
        """Normaliza palavra para comparação fuzzy"""
        import unicodedata
        w = unicodedata.normalize('NFD', w.lower())
        w = ''.join(c for c in w if unicodedata.category(c) != 'Mn')  # Remove acentos
        w = re.sub(r'[^a-z0-9]', '', w)  # Remove pontuação
        return w
    
    def similarity_score(word1, word2):
        """Calcula similaridade entre duas palavras (0-1)"""
        w1, w2 = normalize_word(word1), normalize_word(word2)
        if not w1 or not w2:
            return 0.0
        if w1 == w2:
            return 1.0
        # Similaridade por substring
        if w1 in w2 or w2 in w1:
            return 0.85
        # Similaridade por caracteres em comum
        common = sum(1 for c in w1 if c in w2)
        return common / max(len(w1), len(w2))
    
    def find_sequence_in_transcript(txt_words, transcript, start_idx=0, search_window=None):
        """
        Encontra uma sequência de palavras do TXT na transcrição.
        Retorna (start_word_idx, end_word_idx) na transcrição, ou None se não encontrar.
        
        Usa busca fuzzy para tolerar pequenas diferenças.
        """
        if not txt_words or not transcript:
            return None
        
        # Normalizar palavras do TXT
        txt_normalized = [normalize_word(w) for w in txt_words if len(normalize_word(w)) >= 2]
        if len(txt_normalized) < 2:
            return None
        
        # Limitar janela de busca
        if search_window:
            end_idx = min(len(transcript), start_idx + search_window)
        else:
            end_idx = len(transcript)
        
        # Buscar as primeiras palavras significativas do bloco (para encontrar início)
        first_words = txt_normalized[:min(5, len(txt_normalized))]
        # Buscar as últimas palavras significativas do bloco (para encontrar fim)  
        last_words = txt_normalized[-min(5, len(txt_normalized)):]
        
        best_start_idx = None
        best_start_score = 0
        best_end_idx = None
        best_end_score = 0
        
        # Varrer transcrição procurando matches
        for i in range(start_idx, end_idx):
            trans_word = normalize_word(transcript[i].get("word", ""))
            if len(trans_word) < 2:
                continue
            
            # Verificar se encontramos o INÍCIO do bloco
            if best_start_idx is None:
                for j, fw in enumerate(first_words):
                    score = similarity_score(fw, trans_word)
                    if score > 0.75:
                        # Verificar se próximas palavras também batem
                        consecutive_matches = 1
                        for k in range(1, min(3, len(first_words) - j)):
                            if i + k < end_idx:
                                next_trans = normalize_word(transcript[i + k].get("word", ""))
                                if j + k < len(first_words):
                                    next_score = similarity_score(first_words[j + k], next_trans)
                                    if next_score > 0.7:
                                        consecutive_matches += 1
                        
                        total_score = score + (consecutive_matches - 1) * 0.3
                        if total_score > best_start_score:
                            best_start_score = total_score
                            best_start_idx = i
                        break
            
            # Verificar se encontramos o FIM do bloco
            for j, lw in enumerate(last_words):
                score = similarity_score(lw, trans_word)
                if score > 0.75:
                    # Verificar palavras anteriores para confirmar
                    consecutive_matches = 1
                    for k in range(1, min(3, j + 1)):
                        if i - k >= start_idx:
                            prev_trans = normalize_word(transcript[i - k].get("word", ""))
                            if j - k >= 0:
                                prev_score = similarity_score(last_words[j - k], prev_trans)
                                if prev_score > 0.7:
                                    consecutive_matches += 1
                    
                    total_score = score + (consecutive_matches - 1) * 0.3
                    if total_score > best_end_score:
                        best_end_score = total_score
                        best_end_idx = i
        
        return (best_start_idx, best_end_idx) if best_start_idx is not None or best_end_idx is not None else None
    
    # ========== CÁLCULO PURO MATEMÁTICO (SOLICITAÇÃO DO USUÁRIO - CARACTERES) ==========
    # Ignora transcrição. Distribui o tempo total do áudio proporcionalmente
    # à quantidade de CARACTERES de cada bloco (maior precisão).
    
    block_times = []
    
    # 1. Calcular total de CARACTERES no texto
    total_chars = 0
    scenes_chars = []
    for scene in scenes:
        # Conta caracteres totais (incluindo espaços e pontuação) para precisão máxima
        char_count = len(scene["text"])
        scenes_chars.append(char_count)
        total_chars += char_count
        
    log_fn(f"       [MATH-ONLY] Total de caracteres: {total_chars}")
    log_fn(f"       [MATH-ONLY] Duração total áudio: {audio_duration:.2f}s")
    
    if total_chars == 0:
        # Fallback de emergência
        part = audio_duration / max(1, len(scenes))
        curr = 0.0
        for _ in scenes:
            block_times.append((curr, curr + part))
            curr += part
    else:
        # 2. Calcular tempo por caractere
        running_time = intro_duration if has_intro else 0.0
        available_time = max(0, audio_duration - running_time)
        
        sec_per_char = available_time / total_chars
        log_fn(f"       [MATH-ONLY] Tempo por caractere: {sec_per_char:.5f}s")
        
        for i, char_count in enumerate(scenes_chars):
            # Duração deste bloco baseada em caracteres
            duration = char_count * sec_per_char
            
            start_t = running_time
            end_t = start_t + duration
            
            if end_t > audio_duration:
                end_t = audio_duration
                
            block_times.append((start_t, end_t))
            log_fn(f"       Bloco {i+1}: {start_t:.2f}s - {end_t:.2f}s ({char_count} chars)")
            
            running_time = end_t
            
    # Ajustar último bloco para cravar no final
    if block_times:
        last_s, _ = block_times[-1]
        block_times[-1] = (last_s, audio_duration)
        log_fn(f"       [MATH-ONLY] Ajuste final: {audio_duration:.2f}s")
    
    # ========== CONSTRUIR MAPPING ==========
    mapping = {
        "audio_duration": audio_duration,
        "intro_offset": intro_duration if has_intro else 0.0,
        "generated_at": datetime.now().isoformat(),
        "images": []
    }
    
    # Adicionar INTRO como primeira cena
    if has_intro:
        intro_text = scenes[0]["text"] if scenes else ""
        mapping["images"].append({
            "file": str(intro_file),
            "block_index": 1,
            "text": intro_text,
            "start": 0.0,
            "end": round(intro_duration, 3),
            "status": "intro",
            "is_intro": True
        })
        log_fn(f"\n       [INTRO] {Path(intro_file).name}")
        log_fn(f"               0.00s - {intro_duration:.2f}s (Bloco 1)")
    
    # Adicionar IMAGENS com os tempos calculados
    # Lógica 1:1 com reciclagem de mídia (video cycling)
    # Usuario exige: 1 Mídia para CADA bloco de texto.
    # Se tivermos mais blocos (35) que imagens (15), reciclamos as imagens na sequência: 1..15, 1..15, 1..5
    
    num_images = len(imagens_files)
    num_blocks = len(scenes)
    
    # Se houver intro, consideramos que a intro consome o primeiro bloco
    start_block_idx = 0
    available_blocks_count = num_blocks
    
    if has_intro:
        start_block_idx = 1
        available_blocks_count -= 1
    
    if num_images == 0:
        log_fn("⚠️ Nenhuma imagem/vídeo para mapear!")
    else:
        # Iteramos sobre os BLOCOS DE TEXTO disponíveis
        for i in range(available_blocks_count):
            abs_block_idx = start_block_idx + i
            
            # Escolher imagem ciclicamente
            img_file = imagens_files[i % num_images]
            
            scene_text = scenes[abs_block_idx]["text"]
            start_time, end_time = block_times[abs_block_idx]
            
            # Última cena vai até o fim do áudio?
            # Na verdade, "última cena" aqui é o último bloco de texto.
            is_last_block = (i == available_blocks_count - 1)
            if is_last_block:
                end_time = audio_duration
            
            scene_num = i + 2 if has_intro else i + 1
            final_duration = end_time - start_time
            
            log_fn(f"\n       [{scene_num}] {Path(img_file).name}")
            log_fn(f"               Bloco Texto {abs_block_idx+1}: {start_time:.2f}s - {end_time:.2f}s ({final_duration:.1f}s)")
            
            mapping["images"].append({
                "file": str(Path(img_file).resolve()),
                "block_index": abs_block_idx + 1,
                "text": scene_text,
                "start": round(start_time, 3),
                "end": round(end_time, 3),
                "status": "word_aligned"
            })
            
            prev_end_time = end_time
    
    # 7. Salvar mapping.json
    try:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        Path(output_file).write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
        log_fn(f"\n{'='*70}")
        log_fn(f"[OK] Mapping salvo em: {output_file}")
        log_fn(f"     Total de cenas: {len(mapping['images'])}")
        log_fn(f"     Total de palavras transcritas: {len(words)}")
        log_fn("="*70)
        # Retornar mapping E palavras para que possam ser cacheadas
        mapping["_transcribed_words"] = words
        return mapping
    except Exception as e:
        log_fn(f"[ERRO] Falha ao salvar mapping: {e}")
        return False


# ---------- ASS helpers ----------
def ass_time(t):
    cs = int(round(t*100))
    h = cs//360000; cs%=360000
    m = cs//6000;   cs%=6000
    s = cs//100;    cs%=100
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"

def hex_to_ass(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
        return f"&H00{b}{g}{r}&"
    return "&H00FFFFFF&"

def ass_to_hex(ass_color):
    if ass_color.startswith("&H00") and ass_color.endswith("&") and len(ass_color) == 12:
        b, g, r = ass_color[6:8], ass_color[8:10], ass_color[10:12]
        return f"#{r}{g}{b}"
    return "#FFFFFF"

def ass_align(pos): return {"embaixo":2,"meio":5,"topo":8}.get(pos,2)

def ass_header(font, size, primary, secondary, outline, alignment, margin_v, W, H):
    return (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding\n"
        f"Style: SubK,{font},{size},{primary},{secondary},{outline},&H00000000,-1,0,0,0,100,100,0,0,1,3,0,{alignment},50,50,{margin_v},1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

def words_to_ass(words, words_per_block, font, size, color1, outline1, motion_color, motion_outline, position, margin_v, W, H, uppercase, hold, max_gap, audio_end):
    P, S, O = color1, motion_color, outline1
    al = ass_align(position)
    
    # Calcular Y:
    # Topo (8) -> y = margin_v
    # Meio (5) -> y = H/2
    # Embaixo (2) -> y = H - margin_v
    # Meio-baixo (custom) -> y = H - (H * 0.25) approx. ou H * 0.75
    if position == "meio-baixo":
        # Posicionar a 25% da borda inferior (ou seja, em 75% da altura)
        y = int(H * 0.75)
        # Ajustar alignment para 2 (Bottom Center) e recalcular margin_v efetivo para o header style?
        # O Style no header usa 'margin_v'. Se definirmos margin_v fixo no header, o \pos(x,y) sobrescreve?
        # Sim, \pos(x,y) sobrescreve alinhamento/margem do estilo para o posicionamento.
        # Mas o header pede um margin_v. Vamos usar o padrão.
    else:
        y = (H-margin_v if al==2 else H//2 if al==5 else margin_v)
    
    # Se alignment for 2 ou 8 ou 5, o X é sempre centro (W//2) porque usamos \an5 (Middle Center alignment tag) no text?
    # O código original usa anchor = r"{\an5}" que força alinhamento pelo centro do texto.
    # Então a posição (x,y) define onde o CENTRO do texto vai ficar.
    x = W // 2
    anchor = r"{\an5}"
    pos    = rf"{{\pos({x},{y})}}"
    head = ass_header(font, size, P, S, O, al, margin_v, W, H)
    if not words:
        return head + f"Dialogue: 0,0:00:00.00,0:00:01.00,SubK,,0,0,0,,{anchor}{pos}.\n"
    def group(seq, n):
        return [seq[i:i+n] for i in range(0, len(seq), n)]
    blocks = group(words, max(1, int(words_per_block)))
    lines = []
    for bi, blk in enumerate(blocks):
        st = float(blk[0]["start"]); end_raw = float(blk[-1]["end"]); end = end_raw
        if hold:
            if bi < len(blocks)-1:
                next_st = float(blocks[bi+1][0]["start"])
                gap = max(0.0, next_st - end_raw)
                if gap <= float(max_gap):
                    end = max(st, next_st - 0.01)
            else:
                if audio_end is not None: end = float(audio_end)
        def txt(hidx=None):
            parts=[anchor,pos]
            for j,w in enumerate(blk):
                t = (w["word"].upper() if uppercase else w["word"])
                parts.append(rf"{{\c{S}}}" if j==hidx else rf"{{\c{P}}}")
                parts.append(t)
                if j<len(blk)-1: parts.append(" ")
            return "".join(parts)
        lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(end)},SubK,,0,0,0,,{txt()}")
        for j,w in enumerate(blk):
            wst = float(w["start"]); wen = max(wst+0.05, float(w["end"]))
            lines.append(f"Dialogue: 1,{ass_time(wst)},{ass_time(wen)},SubK,,0,0,0,,{txt(hidx=j)}")
            
            # [E3] WORD HIGHLIGHT DINÂMICO: palavras com motion_trigger "saltam" na tela
            if w.get("motion_trigger"):
                word_txt = (w["word"].upper() if uppercase else w["word"])
                # Posicionar acima da legenda normal (simula "salto")
                y_motion = max(margin_v, y - int(size * 1.8))
                motion_pos = rf"{{\pos({x},{y_motion})}}"
                # Tamanho 130% do normal para destaque visual
                motion_size = int(size * 1.30)
                # Amarelo vivo (BGR ASS) + contorno preto + fade in/out 80ms
                MOTION_COLOR   = motion_color
                MOTION_OUTLINE = motion_outline
                motion_tag = (
                    r"{\an5}"
                    + motion_pos
                    + rf"{{\fad(80,80)}}"
                    + rf"{{\fs{motion_size}}}"
                    + rf"{{\c{MOTION_COLOR}}}"
                    + rf"{{\3c{MOTION_OUTLINE}}}"
                    + rf"{{\bord3}}"
                )
                lines.append(
                    f"Dialogue: 2,{ass_time(wst)},{ass_time(wen)},SubK,,0,0,0,,"
                    f"{motion_tag}{word_txt}"
                )
    return head + "\n".join(lines) + "\n"

# ---------- App ----------
class AbaDarkFacil(ctk.CTkFrame):
    def __init__(self, root, config_manager=None):
        super().__init__(root)
        self.root = self
        self.config_manager = config_manager
        
        try:
            root.title(f"Dark fácil by Enoch (Vosk-ready) - Versão Atualizada {datetime.now().strftime('%H:%M:%S')}")
            root.geometry("1150x1500")
            root.resizable(True, True)
        except AttributeError:
            pass # É um notebook, não precisa
            
        # BYPASS SUPREMO: Forçar modo ilimitado antes de qualquer coisa
        self.limited_mode = False 
        
        # Iniciar loop de reforço
        self.root.after(5000, self.force_unlock_loop) 

        self.root.configure()

        self.ffmpeg = get_ffmpeg()
        self.audio_pipeline = AudioPipeline(self.ffmpeg, logger=self.log)
        self.ffprobe = get_ffprobe(self.ffmpeg)

        # Job / parallel render management
        self._job_id = str(os.getpid())
        self._headless = False

        # Estado
        self.images = []
        self.video_clips = []
        self.audio_path = None
        self.fps = 30

        # Overlays e SFX
        self.fx1_path = None; self.fx2_path = None; self.sfx_path = None
        self.fx1_en = tk.BooleanVar(value=False); self.fx2_en = tk.BooleanVar(value=False)
        self.fx1_op = tk.DoubleVar(value=0.65); self.fx2_op = self.fx1_op
        self.fx_key = tk.DoubleVar(value=0.25); self.fx_blend = tk.DoubleVar(value=0.02)

        self.sfx_en = tk.BooleanVar(value=False); self.sfx_vol = tk.DoubleVar(value=0.35)
        self.sfx_gate = tk.BooleanVar(value=True); self.sfx_thr = tk.DoubleVar(value=0.02)
        self.sfx_att = tk.IntVar(value=5); self.sfx_rel = tk.IntVar(value=150)

        # Modelo Vosk selecionado
        self.vosk_dir = None

        # Vídeo Intro (toca antes do mapeamento, na velocidade original)
        self.intro_video_path = tk.StringVar(value="")
        self.intro_video_en = tk.BooleanVar(value=False)
        self.intro_duration = 0.0  # duração detectada do intro

        # Mapeamento
        self.manual_blocks = []
        self.mapping_timeline = None
        self.mapping_timeline_job1 = None  # Mapping separado para Job 1
        self.mapping_timeline_job2 = None  # Mapping separado para Job 2
        self.current_mapping_job = tk.IntVar(value=1)  # Qual job está sendo editado (1 ou 2)
        self.use_manual_map = tk.BooleanVar(value=False)
        # Gerador inteligente integrado (função generate_mapping_integrated)
        self.scenes_txt_path = tk.StringVar(value="")
        self.scenes_txt_path = tk.StringVar(value="")
        self.gen_model_size = tk.StringVar(value="medium")
        self.gen_device = tk.StringVar(value="cpu")
        self.gen_compute = tk.StringVar(value="float32")
        self.gen_transcriber = tk.StringVar(value="faster")

        # [E1] Instanciar o Cérebro de IA (AIDirectorPipeline)
        # Usa um config_manager simplificado que lê diretamente do config.json local
        self._ai_director = None
        if AI_DIRECTOR_OK:
            try:
                # Cria um wrapper mínimo de config para o AIDirectorPipeline
                class _DarkFacilConfig:
                    def __init__(self):
                        self._data = {}
                        _cfg_path = BASE_DIR / "config.json"
                        if _cfg_path.exists():
                            try:
                                with open(_cfg_path, "r", encoding="utf-8") as _f:
                                    self._data = json.load(_f)
                            except Exception:
                                pass
                    def get(self, key, default=None):
                        return self._data.get(key, default)
                    def get_api_config(self, provider, field):
                        return self._data.get("api", {}).get(provider, {}).get(field)

                self._ai_director = AIDirectorPipeline(_DarkFacilConfig())
            except Exception as _e:
                self.log(f"[IA] AIDirectorPipeline não inicializado: {_e}") if hasattr(self, 'log') else None

        # Carregar settings
        self._load_settings()

        # Verificar licença no início e ativar modo limitado se não houver
        try:
            payload = self._get_license_payload()
            self.limited_mode = False  # BYPASS: Sempre desbloqueado
        except Exception:
            self.limited_mode = False
        # ---------- Layout: esquerda com logo ----------
        shell = ctk.CTkFrame(self); shell.pack(fill="both", expand=True)
        left  = ctk.CTkFrame(shell); left.pack(side="left", fill="y", padx=6, pady=6)
        self.left = left
        right = ctk.CTkFrame(shell); right.pack(side="right", fill="both", expand=True, padx=6, pady=6)
        self.right = right

        # LOGO
        self.logo_lbl = ctk.CTkLabel(left)
        self.logo_lbl.pack(fill="both", expand=True, padx=10, pady=(8,6))
        self._load_logo()

        def bigbtn(text, cmd):
            b = ctk.CTkButton(left, text=text, command=cmd, font=("Arial", 10, "bold"), padx=10, pady=8)
            b.pack(fill="x", padx=8, pady=6); return b
        bigbtn("📁 Novo projeto", self.novo_projeto)
        bigbtn("📂 Abrir pasta de saída", lambda: self._abrir_pasta(OUT_DIR))
        bigbtn("📂 Abrir models", lambda: self._abrir_pasta(MODELS_DIR))
        bigbtn("📂 Abrir fonts",  lambda: self._abrir_pasta(FONTS_DIR))
        bigbtn("📂 Abrir imagens", lambda: self._abrir_pasta(IMAGEM_DIR))
        bigbtn("📂 Abrir áudio",   lambda: self._abrir_pasta(AUDIO_DIR))
        bigbtn("🔑 Importar licença", lambda: self.sel_license())
        bigbtn("🆔 Mostrar HWID", lambda: self.show_hwid())
        
        # [E14] Dashboard de Status
        self._build_dashboard(left)

        # ---------- Abas ----------
        self.nb = ttk.Notebook(right)
        self.tab_cfg = ctk.CTkFrame(self.nb)
        self.tab_pairs = ctk.CTkFrame(self.nb)
        self.tab_map = ctk.CTkFrame(self.nb)
        self.tab_wm  = ctk.CTkFrame(self.nb)
        self.tab_log = ctk.CTkFrame(self.nb)
        self.nb.add(self.tab_cfg, text="Configuração")
        # Inserir aba de pares entre Configuração e Mapeamento
        self.nb.add(self.tab_pairs, text="Combinar Pares")
        self.nb.add(self.tab_map, text="Mapeamento")
        self.nb.add(self.tab_wm,  text="Marca d'Água")
        self.nb.add(self.tab_log, text="Logs")
        self.nb.pack(fill="both", expand=True)

        # ---------- Config (com rolagem) ----------
        canvas = tk.Canvas(self.tab_cfg)
        vsb = ttk.Scrollbar(self.tab_cfg, orient="vertical", command=canvas.yview)
        self.cfg = ctk.CTkFrame(canvas)
        self.cfg.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.cfg, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True); vsb.pack(side="right", fill="y")

        ctk.CTkLabel(self.cfg, text="(Dark fácil by Enoch)", font=("Arial", 16, "bold")).pack(pady=12)

        # ---------- Status da licença (exibe validade e tempo restante) ----------
        lic_frame = ctk.CTkFrame(self.cfg)
        lic_frame.pack(fill="x", pady=6)
        ctk.CTkLabel(lic_frame, text="Licença:").pack(side="left")
        self.lic_status_var = tk.StringVar(value="Sem licença verificada")
        ctk.CTkLabel(lic_frame, textvariable=self.lic_status_var).pack(side="left", padx=(6,12))
        self.lic_exp_var = tk.StringVar(value="")
        ctk.CTkLabel(lic_frame, textvariable=self.lic_exp_var).pack(side="left", padx=(6,12))
        self.lic_remain_var = tk.StringVar(value="")
        ctk.CTkLabel(lic_frame, textvariable=self.lic_remain_var).pack(side="left", padx=(6,12))
        ctk.CTkButton(lic_frame, text="Atualizar licença", command=lambda: self._update_license_status()).pack(side="right")

        # ----- VÍDEO INTRO (opcional) -----
        f_intro = ctk.CTkLabelFrame(self.cfg, text="🎬 VÍDEO INTRO (opcional - toca antes do mapeamento)", padx=10, pady=10)
        f_intro.pack(fill="x", pady=6)
        intro_row = ctk.CTkFrame(f_intro); intro_row.pack(fill="x")
        self.intro_chk = ctk.CTkSwitch(intro_row, text="Usar vídeo intro", variable=self.intro_video_en, selectcolor="#1e1e1e")
        self.intro_chk.pack(side="left")
        ctk.CTkButton(intro_row, text="📁 Selecionar", command=self.sel_intro_video).pack(side="left", padx=(10,0))
        self.lbl_intro = ctk.CTkLabel(intro_row, text="Nenhum")
        self.lbl_intro.pack(side="left", padx=(10,0))
        self.lbl_intro_dur = ctk.CTkLabel(intro_row, text="")
        self.lbl_intro_dur.pack(side="left", padx=(10,0))
        ctk.CTkLabel(f_intro, text="💡 O intro toca na velocidade original. O mapeamento das cenas começa DEPOIS do intro.", font=("Arial",8)).pack(anchor="w")

        # ----- VÍDEOS DE CENA -----
        f_img = ctk.CTkLabelFrame(self.cfg, text="🎞️ VÍDEOS (cenas)", padx=10, pady=10)
        f_img.pack(fill="x", pady=6)
        ctk.CTkButton(f_img, text="📁 Selecionar vídeos (mp4/mov/mkv...)", command=self.sel_midias, font=("Arial",10,"bold")).pack(fill="x", pady=4)
        self.lbl_midias = ctk.CTkLabel(f_img, text="Nenhum vídeo"); self.lbl_midias.pack(fill="x")
        ctk.CTkLabel(f_img, text="Velocidade dos clipes (%):").pack(side="left")
        self.clip_speed = tk.IntVar(value=100)
        tk.Spinbox(f_img, from_=100, to=120, increment=1, variable=self.clip_speed, width=6).pack(side="left", padx=(6,0))

        self.keep_video_audio = tk.BooleanVar(value=False)
        ctk.CTkSwitch(f_img, text="Manter áudio original", variable=self.keep_video_audio, selectcolor="#1e1e1e").pack(side="left", padx=(15,0))
        
        ctk.CTkLabel(f_img, text="Vol:").pack(side="left", padx=(5,0))
        self.video_audio_vol = tk.DoubleVar(value=1.0)
        tk.Spinbox(f_img, from_=0.0, to=2.0, increment=0.1, variable=self.video_audio_vol, width=5).pack(side="left", padx=(2,0))

        # ----- ÁUDIO -----
        f_aud = ctk.CTkLabelFrame(self.cfg, text="🎵 ÁUDIO (narração)", padx=10, pady=10)
        f_aud.pack(fill="x", pady=6)
        ctk.CTkButton(f_aud, text="📁 Selecionar Áudio", command=self.sel_audio, font=("Arial",10,"bold")).pack(fill="x", pady=4)
        self.lbl_audio = ctk.CTkLabel(f_aud, text="Nenhum áudio"); self.lbl_audio.pack(fill="x")
        ctk.CTkLabel(f_aud, text="Velocidade narração (atempo):").pack(side="left")
        self.narr_atempo = tk.DoubleVar(value=1.0)
        tk.Spinbox(f_aud, from_=0.90, to=1.10, increment=0.01, textvariable=self.narr_atempo, width=6).pack(side="left", padx=(6,0))

        # [E8] Normalização LUFS
        self.opt_lufs = tk.BooleanVar(value=True)
        self.lufs_target = tk.DoubleVar(value=-14.0)
        f_lufs = ctk.CTkFrame(f_aud)
        f_lufs.pack(fill="x", pady=(6, 0))
        ctk.CTkSwitch(
            f_lufs, text="🎨 Normalizar áudio (LUFS)",
            variable=self.opt_lufs, selectcolor="#1e1e1e",
            font=("Arial", 9, "bold")
        ).pack(side="left")
        ctk.CTkLabel(f_lufs, text="  Alvo:").pack(side="left")
        ctk.CTkOptionMenu(
            f_lufs,
            variable=self.lufs_target,
            values=[-14.0, -16.0, -23.0],
            width=6
        ).pack(side="left", padx=(4, 0))
        ctk.CTkLabel(f_lufs, text="LUFS   (-14=YouTube/TikTok  -16=Spotify  -23=Broadcast)", font=("Arial", 8)).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(f_aud, text="Volume:").pack(side="left", padx=(15,0))
        self.narr_vol = tk.DoubleVar(value=1.0)
        tk.Spinbox(f_aud, from_=0.0, to=2.0, increment=0.1, variable=self.narr_vol, width=5).pack(side="left", padx=(2,0))

        # [E6] Radio Voice: compressor profissional de voz
        f_rv = ctk.CTkFrame(f_aud)
        f_rv.pack(fill="x", pady=(8, 0))
        self.opt_radio_voice = tk.BooleanVar(value=False)
        ctk.CTkSwitch(
            f_rv, text="🎙️ Voz de Rádio (Compressor + EQ profissional)",
            variable=self.opt_radio_voice, selectcolor="#1e1e1e",
            font=("Arial", 9, "bold")
        ).pack(side="left")
        ctk.CTkLabel(f_rv, text="  Intensidade:").pack(side="left")
        self.radio_voice_preset = tk.StringVar(value="Médio")
        ctk.CTkOptionMenu(
            f_rv,
            variable=self.radio_voice_preset,
            values=["Suave", "Médio", "Forte"],
            width=8
        ).pack(side="left", padx=(4, 0))

        # ----- VÍDEO -----
        f_vid = ctk.CTkLabelFrame(self.cfg, text="⚙️ VÍDEO", padx=10, pady=10)
        f_vid.pack(fill="x", pady=6)
        self.orient = tk.StringVar(value="horizontal")
        fr = ctk.CTkFrame(f_vid); fr.pack(anchor="w")
        tk.Radiobutton(fr, text="Horizontal (16:9)", variable=self.orient, value="horizontal", selectcolor="#1e1e1e").pack(side="left")
        tk.Radiobutton(fr, text="Vertical (9:16)",   variable=self.orient, value="vertical", selectcolor="#1e1e1e").pack(side="left", padx=(20,0))
        frz = ctk.CTkFrame(f_vid); frz.pack(anchor="w", pady=2)
        self.zoom_basic = tk.BooleanVar(value=True)
        ctk.CTkSwitch(frz, text="Zoom suave (básico)", variable=self.zoom_basic, selectcolor="#1e1e1e").pack(side="left")
        self.zoom_amp = tk.DoubleVar(value=0.10)
        self.low_mem_mode = tk.BooleanVar(value=False)
        ctk.CTkSwitch(frz, text="Modo baixo uso de memória (mais rápido)", variable=self.low_mem_mode, selectcolor="#1e1e1e").pack(side="left", padx=(8,0))
        self.random_eff_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(frz, text="Aleatório (Randomize)", variable=self.random_eff_en, selectcolor="#1e1e1e").pack(side="left", padx=(8,0))
        adv_frame = ctk.CTkLabelFrame(f_vid, text="Avançado (opcional)", padx=8, pady=6)
        adv_frame.pack(fill="x", pady=(8,6))
        self.zoom_adv_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(adv_frame, text="Zoom avançado (amplitude %)", variable=self.zoom_adv_en, selectcolor="#1e1e1e").grid(row=0,column=0, sticky="w")
        self.zoom_adv_amp = tk.DoubleVar(value=0.10)
        tk.Spinbox(adv_frame, from_=0.00, to=1.00, increment=0.01, variable=self.zoom_adv_amp, width=8).grid(row=0,column=1, sticky="w", padx=(6,0))
        self.float_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(adv_frame, text="Flutuar lateral", variable=self.float_en, selectcolor="#1e1e1e").grid(row=1,column=0, sticky="w", pady=(6,0))
        ctk.CTkLabel(adv_frame, text="Amplitude(px):").grid(row=1,column=1, sticky="e")
        self.float_amp = tk.IntVar(value=16)
        tk.Spinbox(adv_frame, from_=0, to=400, increment=1, variable=self.float_amp, width=6).grid(row=1,column=2, sticky="w", padx=(6,0))
        ctk.CTkLabel(adv_frame, text="Período(s):").grid(row=1,column=3, sticky="e")
        self.float_period = tk.DoubleVar(value=6.0)
        tk.Spinbox(adv_frame, from_=0.5, to=30.0, increment=0.1, textvariable=self.float_period, width=6).grid(row=1,column=4, sticky="w", padx=(6,0))
        # Linha 2: Efeitos de movimento adicionais
        self.pan_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(adv_frame, text="Pan (esq→dir)", variable=self.pan_en, selectcolor="#1e1e1e").grid(row=2,column=0, sticky="w", pady=(4,0))
        ctk.CTkLabel(adv_frame, text="Velocidade:").grid(row=2,column=1, sticky="e")
        self.pan_speed = tk.DoubleVar(value=0.05)
        tk.Spinbox(adv_frame, from_=0.01, to=0.20, increment=0.01, variable=self.pan_speed, width=6).grid(row=2,column=2, sticky="w", padx=(6,0))
        # Linha 3: Tilt (cima/baixo)
        self.tilt_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(adv_frame, text="Tilt (cima→baixo)", variable=self.tilt_en, selectcolor="#1e1e1e").grid(row=3,column=0, sticky="w", pady=(4,0))
        ctk.CTkLabel(adv_frame, text="Velocidade:").grid(row=3,column=1, sticky="e")
        self.tilt_speed = tk.DoubleVar(value=0.05)
        tk.Spinbox(adv_frame, from_=0.01, to=0.20, increment=0.01, variable=self.tilt_speed, width=6).grid(row=3,column=2, sticky="w", padx=(6,0))
        # Linha 4: Shake (tremor)
        self.shake_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(adv_frame, text="Shake (tremor)", variable=self.shake_en, selectcolor="#1e1e1e").grid(row=4,column=0, sticky="w", pady=(4,0))
        ctk.CTkLabel(adv_frame, text="Intensidade(px):").grid(row=4,column=1, sticky="e")
        self.shake_intensity = tk.IntVar(value=3)
        tk.Spinbox(adv_frame, from_=1, to=20, increment=1, variable=self.shake_intensity, width=6).grid(row=4,column=2, sticky="w", padx=(6,0))
        # Linha 5: Ken Burns (zoom + pan combinado)
        self.kenburns_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(adv_frame, text="Ken Burns (zoom+pan)", variable=self.kenburns_en, selectcolor="#1e1e1e").grid(row=5,column=0, sticky="w", pady=(4,0))
        ctk.CTkLabel(adv_frame, text="Intensidade:").grid(row=5,column=1, sticky="e")
        self.kenburns_intensity = tk.DoubleVar(value=0.15)
        tk.Spinbox(adv_frame, from_=0.05, to=0.30, increment=0.01, variable=self.kenburns_intensity, width=6).grid(row=5,column=2, sticky="w", padx=(6,0))
        for i in range(5): adv_frame.columnconfigure(i, weight=1)
        ctk.CTkLabel(f_vid, text="Transição (todas):").pack(side="left")
        self.transition = tk.StringVar(value="fade")
        ctk.CTkOptionMenu(f_vid, variable=self.transition, values=["sem","fade","dissolve","slide_left","slide_right","slide_up","slide_down","zoom_in","zoom_out","wipe_left","wipe_right"], width=120).pack(side="left", padx=(6,0))
        ctk.CTkLabel(f_vid, text="Duração (s):").pack(side="left", padx=(10,0))
        self.transition_dur = tk.DoubleVar(value=0.9)
        tk.Spinbox(f_vid, from_=0.0, to=3.0, increment=0.1, textvariable=self.transition_dur, width=6).pack(side="left")
        self.strict_cuts = tk.BooleanVar(value=True)
        ctk.CTkSwitch(f_vid, text="Cortes estritos (troca na borda)", variable=self.strict_cuts, selectcolor="#1e1e1e").pack(side="left", padx=(16,0))

        # ----- LEGENDAS (VOZ & KARAOKÊ) -----
        f_leg = ctk.CTkLabelFrame(self.cfg, text="📝 LEGENDAS — VOZ & KARAOKÊ", padx=10, pady=10)
        f_leg.pack(fill="x", pady=6)
        self.opt_leg = tk.BooleanVar(value=True)
        ctk.CTkSwitch(f_leg, text="Gerar & Queimar legendas ASS (karaokê)", variable=self.opt_leg, selectcolor="#1e1e1e").grid(row=0, column=0, columnspan=6, sticky="w")
        ctk.CTkLabel(f_leg, text="Modelo de voz (pasta):").grid(row=1, column=0, sticky="w", pady=(4,2))
        self.vosk_entry = ctk.CTkEntry(f_leg, width=500); self.vosk_entry.grid(row=1, column=1, sticky="w", padx=(6,0))
        ctk.CTkButton(f_leg, text="📂 Selecionar modelo", command=self.sel_modelo).grid(row=1, column=2, sticky="w", padx=(6,0))
        if self.vosk_dir and Path(self.vosk_dir).exists(): self.vosk_entry.insert(0, self.vosk_dir)
        ctk.CTkLabel(f_leg, text="(Instale 'vosk' com pip se necessário)").grid(row=1, column=3, sticky="w", padx=(6,0))
        ctk.CTkLabel(f_leg, text="Fonte:").grid(row=2, column=0, sticky="e", pady=(6,2))
        self.font_name = tk.StringVar(value="Bangers")
        ctk.CTkOptionMenu(f_leg, variable=self.font_name, values=["Bangers","Arial","Montserrat","Anton","Bebas Neue","Impact"], width=140).grid(row=2, column=1, sticky="w", padx=(6,0))
        self.uppercase = tk.BooleanVar(value=True)
        ctk.CTkSwitch(f_leg, text="MAIÚSCULAS", variable=self.uppercase, selectcolor="#1e1e1e").grid(row=2, column=2, sticky="w", padx=(20,0))
        ctk.CTkLabel(f_leg, text="Palavras/bloco:").grid(row=3, column=0, sticky="e")
        self.words_block = tk.IntVar(value=5)
        tk.Spinbox(f_leg, from_=1, to=200, increment=1, variable=self.words_block, width=6).grid(row=3, column=1, sticky="w", padx=(6,0))
        ctk.CTkLabel(f_leg, text="Tamanho (pt):").grid(row=3, column=2, sticky="e")
        self.font_size = tk.IntVar(value=56)
        tk.Spinbox(f_leg, from_=32, to=96, increment=2, textvariable=self.font_size, width=6).grid(row=3, column=3, sticky="w", padx=(6,0))
        ctk.CTkLabel(f_leg, text="Posição:").grid(row=4, column=0, sticky="e")
        self.pos = tk.StringVar(value="embaixo")
        ctk.CTkOptionMenu(f_leg, variable=self.pos, values=["topo","meio","meio-baixo","embaixo"], width=100).grid(row=4, column=1, sticky="w", padx=(6,0))
        ctk.CTkLabel(f_leg, text="MargemV(px):").grid(row=4, column=2, sticky="e")
        self.margin_v = tk.IntVar(value=80)
        tk.Spinbox(f_leg, from_=0, to=400, increment=5, textvariable=self.margin_v, width=6).grid(row=4, column=3, sticky="w", padx=(6,0))
        self.color1 = tk.StringVar(value="&H00FFFFFF&") # Branco
        self.outline1 = tk.StringVar(value="&H00000000&") # Preto
        self.motion_color = tk.StringVar(value="&H0000FFFF&") # Amarelo
        self.motion_outline = tk.StringVar(value="&H00000000&") # Preto
        
        import tkinter.colorchooser
        
        def _pick_color(var, btn, title):
            current_hex = ass_to_hex(var.get())
            _, hex_c = tkinter.colorchooser.askcolor(title=title, initialcolor=current_hex)
            if hex_c:
                var.set(hex_to_ass(hex_c))
                btn.configure(fg_color=hex_c)
        
        fr_colors = ctk.CTkFrame(f_leg)
        fr_colors.grid(row=5, column=0, columnspan=2, sticky="w", pady=(2,0))
        ctk.CTkLabel(fr_colors, text="Cores:").pack(side="left", padx=(0, 4))
        
        btn_c1 = ctk.CTkButton(fr_colors, width=20, fg_color=ass_to_hex(self.color1.get()))
        btn_c1.config(command=lambda: _pick_color(self.color1, btn_c1, "Cor Base"))
        btn_c1.pack(side="left", padx=2)
        
        btn_o1 = ctk.CTkButton(fr_colors, width=20, fg_color=ass_to_hex(self.outline1.get()))
        btn_o1.config(command=lambda: _pick_color(self.outline1, btn_o1, "Contorno Base"))
        btn_o1.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(fr_colors, text="Destq:").pack(side="left", padx=(0, 4))
        btn_mc = ctk.CTkButton(fr_colors, width=20, fg_color=ass_to_hex(self.motion_color.get()))
        btn_mc.config(command=lambda: _pick_color(self.motion_color, btn_mc, "Cor Destaque"))
        btn_mc.pack(side="left", padx=2)

        btn_mo = ctk.CTkButton(fr_colors, width=20, fg_color=ass_to_hex(self.motion_outline.get()))
        btn_mo.config(command=lambda: _pick_color(self.motion_outline, btn_mo, "Contorno Destaque"))
        btn_mo.pack(side="left", padx=2)
        self.hold = tk.BooleanVar(value=True)
        ctk.CTkSwitch(f_leg, text="Segurar nas pausas", variable=self.hold, selectcolor="#1e1e1e").grid(row=5, column=2, sticky="w", padx=(10,0))
        ctk.CTkLabel(f_leg, text="Até (s):").grid(row=5, column=3, sticky="e")
        self.hold_gap = tk.DoubleVar(value=2.0)
        tk.Spinbox(f_leg, from_=0.0, to=10.0, increment=0.1, variable=self.hold_gap, width=6).grid(row=5, column=4, sticky="w", padx=(6,0))
        for i in range(6): f_leg.columnconfigure(i, weight=1)

        # [E5] Smart Pacing: remoção de silêncio via FFmpeg
        f_sp = ctk.CTkFrame(f_leg)
        f_sp.grid(row=6, column=0, columnspan=6, sticky="w", pady=(8, 0))
        self.opt_smart_pacing = tk.BooleanVar(value=False)
        ctk.CTkSwitch(
            f_sp,
            text="✂️ Smart Pacing (Remover silêncios > 0.3s antes de transcrever)",
            variable=self.opt_smart_pacing, selectcolor="#1e1e1e",
            font=("Arial", 9, "bold")
        ).pack(side="left")
        ctk.CTkLabel(f_sp, text="  Limiar:").pack(side="left")
        self.smart_pacing_noise = tk.StringVar(value="-40dB")
        ctk.CTkOptionMenu(
            f_sp,
            variable=self.smart_pacing_noise,
            values=["-30dB", "-35dB", "-40dB", "-45dB", "-50dB"],
            width=7
        ).pack(side="left", padx=(4, 0))
        ctk.CTkLabel(f_sp, text="  Dur. mín. silêncio (s):").pack(side="left", padx=(10, 0))
        self.smart_pacing_dur = tk.DoubleVar(value=0.3)
        tk.Spinbox(f_sp, from_=0.1, to=2.0, increment=0.05, textvariable=self.smart_pacing_dur, width=5).pack(side="left", padx=(4, 0))

        # Auto-carregar mídia da estrutura padrão (./imagem e ./audio)
        try:
            # V2: prioriza vídeos como mídia de cena
            if not self.video_clips:
                vids = []
                for ext in ("*.mp4","*.mov","*.mkv","*.webm","*.avi"):
                    vids.extend([str(p) for p in IMAGEM_DIR.glob(ext)])
                try:
                    vids = sorted(vids, key=_natural_key)
                except Exception:
                    vids = sorted(vids)
                self.video_clips = vids
                # manter compatibilidade: imagens ficam vazias na V2
                self.images = []
                if self.video_clips:
                    self.lbl_midias.config(text=f"🎞️ {len(self.video_clips)} vídeo(s)")
                    self.log(f"{len(self.video_clips)} vídeo(s) importados (auto ./imagem)")
            if not self.audio_path:
                auds = []
                for ext in ("*.mp3","*.wav","*.m4a","*.aac"):
                    auds.extend([str(p) for p in AUDIO_DIR.glob(ext)])
                try:
                    auds = sorted(auds, key=_natural_key)
                except Exception:
                    auds = sorted(auds)
                if auds:
                    self.audio_path = auds[0]
                    self.lbl_audio.config(text=f"✅ {Path(self.audio_path).name}")
                    self.log(Path(self.audio_path).name)
            if not self.scenes_txt_path.get():
                txts = sorted(p for p in AUDIO_DIR.glob("*.txt"))
                if txts:
                    # Prioriza nome comum
                    pref = [p for p in txts if "prompt" in p.name.lower() or "cena" in p.name.lower()]
                    chosen = pref[0] if pref else txts[0]
                    self.scenes_txt_path.set(str(chosen))
                    self.log(f"TXT de cenas auto: {chosen.name}")
            self._check_ready()
        except Exception as e:
            self.log(f"⚠️ Auto-carregamento parcial falhou: {e}")

        # ----- MP4 FX -----
        if not HIDE_FX_UI:
            f_fx = ctk.CTkLabelFrame(self.cfg, text="🎞️ MP4 com fundo preto — até 2 camadas", padx=10, pady=10)
            f_fx.pack(fill="x", pady=6)
            ctk.CTkSwitch(f_fx, text="Ativar #1", variable=self.fx1_en, selectcolor="#1e1e1e").grid(row=0, column=0, sticky="w")
            ctk.CTkButton(f_fx, text="📁 Selecionar MP4 #1", command=lambda: self.sel_fx(1)).grid(row=0, column=1, sticky="w", padx=(8,0))
            self.fx1_lbl = ctk.CTkLabel(f_fx, text="(sem arquivo)"); self.fx1_lbl.grid(row=0, column=2, sticky="w", padx=(8,0))
            # Controles da camada #2 removidos
            ctk.CTkLabel(f_fx, text="Opacidade #1:").grid(row=2, column=0, sticky="e")
            tk.Spinbox(f_fx, from_=0.0, to=1.0, increment=0.05, variable=self.fx1_op, width=6).grid(row=2, column=1, sticky="w")
            # Opacidade #2 removida: camada 2 usa a mesma opacidade da #1
            ctk.CTkLabel(f_fx, text="Similaridade:").grid(row=3, column=0, sticky="e")
            tk.Spinbox(f_fx, from_=0.00, to=1.00, increment=0.01, textvariable=self.fx_key, width=6).grid(row=3, column=1, sticky="w")
            ctk.CTkLabel(f_fx, text="Maciez:").grid(row=3, column=2, sticky="e")
            tk.Spinbox(f_fx, from_=0.00, to=0.50, increment=0.01, textvariable=self.fx_blend, width=6).grid(row=3, column=3, sticky="w")
            for i in range(4): f_fx.columnconfigure(i, weight=1)

        # ----- EFEITO SONORO -----
        f_sfx = ctk.CTkLabelFrame(self.cfg, text="🔊 EFEITO SONORO", padx=10, pady=10)
        f_sfx.pack(fill="x", pady=6)
        ctk.CTkSwitch(f_sfx, text="Ativar", variable=self.sfx_en, selectcolor="#1e1e1e").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(f_sfx, text="📁 Selecionar áudio do efeito", command=self.sel_sfx).grid(row=0, column=1, sticky="w", padx=(8,0))
        self.sfx_lbl = ctk.CTkLabel(f_sfx, text="(sem arquivo)"); self.sfx_lbl.grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(f_sfx, text="Volume (0–1):").grid(row=1, column=0, sticky="e", pady=(8,0))
        tk.Spinbox(f_sfx, from_=0.0, to=1.0, increment=0.05, variable=self.sfx_vol, width=6).grid(row=1, column=1, sticky="w", pady=(8,0))

        # [E7] Ducking de Trilha: substituiu o gate brusco por sidechain compress suave
        self.sfx_duck_mode = tk.StringVar(value="Médio")
        ctk.CTkLabel(f_sfx, text="🎧 Ducking:", font=("Arial",9,"bold")).grid(row=1, column=2, sticky="e", pady=(8,0))
        ctk.CTkOptionMenu(
            f_sfx,
            variable=self.sfx_duck_mode,
            values=["Desligado", "Suave", "Médio", "Forte"],
            width=9
        ).grid(row=1, column=3, sticky="w", pady=(8,0), padx=(4,0))

        ctk.CTkLabel(f_sfx, text="Attack (ms):").grid(row=2, column=0, sticky="e")
        tk.Spinbox(f_sfx, from_=1, to=200, increment=1, textvariable=self.sfx_att, width=6).grid(row=2, column=1, sticky="w")
        ctk.CTkLabel(f_sfx, text="Release (ms):").grid(row=2, column=2, sticky="e")
        tk.Spinbox(f_sfx, from_=10, to=2000, increment=10, textvariable=self.sfx_rel, width=6).grid(row=2, column=3, sticky="w")
        for i in range(6): f_sfx.columnconfigure(i, weight=1)

        # [E9] SFX de Transição (woosh/impact sincronizado com B-Roll)
        f_sfx_tr = ctk.CTkFrame(f_sfx)
        f_sfx_tr.grid(row=3, column=0, columnspan=6, sticky="w", pady=(8, 0))
        self.opt_sfx_transition = tk.BooleanVar(value=False)
        self.sfx_transition_path = tk.StringVar(value="")
        ctk.CTkSwitch(
            f_sfx_tr, text="⚡ SFX de Transição (entra com B-Roll)",
            variable=self.opt_sfx_transition, selectcolor="#1e1e1e",
            font=("Arial", 9, "bold")
        ).pack(side="left")
        ctk.CTkEntry(f_sfx_tr, textvariable=self.sfx_transition_path, width=300).pack(side="left", padx=(8, 4))
        ctk.CTkButton(
            f_sfx_tr, text="📁",
            command=lambda: self.sfx_transition_path.set(
                filedialog.askopenfilename(
                    title="Selecionar SFX de transição",
                    filetypes=[("Áudio", "*.mp3 *.wav *.ogg *.aac")]
                ) or self.sfx_transition_path.get()
            )
        ).pack(side="left")
        ctk.CTkLabel(f_sfx_tr, text="  Vol:").pack(side="left", padx=(8,0))
        self.sfx_transition_vol = tk.DoubleVar(value=0.5)
        tk.Spinbox(f_sfx_tr, from_=0.05, to=1.0, increment=0.05,
                   textvariable=self.sfx_transition_vol, width=5).pack(side="left", padx=(2, 0))

        # ----- SAÍDA -----
        f_out = ctk.CTkLabelFrame(self.cfg, text="💾 SAÍDA", padx=10, pady=10)
        f_out.pack(fill="x", pady=6)
        ctk.CTkLabel(f_out, text="Nome do arquivo (MP4):").grid(row=0, column=0, sticky="e")
        self.out_name = tk.StringVar(value="video_karaoke.mp4")
        ctk.CTkEntry(f_out, textvariable=self.out_name, width=400).grid(row=0, column=1, sticky="w")
        for i in range(2): f_out.columnconfigure(i, weight=1)

        # ----- AÇÕES -----
        f_act = ctk.CTkLabelFrame(self.cfg, text="▶ AÇÕES", padx=10, pady=10)
        f_act.pack(fill="x", pady=6)
        self.btn_go = ctk.CTkButton(f_act, text="▶️ CRIAR VÍDEO (F9)", command=self.go_thread, font=("Arial",12,"bold"), padx=30, pady=8, state="disabled")
        self.btn_go.pack(fill="x")
        self.btn_rascunho = ctk.CTkButton(f_act, text="🎬 GERAR RASCUNHO (360p)", command=lambda: self.go_thread(draft=True), font=("Arial",10,"bold"), padx=10, pady=6)
        self.btn_rascunho.pack(fill="x", pady=(6,0))
        # Frame para barra de progresso + porcentagem
        prog_frame = ctk.CTkFrame(f_act)
        prog_frame.pack(fill="x", pady=6)
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(prog_frame, mode='determinate', variable=self.progress_var, maximum=100)
        self.progress.pack(side="left", fill="x", expand=True)
        self.progress_label = ctk.CTkLabel(prog_frame, text="0%", font=("Arial", 10, "bold"), width=60)
        self.progress_label.pack(side="right", padx=(6, 0))
        self._progress_mode = 'determinate'  # Rastrear modo atual
        root.bind("<F9>", lambda e: self.go_thread())

        # ----- Aba Mapeamento (conteúdo) -----
        self._build_mapping_tab()

        # ----- Aba Combinar Pares (novo) -----
        try:
            self._build_pairs_tab()
        except Exception:
            pass

        # ----- Marca d'água -----
        self._build_watermark_tab()

        # ----- Logs -----
        f_log = ctk.CTkLabelFrame(self.tab_log, text="📋 LOG", padx=10, pady=10)
        f_log.pack(fill="both", expand=True, pady=5)
        self.log_txt = ctk.CTkTextbox(f_log, height=200, font=("Consolas", 12))
        self.log_txt.pack(fill="both", expand=True, pady=(0, 6))
        # botão para limpar o log
        try:
            btn_clear = ctk.CTkButton(f_log, text="Limpar log", command=lambda: (self.log_txt.delete('1.0','end')))
            btn_clear.pack(fill="x", pady=(6,0))
        except Exception:
            pass

        # Limpeza automática de arquivos temporários órfãos de execuções anteriores
        try:
            _orphan_patterns = ["_seg_*.mp4", "temp_video_*.mp4", "temp_audio_16k*.wav",
                                "temp_stretch_*.mp4", "subs_*.ass", "_wm_proc_*.png", "_intro_temp_*.mp4"]
            _orphan_count = 0
            _orphan_bytes = 0
            for _pat in _orphan_patterns:
                for _fp in BASE_DIR.glob(_pat):
                    try:
                        _orphan_bytes += _fp.stat().st_size
                        _fp.unlink()
                        _orphan_count += 1
                    except Exception:
                        pass
            if _orphan_count > 0:
                self.log(f"[startup] 🧹 {_orphan_count} arquivo(s) temporário(s) órfão(s) removido(s) ({_orphan_bytes/1024/1024:.1f} MB liberados)")
        except Exception:
            pass

        self.log("Pronto para criar vídeos! (Vosk disponível: {})".format("sim" if VOSK_OK else "não"))
        if not VOSK_OK:
            self.log("Se quiser usar transcrição automática, instale 'vosk' (pip install vosk) e baixe um modelo em /models.")
        try:
            # inicia atualização periódica do status da licença
            try:
                self._update_license_status()
            except Exception:
                pass
        except Exception:
            pass

        # Se iniciou sem licença, entrar em tela bloqueada (modo limitado)
        try:
            if getattr(self, 'limited_mode', False):
                self._apply_limited_mode_ui()
        except Exception:
            pass

    # ---------- Aba Mapeamento ----------
    def _build_mapping_tab(self):
        f = ctk.CTkFrame(self.tab_map); f.pack(fill="both", expand=True, padx=10, pady=10)
        left = ctk.CTkFrame(f); left.pack(side="right", fill="both", expand=True, padx=(0,6))
        right = ctk.CTkFrame(f, width=320); right.pack(side="left", fill="y")

        # ============================================================
        # PAINEL ESQUERDO (grande): Entrada de texto direta
        # ============================================================
        # Cabeçalho do painel
        hdr = ctk.CTkFrame(left); hdr.pack(fill="x", pady=(0,4))
        ctk.CTkLabel(hdr, text="📝 Cola o Texto das Cenas Aqui", font=("Arial", 13, "bold")).pack(side="left")
        ctk.CTkLabel(hdr,
                 text="(dispensa arquivo TXT — mesmo formato do mapeamento inteligente)", font=("Arial", 8)).pack(side="left", padx=(8, 0))

        # Barra de ações do painel de texto
        bar = ctk.CTkFrame(left); bar.pack(fill="x", pady=(0, 4))

        def _clear_text():
            self.map_text.delete("1.0", "end")

        def _copy_from_txt():
            """Lê o arquivo TXT selecionado no campo 'Cenas (TXT):' e cola no painel."""
            p = self.scenes_txt_path.get().strip()
            if not p or not Path(p).exists():
                messagebox.showwarning("Aviso", "Nenhum arquivo TXT selecionado no campo 'Cenas (TXT):'.")
                return
            try:
                raw = Path(p).read_text(encoding="utf-8")
                self.map_text.delete("1.0", "end")
                self.map_text.insert("1.0", raw)
                self.log(f"[texto] Conteúdo importado do TXT: {Path(p).name}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao ler TXT: {e}")

        def _generate_from_text():
            """Gera mapping.json usando o texto colado no painel (mesmo fluxo do botão TXT)."""
            raw = self.map_text.get("1.0", "end").strip()
            # Ignorar se for o placeholder
            if not raw or raw.startswith("Cole aqui o texto das suas cenas"):
                messagebox.showwarning("Aviso", "Cole o texto das cenas no painel antes de gerar.")
                return
            # Salvar temporariamente como TXT e chamar o gerador existente
            tmp_file = BASE_DIR / "_cenas_for_generator.txt"
            try:
                tmp_file.write_text(raw, encoding="utf-8")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível criar arquivo temporário: {e}")
                return
            old_path = self.scenes_txt_path.get()
            self.scenes_txt_path.set(str(tmp_file))
            def _restore_and_run():
                try:
                    self._run_generate_mapping_external()
                finally:
                    # Restaurar o caminho original após a geração
                    self.scenes_txt_path.set(old_path)
                    try:
                        tmp_file.unlink()
                    except Exception:
                        pass
            threading.Thread(target=_restore_and_run, daemon=True).start()

        ctk.CTkButton(bar, text="⚡ Gerar mapping.json do texto",
                  font=("Arial", 10, "bold"),
                  command=_generate_from_text,
                  padx=12, pady=5).pack(side="left", padx=(0, 8))

        ctk.CTkButton(bar, text="📂 Importar do TXT selecionado",
                  command=_copy_from_txt,
                  padx=8, pady=5).pack(side="left", padx=(0, 8))

        ctk.CTkButton(bar, text="🗑️ Limpar",
                  command=_clear_text,
                  padx=8, pady=5).pack(side="left")

        # Dica de formato
        tip = ctk.CTkFrame(left); tip.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(tip,
                 text="💡 Formato: uma cena por linha separada por linha em branco. Cada bloco vira uma cena.", font=("Arial", 8), justify="left").pack(anchor="w")

        # Área de texto principal  
        txt_frame = ctk.CTkFrame(left); txt_frame.pack(fill="both", expand=True, pady=5)
        self.map_text = ctk.CTkTextbox(
            txt_frame,
            height=500,
            font=("Consolas", 14),
            wrap="word"
        )
        self.map_text.pack(fill="both", expand=True)

        # Placeholder visual quando vazio
        _placeholder = ("Cole aqui o texto das suas cenas...\n\n"
                        "Exemplo:\n"
                        "Cena 1 - descrição do que foi falado nesta cena.\n\n"
                        "Cena 2 - próxima cena com outro assunto.\n\n"
                        "(Cada bloco separado por linha em branco = 1 cena/vídeo)")

        def _on_focus_in(e):
            if self.map_text.get("1.0", "end").strip() == _placeholder.strip():
                self.map_text.delete("1.0", "end")
                self.map_text.config(fg="#e6edf3")

        def _on_focus_out(e):
            if not self.map_text.get("1.0", "end").strip():
                self.map_text.insert("1.0", _placeholder)
                self.map_text.config(fg="#444")

        self.map_text.insert("1.0", _placeholder)
        self.map_text.config(fg="#444")
        self.map_text.bind("<FocusIn>", _on_focus_in)
        self.map_text.bind("<FocusOut>", _on_focus_out)

        # Contador de caracteres / linhas
        self._map_text_info = tk.StringVar(value="0 linhas | 0 caracteres")
        ctk.CTkLabel(left, textvariable=self._map_text_info, font=("Arial", 8)).pack(anchor="e", pady=(2, 0))

        def _update_counter(e=None):
            try:
                content = self.map_text.get("1.0", "end")
                if content.strip() == _placeholder.strip():
                    self._map_text_info.set("0 linhas | 0 caracteres")
                    return
                lines = [l for l in content.splitlines() if l.strip()]
                self._map_text_info.set(f"{len(lines)} linhas | {len(content.strip())} caracteres")
            except Exception:
                pass
        self.map_text.bind("<KeyRelease>", _update_counter)

        # ============================================================
        # PAINEL DIREITO (sidebar): controles existentes (sem mudança)
        # ============================================================

        
        # ========== SELETOR DE JOB PARA MAPEAMENTO ==========
        job_frame = ctk.CTkLabelFrame(right, text="📁 Mapeamento por Job", padx=8, pady=6)
        job_frame.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(job_frame, text="Editando mapping para:").pack(anchor="w")
        job_selector = ctk.CTkFrame(job_frame)
        job_selector.pack(fill="x", pady=(4,0))
        tk.Radiobutton(job_selector, text="Job 1", variable=self.current_mapping_job, value=1, selectcolor="#1e1e1e",
                       command=self._switch_mapping_job).pack(side="left", padx=(0,10))
        tk.Radiobutton(job_selector, text="Job 2", variable=self.current_mapping_job, value=2, selectcolor="#1e1e1e",
                       command=self._switch_mapping_job).pack(side="left")
        # Labels de status
        self.job1_status = ctk.CTkLabel(job_frame, text="Job 1: (vazio)")
        self.job1_status.pack(anchor="w", pady=(4,0))
        self.job2_status = ctk.CTkLabel(job_frame, text="Job 2: (vazio)")
        self.job2_status.pack(anchor="w")
        
        # área principal de visualização (mantida vazia — sem mensagens)
        # O conteúdo de controle foi movido para a coluna lateral (à esquerda)
        ctk.CTkLabel(right, text="Opções", font=("Arial",11,"bold")).pack(anchor="w", pady=(0,6))
        ctk.CTkSwitch(right, text="Usar mapeamento manual (quando disponível)", variable=self.use_manual_map).pack(anchor="w", pady=(0,6))
        ctk.CTkLabel(right, text="Palavras por bloco (auto):").pack(anchor="w")
        tk.Spinbox(right, from_=5, to=200, increment=1, variable=self.words_block, width=6).pack(anchor="w", pady=(0,8))
        ctk.CTkLabel(right, text="Preview do mapping", font=("Arial",11,"bold")).pack(anchor="w", pady=(8,6))
        self.mapping_preview = tk.Listbox(right, height=18)
        self.mapping_preview.pack(fill="both", expand=True)
        # Botões extras: carregar mapping e gerador inteligente
        ctk.CTkButton(right, text="Carregar mapping.json (arquivo...)", command=self.load_mapping_from_dialog).pack(fill="x", pady=(6,2))
        ctk.CTkButton(right, text="Recarregar mapping.json local", command=self.reload_mapping_from_file).pack(fill="x", pady=(0,8))
        if not HIDE_GENERATOR_UI:
            box_gen = ctk.CTkLabelFrame(right, text="Gerador inteligente", padx=6, pady=6)
            box_gen.pack(fill="x", pady=(0,8))
            # Campo para selecionar Python personalizado (para acelerar gerador usando outra venv)
            ctk.CTkLabel(box_gen, text="Python:").grid(row=0, column=0, sticky="e")
            self.python_gen_var = tk.StringVar(value=getattr(self, "python_gen_exe", ""))
            ctk.CTkEntry(box_gen, textvariable=self.python_gen_var, width=200).grid(row=0, column=1, sticky="w")
            def _sel_py_exe():
                p = filedialog.askopenfilename(title="Selecionar python.exe", filetypes=[("Python","python.exe"),("Todos","*.*")])
                if not p: return
                self.python_gen_exe = p
                self.python_gen_var.set(p)
                self._save_settings()
                self.log(f"[gerador] Python externo definido: {p}")
            ctk.CTkButton(box_gen, text="Selecionar", command=_sel_py_exe).grid(row=0, column=2, sticky="w", padx=(6,0))
            ctk.CTkLabel(box_gen, text="Cenas (TXT):").grid(row=1, column=0, sticky="e")
            ctk.CTkEntry(box_gen, textvariable=self.scenes_txt_path, width=200).grid(row=1, column=1, sticky="w")
            ctk.CTkButton(box_gen, text="TXT", command=self.select_scenes_txt).grid(row=1, column=2, sticky="w", padx=(6,0))
            ctk.CTkButton(box_gen, text="Gerar mapping.json (inteligente)", command=self.generate_mapping_external).grid(row=2, column=0, columnspan=3, sticky="we", pady=(8,0))
            ctk.CTkLabel(box_gen, text="Modelo:").grid(row=3, column=0, sticky="e", pady=(6,0))
            ctk.CTkOptionMenu(box_gen, variable=self.gen_model_size, values=["tiny","base","small","medium"], width=100).grid(row=3, column=1, sticky="w", pady=(6,0))
            ctk.CTkLabel(box_gen, text="Device:").grid(row=4, column=0, sticky="e")
            ctk.CTkOptionMenu(box_gen, variable=self.gen_device, values=["cpu","cuda"], width=100).grid(row=4, column=1, sticky="w")
            ctk.CTkLabel(box_gen, text="Compute:").grid(row=5, column=0, sticky="e")
            ctk.CTkOptionMenu(box_gen, variable=self.gen_compute, values=["int8","float16","float32"], width=100).grid(row=5, column=1, sticky="w")
            ctk.CTkLabel(box_gen, text="Transcriber:").grid(row=6, column=0, sticky="e")
            ctk.CTkOptionMenu(box_gen, variable=self.gen_transcriber, values=["faster","openai"], width=100).grid(row=6, column=1, sticky="w")
            for r in range(7): box_gen.rowconfigure(r, weight=1)
            for c in range(3): box_gen.columnconfigure(c, weight=1)
            # Importador de 'Originals' via script externo
            ctk.CTkLabel(right, text="Importar 'Originals' (TXT):").pack(anchor="w", pady=(6,2))
            self.import_punct = tk.StringVar(value='none')
            ctk.CTkOptionMenu(right, variable=self.import_punct, values=['both','comma','period','none'], width=100).pack(anchor='w')
            ctk.CTkButton(right, text="Importar Originals (TXT)", command=self.import_originals).pack(fill="x", pady=(6,8))
        if MAPPING_JSON.exists():
            try:
                with open(MAPPING_JSON, "r", encoding="utf-8") as f:
                    self.mapping_timeline = json.load(f)
                    self._show_mapping_preview(self.mapping_timeline)
            except Exception:
                pass

    def load_blocks_file(self):
        p = filedialog.askopenfilename(title="Selecione TXT com blocos", filetypes=[("Text","*.txt"),("All","*.*")])
        if not p: return
        try:
            raw = Path(p).read_text(encoding="utf-8")
            self.map_text.delete("1.0","end"); self.map_text.insert("1.0", raw)
            self.log("Blocos carregados.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def import_originals(self):
        """Abre seletor de TXT, chama `scripts/extract_originals.py` e cola o resultado na área de Mapeamento."""
        def _run(path):
            try:
                script = BASE_DIR / "scripts" / "extract_originals.py"
                if not script.exists():
                    messagebox.showerror("Erro", f"Script não encontrado: {script}")
                    return
                punct = str(self.import_punct.get() or 'none')
                cmd = [sys.executable, str(script), str(path), "--punctuation", punct]
                self.log(f"[import] executando: {cmd}")
                # Executar o extractor no diretório do arquivo de input para evitar problemas de caminho/privilegios
                try:
                    run_cwd = str(Path(path).parent)
                except Exception:
                    run_cwd = str(BASE_DIR)
                r = subprocess.run(cmd, cwd=run_cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
                # Log stdout/stderr do extractor para diagnóstico
                if r.stdout and r.stdout.strip():
                    for ln in (r.stdout or '').splitlines():
                        self.log(f"[extractor stdout] {ln}")
                if r.stderr and r.stderr.strip():
                    for ln in (r.stderr or '').splitlines():
                        self.log(f"[extractor stderr] {ln}")
                if r.returncode != 0:
                    out = (r.stderr or r.stdout or '').strip()
                    messagebox.showerror("Erro", f"Falha ao executar extractor (code={r.returncode}):\n{out}")
                    return
                # caminho esperado padrão
                out_path = Path(path).parent / "originals_numbered.txt"
                if not out_path.exists():
                    # tenta localizar automaticamente o arquivo gerado em locais prováveis
                    self.log(f"[import] arquivo esperado não encontrado: {out_path} — procurando alternativas...")
                    candidates = []
                    try:
                        # procurar no diretório do input por arquivos 'originals*.txt'
                        pdir = Path(path).parent
                        for p in sorted(pdir.glob('originals*.txt'), key=lambda x: x.stat().st_mtime, reverse=True):
                            candidates.append(p)
                    except Exception:
                        pass
                    try:
                        # procurar em mapeing/originals
                        for p in sorted((MAPPING_DIR / 'originals').glob('originals*.txt'), key=lambda x: x.stat().st_mtime, reverse=True):
                            candidates.append(p)
                    except Exception:
                        pass
                    try:
                        # procurar na pasta do app
                        for p in sorted(Path(BASE_DIR).glob('originals*.txt'), key=lambda x: x.stat().st_mtime, reverse=True):
                            candidates.append(p)
                    except Exception:
                        pass
                    # remover duplicados preservando ordem
                    seen = set(); uniq = []
                    for c in candidates:
                        try:
                            k = str(c.resolve())
                        except Exception:
                            k = str(c)
                        if k not in seen:
                            seen.add(k); uniq.append(c)
                    if uniq:
                        found = uniq[0]
                        self.log(f"[import] encontrado arquivo alternativo: {found}")
                        out_path = found
                    else:
                        messagebox.showwarning("Aviso", f"Arquivo de saída não encontrado: {out_path}")
                        return
                txt = out_path.read_text(encoding='utf-8')
                # tenta colar na área de mapeamento se existir
                try:
                    if hasattr(self, 'map_text'):
                        self.map_text.delete('1.0', 'end')
                        self.map_text.insert('1.0', txt)
                        # também atualiza o campo de TXT de cenas para apontar para este arquivo
                        try:
                            # Copiar também para uma pasta organizada dentro de MAPPING_DIR (mapeing/originals)
                            try:
                                dest_dir = MAPPING_DIR / "originals"
                                dest_dir.mkdir(parents=True, exist_ok=True)
                                dest = dest_dir / out_path.name
                                shutil.copy(str(out_path), str(dest))
                                # Aponta o campo para a cópia centralizada
                                self.scenes_txt_path.set(str(dest))
                                self.log(f"[import] Copiado para: {dest}")
                            except Exception:
                                # se copy falhar, mantemos o arquivo original como fonte
                                self.scenes_txt_path.set(str(out_path))
                        except Exception:
                            try: self.scenes_txt_path.set(str(out_path))
                            except Exception: pass
                        self.log(f"[import] Conteúdo inserido na área de mapeamento ({out_path})")
                        messagebox.showinfo("OK", f"Importado e colado na área de mapeamento:\n{out_path}")
                    else:
                        # se não existir, apenas notifica onde foi salvo
                        try:
                            try:
                                dest_dir = MAPPING_DIR / "originals"
                                dest_dir.mkdir(parents=True, exist_ok=True)
                                dest = dest_dir / out_path.name
                                shutil.copy(str(out_path), str(dest))
                                self.scenes_txt_path.set(str(dest))
                                self.log(f"[import] Copiado para: {dest}")
                            except Exception:
                                self.scenes_txt_path.set(str(out_path))
                        except Exception:
                            try: self.scenes_txt_path.set(str(out_path))
                            except Exception: pass
                        messagebox.showinfo("OK", f"Arquivo gerado: {out_path}\nNão foi encontrada a área de mapeamento para colar automaticamente.")
                except Exception as e:
                    messagebox.showerror("Erro", str(e))
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        p = filedialog.askopenfilename(title="Selecione TXT com blocos (Original:)", filetypes=[("Text","*.txt"),("All","*.*")])
        if not p:
            return
        threading.Thread(target=_run, args=(p,), daemon=True).start()

    def save_mapping_file(self):
        if not self.mapping_timeline:
            messagebox.showwarning("Aviso","Nenhum mapping gerado para salvar.")
            return
        try:
            MAPPING_DIR.mkdir(parents=True, exist_ok=True)
            with open(MAPPING_JSON, "w", encoding="utf-8") as f:
                json.dump(self.mapping_timeline, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("OK", f"mapping salvo em: {MAPPING_JSON}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def generate_mapping_preview(self):
        raw = self.map_text.get("1.0","end").strip()
        blocks_parsed = parse_manual_text_blocks(raw)
        self.manual_blocks = blocks_parsed
        try:
            # Sem vídeos: mostra um preview textual (para validar o parser)
            if not self.video_clips:
                self.mapping_preview.delete(0, "end")
                if not blocks_parsed:
                    self.mapping_preview.insert("end", "(nenhum bloco detectado)")
                else:
                    for i, (num, txt) in enumerate(blocks_parsed):
                        idx = (num if num is not None else i + 1)
                        short = (txt[:60] + "...") if len(txt) > 60 else txt
                        self.mapping_preview.insert("end", f"(sem vídeos) bloco {idx}: \"{short}\"")
                messagebox.showwarning(
                    "Sem vídeos",
                    "Para ver o preview com arquivos, importe os vídeos (cenas) na aba Configuração."
                )
                self.mapping_timeline = {"audio_duration": None, "images": []}
                return

            # Com imagens: gera timeline normalmente
            words = getattr(self, "_last_transcript_words", [])
            dur = getattr(self, "_last_audio_duration", None)
            if not dur and self.audio_path:
                dur = self._audio_duration(self.audio_path)

            intro_off = self.get_intro_offset()
            media_items = self.get_media_items()
            
            # Obter arquivo do intro (se habilitado)
            intro_file = None
            if intro_off > 0:
                intro_var = getattr(self, 'intro_video_path', None)
                if intro_var and intro_var.get():
                    intro_file = intro_var.get()
            
            # Log detalhado para debug
            self.log(f"[mapping] Intro offset: {intro_off:.2f}s")
            self.log(f"[mapping] Intro file: {Path(intro_file).name if intro_file else 'Nenhum'}")
            self.log(f"[mapping] Total de blocos de texto: {len(blocks_parsed)}")
            self.log(f"[mapping] Total de imagens (excluindo intro): {len(media_items)}")
            self.log(f"[mapping] Total de palavras transcritas: {len(words)}")
            
            timeline = build_image_timeline_from_words_and_manual(
                blocks_parsed, media_items, words, audio_duration=dur, intro_offset=intro_off, intro_file=intro_file
            )
            
            # Log do timeline gerado
            self.log(f"[mapping] Timeline gerado ({len(timeline)} cenas):")
            for i, item in enumerate(timeline):
                is_intro = item.get('is_intro', False)
                prefix = "[INTRO] " if is_intro else ""
                self.log(f"  {prefix}[{i+1}] {Path(item['file']).name}: {item['start']:.2f}s -> {item['end']:.2f}s")
            
            self.mapping_timeline = {"audio_duration": dur, "intro_offset": intro_off, "images": timeline}
            
            # Salvar no job atual
            self._save_current_mapping_to_job()
            
            # Salvar também no arquivo JSON
            job_num = self.current_mapping_job.get()
            MAPPING_DIR.mkdir(parents=True, exist_ok=True)
            mapping_file = MAPPING_DIR / f"mapping_job{job_num}.json"
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(self.mapping_timeline, f, ensure_ascii=False, indent=2)
            # Também salvar no mapping.json padrão (compatibilidade)
            with open(MAPPING_JSON, "w", encoding="utf-8") as f:
                json.dump(self.mapping_timeline, f, ensure_ascii=False, indent=2)

            self._show_mapping_preview(self.mapping_timeline)
            messagebox.showinfo(
                "Pronto",
                f"Mapping gerado e salvo para Job {job_num} (preview atualizado). "
                "Ative 'Usar mapeamento manual' para aplicá-lo ao renderizar."
            )
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _show_mapping_preview(self, mapping):
        self.mapping_preview.delete(0, "end")
        if not mapping or "images" not in mapping:
            self.mapping_preview.insert("end","(nenhum mapping)")
            return
        for i, it in enumerate(mapping["images"]):
            s = f"{i+1}. {Path(it['file']).name} — {it.get('start',0):.3f}s -> {it.get('end',0):.3f}s — \"{(it.get('text','')[:60]+'...') if len(it.get('text',''))>60 else it.get('text','') }\""
            self.mapping_preview.insert("end", s)

    def _switch_mapping_job(self):
        """Troca entre mapeamento do Job 1 e Job 2"""
        job_num = self.current_mapping_job.get()
        if job_num == 1:
            self.mapping_timeline = self.mapping_timeline_job1
        else:
            self.mapping_timeline = self.mapping_timeline_job2
        
        # Atualizar preview
        self._show_mapping_preview(self.mapping_timeline)
        self._update_job_mapping_status()
        self.log(f"[mapping] Editando mapeamento do Job {job_num}")

    def _save_current_mapping_to_job(self):
        """Salva o mapping_timeline atual no job selecionado"""
        job_num = self.current_mapping_job.get()
        if job_num == 1:
            self.mapping_timeline_job1 = self.mapping_timeline
        else:
            self.mapping_timeline_job2 = self.mapping_timeline
        self._update_job_mapping_status()

    def _update_job_mapping_status(self):
        """Atualiza os labels de status dos mappings"""
        try:
            if self.mapping_timeline_job1 and isinstance(self.mapping_timeline_job1, dict):
                n1 = len(self.mapping_timeline_job1.get('images', []))
                self.job1_status.config(text=f"Job 1: ✅ {n1} imagens")
            else:
                self.job1_status.config(text="Job 1: (vazio)")
            
            if self.mapping_timeline_job2 and isinstance(self.mapping_timeline_job2, dict):
                n2 = len(self.mapping_timeline_job2.get('images', []))
                self.job2_status.config(text=f"Job 2: ✅ {n2} imagens")
            else:
                self.job2_status.config(text="Job 2: (vazio)")
        except Exception:
            pass

    def _get_mapping_for_job(self, job_num):
        """Retorna o mapping correto para o job especificado"""
        if job_num == 1:
            return self.mapping_timeline_job1
        elif job_num == 2:
            return self.mapping_timeline_job2
        return self.mapping_timeline

    # ---------- Mapping externo: carregar / gerar ----------
    def load_mapping_from_dialog(self):
        p = filedialog.askopenfilename(title="Selecionar mapping.json", filetypes=[("JSON","*.json"),("Todos","*.*")])
        if not p: return
        try:
            data = json.loads(Path(p).read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "images" not in data:
                messagebox.showerror("Erro","Arquivo inválido (sem chave 'images').")
                return
            self.mapping_timeline = data
            try:
                MAPPING_DIR.mkdir(parents=True, exist_ok=True)
                MAPPING_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                pass
            self._show_mapping_preview(data)
            self.use_manual_map.set(True)
            self.log(f"Mapping externo carregado: {p}")
            messagebox.showinfo("OK","Mapping carregado e salvo como mapping.json.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha carregar mapping: {e}")

    def reload_mapping_from_file(self):
        if not MAPPING_JSON.exists():
            messagebox.showwarning("Aviso","Nenhum mapping.json local encontrado.")
            return
        try:
            data = json.loads(MAPPING_JSON.read_text(encoding="utf-8"))
            self.mapping_timeline = data
            self._show_mapping_preview(data)
            self.log("mapping.json recarregado.")
            messagebox.showinfo("OK","mapping.json recarregado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao recarregar mapping: {e}")

    def select_scenes_txt(self):
        p = filedialog.askopenfilename(title="Selecionar TXT com cenas", filetypes=[("Text","*.txt"),("Todos","*.*")])
        if not p: return
        try:
            Path(p).read_text(encoding="utf-8")
            self.scenes_txt_path.set(p)
            self.log(f"TXT de cenas selecionado: {os.path.basename(p)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo: {e}")

    def generate_mapping_external(self):
        threading.Thread(target=self._run_generate_mapping_external, daemon=True).start()

    def _run_generate_mapping_external(self):
        try:
            if not self.audio_path or not Path(self.audio_path).exists():
                messagebox.showwarning("Aviso","Selecione o áudio primeiro.")
                return
            if not self.video_clips:
                messagebox.showwarning("Aviso","Selecione os vídeos (cenas) primeiro.")
                return
            txt_path = self.scenes_txt_path.get().strip()
            tmp_file = None
            if not txt_path:
                raw = ""
                try:
                    raw = self.map_text.get("1.0","end").strip()
                except Exception:
                    raw = ""
                if not raw:
                    messagebox.showwarning("Aviso","Forneça um TXT de cenas ou cole o texto na área de mapeamento.")
                    return
                tmp_file = BASE_DIR / "_cenas_for_generator.txt"
                tmp_file.write_text(raw, encoding="utf-8")
                txt_path = str(tmp_file)
            
            MAPPING_DIR.mkdir(parents=True, exist_ok=True)

            # Novo fluxo: se o TXT estiver no formato numerado (1 "texto"),
            # geramos o mapping.json internamente (cena N = texto N) e pulamos o gerador externo.
            try:
                raw_num = Path(txt_path).read_text(encoding='utf-8')
            except Exception:
                try:
                    raw_num = Path(txt_path).read_text(encoding='cp1252')
                except Exception:
                    raw_num = Path(txt_path).read_text(encoding='latin-1')

            num_re_direct = re.compile(r"^\s*(\d+)\s*[\"“”'’]?\s*(.*)$")
            num_lines = []
            for ln in raw_num.splitlines():
                m = num_re_direct.match(ln)
                if m:
                    idx = int(m.group(1))
                    txt_line = (m.group(2) or '').strip().strip('“”"\'’ ')
                    if txt_line:
                        num_lines.append((idx, txt_line))
            if num_lines:
                self.log("[generator] TXT numerado detectado — gerando mapping internamente (cena N = texto N)...")
                # Priorizar Vosk (retorna word-level nativo) depois Whisper como fallback
                words = []
                dur = getattr(self, "_last_audio_duration", None)
                if not dur and self.audio_path:
                    dur = self._audio_duration(self.audio_path)
                
                # VERIFICAR se cache é válido para este áudio
                cached_words = getattr(self, "_last_transcript_words", None)
                cached_audio = getattr(self, "_last_audio_path", None)
                cache_valid = False
                
                if cached_words and cached_audio and str(cached_audio) == str(self.audio_path):
                    min_expected = max(10, int(dur / 2)) if dur else 50
                    if len(cached_words) >= min_expected:
                        words = cached_words
                        cache_valid = True
                        self.log(f"[generator] Usando {len(words)} palavras em cache (mesmo áudio)")
                    else:
                        self.log(f"[generator] Cache incompatível: {len(cached_words)} palavras para {dur:.0f}s de áudio")
                        self._last_transcript_words = None
                elif cached_words:
                    self.log(f"[generator] Áudio diferente - descartando {len(cached_words)} palavras antigas")
                    self._last_transcript_words = None
                
                if not cache_valid:
                    # [E5] Smart Pacing: remover silêncios do áudio antes de transcrever
                    tmp_wav = BASE_DIR / f"temp_audio_16k_{os.getpid()}.wav"
                    convert_to_wav16k(self.ffmpeg, Path(self.audio_path), tmp_wav)
                    if getattr(self, 'opt_smart_pacing', None) and self.opt_smart_pacing.get():
                        try:
                            noise_thr = getattr(self, 'smart_pacing_noise', None)
                            dur_min   = getattr(self, 'smart_pacing_dur',   None)
                            noise_str = noise_thr.get() if noise_thr else "-40dB"
                            dur_val   = float(dur_min.get()) if dur_min else 0.3
                            paced_wav = self.audio_pipeline.remover_silencio_ffmpeg(str(tmp_wav), noise_str, dur_val)
                            if paced_wav and Path(paced_wav).exists():
                                tmp_wav.unlink(missing_ok=True)
                                tmp_wav = Path(paced_wav)
                                dur = self._audio_duration(str(tmp_wav)) or dur
                                self.log(f"[E5] ✂️ Smart Pacing aplicado. Nova duração: {dur:.1f}s")
                        except Exception as _esp:
                            self.log(f"[E5] ⚠️ Smart Pacing ignorado: {_esp}")
                            
                    try:
                        # PRIORIDADE 1: Vosk (word-level timestamps nativos)
                        model_dir = Path(self.vosk_entry.get().strip() or self.vosk_dir or "")
                        if VOSK_OK and model_dir.exists() and validate_vosk_dir(model_dir):
                            self.log("[generator] Transcrevendo com Vosk (melhor word-level)...")
                            tmp_wav = BASE_DIR / "temp_audio_16k.wav"
                            convert_to_wav16k(self.ffmpeg, Path(self.audio_path), tmp_wav)
                            words = vosk_transcribe(tmp_wav, model_dir, log_fn=self.log)
                            self._last_transcript_words = words
                            self._last_audio_path = str(self.audio_path)
                        else:
                            raise RuntimeError("Vosk indisponível")
                    except Exception as e_vosk:
                        self.log(f"[generator] Vosk indisponível/erro: {e_vosk} — tentando Whisper...")
                        # PRIORIDADE 2: Whisper como fallback
                        try:
                            if WHISPER_OK:
                                self.log("[generator] Transcrevendo com Whisper...")
                                words = whisper_transcribe(str(self.audio_path), log_fn=self.log)
                                self._last_transcript_words = words
                                self._last_audio_path = str(self.audio_path)
                            else:
                                raise RuntimeError("Whisper também indisponível")
                        except Exception as e_whisper:
                            self.log(f"[generator] Whisper indisponível/erro: {e_whisper} — seguindo sem transcrição.")
                            words = []

                media_items = self.get_media_items()
                blocks_parsed = [(idx, text) for (idx, text) in num_lines]
                intro_off = self.get_intro_offset()
                intro_file = self.intro_video_path.get() if intro_off > 0 and hasattr(self, 'intro_video_path') else None
                timeline = build_image_timeline_from_words_and_manual(blocks_parsed, media_items, words, audio_duration=dur, intro_offset=intro_off, intro_file=intro_file)
                mapping = {"audio_duration": dur, "intro_offset": intro_off, "images": timeline}
                with open(MAPPING_JSON, "w", encoding="utf-8") as f:
                    json.dump(mapping, f, ensure_ascii=False, indent=2)
                self.mapping_timeline = mapping
                self._show_mapping_preview(mapping)
                self.use_manual_map.set(True)
                self.log("[generator] mapping.json gerado internamente a partir do TXT numerado.")
                messagebox.showinfo("OK","mapping.json gerado internamente a partir do TXT numerado.")
                return

            # ========== USAR FUNÇÃO INTEGRADA (SEM SCRIPT EXTERNO) ==========
            MAPPING_DIR.mkdir(parents=True, exist_ok=True)
            
            # calcula chunk-seconds adaptativo
            # Regra: em CPU manter 60s para evitar longas esperas; em GPU usar 60s (<10min) ou 190s (>=10min)
            try:
                aud_dur = None
                try:
                    aud_dur = float(self._audio_duration(self.audio_path)) if self.audio_path else None
                except Exception:
                    aud_dur = None
                dev = str(self.gen_device.get() or "cpu").lower()
                if dev == "cpu":
                    chunk = 60
                else:
                    if aud_dur is None:
                        chunk = 60
                    else:
                        chunk = 60 if aud_dur < 600.0 else 190
            except Exception:
                chunk = 60
            self.log(f"[generator] chunk-seconds escolhido: {chunk}s (audio_dur={aud_dur})")

            self._start_progress_indeterminate(); self.nb.select(self.tab_log)
            self.log("[generator] Iniciando gerador INTEGRADO...")
            
            # ========== USAR FUNÇÃO INTEGRADA ==========
            # Obter info do intro se habilitado
            intro_file_gen = None
            intro_dur_gen = 0.0
            self.log(f"[generator] Verificando intro... get_intro_offset()={self.get_intro_offset()}")
            if self.get_intro_offset() > 0:
                intro_var = getattr(self, 'intro_video_path', None)
                if intro_var and intro_var.get():
                    intro_file_gen = intro_var.get()
                    intro_dur_gen = self.get_intro_offset()
                    self.log(f"[generator] ✅ Intro detectado: {Path(intro_file_gen).name} ({intro_dur_gen:.1f}s)")
                else:
                    self.log(f"[generator] ⚠️ Intro habilitado mas caminho não definido!")
            else:
                self.log(f"[generator] Intro não habilitado (offset=0)")
            
            # Obter imagens (SEM o intro)
            imgs = [str(p) for p in self.get_media_items()]
            self.log(f"[generator] Imagens para mapeamento: {len(imgs)}")
            
            # Obter palavras transcritas - VERIFICAR se correspondem ao áudio atual
            words = None
            cached_words = getattr(self, "_last_transcript_words", None)
            cached_audio = getattr(self, "_last_audio_path", None)
            
            # Só usar cache se for o MESMO áudio e tiver palavras suficientes
            if cached_words and cached_audio and str(cached_audio) == str(self.audio_path):
                # Verificar se número de palavras faz sentido (mínimo ~1 palavra por segundo)
                min_expected = max(10, int(aud_dur / 2))  # pelo menos 1 palavra a cada 2 segundos
                if len(cached_words) >= min_expected:
                    words = cached_words
                    self.log(f"[generator] Usando {len(words)} palavras em cache (mesmo áudio)")
                else:
                    self.log(f"[generator] Cache tem apenas {len(cached_words)} palavras para {aud_dur:.0f}s - forçando nova transcrição")
                    self._last_transcript_words = None
            else:
                if cached_words:
                    self.log(f"[generator] Áudio mudou - descartando {len(cached_words)} palavras antigas")
                    self._last_transcript_words = None

            # Se ainda não temos palavras, transcrever AQUI (para suportar inglês também)
            # usando a escolha do usuário (Vosk primeiro, depois faster/openai whisper).
            if not words:
                # Heurística simples: inferir idioma pelo nome da pasta do modelo Vosk selecionado
                lang_hint = "pt"
                try:
                    model_hint = str(self.vosk_entry.get().strip() or self.vosk_dir or "").lower()
                    if any(k in model_hint for k in ("en-us", "-en-", "_en_", "\\en\\", "/en/")):
                        lang_hint = "en"
                except Exception:
                    lang_hint = "pt"

                try:
                    model_dir = Path(self.vosk_entry.get().strip() or self.vosk_dir or "")
                except Exception:
                    model_dir = Path("")

                try:
                    # PRIORIDADE 1: Vosk (se tiver modelo válido selecionado)
                    if VOSK_OK and model_dir.exists() and validate_vosk_dir(model_dir):
                        self.log(f"[generator] Transcrevendo com Vosk (lang_hint={lang_hint})...")
                        tmp_wav = BASE_DIR / "temp_audio_16k.wav"
                        convert_to_wav16k(self.ffmpeg, Path(self.audio_path), tmp_wav)
                        words = vosk_transcribe(tmp_wav, model_dir, log_fn=self.log)
                    else:
                        raise RuntimeError("Vosk indisponível ou modelo inválido")
                except Exception as e_vosk:
                    self.log(f"[generator] Vosk indisponível/erro: {e_vosk}")
                    # PRIORIDADE 2: Whisper (faster/openai)
                    try:
                        choice = str(self.gen_transcriber.get() or "faster").lower()
                    except Exception:
                        choice = "faster"
                    try:
                        if choice == "faster" and FASTER_WHISPER_OK:
                            self.log(f"[generator] Transcrevendo com faster-whisper (lang={lang_hint})...")
                            words = faster_whisper_transcribe(str(self.audio_path), log_fn=self.log, chunk_duration=chunk, language=lang_hint)
                        elif WHISPER_OK:
                            self.log(f"[generator] Transcrevendo com openai/whisper (lang={lang_hint})...")
                            words = whisper_transcribe(str(self.audio_path), log_fn=self.log, chunk_duration=chunk, language=lang_hint)
                        else:
                            words = []
                            self.log("[generator] Nenhum transcritor disponível (Vosk/Whisper/faster-whisper)")
                    except Exception as e_wh:
                        self.log(f"[generator] Falha na transcrição (whisper): {e_wh}")
                        words = []

                # Atualizar cache se conseguimos palavras
                try:
                    if words and isinstance(words, list):
                        self._last_transcript_words = words
                        self._last_audio_path = str(self.audio_path)
                        self.log(f"[generator] Cache atualizado: {len(words)} palavras para este áudio")
                except Exception:
                    pass
            
            # Chamar função integrada
            result = generate_mapping_integrated(
                audio_file=str(self.audio_path),
                texto_file=str(txt_path),
                imagens_files=imgs,
                output_file=str(MAPPING_JSON),
                intro_file=intro_file_gen,
                intro_duration=intro_dur_gen,
                audio_duration=aud_dur,
                words=words,
                log_fn=self.log
            )
            
            rc = 0 if result else 1
            
            # Salvar palavras transcritas e mapping para uso posterior
            if result and isinstance(result, dict):
                self.mapping_timeline = result
                # Salvar palavras transcritas no cache (se a função retornou)
                transcribed_words = result.pop("_transcribed_words", None)
                if transcribed_words:
                    self._last_transcript_words = transcribed_words
                    self._last_audio_path = str(self.audio_path)
                    self.log(f"[generator] Cache atualizado: {len(transcribed_words)} palavras para este áudio")
            
            if rc != 0:
                self.log(f"[generator] falhou (code={rc})")
                messagebox.showerror("Erro", "Gerador de mapeamento falhou. Veja os logs.")
                return
            
            self.log("[generator] mapping.json gerado com sucesso.")
            self.reload_mapping_from_file()
            self.use_manual_map.set(True)
            messagebox.showinfo("OK", "mapping.json gerado e carregado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no gerador: {e}")
        finally:
            try: self._stop_progress()
            except Exception: pass
            if tmp_file and Path(tmp_file).exists():
                try: Path(tmp_file).unlink()
                except Exception: pass

    # ---------- UI: Marca d'água ----------
    def _build_watermark_tab(self):
        # Container principal com grid para melhor controle do layout
        main = ctk.CTkFrame(self.tab_wm)
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ========== LINHA SUPERIOR: Imagem (esquerda) + Efeito (direita) ==========
        top_row = ctk.CTkFrame(main)
        top_row.pack(fill="x", pady=(0,5))
        
        # ----- COLUNA ESQUERDA: Marca d'Água - Imagem -----
        box_img = ctk.CTkLabelFrame(top_row, text="Marca d'Água - Imagem", padx=8, pady=5)
        box_img.pack(side="left", fill="both", expand=True, padx=(0,3))
        
        self.wm_img_en = tk.BooleanVar(value=False)
        row = 0
        ctk.CTkSwitch(box_img, text="Ativar", variable=self.wm_img_en, selectcolor="#1e1e1e").grid(row=row,column=0,sticky="w")
        ctk.CTkButton(box_img, text="Selecionar imagem", command=self.sel_wm_img).grid(row=row,column=1,sticky="w", padx=2)
        
        row += 1
        self.wm_img_path = tk.StringVar(value="")
        ctk.CTkLabel(box_img, textvariable=self.wm_img_path).grid(row=row,column=0,columnspan=2,sticky="w")
        
        row += 1
        ctk.CTkLabel(box_img, text="Remover fundo:").grid(row=row, column=0, sticky="w")
        self.wm_remove = tk.StringVar(value="nenhum")
        rem_frame = ctk.CTkFrame(box_img)
        rem_frame.grid(row=row, column=1, sticky="w")
        for txt, val in [("Nenhum","nenhum"), ("Preto","preto"), ("Verde","verde"), ("Ambos","ambos")]:
            tk.Radiobutton(rem_frame, text=txt, variable=self.wm_remove, value=val, selectcolor="#1e1e1e").pack(side="left")
        
        row += 1
        ctk.CTkLabel(box_img, text="Tolerância:").grid(row=row,column=0, sticky="e")
        self.wm_tol = tk.IntVar(value=30)
        tk.Spinbox(box_img, from_=0, to=255, increment=1, textvariable=self.wm_tol, width=5).grid(row=row,column=1, sticky="w")
        
        row += 1
        ctk.CTkLabel(box_img, text="Opacidade:").grid(row=row,column=0,sticky="e")
        self.wm_img_op = tk.DoubleVar(value=1.0)
        tk.Scale(box_img, from_=0.0, to=1.0, resolution=0.05, orient="horizontal", variable=self.wm_img_op, length=150).grid(row=row,column=1,sticky="w")
        
        row += 1
        ctk.CTkLabel(box_img, text="Tamanho %:").grid(row=row,column=0,sticky="e")
        self.wm_img_scale = tk.DoubleVar(value=0.25)
        tk.Scale(box_img, from_=0.05, to=0.75, resolution=0.01, orient="horizontal", variable=self.wm_img_scale, length=150).grid(row=row,column=1,sticky="w")
        
        row += 1
        ctk.CTkLabel(box_img, text="Posição:").grid(row=row,column=0,sticky="e")
        self.wm_img_pos = tk.StringVar(value="bottom-right")
        ctk.CTkOptionMenu(box_img, variable=self.wm_img_pos, values=["top-left","top-right","bottom-left","bottom-right","center"], width=120).grid(row=row,column=1,sticky="w")
        
        row += 1
        off_frame = ctk.CTkFrame(box_img)
        off_frame.grid(row=row, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(off_frame, text="Offset X:").pack(side="left")
        self.wm_img_x = tk.IntVar(value=20)
        tk.Spinbox(off_frame, from_=0, to=400, increment=1, textvariable=self.wm_img_x, width=5).pack(side="left", padx=2)
        ctk.CTkLabel(off_frame, text="Y:").pack(side="left", padx=(8,0))
        self.wm_img_y = tk.IntVar(value=20)
        tk.Spinbox(off_frame, from_=0, to=400, increment=1, textvariable=self.wm_img_y, width=5).pack(side="left", padx=2)
        
        # ----- COLUNA DIREITA: Efeito animado (vídeo com fundo verde) -----
        box_eff = ctk.CTkLabelFrame(top_row, text="Efeito Animado (vídeo verde)", padx=8, pady=5)
        box_eff.pack(side="left", fill="both", expand=True, padx=(3,0))
        
        self.wm_eff_en = tk.BooleanVar(value=False)
        row = 0
        ctk.CTkSwitch(box_eff, text="Ativar", variable=self.wm_eff_en, selectcolor="#1e1e1e").grid(row=row,column=0,sticky="w")
        ctk.CTkButton(box_eff, text="Selecionar vídeo", command=self.sel_wm_effect).grid(row=row,column=1,sticky="w", padx=2)
        
        row += 1
        self.wm_eff_path = tk.StringVar(value="")
        ctk.CTkLabel(box_eff, textvariable=self.wm_eff_path).grid(row=row,column=0,columnspan=2,sticky="w")
        
        row += 1
        time_frame = ctk.CTkFrame(box_eff)
        time_frame.grid(row=row, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(time_frame, text="Iniciar:").pack(side="left")
        self.wm_eff_min = tk.IntVar(value=0)
        tk.Spinbox(time_frame, from_=0, to=999, increment=1, textvariable=self.wm_eff_min, width=4).pack(side="left", padx=2)
        ctk.CTkLabel(time_frame, text="min").pack(side="left")
        self.wm_eff_sec = tk.DoubleVar(value=0.0)
        tk.Spinbox(time_frame, from_=0, to=59.9, increment=0.5, textvariable=self.wm_eff_sec, width=5).pack(side="left", padx=2)
        ctk.CTkLabel(time_frame, text="seg").pack(side="left")

        row += 1
        # Exibir o efeito automaticamente em 3 tempos do vídeo:
        # 1) 1 minuto, 2) metade do vídeo, 3) 1 minuto antes de acabar
        self.wm_eff_three_times = tk.BooleanVar(value=False)
        ctk.CTkSwitch(
            box_eff,
            text="3 tempos (1min / metade / -1min)",
            variable=self.wm_eff_three_times,
            selectcolor="#1e1e1e",
        ).grid(row=row, column=0, columnspan=2, sticky="w")
        
        row += 1
        ctk.CTkLabel(box_eff, text="Tamanho %:").grid(row=row,column=0,sticky="e")
        self.wm_eff_scale = tk.DoubleVar(value=0.25)
        tk.Scale(box_eff, from_=0.05, to=0.75, resolution=0.01, orient="horizontal", variable=self.wm_eff_scale, length=150).grid(row=row,column=1,sticky="w")
        
        row += 1
        ctk.CTkLabel(box_eff, text="Posição:").grid(row=row,column=0,sticky="e")
        self.wm_eff_pos = tk.StringVar(value="bottom-right")
        ctk.CTkOptionMenu(box_eff, variable=self.wm_eff_pos, values=["top-left","top-right","bottom-left","bottom-right","center"], width=120).grid(row=row,column=1,sticky="w")
        
        row += 1
        off_frame2 = ctk.CTkFrame(box_eff)
        off_frame2.grid(row=row, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(off_frame2, text="Offset X:").pack(side="left")
        self.wm_eff_x = tk.IntVar(value=20)
        tk.Spinbox(off_frame2, from_=0, to=400, increment=1, variable=self.wm_eff_x, width=5).pack(side="left", padx=2)
        ctk.CTkLabel(off_frame2, text="Y:").pack(side="left", padx=(8,0))
        self.wm_eff_y = tk.IntVar(value=20)
        tk.Spinbox(off_frame2, from_=0, to=400, increment=1, textvariable=self.wm_eff_y, width=5).pack(side="left", padx=2)
        
        row += 1
        ctk.CTkLabel(box_eff, text="Chroma sim:").grid(row=row,column=0,sticky="e")
        self.wm_eff_similarity = tk.DoubleVar(value=0.15)
        tk.Scale(box_eff, from_=0.01, to=0.5, resolution=0.01, orient="horizontal", variable=self.wm_eff_similarity, length=150).grid(row=row,column=1,sticky="w")
        
        row += 1
        ctk.CTkLabel(box_eff, text="Chroma blend:").grid(row=row,column=0,sticky="e")
        self.wm_eff_blend = tk.DoubleVar(value=0.1)
        tk.Scale(box_eff, from_=0.0, to=0.5, resolution=0.01, orient="horizontal", variable=self.wm_eff_blend, length=150).grid(row=row,column=1,sticky="w")
        
        row += 1
        ctk.CTkLabel(box_eff, text="Despill (borda):").grid(row=row,column=0,sticky="e")
        self.wm_eff_despill = tk.DoubleVar(value=0.15)
        tk.Scale(box_eff, from_=0.0, to=0.5, resolution=0.01, orient="horizontal", variable=self.wm_eff_despill, length=150).grid(row=row,column=1,sticky="w")
        
        row += 1
        ctk.CTkLabel(box_eff, text="Volume:").grid(row=row,column=0,sticky="e")
        self.wm_eff_vol = tk.DoubleVar(value=1.0)
        tk.Scale(box_eff, from_=0.0, to=2.0, resolution=0.05, orient="horizontal", variable=self.wm_eff_vol, length=150).grid(row=row,column=1,sticky="w")
        
        # ========== LINHA DO MEIO: Texto (compacto, largura total) ==========
        box_txt = ctk.CTkLabelFrame(main, text="Marca d'Água - Texto", padx=8, pady=3)
        box_txt.pack(fill="x", pady=(0,5))
        
        txt_row = ctk.CTkFrame(box_txt)
        txt_row.pack(fill="x")
        
        self.wm_txt_en = tk.BooleanVar(value=False)
        ctk.CTkSwitch(txt_row, text="Ativar", variable=self.wm_txt_en, selectcolor="#1e1e1e").pack(side="left")
        ctk.CTkLabel(txt_row, text="Texto:").pack(side="left", padx=(10,2))
        self.wm_txt = tk.StringVar(value="Seu Texto Aqui")
        ctk.CTkEntry(txt_row, textvariable=self.wm_txt, width=200).pack(side="left", padx=2)
        ctk.CTkLabel(txt_row, text="Fonte:").pack(side="left", padx=(10,2))
        self.wm_txt_font = tk.StringVar(value="Arial")
        ctk.CTkOptionMenu(txt_row, variable=self.wm_txt_font, values=["Arial","Bangers","Impact","Montserrat","Anton","Bebas Neue"], width=100).pack(side="left", padx=2)
        ctk.CTkLabel(txt_row, text="Tam:").pack(side="left", padx=(10,2))
        self.wm_txt_size = tk.IntVar(value=36)
        tk.Spinbox(txt_row, from_=12, to=128, increment=1, textvariable=self.wm_txt_size, width=4).pack(side="left", padx=2)
        ctk.CTkLabel(txt_row, text="Cor:").pack(side="left", padx=(10,2))
        self.wm_txt_color = tk.StringVar(value="#FFFFFF")
        ctk.CTkEntry(txt_row, textvariable=self.wm_txt_color, width=80).pack(side="left", padx=2)
        
        txt_row2 = ctk.CTkFrame(box_txt)
        txt_row2.pack(fill="x", pady=(3,0))
        
        ctk.CTkLabel(txt_row2, text="Opacidade:").pack(side="left")
        self.wm_txt_op = tk.DoubleVar(value=1.0)
        tk.Scale(txt_row2, from_=0.0, to=1.0, resolution=0.05, orient="horizontal", variable=self.wm_txt_op, length=100).pack(side="left", padx=2)
        ctk.CTkLabel(txt_row2, text="Posição:").pack(side="left", padx=(15,2))
        self.wm_txt_pos = tk.StringVar(value="top-left")
        ctk.CTkOptionMenu(txt_row2, variable=self.wm_txt_pos, values=["top-left","top-right","bottom-left","bottom-right","center"], width=120).pack(side="left", padx=2)
        self.wm_txt_bold = tk.BooleanVar(value=True)
        ctk.CTkSwitch(txt_row2, text="Negrito", variable=self.wm_txt_bold, selectcolor="#1e1e1e").pack(side="left", padx=(15,0))
        self.wm_txt_shadow = tk.BooleanVar(value=True)
        ctk.CTkSwitch(txt_row2, text="Sombra", variable=self.wm_txt_shadow, selectcolor="#1e1e1e").pack(side="left", padx=5)
        
        # ========== ÁREA GRANDE: Preview (ocupa todo o resto) ==========
        try:
            self._create_wm_preview_widgets(main)
            self._register_wm_preview_traces()
            try: self._update_wm_preview()
            except Exception: pass
        except Exception:
            pass

    # ---------- Aba Combinar Pares (UI + lógica) ----------
    def _build_pairs_tab(self):
        f = ctk.CTkFrame(self.tab_pairs)
        f.pack(fill="x", pady=6)
        box = ctk.CTkLabelFrame(f, text="🔗 Combinar Pares de Vídeo", padx=10, pady=10)
        box.pack(fill="x", pady=6)
        ctk.CTkButton(box, text="📁 Selecionar vídeos (ordem será preservada)", command=self.sel_pairs_videos).pack(fill="x")
        self.pairs_listbox = tk.Listbox(box, height=6)
        self.pairs_listbox.pack(fill="x", pady=(6,4))
        frm = ctk.CTkFrame(box)
        frm.pack(fill="x")
        self.pairs_add_to_project = tk.BooleanVar(value=True)
        ctk.CTkSwitch(frm, text="Adicionar pares/concat ao projeto", variable=self.pairs_add_to_project, selectcolor="#1e1e1e").pack(side="left")

        # Novas opções do Combinar Pares
        frm2 = ctk.CTkFrame(box)
        frm2.pack(fill="x", pady=2)
        ctk.CTkLabel(frm2, text="Formato:").pack(side="left")
        self.pairs_orient = tk.StringVar(value="vertical")
        tk.Radiobutton(frm2, text="Vertical", variable=self.pairs_orient, value="vertical", selectcolor="#1e1e1e").pack(side="left")
        tk.Radiobutton(frm2, text="Horizontal", variable=self.pairs_orient, value="horizontal", selectcolor="#1e1e1e").pack(side="left", padx=(0,15))
        
        self.pairs_keep_audio = tk.BooleanVar(value=False)
        ctk.CTkSwitch(frm2, text="Manter Áudio", variable=self.pairs_keep_audio, selectcolor="#1e1e1e").pack(side="left")
        
        ctk.CTkLabel(frm2, text="Vol:").pack(side="left", padx=(5,0))
        self.pairs_audio_vol = tk.DoubleVar(value=1.0)
        tk.Spinbox(frm2, from_=0.0, to=2.0, increment=0.1, variable=self.pairs_audio_vol, width=5).pack(side="left")

        btnbar = ctk.CTkFrame(box); btnbar.pack(fill="x", pady=(6,0))
        ctk.CTkButton(btnbar, text="▶️ Consolidar Continuidades (Smart)", command=self._export_consolidated_continuations).pack(side="left")
        ctk.CTkButton(btnbar, text="▶️ Gerar pares (concat simples)", command=self._create_pairs).pack(side="right")
        ctk.CTkButton(btnbar, text="▶️ Concat sequência (todos)", command=self._create_sequence).pack(side="right", padx=(0,6))

        ctk.CTkLabel(box, text="Observação: concat re-encoda no formato escolhido; áudio pode ser mantido se os vídeos o possuírem.").pack(fill="x", pady=(6,0))
        # estado
        self._pairs_videos = []

    def sel_pairs_videos(self):
        files = filedialog.askopenfilenames(title="Selecione vídeos para combinar (ordem)",
                    filetypes=[("Vídeos","*.mp4 *.mov *.mkv *.webm *.avi"), ("Todos","*.*")])
        if not files: return
        try:
            lst = list(files)
            try:
                lst = sorted(lst, key=_natural_key)
            except Exception:
                pass
            self._pairs_videos = lst
            self.pairs_listbox.delete(0, "end")
            for p in self._pairs_videos:
                self.pairs_listbox.insert("end", Path(p).name)
            self.log(f"{len(self._pairs_videos)} vídeo(s) selecionados para combinar.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _create_pairs(self):
        if not getattr(self, '_pairs_videos', None):
            messagebox.showwarning("Aviso","Nenhum vídeo selecionado para combinar.")
            return
        out_dir = BASE_DIR / "paired_videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        vids = list(self._pairs_videos)
        created = []
        for i in range(0, len(vids), 2):
            a = vids[i]
            b = vids[i+1] if i+1 < len(vids) else None
            if not b:
                # se ímpar, apenas copia o último para saída
                outp = out_dir / f"pair_{i+1:03d}.mp4"
                try:
                    shutil.copy(a, outp)
                    created.append(str(outp))
                    self.log(f"Par {i+1} criado (único): {outp.name}")
                except Exception as e:
                    self.log(f"Falha copiar único: {e}")
                continue
            outp = out_dir / f"pair_{i+1+1:03d}.mp4"
            try:
                ok = self._concat_pair_ffmpeg(a, b, str(outp))
                if ok:
                    created.append(str(outp))
                    self.log(f"Par criado: {outp.name}")
                else:
                    self.log(f"Falha criar par: {Path(a).name} + {Path(b).name}")
            except Exception as e:
                self.log(f"Erro ao criar par: {e}")

        # adicionar ao projeto se desejado
        if self.pairs_add_to_project.get() and created:
            try:
                for p in created:
                    # adiciona como vídeo_clips (prioridade de vídeos)
                    self.video_clips.append(p)
                self.lbl_midias.config(text=f"📷 {len(self.images)} imagem(ns) + 🎞️ {len(self.video_clips)} vídeo(s)")
                self.log(f"{len(created)} pares adicionados ao projeto.")
            except Exception:
                pass
        messagebox.showinfo("Pronto", f"{len(created)} pares gerados em:\n{out_dir}")

    def _detect_video_orientation(self, video_path):
        """Detecta a orientação real do vídeo usando ffprobe. Retorna (W, H)."""
        try:
            import json as _json
            cmd = [self.ffprobe, '-v', 'error', '-select_streams', 'v:0',
                   '-show_entries', 'stream=width,height,codec_tag_string',
                   '-of', 'json', str(video_path)]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
            if r.returncode == 0 and r.stdout:
                data = _json.loads(r.stdout)
                s = data.get('streams', [{}])[0]
                w = int(s.get('width', 0))
                h = int(s.get('height', 0))
                if w > 0 and h > 0:
                    return (w, h)
        except Exception:
            pass
        # Fallback: usa configuração da UI
        if str(getattr(self, 'orient', tk.StringVar(value='horizontal')).get()) == 'vertical':
            return (1080, 1920)
        return (1920, 1080)

    def _concat_pair_ffmpeg(self, a, b, outp):
        """Concatena dois vídeos simples re-encodificando vídeo e possivelmente áudio."""
        try:
            orient = getattr(self, 'pairs_orient', tk.StringVar(value='vertical')).get()
            W, H = (1080, 1920) if orient == 'vertical' else (1920, 1080)
            fps = int(getattr(self, 'fps', 30) or 30)
            
            keep_audio = getattr(self, 'pairs_keep_audio', tk.BooleanVar(value=False)).get()
            vol = getattr(self, 'pairs_audio_vol', tk.DoubleVar(value=1.0)).get()
            
            fc_lines = [
                f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}[v0]",
                f"[1:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}[v1]"
            ]
            if keep_audio:
                # pad/resample para evitar erro de concat se um for silencioso (mas exige áudio no input)
                fc_lines.append(f"[0:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={vol:.3f}[a0]")
                fc_lines.append(f"[1:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={vol:.3f}[a1]")
                fc_lines.append(f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[outv][outa]")
                map_args = ["-map", "[outv]", "-map", "[outa]"]
            else:
                fc_lines.append(f"[v0][v1]concat=n=2:v=1:a=0[outv]")
                map_args = ["-map", "[outv]"]

            fc = ';'.join(fc_lines)
            
            cmd = [self.ffmpeg, "-y", "-i", str(a), "-i", str(b), "-filter_complex", fc,
                   *map_args,
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
                   "-preset", "veryfast", "-crf", "20",
                   "-movflags", "+faststart",
                   outp]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if r.returncode == 0:
                return True
            else:
                self.log(f"[pairs] ffmpeg erro: {r.stderr or r.stdout}")
                return False
        except Exception as e:
            self.log(f"[pairs] exceção: {e}")
            return False

    def _concat_group_safe(self, group):
        """Concatena um grupo de vídeos em um único arquivo temporário."""
        import tempfile as _tempfile
        out_dir = BASE_DIR / "paired_videos"
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp = out_dir / f"_tmp_group_{os.getpid()}_{id(group)}.mp4"
        try:
            orient = getattr(self, 'pairs_orient', tk.StringVar(value='vertical')).get()
            W, H = (1080, 1920) if orient == 'vertical' else (1920, 1080)
            fps = int(getattr(self, 'fps', 30) or 30)
            
            keep_audio = getattr(self, 'pairs_keep_audio', tk.BooleanVar(value=False)).get()
            vol = getattr(self, 'pairs_audio_vol', tk.DoubleVar(value=1.0)).get()

            inputs = []
            fc_lines = []
            v_labels = []
            a_labels = []
            
            for i, p in enumerate(group):
                inputs += ["-i", str(p)]
                fc_lines.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}[v{i}]")
                v_labels.append(f"[v{i}]")
                if keep_audio:
                    fc_lines.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={vol:.3f}[a{i}]")
                    a_labels.append(f"[a{i}]")

            if keep_audio:
                concat = ''.join(v_labels) + ''.join(a_labels) + f"concat=n={len(group)}:v=1:a=1[outv][outa]"
                map_args = ["-map", "[outv]", "-map", "[outa]"]
            else:
                concat = ''.join(v_labels) + f"concat=n={len(group)}:v=1:a=0[outv]"
                map_args = ["-map", "[outv]"]
                
            fc_lines.append(concat)
            fc = ';'.join(fc_lines)
            
            cmd = [self.ffmpeg, "-y", *inputs, "-filter_complex", fc,
                   *map_args,
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
                   "-preset", "veryfast", "-crf", "20",
                   "-movflags", "+faststart", str(tmp)]
            r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if r.returncode != 0:
                self.log(f"[concat_group] ffmpeg erro: {(r.stderr or '')[:800]}")
                raise RuntimeError("ffmpeg concat_group falhou")
            return str(tmp)
        except Exception as e:
            self.log(f"[concat_group] erro: {e}")
            raise


    def _create_sequence(self):
        """Concatena todos os vídeos selecionados em uma única sequência na ordem (natural)."""
        if not getattr(self, '_pairs_videos', None):
            messagebox.showwarning("Aviso","Nenhum vídeo selecionado para concat.")
            return
        try:
            vids = list(self._pairs_videos)
            try:
                vids = sorted(vids, key=_natural_key)
            except Exception:
                pass
            out_dir = BASE_DIR / "paired_videos"
            out_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            outp = out_dir / f"concat_seq_{ts}.mp4"

            orient = getattr(self, 'pairs_orient', tk.StringVar(value='vertical')).get()
            W, H = (1080, 1920) if orient == 'vertical' else (1920, 1080)
            fps = int(getattr(self, 'fps', 30) or 30)
            self.log(f"[concat] Orientação escolhida: {W}x{H}")

            keep_audio = getattr(self, 'pairs_keep_audio', tk.BooleanVar(value=False)).get()
            vol = getattr(self, 'pairs_audio_vol', tk.DoubleVar(value=1.0)).get()

            inputs = []
            fc_lines = []
            v_labels = []
            a_labels = []
            
            for i, p in enumerate(vids):
                inputs += ["-i", str(p)]
                fc_lines.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}[v{i}]")
                v_labels.append(f"[v{i}]")
                if keep_audio:
                    fc_lines.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={vol:.3f}[a{i}]")
                    a_labels.append(f"[a{i}]")

            if keep_audio:
                concat = ''.join(v_labels) + ''.join(a_labels) + f"concat=n={len(vids)}:v=1:a=1[outv][outa]"
                map_args = ["-map", "[outv]", "-map", "[outa]"]
            else:
                concat = ''.join(v_labels) + f"concat=n={len(vids)}:v=1:a=0[outv]"
                map_args = ["-map", "[outv]"]
                
            fc_lines.append(concat)
            fc = ';'.join(fc_lines)
            
            cmd = [self.ffmpeg, "-y", *inputs, "-filter_complex", fc,
                   *map_args,
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
                   "-preset", "veryfast", "-crf", "20",
                   "-movflags", "+faststart",
                   str(outp)]

            self.log(f"[concat] executando FFmpeg com {len(vids)} entradas…")
            r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if r.returncode != 0:
                self.log(f"[concat] ffmpeg stderr: {(r.stderr or '')[:1500]}")
                raise RuntimeError("ffmpeg concat falhou.")

            # adicionar ao projeto se desejado
            if self.pairs_add_to_project.get():
                try:
                    self.video_clips.append(str(outp))
                    self.lbl_midias.config(text=f"📷 {len(self.images)} imagem(ns) + 🎞️ {len(self.video_clips)} vídeo(s)")
                except Exception:
                    pass

            messagebox.showinfo("Pronto", f"Concat concluído em:\n{outp}")
            self.log(f"Concat OK: {outp}")
        except Exception as e:
            self.log(f"[concat] erro: {e}")
            messagebox.showerror("Erro", str(e))

    def _export_consolidated_continuations(self):
        """Função standalone da Aba 2 que consolida vídeos de continuação e exporta o resultado final."""
        if not getattr(self, '_pairs_videos', None):
            messagebox.showwarning("Aviso", "Nenhum vídeo selecionado.")
            return
            
        vids = list(self._pairs_videos)
        try: vids = sorted(vids, key=_natural_key)
        except Exception: pass
        
        out_dir = BASE_DIR / "paired_videos" / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        new_clips = []
        current_group = []
        
        for clip in vids:
            name = Path(clip).name.lower()
            # BUG FIX: detecta também vídeos em subpasta "_cont" (padrão AutoFlow Apollo)
            full_path_lower = str(clip).lower().replace('\\', '/')
            is_cont = (
                'cont_' in name or '_cont' in name or 'cont-' in name or
                '/_cont/' in full_path_lower or full_path_lower.endswith('/_cont')
            )
            if is_cont and current_group:
                current_group.append(clip)
            else:
                if current_group:
                    new_clips.append(current_group)
                current_group = [clip]
                
        if current_group:
            new_clips.append(current_group)
            
        if not new_clips: return
        
        self.log(f"[smart-export] Processando {len(vids)} vídeos para {len(new_clips)} saídas finais...")
        
        for i, group in enumerate(new_clips, start=1):
            outp = out_dir / f"cena_{i:02d}.mp4"
            if len(group) == 1:
                shutil.copy2(group[0], outp)
                self.log(f"Cena {i:02d} -> {Path(group[0]).name} (copiado)")
            else:
                temp_merged = self._concat_group_safe(group)
                shutil.move(temp_merged, outp)
                self.log(f"Cena {i:02d} -> {len(group)} vídeos unidos (iniciando em {Path(group[0]).name})")
                
        messagebox.showinfo("Pronto", f"Exportação consolidada concluída!\n{len(new_clips)} vídeos exportados em:\n{out_dir}")
        try:
            os.startfile(out_dir)
        except Exception:
            pass

    # ---------- Logo ----------
    def _load_logo(self):
        for name in ("logo.jpeg","logo.jpg","logo.png"):
            p = BASE_DIR / name
            if p.exists():
                try:
                    im = Image.open(p).convert("RGBA")
                    max_w, max_h = 260, 260
                    im.thumbnail((max_w, max_h), Image.LANCZOS)
                    self._logo_img = ImageTk.PhotoImage(im)
                    self.logo_lbl.config(image=self._logo_img)
                    return
                except Exception:
                    pass
        try:
            self.logo_lbl.config(text="Coloque seu arquivo\nlogo.jpeg\nna pasta do app", font=("Arial", 12, "bold"))
        except Exception:
            pass

    def _ensure_limited_panel(self):
        # BYPASS: Desativar painel de bloqueio completamente
        return

    def _apply_limited_mode_ui(self):
        # BYPASS: Desativar restrições de UI completamente
        return

    def _clear_limited_mode_ui(self):
        """Re-ativa toda a UI quando licença válida."""
        try:
            if hasattr(self, 'left'):
                for w in self.left.winfo_children():
                    try:
                        if isinstance(w, ctk.CTkButton):
                            w.config(state='normal')
                    except Exception:
                        pass
            # Esconder painel limitado e restaurar notebook
            try:
                if getattr(self, '_limited_panel', None) is not None:
                    self._limited_panel.pack_forget()
            except Exception:
                pass
            try:
                if hasattr(self, 'nb'):
                    self.nb.pack(fill='both', expand=True)
            except Exception:
                pass

            # Recriar o bind do F9 (igual ao init)
            try:
                self.root.bind('<F9>', lambda e: self.go_thread())
            except Exception:
                pass
        except Exception:
            pass

    # ---------- utilitários ----------
    def _abrir_pasta(self, p: Path):
        try:
            p.mkdir(parents=True, exist_ok=True)
            if os.name == "nt": os.startfile(str(p))
            elif sys.platform == "darwin": subprocess.Popen(["open", str(p)])
            else: subprocess.Popen(["xdg-open", str(p)])
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _save_settings(self):
        data = {}
        try:
            if SETTINGS_JSON.exists():
                loaded = json.loads(SETTINGS_JSON.read_text(encoding="utf-8", errors="replace"))
                if isinstance(loaded, dict):
                    data.update(loaded)
        except Exception:
            data = {}
        data["vosk_dir"] = self.vosk_dir or ""
        try:
            SETTINGS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _load_settings(self):
        try:
            data = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
            self.vosk_dir = data.get("vosk_dir") or ""
        except Exception:
            self.vosk_dir = ""
        
        # Validar caminho do modelo. Se inválido, tentar fallback para modelo embutido.
        # Isso corrige falhas quando configurações são importadas de outro PC/usuário.
        if not self.vosk_dir or not Path(self.vosk_dir).exists():
            if DEFAULT_MODEL_DIR.exists():
                self.vosk_dir = str(DEFAULT_MODEL_DIR)
                self.log(f"Modelo Vosk configurado não encontrado. Usando padrão: {self.vosk_dir}")

    # ---------- Licença: leitura e exibição de validade ----------
    def _get_license_payload(self):
        """Tenta ler `license.key` e verificar com `public.pem`. Retorna payload dict ou None."""
        try:
            _ensure_license_check_importable()
        except Exception:
            pass
            
        # BYPASS: Sempre retornar licença TRIAL INFINITA (conforme solicitado pelo usuário)
        return {
            "type": "vip", 
            "expiration": "2099-12-31", 
            "hwid": "bypass", 
            "exp": "4102358400",
            "trial": True,
            "trial_remaining_seconds": 999999999
        }

        # 0) Bridge token gravado pela V1 (curta duração) para garantir que V2 herde o desbloqueio
        # quando V1 já está em trial/licença.
        try:
            if license_check is not None:
                bridge_path = BASE_DIR / 'license_bridge.token'
                if bridge_path.exists():
                    try:
                        tok = bridge_path.read_text(encoding='utf-8', errors='replace').strip()
                    except Exception:
                        tok = ''
                    if tok:
                        p = license_check.verify_bridge_token(tok)
                        if p and isinstance(p, dict):
                            # Ajusta remaining do trial para ficar “correndo” a partir do token
                            if p.get('trial'):
                                try:
                                    # Como o token tem validade curta, a aproximação é suficiente:
                                    # a V2 vai recalcular via license_check normalmente nos próximos ticks.
                                    rem = int(p.get('trial_remaining_seconds') or 0)
                                    if rem > 0:
                                        p['trial_remaining_seconds'] = rem
                                except Exception:
                                    pass
                            return p
        except Exception:
            pass

        try:
            import license_utils
        except Exception:
            return None
        try:
            pub_path_user = BASE_DIR / 'public.pem'
            pub_path_bundle = BUNDLE_DIR / 'public.pem'
            public_pem = None
            if pub_path_user.exists():
                try:
                    public_pem = pub_path_user.read_bytes()
                except Exception:
                    public_pem = None
            elif pub_path_bundle.exists():
                try:
                    public_pem = pub_path_bundle.read_bytes()
                except Exception:
                    public_pem = None
            lic_path = str(BASE_DIR / 'license.key')
            payload = license_utils.verify_license_file(lic_path, public_pem=public_pem, fail_on_missing=False)
            if not payload:
                # Sem licença: tenta liberar via TRIAL
                try:
                    if license_check is not None:
                        t = license_check.get_trial_payload()
                        if t:
                            return t
                except Exception:
                    pass
                return None
            return payload
        except Exception:
            # Se falhar por qualquer motivo (ex.: public.pem ausente), ainda tenta TRIAL
            try:
                if license_check is not None:
                    t = license_check.get_trial_payload()
                    if t:
                        return t
            except Exception:
                pass
            return None

    def _format_timespan(self, secs: int) -> str:
        try:
            s = int(secs)
        except Exception:
            return "indisponível"
        if s <= 0:
            return "expirada"
        days, rem = divmod(s, 86400)
        hours, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if mins:
            parts.append(f"{mins}m")
        parts.append(f"{secs}s")
        return " ".join(parts)

    def _update_license_status(self):
        """Atualiza os labels da UI com validade e tempo restante; agenda próxima atualização."""
        # BYPASS: Forçar sempre status de sucesso (VIP Vitalício)
        try:
            self.lic_status_var.set("TRIAL ATIVO (Modo de Teste Infinito)")
            self.lic_exp_var.set("Expira em: 2099-12-31")
            self.lic_remain_var.set("Dias restantes: 999999+")
            
            # Garantir desbloqueio
            try:
                if getattr(self, 'limited_mode', False):
                    self.limited_mode = False
            except:
                self.limited_mode = False
            
            # Tenta limpar UI se métodos existirem
            if hasattr(self, '_remove_limited_panel'):
                self._remove_limited_panel()
            if hasattr(self, '_clear_limited_mode_ui'):
                self._clear_limited_mode_ui()
                
        except Exception:
            pass

        # agendar próxima atualização (pode ser longo, pois é vitalício)
        try:
            self.root.after(60000, self._update_license_status)
        except Exception:
            pass

    # ---------- seletores ----------
    def sel_midias(self):
        files = filedialog.askopenfilenames(
            title="Selecione os VÍDEOS das cenas",
            filetypes=[
                ("Vídeos", "*.mp4 *.mov *.mkv *.webm *.avi"),
                ("Todos", "*.*"),
            ],
        )
        if not files: return
        self.images, self.video_clips = [], []
        for p in files:
            ext = Path(p).suffix.lower()
            if ext in (".mp4", ".mov", ".mkv", ".webm", ".avi"):
                self.video_clips.append(p)
        try:
            self.video_clips.sort(key=_natural_key)
        except Exception:
            self.video_clips.sort()
        self.lbl_midias.config(text=f"🎞️ {len(self.video_clips)} vídeo(s)")
        if self.video_clips:
            self.log(f"{len(self.video_clips)} vídeo(s) importados.")
        self._check_ready()

    def sel_intro_video(self):
        """Seleciona um vídeo intro que será reproduzido antes do mapeamento de imagens."""
        p = filedialog.askopenfilename(
            title="Selecione o vídeo INTRO",
            filetypes=[("Vídeos","*.mp4 *.mov *.mkv *.webm *.avi"), ("Todos","*.*")]
        )
        if not p:
            return
        self.intro_video_path.set(p)
        self.intro_video_en.set(True)
        # Detectar duração do vídeo intro
        try:
            result = subprocess.run(
                [self.ffprobe, '-v', 'error', '-select_streams', 'v:0',
                 '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(p)],
                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10
            )
            dur = float(result.stdout.strip()) if result.returncode == 0 and result.stdout.strip() else 0.0
            self.intro_duration = dur
        except Exception as e:
            self.log(f"⚠️ Não foi possível detectar duração do intro: {e}")
            self.intro_duration = 0.0
            dur = 0.0
        
        self.lbl_intro.config(text=f"✅ {os.path.basename(p)}")
        self.lbl_intro_dur.config(text=f"({dur:.1f}s)")
        self.log(f"Vídeo intro selecionado: {os.path.basename(p)} ({dur:.1f}s)")
        self.log(f"💡 O mapeamento de imagens começará após {dur:.1f}s do intro")

    def get_intro_offset(self):
        """Retorna o offset do intro em segundos (0 se não houver intro habilitado)."""
        if getattr(self, 'intro_video_en', None) and self.intro_video_en.get():
            intro_path = getattr(self, 'intro_video_path', None)
            if intro_path and intro_path.get() and Path(intro_path.get()).exists():
                return getattr(self, 'intro_duration', 0.0) or 0.0
        return 0.0

    def get_media_items(self):
        """Retorna lista combinada de mídias (vídeos + imagens) ordenada naturalmente pelos nomes.
        Mantém caminhos completos (strings).
        IMPORTANTE: Exclui o arquivo de intro da lista (se estiver habilitado).
        """
        items = []
        try:
            items = list(self.video_clips or []) + list(self.images or [])
            
            # Excluir o arquivo de intro da lista de mídias (se habilitado)
            intro_path = None
            if getattr(self, 'intro_video_en', None) and self.intro_video_en.get():
                intro_var = getattr(self, 'intro_video_path', None)
                if intro_var and intro_var.get():
                    intro_path = Path(intro_var.get()).resolve()
            
            if intro_path:
                # Filtrar removendo o arquivo de intro
                items = [p for p in items if Path(p).resolve() != intro_path]
            
            try:
                items = sorted(items, key=_natural_key)
            except Exception:
                items = sorted(items)
        except Exception:
            items = list(self.images or [])
        return items

    def sel_audio(self):
        p = filedialog.askopenfilename(title="Selecione áudio", filetypes=[("Áudio","*.mp3 *.wav *.m4a *.aac")])
        if not p: return
        # LIMPAR transcrição anterior ao trocar de áudio (evita usar dados incompatíveis)
        if hasattr(self, '_last_transcript_words'):
            self._last_transcript_words = None
            self.log("[áudio] Transcrição anterior limpa (novo áudio selecionado)")
        if hasattr(self, '_last_audio_duration'):
            self._last_audio_duration = None
        if hasattr(self, '_last_audio_path'):
            self._last_audio_path = None
        self.audio_path = p
        self._last_audio_path = p  # Guardar qual áudio foi transcrito
        # Obter duração do áudio usando ffprobe
        dur_str = ""
        try:
            result = subprocess.run(
                [self.ffprobe, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p],
                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                dur_sec = float(result.stdout.strip())
                mins = int(dur_sec // 60)
                secs = int(dur_sec % 60)
                dur_str = f" ({mins}m {secs}s)"
                self._last_audio_duration = dur_sec
        except Exception:
            pass
        self.lbl_audio.config(text=f"✅ {os.path.basename(p)}{dur_str}")
        self.log(f"{os.path.basename(p)}{dur_str}")
        self._check_ready()

    def sel_modelo(self):
        p = filedialog.askdirectory(title="Selecione a pasta do modelo de voz")
        if not p: return
        self.vosk_dir = p
        self.vosk_entry.delete(0,"end"); self.vosk_entry.insert(0, p)
        self._save_settings()
        ok = validate_vosk_dir(Path(p))
        if ok:
            self.log(f"Modelo configurado: {p}")
        else:
            self.log(f"Aviso: pasta selecionada ({p}) pode não ser um modelo Vosk válido.")

    def sel_fx(self, n):
        p = filedialog.askopenfilename(title=f"Selecione MP4 do efeito #{n}", filetypes=[("Vídeo MP4","*.mp4"),("Vídeo","*.mp4 *.mov *.mkv *.webm")])
        if not p: return
        if n==1:
            self.fx1_path = p; self.fx1_en.set(True); self.fx1_lbl.config(text=os.path.basename(p))
        else:
            self.fx2_path = p; self.fx2_en.set(True); self.fx2_lbl.config(text=os.path.basename(p))

    def sel_sfx(self):
        p = filedialog.askopenfilename(title="Selecione o áudio do efeito", filetypes=[("Áudio","*.mp3 *.wav *.m4a *.aac")])
        if not p: return
        self.sfx_path = p; self.sfx_en.set(True); self.sfx_lbl.config(text=os.path.basename(p))

    def sel_wm_img(self):
        p = filedialog.askopenfilename(title="Selecione imagem", filetypes=[("Imagens","*.png *.jpg *.jpeg *.webp")])
        if not p: return
        self.wm_img_path.set(p); self.wm_img_en.set(True)

    def sel_wm_effect(self):
        p = filedialog.askopenfilename(title="Selecione vídeo do efeito (fundo verde)", filetypes=[("Vídeos","*.mp4 *.mov *.mkv *.webm")])
        if not p:
            return
        self.wm_eff_path.set(p); self.wm_eff_en.set(True)

    def sel_license(self):
        """Importa um arquivo de licença (`license.key`) para o diretório do app e verifica localmente.
        Copia o arquivo selecionado para `BASE_DIR/license.key` e tenta validar usando `BASE_DIR/public.pem`.
        Mostra caixa de diálogo de sucesso/erro.
        """
        try:
            p = filedialog.askopenfilename(title="Selecione o arquivo de licença (license.key)", filetypes=[("Licença","*.key *.lic;*.*")])
            if not p:
                return
            dest = BASE_DIR / 'license.key'
            try:
                shutil.copy(p, str(dest))
            except Exception:
                # fallback: attempt write
                with open(p, 'rb') as fr, open(dest, 'wb') as fw:
                    fw.write(fr.read())
            # try to validate using public.pem in app dir
            pub_path = (BASE_DIR / 'public.pem') if (BASE_DIR / 'public.pem').exists() else (BUNDLE_DIR / 'public.pem')
            public_pem = None
            if pub_path.exists():
                try:
                    public_pem = pub_path.read_bytes()
                except Exception:
                    public_pem = None
            try:
                from license_utils import verify_license_file
            except Exception:
                messagebox.showwarning('Licença', 'Módulo de verificação não disponível (license_utils).')
                return
            try:
                payload = verify_license_file(str(dest), public_pem=public_pem)
                exp_ts = payload.get('exp')
                exp_s = datetime.fromtimestamp(int(exp_ts)).strftime('%Y-%m-%d %H:%M:%S') if exp_ts else 'desconhecido'
                messagebox.showinfo('Licença válida', f'Licença válida. Expira em: {exp_s}')
            except Exception as e:
                messagebox.showerror('Licença inválida', str(e))
        except Exception as e:
            try:
                messagebox.showerror('Erro', str(e))
            except Exception:
                print('Erro ao importar licença:', e)

    def show_hwid(self):
        """Mostra o HWID desta máquina em caixa de diálogo e copia para a área de transferência."""
        try:
            try:
                from license_utils import get_hwid
            except Exception:
                try:
                    import importlib
                    lu = importlib.import_module('license_utils')
                    get_hwid = lu.get_hwid
                except Exception:
                    messagebox.showerror('HWID', 'Módulo license_utils não disponível para obter HWID.')
                    return
            hw = get_hwid()
            try:
                # copiar para clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(hw)
            except Exception:
                pass
            try:
                messagebox.showinfo('HWID', f'HWID (copiado para área de transferência):\n{hw}')
            except Exception:
                print('HWID:', hw)
        except Exception as e:
            try:
                messagebox.showerror('HWID erro', str(e))
            except Exception:
                print('Erro ao obter HWID:', e)


    def _build_dashboard(self, parent):
        """[E14] Dashboard de Status de Pastas"""
        f = ctk.CTkFrame(parent, padx=5, pady=5)
        f.pack(fill="x", padx=8, pady=15)
        ctk.CTkLabel(f, text="📊 DASHBOARD HOJE", font=("Arial", 9, "bold")).pack(anchor="w")
        
        self.lbl_dash_out = ctk.CTkLabel(f, text="Output: Calculando...", font=("Arial", 8))
        self.lbl_dash_out.pack(anchor="w")
        
        self.lbl_dash_tmp = ctk.CTkLabel(f, text="Temp: Calculando...", font=("Arial", 8))
        self.lbl_dash_tmp.pack(anchor="w")
        
        def _monitor():
            while True:
                try:
                    # Contar vídeos
                    mp4s = list(OUT_DIR.glob("*.mp4"))
                    vcount = len(mp4s)
                    
                    # Calcular tamanho de TEMP e CHUNKS
                    tsize = 0
                    for p in BASE_DIR.glob("temp_*"):
                        if p.is_file(): tsize += p.stat().st_size
                    for p in BASE_DIR.glob("*_lufs_*.mp4"):
                        if p.is_file(): tsize += p.stat().st_size
                    for p in BASE_DIR.glob("*_paced_*.wav"):
                        if p.is_file(): tsize += p.stat().st_size
                    for p in BASE_DIR.glob("subs_*.ass"):
                        if p.is_file(): tsize += p.stat().st_size
                    chunks = BASE_DIR / "_chunks"
                    if chunks.exists():
                        for root, _, files in os.walk(str(chunks)):
                            for name in files:
                                tsize += os.path.getsize(os.path.join(root, name))
                    
                    mb = tsize / (1024*1024)
                    
                    def _update_ui(v=vcount, m=mb):
                        try:
                            self.lbl_dash_out.config(text=f"📂 Output: {v} vídeo(s)")
                            color = "#ccc"
                            if m > 500: color = "#ffaa00"
                            if m > 2000: color = "#ff4444"
                            self.lbl_dash_tmp.config(text=f"🗑️ Lixo/Temp: {m:.1f} MB", fg=color)
                        except Exception:
                            pass

                    self.root.after(0, _update_ui)
                except Exception:
                    pass
                time.sleep(5)
        
        import threading
        t = threading.Thread(target=_monitor, daemon=True)
        t.start()

    def force_unlock_loop(self):
        """Reforça o desbloqueio periodicamente."""
        try:
            self.limited_mode = False
            if " - TRIAL DESBLOQUEADO" not in self.root.title():
                self.root.title(self.root.title() + " - TRIAL DESBLOQUEADO")
        except:
            pass
        self.root.after(5000, self.force_unlock_loop)

    def _check_ready(self):
        try:
            if hasattr(self, "btn_go") and self.btn_go is not None:
                state = ("normal" if (self.audio_path and (self.images or self.video_clips)) else "disabled")
                self.btn_go.config(state=state)
        except Exception:
            pass

    # ---------- logs ----------
    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        try:
            self.log_txt.insert("end", f"[{ts}] {msg}\n"); self.log_txt.see("end")
        except Exception:
            pass
        try: print(msg)
        except: pass

    # ---------- progresso ----------
    def _update_progress(self, percent, status_text=None):
        """Atualiza a barra de progresso com porcentagem (0-100) - thread-safe"""
        if getattr(self, '_headless', False):
            return
        def _do_update():
            try:
                p = max(0, min(100, percent))
                self.progress_var.set(p)
                self.progress_label.config(text=f"{int(p)}%")
                self.root.update_idletasks()  # Forçar atualização visual
            except Exception:
                pass
        try:
            if status_text:
                self.log(f"[{int(percent)}%] {status_text}")
            # Agendar atualização na thread principal
            self.root.after(0, _do_update)
        except Exception:
            pass

    def _start_progress_indeterminate(self):
        """Inicia o modo indeterminado (animação) quando não sabemos o progresso exato"""
        if getattr(self, '_headless', False):
            return
        try:
            self.progress.config(mode='indeterminate')
            self._progress_mode = 'indeterminate'
            self.progress.start(10)
            self.progress_label.config(text="...")
        except Exception:
            pass

    def _stop_progress(self):
        """Para a barra de progresso e reseta para 0%"""
        if getattr(self, '_headless', False):
            return
        try:
            if self._progress_mode == 'indeterminate':
                self.progress.stop()
            self.progress.config(mode='determinate')
            self._progress_mode = 'determinate'
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
        except Exception:
            pass

    # ---------- thread ----------
    def go_thread(self, draft=False):
        """Ao pressionar F9: Inicia a criação do vídeo usando as configurações atuais."""
        self.nb.select(self.tab_log)
        self._draft = draft
        threading.Thread(target=self._create_video, daemon=True).start()



    # ---------- duração do áudio ----------
    def _audio_duration(self, path):
        try:
            r = subprocess.run([self.ffprobe,"-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", path],
                               capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=15)
            if r.returncode == 0 and r.stdout:
                return float(r.stdout.strip())
            audio = AudioSegment.from_file(path)
            return audio.duration_seconds
        except Exception:
            try:
                audio = AudioSegment.from_file(path)
                return audio.duration_seconds
            except Exception:
                return None

    def _align_media_to_scenes(self, mapping, media_list, total_dur=None):
        """
        Retorna uma lista de timeline entries.
        
        IMPORTANTE: Se o mapping já tem os arquivos corretos (cena_1.mp4, cena_2.png, etc.),
        NÃO substituir pelos arquivos da media_list. Apenas usar os tempos do mapping.
        
        Só faz realinhamento se os arquivos do mapping não existirem ou se explicitamente solicitado.
        """
        try:
            scenes = mapping.get('images', []) if mapping else []
            intro_offset = float(mapping.get('intro_offset', 0.0)) if mapping else 0.0
            
            self.log(f"[align] Verificando mapping com {len(scenes)} cenas")
            self.log(f"[align] intro_offset={intro_offset}")
            
            # NOVA LÓGICA: Verificar se os arquivos do mapping existem
            # Se existirem, MANTER o mapping original (com os tempos corretos)
            all_files_exist = True
            for scene in scenes:
                file_path = scene.get('file', '')
                if file_path and not Path(file_path).exists():
                    all_files_exist = False
                    self.log(f"[align] ⚠️ Arquivo não encontrado: {file_path}")
                    break
            
            if all_files_exist and scenes:
                # USAR O MAPPING ORIGINAL - NÃO SUBSTITUIR ARQUIVOS
                self.log(f"[align] ✅ Todos os arquivos do mapping existem - usando mapping original")
                out = []
                for scene in scenes:
                    out.append({
                        'file': scene.get('file', ''),
                        'start': round(float(scene.get('start', 0.0)), 3),
                        'end': round(float(scene.get('end', 0.0)), 3),
                        'block_index': scene.get('block_index', 0),
                        'text': scene.get('text', ''),
                        'is_intro': scene.get('is_intro', False)
                    })
                    self.log(f"[align] Cena {scene.get('block_index')}: {scene.get('start')}s - {scene.get('end')}s ({Path(scene.get('file','')).name})")
                return out
            
            # Se os arquivos não existem, tentar alinhar com media_list
            self.log(f"[align] Arquivos do mapping não encontrados - realinhando com media_list ({len(media_list)} itens)")
            
            # Verificar se há intro no mapping
            has_intro_in_mapping = False
            intro_scene = None
            image_scenes = []
            
            for scene in scenes:
                if scene.get('is_intro', False):
                    has_intro_in_mapping = True
                    intro_scene = scene
                else:
                    image_scenes.append(scene)
            
            self.log(f"[align] has_intro_in_mapping={has_intro_in_mapping}")
            self.log(f"[align] total scenes in mapping: {len(scenes)}, image scenes: {len(image_scenes)}")
            
            # Se temos um mapping válido com tempos, usar os tempos originais
            if image_scenes and len(image_scenes) > 0:
                out = []
                
                # Se há intro, MANTÊ-LO como primeira entrada
                if has_intro_in_mapping and intro_scene:
                    # Procurar arquivo de intro na media_list
                    intro_file = intro_scene.get('file', '')
                    if intro_file and not Path(intro_file).exists():
                        # Tentar encontrar arquivo similar na pasta
                        intro_name = Path(intro_file).name
                        for m in media_list:
                            if Path(m).name == intro_name or 'cena_1' in Path(m).name.lower():
                                intro_file = m
                                break
                    out.append({
                        'file': intro_file,
                        'start': round(float(intro_scene.get('start', 0.0)), 3),
                        'end': round(float(intro_scene.get('end', intro_offset)), 3),
                        'block_index': intro_scene.get('block_index', 1),
                        'text': intro_scene.get('text', ''),
                        'is_intro': True
                    })
                    self.log(f"[align] ✅ Intro mantido: 0.0s -> {intro_scene.get('end')}s")
                
                # Agora alinhar media_list com image_scenes (excluindo o intro)
                for i, m in enumerate(media_list):
                    if i < len(image_scenes):
                        # Usar os tempos do mapping original (já considera intro)
                        scene = image_scenes[i]
                        out.append({
                            'file': m,
                            'start': round(float(scene.get('start', 0.0)), 3),
                            'end': round(float(scene.get('end', 0.0)), 3),
                            'block_index': scene.get('block_index', i+2 if has_intro_in_mapping else i+1),
                            'text': scene.get('text', '')
                        })
                    else:
                        # Mídia extra: distribuir após a última cena
                        last_end = float(image_scenes[-1].get('end', 0.0)) if image_scenes else intro_offset
                        remaining = (total_dur or last_end + 3.0) - last_end
                        extra_count = len(media_list) - len(image_scenes)
                        avg = max(MIN_SCENE_DURATION, remaining / max(1, extra_count))
                        idx = i - len(image_scenes)
                        st = last_end + idx * avg
                        en = min(total_dur or st + avg, st + avg)
                        out.append({
                            'file': m,
                            'start': round(st, 3),
                            'end': round(en, 3),
                            'block_index': i + 2 if has_intro_in_mapping else i + 1,
                            'text': ''
                        })
                return out
            
            # Fallback: distribuir uniformemente se não há mapping válido
            n_media = max(1, len(media_list))
            total = float(total_dur or 0.0) or (n_media * 3.0)
            avg = total / n_media
            out = []
            t0 = intro_offset  # Começar após o intro se houver
            for i, m in enumerate(media_list):
                t1 = min(total, t0 + avg)
                out.append({'file': m, 'start': round(t0, 3), 'end': round(t1, 3), 'block_index': i + 1})
                t0 = t1
            return out
            
        except Exception as e:
            self.log(f"[align] falha ao alinhar mídias às cenas: {e}")
            # fallback: simple equal split
            out = []
            total = float(total_dur or 0.0) or (len(media_list) * 3.0)
            avg = total / max(1, len(media_list))
            t0 = 0.0
            for i, m in enumerate(media_list):
                t1 = min(total, t0 + avg)
                out.append({'file': m, 'start': round(t0, 3), 'end': round(t1, 3), 'block_index': i + 1})
                t0 = t1
            return out

    def _preprocess_continuations(self):
        """
        Agrupa e concatena fisicamente vídeos de continuação (marcados com _CONT_ ou _cont_ no nome)
        para que o mapeamento e as transições do pipeline enxerguem apenas 1 vídeo por cena.
        """
        if not self.video_clips:
            return
        
        new_clips = []
        current_group = []
        
        for clip in self.video_clips:
            name = Path(clip).name.lower()
            if ("cont_" in name or "_cont" in name or "cont-" in name) and current_group:
                current_group.append(clip)
            else:
                if current_group:
                    new_clips.append(self._concat_group_safe(current_group))
                current_group = [clip]
                
        if current_group:
            new_clips.append(self._concat_group_safe(current_group))
            
        if len(new_clips) < len(self.video_clips):
            self.log(f"[concat] Agrupou {len(self.video_clips)} clipes importados em {len(new_clips)} cenas virtuais de continuidade.")
            self.video_clips = new_clips

    def _concat_group_safe(self, group):
        if len(group) == 1:
            return group[0]
            
        out_dir = BASE_DIR / "temp"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        outp = out_dir / f"merged_cont_{ts}.mp4"
        
        list_txt = out_dir / f"list_{ts}.txt"
        with open(list_txt, "w", encoding="utf-8") as f:
            for p in group:
                f.write(f"file '{Path(p).resolve().as_posix()}'\n")
                
        cmd = [self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_txt), "-c", "copy", str(outp)]
        self.log(f"[concat] Unindo {len(group)} vídeos de continuação ({Path(group[0]).name}...)")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            self.log(f"[concat aviso] Erro copy: {r.stderr[:200]}. Caiu fallback de reencode.")
            return self._concat_group_fallback(group, outp)
            
        try:
            list_txt.unlink(missing_ok=True)
        except:
            pass
            
        return str(outp)

    def _concat_group_fallback(self, group, outp):
        # Fallback caso o concat copy falhe por metadados incompatíveis
        if str(getattr(self, 'orient', tk.StringVar(value='horizontal')).get()) == 'vertical':
            W, H = 1080, 1920
        else:
            W, H = 1920, 1080
        fps = int(getattr(self, 'fps', 30) or 30)

        inputs = []
        chains = []
        labels = []
        for i, p in enumerate(group):
            inputs += ["-i", str(p)]
            chains.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}[v{i}]")
            labels.append(f"[v{i}]")
        concat = ''.join(labels) + f"concat=n={len(group)}:v=1:a=0[outv]"
        fc = ';'.join(chains + [concat])
        preset = "ultrafast" if getattr(self, '_draft', False) else "veryfast"
        crf = "28" if getattr(self, '_draft', False) else "20"
        cmd = [self.ffmpeg, "-y", *inputs, "-filter_complex", fc, "-map", "[outv]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", "-preset", preset, "-crf", crf, str(outp)]
        subprocess.run(cmd, capture_output=True)
        return str(outp)


    def _remover_silencio_ffmpeg(self, audio_path: str, noise: str = "-40dB", min_dur: float = 0.3) -> str:
        """
        [E5] Remove silêncios do áudio usando FFmpeg silencedetect + aselect.

        1. Detecta regiões silenciosas com `silencedetect=noise=X:d=Y`
        2. Constrói expressão `aselect` para manter apenas os trechos com voz
        3. Retorna o path do arquivo processado (ou None em falha)

        Args:
            audio_path: caminho do .wav de entrada
            noise:      limiar de silêncio (ex: '-40dB')
            min_dur:    duração mínima para considerar silêncio (ex: 0.3s)
        """
        try:
            out_path = str(Path(audio_path).with_suffix('')) + f"_paced_{os.getpid()}.wav"

            # PASSO 1: detectar silêncios
            self.log(f"[E5] 🔍 Detectando silêncios (limiar={noise}, dur≥{min_dur}s)...")
            detect_cmd = [
                self.ffmpeg, "-y", "-i", audio_path,
                "-af", f"silencedetect=noise={noise}:d={min_dur}",
                "-f", "null", "-"
            ]
            result = subprocess.run(
                detect_cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace"
            )
            stderr_out = (result.stderr or "")

            # PASSO 2: extrair intervalos de silêncio do stderr
            import re as _re
            starts = [float(m) for m in _re.findall(r"silence_start:\s*([\d.]+)", stderr_out)]
            ends   = [float(m) for m in _re.findall(r"silence_end:\s*([\d.]+)",   stderr_out)]

            if not starts:
                self.log("[E5] Nenhum silêncio detectado. Áudio inalterado.")
                return audio_path  # nada a cortar

            self.log(f"[E5] {len(starts)} trecho(s) silencioso(s) encontrado(s).")

            # PASSO 3: montar expressão aselect para MANTER as regiões com voz
            # Lógica: manter [0 → start0] [end0 → start1] [end1 → start2] ... [endN → fim]
            keep_parts = []
            prev_end = 0.0
            for s, e in zip(starts, ends):
                if s > prev_end + 0.05:  # há voz entre prev_end e s
                    keep_parts.append(f"between(t,{prev_end:.3f},{s:.3f})")
                prev_end = e

            # Trecho final após o último silêncio
            keep_parts.append(f"gte(t,{prev_end:.3f})")

            aselect_expr = "+".join(keep_parts)

            # PASSO 4: aplicar corte
            self.log("[E5] ✂️ Aplicando cortes no áudio...")
            cut_cmd = [
                self.ffmpeg, "-y", "-i", audio_path,
                "-af", f"aselect='{aselect_expr}',asetpts=N/SR/TB",
                "-ar", "16000", "-ac", "1",
                out_path
            ]
            r2 = subprocess.run(
                cut_cmd, capture_output=True, text=True,
                encoding="utf-8", errors="replace"
            )
            if r2.returncode != 0:
                self.log(f"[E5] Erro FFmpeg ao cortar silêncio: {r2.stderr[-300:]}")
                return audio_path  # fallback: retorna original

            self.log(f"[E5] ✅ Áudio processado: {Path(out_path).name}")
            return out_path

        except Exception as e:
            self.log(f"[E5] Erro em _remover_silencio_ffmpeg: {e}")
            return audio_path  # sempre retorna algo válido

    # ---------- criar vídeo (fluxo principal) ----------
    def _show_preview_window_sync(self, words):
        import queue
        result_q = queue.Queue()
        def _show():
            top = tk.Toplevel(self.root)
            top.title("Revisão do Diretor IA (Pré-Render)")
            top.geometry("800x500")
            top.configure()
            top.transient(self.root)
            top.grab_set()

            lbl = ctk.CTkLabel(top, text="🎬 Timeline de Ações da Inteligência Artificial", font=("Segoe UI", 14, "bold"), text_color="#00E676")
            lbl.pack(pady=10)
            
            frame_list = ctk.CTkFrame(top)
            frame_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            scrollbar = ttk.Scrollbar(frame_list)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            tree = ttk.Treeview(frame_list, columns=("tempo", "texto", "acoes"), show="headings", yscrollcommand=scrollbar.set)
            tree.heading("tempo", text="Tempo")
            tree.heading("texto", text="Texto Base")
            tree.heading("acoes", text="Ações Injetadas pela IA")
            
            tree.column("tempo", width=80, anchor=tk.CENTER)
            tree.column("texto", width=350)
            tree.column("acoes", width=300)
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=tree.yview)

            for b in words:
                acoes = []
                if b.get('is_censored'): acoes.append("🤬 CENSURA (Bipe)")
                if b.get('zoom_trigger'): acoes.append("🔍 PUNCH-IN")
                if b.get('motion_trigger'): acoes.append("✨ MOTION DESIGN")
                if b.get('sfx_trigger'): acoes.append("🔊 SFX")
                if b.get('broll_path'): acoes.append(f"🎥 B-ROLL [{b.get('broll_tag', 'geral')}]")
                
                if acoes:
                    t_str = f"{b.get('start', 0.0):.1f}s"
                    texto = b.get('word', b.get('texto', ''))[:40] + "..."
                    tree.insert("", "end", values=(t_str, texto, " + ".join(acoes)))

            if len(tree.get_children()) == 0:
                tree.insert("", "end", values=("-", "Nenhuma ação engatilhada pela IA.", "-"))

            frame_btn = ctk.CTkFrame(top)
            frame_btn.pack(fill=tk.X, pady=20)

            def on_confirm():
                result_q.put(True)
                top.grab_release()
                top.destroy()
                
            def on_cancel():
                result_q.put(False)
                top.grab_release()
                top.destroy()

            top.protocol("WM_DELETE_WINDOW", on_cancel)

            btn_ok = ctk.CTkButton(frame_btn, text="Aprovar e Renderizar Vídeo", font=("Segoe UI", 12, "bold"), command=on_confirm)
            btn_ok.pack(side=tk.LEFT, expand=True, padx=20, pady=10)
            
            btn_no = ctk.CTkButton(frame_btn, text="Cancelar Renderização", font=("Segoe UI", 12), command=on_cancel)
            btn_no.pack(side=tk.RIGHT, expand=True, padx=20, pady=10)

        self.root.after(0, _show)
        try:
            return result_q.get(timeout=600)
        except queue.Empty:
            return True

    def _create_video(self):
        try:
            if not (self.images or self.video_clips): raise RuntimeError("Selecione imagens e/ou vídeos.")
            
            # Chama o pré-processador na thread principal (rápido se for copy) 
            # para já preparar a self.video_clips antes das checagens do mapping
            if self.video_clips:
                self._preprocess_continuations()
                
            if not self.audio_path: raise RuntimeError("Selecione o áudio.")
            self.btn_go.config(state="disabled")
            self._update_progress(0, "Iniciando renderização...")

            dur = self._audio_duration(self.audio_path)
            if not dur: raise RuntimeError("Erro ao ler duração do áudio.")
            self._last_audio_duration = dur
            m,s = divmod(int(dur),60); self.log(f"Duração da narração: {m}m {s}s")
            self._update_progress(5, "Convertendo áudio...")

            tmp_wav = BASE_DIR / f"temp_audio_16k_{os.getpid()}.wav"
            convert_to_wav16k(self.ffmpeg, Path(self.audio_path), tmp_wav)

            # [E5] Smart Pacing: remover silêncios do áudio antes de transcrever
            if getattr(self, 'opt_smart_pacing', None) and self.opt_smart_pacing.get():
                try:
                    noise_str = self.smart_pacing_noise.get() if hasattr(self, 'smart_pacing_noise') else "-40dB"
                    dur_val   = float(self.smart_pacing_dur.get()) if hasattr(self, 'smart_pacing_dur') else 0.3
                    paced_wav = self.audio_pipeline.remover_silencio_ffmpeg(str(tmp_wav), noise_str, dur_val)
                    if paced_wav and Path(paced_wav).exists():
                        try: tmp_wav.unlink()
                        except Exception: pass
                        tmp_wav = Path(paced_wav)
                        dur = self._audio_duration(str(tmp_wav)) or dur
                        self._last_audio_duration = dur
                        m, s = divmod(int(dur), 60)
                        self.log(f"[E5] ✂️ Smart Pacing ok. Duração após cortes: {m}m {s}s")
                except Exception as _esp:
                    self.log(f"[E5] ⚠️ Smart Pacing ignorado (render continua): {_esp}")

            self._update_progress(10, "Transcrevendo áudio...")

            words = []
            is_headless = getattr(self, '_headless', False)
            
            # OTIMIZAÇÃO: Se já temos palavras carregadas do job, usar diretamente (evita re-transcrição)
            job_words = getattr(self, '_job_transcript_words', None)
            if job_words and len(job_words) > 0:
                words = job_words
                self.log(f"[voz] Usando {len(words)} palavras já transcritas do job (SEM re-transcrição)")
                self._job_transcript_words = None  # Limpar flag para próximos jobs
            elif self.opt_leg.get():
                # Preferência: Whisper > Vosk
                tried_whisper = False
                tried_vosk = False
                
                # Tenta Whisper primeiro (reconhece fala melhor, com timestamps de palavras)
                if WHISPER_OK:
                    try:
                        self.log("[voz] Transcrevendo com openai/whisper para alinhamento...")
                        words = whisper_transcribe(str(self.audio_path), log_fn=self.log)
                        self._last_transcript_words = words
                        tried_whisper = True
                    except Exception as e:
                        self.log(f"⚠️ Whisper falhou: {e}")
                        tried_whisper = False
                
                # Se Whisper não funcionou, tenta Vosk como fallback
                if not words and VOSK_OK:
                    model_dir = Path(self.vosk_entry.get().strip() or self.vosk_dir or "")
                    if model_dir and model_dir.exists() and validate_vosk_dir(model_dir):
                        try:
                            self.log("[voz] Transcrevendo com Vosk para alinhamento (fallback)...")
                            words = vosk_transcribe(tmp_wav, model_dir, log_fn=self.log)
                            self._last_transcript_words = words
                            tried_vosk = True
                        except Exception as e:
                            self.log(f"⚠️ Vosk falhou: {e}")
                            tried_vosk = False
                
                # Se nenhum funcionou
                if not words:
                    msg = "⚠️ Nenhum transcritor disponível."
                    if not tried_whisper and not WHISPER_OK:
                        msg += " Instale Whisper: pip install openai-whisper"
                    if not tried_vosk:
                        msg += " (Vosk não configurado)"
                    msg += " O vídeo seguirá com legendas geradas por divisão de tempo."
                    self.log(msg)

            # ─────────────────────────────────────────────────────────────────
            # [E1] CÉREBRO IA: Analisar blocos com AIDirectorPipeline
            # Injeta zoom_trigger, motion_trigger, broll_path, is_censored em cada palavra
            # ─────────────────────────────────────────────────────────────────
            if words and self._ai_director and self._ai_director.is_active():
                try:
                    self.log("[IA] 🧠 Analisando roteiro com Diretor IA...")
                    user_prompt = ""
                    # Tenta capturar prompt natural da aba Diretor IA, se existir
                    try:
                        user_prompt = getattr(self, '_ia_user_prompt', "") or ""
                    except Exception:
                        pass
                    words = self._ai_director.analisar_roteiro(words, user_prompt=user_prompt)
                    # Salvar palavras ENRIQUECIDAS para E2 (zoom) e E4 (broll) usarem no _ffmpeg_build
                    self._last_ia_words = words
                    # Estatísticas para o log
                    n_zoom   = sum(1 for w in words if w.get("zoom_trigger"))
                    n_motion = sum(1 for w in words if w.get("motion_trigger"))
                    n_broll  = sum(1 for w in words if w.get("broll_path"))
                    n_censor = sum(1 for w in words if w.get("is_censored"))
                    n_impacto = n_zoom + n_motion
                    tokens = self._ai_director.get_last_token_usage() if hasattr(self._ai_director, 'get_last_token_usage') else 0
                    
                    motor_nome = "Gemini" if (hasattr(self._ai_director, 'has_gemini') and self._ai_director.has_gemini()) else "Heurística (Offline)"
                    self.log(f"[IA] ✅ {motor_nome} detectou {n_impacto} palavras de impacto, {n_broll} blocos de B-Roll, {n_censor} censura(s). Tokens gastos: {tokens}.")
                    
                    # [ETAPA 17] - Janela Modal de Preview (se não estiver rodando em background/job)
                    if not getattr(self, '_headless', False) and any([n_zoom, n_motion, n_broll, n_censor]):
                        aprovado = self._show_preview_window_sync(words)
                        if not aprovado:
                            self.log("🛑 Renderização cancelada pelo usuário na tela de Revisão da IA.")
                            self.btn_go.config(state="normal")
                            self._update_progress(0, "Cancelado")
                            return
                            
                except Exception as _e_ia:
                    self.log(f"[IA] ⚠️ Erro na análise IA (render continua normalmente): {_e_ia}")
            elif self._ai_director and not self._ai_director.is_active():
                self.log("[IA] 💤 Diretor IA disponível mas inativo. Ative na Aba Diretor IA.")
            # ─────────────────────────────────────────────────────────────────

            # --- Gerar timeline: se usar mapeamento manual, tenta carregar mapping.json ou gerar a partir do texto colado ---
            mapping = None
            # is_headless já foi definido acima
            
            if self.use_manual_map.get():
                # PRIORIDADE 1: usar mapping_timeline já carregado (do job ou da UI)
                if getattr(self, 'mapping_timeline', None) and isinstance(self.mapping_timeline, dict) and self.mapping_timeline.get('images'):
                    mapping = self.mapping_timeline
                    self.log(f"Usando mapping_timeline já carregado ({len(mapping.get('images', []))} imagens).")
                # PRIORIDADE 2: ler do arquivo mapping.json (APENAS no modo interativo, não no headless/job)
                elif not is_headless and MAPPING_JSON.exists():
                    try:
                        with open(MAPPING_JSON, "r", encoding="utf-8") as f:
                            mapping = json.load(f)
                            self.log("Usando mapping.json encontrado na pasta do app.")
                    except Exception:
                        mapping = None
                if mapping is None and not is_headless:
                    raw = self.map_text.get("1.0","end").strip() if hasattr(self, "map_text") else ""
                    if raw:
                        parsed = parse_manual_text_blocks(raw)
                        dur_map = getattr(self, "_last_audio_duration", None) or dur
                        intro_off = self.get_intro_offset()
                        intro_file = self.intro_video_path.get() if intro_off > 0 and hasattr(self, 'intro_video_path') else None
                        timeline = build_image_timeline_from_words_and_manual(parsed, self.get_media_items(), words, audio_duration=dur_map, intro_offset=intro_off, intro_file=intro_file)
                        mapping = {"audio_duration": dur_map, "intro_offset": intro_off, "images": timeline}
                        try:
                            with open(MAPPING_JSON, "w", encoding="utf-8") as f:
                                json.dump(mapping, f, ensure_ascii=False, indent=2)
                            self.log("mapping.json salvo (a partir do texto colado).")
                        except Exception:
                            pass

            # --- criar vídeo base ---
            self._update_progress(20, "Criando vídeo base...")
            W,H = ((1920,1080) if self.orient.get()=="horizontal" else (1080,1920))
            
            # --- MODO RASCUNHO (360p) ---
            if getattr(self, '_draft', False):
                if H > W: # Vertical
                    W = int(W * 360 / H)
                    H = 360
                else:     # Horizontal
                    H = int(H * 360 / W)
                    W = 360
                W = (W // 2) * 2  # garante que seja par (h264 exige isso)
                H = (H // 2) * 2
                self.log(f"[rascunho] 🔥 Modo Rascunho ativado! Resolução esmagada para {W}x{H}.")

            temp_video = BASE_DIR / f"temp_video_{os.getpid()}.mp4"
            if mapping and "images" in mapping and mapping["images"]:
                # Antes de construir: verificar e ajustar timeline para garantir alinhamento com a narração
                try:
                    # Recria o timeline para corresponder exatamente às mídias carregadas
                    media_list = self.get_media_items()
                    if media_list:
                        try:
                            mapping_images = self._align_media_to_scenes(mapping, media_list, total_dur=dur)
                            self.log(f"[align] timeline reatribuído para {len(mapping_images)} mídias (vídeos+imagens)")
                        except Exception as e:
                            self.log(f"[align] falha ao reatribuir mídias: {e}")
                    else:
                        mapping_images = mapping.get("images", [])
                    adjusted = self._verify_and_adjust_timeline(mapping_images, words, dur)
                    mapping["images"] = adjusted
                    # Só salvar no arquivo global se NÃO for modo headless (evitar conflitos entre jobs)
                    if not is_headless:
                        try:
                            with open(MAPPING_JSON, "w", encoding="utf-8") as f:
                                json.dump(mapping, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                except Exception as e:
                    self.log(f"[verify] falha verificação timeline: {e}")
                # usar builder timeline (mais preciso)
                self._update_progress(20, "Criando vídeo base...")
                try:
                    # permitir forçar fade nesta execução se o usuário escolheu 'fade' e duração>0
                    force = (str(self.transition.get()).lower() == "fade" and float(self.transition_dur.get() or 0.0) > 0.0)
                    self._build_base_using_timeline(mapping["images"], self.video_clips, temp_video, W, H, dur, self.transition.get(), float(self.transition_dur.get()), force_fade=force)
                except Exception as e:
                    self.log(f"Erro em _build_base_using_timeline: {e} -> fallback para _build_base")
                    self._build_base(self.images, self.video_clips, temp_video, W, H, dur, self.transition.get(), float(self.transition_dur.get()))
            else:
                # comportamento padrão (divisão proporcional)
                self._update_progress(20, "Criando vídeo base...")
                self._build_base(self.images, self.video_clips, temp_video, W, H, dur, self.transition.get(), float(self.transition_dur.get()))

            self._update_progress(50, "Gerando legendas...")
            ass_path = None
            if words:
                ass_txt = words_to_ass(words, int(self.words_block.get()), self.font_name.get(), int(self.font_size.get()),
                                       self.color1.get(), self.outline1.get(), self.motion_color.get(), self.motion_outline.get(),
                                       self.pos.get(), int(self.margin_v.get()),
                                       W,H, bool(self.uppercase.get()), bool(self.hold.get()), float(self.hold_gap.get()), float(dur))
                ass_path = BASE_DIR / f"subs_{os.getpid()}.ass"; ass_path.write_text(ass_txt, encoding="utf-8")
                self.log(f"Legendas prontas.")

            OUT_DIR.mkdir(parents=True, exist_ok=True)
            name = (self.out_name.get().strip() or "video_karaoke.mp4")
            if not name.lower().endswith(".mp4"): name += ".mp4"
            # NO MODO HEADLESS: garantir nome único para evitar conflitos entre jobs paralelos
            if is_headless:
                # Verificar se arquivo já existe, se sim adicionar PID
                output = OUT_DIR / name
                if output.exists():
                    stem = Path(name).stem
                    name = f"{stem}_{os.getpid()}.mp4"
                    self.log(f"[headless] Arquivo já existe, usando nome único: {name}")
            output = OUT_DIR / name
            self.log(f"[output] Gerando vídeo: {output}")
            self._update_progress(60, "Codificando vídeo com FFmpeg...")
            self._ffmpeg_build(temp_video, ass_path, output, W,H, dur, getattr(self, '_last_clips_audio', None))

            self._update_progress(85, "Aplicando marca d'água...")
            out2 = self._apply_watermark(str(output))
            if out2 and out2 != str(output) and Path(out2).exists():
                try:
                    os.remove(output)
                    os.rename(out2, output)
                except Exception: pass

            # [E8] Normalização LUFS two-pass
            if getattr(self, 'opt_lufs', None) and self.opt_lufs.get():
                try:
                    target = float(self.lufs_target.get()) if hasattr(self, 'lufs_target') else -14.0
                    self._update_progress(92, f"Normalizando áudio ({target} LUFS)...")
                    norm_out = self.audio_pipeline.normalize_lufs_output(str(output), target_lufs=target)
                    if norm_out and norm_out != str(output) and Path(norm_out).exists():
                        try:
                            os.remove(output)
                            os.rename(norm_out, str(output))
                            self.log(f"[E8] 🎨 Áudio normalizado para {target} LUFS")
                        except Exception as _em:
                            self.log(f"[E8] ⚠️ Falha ao substituir arquivo: {_em}")
                except Exception as _el:
                    self.log(f"[E8] ⚠️ Normalização LUFS ignorada (render continua): {_el}")

            self._update_progress(100, "Vídeo pronto!")
            self.log("✅✅✅ VÍDEO PRONTO!")
            self.log(f"📁 {output}")
            # Remover mapping.json e artefatos para não carregar em próximo vídeo
            # NO MODO HEADLESS: não mexer no arquivo global para evitar conflitos com outros jobs
            if not is_headless:
                try:
                    # mover mapping e arquivos relacionados para pasta de histórico (não carregar automaticamente na próxima vez)
                    if MAPPING_JSON.exists():
                        try:
                            MAPPING_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
                        except Exception:
                            pass
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest = MAPPING_HISTORY_DIR / f"mapping_{ts}.json"
                        try:
                            shutil.move(str(MAPPING_JSON), str(dest))
                        except Exception:
                            try:
                                MAPPING_JSON.unlink()
                            except Exception:
                                pass
                        for extra in (MAPPING_JSON.with_suffix(".metrics.json"), MAPPING_JSON.with_suffix(".alignment.log")):
                            if extra.exists():
                                try:
                                    shutil.move(str(extra), str(MAPPING_HISTORY_DIR / f"{extra.stem}_{ts}{extra.suffix}"))
                                except Exception:
                                    try:
                                        extra.unlink()
                                    except Exception:
                                        pass
                    self.mapping_timeline = None
                    self.use_manual_map.set(False)
                    self._show_mapping_preview(None)
                    self.log(f"[mapping] mapping.json movido para histórico: {MAPPING_HISTORY_DIR}")
                except Exception as e_del:
                    self.log(f"[mapping] falha ao mover mapping: {e_del}")
            else:
                # Modo headless: apenas limpar a variável local
                self.log(f"[headless] Vídeo concluído (mapping do job usado)")
            
            if getattr(self, '_headless', False):
                self.log(f"[headless] Vídeo gerado: {output}")
            else:
                messagebox.showinfo("Sucesso", f"Vídeo gerado!\n\n{output}")
        except Exception as e:
            self.log(f"❌ {e}")
            if getattr(self, '_headless', False):
                # em headless, apenas logar e retornar
                self.log(f"[headless] erro: {e}")
            else:
                messagebox.showerror("Erro", str(e))
        finally:
            try:
                self._stop_progress()
                self._update_progress(100, "Concluído!")
                self.btn_go.config(state="normal")
            except Exception:
                pass
            # [E13] Auto-Purge de Temporários (incluindo lixo de áudio e chunks pesados)
            import shutil
            for p in (
                f"temp_audio_16k_{os.getpid()}.wav", 
                f"temp_video_{os.getpid()}.mp4", 
                f"subs_{os.getpid()}.ass", 
                f"_wm_proc_{os.getpid()}.png", 
                f"temp_clips_audio_{os.getpid()}.wav",
                f"temp_audio_16k_{os.getpid()}_paced_{os.getpid()}.wav"
            ):
                try:
                    fp = BASE_DIR / p
                    if fp.exists(): fp.unlink()
                except Exception:
                    pass
            
            # Limpar lufs files residuais no output dir
            try:
                if 'output' in locals():
                    lufs_p = Path(output).with_suffix('')
                    lufs_file = str(lufs_p) + f"_lufs_{os.getpid()}.mp4"
                    if os.path.exists(lufs_file):
                        os.remove(lufs_file)
            except Exception:
                pass
                
            # Limpar chunks de processamento do OpenCV/FFmpeg
            try:
                chunks_dir = BASE_DIR / "_chunks"
                if chunks_dir.exists():
                    shutil.rmtree(str(chunks_dir), ignore_errors=True)
            except Exception:
                    pass
            self._last_clips_audio = None

    # ---------- ELASTICIDADE: Acelerar/Desacelerar vídeo ----------
    def _create_stretched_segment(self, video_path, target_dur, W, H, fps, idx):
        """
        Cria um arquivo temporário com o vídeo acelerado ou desacelerado
        para caber EXATAMENTE em 'target_dur'.
        Se keep_video_audio estiver ativo, o áudio também é esticado/comprimido.
        Retorna o path do temporário ou None se falhar.
        """
        try:
            prob = subprocess.run(
                [self.ffprobe, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)],
                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5
            )
            orig_dur = float(prob.stdout.strip())
            if orig_dur <= 0.01: return None

            factor = target_dur / orig_dur
            factor = max(0.01, min(100.0, factor))

            out_path = BASE_DIR / f"temp_stretch_{idx}_{os.getpid()}.mp4"

            vf = (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},setsar=1,fps={int(fps)},"
                f"setpts=PTS*{factor:.6f}"
            )

            cmd = [self.ffmpeg, '-y', '-i', str(video_path), '-vf', vf]

            if getattr(self, 'keep_video_audio', tk.BooleanVar(value=False)).get():
                new_sr = max(100, int(44100 / factor))
                af = f"asetrate={new_sr},aresample=44100,aformat=sample_rates=44100:channel_layouts=stereo"
                cmd += ['-af', af, '-c:a', 'aac', '-b:a', '192k']
            else:
                cmd += ['-an']

            cmd += [
                '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-t', f"{target_dur+0.1:.3f}",
                str(out_path)
            ]

            subprocess.run(cmd, capture_output=True, timeout=120)

            if out_path.exists() and out_path.stat().st_size > 1000:
                return str(out_path)
            return None

        except Exception as e:
            self.log(f"[elastic] Erro: {e}")
            return None

    # ---------- _build_base (compatibilidade) ----------
    def _build_base(self, imgs, clips, out_mp4, W, H, total_dur, trans_type, trans_dur):
        self.log(f"Criando vídeo base {W}x{H}... (transição: {trans_type}, {trans_dur:.2f}s)")
        out = cv2.VideoWriter(str(out_mp4), cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (W,H))

        # ========== SUPORTE PARA INTRO SEM MAPEAMENTO ==========
        intro_offset = self.get_intro_offset()
        intro_written = False
        last_intro_frame = None  # Guardar último frame do intro para transição
        if intro_offset > 0 and hasattr(self, 'intro_video_path'):
            intro_path = self.intro_video_path.get()
            if intro_path and Path(intro_path).exists():
                self.log(f"[intro] Renderizando intro SEM mapeamento: {Path(intro_path).name} ({intro_offset:.1f}s)")
                # Renderizar intro temporário
                intro_temp = Path(out_mp4).parent / f"_intro_temp_{os.getpid()}.mp4"
                try:
                    cmd = [
                        self.ffmpeg, '-y', '-i', str(intro_path),
                        '-vf', f'scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black',
                        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                        '-an', '-r', str(self.fps), str(intro_temp)
                    ]
                    subprocess.run(cmd, capture_output=True, timeout=300)
                    if intro_temp.exists():
                        cap_intro = cv2.VideoCapture(str(intro_temp))
                        intro_frame_count = 0
                        while True:
                            ok, frame = cap_intro.read()
                            if not ok:
                                break
                            if frame.shape[1] != W or frame.shape[0] != H:
                                frame = cv2.resize(frame, (W, H))
                            out.write(frame)
                            last_intro_frame = frame.copy()
                            intro_frame_count += 1
                        cap_intro.release()
                        intro_temp.unlink()
                        self.log(f"[intro] Intro escrito: {intro_frame_count} frames")
                        intro_written = True
                except Exception as e:
                    self.log(f"[intro] Erro ao processar intro: {e}")
                    if intro_temp.exists():
                        intro_temp.unlink()

        items = [("video", p) for p in clips] + [("image", p) for p in imgs]
        if not items:
            raise RuntimeError("Nenhuma mídia.")

        clip_secs = 0.0
        for k,vp in items:
            if k!="video": continue
            cap = cv2.VideoCapture(vp); fps = cap.get(cv2.CAP_PROP_FPS) or self.fps; frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
            clip_secs += float(frames)/max(1.0,fps); cap.release()
        nimg = len([1 for k,_ in items if k=="image"])
        rest = max(0.1, total_dur - clip_secs); dur_img = rest / max(1, nimg)

        zoom_basic_enabled = self.zoom_basic.get()
        zoom_adv_enabled = self.zoom_adv_en.get()
        zoom_adv_amp = float(self.zoom_adv_amp.get())
        float_enabled = self.float_en.get()
        float_amp = int(self.float_amp.get())
        float_period = float(self.float_period.get())
        zoom = 0.10 if zoom_basic_enabled else 0.0
        # Suportar todos os tipos de transição
        use_transition = trans_type not in ("sem", "none", "")
        trans_frames = int(max(0.0, trans_dur)*self.fps) if use_transition else 0

        low_mem = bool(self.low_mem_mode.get())
        # Evita repetir o primeiro frame da próxima cena após crossfade
        skip_first_map = {}
        skip_first_map = {}
        
        # Capturar valores dos novos efeitos
        pan_enabled = hasattr(self, 'pan_en') and self.pan_en.get()
        pan_speed_val = float(self.pan_speed.get()) if hasattr(self, 'pan_speed') else 0.05
        tilt_enabled = hasattr(self, 'tilt_en') and self.tilt_en.get()
        tilt_speed_val = float(self.tilt_speed.get()) if hasattr(self, 'tilt_speed') else 0.05
        shake_enabled = hasattr(self, 'shake_en') and self.shake_en.get()
        shake_intensity_val = int(self.shake_intensity.get()) if hasattr(self, 'shake_intensity') else 3
        kenburns_enabled = hasattr(self, 'kenburns_en') and self.kenburns_en.get()
        kenburns_intensity_val = float(self.kenburns_intensity.get()) if hasattr(self, 'kenburns_intensity') else 0.15

        def prepare(img_np):
            h, w = img_np.shape[:2]; tr = W/H; ir = w/h
            if ir > tr: nh=H; nw=int(nh*ir)
            else: nw=W; nh=int(nw/ir)
            interp = cv2.INTER_LINEAR if low_mem else cv2.INTER_LANCZOS4
            r = cv2.resize(img_np,(nw,nh),interpolation=interp)
            x0=(nw-W)//2; y0=(nh-H)//2
            return r[y0:y0+H, x0:x0+W].copy()

        def apply_transform(base_img, t_frac, t_sec, overrides=None):
            import random
            ease = math.sin(math.pi * t_frac)
            scale = 1.0
            dx = 0
            dy = 0

            def get_flag(name, local_val):
                if overrides and name in overrides:
                    return overrides[name]
                return local_val
            
            # Zoom básico
            if get_flag('zoom_basic', zoom_basic_enabled):
                scale += zoom * ease
            # Zoom avançado
            if get_flag('zoom_adv_en', zoom_adv_enabled):
                scale += zoom_adv_amp * math.sin(2*math.pi * t_frac)
            # Flutuar lateral
            if get_flag('float_en', float_enabled) and float_period > 0:
                dx += int(float_amp * math.sin(2*math.pi * (t_sec / float_period)))
            # Pan (esquerda→direita)
            if get_flag('pan_en', pan_enabled):
                pan_offset = (t_frac - 0.5) * 2 * pan_speed_val * W
                dx += int(pan_offset)
            # Tilt (cima→baixo)
            if get_flag('tilt_en', tilt_enabled):
                tilt_offset = (t_frac - 0.5) * 2 * tilt_speed_val * H
                dy += int(tilt_offset)
            # Shake (tremor)
            if get_flag('shake_en', shake_enabled):
                random.seed(int(t_sec * 1000))
                dx += random.randint(-shake_intensity_val, shake_intensity_val)
                dy += random.randint(-shake_intensity_val, shake_intensity_val)
            # Ken Burns (zoom + pan)
            if get_flag('kenburns_en', kenburns_enabled):
                scale += kenburns_intensity_val * t_frac
                kb_pan = kenburns_intensity_val * 0.5 * W * (t_frac - 0.5)
                dx += int(kb_pan * 0.7)
                dy += int(kb_pan * 0.3)
            
            M = cv2.getRotationMatrix2D((W/2, H/2), 0, scale)
            M[0,2] += dx
            M[1,2] += dy
            frame = cv2.warpAffine(base_img, M, (W,H), borderMode=cv2.BORDER_REPLICATE)
            return frame

        def write_from_img(base, seconds, start_frame=0, overrides=None):
            frames_total = int(seconds*self.fps); frames_total = max(frames_total, 1)
            last_frame = None
            if start_frame >= frames_total:
                frame = apply_transform(base, 1.0, (frames_total-1)/self.fps if frames_total>0 else 0.0, overrides=overrides)
                out.write(frame)
                return frame, frames_total
            if frames_total > 1:
                inv = 1.0 / (frames_total - 1)
                out_write = out.write
                af = apply_transform
                for f in range(start_frame, frames_total):
                    t_frac = f * inv
                    t_sec = f / self.fps
                    frame = af(base, t_frac, t_sec, overrides=overrides)
                    out_write(frame)
                    last_frame = frame
            else:
                out_write = out.write
                af = apply_transform
                frame = af(base, 0.0, 0.0, overrides=overrides)
                out_write(frame)
                last_frame = frame
            if last_frame is None:
                last_frame = apply_transform(base, 0.0, 0.0, overrides=overrides)
            return last_frame, frames_total

        speed = int(self.clip_speed.get()); speed = max(100, min(120, speed))
        drop_every = 0
        if speed>100:
            drop_every = int(round(1.0/(1.0-100.0/speed)));  drop_every = drop_every if drop_every>0 else 6

        img_i = 0
        prev_kind = None
        out_write_global = out.write
        apply_transform_ref = apply_transform
        prepare_ref = prepare
        total_items = len(items)
        
        # Guardar último frame para transições entre vídeo/imagem
        last_frame_for_transition = None
        if intro_written and last_intro_frame is not None:
            last_frame_for_transition = last_intro_frame

        for idx_item, (kind, p) in enumerate(items):
            # Atualizar progresso: 20% a 45% durante build_base
            progress_pct = 20 + int((idx_item / max(1, total_items)) * 25)
            self._update_progress(progress_pct)
            
            # EFEITOS ALEATÓRIOS (para este item)
            current_overrides = self._get_random_overrides()

            if kind == "video":
                cap = cv2.VideoCapture(p); fcount = 0
                fps_local = cap.get(cv2.CAP_PROP_FPS) or self.fps
                first_video_frame = None
                while True:
                    ok, frame = cap.read()
                    if not ok: break
                    fcount += 1
                    if drop_every>0 and (fcount % drop_every)==0: continue
                    base = prepare_ref(frame)
                    t_sec = fcount / fps_local
                    t_frac = (fcount % (self.fps*10)) / (self.fps*10)
                    frame2 = apply_transform_ref(base, t_frac, t_sec, overrides=current_overrides)
                    
                    # Transição do item anterior (intro ou imagem) para este vídeo
                    if first_video_frame is None and last_frame_for_transition is not None and trans_frames > 0:
                        first_video_frame = frame2.copy()
                        # Fazer transição
                        for tf in range(trans_frames):
                            alpha = (tf + 1) / trans_frames
                            blended = self._apply_transition(last_frame_for_transition, first_video_frame, alpha, trans_type, W, H)
                            out_write_global(blended)
                        last_frame_for_transition = None  # Já usamos
                    
                    out_write_global(frame2)
                    last_frame_for_transition = frame2.copy()  # Guardar para próxima transição
                    del base, frame2
                cap.release()
                prev_kind = "video"
                gc.collect()
            else:
                img_cv = None
                if low_mem:
                    try:
                        img_cv = cv2.imread(p)
                        if img_cv is None:
                            raise Exception("cv2.imread falhou")
                    except Exception:
                        try:
                            pil_im = Image.open(p).convert("RGB")
                            img_cv = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
                            del pil_im
                        except Exception as e:
                            self.log(f"⚠️ Falha ao abrir imagem '{p}': {e}")
                            img_cv = None
                else:
                    try:
                        pil_im = Image.open(p).convert("RGB")
                        img_cv = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
                        del pil_im
                    except Exception as e:
                        img_cv = cv2.imread(p)
                        if img_cv is None:
                            self.log(f"⚠️ Imagem ignorada: {p} ({e})")
                            continue

                base = prepare_ref(img_cv)
                del img_cv
                
                # Transição do vídeo/intro anterior para esta imagem
                if last_frame_for_transition is not None and trans_frames > 0:
                    first_img_frame = apply_transform_ref(base, 0.0, 0.0, overrides=current_overrides)
                    for tf in range(trans_frames):
                        alpha = (tf + 1) / trans_frames
                        blended = self._apply_transition(last_frame_for_transition, first_img_frame, alpha, trans_type, W, H)
                        out_write_global(blended)
                    last_frame_for_transition = None  # Já usamos
                    del first_img_frame
                
                if prev_kind == "video":
                    if p in skip_first_map:
                        del skip_first_map[p]
                    start_frame = 0
                else:
                    start_frame = 1 if skip_first_map.get(p, False) else 0

                last_frame, frames_total = write_from_img(base, dur_img, start_frame=start_frame, overrides=current_overrides)
                
                # Guardar último frame para transição com próximo vídeo
                last_frame_for_transition = last_frame.copy() if last_frame is not None else None

                if trans_frames > 0:
                    nxt = None
                    nxt_kind = None
                    for kk in range(idx_item+1, len(items)):
                        nxt_kind = items[kk][0]
                        nxt = items[kk][1]
                        break  # Pegar o próximo item (seja vídeo ou imagem)
                    
                    # Só fazer transição aqui se o próximo for imagem
                    # Se for vídeo, a transição será feita no início do vídeo
                    if nxt and nxt_kind == "image":
                        img2_cv = None
                        try:
                            if low_mem:
                                img2_cv = cv2.imread(nxt)
                                if img2_cv is None:
                                    raise Exception("cv2.imread falhou")
                            else:
                                pil2 = Image.open(nxt).convert("RGB")
                                img2_cv = cv2.cvtColor(np.array(pil2), cv2.COLOR_RGB2BGR)
                                del pil2
                        except Exception:
                            img2_cv = cv2.imread(nxt)
                        if img2_cv is not None:
                            img2_prep = prepare_ref(img2_cv)
                            del img2_cv
                            first_frame_next = apply_transform_ref(img2_prep, 0.0, 0.0)
                            for f in range(trans_frames):
                                alpha = (f+1)/trans_frames
                                # Usar a nova função de transição
                                blended = self._apply_transition(last_frame, first_frame_next, alpha, trans_type, W, H)
                                out_write_global(blended)
                                del blended
                            skip_first_map[nxt] = True
                            last_frame_for_transition = first_frame_next.copy()  # Atualizar
                            del img2_prep, first_frame_next
                try:
                    del base, last_frame
                except Exception:
                    pass
                gc.collect()
                img_i += 1
                prev_kind = "image"

        # Mixar áudio dos vídeos (divisão proporcional) se ativado
        self._last_clips_audio = None
        if getattr(self, 'keep_video_audio', tk.BooleanVar(value=False)).get() and len(clips) > 0:
            try:
                self.log("[audio] Mixando áudio original dos vídeos (divisão proporcional)...")
                from pydub import AudioSegment
                mixed = AudioSegment.silent(duration=int(total_dur * 1000))
                vol_factor = getattr(self, 'video_audio_vol', tk.DoubleVar(value=1.0)).get()
                clips_set = set(str(c) for c in clips)
                all_media = self.get_media_items()
                slice_dur_ms = int((total_dur / max(1, len(all_media))) * 1000)
                curr_ms = 0
                for path in all_media:
                    if str(path) in clips_set:
                        try:
                            seg = AudioSegment.from_file(str(path))
                            clip_speed = getattr(self, 'clip_speed', tk.IntVar(value=100)).get() / 100.0
                            if abs(clip_speed - 1.0) > 0.05:
                                seg = seg.speedup(playback_speed=clip_speed)
                            if len(seg) > slice_dur_ms:
                                seg = seg[:slice_dur_ms]
                            if vol_factor != 1.0 and vol_factor > 0:
                                seg = seg + (20 * math.log10(vol_factor))
                            mixed = mixed.overlay(seg, position=curr_ms)
                        except Exception as e:
                            self.log(f"[audio] Aviso: Falha ao extrair áudio de {path}: {e}")
                    curr_ms += slice_dur_ms

                clips_audio_p = BASE_DIR / f"temp_clips_audio_{os.getpid()}.wav"
                mixed.export(str(clips_audio_p), format="wav")
                self._last_clips_audio = str(clips_audio_p)
                self.log("[audio] Áudio dos vídeos mixado (proporcional) com sucesso.")
            except Exception as e:
                self.log(f"[audio] Erro ao mixar áudio (proporcional): {e}")

        out.release()
        self.log("Vídeo base OK")
        gc.collect()

    def _verify_and_adjust_timeline(self, timeline_images, words, total_dur):
        """
        VERSÃO SIMPLIFICADA: Apenas verifica e retorna o mapping original.
        O mapping já vem com os tempos corretos do gerador inteligente.
        NÃO modifica os tempos para evitar quebrar a sincronização.
        """
        if not timeline_images:
            return timeline_images
        
        self.log(f"[verify] Verificando timeline com {len(timeline_images)} itens")
        
        # Apenas garantir que os tempos estão em ordem crescente
        adjusted = []
        prev_end = 0.0
        total = float(total_dur or 0.0)
        
        for idx, item in enumerate(timeline_images):
            new_item = dict(item)
            start = float(item.get("start", prev_end))
            end = float(item.get("end", start + 1.0))
            
            # Garantir encadeamento: início >= fim anterior
            if start < prev_end:
                start = prev_end
            
            # Garantir que end > start
            if end <= start:
                end = min(total, start + MIN_SCENE_DURATION)
            
            # Última cena vai até o final
            if idx == len(timeline_images) - 1:
                end = total
            
            new_item["start"] = round(start, 3)
            new_item["end"] = round(end, 3)
            adjusted.append(new_item)
            prev_end = end
            
            self.log(f"[verify] Cena {idx+1}: {start:.2f}s - {end:.2f}s ({Path(item.get('file','')).name})")
        
        return adjusted

    def _render_intro_video(self, intro_path, out_mp4, W, H):
        """Renderiza o vídeo intro na resolução correta, mantendo velocidade original."""
        self.log(f"[intro] Renderizando vídeo intro: {os.path.basename(intro_path)}")
        try:
            # Usar FFmpeg para recodificar o intro na resolução correta
            cmd = [
                self.ffmpeg, '-y', '-i', str(intro_path),
                '-vf', f'scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                '-an',  # Sem áudio aqui, será mixado depois
                '-r', str(self.fps),
                str(out_mp4)
            ]
            subprocess.run(cmd, capture_output=True, timeout=300)
            if Path(out_mp4).exists():
                self.log(f"[intro] Intro renderizado: {out_mp4}")
                return True
        except Exception as e:
            self.log(f"[intro] Erro ao renderizar intro: {e}")
        return False

    # ---------- _build_base_using_timeline ----------
    def _build_base_using_timeline(self, timeline_images, clips, out_mp4, W, H, total_dur, trans_type, trans_dur, force_fade=False):
        self.log(f"Criando vídeo base usando timeline {W}x{H}... (transição: {trans_type}, {trans_dur:.2f}s)")
        
        # DEBUG: Verificar estado dos efeitos
        self.log(f"[efeitos] zoom_basic={self.zoom_basic.get()}, float_en={self.float_en.get()}")
        if hasattr(self, 'pan_en'):
            self.log(f"[efeitos] pan_en={self.pan_en.get()}, tilt_en={self.tilt_en.get()}, shake_en={self.shake_en.get()}, kenburns_en={self.kenburns_en.get()}")
        
        # Verificar se há vídeo intro habilitado
        intro_offset = self.get_intro_offset()
        intro_path = None
        intro_temp = None
        self.log(f"[intro] intro_offset={intro_offset}, intro_video_en={self.intro_video_en.get() if hasattr(self, 'intro_video_en') else 'N/A'}")
        if intro_offset > 0:
            intro_path = self.intro_video_path.get()
            self.log(f"[intro] intro_path={intro_path}, exists={Path(intro_path).exists() if intro_path else False}")
            if intro_path and Path(intro_path).exists():
                self.log(f"[intro] Vídeo intro detectado: {intro_offset:.1f}s")
                intro_temp = BASE_DIR / f"_intro_temp_{os.getpid()}.mp4"
                render_ok = self._render_intro_video(intro_path, intro_temp, W, H)
                self.log(f"[intro] Render result: {render_ok}, temp exists: {intro_temp.exists() if intro_temp else False}")
                if not render_ok:
                    intro_temp = None
                    intro_offset = 0
        
        # Usar FFmpeg pipe em vez de cv2.VideoWriter (mp4v falha com vídeos H264/Veo)
        _ffpipe_cmd = [
            self.ffmpeg, '-y',
            '-f', 'rawvideo', '-pix_fmt', 'bgr24',
            '-s', f'{W}x{H}',
            '-r', str(int(self.fps)),
            '-i', 'pipe:0',
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
            '-movflags', '+faststart',
            str(out_mp4)
        ]
        self.log(f"[build] Iniciando escritor FFmpeg-pipe ({W}x{H} @ {int(self.fps)}fps)")
        _ffpipe_proc = subprocess.Popen(_ffpipe_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        _pipe_broken = [False]
        _frames_written = [0]
        _ffpipe_cmd_ref = list(_ffpipe_cmd)
        _proc_holder = [_ffpipe_proc]  # Lista mutável para evitar nonlocal

        def _write_frame(frm):
            # Se pipe anterior morreu, tentar reiniciar o processo FFmpeg
            if _pipe_broken[0]:
                try:
                    _proc_holder[0].stdin.close()
                except Exception:
                    pass
                try:
                    _proc_holder[0].wait(timeout=5)
                except Exception:
                    pass
                try:
                    _proc_holder[0] = subprocess.Popen(_ffpipe_cmd_ref, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    _pipe_broken[0] = False
                    self.log("[build] Pipe FFmpeg reiniciado após quebra.")
                except Exception as _re:
                    self.log(f"[build] Não foi possível reiniciar pipe: {_re}")
                    return
            try:
                proc = _proc_holder[0]
                if proc.poll() is None:
                    proc.stdin.write(frm.tobytes())
                    _frames_written[0] += 1
                    # Flush periódico a cada 30 frames para liberar buffer do pipe
                    if _frames_written[0] % 30 == 0:
                        try:
                            proc.stdin.flush()
                        except Exception:
                            pass
            except Exception as _we:
                if not _pipe_broken[0]:
                    self.log(f"[build] Aviso ao escrever frame: {_we}")
                    _pipe_broken[0] = True

        # Se temos intro, primeiro escrever os frames do intro
        if intro_temp and intro_temp.exists():
            self.log(f"[intro] Escrevendo frames do intro...")
            cap = cv2.VideoCapture(str(intro_temp))
            frame_count = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                # Garantir tamanho correto
                if frame.shape[1] != W or frame.shape[0] != H:
                    frame = cv2.resize(frame, (W, H))
                _write_frame(frame)
                frame_count += 1
            cap.release()
            self.log(f"[intro] Frames do intro escritos: {frame_count} frames")
            # Limpar temp
            try:
                intro_temp.unlink()
            except Exception:
                pass

        # Nota: timeline_images agora pode conter vídeos e imagens (arquivos).
        # Processamos a sequência na ordem do timeline (cada item tem 'file','start','end').

        # Ordena por índice de bloco, se disponível, para garantir 1..N
        try:
            timeline_images = sorted(list(timeline_images), key=lambda x: int(x.get("block_index", 0)))
        except Exception:
            timeline_images = list(timeline_images)

        # Respeita preferência de corte estrito (sem fade antecipado)
        strict = bool(getattr(self, "strict_cuts", tk.BooleanVar(value=False)).get())
        # permite forçar fade para esta execução sem alterar a preferência do usuário
        if force_fade and trans_type not in ("sem", "none", ""):
            if strict:
                self.log(f"[transição] Aviso: forçando aplicação de '{trans_type}' mesmo com 'Cortes estritos' ativo.")
            strict = False
        # Verificar se usa transição (qualquer tipo exceto "sem")
        # Se o usuário escolheu uma transição explicitamente, SEMPRE aplicar (ignorar strict)
        use_transition = trans_type not in ("sem", "none", "")
        if use_transition and strict:
            self.log(f"[transição] Aplicando '{trans_type}' (usuário selecionou, ignorando 'cortes estritos')")
        trans_frames = int(max(0.0, trans_dur)*self.fps) if use_transition else 0
        self.log(f"[transição] Tipo: {trans_type}, frames: {trans_frames}, duração: {trans_dur:.2f}s")
        low_mem = bool(self.low_mem_mode.get())
        # evita NameError ao referenciar skip_first_map durante crossfades
        skip_first_map = {}
        # lista de arquivos temporários gerados para segmentos esticados
        tmp_created = []
        total_timeline_items = len(timeline_images)

        # Quando há intro, os tempos no timeline já estão deslocados por intro_offset
        # Os frames do intro já foram escritos, então agora precisamos escrever as cenas
        # A duração de cada cena é calculada a partir dos tempos no timeline

        # IMPORTANTE: Se o intro já foi renderizado acima, PULAR a cena de intro no loop
        # para evitar duplicação de frames
        intro_already_rendered = (intro_temp is not None) or (intro_offset > 0 and intro_path)

        # ======================================================================
        # PRÉ-GERAÇÃO: criar todos os segmentos ajustados ANTES de abrir o pipe
        # Isso evita que o pipe FFmpeg fique ocioso por ~15s enquanto cada
        # segmento é gerado, o que causava o "Broken pipe".
        # ======================================================================
        _VIDEO_EXTS = ('.mp4', '.mov', '.mkv', '.avi', '.webm')
        pre_seg_map = {}  # {img_path: stretched_path}
        self.log("[build] Pré-gerando segmentos de vídeo ajustados...")
        _prev_cut = None
        for _pi, _pitem in enumerate(timeline_images):
            if _pitem.get("is_intro", False) and intro_already_rendered:
                _prev_cut = float(_pitem.get("end", intro_offset))
                continue
            _ppath = _pitem["file"]
            if Path(_ppath).suffix.lower() not in _VIDEO_EXTS:
                continue
            # Calcular dur_img para este item (mesma lógica do loop principal)
            _ps = float(_pitem.get("start", 0.0))
            _pe = float(_pitem.get("end", _ps + 0.5))
            _eff_s = _prev_cut if _prev_cut is not None else _ps
            if _pi + 1 < len(timeline_images):
                _ns = float(timeline_images[_pi + 1].get("start", _pe))
                _bnd = min(_pe, _ns)
            else:
                _bnd = min(max(_pe, _eff_s + 0.01), float(total_dur))
            _eff_e = max(_eff_s + 0.01, _bnd)
            _dur = max(0.01, _eff_e - _eff_s)
            _prev_cut = _eff_e
            try:
                _src = self._create_stretched_segment(_ppath, _dur, W, H, self.fps, _pi + 1)
                pre_seg_map[_ppath] = _src
                if _src and str(_src) != str(_ppath):
                    tmp_created.append(_src)
            except Exception as _pe_err:
                self.log(f"[build] pré-geração falhou para {Path(_ppath).name}: {_pe_err}")
                pre_seg_map[_ppath] = _ppath
        self.log(f"[build] Pré-geração concluída: {len(pre_seg_map)} segmento(s) pronto(s).")
        # ======================================================================

        prev_cut_time = None
        for idx, item in enumerate(timeline_images):
            # PULAR cena de intro se já foi renderizada
            if item.get("is_intro", False) and intro_already_rendered:
                self.log(f"[timeline] Pulando intro (já renderizado): {Path(item.get('file','')).name}")
                prev_cut_time = float(item.get("end", intro_offset))
                continue
            
            # Atualizar progresso: 20% a 45% durante build_base_using_timeline
            progress_pct = 20 + int((idx / max(1, total_timeline_items)) * 25)
            self._update_progress(progress_pct)
            
            img_path = item["file"]
            start_m = float(item.get("start",0.0))
            end_m = float(item.get("end", start_m + 0.5))
            # Início efetivo: para evitar gaps e garantir continuidade exata, encadeia pelo corte anterior
            if prev_cut_time is None:
                effective_start = start_m
            else:
                # encadeamento estrito: início da atual = fim da anterior
                effective_start = prev_cut_time

            # Borda da cena
            if idx+1 < len(timeline_images):
                try:
                    next_start = float(timeline_images[idx+1].get("start", end_m))
                except Exception:
                    next_start = end_m
                if strict:
                    # corte exato na borda: termina exatamente no início da próxima
                    boundary = min(end_m, next_start)
                else:
                    # com fade: ainda assim não extrapola o início da próxima (crossfade ocorre dentro do segmento)
                    boundary = min(end_m, next_start)
            else:
                # última cena: segura até o fim do áudio
                boundary = min(max(end_m, effective_start + 0.01), float(total_dur))

            effective_end = max(effective_start + 0.01, boundary)

            dur_img = max(0.01, effective_end - effective_start)
            frames_total = int(round(dur_img * self.fps))
            if frames_total <= 0:
                continue

            # Crossfade deve ocorrer dentro do segmento (sobreposição), não após o fim
            overlap_frames = trans_frames if (trans_frames > 0 and idx+1 < len(timeline_images)) else 0
            # manter pelo menos 1 frame "base" antes da transição
            if frames_total <= 1:
                overlap_frames = 0
            else:
                overlap_frames = min(overlap_frames, max(frames_total - 1, 0))
            base_frames = max(0, frames_total - overlap_frames)
            last_frame = None
            suff = Path(img_path).suffix.lower()
            is_video = suff in ('.mp4','.mov','.mkv','.avi','.webm')
            if is_video:
                # Usar segmento pré-gerado (evita idle no pipe durante geração)
                src_for_read = pre_seg_map.get(img_path, img_path)

                # STREAMING de frames: ler diretamente do arquivo sem acumular tudo em RAM
                # Para need <= avail (aceleração): stream e para após 'need' frames
                # Para need > avail (desaceleração): buffer e loop (vídeo curto)
                overrides = self._get_random_overrides()
                start_skip = 1 if skip_first_map.get(img_path, False) else 0
                if start_skip:
                    try: del skip_first_map[img_path]
                    except Exception: pass
                write_count = base_frames if overlap_frames > 0 else frames_total
                if write_count <= 0:
                    write_count = 1

                try:
                    cap = cv2.VideoCapture(str(src_for_read))
                    total_avail_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                    need = frames_total

                    if total_avail_frames <= 0 or need <= total_avail_frames:
                        # FAST PATH: stream direto, sem buffer de RAM
                        inv = 1.0 / max(1, write_count - 1) if write_count > 1 else 1.0
                        frames_read = 0
                        written = 0
                        while written < write_count + start_skip:
                            ok, fr = cap.read()
                            if not ok:
                                break
                            frames_read += 1
                            if frames_read <= start_skip:
                                continue
                            actual_f = written
                            try:
                                prepared = self._prepare_frame_for_size(fr, W, H)
                            except Exception:
                                prepared = fr
                            t_frac = actual_f * inv
                            t_sec = actual_f / self.fps
                            frame2 = self._apply_transform(prepared, t_frac, t_sec, W, H, overrides=overrides)
                            _write_frame(frame2)
                            last_frame = frame2
                            written += 1
                        cap.release()
                    else:
                        # SLOW PATH: buffer frames e loop (necessário para slow-motion)
                        frames_list = []
                        while True:
                            ok, fr = cap.read()
                            if not ok: break
                            try:
                                frames_list.append(self._prepare_frame_for_size(fr, W, H))
                            except Exception:
                                frames_list.append(fr)
                        cap.release()
                        if not frames_list:
                            continue
                        avail = len(frames_list)
                        inv = 1.0 / max(1, write_count - 1) if write_count > 1 else 1.0
                        for f in range(write_count):
                            fi = (f + start_skip) % avail
                            frame2 = self._apply_transform(frames_list[fi], f * inv, f / self.fps, W, H, overrides=overrides)
                            _write_frame(frame2)
                            last_frame = frame2
                        del frames_list

                    if last_frame is None:
                        continue

                except Exception as e:
                    self.log(f"⚠️ Falha ao processar vídeo '{img_path}': {e}")
                    continue

            else:
                # imagem estática (comportamento anterior)
                img_cv = None
                if low_mem:
                    img_cv = cv2.imread(img_path)
                    if img_cv is None:
                        try:
                            pil = Image.open(img_path).convert("RGB"); img_cv = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR); del pil
                        except Exception as e:
                            self.log(f"⚠️ Falha ao abrir imagem '{img_path}': {e}")
                            continue
                else:
                    try:
                        pil = Image.open(img_path).convert("RGB"); img_cv = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR); del pil
                    except Exception:
                        img_cv = cv2.imread(img_path)
                        if img_cv is None:
                            self.log(f"⚠️ Imagem ignorada: {img_path}")
                            continue
                base = self._prepare_frame_for_size(img_cv, W, H)
                del img_cv
                
                # EFEITOS ALEATÓRIOS (para este segmento de imagem)
                overrides = self._get_random_overrides()

                if base_frames > 0:
                    inv = 1.0 / max(1, (base_frames - 1)) if base_frames > 1 else 1.0
                    start_skip = 1 if skip_first_map.get(img_path, False) else 0
                    if start_skip:
                        try:
                            del skip_first_map[img_path]
                        except Exception:
                            pass
                    for f in range(start_skip, base_frames):
                        t_frac = f * inv
                        # t_sec relativo ao segmento atual (não absoluto)
                        t_sec = f / self.fps
                        frame = self._apply_transform(base, t_frac, t_sec, W, H, overrides=overrides)
                        _write_frame(frame); last_frame = frame
                else:
                    last_frame = self._apply_transform(base, 1.0, 0.0, W, H, overrides=overrides)

            # Crossfade interno ao segmento
            if overlap_frames > 0:
                nxt = None
                for j in range(idx+1, len(timeline_images)):
                    nxt = timeline_images[j]["file"]; break
                if nxt:
                    first_frame_next = None
                    nxt_suff = Path(str(nxt)).suffix.lower()
                    nxt_is_video = nxt_suff in ('.mp4', '.mov', '.mkv', '.avi', '.webm')
                    if nxt_is_video:
                        # Próxima cena é vídeo: pegar o primeiro frame do próximo vídeo
                        try:
                            cap2 = cv2.VideoCapture(str(nxt))
                            ok2, fr2 = cap2.read()
                            cap2.release()
                            if ok2 and fr2 is not None:
                                fr2p = self._prepare_frame_for_size(fr2, W, H)
                                first_frame_next = self._apply_transform(fr2p, 0.0, 0.0, W, H)
                                del fr2p
                        except Exception:
                            first_frame_next = None
                    else:
                        # Próxima cena é imagem
                        img2_cv = None
                        if low_mem:
                            img2_cv = cv2.imread(nxt)
                            if img2_cv is None:
                                try:
                                    pil2 = Image.open(nxt).convert("RGB"); img2_cv = cv2.cvtColor(np.array(pil2), cv2.COLOR_RGB2BGR); del pil2
                                except:
                                    img2_cv = None
                        else:
                            try:
                                pil2 = Image.open(nxt).convert("RGB"); img2_cv = cv2.cvtColor(np.array(pil2), cv2.COLOR_RGB2BGR); del pil2
                            except:
                                img2_cv = cv2.imread(nxt)
                        if img2_cv is not None:
                            img2_prep = self._prepare_frame_for_size(img2_cv, W, H)
                            first_frame_next = self._apply_transform(img2_prep, 0.0, 0.0, W, H)
                            del img2_prep

                    if first_frame_next is not None and last_frame is not None:
                        for f in range(overlap_frames):
                            # Usa (overlap_frames+1) para evitar alpha==1.0 (sem frame duplicado)
                            alpha = (f+1) / (overlap_frames + 1.0)
                            blended = self._apply_transition(last_frame, first_frame_next, alpha, trans_type, W, H)
                            _write_frame(blended)
                        try:
                            # Marca o próximo arquivo para pular o primeiro frame (evita duplicação)
                            skip_first_map[nxt] = True
                        except Exception:
                            pass
                        try:
                            del first_frame_next
                        except Exception:
                            pass
            prev_cut_time = effective_end
            try:
                if 'base' in locals():
                    del base
            except Exception:
                pass
            try:
                if 'last_frame' in locals():
                    del last_frame
            except Exception:
                pass
            gc.collect()
        try:
            _proc_holder[0].stdin.close()
        except Exception:
            pass
        try:
            rc = _proc_holder[0].wait(timeout=120)
            if rc != 0:
                self.log(f"[build] Aviso: processo FFmpeg-pipe encerrou com código {rc}")
        except Exception as _we:
            self.log(f"[build] Aviso ao aguardar FFmpeg-pipe: {_we}")
        self.log(f"Vídeo base (timeline) OK — {_frames_written[0]} frames escritos")
        
        # Mixar áudio dos vídeos esticados se ativado
        self._last_clips_audio = None
        if getattr(self, 'keep_video_audio', tk.BooleanVar(value=False)).get() and len(clips) > 0:
            try:
                self.log("[audio] Extraindo e mixando áudio original dos segmentos esticados...")
                from pydub import AudioSegment
                mixed = AudioSegment.silent(duration=int(total_dur * 1000))
                vol_factor = getattr(self, 'video_audio_vol', tk.DoubleVar(value=1.0)).get()
                
                for item in timeline_images:
                    orig_path = item["file"]
                    if orig_path not in clips:
                        continue
                    stretched_path = pre_seg_map.get(orig_path, orig_path)
                    
                    start_ms = int(float(item.get("start", 0)) * 1000)
                    end_ms = int(float(item.get("end", total_dur)) * 1000)
                    clip_dur_ms = end_ms - start_ms
                    if clip_dur_ms <= 0: continue
                    
                    try:
                        seg = AudioSegment.from_file(str(stretched_path))
                        if len(seg) > clip_dur_ms:
                            seg = seg[:clip_dur_ms]
                            
                        if vol_factor != 1.0:
                            if vol_factor > 0:
                                seg = seg + (20 * math.log10(vol_factor))
                            else:
                                seg = seg - 100
                        
                        mixed = mixed.overlay(seg, position=start_ms)
                    except Exception as err:
                        self.log(f"[audio] Aviso: Não foi possível extrair áudio do segmento {Path(stretched_path).name}: {err}")
                
                clips_audio_path = BASE_DIR / f"temp_clips_audio_{os.getpid()}.wav"
                mixed.export(str(clips_audio_path), format="wav")
                self._last_clips_audio = str(clips_audio_path)
                self.log(f"[audio] Áudio dos vídeos esticados mixado com sucesso.")
            except Exception as e:
                self.log(f"[audio] Falha ao mixar áudio dos vídeos: {e}")
        # remover segmentos temporários criados
        try:
            for t in tmp_created:
                try:
                    Path(t).unlink()
                except Exception:
                    pass
        except Exception:
            pass
        gc.collect()

    def _build_base_ffmpeg(self, timeline_images, clips, out_mp4, W, H, total_dur, trans_type, trans_dur):
        import hardware_detector
        _hw_enc = hardware_detector.detect_h264_encoder()
        _vc_high = [*_vc_high] if _hw_enc == 'libx264' else ['-c:v', _hw_enc, '-b:v', '8M', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.2']
        _vc_base = [*_vc_base] if _hw_enc == 'libx264' else ['-c:v', _hw_enc, '-b:v', '6M']

        """
        Fallback: monta o vídeo base via ffmpeg usando os vídeos e as imagens (cada imagem com sua duração).
        Usa: -loop 1 -t <dur> -i <image> para imagens e -i <clip> para vídeos e concatena os streams.
        """
        try:
            self.log("[ffmpeg-fallback] Montando vídeo base via ffmpeg...")
            cmd = [self.ffmpeg, "-y", "-threads", "0"]
            inputs = []
            # primeiro, adicionar clips (se existirem)
            for c in clips:
                cmd += ["-i", win_short_path(str(c))]
                inputs.append({'type': 'video', 'path': win_short_path(str(c))})
            # depois, imagens com durações (usando timeline_images order)
            imgs = []
            for item in timeline_images:
                p = item.get('file')
                dur = max(0.01, float(item.get('end', item.get('start', 0.0))) - float(item.get('start', 0.0)))
                _suff = Path(str(p)).suffix.lower() if p else ''
                _is_vid = _suff in ('.mp4', '.mov', '.mkv', '.avi', '.webm')
                if _is_vid:
                    # Vídeo: limitar duração sem loop (loop não funciona em vídeos)
                    cmd += ["-t", f"{dur:.3f}", "-i", win_short_path(str(p))]
                    inputs.append({'type': 'video', 'path': win_short_path(str(p)), 'dur': dur})
                else:
                    # Imagem: usar loop para preencher duração
                    cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", win_short_path(str(p))]
                    inputs.append({'type': 'image', 'path': win_short_path(str(p)), 'dur': dur})
                imgs.append(p)

            total_inputs = len(inputs)
            if total_inputs == 0:
                raise RuntimeError("Nenhum input para montar vídeo via ffmpeg.")

            # preparar filtros: para cada input, scale/crop
            filters = []
            for i in range(total_inputs):
                filters.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1[v{i}]")
            concat_inputs = ''.join(f"[v{i}]" for i in range(total_inputs))
            filters.append(f"{concat_inputs}concat=n={total_inputs}:v=1:a=0[outv]")
            filter_complex = ';'.join(filters)

            cmd += ["-filter_complex", filter_complex, "-map", "[outv]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", "-preset", "veryfast", "-crf", "22", str(out_mp4)]
            self.log(f"[ffmpeg-fallback] cmd: {' '.join(cmd[:6])} ... (completo em log)")
            proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if proc.returncode != 0:
                tail = (proc.stderr or proc.stdout or '')
                self.log(f"[ffmpeg-fallback] falhou: {tail[:1000]}")
                raise RuntimeError("ffmpeg fallback para montagem do vídeo base falhou.")
            self.log("[ffmpeg-fallback] Vídeo base criado com sucesso.")
            return True
        except Exception as e:
            self.log(f"[ffmpeg-fallback] Erro: {e}")
            return False

    # ---------- job manager (simple worker pool) ----------


    def _create_stretched_segment(self, input_path, target_dur, W, H, fps, idx=None):
        """
        V2 (vídeos): Ajusta um vídeo para caber exatamente em `target_dur`.
        - Se o vídeo for MAIOR que o target: CORTA (trim) sem mudar a velocidade.
        - Se o vídeo for MENOR que o target: ESTICA (setpts) para preencher.

        Obs: o áudio do vídeo é descartado (será mixado depois no pipeline principal).
        Retorna o caminho do arquivo gerado (pode ser o `input_path` original se nenhuma
        modificação for necessária ou falhar).
        """
        try:
            inp = str(input_path)
            # obter duração original via ffprobe
            dur = None
            try:
                p = subprocess.run([self.ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", inp], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
                if p.returncode == 0 and p.stdout:
                    dur = float(p.stdout.strip())
            except Exception:
                dur = None

            if dur is None or dur <= 0.001:
                return inp

            target = float(target_dur)
            if target <= 0.001:
                return inp

            # tolerância pequena para evitar reprocessar à toa
            eps = 0.05
            if abs(dur - target) <= eps:
                return inp

            out_name = BASE_DIR / f"_seg_{os.getpid()}_{idx or 0}.mp4"
            outp = str(out_name)

            # Normalizar resolução/fps e ajustar duração
            # Lógica Elastica (Speed Control)
            factor = float(target) / float(dur)
            
            vf = (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},setsar=1,fps={int(fps)},"
                f"setpts={factor:.6f}*PTS,"
                f"setpts=PTS-STARTPTS"
            )

            cmd = [
                self.ffmpeg, "-y",
                "-i", inp
            ]
            
            if getattr(self, 'keep_video_audio', tk.BooleanVar(value=False)).get():
                new_sr = max(100, int(44100 / factor))
                af = f"asetrate={new_sr},aresample=44100,aformat=sample_rates=44100:channel_layouts=stereo"
                cmd += ["-af", af, "-c:a", "aac", "-b:a", "192k"]
            else:
                cmd += ["-an"]

            cmd += [
                "-vf", vf,
                "-t", f"{target + 0.05:.3f}",
                "-r", str(int(fps)),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", "-preset", "veryfast", "-crf", "18",
                outp,
            ]

            action = "acelerando" if factor < 1.0 else "esticando"
            self.log(f"[seg] {action} vídeo e áudio: factor={factor:.3f} ({dur:.3f}s -> {target:.3f}s)")

            r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
            file_valid = Path(outp).exists() and Path(outp).stat().st_size > 10000
            if file_valid:
                if r.returncode != 0:
                    self.log(f"[seg] Arquivo gerado com rc={r.returncode} (aceito - arquivo válido com {Path(outp).stat().st_size} bytes)")
                return outp
            else:
                err_tail = (r.stderr or "")[-400:]
                self.log(f"[seg] ffmpeg falhou (rc={r.returncode}, arquivo ausente/inválido): {err_tail[:300]}")
                # Limpar arquivo parcial
                try:
                    if Path(outp).exists():
                        Path(outp).unlink()
                except Exception:
                    pass
                return inp
        except Exception as e:
            self.log(f"[seg] erro criar segmento: {e}")
            return str(input_path)

    def _apply_transition(self, frame1, frame2, alpha, trans_type, W, H):
        """
        Aplica diferentes tipos de transição entre dois frames.
        """
        if self.random_eff_en.get() and trans_type not in ("sem", "none", ""):
            import random
            try:
                # Hash baseado nos dados do frame1 + seed da sessão
                # Garante consistência durante a transição (mesma escolha para todos os frames)
                # Mas varia a cada execução do programa
                h_val = hash(frame1.tobytes()[:2048])
                seed_val = h_val + getattr(self, 'session_seed', 0)
                rng = random.Random(seed_val)
                opts = ["fade","slide_left","slide_right","slide_up","slide_down","zoom_in","zoom_out","wipe_left","wipe_right"]
                trans_type = rng.choice(opts)
            except Exception:
                pass

        if trans_type in ("sem", "none", ""):
            return frame2 if alpha > 0.5 else frame1
        
        elif trans_type in ("fade", "dissolve"):
            # Crossfade/dissolve clássico
            return cv2.addWeighted(frame1, 1.0 - alpha, frame2, alpha, 0.0)
        
        elif trans_type == "slide_left":
            # Frame2 entra da direita para esquerda
            offset = int((1.0 - alpha) * W)
            result = np.zeros_like(frame1)
            if offset < W:
                result[:, :W-offset] = frame2[:, offset:]
            if offset > 0:
                result[:, W-offset:] = frame1[:, :offset]
            return result
        
        elif trans_type == "slide_right":
            # Frame2 entra da esquerda para direita
            offset = int((1.0 - alpha) * W)
            result = np.zeros_like(frame1)
            if offset < W:
                result[:, offset:] = frame2[:, :W-offset]
            if offset > 0:
                result[:, :offset] = frame1[:, W-offset:]
            return result
        
        elif trans_type == "slide_up":
            # Frame2 entra de baixo para cima
            offset = int((1.0 - alpha) * H)
            result = np.zeros_like(frame1)
            if offset < H:
                result[:H-offset, :] = frame2[offset:, :]
            if offset > 0:
                result[H-offset:, :] = frame1[:offset, :]
            return result
        
        elif trans_type == "slide_down":
            # Frame2 entra de cima para baixo
            offset = int((1.0 - alpha) * H)
            result = np.zeros_like(frame1)
            if offset < H:
                result[offset:, :] = frame2[:H-offset, :]
            if offset > 0:
                result[:offset, :] = frame1[H-offset:, :]
            return result
        
        elif trans_type == "wipe_left":
            # Wipe horizontal da direita para esquerda
            pos = int(alpha * W)
            result = frame1.copy()
            if pos > 0:
                result[:, :pos] = frame2[:, :pos]
            return result
        
        elif trans_type == "wipe_right":
            # Wipe horizontal da esquerda para direita
            pos = int((1.0 - alpha) * W)
            result = frame2.copy()
            if pos > 0:
                result[:, :pos] = frame1[:, :pos]
            return result
        
        elif trans_type == "zoom_in":
            # Frame1 dá zoom in enquanto frame2 aparece
            scale = 1.0 + alpha * 0.5  # zoom de 1.0 até 1.5
            M = cv2.getRotationMatrix2D((W/2, H/2), 0, scale)
            zoomed = cv2.warpAffine(frame1, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
            # Blend com frame2
            return cv2.addWeighted(zoomed, 1.0 - alpha, frame2, alpha, 0.0)
        
        elif trans_type == "zoom_out":
            # Frame2 começa com zoom e vai para tamanho normal
            scale = 1.5 - alpha * 0.5  # zoom de 1.5 até 1.0
            M = cv2.getRotationMatrix2D((W/2, H/2), 0, scale)
            zoomed = cv2.warpAffine(frame2, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
            # Blend com frame1
            return cv2.addWeighted(frame1, 1.0 - alpha, zoomed, alpha, 0.0)
        
        else:
            # Fallback para fade
            return cv2.addWeighted(frame1, 1.0 - alpha, frame2, alpha, 0.0)

    # ---------- Helper para Efeitos Aleatórios ----------
    def _get_random_overrides(self):
        """Retorna dicionário com ONE efeito ativado aleatoriamente, se checkbox Aleatório estiver marcado."""
        import random
        if not self.random_eff_en.get():
            return None
            
        options = ['zoom_basic', 'zoom_adv_en', 'float_en', 'pan_en', 'tilt_en', 'shake_en', 'kenburns_en']
        chosen = random.choice(options)
        
        # Desativa todos, ativa o escolhido
        overrides = {k: False for k in options}
        overrides[chosen] = True
        return overrides

    def _prepare_frame_for_size(self, img_np, W, H):
        h, w = img_np.shape[:2]; tr = W/H; ir = w/h
        if ir > tr: nh=H; nw=int(nh*ir)
        else: nw=W; nh=int(nw/ir)
        interp = cv2.INTER_LINEAR if bool(self.low_mem_mode.get()) else cv2.INTER_LANCZOS4
        r = cv2.resize(img_np,(nw,nh),interpolation=interp)
        x0=(nw-W)//2; y0=(nh-H)//2
        return r[y0:y0+H, x0:x0+W].copy()

    def _apply_transform(self, base_img, t_frac, t_sec, W, H, overrides=None):
        import random
        ease = math.sin(math.pi * t_frac)
        scale = 1.0
        dx = 0
        dy = 0
        
        def get_flag(name, attr_name=None):
            if overrides is not None and name in overrides:
                return overrides[name]
            # Se não houver override, usa configuração global da UI
            attr = attr_name if attr_name else name
            if hasattr(self, attr):
                return getattr(self, attr).get()
            return False

        # Zoom básico (suave)
        if get_flag('zoom_basic'):
            scale += (0.10) * ease
        
        # Zoom avançado (senoidal)
        if get_flag('zoom_adv_en'):
            scale += float(self.zoom_adv_amp.get()) * math.sin(2*math.pi * t_frac)
        
        # Flutuar lateral (oscilação senoidal)
        if get_flag('float_en') and float(self.float_period.get()) > 0:
            dx += int(self.float_amp.get() * math.sin(2*math.pi * (t_sec / float(self.float_period.get()))))
        
        # Pan (movimento horizontal contínuo esquerda→direita)
        if get_flag('pan_en'):
            pan_speed = float(self.pan_speed.get()) if hasattr(self, 'pan_speed') else 0.05
            # Move de -10% a +10% da largura ao longo do tempo
            pan_offset = (t_frac - 0.5) * 2 * pan_speed * W
            dx += int(pan_offset)
        
        # Tilt (movimento vertical contínuo cima→baixo)
        if get_flag('tilt_en'):
            tilt_speed = float(self.tilt_speed.get()) if hasattr(self, 'tilt_speed') else 0.05
            # Move de -10% a +10% da altura ao longo do tempo
            tilt_offset = (t_frac - 0.5) * 2 * tilt_speed * H
            dy += int(tilt_offset)
        
        # Shake (tremor aleatório)
        if get_flag('shake_en'):
            intensity = int(self.shake_intensity.get()) if hasattr(self, 'shake_intensity') else 3
            # Usar gerador isolado para não afetar o estado global
            rng = random.Random(int(t_sec * 1000))
            dx += rng.randint(-intensity, intensity)
            dy += rng.randint(-intensity, intensity)
        
        # Ken Burns (zoom + pan combinado - efeito cinematográfico)
        if get_flag('kenburns_en'):
            kb_intensity = float(self.kenburns_intensity.get()) if hasattr(self, 'kenburns_intensity') else 0.15
            # Zoom gradual de 1.0 para 1.0+intensity
            scale += kb_intensity * t_frac
            # Pan diagonal suave
            kb_pan = kb_intensity * 0.5 * W * (t_frac - 0.5)
            dx += int(kb_pan * 0.7)  # Mais horizontal
            dy += int(kb_pan * 0.3)  # Menos vertical
        
        # Aplicar transformação
        M = cv2.getRotationMatrix2D((W/2, H/2), 0, scale)
        M[0,2] += dx
        M[1,2] += dy
        frame = cv2.warpAffine(base_img, M, (W,H), borderMode=cv2.BORDER_REPLICATE)
        return frame

    def _build_broll_sfx_chain(self, broll_windows, cmd, fc, out_a, next_idx):
        """
        [E9] Para cada janela de B-Roll, injeta um SFX de transição (woosh/impact)
        no timestamp exato de entrada do B-Roll via `adelay` + `amix`.

        - Reutiliza o mesmo arquivo de SFX para todas as transições
        - Usa `adelay={ms}` para posicionar o SFX no tempo certo
        - Retorna (fc, out_a, next_idx) atualizados ou (fc, out_a, next_idx) inalterados em falha
        """
        sfx_path = getattr(self, 'sfx_transition_path', None)
        sfx_vol  = getattr(self, 'sfx_transition_vol', None)

        if not sfx_path:
            return fc, out_a, next_idx

        sfx_file = sfx_path.get() if hasattr(sfx_path, 'get') else str(sfx_path)
        vol_val  = float(sfx_vol.get()) if sfx_vol else 0.5

        if not sfx_file or not Path(sfx_file).exists():
            self.log("[E9] ⚠️ Arquivo SFX de transição não encontrado. Ignorando.")
            return fc, out_a, next_idx

        sfx_labels = []
        for i, win in enumerate(broll_windows):
            bst_ms = int(win["start"] * 1000)  # converter para milissegundos
            sfx_label = f"sfxtr{i}"

            # Adicionar o arquivo SFX como input (um por transição, posicionado com adelay)
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

        if not sfx_labels:
            return fc, out_a, next_idx

        # Misturar todos os SFX com o áudio corrente
        all_inputs = f"[{out_a}]" + "".join(f"[{l}]" for l in sfx_labels)
        n_inputs   = 1 + len(sfx_labels)
        mixed_label = "sfxtr_out"
        fc.append(
            f"{all_inputs}amix=inputs={n_inputs}:duration=longest:dropout_transition=0"
            f"[{mixed_label}]"
        )
        self.log(f"[E9] ⚡ {len(sfx_labels)} SFX(s) de transição sincronizados com B-Roll")
        return fc, mixed_label, next_idx

    def _collect_broll_windows(self, words):
        """
        [E4] Agrupa palavras com broll_path em janelas de tempo {path, start, end}.
        Janelas com o mesmo arquivo são mescladas. Limite: no máximo 6 B-Rolls por vídeo
        para não sobrecarregar o filter_complex.
        Retorna: lista de dicts [{path, start, end}, ...]
        """
        if not words:
            return []

        windows = []
        cur_path = None
        cur_start = None
        cur_end = None

        for w in words:
            bp = w.get("broll_path")
            wst = float(w.get("start", 0))
            wen = float(w.get("end", wst + 0.1))

            if bp and Path(bp).exists():
                if bp == cur_path and wst <= cur_end + 0.5:
                    # Estender janela atual
                    cur_end = max(cur_end, wen)
                else:
                    # Fechar janela anterior
                    if cur_path:
                        windows.append({"path": cur_path, "start": cur_start, "end": cur_end})
                    cur_path  = bp
                    cur_start = wst
                    cur_end   = wen
            else:
                if cur_path:
                    windows.append({"path": cur_path, "start": cur_start, "end": cur_end})
                    cur_path = None

        if cur_path:
            windows.append({"path": cur_path, "start": cur_start, "end": cur_end})

        # Garantir duração mínima de 1s por B-Roll
        for w in windows:
            if w["end"] - w["start"] < 1.0:
                w["end"] = w["start"] + 1.0

        return windows[:6]  # Limite de segurança: max 6 B-Rolls

    def _apply_broll_overlays(self, broll_windows, cmd, fc, cur_label, next_idx, W, H):
        """
        [E4] Injeta cada B-Roll como overlay FFmpeg sobre o vídeo base.

        - Imagens (png/jpg): usa loop=1 + trim para a duração exata
        - Vídeos (mp4/mov): usa trim + setpts para o segmento exato
        - Escala o B-Roll para W×H mantendo o aspecto (preenche com blur se necessário)
        - Usa enable='between(t,s,e)' para ativar/desativar no tempo certo
        - Retorna (fc_atualizado, cur_label_novo, next_idx_novo) ou None em falha
        """
        try:
            VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
            IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

            for i, win in enumerate(broll_windows):
                bp    = win["path"]
                bst   = win["start"]
                bend  = win["end"]
                bdur  = max(0.1, bend - bst)
                ext   = Path(bp).suffix.lower()
                label_br = f"br{i}"
                label_sc = f"brsc{i}"
                label_ov = f"brov{i}"

                if ext in IMAGE_EXTS:
                    # Imagem: adicionar como loop infinito, trim para a duração
                    cmd += ["-loop", "1", "-t", f"{bdur:.3f}", "-i", bp]
                    fc.append(
                        f"[{next_idx}:v]"
                        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                        f"crop={W}:{H},"
                        f"setsar=1,"
                        f"format=yuva420p,"
                        f"colorchannelmixer=aa=0.85"
                        f"[{label_sc}]"
                    )
                elif ext in VIDEO_EXTS:
                    # Vídeo: trim no segmento e resetar pts
                    cmd += ["-i", bp]
                    fc.append(
                        f"[{next_idx}:v]"
                        f"trim=duration={bdur:.3f},"
                        f"setpts=PTS-STARTPTS,"
                        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                        f"crop={W}:{H},"
                        f"setsar=1,"
                        f"format=yuva420p,"
                        f"colorchannelmixer=aa=0.85"
                        f"[{label_sc}]"
                    )
                else:
                    continue  # Formato não suportado: pular

                next_idx += 1

                # Overlay com enable por timestamp — atrasa o B-Roll até o tempo certo
                fc.append(
                    f"[{cur_label}][{label_sc}]"
                    f"overlay=0:0:"
                    f"enable='between(t\\,{bst:.3f}\\,{bend:.3f})':"
                    f"eof_action=pass:"
                    f"format=auto"
                    f"[{label_ov}]"
                )
                cur_label = label_ov

            return fc, cur_label, next_idx

        except Exception as e:
            self.log(f"[E4] Erro interno em _apply_broll_overlays: {e}")
            return None

    def _build_zoom_filter(self, words, W, H, fps=30):
        """
        [E2] Gera filtro FFmpeg `select+zoompan` para aplicar Punch-in
        nos timestamps onde zoom_trigger=True (detectado pelo Diretor IA).

        Retorna (filtro_str, label_saida) ou (None, None) se não houver triggers.
        O filtro recebe [vb] e emite [vzoom].
        """
        if not words:
            return None, None

        # Coletar janelas de zoom: cada trigger abre 1.5s de punch-in
        ZOOM_DUR   = 1.5   # duração do zoom em segundos
        ZOOM_LEVEL = 1.15  # nível de zoom (1.15 = 15% maior)
        zoom_windows = []

        for bloco in words:
            if not bloco.get("zoom_trigger"):
                continue
            t_start = float(bloco.get("start", 0))
            t_end   = t_start + ZOOM_DUR
            # Mesclar janelas sobrepostas (evitar conflitos no filtro)
            if zoom_windows and t_start < zoom_windows[-1][1]:
                zoom_windows[-1] = (zoom_windows[-1][0], max(zoom_windows[-1][1], t_end))
            else:
                zoom_windows.append((t_start, t_end))

        if not zoom_windows:
            return None, None

        self.log(f"[E2] 🔍 {len(zoom_windows)} janelas de Zoom/Punch-in detectadas")

        # Montar expressão `between(t,inicio,fim)` para o filtro `select`
        # Usar zoompan com exprão condicional: se t está na janela, zoom=1.15, senão zoom=1.0
        # Construímos via `if(between(t,s,e),zoom,1)` encadeado
        zoom_expr_parts = []
        for s, e in zoom_windows:
            zoom_expr_parts.append(f"between(t\\,{s:.3f}\\,{e:.3f}")

        # Expressão de zoom: durante as janelas usa ZOOM_LEVEL, fora usa 1.0
        # zoompan aceita: z='if(between(t,s1,e1)+between(t,s2,e2),zoom,1)'
        between_sum = "+".join([f"between(t\\,{s:.3f}\\,{e:.3f})" for s, e in zoom_windows])
        z_expr  = f"if(gt({between_sum}\\,0)\\,{ZOOM_LEVEL:.3f}\\,1)"
        # centralizar: x e y para manter o centro da imagem
        x_expr  = f"iw/2-(iw/zoom/2)"
        y_expr  = f"ih/2-(ih/zoom/2)"

        zoom_filter = (
            f"[vb]zoompan="
            f"z='{z_expr}':"
            f"x='{x_expr}':"
            f"y='{y_expr}':"
            f"d=1:"
            f"s={W}x{H}:"
            f"fps={fps}[vzoom]"
        )

        return zoom_filter, "vzoom"

    def _ffmpeg_build(self, base_mp4, ass_path, output, W,H, dur, clips_audio_path=None):
        import hardware_detector
        _hw_enc = hardware_detector.detect_h264_encoder()
        _vc_high = [*_vc_high] if _hw_enc == 'libx264' else ['-c:v', _hw_enc, '-b:v', '8M', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.2']
        _vc_base = [*_vc_base] if _hw_enc == 'libx264' else ['-c:v', _hw_enc, '-b:v', '6M']

        have_fx1 = bool(self.fx1_en.get() and self.fx1_path and Path(self.fx1_path).exists())
        # Camada #2 desativada no app
        have_fx2 = False
        have_sfx = bool(self.sfx_en.get() and self.sfx_path and Path(self.sfx_path).exists())

        base_in = win_short_path(str(base_mp4))
        # Verificação preventiva: garantir que o arquivo base contenha stream de vídeo
        def _ffprobe_has_video(pth: str):
            try:
                r = subprocess.run([self.ffprobe, "-v", "error", "-select_streams", "v", "-show_entries", "stream=index", "-of", "csv=p=0", pth], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
                out = (r.stdout or "") + (r.stderr or "")
                has = bool((r.stdout or "").strip())
                return has, out
            except Exception as e:
                return False, str(e)

        if not Path(base_in).exists():
            self.log(f"[ffmpeg] arquivo base não encontrado: {base_in}")
            raise RuntimeError(f"Arquivo base ausente: {base_in}")

        has_vid, probe_out = _ffprobe_has_video(base_in)
        if not has_vid:
            # tentativa automática de reconstruir o vídeo base (uma vez)
            self.log('[ffmpeg] Aviso: vídeo base parece não conter stream de vídeo. Tentando reconstruir...')
            try:
                # tenta reconstruir usando timeline salvo, se houver
                mapping_exists = hasattr(self, 'mapping_timeline') and self.mapping_timeline and isinstance(self.mapping_timeline, dict) and self.mapping_timeline.get('images')
                if mapping_exists:
                    try:
                        force = (str(self.transition.get()).lower() == "fade" and float(self.transition_dur.get() or 0.0) > 0.0)
                        self._build_base_using_timeline(self.mapping_timeline['images'], self.video_clips, Path(base_mp4), W, H, dur, self.transition.get(), float(self.transition_dur.get()), force_fade=force)
                    except Exception:
                        self._build_base(self.images, self.video_clips, Path(base_mp4), W, H, dur, self.transition.get(), float(self.transition_dur.get()))
                else:
                    self._build_base(self.images, self.video_clips, Path(base_mp4), W, H, dur, self.transition.get(), float(self.transition_dur.get()))
            except Exception as e:
                self.log(f"[ffmpeg] Reconstrução do vídeo base falhou: {e}")
            # re-checar
            has_vid, probe_out = _ffprobe_has_video(base_in)
            if not has_vid:
                # tentar fallback via ffmpeg (montagem direta das imagens/clips)
                try:
                    ok_ff = False
                    if mapping_exists:
                        ok_ff = self._build_base_ffmpeg(self.mapping_timeline.get('images', []), self.video_clips, Path(base_mp4), W, H, dur, self.transition.get(), float(self.transition_dur.get()))
                    else:
                        # montar via imagens conhecidas
                        media = self.get_media_items()
                        timeline_imgs = [{'file': p, 'start': 0.0, 'end': dur/ max(1, len(media))} for p in media]
                        ok_ff = self._build_base_ffmpeg(timeline_imgs, self.video_clips, Path(base_mp4), W, H, dur, self.transition.get(), float(self.transition_dur.get()))
                    if ok_ff:
                        has_vid, probe_out = _ffprobe_has_video(base_in)
                except Exception as e:
                    self.log(f"[ffmpeg] fallback via ffmpeg falhou: {e}")
            if not has_vid:
                self.log('[ffmpeg] Após tentativa, arquivo ainda sem stream de vídeo. Saindo.')
                self.log(probe_out)
                raise RuntimeError('Arquivo de vídeo base inválido (sem stream de vídeo). Verifique codecs/permissões.')
        audio_in = win_short_path(str(self.audio_path)) if self.audio_path else str(self.audio_path)
        cmd = [self.ffmpeg, "-y", "-threads", "0", "-hwaccel", "auto", "-i", base_in, "-i", audio_in]
        next_idx = 2; fx1_idx=fx2_idx=sfx_idx=clips_audio_idx=None
        
        if clips_audio_path and Path(clips_audio_path).exists():
            cmd += ["-i", str(clips_audio_path)]
            clips_audio_idx = next_idx
            next_idx += 1

        if have_fx1: cmd += ["-stream_loop","-1","-i", self.fx1_path]; fx1_idx=next_idx; next_idx+=1
        if have_sfx: cmd += ["-stream_loop","-1","-i", self.sfx_path]; sfx_idx=next_idx; next_idx+=1

        fc = []; cur="vb"; fc.append(f"[0:v]format=yuv420p[{cur}]")

        # [E2] Punch-in Zoom: aplicar zoompan nos timestamps dos zoom_trigger
        # BUG FIX: usar _last_ia_words (enriquecidos pela IA) em vez de _last_transcript_words
        try:
            _words_for_zoom = getattr(self, '_last_ia_words', None) or getattr(self, '_last_transcript_words', None) or []
            _fps = int(getattr(self, 'fps', 30) or 30)
            zoom_filter, zoom_label = self._build_zoom_filter(_words_for_zoom, W, H, fps=_fps)
            if zoom_filter and zoom_label:
                fc.append(zoom_filter)
                cur = zoom_label  # pipeline continua a partir de [vzoom]
                self.log(f"[E2] ✨ Zoom/Punch-in aplicado no pipeline de vídeo")
        except Exception as _ez:
            self.log(f"[E2] ⚠️ Zoom ignorado (render continua): {_ez}")

        # [E4] B-Roll Contextual: sobrepor imagens/vídeos nos timestamps broll_path
        try:
            _words_for_broll = getattr(self, '_last_ia_words', None) or []
            broll_windows = self._collect_broll_windows(_words_for_broll)
            if broll_windows:
                broll_result = self._apply_broll_overlays(broll_windows, cmd, fc, cur, next_idx, W, H)
                if broll_result:
                    fc, cur, next_idx = broll_result
                    self.log(f"[E4] 🎬 {len(broll_windows)} B-Roll(s) contextual(is) injetado(s) no pipeline")
        except Exception as _eb:
            self.log(f"[E4] ⚠️ B-Roll ignorado (render continua): {_eb}")


        key = float(self.fx_key.get()); blend=float(self.fx_blend.get())
        if have_fx1:
            opa=float(self.fx1_op.get())
            fc.append(f"[{fx1_idx}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},format=rgba,colorkey=0x000000:{key:.3f}:{blend:.3f},colorchannelmixer=aa={opa:.3f}[fx1]")
            fc.append(f"[{cur}][fx1]overlay=0:0:eof_action=pass:shortest=0[ovA]"); cur="ovA"
        # Camada #2 removida

        include_subs = bool(ass_path and ass_path.exists())
        if include_subs:
            subs = escape_subs(Path(win_short_path(str(ass_path))))
            fonts = escape_subs(Path(win_short_path(str(FONTS_DIR))))
            fc.append(f"[{cur}]subtitles=filename='{subs}':fontsdir='{fonts}'[v]")
        else:
            fc.append(f"[{cur}]format=yuv420p[v]")

        # Configuração para o AudioPipeline
        audio_config = {
            "narr_atempo": float(self.narr_atempo.get()),
            "narr_vol": float(getattr(self, 'narr_vol', tk.DoubleVar(value=1.0)).get()),
            "rv_active": getattr(self, 'opt_radio_voice', None) and self.opt_radio_voice.get(),
            "rv_preset": getattr(self, 'radio_voice_preset', tk.StringVar(value="Médio")).get() if hasattr(self, 'radio_voice_preset') else "Médio",
            "sfx_trans_active": getattr(self, 'opt_sfx_transition', None) and self.opt_sfx_transition.get(),
            "sfx_trans_path": getattr(self, 'sfx_transition_path', tk.StringVar(value="")).get() if hasattr(self, 'sfx_transition_path') else "",
            "sfx_trans_vol": float(getattr(self, 'sfx_transition_vol', tk.DoubleVar(value=0.5)).get()) if hasattr(self, 'sfx_transition_vol') else 0.5,
            "clips_audio_idx": clips_audio_idx,
            "have_sfx": have_sfx,
            "sfx_idx": sfx_idx,
            "sfx_vol": float(self.sfx_vol.get()),
            "dur": dur,
            "sfx_duck_mode": getattr(self, 'sfx_duck_mode', tk.StringVar(value="Médio")).get() if hasattr(self, 'sfx_duck_mode') else "Médio",
            "next_idx": next_idx
        }

        try:
            _words_for_broll = getattr(self, '_last_ia_words', None) or []
            _broll_wins = self._collect_broll_windows(_words_for_broll)
        except Exception:
            _broll_wins = []

        # [E11] Chama a pipeline de áudio modularizada
        fc, cmd, out_a = self.audio_pipeline.build_audio_filter_chain(audio_config, fc, cmd, broll_windows=_broll_wins)
        next_idx = audio_config.get("next_idx", next_idx)

        def run_ffmpeg(fc_list, note):
            filter_complex = ";".join(fc_list)
            self.log(note)
            
            # Preset mais rápido para rascunho
            preset = "ultrafast" if getattr(self, '_draft', False) else "veryfast"
            crf = "28" if getattr(self, '_draft', False) else "22"
            
            return subprocess.run(
                cmd + ["-filter_complex", filter_complex, "-map", "[v]", "-map", f"[{out_a}]",
                       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2", "-preset", preset, "-crf", crf, "-c:a", "aac", "-b:a", "192k", "-shortest", str(output)],
                capture_output=True, text=True, encoding='utf-8', errors='replace')
        r = run_ffmpeg(fc, "Finalizando vídeo…")
        if r.returncode != 0 and include_subs:
            # Fallback 1: tentar usar 'ass' em vez de 'subtitles' (às vezes subtitles falha por fontconfig/libass)
            try:
                self.log("[ffmpeg] Falhou com subtitles; tentando usar 'ass' filter como fallback...")
                fc_ass = [x if "subtitles=" not in x else f"[{cur}]ass='{subs}'[v]" for x in fc]
                r2 = run_ffmpeg(fc_ass, "Finalizando vídeo (ass fallback)...")
                if r2.returncode == 0:
                    r = r2
                else:
                    self.log("[ffmpeg] Fallback 'ass' também falhou; tentando sem legendas...")
                    # Fallback 2: remover subtitles do filter_complex
                    fc_no_subs = [x for x in fc if "subtitles=" not in x]
                    # garantir estágio final [v]
                    if not any(x.strip().endswith("[v]") for x in fc_no_subs):
                        fc_no_subs.append(f"[{cur}]format=yuv420p[v]")
                    r = run_ffmpeg(fc_no_subs, "Finalizando vídeo (sem legendas)…")
            except Exception as e:
                self.log(f"[ffmpeg] Erro no fallback de legendas: {e}")
                # tentar sem legendas como último recurso
                fc_no_subs = [x for x in fc if "subtitles=" not in x]
                if not any(x.strip().endswith("[v]") for x in fc_no_subs):
                    fc_no_subs.append(f"[{cur}]format=yuv420p[v]")
                r = run_ffmpeg(fc_no_subs, "Finalizando vídeo (sem legendas)…")
            # Log stderr/stdout quando algo falhar, para diagnóstico (não sobrescrever retorno)
            try:
                if r.returncode != 0:
                    out = (r.stderr or r.stdout or "")
                    for ln in out.splitlines()[:200]:
                        self.log(f"[ffmpeg-out] {ln}")
            except Exception:
                pass
        if r.returncode != 0:
            tail = "\n".join((r.stderr or "").splitlines()[-80:])
            self.log("❌ FFmpeg falhou. Últimas linhas:"); self.log(tail)
            tmp = Path(os.getenv("TEMP") or ".") / f"ffmpeg_log_{os.getpid()}.txt"
            try: tmp.write_text(r.stderr or "", encoding="utf-8", errors="ignore")
            except Exception: pass
            raise RuntimeError("Falha no FFmpeg.")

    # ---------- Marca d'água ----------
    def _apply_watermark(self, input_video: str) -> str:
        out = str((Path(input_video).with_name("wm_"+Path(input_video).name)))
        filters = []; cmd=[self.ffmpeg,"-y","-i",input_video]; cur="v0"; filters.append(f"[0:v]format=rgba[{cur}]"); idx=1
        temp_wm = None
        out_audio_map = None  # Inicializar variável
        
        # DEBUG: Log estado das marcas d'água
        self.log(f"[wm] === ESTADO DAS MARCAS D'ÁGUA ===")
        self.log(f"[wm] Imagem: habilitada={self.wm_img_en.get()}, path={self.wm_img_path.get() if hasattr(self, 'wm_img_path') else 'N/A'}")
        self.log(f"[wm] Efeito: habilitada={getattr(self, 'wm_eff_en', tk.BooleanVar()).get()}, path={getattr(self, 'wm_eff_path', tk.StringVar()).get()}")
        self.log(f"[wm] Texto: habilitada={self.wm_txt_en.get()}, texto='{self.wm_txt.get()[:20] if self.wm_txt.get() else ''}'")
        
        # Obter resolução do vídeo base para calcular tamanhos corretamente
        try:
            probe_cmd = [self.ffprobe, '-v', 'error', '-select_streams', 'v:0', 
                        '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(input_video)]
            p = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5)
            if p.returncode == 0 and p.stdout.strip():
                parts = p.stdout.strip().split(',')
                base_w = int(parts[0])
                base_h = int(parts[1])
                self.log(f"[wm] Vídeo base: {base_w}x{base_h}")
            else:
                base_w, base_h = 1920, 1080  # fallback
        except Exception as e:
            self.log(f"[wm] Erro ao obter resolução: {e}")
            base_w, base_h = 1920, 1080
        
        def pos_expr(position, x,y):
            m={"top-left":f"{x}:{y}","top-right":f"main_w-overlay_w-{x}:{y}","bottom-left":f"{x}:main_h-overlay_h-{y}","bottom-right":f"main_w-overlay_w-{x}:main_h-overlay_h-{y}","center":"(main_w-overlay_w)/2:(main_h-overlay_h)/2"}
            return m.get(position,f"{x}:{y}")
        
        if self.wm_img_en.get() and self.wm_img_path.get():
            wm = self.wm_img_path.get()
            if Path(wm).exists():
                self.log(f"[wm] Aplicando marca d'água de IMAGEM: {wm}")
                remove_opt = self.wm_remove.get()
                tol = int(self.wm_tol.get())
                try:
                    proc = preprocess_wm_image(wm, remove_opt, tol, log_fn=self.log)
                    self.log(f"[wm] Imagem processada: {proc}")
                except Exception as e:
                    self.log(f"[wm] Erro ao processar imagem: {e}")
                    proc = wm
                wm_to_use = proc if proc else wm
                cmd += ["-i", wm_to_use]
                opacity=float(self.wm_img_op.get()); scale=float(self.wm_img_scale.get())
                pos = pos_expr(self.wm_img_pos.get(), int(self.wm_img_x.get()), int(self.wm_img_y.get()))
                # CORRIGIDO: usar tamanho fixo baseado no vídeo base, não no tamanho da imagem
                target_w = int(base_w * scale)
                self.log(f"[wm] Imagem: pos={pos}, scale={scale} ({target_w}px), opacity={opacity}")
                # IMPORTANTE: usar format=rgba ANTES de escalar para preservar transparência do PNG
                # Depois aplicar opacidade com geq (general equation) que preserva o alpha original
                # geq: a'(X,Y) = alpha(X,Y) * opacity - preserva a transparência já processada
                if opacity < 0.99:
                    # Se opacidade < 100%, multiplicar o alpha existente pela opacidade
                    filters.append(f"[{idx}:v]format=rgba,scale={target_w}:-1:flags=lanczos,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*{opacity:.3f}'[wmimg]")
                else:
                    # Opacidade 100% - preservar alpha original intacto
                    filters.append(f"[{idx}:v]format=rgba,scale={target_w}:-1:flags=lanczos[wmimg]")
                filters.append(f"[{cur}][wmimg]overlay={pos}:format=rgb[vimg]")
                cur="vimg"; idx+=1
                self.log(f"[wm] Marca d'água de imagem configurada (input idx={idx-1})")
        
        # efeito animado (vídeo com fundo verde) - RÁPIDO: chromakey inline no FFmpeg (sem pré-render)
        if getattr(self, 'wm_eff_en', tk.BooleanVar()).get() and getattr(self, 'wm_eff_path', tk.StringVar()).get():
            eff = self.wm_eff_path.get()
            if eff and Path(eff).exists():
                try:
                    # parâmetros do efeito
                    start_min = int(self.wm_eff_min.get() or 0)
                    start_sec = float(self.wm_eff_sec.get() or 0.0)
                    start = float(start_min * 60 + start_sec)
                    try:
                        p = subprocess.run([self.ffprobe, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(eff)], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=5)
                        eff_dur = float(p.stdout.strip()) if p.returncode == 0 and p.stdout else 8.0
                    except Exception:
                        eff_dur = 8.0
                    end = start + float(eff_dur)
                    similarity = float(self.wm_eff_similarity.get() or 0.15)
                    blend_val = float(self.wm_eff_blend.get() or 0.1)
                    despill_val = float(getattr(self, 'wm_eff_despill', tk.DoubleVar(value=0.15)).get() or 0.15)
                    scale = float(self.wm_eff_scale.get() or 0.25)
                    pos = pos_expr(self.wm_eff_pos.get(), int(self.wm_eff_x.get()), int(self.wm_eff_y.get()))

                    # Se ativado, o efeito aparece automaticamente em 3 tempos do vídeo base
                    three_times = bool(getattr(self, 'wm_eff_three_times', tk.BooleanVar(value=False)).get())
                    base_dur = None
                    if three_times:
                        try:
                            pvd = subprocess.run(
                                [
                                    self.ffprobe,
                                    '-v', 'error',
                                    '-show_entries', 'format=duration',
                                    '-of', 'default=noprint_wrappers=1:nokey=1',
                                    str(input_video),
                                ],
                                capture_output=True,
                                text=True, encoding='utf-8', errors='replace',
                                timeout=5,
                            )
                            if pvd.returncode == 0 and (pvd.stdout or '').strip():
                                base_dur = float(pvd.stdout.strip())
                        except Exception:
                            base_dur = None

                        if not base_dur or base_dur <= 0:
                            self.log("[wm] Não consegui medir duração do vídeo base; usando início manual do efeito.")
                            three_times = False

                    # Montar lista de inícios (para vídeo e áudio)
                    starts = [start]
                    if three_times and base_dur:
                        raw_starts = [60.0, base_dur / 2.0, max(0.0, base_dur - 60.0)]
                        max_start = max(0.0, base_dur - float(eff_dur))
                        # clamp dentro do vídeo
                        clamped = [min(max(0.0, s), max_start) for s in raw_starts]
                        # deduplicar por proximidade
                        starts = []
                        for s in sorted(clamped):
                            if not starts or abs(s - starts[-1]) > 0.25:
                                starts.append(s)
                        self.log(f"[wm] 3 tempos ativado. Duração base={base_dur:.1f}s, starts={', '.join(f'{x:.1f}s' for x in starts)}")

                    # para log
                    end = (max(starts) if starts else start) + float(eff_dur)
                    
                    # CORRIGIDO: calcular tamanho fixo baseado no vídeo base
                    target_w = int(base_w * scale)
                    
                    # MÉTODO RÁPIDO: chromakey inline no FFmpeg (instantâneo, sem pré-render)
                    self.log(f"[wm] Aplicando efeito animado INLINE (s={similarity:.3f}, b={blend_val:.3f}, despill={despill_val:.3f})")
                    self.log(f"[wm] Efeito: scale={scale} -> {target_w}px (base={base_w}x{base_h})")
                    eff_input_idx = idx
                    cmd += ["-i", eff]
                    
                    # FILTRO COM DESPILL: Remove verde do fundo + neutraliza tom verde das bordas
                    # 1. Escala para tamanho fixo
                    # 2. Chromakey para remover fundo verde
                    # 3. DESPILL: colorbalance reduz tom verde só nas sombras/midtones (onde fica a borda)
                    #    gs = green shadows, gm = green midtones (valores negativos reduzem verde)
                    # Importante: NÃO usar stream_loop + enable, porque isso faz a animação
                    # estar "rodando" em background e, ao reaparecer, não começa do frame 0.
                    # Solução: trim do efeito (0->dur) e deslocar PTS para cada start.
                    eff_base = f"effbase{eff_input_idx}"
                    if despill_val > 0.01:
                        despill = f"colorbalance=gs=-{despill_val:.2f}:gm=-{despill_val * 0.7:.2f}"
                        chroma_filter = (
                            f"[{idx}:v]scale={target_w}:-1:flags=lanczos,format=rgba,"
                            f"chromakey=0x00FF00:{similarity:.3f}:{blend_val:.3f},{despill},"
                            f"trim=0:{eff_dur:.3f},setpts=PTS-STARTPTS[{eff_base}]"
                        )
                    else:
                        chroma_filter = (
                            f"[{idx}:v]scale={target_w}:-1:flags=lanczos,format=rgba,"
                            f"chromakey=0x00FF00:{similarity:.3f}:{blend_val:.3f},"
                            f"trim=0:{eff_dur:.3f},setpts=PTS-STARTPTS[{eff_base}]"
                        )
                    filters.append(chroma_filter)

                    if len(starts) <= 1:
                        eff_t = f"efft{eff_input_idx}_1"
                        s0 = starts[0] if starts else start
                        filters.append(f"[{eff_base}]setpts=PTS+{s0:.3f}/TB[{eff_t}]")
                        # NÃO usar shortest=1 aqui: pode encurtar o vídeo e causar "congelamento" até o fim do áudio.
                        filters.append(f"[{cur}][{eff_t}]overlay={pos}:eof_action=pass:format=auto[veff]")
                        cur = "veff"
                    else:
                        split_outs = "".join([f"[effs{eff_input_idx}_{j}]" for j in range(1, len(starts) + 1)])
                        filters.append(f"[{eff_base}]split={len(starts)}{split_outs}")
                        prev_v = cur
                        for j, s in enumerate(starts, start=1):
                            effs = f"effs{eff_input_idx}_{j}"
                            efft = f"efft{eff_input_idx}_{j}"
                            outv = f"veff{eff_input_idx}_{j}"
                            filters.append(f"[{effs}]setpts=PTS+{s:.3f}/TB[{efft}]")
                            # NÃO usar shortest=1 aqui: pode encurtar o vídeo e causar "congelamento" até o fim do áudio.
                            filters.append(f"[{prev_v}][{efft}]overlay={pos}:eof_action=pass:format=auto[{outv}]")
                            prev_v = outv
                        cur = prev_v
                    
                    # detectar áudio do efeito e mixar se existir
                    try:
                        pchk = subprocess.run([self.ffprobe, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', str(eff)], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3)
                        has_eff_audio = bool((pchk.stdout or '').strip())
                    except Exception:
                        has_eff_audio = False
                    if has_eff_audio:
                        try:
                            vol = float(getattr(self, 'wm_eff_vol', tk.DoubleVar(value=1.0)).get() or 1.0)
                        except Exception:
                            vol = 1.0
                        # Para 1 janela: manter o comportamento atual (delay + 1 segmento)
                        # Para 3 janelas: criar 3 segmentos (mesmo início do efeito) com delays diferentes e mixar
                        if len(starts) <= 1:
                            eff_a_label = f"effa{eff_input_idx}"
                            start_ms = int(starts[0] * 1000)
                            filters.append(
                                f"[{eff_input_idx}:a]atrim=0:{eff_dur:.3f},asetpts=PTS-STARTPTS,volume={vol:.3f},adelay={start_ms}|{start_ms}[{eff_a_label}]"
                            )
                            self.log(f"[wm] Áudio do efeito: delay={start_ms}ms, duração={eff_dur:.1f}s")
                            eff_mix_label = f"[{eff_a_label}]"
                        else:
                            seg_labels = []
                            for j, s in enumerate(starts, start=1):
                                seg = f"effa{eff_input_idx}_t{j}"
                                dms = int(s * 1000)
                                filters.append(
                                    f"[{eff_input_idx}:a]atrim=0:{eff_dur:.3f},asetpts=PTS-STARTPTS,volume={vol:.3f},adelay={dms}|{dms}[{seg}]"
                                )
                                seg_labels.append(f"[{seg}]")
                            effmix = f"effmix{eff_input_idx}"
                            filters.append(f"{''.join(seg_labels)}amix=inputs={len(seg_labels)}:duration=longest:dropout_transition=0[{effmix}]")
                            eff_mix_label = f"[{effmix}]"
                        try:
                            pchk2 = subprocess.run([self.ffprobe, '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0', str(input_video)], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3)
                            has_base_audio = bool((pchk2.stdout or '').strip())
                        except Exception:
                            has_base_audio = False
                        if has_base_audio:
                            # Misturar áudio base + áudio do efeito (1x ou 3x)
                            filters.append(f"[0:a]{eff_mix_label}amix=inputs=2:duration=first:dropout_transition=0[aout]")
                            out_audio_map = "[aout]"
                        else:
                            out_audio_map = eff_mix_label
                    idx += 1
                    if len(starts) <= 1:
                        self.log(f"[wm] Efeito animado configurado: {starts[0]:.1f}s - {end:.1f}s, tamanho={target_w}px")
                    else:
                        self.log(f"[wm] Efeito animado configurado: {len(starts)} ocorrências, tamanho={target_w}px")
                except Exception as e:
                    self.log(f"⚠️ Falha ao adicionar efeito animado: {e}")
        text_png=None
        if self.wm_txt_en.get() and self.wm_txt.get().strip():
            try:
                txt=self.wm_txt.get().strip(); size=int(self.wm_txt_size.get()); color=self.wm_txt_color.get().lstrip("#") or "FFFFFF"
                r=int(color[0:2],16); g=int(color[2:4],16); b=int(color[4:6],16); a=int(max(0,min(1,float(self.wm_txt_op.get())))*255)
                font_path = str(FONTS_DIR / f"{self.wm_txt_font.get()}.ttf")
                try: font = ImageFont.truetype(font_path, size)
                except Exception:
                    font = ImageFont.load_default()
                tmp = Image.new("RGBA",(4,4),(0,0,0,0)); d=ImageDraw.Draw(tmp); bbox=d.textbbox((0,0),txt,font=font)
                tw,th=bbox[2]-bbox[0], bbox[3]-bbox[1]; pad=max(4,size//6); Wt,Ht=tw+pad*2, th+pad*2
                im = Image.new("RGBA",(Wt,Ht),(0,0,0,0)); d=ImageDraw.Draw(im)
                if self.wm_txt_shadow.get():
                    for dx,dy in ((1,1),(2,2)): d.text((pad+dx,pad+dy), txt, font=font, fill=(0,0,0,200))
                if self.wm_txt_bold.get(): d.text((pad+1,pad), txt, font=font, fill=(r,g,b,a))
                d.text((pad,pad), txt, font=font, fill=(r,g,b,a))
                text_png = str(BASE_DIR / f"_wm_text_{os.getpid()}.png"); im.save(text_png)
                cmd += ["-i", text_png]
                pos = pos_expr(self.wm_txt_pos.get(), 12, 12)
                filters.append(f"[{idx}:v]format=rgba[wmtxt]")
                filters.append(f"[{cur}][wmtxt]overlay={pos}:format=auto[vo]")
                cur="vo"; idx+=1
            except Exception as e:
                self.log(f"⚠️ Marca d'água de texto ignorada: {e}")
        if cur=="v0":
            return input_video
        # if we created a mixed audio label (aout), prefer mapping it
        audio_map = "0:a?"
        if out_audio_map:
            audio_map = out_audio_map
        fc=";".join(filters); cmd += ["-filter_complex", fc, "-map", f"[{cur}]", "-map", audio_map, "-c:v","libx264","-preset","veryfast","-crf","22","-c:a","aac","-b:a","192k", out]
        self.log("Aplicando marcas d'água...")
        self.log(f"[DEBUG] Filtros: {fc}")
        self.log(f"[DEBUG] Comando FFmpeg: {' '.join(str(c) for c in cmd[:20])}...")
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if text_png:
            try: os.remove(text_png)
            except Exception: pass
        if temp_wm:
            try: os.remove(temp_wm)
            except Exception: pass
        if r.returncode!=0:
            self.log("⚠️ Erro ao aplicar marcas d'água. Mantendo arquivo original.")
            tail = "\n".join((r.stderr or "").splitlines()[-60:])
            self.log(tail)
            return input_video
        self.log("Marcas d'água aplicadas.")
        return out

    # ---------- utilidade: novo projeto ----------
    def novo_projeto(self):
        self.images=[]; self.video_clips=[]
        self.audio_path=None
        try:
            self.lbl_midias.config(text="Nenhuma mídia")
        except Exception:
            pass
        try:
            self.lbl_audio.config(text="Nenhum áudio")
        except Exception:
            pass
        self.log("Novo projeto iniciado.")
        self._check_ready()

    # ---------- Preview dinâmico da marca d'água (UI) ----------
    def _create_wm_preview_widgets(self, parent):
        # Frame com scroll para conter preview grande
        preview_outer = ctk.CTkFrame(parent)
        preview_outer.pack(fill="both", expand=True, pady=6)
        
        # Canvas com scrollbar para preview grande
        canvas = tk.Canvas(preview_outer)
        scrollbar_v = tk.Scrollbar(preview_outer, orient="vertical", command=canvas.yview)
        scrollbar_h = tk.Scrollbar(preview_outer, orient="horizontal", command=canvas.xview)
        
        preview_frame = ctk.CTkLabelFrame(canvas, text="🎬 Preview (ao vivo) - 16:9 HD - 960x540", padx=6, pady=6)
        
        # tamanho 16:9 HD para visualização precisa - BEM MAIOR
        self._preview_w = 960
        self._preview_h = 540
        # Cache para evitar lag
        self._wm_cache = {}  # cache de imagens processadas
        self._eff_frame_cache = {}  # cache do frame do efeito
        self._preview_update_pending = None  # debounce timer
        
        # Label com tamanho FIXO para garantir que apareça grande
        self.wm_preview_label = ctk.CTkLabel(preview_frame, width=self._preview_w, height=self._preview_h)
        self.wm_preview_label.pack()
        
        btns = ctk.CTkFrame(preview_frame)
        btns.pack(fill="x", pady=(6,0))
        ctk.CTkButton(btns, text="⟳ Atualizar", command=self._update_wm_preview_now).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(btns, text="▶ Próx. imagem", command=self._cycle_preview_image).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(btns, text="🗑 Cache", command=self._clear_preview_cache).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(btns, text="🔲 Janela Grande", command=self._open_preview_window).pack(side="left", padx=4, pady=4)
        self._preview_base_idx = 0
        
        # Configurar scroll
        canvas.create_window((0, 0), window=preview_frame, anchor="nw")
        preview_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"), yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Layout com scrollbars
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        preview_outer.grid_rowconfigure(0, weight=1)
        preview_outer.grid_columnconfigure(0, weight=1)
        
        # Scroll com mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _open_preview_window(self):
        """Abre janela separada com preview GRANDE em tela cheia"""
        try:
            # Fechar janela anterior se existir
            if hasattr(self, '_preview_window') and self._preview_window:
                try:
                    self._preview_window.destroy()
                except Exception:
                    pass
            
            # Criar nova janela
            self._preview_window = tk.Toplevel(self)
            self._preview_window.title("Preview Grande - Marca d'Água (16:9)")
            self._preview_window.configure()
            
            # Tamanho grande - quase tela cheia
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            win_w = min(1400, screen_w - 100)
            win_h = min(900, screen_h - 100)
            x = (screen_w - win_w) // 2
            y = (screen_h - win_h) // 2
            self._preview_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
            
            # Label para preview grande
            self._preview_window_label = ctk.CTkLabel(self._preview_window)
            self._preview_window_label.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Botões
            btn_frame = ctk.CTkFrame(self._preview_window)
            btn_frame.pack(fill="x", pady=6)
            ctk.CTkButton(btn_frame, text="⟳ Atualizar", command=self._update_preview_window, font=("Arial", 12)).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="▶ Próxima imagem", command=lambda: (self._cycle_preview_image(), self._update_preview_window()), font=("Arial", 12)).pack(side="left", padx=10)
            ctk.CTkButton(btn_frame, text="✕ Fechar", command=self._preview_window.destroy, font=("Arial", 12)).pack(side="right", padx=10)
            
            # Atualizar preview na janela
            self._update_preview_window()
            
        except Exception as e:
            self.log(f"[preview] Erro ao abrir janela: {e}")

    def _update_preview_window(self):
        """Atualiza o preview na janela grande"""
        try:
            if not hasattr(self, '_preview_window') or not self._preview_window:
                return
            
            # Gerar imagem do preview em alta resolução
            preview_img = self._generate_preview_image(1280, 720)
            if preview_img:
                self._preview_window_tk = ImageTk.PhotoImage(preview_img)
                self._preview_window_label.config(image=self._preview_window_tk)
        except Exception as e:
            self.log(f"[preview] Erro update window: {e}")

    def _generate_preview_image(self, width, height):
        """Gera imagem do preview com todas as marcas d'água aplicadas"""
        try:
            # construir base
            base = None
            if getattr(self, 'images', None):
                try:
                    p = self.images[self._preview_base_idx % len(self.images)]
                    base = Image.open(p).convert('RGBA')
                except Exception:
                    base = None
            if base is None:
                base = Image.new('RGBA', (width, height), (18,18,18,255))
            else:
                base.thumbnail((width, height), Image.LANCZOS)
                tmp = Image.new('RGBA', (width, height), (18,18,18,255))
                x = (width - base.width)//2; y = (height - base.height)//2
                tmp.paste(base, (x,y)); base = tmp

            # imagem watermark
            try:
                if getattr(self, 'wm_img_en', tk.BooleanVar()).get() and getattr(self, 'wm_img_path', tk.StringVar()).get():
                    wm_path = self.wm_img_path.get()
                    if wm_path and Path(wm_path).exists():
                        wm = Image.open(wm_path).convert('RGBA')
                        scale = float(self.wm_img_scale.get() or 0.25)
                        new_w = int(width * scale)
                        if new_w <= 0: new_w = min(width, wm.width)
                        nw = new_w; nh = int(nw * (wm.height / max(1, wm.width)))
                        wm_resized = wm.resize((nw, nh), Image.LANCZOS)
                        opa = float(self.wm_img_op.get() or 1.0)
                        if opa < 1.0:
                            a = wm_resized.split()[3].point(lambda p: int(p * opa))
                            wm_resized.putalpha(a)
                        pos = self.wm_img_pos.get() if hasattr(self, 'wm_img_pos') else 'bottom-right'
                        if pos == 'top-left': px,py = 12,12
                        elif pos == 'top-right': px,py = width - wm_resized.width - 12, 12
                        elif pos == 'bottom-left': px,py = 12, height - wm_resized.height - 12
                        elif pos == 'bottom-right': px,py = width - wm_resized.width - 12, height - wm_resized.height - 12
                        else: px,py = (width - wm_resized.width)//2, (height - wm_resized.height)//2
                        base.alpha_composite(wm_resized, (px,py))
            except Exception as e:
                self.log(f"[preview gen] wm image erro: {e}")

            # efeito animado - usar cache
            try:
                if getattr(self, 'wm_eff_en', tk.BooleanVar()).get() and getattr(self, 'wm_eff_path', tk.StringVar()).get():
                    eff_path = self.wm_eff_path.get()
                    if eff_path and Path(eff_path).exists():
                        similarity = float(self.wm_eff_similarity.get() or 0.15)
                        blend_val = float(self.wm_eff_blend.get() or 0.1)
                        cache_key = f"{eff_path}_{similarity:.3f}_{blend_val:.3f}"
                        
                        if hasattr(self, '_eff_frame_cache') and cache_key in self._eff_frame_cache:
                            im_eff = self._eff_frame_cache[cache_key].copy()
                        else:
                            im_eff = self._extract_eff_frame_with_alpha_ffmpeg(eff_path)
                            if im_eff and hasattr(self, '_eff_frame_cache'):
                                self._eff_frame_cache[cache_key] = im_eff.copy()
                        
                        if im_eff:
                            scale = float(self.wm_eff_scale.get() or 0.25)
                            new_w = int(width * scale)
                            if new_w <= 0: new_w = min(width, im_eff.width)
                            nw = new_w; nh = int(nw * (im_eff.height / max(1, im_eff.width)))
                            eff_resized = im_eff.resize((nw, nh), Image.LANCZOS)
                            pos = self.wm_eff_pos.get() if hasattr(self, 'wm_eff_pos') else 'bottom-right'
                            ox = int(self.wm_eff_x.get() or 0)
                            oy = int(self.wm_eff_y.get() or 0)
                            if pos == 'top-left': px,py = ox, oy
                            elif pos == 'top-right': px,py = width - eff_resized.width - ox, oy
                            elif pos == 'bottom-left': px,py = ox, height - eff_resized.height - oy
                            elif pos == 'bottom-right': px,py = width - eff_resized.width - ox, height - eff_resized.height - oy
                            else: px,py = (width - eff_resized.width)//2, (height - eff_resized.height)//2
                            base.alpha_composite(eff_resized, (px,py))
            except Exception as e:
                self.log(f"[preview gen] efeito erro: {e}")

            # texto watermark
            try:
                if getattr(self, 'wm_txt_en', tk.BooleanVar()).get() and getattr(self, 'wm_txt', tk.StringVar()).get().strip():
                    txt = self.wm_txt.get().strip()
                    size = int(self.wm_txt_size.get() or 36)
                    col = self.wm_txt_color.get().lstrip('#') if hasattr(self, 'wm_txt_color') else 'FFFFFF'
                    r = int(col[0:2],16); g=int(col[2:4],16); b=int(col[4:6],16)
                    alpha = int(max(0.0, min(1.0, float(self.wm_txt_op.get() or 1.0))) * 255)
                    font_path = FONTS_DIR / f"{self.wm_txt_font.get()}.ttf" if hasattr(self, 'wm_txt_font') else None
                    try:
                        font = ImageFont.truetype(str(font_path), size) if font_path and font_path.exists() else ImageFont.load_default()
                    except Exception:
                        font = ImageFont.load_default()
                    txt_img = Image.new('RGBA', (width, height), (0,0,0,0))
                    d = ImageDraw.Draw(txt_img)
                    try:
                        bbox = d.textbbox((0,0), txt, font=font)
                        tw,th = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    except Exception:
                        try:
                            tw,th = font.getsize(txt)
                        except Exception:
                            tw,th = (len(txt)*6, size+4)
                    pos = self.wm_txt_pos.get() if hasattr(self, 'wm_txt_pos') else 'top-left'
                    if pos == 'top-left': tx,ty = 12,12
                    elif pos == 'top-right': tx,ty = width - tw - 12, 12
                    elif pos == 'bottom-left': tx,ty = 12, height - th - 12
                    elif pos == 'bottom-right': tx,ty = width - tw - 12, height - th - 12
                    else: tx,ty = (width - tw)//2, (height - th)//2
                    if getattr(self, 'wm_txt_shadow', tk.BooleanVar()).get():
                        d.text((tx+2,ty+2), txt, font=font, fill=(0,0,0,int(alpha*0.6)))
                    d.text((tx,ty), txt, font=font, fill=(r,g,b,alpha))
                    base = Image.alpha_composite(base, txt_img)
            except Exception as e:
                self.log(f"[preview gen] wm text erro: {e}")

            return base.convert('RGB')
        except Exception as e:
            self.log(f"[preview gen] erro geral: {e}")
            return None

    def _clear_preview_cache(self):
        """Limpa cache do preview para forçar reprocessamento"""
        self._wm_cache = {}
        self._eff_frame_cache = {}
        self.log("[preview] Cache limpo")
        self._update_wm_preview_now()

    def _update_wm_preview_now(self):
        """Atualiza preview imediatamente (sem debounce)"""
        # Verificar se está no modo headless (sem janela Tkinter)
        if getattr(self, '_headless', False) or not hasattr(self, 'root'):
            return
        try:
            if hasattr(self, '_preview_update_pending') and self._preview_update_pending:
                try:
                    self.root.after_cancel(self._preview_update_pending)
                except Exception:
                    pass
                self._preview_update_pending = None
            self._update_wm_preview()
        except Exception:
            pass

    def _cycle_preview_image(self):
        try:
            if not getattr(self, 'images', None):
                return
            self._preview_base_idx = (self._preview_base_idx + 1) % len(self.images)
            self._update_wm_preview_now()
        except Exception:
            pass

    def _schedule_preview_update(self):
        """Agenda atualização do preview com debounce de 150ms para evitar lag"""
        # Verificar se está no modo headless (sem janela Tkinter)
        if getattr(self, '_headless', False) or not hasattr(self, 'root'):
            return  # Ignorar preview em modo headless
        try:
            if hasattr(self, '_preview_update_pending') and self._preview_update_pending:
                try:
                    self.root.after_cancel(self._preview_update_pending)
                except Exception:
                    pass
            self._preview_update_pending = self.root.after(150, self._update_wm_preview)
        except Exception:
            pass  # Ignorar erros se não tiver janela

    def _extract_eff_frame_with_alpha_ffmpeg(self, video_path):
        try:
            # Extrair primeiro frame como PNG via pipe para preservar alpha
            ffmpeg_exe = getattr(self, 'ffmpeg', 'ffmpeg') or 'ffmpeg'
            cmd = [ffmpeg_exe, '-y', '-i', str(video_path), '-vframes', '1', '-f', 'image2', '-c:v', 'png', 'pipe:1']
            # No Windows, evitar janela de console
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.log(f"[preview] _extract_eff_frame_with_alpha_ffmpeg: running ffmpeg -> {cmd}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, check=False)
            # Log ffmpeg output for debugging
            try:
                if result.returncode != 0:
                    self.log(f"[preview] ffmpeg failed (rc={result.returncode}): { (result.stderr or b'').decode('utf-8', errors='replace')[:400] }")
                else:
                    self.log(f"[preview] ffmpeg OK (stdout {len(result.stdout)} bytes)")
            except Exception:
                pass
            
            import io
            try:
                img = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
                # quick sanity check: log non-opaque pixels
                try:
                    a = np.array(img.getchannel('A'))
                    non_opaque = int(np.sum(a < 255))
                    total = a.size
                    pct = (non_opaque / total) * 100.0
                    self.log(f"[preview] ffmpeg extracted image alpha non-opaque: {non_opaque}/{total} ({pct:.2f}%)")
                except Exception:
                    pass
                # If there is no transparency (all alpha==255) or extraction produced 0 bytes, try chromakey fallback via ffmpeg
                try:
                    a = np.array(img.getchannel('A'))
                    non_opaque = int(np.sum(a < 255))
                    total = a.size
                    if total == 0 or (non_opaque == 0 and result.returncode == 0):
                        # Try chromakey filter with app-configured similarity and blend
                        similarity = float(getattr(self, 'wm_eff_similarity', tk.DoubleVar(value=0.15)).get() or 0.15)
                        blend = float(getattr(self, 'wm_eff_blend', tk.DoubleVar(value=0.1)).get() or 0.1)
                        chroma_candidates = [(similarity, blend), (min(0.45, similarity*2), min(0.5, blend*2)), (0.35, 0.15), (0.5, 0.25)]
                        for (s_try, b_try) in chroma_candidates:
                            chroma_filter = f"format=rgba,chromakey=0x00FF00:{s_try:.3f}:{b_try:.3f},format=rgba"
                            cmd2 = [ffmpeg_exe, '-y', '-i', str(video_path), '-vf', chroma_filter, '-vframes', '1', '-f', 'image2', '-c:v', 'png', 'pipe:1']
                            self.log(f"[preview] ffmpeg fallback chromakey attempt: s={s_try:.3f} b={b_try:.3f}")
                            res2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, check=False)
                            if res2.returncode == 0 and res2.stdout:
                                try:
                                    img2 = Image.open(io.BytesIO(res2.stdout)).convert('RGBA')
                                    a2 = np.array(img2.getchannel('A'))
                                    non_opaque2 = int(np.sum(a2 < 255))
                                    self.log(f"[preview] ffmpeg chromakey (s={s_try:.3f},b={b_try:.3f}) non-opaque: {non_opaque2}/{a2.size}")
                                    if non_opaque2 > 0:
                                        return img2
                                    else:
                                        self.log(f"[preview] ffmpeg chromakey (s={s_try:.3f},b={b_try:.3f}) produced no transparent pixels, trying next candidate")
                                except Exception as e:
                                    self.log(f"[preview] ffmpeg chromakey output decode error: {e}")
                            else:
                                try:
                                    self.log(f"[preview] ffmpeg chromakey (s={s_try:.3f},b={b_try:.3f}) failed: { (res2.stderr or b'').decode('utf-8', errors='replace')[:400] }")
                                except Exception:
                                    pass
                except Exception:
                    pass
                return img
            except Exception as e:
                self.log(f"[preview] erro ao abrir imagem extraida via ffmpeg: {e}")
                return None
        except Exception as e:
            print(f"Erro ffmpeg preview: {e}")
            return None

    def _update_wm_preview(self):
        """Atualiza o preview na aba de marca d'água"""
        # Verificar se está no modo headless (sem janela Tkinter)
        if getattr(self, '_headless', False):
            return
        try:
            if not hasattr(self, 'wm_preview_label'):
                return
            # Garantir valores padrão para dimensões
            pw = getattr(self, '_preview_w', 960)
            ph = getattr(self, '_preview_h', 540)
            disp = self._generate_preview_image(pw, ph)
            if disp:
                self._preview_tk = ImageTk.PhotoImage(disp)
                try:
                    self.wm_preview_label.config(image=self._preview_tk)
                except Exception:
                    pass
        except Exception as e:
            self.log(f"[preview] erro geral: {e}")

    def _register_wm_preview_traces(self):
        try:
            vars_to_trace = []
            for name in ('wm_img_en','wm_img_path','wm_img_scale','wm_img_op','wm_img_pos','wm_txt_en','wm_txt','wm_txt_size','wm_txt_color','wm_txt_op','wm_txt_pos','wm_txt_shadow'):
                # include effect vars when we hit the last wm_txt_shadow entry
                if name == 'wm_txt_shadow':
                    extra = ['wm_eff_en','wm_eff_path','wm_eff_min','wm_eff_sec','wm_eff_scale','wm_eff_pos','wm_eff_x','wm_eff_y','wm_eff_similarity','wm_eff_blend']
                    for e in extra:
                        v2 = getattr(self, e, None)
                        if isinstance(v2, tk.Variable):
                            try:
                                v2.trace_add('write', lambda *a: self._schedule_preview_update())
                            except Exception:
                                pass
                v = getattr(self, name, None)
                if isinstance(v, tk.Variable):
                    try:
                        v.trace_add('write', lambda *a: self._schedule_preview_update())
                    except Exception:
                        pass
        except Exception:
            pass


def launch(parent=None):
    """Abre a UI V2.

    - Se parent for fornecido (Tk/Toplevel), abre em uma nova janela (Toplevel) sem iniciar mainloop.
    - Se parent=None, cria Tk() e roda mainloop (modo standalone).
    """
    if parent is None:
        root = tk.Tk()
        root.title(APP_TITLE)
        app = AbaDarkFacil(root)
        app.pack(fill="both", expand=True)
        root.mainloop()
        return root, app

    win = tk.Toplevel(parent)
    win.title(APP_TITLE)
    app = AbaDarkFacil(win)
    app.pack(fill="both", expand=True)
    try:
        win.lift()
        win.focus_force()
    except Exception:
        pass
    return win, app

# ---------- main ----------
if __name__ == "__main__":
    # Licença: o app SEMPRE abre.
    # A validação é LOCAL e o bloqueio é feito pela UI em "modo limitado"
    # (permitindo apenas importar licença e mostrar HWID).
    # Não usamos SKIP_LICENSE_CHECK e não encerramos o app por falta de licença.
    # Headless run support: if called with --run-job <job.json>, execute render in a subprocess without GUI loop
    # (No executável, podem existir args extras; então procuramos a flag em qualquer posição.)
    job_flag = None
    if "--run-job" in sys.argv:
        job_flag = "--run-job"
    elif "--render-job" in sys.argv:
        job_flag = "--render-job"
    if job_flag is not None:
        try:
            idx = sys.argv.index(job_flag)
            job_path = sys.argv[idx + 1]
        except Exception:
            print(f"Uso: {Path(sys.executable).name} {job_flag} <job.json>")
            sys.exit(2)
        # inicializar app de forma headless (esconde a janela)
        try:
            if os.name == "nt":
                try:
                    import multiprocessing; multiprocessing.freeze_support()
                except Exception:
                    pass
            root = tk.Tk(); root.withdraw()
            app = AbaDarkFacil(root)
            app._headless = True
            # carregar job JSON
            try:
                j = json.loads(Path(job_path).read_text(encoding='utf-8'))
            except Exception as e:
                print(f"Falha ao ler job: {e}"); sys.exit(2)
            # aplicar configurações do job no app
            try:
                app.images = j.get('images', []) or []
                app.video_clips = j.get('video_clips', []) or []
                app.audio_path = j.get('audio_path')
                app.out_name.set(j.get('out_name') or app.out_name.get())
                app.opt_leg.set(bool(j.get('opt_leg', True)))
                # IMPORTANTE: ativar uso do mapping manual se o job tiver mapping salvo
                app.use_manual_map.set(bool(j.get('use_manual_map', False)))
                try: app.words_block.set(int(j.get('words_block', app.words_block.get())))
                except Exception: pass
                app.font_name.set(j.get('font_name', app.font_name.get()))
                try: app.font_size.set(int(j.get('font_size', app.font_size.get())))
                except Exception: pass
                app.theme.set(j.get('theme', app.theme.get()))
                app.pos.set(j.get('pos', app.pos.get()))
                try: app.margin_v.set(int(j.get('margin_v', app.margin_v.get())))
                except Exception: pass
                app.uppercase.set(bool(j.get('uppercase', app.uppercase.get())))
                app.hold.set(bool(j.get('hold', app.hold.get())))
                try: app.hold_gap.set(float(j.get('hold_gap', app.hold_gap.get())))
                except Exception: pass
                app.transition.set(j.get('transition', app.transition.get()))
                try: app.transition_dur.set(float(j.get('transition_dur', app.transition_dur.get())))
                except Exception: pass
                app.orient.set(j.get('orient', app.orient.get()))
                try: app.clip_speed.set(int(j.get('clip_speed', app.clip_speed.get())))
                except Exception: pass
                app.low_mem_mode.set(bool(j.get('low_mem_mode', app.low_mem_mode.get())))
                # FX / SFX
                try: app.fx1_en.set(bool(j.get('fx1_en', False)))
                except Exception: pass
                app.fx1_path = j.get('fx1_path')
                try: app.fx1_op.set(float(j.get('fx1_op', app.fx1_op.get())))
                except Exception: pass
                try: app.fx_key.set(float(j.get('fx_key', app.fx_key.get())))
                except Exception: pass
                try: app.fx_blend.set(float(j.get('fx_blend', app.fx_blend.get())))
                except Exception: pass
                try: app.sfx_en.set(bool(j.get('sfx_en', False)))
                except Exception: pass
                app.sfx_path = j.get('sfx_path')
                try: app.sfx_vol.set(float(j.get('sfx_vol', app.sfx_vol.get())))
                except Exception: pass
                try: app.sfx_gate.set(bool(j.get('sfx_gate', app.sfx_gate.get())))
                except Exception: pass
                try: app.sfx_thr.set(float(j.get('sfx_thr', app.sfx_thr.get())))
                except Exception: pass
                try: app.sfx_att.set(int(j.get('sfx_att', app.sfx_att.get())))
                except Exception: pass
                try: app.sfx_rel.set(int(j.get('sfx_rel', app.sfx_rel.get())))
                except Exception: pass
                try: app.narr_atempo.set(float(j.get('narr_atempo', app.narr_atempo.get())))
                except Exception: pass
                # --- Watermark / effects (carregar configurações salvo por job) ---
                try:
                    try: app.wm_img_en.set(bool(j.get('wm_img_en', False)))
                    except Exception: pass
                    try: app.wm_img_path.set(j.get('wm_img_path') or "")
                    except Exception: pass
                    try: app.wm_remove.set(j.get('wm_remove', app.wm_remove.get()))
                    except Exception: pass
                    try: app.wm_tol.set(int(j.get('wm_tol', app.wm_tol.get())))
                    except Exception: pass
                    try: app.wm_img_op.set(float(j.get('wm_img_op', app.wm_img_op.get())))
                    except Exception: pass
                    try: app.wm_img_scale.set(float(j.get('wm_img_scale', app.wm_img_scale.get())))
                    except Exception: pass
                    try: app.wm_img_pos.set(j.get('wm_img_pos', app.wm_img_pos.get()))
                    except Exception: pass
                    try: app.wm_img_x.set(int(j.get('wm_img_x', app.wm_img_x.get())))
                    except Exception: pass
                    try: app.wm_img_y.set(int(j.get('wm_img_y', app.wm_img_y.get())))
                    except Exception: pass

                    try: app.wm_txt_en.set(bool(j.get('wm_txt_en', False)))
                    except Exception: pass
                    try: app.wm_txt.set(j.get('wm_txt', app.wm_txt.get()))
                    except Exception: pass
                    try: app.wm_txt_font.set(j.get('wm_txt_font', app.wm_txt_font.get()))
                    except Exception: pass
                    try: app.wm_txt_size.set(int(j.get('wm_txt_size', app.wm_txt_size.get())))
                    except Exception: pass
                    try: app.wm_txt_color.set(j.get('wm_txt_color', app.wm_txt_color.get()))
                    except Exception: pass
                    try: app.wm_txt_op.set(float(j.get('wm_txt_op', app.wm_txt_op.get())))
                    except Exception: pass
                    try: app.wm_txt_pos.set(j.get('wm_txt_pos', app.wm_txt_pos.get()))
                    except Exception: pass
                    try: app.wm_txt_bold.set(bool(j.get('wm_txt_bold', app.wm_txt_bold.get())))
                    except Exception: pass
                    try: app.wm_txt_shadow.set(bool(j.get('wm_txt_shadow', app.wm_txt_shadow.get())))
                    except Exception: pass

                    try: app.wm_eff_en.set(bool(j.get('wm_eff_en', False)))
                    except Exception: pass
                    try: app.wm_eff_path.set(j.get('wm_eff_path', app.wm_eff_path.get()))
                    except Exception: pass
                    try: app.wm_eff_min.set(int(j.get('wm_eff_min', app.wm_eff_min.get())))
                    except Exception: pass
                    try: app.wm_eff_sec.set(float(j.get('wm_eff_sec', app.wm_eff_sec.get())))
                    except Exception: pass
                    try: app.wm_eff_three_times.set(bool(j.get('wm_eff_three_times', app.wm_eff_three_times.get())))
                    except Exception: pass
                    try: app.wm_eff_scale.set(float(j.get('wm_eff_scale', app.wm_eff_scale.get())))
                    except Exception: pass
                    try: app.wm_eff_pos.set(j.get('wm_eff_pos', app.wm_eff_pos.get()))
                    except Exception: pass
                    try: app.wm_eff_x.set(int(j.get('wm_eff_x', app.wm_eff_x.get())))
                    except Exception: pass
                    try: app.wm_eff_y.set(int(j.get('wm_eff_y', app.wm_eff_y.get())))
                    except Exception: pass
                    try: app.wm_eff_similarity.set(float(j.get('wm_eff_similarity', app.wm_eff_similarity.get())))
                    except Exception: pass
                    try: app.wm_eff_blend.set(float(j.get('wm_eff_blend', app.wm_eff_blend.get())))
                    except Exception: pass
                    try: app.wm_eff_vol.set(float(j.get('wm_eff_vol', app.wm_eff_vol.get())))
                    except Exception: pass
                    # Vídeo Intro
                    try: app.intro_video_en.set(bool(j.get('intro_video_en', False)))
                    except Exception: pass
                    try: app.intro_video_path.set(j.get('intro_video_path') or "")
                    except Exception: pass
                    try: app.intro_duration = float(j.get('intro_duration', 0.0) or 0.0)
                    except Exception: app.intro_duration = 0.0
                    # Efeitos de movimento
                    try: app.zoom_basic.set(bool(j.get('zoom_basic', True)))
                    except Exception: pass
                    try: app.zoom_adv_en.set(bool(j.get('zoom_adv_en', False)))
                    except Exception: pass
                    try: app.zoom_adv_amp.set(float(j.get('zoom_adv_amp', 0.08)))
                    except Exception: pass
                    try: app.float_en.set(bool(j.get('float_en', False)))
                    except Exception: pass
                    try: app.float_amp.set(int(j.get('float_amp', 10)))
                    except Exception: pass
                    try: app.float_period.set(float(j.get('float_period', 4.0)))
                    except Exception: pass
                    try: app.pan_en.set(bool(j.get('pan_en', False)))
                    except Exception: pass
                    try: app.pan_speed.set(float(j.get('pan_speed', 0.05)))
                    except Exception: pass
                    try: app.tilt_en.set(bool(j.get('tilt_en', False)))
                    except Exception: pass
                    try: app.tilt_speed.set(float(j.get('tilt_speed', 0.05)))
                    except Exception: pass
                    try: app.shake_en.set(bool(j.get('shake_en', False)))
                    except Exception: pass
                    try: app.shake_intensity.set(int(j.get('shake_intensity', 3)))
                    except Exception: pass
                    try: app.kenburns_en.set(bool(j.get('kenburns_en', False)))
                    except Exception: pass
                    try: app.kenburns_intensity.set(float(j.get('kenburns_intensity', 0.15)))
                    except Exception: pass
                except Exception as e:
                    try:
                        app.log(f"[headless] falha aplicar watermark settings: {e}")
                    except Exception:
                        print(f"[headless] falha aplicar watermark settings: {e}")
                # IMPORTANTE: carregar o mapping_timeline salvo para sincronização correta
                try:
                    saved_mapping = j.get('mapping_timeline')
                    if saved_mapping:
                        app.mapping_timeline = saved_mapping
                        num_images = len(saved_mapping.get('images', [])) if isinstance(saved_mapping, dict) else 0
                        app.log(f"[headless] Mapping carregado do job ({num_images} imagens)")
                    else:
                        app.log("[headless] Job sem mapping salvo - será recalculado")
                except Exception as e:
                    app.log(f"[headless] falha ao carregar mapping: {e}")
                # IMPORTANTE: carregar as palavras da transcrição para evitar re-transcrição
                try:
                    saved_words = j.get('transcript_words')
                    if saved_words and len(saved_words) > 0:
                        app._last_transcript_words = saved_words
                        app._job_transcript_words = saved_words  # Flag especial para job
                        app.log(f"[headless] Transcrição carregada do job ({len(saved_words)} palavras) - NÃO será re-transcrito")
                    else:
                        app.log("[headless] Job sem transcrição salva - será transcrito")
                except Exception as e:
                    app.log(f"[headless] falha ao carregar transcrição: {e}")
            except Exception as e:
                app.log(f"[headless] falha aplicar job: {e}")
            # executar
            try:
                app._create_video()
                sys.exit(0)
            except SystemExit:
                raise
            except Exception as e:
                app.log(f"[headless] erro durante render: {e}")
                sys.exit(3)
        except Exception as e:
            print(f"Erro headless: {e}"); sys.exit(4)

    if os.name == "nt":
        try:
            import multiprocessing; multiprocessing.freeze_support()
        except Exception:
            pass
    try:
        launch(parent=None)
    except Exception as e:
        # Captura qualquer exceção de inicialização e garante que seja visível
        import traceback
        tb = traceback.format_exc()
        try:
            print("[ERROR] Falha ao iniciar a aplicação:\n", tb)
        except Exception:
            pass
        try:
            # tenta mostrar um diálogo, se o Tk estiver disponível
            from tkinter import messagebox
            messagebox.showerror("Erro ao iniciar", f"Falha ao iniciar o app:\n{e}")
        except Exception:
            pass
        # salva log de erro no diretório do app para inspeção
        try:
            errpath = BASE_DIR / 'startup_error.log'
            errpath.write_text(tb, encoding='utf-8')
        except Exception:
            pass
        # sair com código de erro
        sys.exit(2)
