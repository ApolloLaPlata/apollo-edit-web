import requests
import json
from typing import Optional, Dict, Any, List
from config_manager import ConfigManager

class GeminiAPI:
    """Cliente para API do Google Gemini"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.base_url = self.config.get("api_config.gemini.base_url", "https://generativelanguage.googleapis.com/v1beta")
        self.api_key = self.config.get("api_config.gemini.api_key")
        self.api_keys_list = self.config.get("api_config.gemini.api_keys", [])
        
        # Fallback: Se não houver chaves no workspace atual, busca no admin_config.json (Chaves Globais)
        if not self.api_keys_list:
            import os
            admin_cfg_path = os.path.join(os.path.dirname(__file__), "admin_config.json")
            if os.path.exists(admin_cfg_path):
                try:
                    with open(admin_cfg_path, 'r', encoding='utf-8') as f:
                        admin_cfg = json.load(f)
                        self.api_keys_list = admin_cfg.get("api_config", {}).get("gemini", {}).get("api_keys", [])
                except:
                    pass
                    
        self.current_key_idx = 0
        if not self.api_key and self.api_keys_list:
            self.api_key = self.api_keys_list[self.current_key_idx].get("key")
        self.model = self.config.get("api_config.gemini.model", "gemini-2.5-flash")
        
        if not self.api_key:
            print("⚠️  API Key do Gemini não configurada globalmente nem no canal.")

    def rotate_key(self) -> bool:
        """Rotaciona para a próxima chave de API disponível"""
        if not self.api_keys_list or len(self.api_keys_list) <= 1:
            return False
            
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys_list)
        self.api_key = self.api_keys_list[self.current_key_idx].get("key")
        name = self.api_keys_list[self.current_key_idx].get("name", "Unknown")
        print(f"🔄 Rotacionando para nova chave Gemini: {name}")
        return True
    
    def generate_content(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """
        Gera conteúdo usando a API do Gemini
        
        Args:
            prompt: Texto principal para gerar conteúdo
            system_prompt: Instruções do sistema (opcional)
            
        Returns:
            str: Conteúdo gerado ou None se erro
        """
        if not self.api_key:
            print("❌ API Key do Gemini não configurada")
            return None
        
        try:
            url = f"{self.base_url}/models/{self.model}:generateContent"
            
            max_retries = len(self.api_keys_list) if self.api_keys_list else 1
            for attempt in range(max_retries):
                headers = {
                    "Content-Type": "application/json",
                    "X-goog-api-key": self.api_key
                }
                
                # Constrói o prompt completo
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": full_prompt
                                }
                            ]
                        }
                    ]
                }
                
                print(f"🤖 Gerando conteúdo com Gemini (Tentativa {attempt + 1})...")
                print(f"📝 Prompt: {prompt[:100]}...")
                
                import os
                debug_log_path = os.path.join(os.path.dirname(__file__), "gemini_debug.txt")
                with open(debug_log_path, "a", encoding="utf-8") as df:
                    df.write(f"\\n--- TENTATIVA {attempt + 1} com chave {self.api_key[:10]}... ---\\n")
                    df.write(f"URL: {url}\\n")
                    
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                with open(debug_log_path, "a", encoding="utf-8") as df:
                    df.write(f"Status Code: {response.status_code}\\n")
                    df.write(f"Response: {response.text[:500]}\\n")
                
                if response.status_code == 200:
                    result = response.json()
                
                    # Extrai o texto gerado da resposta
                    if 'candidates' in result and len(result['candidates']) > 0:
                        content = result['candidates'][0]['content']
                        
                        # Extrair uso de tokens
                        tokens_usados = 0
                        if 'usageMetadata' in result:
                            tokens_usados = result['usageMetadata'].get('totalTokenCount', 0)
                            
                        # Gravar no DB
                        try:
                            from database_manager import db
                            canal_id = self.config.get("canal_id", 1) 
                            custo_estimado = tokens_usados * 0.00000015 # Custo aproximado do Flash
                            db.gravar_uso_api(canal_id, f"gemini_{self.model}", tokens_usados, custo_estimado)
                        except Exception as e:
                            print(f"Erro ao gravar estatística de API: {e}")

                        if 'parts' in content and len(content['parts']) > 0:
                            generated_text = content['parts'][0]['text']
                            print(f"✅ Conteúdo gerado com sucesso! ({tokens_usados} tokens)")
                            return generated_text
                    
                    print(f"⚠️  Resposta inesperada da API: {result}")
                    return None
                elif response.status_code == 429:
                    print(f"⚠️ Limite de cota atingido na chave atual (429).")
                    if self.rotate_key():
                        continue
                    else:
                        return None
                elif response.status_code in [403, 500, 503]:
                    print(f"⚠️ Erro {response.status_code} na chave atual. Tentando próxima chave...")
                    if self.rotate_key():
                        continue
                    else:
                        return None
                else:
                    print(f"❌ Erro na API Gemini: {response.status_code} - {response.text}")
                    with open(debug_log_path, "a", encoding="utf-8") as df:
                        df.write(f"ABORTANDO devido a erro: {response.status_code}\\n")
                    return None
                
            return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            with open(debug_log_path, "a", encoding="utf-8") as df:
                df.write(f"Erro de conexao: {e}\\n")
            return None
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            with open(debug_log_path, "a", encoding="utf-8") as df:
                df.write(f"Erro inesperado: {e}\\n")
            return None

    def analyze_multimodal(self, file_path: str, prompt: str, system_prompt: str = None) -> Optional[str]:
        """
        Usa o SDK nativo do Google (google-generativeai) para enviar arquivos grandes (Áudio/Vídeo) 
        para análise multimodal do Gemini 1.5 Pro.
        """
        if not self.api_key:
            print("❌ API Key do Gemini não configurada")
            return None
            
        try:
            import google.generativeai as genai
            import time
            
            genai.configure(api_key=self.api_key)
            
            print(f"⬆️ Fazendo upload do arquivo para o Gemini: {file_path}")
            uploaded_file = genai.upload_file(file_path)
            
            # Aguardar o arquivo ficar ativo se for vídeo grande (pode levar alguns segundos)
            max_wait = 120  # timeout de 120 segundos para evitar loop infinito
            waited = 0
            while uploaded_file.state.name == "PROCESSING" and waited < max_wait:
                print("⏳ Processando mídia no servidor do Gemini...")
                time.sleep(2)
                waited += 2
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "PROCESSING":
                print("⏱️ Timeout: arquivo ainda em PROCESSING após 120s. Abortando.")
                return None
                
            if uploaded_file.state.name == "FAILED":
                print("❌ Falha ao processar o arquivo no Gemini.")
                return None
                
            print(f"✅ Arquivo pronto! Analisando conteúdo...")
            
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_prompt
            )
            
            response = model.generate_content([uploaded_file, prompt])
            
            # Limpar o arquivo da cota do usuário
            try:
                genai.delete_file(uploaded_file.name)
            except:
                pass
                
            return response.text
            
        except ImportError:
            print("❌ A biblioteca 'google-generativeai' não está instalada. Use: pip install google-generativeai")
            return None
        except Exception as e:
            print(f"❌ Erro na análise multimodal: {e}")
            return None
    
    def generate_news_script(self, topic: str, style: str = "jornalístico", duration: str = "2 minutos") -> Optional[str]:
        """
        Gera roteiro de notícia usando IA
        
        Args:
            topic: Tópico da notícia
            style: Estilo do roteiro (jornalístico, informal, etc.)
            duration: Duração desejada
            
        Returns:
            str: Roteiro gerado
        """
        system_prompt = f"""Você é um roteirista especializado em notícias para YouTube. 
        Crie roteiros {style} com duração de {duration}.
        Use linguagem clara, objetiva e envolvente.
        Inclua introdução, desenvolvimento e conclusão.
        Evite jargões técnicos complexos."""
        
        prompt = f"""Crie um roteiro de notícia sobre: {topic}
        
        O roteiro deve ser:
        - {style} no tom
        - Com duração de {duration}
        - Estruturado para narração
        - Com linguagem natural para TTS"""
        
        return self.generate_content(prompt, system_prompt)
    
    def generate_thumbnail_text(self, news_title: str, style: str = "impactante") -> Optional[str]:
        """
        Gera texto para thumbnail baseado no título da notícia
        
        Args:
            news_title: Título da notícia
            style: Estilo desejado (impactante, informativo, etc.)
            
        Returns:
            str: Texto para thumbnail
        """
        system_prompt = f"""Você é um especialista em marketing digital para YouTube.
        Crie textos curtos e {style} para thumbnails que aumentem o CTR.
        Use no máximo 5-8 palavras.
        Seja direto e impactante."""
        
        prompt = f"""Crie um texto para thumbnail sobre: "{news_title}"
        
        O texto deve ser:
        - {style} e chamativo
        - Máximo 8 palavras
        - Otimizado para CTR
        - Relacionado ao título da notícia"""
        
        return self.generate_content(prompt, system_prompt)
    
    def generate_music_metadata(self, prompt_text: str, song_name: str = "", channel_context: str = "", example_metadata: str = "") -> Optional[str]:
        """
        Gera metadados (Título, Descrição, Tags) para uma música com base no prompt/letra.
        Retorna em formato JSON.
        """
        system_prompt = f"""You are a YouTube SEO expert and Prompts Engineer for music channels.
        CRITICAL RULES:
        1. All outputs MUST be in ENGLISH.
        2. DO NOT translate or change the original song name if provided. Use it exactly as is: "{song_name}"
        3. Read the channel context: {channel_context}
        4. Follow this structure example for metadata formatting:
        {example_metadata}
        
        Create a detailed "image_prompt" in ENGLISH for a 1:1 square album cover art that matches the song's vibe.
        Create an array "broll_prompts" containing 3 to 5 objects in ENGLISH. Each object must have:
        - "description": Detailed description of a short B-Roll scene that matches the song.
        - "efeito_camera": Suggest the best camera movement. Choose ONE from: "zoom_in", "zoom_out", "pan_left", "pan_right", "shake", "kenburns_slow", or "none".
        
        If there are lyrics in the prompt, extract the main parts into "lyrics" formatted with line breaks.
        Return ONLY a valid JSON in the following format:
        {{
            "title": "Catchy YouTube Title (Max 60 chars)",
            "description": "Engaging description about the song, including any links provided in the context.",
            "tags": ["tag1", "tag2", "tag3"],
            "image_prompt": "highly detailed masterpiece, 8k resolution, cinematic lighting...",
            "broll_prompts": [
                {{"description": "scene 1 description...", "efeito_camera": "zoom_in"}},
                {{"description": "scene 2 description...", "efeito_camera": "pan_left"}}
            ],
            "lyrics": "Line 1 of lyrics\\nLine 2 of lyrics\\n..."
        }}"""
        
        prompt = f"""Generate musical metadata for the following song based on this prompt/lyrics:
        {prompt_text}"""
        
        return self.generate_content(prompt, system_prompt)

    def generate_image(self, prompt: str, output_path: str = None, aspect_ratio: str = "16:9") -> Optional[bytes]:
        """
        Gera imagem usando a API do Gemini (Imagen 3)
        """
        if not self.api_key:
            print("❌ API Key do Gemini não configurada")
            return None
        
        try:
            url = f"{self.base_url}/models/imagen-3.0-generate-002:predict"
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": self.api_key
            }
            payload = {
                "instances": [{"prompt": prompt}],
                "parameters": {"sampleCount": 1, "aspectRatio": aspect_ratio}
            }
            
            print(f"🎨 Chamando Imagen 3 para B-Roll: {prompt[:50]}...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'predictions' in result and len(result['predictions']) > 0:
                    import base64
                    img_b64 = result['predictions'][0]['bytesBase64Encoded']
                    img_bytes = base64.b64decode(img_b64)
                    
                    if output_path:
                        with open(output_path, 'wb') as f:
                            f.write(img_bytes)
                        print(f"✅ Imagem gerada e salva em: {output_path}")
                        
                    # Gravar no DB o custo da imagem
                    try:
                        from database_manager import db
                        canal_id = self.config.get("canal_id", 1)
                        db.gravar_uso_api(canal_id, "imagen3", 1, 0.03)
                    except Exception as e:
                        print(f"Erro ao gravar estatística de Imagen: {e}")
                        
                    return img_bytes
            print(f"❌ Erro na API Imagen: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            import traceback
            print(f"❌ Erro na geração de imagem: {traceback.format_exc()}")
            return None

    def analyze_news_trending(self, news_list: List[str]) -> Optional[str]:
        """
        Analisa tendências de notícias e sugere prioridades
        
        Args:
            news_list: Lista de notícias disponíveis
            
        Returns:
            str: Análise e sugestões de priorização
        """
        system_prompt = """Você é um editor-chefe experiente em notícias.
        Analise a relevância e urgência das notícias.
        Sugira ordem de prioridade para publicação.
        Considere impacto social, urgência e interesse público."""
        
        news_text = "\n".join([f"- {news}" for news in news_list])
        
        prompt = f"""Analise estas notícias e sugira ordem de prioridade:
        
        {news_text}
        
        Para cada notícia, indique:
        - Nível de urgência (Alto/Médio/Baixo)
        - Potencial de engajamento
        - Ordem recomendada para publicação
        - Justificativa para a priorização"""
        
        return self.generate_content(prompt, system_prompt)
    
    def test_connection(self) -> bool:
        """Testa conexão com a API do Gemini"""
        if not self.api_key:
            return False
        
        try:
            result = self.generate_content("Teste de conexão - responda apenas 'OK'")
            return result == "OK" if result else False
        except:
            return False

# Função de simulação para quando a API não estiver disponível
def simulate_gemini_response(prompt: str, response_type: str = "script") -> str:
    """
    Simula resposta do Gemini para testes offline
    """
    if response_type == "script":
        return f"""🎬 ROTEIRO SIMULADO - {prompt[:30]}...

INTRODUÇÃO:
Bem-vindos ao Descarga News! Hoje vamos falar sobre {prompt[:20]}.

DESENVOLVIMENTO:
Esta é uma notícia simulada criada para teste. Em produção, o Gemini geraria um roteiro real e personalizado.

CONCLUSÃO:
Fiquem ligados para mais atualizações sobre este assunto no Descarga News!"""
    
    elif response_type == "thumbnail":
        return f"🚨 {prompt[:15]}..."
    
    else:
        return f"Resposta simulada para: {prompt[:50]}..."
