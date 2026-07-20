import os
import json
import base64
import requests
import random
import time
from typing import Dict, Any, Optional

class GeminiTTSProvider:
    """Implementa Google GenAI TTS (Modelo 3) com suporte a rotação de chaves e retry"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        
        # Recupera as chaves do Gemini configuradas (pode ser uma string separada por vírgulas ou list)
        gemini_keys_raw = self.config.get_api_config("gemini", "api_keys")
        if not gemini_keys_raw:
            # Fallback para api_key simples antigo
            old_key = self.config.get_api_config("gemini", "api_key")
            self.api_keys = [old_key] if old_key else []
        elif isinstance(gemini_keys_raw, str):
            self.api_keys = [k.strip() for k in gemini_keys_raw.split(',') if k.strip()]
        else:
            # Lista de dicts (novo formato do aba_configuracoes) ou strings
            parsed_keys = []
            for item in gemini_keys_raw:
                if isinstance(item, dict) and "key" in item:
                    if item["key"].strip():
                        parsed_keys.append(item["key"].strip())
                elif isinstance(item, str) and item.strip():
                    parsed_keys.append(item.strip())
            self.api_keys = parsed_keys
            
        self.current_key_idx = 0
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent"
        
        if not self.api_keys:
            print("⚠️ Nenhuma API Key do Gemini configurada.")
            
    def _get_current_key(self):
        if not self.api_keys:
            return None
        return self.api_keys[self.current_key_idx]

    def _rotate_key(self):
        """Alterna para a próxima chave de API caso a atual dê erro (Ex: limite atingido)"""
        if self.api_keys and len(self.api_keys) > 1:
            self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)
            print(f"🔄 Rotação de API Key do Gemini realizada. Usando a chave {self.current_key_idx + 1}/{len(self.api_keys)}.")
            return True
        return False

    def generate_tts(self, text: str, voice_id: str, output_path: str,
                     instruction_prompt: str = "", temperature: float = 1.0,
                     max_retries=3, gerar_srt: bool = False, **kwargs) -> bool:
        """Gera o áudio usando a API do Gemini copiando a aproximação de 'gemini-tts-studio'.
        
        Se gerar_srt=True, roda Whisper após a geração e salva um .srt
        word-level na mesma pasta do áudio gerado.
        """
        if not self.api_keys:
            print("❌ Nenhuma API Key configurada para o Gemini TTS.")
            return False

        # Monta o prompt real injetando as orientações baseadas no gemini-tts-studio
        actual_text = text
        if instruction_prompt and instruction_prompt.strip() != "":
            clean_instruction = instruction_prompt.strip()
            # Se já começar com "say" em inglês ou "fale" em português
            if clean_instruction.lower().startswith("say ") or clean_instruction.lower().startswith("fale "):
                actual_text = f"{clean_instruction} {text}"
            else:
                actual_text = f"Say {clean_instruction}: {text}"

        payload = {
            "contents": [{
                "parts": [{"text": actual_text}]
            }],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "temperature": temperature,
                "speechConfig": {
                    "voiceConfig": {
                        "prebuiltVoiceConfig": {
                            "voiceName": voice_id
                        }
                    }
                }
            }
        }

        # Loop de Tentativas / Rotação de Chaves
        # Garantir retries suficientes para tentar todas as chaves
        total_attempts = max(max_retries, len(self.api_keys) + 1) if self.api_keys else max_retries
        for attempt in range(total_attempts):
            api_key = self._get_current_key()
            if not api_key:
                return False

            url = f"{self.base_url}?key={api_key}"
            headers = {"Content-Type": "application/json"}

            print(f"🤖 Gerando áudio via Gemini TTS (Tentativa {attempt+1}/{total_attempts}) com voz '{voice_id}'...")
            
            try:
                # Aumentado o timeout para 120s devido a eventuais engasgos da API Gemini 
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                
                # Sucesso!
                if response.status_code == 200:
                    data = response.json()
                    
                    try:
                        # Extrair base64 e MimeType
                        inline_data = data["candidates"][0]["content"]["parts"][0]["inlineData"]
                        base64_audio = inline_data["data"]
                        mime_type = inline_data.get("mimeType", "").lower()
                        
                        # Decodificar os bytes puros
                        audio_bytes = base64.b64decode(base64_audio)
                        
                        # Salva o arquivo temporário inicial (os bytes brutos que a API Google devolveu)
                        # A API do Google muitas vezes retorna MP3, OGG ou PCM bruto independentemente do que pedimos
                        temp_raw_path = output_path + ".temp_google.raw"
                        with open(temp_raw_path, "wb") as f:
                            f.write(audio_bytes)
                            
                        try:
                            import subprocess
                            cmd = ['ffmpeg', '-y']
                            
                            if "pcm" in mime_type:
                                cmd.extend(['-f', 's16le', '-ar', '24000', '-ac', '1'])
                                
                            cmd.extend(['-i', temp_raw_path])
                            
                            if output_path.lower().endswith(".mp3"):
                                cmd.extend(['-c:a', 'libmp3lame', '-b:a', '192k'])
                            else:
                                # Força a conversão explícita para PCM WAV para Applio ler sem problemas
                                cmd.extend(['-c:a', 'pcm_s16le', '-ar', '44100'])
                                
                            cmd.append(output_path)
                            
                            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                            
                            if result.returncode != 0 or not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                                erro_msg = result.stderr.decode('utf-8', errors='replace')[-200:] if result.stderr else "Erro desconhecido"
                                print(f"⚠️ Aviso: FFmpeg falhou na conversão (Codigo {result.returncode}). Detalhe: {erro_msg}")
                                
                                import shutil
                                shutil.copy(temp_raw_path, output_path)
                        except Exception as e:
                            print(f"⚠️ Aviso: Comando de conversão FFmpeg não executou. Erro: {e}")
                            import shutil
                            shutil.copy(temp_raw_path, output_path)
                        finally:
                            if os.path.exists(temp_raw_path):
                                try:
                                    os.remove(temp_raw_path)
                                except:
                                    pass
                        
                        print(f"✅ Áudio Gemini TTS gerado com sucesso em: {output_path}")
                        # ── SRT opcional via Whisper ─────────────────────────
                        if gerar_srt:
                            self._gerar_srt_whisper(output_path, text)
                        return True
                        
                    except (KeyError, IndexError) as e:
                        print(f"❌ Erro ao extrair áudio da resposta do Gemini: {e}")
                        print(json.dumps(data, indent=2))
                        return False
                        
                # Erro 429 = Quota Exceeded ou Rate Limit
                # Erro 400 = Chave inválida ou Parâmetros errados
                elif response.status_code in [429, 400, 403]:
                    if response.status_code == 429:
                        print("⚠️ Erro 429: Limite de cota atingido.")
                    else:
                        print(f"⚠️ Erro {response.status_code}: Chave de API recusa ou inválida.")
                        
                    if self._rotate_key():
                        print("🔄 Rotacionando a chave e tentando novamente de imediato...")
                        continue
                    else:
                        print("⏳ Sem mais chaves, esperando 10s antes do próximo retry...")
                        time.sleep(10)
                        
                else:
                    print(f"❌ Falha no Gemini TTS: {response.status_code} - {response.text}")
                    time.sleep(2)

            except Exception as e:
                print(f"❌ Erro de conexão no Gemini TTS: {str(e)}")
                time.sleep(2)

        print("❌ Todas as tentativas ou chaves se esgotaram e não foi possível gerar o áudio.")
        return False

    # ── SRT HELPER ───────────────────────────────────────────────────────────
    def _gerar_srt_whisper(self, audio_path: str, texto_original: str = "") -> bool:
        """
        Roda Whisper (modelo 'base') no áudio gerado e salva um .srt
        word-level na mesma pasta do áudio.
        Retorna True se gerou com sucesso.
        """
        try:
            import whisper, os

            srt_path = os.path.splitext(audio_path)[0] + ".srt"
            print(f"📝 [Gemini TTS] Gerando SRT via Whisper: {os.path.basename(srt_path)}")

            model  = whisper.load_model("base")
            result = model.transcribe(
                audio_path,
                fp16=False,
                language="pt",
                word_timestamps=True
            )

            # Garante words em todos os segmentos
            for seg in result.get("segments", []):
                if not seg.get("words"):
                    seg["words"] = [{"word": seg["text"].strip(),
                                     "start": seg["start"], "end": seg["end"]}]

            with open(srt_path, "w", encoding="utf-8") as f:
                idx = 1
                for seg in result.get("segments", []):
                    for w in seg.get("words", []):
                        word = w["word"].strip()
                        if not word:
                            continue
                        f.write(f"{idx}\n")
                        f.write(f"{_fmt_srt_ts(w['start'])} --> {_fmt_srt_ts(w['end'])}\n")
                        f.write(f"{word}\n\n")
                        idx += 1

            print(f"✅ [Gemini TTS] SRT gerado: {os.path.basename(srt_path)}")
            return True

        except ImportError:
            print("⚠️ [Gemini TTS] Whisper não instalado. Rode: pip install openai-whisper")
        except Exception as ex:
            print(f"❌ [Gemini TTS] Erro ao gerar SRT: {ex}")
        return False


# ── Utilitário de timestamp SRT ───────────────────────────────────────────────
def _fmt_srt_ts(seconds: float) -> str:
    """Converte segundos float → formato SRT HH:MM:SS,mmm"""
    ms = int((seconds % 1) * 1000)
    s  = int(seconds)
    h  = s // 3600; s %= 3600
    m  = s // 60;   s %= 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
