import os
import torch
import warnings
from typing import List, Dict, Any
from pyannote.audio import Pipeline
from pydub import AudioSegment

class DiarizationEngine:
    def __init__(self, logger=None):
        self._log = logger or print
        
        # Ignora avisos excessivos do Torch e Pyannote
        warnings.filterwarnings("ignore")

    def extract_samples(self, vocals_path: str, segments: List[Dict], output_dir: str):
        """Extrai até 4 segundos de uma das falas de cada locutor para Preview no UI"""
        from pydub import AudioSegment
        audio = AudioSegment.from_file(vocals_path)
        os.makedirs(output_dir, exist_ok=True)
        unique_spks = {}
        
        # Pega a melhor fala para preview (mais longa se possivel)
        for seg in segments:
            spk = seg["speaker_id"]
            if spk not in unique_spks:
                unique_spks[spk] = seg
            else:
                dur = seg["end"] - seg["start"]
                if dur > (unique_spks[spk]["end"] - unique_spks[spk]["start"]) and dur < 8.0:
                    unique_spks[spk] = seg
                    
        sample_paths = {}
        for spk, seg in unique_spks.items():
            start_ms = max(0, int(seg["start"] * 1000))
            end_ms = int(seg["end"] * 1000)
            if end_ms - start_ms > 4000:
                end_ms = start_ms + 4000
                
            sample = audio[start_ms:end_ms]
            # Normaliza e salva
            if sample.max_dBFS < -5.0:
                sample = sample.apply_gain(min(15, -5.0 - sample.max_dBFS))
                
            clean_spk = spk.replace(" ", "_")
            out_file = os.path.join(output_dir, f"sample_{clean_spk}.wav")
            sample.export(out_file, format="wav")
            sample_paths[spk] = out_file
            
        return sample_paths

    def diarize_vocals(self, vocals_path: str, hf_token: str, min_speakers: int = 1, max_speakers: int = 4) -> List[Dict[str, Any]]:
        self._log("🕵️ Iniciando Detecção de Múltiplos Falantes (Pyannote)...")
        if not hf_token:
            raise ValueError("Token HuggingFace não configurado! Insira-o na aba de Configurações.")
            
        try:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=hf_token
            )
        except Exception as e:
            if "401" in str(e) or "403" in str(e):
                raise PermissionError("Erro de Permissão no HuggingFace. Verifique se o Token está correto e se os termos foram aceitos (pyannote/speaker-diarization-3.1).")
            raise e
            
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._log(f"Carregando IA de biometria de voz em: {device.type.upper()}")
        pipeline.to(device)
        
        # Bypass pyannote's torchcodec by pre-loading audio into memory using soundfile
        import soundfile as sf
        import numpy as np
        data, sample_rate = sf.read(vocals_path, dtype='float32')
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        waveform = torch.from_numpy(data).T
        audio_in_memory = {"waveform": waveform, "sample_rate": sample_rate}
        
        # O processamento pode demorar dependendo do tamanho do audio
        output = pipeline(audio_in_memory, min_speakers=min_speakers, max_speakers=max_speakers)
        
        if hasattr(output, "speaker_diarization"):
            annotation = output.speaker_diarization
        else:
            annotation = output
            
        segments = []
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            segments.append({
                "speaker_id": str(speaker),
                "start": float(turn.start),
                "end": float(turn.end)
            })
            
        # Agrupa falas muito curtas ou pausas pequenas da mesma pessoa 
        grouped_segments = self._group_segments(segments)
        
        qtde_falantes = len(set(s['speaker_id'] for s in grouped_segments))
        self._log(f"✅ Análise concluída! Foram detectados {qtde_falantes} falantes únicos ao longo do vídeo.")
        return grouped_segments

    def _group_segments(self, segments, gap_threshold=0.8):
        """Agrupa segmentos consecutivos do mesmo falante que estão próximos"""
        if not segments: return []
        segments.sort(key=lambda x: x["start"])
        grouped = []
        current = segments[0].copy()
        
        for next_seg in segments[1:]:
            if next_seg["speaker_id"] == current["speaker_id"]:
                # Se a pausa entre as falas do mesmo cara for menor que o limite, junta tudo
                if next_seg["start"] - current["end"] <= gap_threshold:
                    current["end"] = next_seg["end"]
                else:
                    grouped.append(current)
                    current = next_seg.copy()
            else:
                grouped.append(current)
                current = next_seg.copy()
        grouped.append(current)
        return grouped

    def slice_vocals(self, vocals_path: str, segments: List[Dict], output_dir: str):
        self._log("✂️ Fatiando áudio vocal limpo baseando-se nas assinaturas dos falantes...")
        audio = AudioSegment.from_file(vocals_path)
        os.makedirs(output_dir, exist_ok=True)
        
        fo_list = []
        for idx, seg in enumerate(segments):
            start_ms = max(0, int(seg["start"] * 1000) - 100) # Coloca uma gordurinha de 100ms antes
            end_ms = int(seg["end"] * 1000) + 100             # Gordurinha de 100ms no fim
            
            segment_audio = audio[start_ms:end_ms]
            spk = seg["speaker_id"].replace(" ", "_")
            out_file = os.path.join(output_dir, f"fatia_{idx:03d}_{spk}.wav")
            
            # Exporta fatias individuais
            segment_audio.export(out_file, format="wav")
            seg["file_path"] = out_file
            
        self._log(f"Foram criadas {len(segments)} micro-fatias de áudio isoladas para envio ao RVC.")
        return segments

    def stitch_vocals(self, original_vocals_path: str, processed_segments: List[Dict], output_path: str):
        self._log("🪡 Costurando fatias RVC de volta à linha do tempo principal...")
        original_audio = AudioSegment.from_file(original_vocals_path)
        
        # Cria uma tela de pintura silenciosa no tamanho exato do audio original
        canvas = AudioSegment.silent(duration=len(original_audio), frame_rate=original_audio.frame_rate)
        
        for seg in processed_segments:
            if "rvc_file_path" in seg and os.path.exists(seg["rvc_file_path"]):
                rvc_audio = AudioSegment.from_file(seg["rvc_file_path"])
                
                # FADE de 30ms arredonda as bordas secas do RVC que causam o ruido "tremulo" ou "cliques"
                if len(rvc_audio) > 60:
                    rvc_audio = rvc_audio.fade_in(30).fade_out(30)
                    
                start_ms = max(0, int(seg["start"] * 1000) - 100)
                
                # Cola o trecho renderizado de volta no segundo exato
                canvas = canvas.overlay(rvc_audio, position=start_ms)
                
        canvas.export(output_path, format="wav")
        self._log(f"Fatiamento reconstituído com sucesso!")
        return output_path
