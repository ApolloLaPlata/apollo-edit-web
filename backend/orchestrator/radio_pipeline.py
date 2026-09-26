import json
import asyncio
import logging
import os
import random
import datetime
import modal
import base64
import shutil
import requests
from backend.services.audio_video_tools import extrair_ultimo_frame

logger = logging.getLogger("RadioPipeline")

class RadioPipelineManager:
    def __init__(self):
        self.is_running = False
        self.current_task = None
        self.active_accounts = [] 
        self.lightning_accounts = []
        
        self.load_secrets()

    def load_secrets(self):
        try:
            secrets_path = os.path.join(os.path.dirname(__file__), '..', 'cloud_tools', 'fleet_secrets.json')
            with open(secrets_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.active_accounts = [a for a in data.get('modal_accounts', []) if a['status'] == 'active']
                self.lightning_accounts = [a for a in data.get('lightning_accounts', []) if a['status'] == 'active']
        except Exception as e:
            logger.error(f"Erro ao carregar secrets na R�dio: {e}")

    async def start_radio(self, veo_folder: str, out_folder: str):
        if self.is_running:
            return False
            
        self.is_running = True
        self.current_task = asyncio.create_task(self._radio_loop(veo_folder, out_folder))
        logger.info(f"[Radio] F�brica infinita de r�dio iniciada!")
        return True
        
    def stop_radio(self):
        self.is_running = False
        if self.current_task:
            self.current_task.cancel()
        logger.info("[Radio] F�brica interrompida.")

    async def _radio_loop(self, veo_folder: str, out_folder: str):
        import json
        
        if not os.path.exists(out_folder):
            os.makedirs(out_folder, exist_ok=True)
            
        while self.is_running:
            try:
                # 1. Pega VEO base
                veos = [os.path.join(veo_folder, f) for f in os.listdir(veo_folder) if f.endswith('.mp4')]
                if not veos:
                    logger.error("[Radio] Nenhum v�deo VEO encontrado na pasta!")
                    await asyncio.sleep(5)
                    continue
                    
                base_vid = random.choice(veos)
                logger.info(f"[Radio] Sorteado VEO: {os.path.basename(base_vid)}")
                
                # 2. Extrai Frame
                temp_out = os.path.join(out_folder, "temp_veo_frame.jpg")
                extrair_ultimo_frame(base_vid, temp_out)
                
                base64_img = None
                if os.path.exists(temp_out):
                    with open(temp_out, "rb") as image_file:
                        base64_img = base64.b64encode(image_file.read()).decode('utf-8')
                    os.remove(temp_out)
                
                # 3. Florence Vision
                vision_text = None
                if base64_img and self.active_accounts:
                    try:
                        acc = next((a for a in self.active_accounts if a["id"] == "modal_1"), self.active_accounts[0])
                        os.environ["MODAL_TOKEN_ID"] = acc["token_id"]
                        os.environ["MODAL_TOKEN_SECRET"] = acc["token_secret"]
                        
                        vision_cls = modal.Cls.from_name("apollo-vision-engine", "FlorenceVisionEngine")
                        vision_engine = vision_cls()
                        # Remote method call requires wrapping in asyncio.to_thread since Modal API is sync
                        vision_text = await asyncio.to_thread(vision_engine.analyze_image.remote, image_b64=base64_img)
                        logger.info(f"[Radio] Florence-2 leu: '{vision_text}'")
                    except Exception as e:
                        logger.error(f"[Radio] Erro Florence-2: {e}")
                        vision_text = "A surreal abstract painting"
                
                # 4. Lightning AI (Roteiro)
                schedule = ""
                if self.lightning_accounts:
                    light = self.lightning_accounts[0]
                    headers = {"Authorization": f"Bearer {light['api_key']}", "Content-Type": "application/json"}
                    
                    messages = [
                        {"role": "system", "content": "Voc� � um diretor de arte psicod�lica de videoclipes. Gere um schedule para um AI Video Morphing de 1800 frames, mudando a cena e o estilo CADA 200 FRAMES (0, 200, 400, 600, 800, 1000, 1200, 1400, 1600). O objetivo � N�O REPETIR imagens e criar muita varia��o. Responda APENAS com as linhas no formato: FRAME | PROMPT EM INGL�S | LORA_NAME."}
                    ]
                    
                    if vision_text:
                        messages.append({"role": "user", "content": f"O FRAME 0 DEVE SER EXATAMENTE ESTA DESCRI��O: '{vision_text}'. A partir do frame 200, comece a transformar essa cena original em uma viagem surreal �pica, viajando por m�ltiplos cen�rios e estilos. Escreva o schedule."})
                    
                    payload = {"model": "meta-llama/Llama-3.1-70B-Instruct", "messages": messages}
                    
                    r = await asyncio.to_thread(requests.post, "https://api.lightning.ai/v1/chat/completions", headers=headers, json=payload, timeout=30)
                    if r.status_code == 200:
                        schedule = r.json()["choices"][0]["message"]["content"].strip()
                
                if not schedule:
                    schedule = "0 | " + (vision_text or "surreal painting") + " | None\n200 | cyberpunk city | KappaNeuro/cyberpunk-style"
                
                # 5. Copia o original para Output (A)
                stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                veo_out = os.path.join(out_folder, f"{stamp}_A_veo_original.mp4")
                shutil.copy2(base_vid, veo_out)
                
                # 6. Manda pra Modal A100 (Deforum) (B)
                acc2 = next((a for a in self.active_accounts if a["id"] == "modal_2"), self.active_accounts[0])
                os.environ["MODAL_TOKEN_ID"] = acc2["token_id"]
                os.environ["MODAL_TOKEN_SECRET"] = acc2["token_secret"]
                
                logger.info("[Radio] Enviando para Deforum na Nuvem...")
                engine_cls = modal.Cls.from_name("apollo-render-router", "DeforumLCMEngine")
                engine = engine_cls()
                
                res = await asyncio.to_thread(engine.generate_lcm_deforum.remote, prompt_schedule=schedule, total_frames=1800, fps=15, zoom=1.015, angle=0.5, init_image_b64=base64_img)
                
                out_path = os.path.join(out_folder, f"{stamp}_B_deforum_morph.mp4")
                with open(out_path, "wb") as f:
                    f.write(res)
                    
                logger.info(f"[Radio] Loop conclu�do. Gerado: {os.path.basename(out_path)}")
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"[Radio] Erro no loop da f�brica: {e}")
                await asyncio.sleep(10)

    async def mix_radio(self, out_folder: str, music_prompt: str = ""):
        from backend.services.audio_video_tools import liquidificador_mixar
        import asyncio
        import os
        import random
        
        logger.info("[Radio] Iniciando Mixagem Total da Estação...")
        try:
            videos = []
            for f in os.listdir(out_folder):
                if f.endswith(".mp4") and "merged" not in f.lower() and "final" not in f.lower():
                    videos.append(os.path.join(out_folder, f))
            
            if not videos:
                logger.error("[Radio] Nenhum clipe base encontrado para mixar.")
                return False
                
            videos.sort()
            list_txt_path = os.path.join(out_folder, "concat_list.txt")
            with open(list_txt_path, "w", encoding="utf-8") as f:
                for v in videos:
                    f.write(f"file '{os.path.basename(v)}'\n")
                    
            audio_path = None
            if music_prompt:
                logger.info("[Radio] Gerando Música via Modal (StableAudio)...")
                try:
                    audio_engine_cls = modal.Cls.from_name('apollo-render-router', 'StableAudioEngine')
                    audio_engine = audio_engine_cls()
                    res_audio = await asyncio.to_thread(audio_engine.generate_audio.remote, music_prompt, duration_s=47.0, num_inference_steps=50, seed=random.randint(0, 99999))
                    audio_path = os.path.join(out_folder, "background_track.wav")
                    with open(audio_path, "wb") as f:
                        f.write(res_audio)
                except Exception as e:
                    logger.error(f"[Radio] Erro Audio: {e}")
                    
            voice_path = None
            if self.lightning_accounts:
                logger.info("[Radio] Gerando Locutor...")
                try:
                    light = self.lightning_accounts[0]
                    headers = {"Authorization": f"Bearer {light['api_key']}", "Content-Type": "application/json"}
                    
                    sys_prompt = "Você é um Diretor de Rádio e Roteirista de entretenimento. Escreva UMA frase curta para o locutor da rádio 24/7 (Sombrio, noturno). Apenas a fala."
                    payload = {"model": "meta-llama/Llama-3.1-70B-Instruct", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": "Anuncie a música."}]}
                    
                    import requests
                    r = await asyncio.to_thread(requests.post, "https://api.lightning.ai/v1/chat/completions", headers=headers, json=payload, timeout=20)
                    if r.status_code == 200:
                        llm_response = r.json()["choices"][0]["message"]["content"].strip().replace('"', '').replace('*', '')
                        logger.info(f"[Radio] Locutor disse: {llm_response}")
                        
                        import httpx
                        
                        # Sorteia entre Qwen-TTS e Moss-TTS (Conta 10)
                        tts_engine = random.choice(["qwen-tts", "moss-tts"])
                        tts_url = f"https://sitesviniciusmiranda--apollo-api-{tts_engine}.modal.run"
                        
                        logger.info(f"[Radio] Gerando voz na Conta 10 ({tts_engine})...")
                        
                        # Criar udio mudo falso para no quebrar os motores que exigem referncia
                        import wave, io, struct, base64
                        fake_wav = io.BytesIO()
                        with wave.open(fake_wav, 'wb') as wav:
                            wav.setnchannels(1)
                            wav.setsampwidth(2)
                            wav.setframerate(24000)
                            for _ in range(24000):
                                wav.writeframes(struct.pack('h', 0))
                        ref_audio_b64 = base64.b64encode(fake_wav.getvalue()).decode("utf-8")
                        
                        payload_tts = {
                            "text": llm_response,
                            "reference_audio_base64": ref_audio_b64,
                            "ref_audio_base64": ref_audio_b64,
                            "reference_text": "Este é um teste de voz.",
                            "ref_text": "Este é um teste de voz.",
                            "prompt_text": "Você é um locutor de rádio com voz grossa, misterioso, noturno."
                        }
                        
                        r_tts = await asyncio.to_thread(requests.post, tts_url, json=payload_tts, timeout=300)
                        if r_tts.status_code == 200:
                            voice_path = os.path.join(out_folder, "radio_host.wav")
                            with open(voice_path, "wb") as f:
                                f.write(r_tts.content)
                            logger.info(f"[Radio] Voz salva do {tts_engine}!")
                        else:
                            logger.error(f"[Radio] Falha no TTS Conta 10: {r_tts.status_code}")
                            
                except Exception as e:
                    logger.error(f"[Radio] Erro Locutor: {e}")
                    
            final_output = os.path.join(out_folder, "FINAL_RENDER.mp4")
            if os.path.exists(final_output):
                os.remove(final_output)
                
            logger.info("[Radio] Costurando vídeo + música + locutor no Liquidificador central...")
            liquidificador_mixar(list_txt_path, audio_path, voice_path, final_output)
            logger.info(f"[Radio] ✅ Mixagem Completa: {final_output}")
            return True
            
        except Exception as e:
            logger.error(f"[Radio] Erro fatal na Mixagem: {e}")
            return False

radio_manager = RadioPipelineManager()


