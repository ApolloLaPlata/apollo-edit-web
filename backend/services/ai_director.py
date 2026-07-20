import json
import os
import re
import random
import requests
import time
import logging

class AIDirectorPipeline:
    """
    [PARTE 8] Cérebro Semântico com Gemini Real integrado.
    Substitui toda a análise heurística por chamadas LLM reais quando a API está disponível,
    com fallback transparente para o modo heurístico quando não há chave configurada.
    """

    # Modelo Gemini para analise de texto
    GEMINI_BASE_URL    = "https://generativelanguage.googleapis.com/v1beta/models"
    GEMINI_TEXT_MODEL  = "gemini-2.0-flash"
    GEMINI_VISION_MODEL = "gemini-2.0-flash"

    # Endpoints dos outros providers
    OPENAI_URL         = "https://api.openai.com/v1/chat/completions"
    OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
    GROK_URL           = "https://api.x.ai/v1/chat/completions"

    def __init__(self, config_manager=None):
        self.config_manager = config_manager or {}
        
        
        self._gemini_keys      = self._load_provider_keys("gemini")
        # [E20] Chaves dos providers alternativos
        self._openai_keys      = self._load_provider_keys("openai")
        self._openrouter_keys  = self._load_provider_keys("openrouter")
        self._grok_keys        = self._load_provider_keys("grok")
        self.last_token_usage = 0

    # ─────────────────────────────────────────────────────────
    # SEÇÃO 1: CONFIGURAÇÃO E ESTADO
    # ─────────────────────────────────────────────────────────

    def _load_provider_keys(self, provider_name):
        """
        Carrega TODAS as API Keys válidas de um provedor a partir do config_manager.
        Suporta o formato de lista de dicionários e fallback para string simples.
        """
        if provider_name == "openai":
            provider_name = "chatgpt" # Traduz nome interno do config_manager
            
        valid_keys = []
        try:
            keys = self.config_manager.get_api_config(provider_name, "api_keys")
            if isinstance(keys, list):
                for item in keys:
                    k = None
                    if isinstance(item, dict):
                        k = item.get("key", "").strip()
                    elif isinstance(item, str):
                        k = item.strip()
                    if k and k != "YOUR_API_KEY" and k not in valid_keys:
                        valid_keys.append(k)
            
            if not valid_keys:
                single = self.config_manager.get_api_config(provider_name, "api_key")
                if isinstance(single, str) and single.strip() and single.strip() != "YOUR_API_KEY":
                    valid_keys.append(single.strip())
        except Exception as e:
            logging.warning(f"[IA Pipeline] Erro ao carregar chaves do {provider_name}: {e}")
            
        return valid_keys

    def _get_provider(self):
        """[E20] Retorna o provider LLM ativo conforme configurado na aba Diretor IA."""
        cfg = self.config_manager.get("diretor_ia", {})
        return cfg.get("llm_provider", "gemini").lower()

    def has_gemini(self):
        """Retorna True se uma API Key do Gemini esta disponivel."""
        return len(self._gemini_keys) > 0

    def has_llm(self):
        """[E20] Retorna True se qualquer LLM esta disponivel (Gemini, OpenAI, OpenRouter ou Grok)."""
        provider = self._get_provider()
        if provider == "gemini":      return len(self._gemini_keys) > 0
        if provider == "openai":      return len(self._openai_keys) > 0
        if provider == "openrouter":  return len(self._openrouter_keys) > 0
        if provider == "grok":        return len(self._grok_keys) > 0
        return False

    def is_active(self):
        cfg = self.config_manager.get("diretor_ia", {})
        if not cfg.get("ia_ativa", True):
            return False
        # Ativa se qualquer modulo estiver ligado OU se houver prompt estrategico/canal preenchido
        _modulos = any([
            cfg.get("limpeza_semantica", False),
            cfg.get("broll_contextual",  False),
            cfg.get("sfx_inteligente",   False),
            cfg.get("punch_in",          False),
            cfg.get("motion_design",     False),
            cfg.get("censura",           False),
        ])
        _tem_prompt = bool(cfg.get("prompt_estrategico", "").strip()) or \
                      bool(cfg.get("prompt_canal", "").strip())
        return _modulos or _tem_prompt

    # ─────────────────────────────────────────────────────────
    # SEÇÃO 2: MOTOR GEMINI REAL
    # ─────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────
    # SEÇÃO 2: MOTOR LLM MULTI-PROVIDER  [E20]
    # ─────────────────────────────────────────────────────────

    def _chamar_llm(self, prompt, max_retries=2, images_b64=None):
        """
        [E20] Roteador central de chamadas LLM.
        Direciona para o provider configurado pelo usuario: Gemini, OpenAI, OpenRouter ou Grok.
        Em caso de falha, faz fallback automatico para Gemini se disponivel.
        """
        provider = self._get_provider()
        logging.info(f"[LLM] Provider ativo: {provider.upper()}")

        resposta = None
        if provider == "gemini":
            resposta = self._chamar_gemini(prompt, max_retries, images_b64)
        elif provider == "openai":
            resposta = self._chamar_openai(prompt, max_retries)
        elif provider == "openrouter":
            resposta = self._chamar_openrouter(prompt, max_retries)
        elif provider == "grok":
            resposta = self._chamar_grok(prompt, max_retries)
        else:
            resposta = self._chamar_gemini(prompt, max_retries, images_b64)

        # Fallback para Gemini se o provider primario falhar
        if resposta is None and provider != "gemini" and self._gemini_keys:
            logging.warning(f"[LLM] {provider.upper()} falhou. Usando Gemini como fallback.")
            resposta = self._chamar_gemini(prompt, max_retries, images_b64)

        return resposta

    def _chamar_gemini(self, prompt, max_retries=2, images_b64=None):
        """
        Chama o Gemini API (suporta texto e imagens para o Vision).
        Se a chave atual falhar (ex: Quota 429), tenta a próxima chave automaticamente.
        """
        if not self._gemini_keys:
            return None

        parts = [{"text": prompt}]
        if images_b64:
            for b64 in images_b64:
                parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64}})

        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json"
            }
        }
        
        for attempt in range(max_retries):
            for key in self._gemini_keys:
                url = f"{self.GEMINI_BASE_URL}/{self.GEMINI_TEXT_MODEL}:generateContent?key={key}"
                try:
                    resp = requests.post(url, json=payload,
                                         headers={"Content-Type": "application/json"},
                                         timeout=45)
                    if resp.status_code == 200:
                        data = resp.json()
                        self._registrar_uso_tokens(data)
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    elif resp.status_code == 429 or "quota" in resp.text.lower() or "exhausted" in resp.text.lower():
                        logging.warning(f"[Gemini] Limite excedido na chave atual. Tentando proxima chave...")
                        continue # Vai para a proxima chave do loop
                    elif resp.status_code == 403:
                        logging.warning(f"[Gemini] HTTP 403: Chave bloqueada ou API não habilitada no GCP para esta conta. Pulando...")
                        continue
                    else:
                        logging.warning(f"[Gemini] HTTP {resp.status_code}: {resp.text[:200]}")
                        if resp.status_code == 400: return None # Bad request nao se cura com rotacao
                except Exception as e:
                    logging.warning(f"[Gemini] Erro de conexao com a chave atual: {e}")
            
            # Se tentou TODAS as chaves e nao retornou, espera antes do proximo retry
            time.sleep(3)
            
        return None

    def _chamar_openai(self, prompt, max_retries=2):
        """[E20] Chama a API da OpenAI rotacionando as chaves em caso de falha."""
        if not self._openai_keys:
            return None
        cfg = self.config_manager.get("diretor_ia", {})
        model = cfg.get("llm_model_openai", "gpt-4o-mini")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2048,
            "response_format": {"type": "json_object"}
        }
        for attempt in range(max_retries):
            for key in self._openai_keys:
                try:
                    resp = requests.post(
                        self.OPENAI_URL, json=payload,
                        headers={"Authorization": f"Bearer {key}",
                                 "Content-Type": "application/json"},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"]
                    elif resp.status_code == 429 or "quota" in resp.text.lower():
                        logging.warning(f"[OpenAI] Limite de cota atingido. Rotacionando chave...")
                        continue
                    else:
                        logging.warning(f"[OpenAI] HTTP {resp.status_code}: {resp.text[:200]}")
                        if resp.status_code == 400: return None
                except Exception as e:
                    logging.warning(f"[OpenAI] Erro com a chave atual: {e}")
            time.sleep(2)
        return None

    def _chamar_openrouter(self, prompt, max_retries=2):
        """[E20] Chama a API do OpenRouter rotacionando as chaves em caso de falha."""
        if not self._openrouter_keys:
            return None
        cfg = self.config_manager.get("diretor_ia", {})
        model = cfg.get("llm_model_openrouter", "meta-llama/llama-3-8b-instruct")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 8192
        }
        for attempt in range(max_retries):
            for key in self._openrouter_keys:
                try:
                    resp = requests.post(
                        self.OPENROUTER_URL, json=payload,
                        headers={"Authorization": f"Bearer {key}",
                                 "Content-Type": "application/json",
                                 "HTTP-Referer": "https://apollo-editor.app"},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"]
                    elif resp.status_code == 429 or "insufficient_quota" in resp.text.lower():
                        logging.warning(f"[OpenRouter] Limite atingido. Rotacionando chave...")
                        continue
                    else:
                        logging.warning(f"[OpenRouter] HTTP {resp.status_code}: {resp.text[:200]}")
                        if resp.status_code == 400: return None
                except Exception as e:
                    logging.warning(f"[OpenRouter] Erro com a chave atual: {e}")
            time.sleep(2)
        return None

    def _chamar_grok(self, prompt, max_retries=2):
        """[E20] Chama a API do Grok (xAI) rotacionando chaves em caso de falha."""
        if not self._grok_keys:
            return None
        cfg = self.config_manager.get("diretor_ia", {})
        model = cfg.get("llm_model_grok", "grok-3-mini")
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 8192
        }
        for attempt in range(max_retries):
            for key in self._grok_keys:
                try:
                    resp = requests.post(
                        self.GROK_URL, json=payload,
                        headers={"Authorization": f"Bearer {key}",
                                 "Content-Type": "application/json"},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        return resp.json()["choices"][0]["message"]["content"]
                    elif resp.status_code == 429 or "quota" in resp.text.lower():
                        logging.warning(f"[Grok] Cota excedida. Rotacionando chave...")
                        continue
                    else:
                        logging.warning(f"[Grok] HTTP {resp.status_code}: {resp.text[:200]}")
                        if resp.status_code == 400: return None
                except Exception as e:
                    logging.warning(f"[Grok] Erro com a chave atual: {e}")
            time.sleep(2)
        return None

    def _registrar_uso_tokens(self, data):
        """[PARTE 13] Salva o uso de tokens da API para monitoramento."""
        try:
            usage = data.get("usageMetadata", {})
            if not usage:
                return
            _cm = getattr(self, "config_manager", None)
            if _cm and hasattr(_cm, "workspace_dir"):
                hist_file = os.path.join(_cm.workspace_dir, "historico_tokens.json")
            else:
                hist_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historico_tokens.json")
            historico = {"total": 0, "prompt": 0, "candidates": 0, "calls": 0, "history": []}
            if os.path.exists(hist_file):
                with open(hist_file, "r", encoding="utf-8") as f:
                    historico = json.load(f)
            
            p_tokens = usage.get("promptTokenCount", 0)
            c_tokens = usage.get("candidatesTokenCount", 0)
            t_tokens = usage.get("totalTokenCount", 0)
            
            historico["prompt"] += p_tokens
            historico["candidates"] += c_tokens
            historico["total"] += t_tokens
            historico["calls"] += 1
            
            self.last_token_usage = t_tokens
            
            historico["history"].append({
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total": t_tokens
            })
            if len(historico["history"]) > 100:
                historico["history"].pop(0)
                
            with open(hist_file, "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4)
        except Exception as e:
            logging.warning(f"[GeminiIA] Falha ao registrar tokens: {e}")

    def get_last_token_usage(self):
        return self.last_token_usage

    # ─────────────────────────────────────────────────────────
    # SEÇÃO 3: MAPEAMENTO DE PASTAS (Etapa 3 — com LLM real)
    # ─────────────────────────────────────────────────────────

    def auto_map_folders_to_tags(self, folder_list):
        """
        [ETAPA 3 — GEMINI REAL] Analisa os nomes das pastas e gera TAGs semânticas.
        Com Gemini: usa LLM para categorizar qualquer nome de pasta em português.
        Sem Gemini: fallback heurístico por palavras-chave no nome da pasta.
        Retorna: {folder_path: [tag1, tag2, ...]}
        """
        if not folder_list:
            return {}

        if self.has_gemini():
            return self._map_folders_gemini(folder_list)
        else:
            return self._map_folders_heuristico(folder_list)

    def _map_folders_gemini(self, folder_list):
        """Usa Gemini para categorizar pastas em tags semânticas em PT-BR."""
        nomes = [os.path.basename(f) for f in folder_list]
        lista_str = "\n".join([f"- {n}" for n in nomes])

        prompt = f"""Você é um assistente de edição de vídeo. Analise os nomes das pastas abaixo e retorne um JSON onde cada chave é o nome da pasta e o valor é uma lista de tags semânticas em português (máximo 5 tags por pasta, palavras simples e relevantes para contexto visual de vídeo).

Pastas:
{lista_str}

Responda SOMENTE com JSON válido, sem explicações. Exemplo de formato:
{{"Pasta Fogo": ["fogo", "chamas", "ação", "impacto"], "Water Drops": ["água", "chuva", "natureza", "calma"]}}"""

        resposta = self._chamar_gemini(prompt)
        mapped = {}

        if resposta:
            try:
                # Limpa possível markdown ao redor do JSON
                resposta_limpa = re.sub(r'```(?:json)?\s*|\s*```', '', resposta).strip()
                tags_por_nome  = json.loads(resposta_limpa)
                for folder in folder_list:
                    basename = os.path.basename(folder)
                    tags = tags_por_nome.get(basename, ["geral"])
                    mapped[folder] = [t.lower() for t in tags]
                logging.info(f"[GeminiIA] Mapeamento de pastas concluído via Gemini: {len(mapped)} pastas.")
                return mapped
            except Exception as e:
                logging.warning(f"[GeminiIA] Falha ao parsear resposta do Gemini: {e}. Usando heurístico.")

        return self._map_folders_heuristico(folder_list)

    def _map_folders_heuristico(self, folder_list):
        """Fallback: Mapeamento de pastas por palavras-chave no nome."""
        mapped = {}
        KEYWORD_MAP = {
            ("fire", "fogo", "chama", "flame"):       ["fogo", "ação", "impacto"],
            ("water", "agua", "chuva", "rain"):        ["água", "natureza", "calma"],
            ("glitch", "erro", "distorção", "noise"):  ["tech", "glitch", "caos"],
            ("light", "luz", "glow", "brilho", "star"):["destaque", "ideia", "brilho"],
            ("city", "cidade", "urban"):               ["cidade", "movimento", "urbano"],
            ("nature", "natureza", "forest", "floresta"):["natureza", "verde", "calma"],
            ("tech", "tecnologia", "digital", "code"): ["tecnologia", "digital", "futuro"],
            ("space", "espaço", "cosmos", "galaxy"):   ["espaço", "cosmos", "épico"],
            ("money", "dinheiro", "gold", "ouro"):     ["dinheiro", "riqueza", "sucesso"],
            ("smoke", "fumaça", "mist", "fog"):        ["fumaça", "misterio", "ambiente"],
        }
        for folder in folder_list:
            basename = os.path.basename(folder).lower()
            tags = []
            for keywords, folder_tags in KEYWORD_MAP.items():
                if any(k in basename for k in keywords):
                    tags.extend(folder_tags)
            if not tags:
                # Usa palavras do nome como fallback
                words = re.sub(r'[^a-záéíóúãõâêîôûç\s]', ' ', basename).split()
                tags = [w for w in words if len(w) > 3][:3] or ["geral"]
            mapped[folder] = list(dict.fromkeys(tags))  # Remove duplicatas
        return mapped

    # ─────────────────────────────────────────────────────────
    # SEÇÃO 4: ANÁLISE DE ROTEIRO (Etapa 4 — Pipeline Central)
    # ─────────────────────────────────────────────────────────

    def _build_director_context(self, prompt_canal, prompt_video, blocos, formato_video="vertical"):
        """
        [ETAPA 3] Fusão dos Três Contextos.
        Combina a Identidade do Canal, a Estratégia do Vídeo e o Roteiro Transcrito
        em um único prompt unificado para o Gemini.
        """
        roteiro_fmt = "\n".join(
            f"[{b['start']:.1f}s] {b.get('word','')}" for b in blocos if b.get('word')
        )
        # Limita o roteiro para não estourar o limite de tokens se for muito grande
        if len(roteiro_fmt) > 15000:
            roteiro_fmt = roteiro_fmt[:15000] + "\n[... roteiro truncado ...]"

        regra_formato = ""
        if formato_video == "vertical":
            regra_formato = "ATENÇÃO: Este vídeo é VERTICAL (9:16) para TikTok/Reels/Shorts. Cortes devem ser muito rápidos (a cada 3-4s). Zooms devem ser frequentes. Legendas precisam ser grandes e centralizadas."
        elif formato_video == "horizontal":
            regra_formato = "ATENÇÃO: Este vídeo é HORIZONTAL (16:9) para o YouTube. O ritmo deve ser mais apresentativo e cadenciado. Use B-Rolls contextuais longos e câmera mais estável."

        # Carrega dinamicamente a lista de templates disponíveis (Etapa 7)
        templates_disponiveis = []
        try:
            perfis_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perfis_templates")
            if os.path.exists(perfis_dir):
                templates_disponiveis = [f.replace(".json", "") for f in os.listdir(perfis_dir) if f.endswith(".json")]
        except Exception:
            pass
        lista_templates = ", ".join(templates_disponiveis) if templates_disponiveis else "Nenhum detectado, use SEM_PERFIL"
        # Load AI Assets
        ai_assets_texto = ""
        try:
            assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_assets.json")
            if os.path.exists(assets_path):
                with open(assets_path, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                v_tags = set()
                for v in db.get('video', []):
                    v_tags.update(v['tags'])
                a_tags = set()
                for a in db.get('audio', []):
                    a_tags.update(a['tags'])
                
                ai_assets_texto = f"VOCÊ POSSUI UM HD LOCAL COM {len(db.get('video', []))} VÍDEOS E {len(db.get('audio', []))} EFEITOS SONOROS (SFX).\n"
                ai_assets_texto += f"Categorias/Tags Visuais disponíveis: {', '.join(list(v_tags)[:50])}...\n"
                ai_assets_texto += f"Categorias/Tags Sonoras disponíveis: {', '.join(list(a_tags)[:50])}...\n"
                ai_assets_texto += "Quando preencher campos como 'overlay', 'broll' ou criar clipes de áudio (sfx), você PODE usar o caminho de arquivo exato se achar algo que combina com a tag, ou pedir à pipeline para buscar automaticamente sugerindo a Tag. Para este teste, apenas indique a Tag desejada no campo respectivo.\n"
        except Exception as e:
            logging.error(f"[DIRETOR IA] Erro ao carregar ai_assets: {e}")
            pass

        contexto_unificado = f"""
=== IDENTIDADE DO CANAL ===
{prompt_canal if prompt_canal else "Sem identidade definida. Use padrão casual."}

=== ESTRATÉGIA DESTE VÍDEO ===
{prompt_video if prompt_video else "Sem estratégia definida. Edite dinamicamente para retenção."}

=== FORMATO DO VÍDEO ===
{regra_formato}

=== TEMPLATES DISPONÍVEIS ===
Você pode sugerir a troca de estética (perfil) para certas cenas. Opções: {lista_templates}

=== [NOVO] BIBLIOTECA DE EFEITOS (HD LOCAL) ===
{ai_assets_texto}

=== [E22] DETECCAO DE MULTIPLOS FALANTES ===
Se o roteiro apresentar claramente mais de um falante (entrevistado, personagem diferente, etc.),
preencha o campo 'falantes' com os segmentos de cada voz e atribua speaker_id unico (1, 2, 3...).
Se for apenas uma voz/narrador, retorne 'falantes' como array vazio.
Nao invente falantes se o roteiro nao deixar claro. So marque quando o roteiro mudar de interlocutor.

=== [E23] EFEITOS GLOBAIS E TRANSIÇÕES ===
Você PODE decidir o clima visual do vídeo inserindo um filtro de cor na raiz do JSON:
  "filtros_globais": ["bw", "sepia", "high_contrast", "cinematic"] (escolha no máximo 1, ou deixe vazio)
Você PODE criar transições nativas inserindo objetos na array "transicoes":
  {{"start": timestamp_do_corte, "type": "fadeblack" | "fadewhite" | "pixelize" | "circlecrop" | "smoothleft" | "smoothright" | "distance"}}

=== [E21] EFEITOS DE CÂMERA HD DISPONÍVEIS ===
Para o campo "camera", use um dos tipos abaixo (escolha pelo mood da cena):
- kenburns: zoom lento entrando na cena (momentos emocionais, revelações)
- kenburns_out: zoom lento saindo da cena (conclusões, encerramento)
- pan: câmera desliza horizontalmente (apresentações, revelações laterais)
- tilt: câmera sobe/desce verticalmente (suspense, descoberta)
- shake: tremor na câmera (impacto, tensão, susto)
- drift: movimento suave diagonal (fluidez, transição suave)
Use "intensity": "leve" | "medio" | "intenso" para calibrar a força do efeito.
Regras: shake apenas em momentos de alto impacto. kenburns em cenas de peso emocional.

=== ROTEIRO COM TIMESTAMPS ===
{roteiro_fmt}

Retorne APENAS um JSON válido com a seguinte estrutura exata (se não houver decisão, use array vazio []):
{{
  "confianca_geral": 0.85,
  "resumo_decisoes": "Breve descricao do que a IA decidiu fazer neste video",
  "zooms": [],
  "brolls": [],
  "sfx": [
    {{"start": 1.0, "end": 2.0, "category": "impacto"}}
  ],
  "motion": [
    {{"start": 1.0, "end": 3.0, "word": "ABSURDO", "animation": "shake"}}
  ],
  "cortes": [],
  "speed": [],
  "templates": [],
  "infograficos": [],
  "legenda_cor": [],
  "camera": [
    {{"start": 1.0, "end": 4.0, "type": "kenburns", "intensity": "medio"}}
  ],
  "efeito_hd": [],
  "falantes": [
    {{"start": 0.0, "end": 5.0, "speaker_id": 1}},
    {{"start": 5.1, "end": 12.0, "speaker_id": 2}}
  ]
}}
"""
        return contexto_unificado

    def analisar_roteiro(self, blocos_whisper, user_prompt="", prompt_canal="", formato_video="vertical", images_b64=None):
        """
        [ETAPA 4 e 15 - GEMINI VISION] Pipeline Central de análise de roteiro.
        Quando o Gemini está disponível, envia o roteiro completo + frames visuais para análise
        e recebe de volta quais blocos devem ter zoom, motion, broll e censura.
        """
        cfg = self.config_manager.get("diretor_ia", {})
        decisoes_brutas = {}

        # [ETAPA 3 e 4] Fusão de Contextos (Canal + Vídeo + Formato + Roteiro)
        contexto_unificado = self._build_director_context(prompt_canal, user_prompt, blocos_whisper, formato_video)
        logging.info(f"[DIRETOR IA] Contexto Unificado Gerado (Tamanho: {len(contexto_unificado)} chars)")
        # [ETAPA 5] Chamada única ao Gemini com Contexto Unificado e Imagens Base (Vision)
        # Ativa a IA se: tem LLM disponível E (algum módulo está ligado OU algum prompt foi preenchido)
        _algum_modulo_ativo = any([
            cfg.get("punch_in"),
            cfg.get("motion_design"),
            cfg.get("broll_contextual"),
            cfg.get("sfx_inteligente"),
            cfg.get("vision_ativo"),
            cfg.get("cores_por_falante"),
        ])
        _tem_prompt = bool(user_prompt and user_prompt.strip()) or bool(prompt_canal and prompt_canal.strip())
        
        if self.has_llm() and (_algum_modulo_ativo or _tem_prompt):
            import hashlib
            hash_str = contexto_unificado
            if images_b64:
                hash_str += "".join(images_b64)
            md5_hash = hashlib.md5(hash_str.encode('utf-8')).hexdigest()
            
            _cm = getattr(self, "config_manager", None)
            cache_file = os.path.join(_cm.workspace_dir if _cm and hasattr(_cm, "workspace_dir") else os.path.dirname(os.path.abspath(__file__)), "analise_cache.json")
            cache_data = {}
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r", encoding="utf-8") as fc:
                        cache_data = json.load(fc)
                except Exception:
                    pass

            _decisoes_ok = None
            if md5_hash in cache_data:
                logging.info(f"[DIRETOR IA] Anti-Gasto: Cache HIT! Reutilizando analise previa. MD5: {md5_hash}")
                _decisoes_ok = cache_data[md5_hash]
            else:
                logging.info(f"[DIRETOR IA] Ativando LLM — módulos_ativos={_algum_modulo_ativo} | tem_prompt={_tem_prompt}")
                if images_b64:
                    logging.info(f"[DIRETOR IA] Vision ativado! Enviando {len(images_b64)} frame(s) para análise.")
                else:
                    logging.info("[DIRETOR IA] Solicitando JSON de decisoes unificadas do LLM...")
                
                resposta = self._chamar_llm(contexto_unificado, images_b64=images_b64)
                
                # ── RETRY automático se o JSON vier truncado ─────────────────────────
                _max_json_attempts = 3
                for _attempt in range(_max_json_attempts):
                    if not resposta:
                        logging.warning(f"[DIRETOR IA] Tentativa {_attempt+1}: LLM não retornou resposta. Retentando...")
                        resposta = self._chamar_llm(contexto_unificado, images_b64=images_b64)
                        continue
                    try:
                        res_limpa = re.sub(r'```(?:json)?\s*|\s*```', '', resposta).strip()
                        # Tenta reparar JSON truncado: fecha chaves/colchetes ausentes
                        _abertos_ch = res_limpa.count('{') - res_limpa.count('}')
                        _abertos_col = res_limpa.count('[') - res_limpa.count(']')
                        if _abertos_ch > 0 or _abertos_col > 0:
                            logging.warning(f"[DIRETOR IA] JSON aparentemente truncado (faltam {_abertos_ch} '}}' e {_abertos_col} ']'). Tentando reparar...")
                            if res_limpa.count('"') % 2 != 0:
                                res_limpa += '"'
                            res_limpa += ']' * max(0, _abertos_col)
                            res_limpa += '}' * max(0, _abertos_ch)
                        _decisoes_ok = json.loads(res_limpa)
                        
                        if (_abertos_ch > 0 or _abertos_col > 0) and not any(k in _decisoes_ok for k in ['zooms', 'brolls', 'camera', 'sfx', 'motion']):
                            raise Exception("JSON foi truncado muito cedo e perdeu todos os blocos de comando visual.")
                            
                        break  # Parsing OK
                    except Exception as e_json:
                        logging.warning(f"[DIRETOR IA] Tentativa {_attempt+1}/{_max_json_attempts} falhou ao parsear JSON: {e_json}")
                        resposta = None
                        time.sleep(1)
                
                if _decisoes_ok is not None:
                    cache_data[md5_hash] = _decisoes_ok
                    try:
                        with open(cache_file, "w", encoding="utf-8") as fc:
                            json.dump(cache_data, fc, indent=4)
                    except Exception as e_cache:
                        logging.warning(f"[DIRETOR IA] Falha ao salvar analise_cache.json: {e_cache}")
            
            if _decisoes_ok is not None:
                decisoes = _decisoes_ok
                decisoes_brutas = decisoes
                confianca = decisoes.get("confianca_geral", None)
                resumo    = decisoes.get("resumo_decisoes", "")
                if confianca is not None:
                    logging.info(f"[DIRETOR IA] Confianca da IA: {confianca:.0%}")
                if resumo:
                    logging.info(f"[DIRETOR IA] Resumo: {resumo}")
                for b in blocos_whisper:
                    b["_ia_confianca"] = confianca
                    b["_ia_resumo"]    = resumo
                logging.info(f"[DIRETOR IA] JSON processado com sucesso: {list(decisoes.keys())}")
                self._aplicar_decisoes_gemini(blocos_whisper, decisoes, cfg)
            else:
                logging.error(f"[DIRETOR IA] Falha total ao parsear JSON após {_max_json_attempts} tentativas. Usando fallback heurístico.")
                self._aplicar_heuristica_fallback(blocos_whisper, cfg)
        else:
            logging.info(f"[DIRETOR IA] Usando fallback heurístico — has_llm={self.has_llm()} | módulos={_algum_modulo_ativo} | prompt={_tem_prompt}")
            self._aplicar_heuristica_fallback(blocos_whisper, cfg)

        # 1. Censura (sempre por regex — determinístico e rápido)
        if cfg.get("censura", False):
            self._aplicar_censura(blocos_whisper)

        # 5. Corte de Silêncio (Etapa 10)
        if cfg.get("limpeza_semantica", False):
            blocos_whisper = self._remover_silencias_hibrido(blocos_whisper)

        return blocos_whisper, decisoes_brutas

    def _aplicar_heuristica_fallback(self, blocos, cfg):
        """Fallback caso o Gemini falhe ou não esteja disponível."""
        if cfg.get("punch_in", False) or cfg.get("motion_design", False):
            self._aplicar_enfase_heuristico(blocos, cfg)
        if cfg.get("broll_contextual", False):
            self._aplicar_broll_contextual(blocos)

    def _aplicar_decisoes_gemini(self, blocos, decisoes, cfg):
        """Mapeia as decisões estruturadas do JSON para os blocos do Whisper."""
        
        # 1. Mapeia Zooms (Punch-In)
        if cfg.get("punch_in", False):
            for z in decisoes.get("zooms", []):
                start = z.get("start", -1)
                end = z.get("end", 99999)
                for b in blocos:
                    if b["start"] >= start and b["start"] <= end:
                        b["zoom_trigger"] = True
                        
        # 2. Mapeia Motion Design (Textos em Destaque)
        if cfg.get("motion_design", False):
            for m in decisoes.get("motion", []):
                start = m.get("start", -1)
                end = m.get("end", 99999)
                palavra_chave = m.get("word", "")
                animacao = m.get("animation", "float") # float, shake, pop
                for b in blocos:
                    if b["start"] >= start and b["start"] <= end:
                        b["motion_trigger"] = True
                        if palavra_chave:
                            b["motion_word"] = palavra_chave
                        b["motion_animation"] = animacao
                        
        # 3. Mapeia B-Rolls
        if cfg.get("broll_contextual", False):
            for br in decisoes.get("brolls", []):
                start = br.get("start", -1)
                tag = br.get("tag", "")
                if tag:
                    for b in blocos:
                        if b["start"] >= start:
                            b["broll_tag"] = tag
                            # Realiza a injeção do arquivo B-Roll local usando a tag
                            self._injetar_broll_por_tag(b, tag)
                            break
                            
        # 4. [ETAPA 13] SFX por categoria semântica
        for s in decisoes.get("sfx", []):
            start = s.get("start", -1)
            end = s.get("end", 99999)
            category = s.get("category", "")
            if category:
                for b in blocos:
                    if b["start"] >= start and b["start"] <= end:
                        b["sfx_trigger"] = True
                        b["sfx_category"] = category
        
        for c in decisoes.get("cortes", []):
            for b in blocos:
                if isinstance(c, dict):
                    c_start = c.get("start", -1)
                    c_reason = c.get("reason", "Corte Inteligente")
                else:
                    c_start = float(c)
                    c_reason = "Corte Inteligente"
                    
                if b["start"] >= c_start:
                    b["corte_acao"] = c_reason
                    break

        for sp in decisoes.get("speed", []):
            start = sp.get("start", -1)
            end = sp.get("end", 99999)
            factor = sp.get("factor", 1.0)
            for b in blocos:
                if b["start"] >= start and b["start"] <= end:
                    b["speed_factor"] = factor

        for tmpl in decisoes.get("templates", []):
            start = tmpl.get("start", -1)
            end = tmpl.get("end", 99999)
            name = tmpl.get("name", "SEM_PERFIL")
            for b in blocos:
                if b["start"] >= start and b["start"] <= end:
                    b["perfil"] = name

        _cam_aplicados = 0
        for cam in decisoes.get("camera", []):
            start = cam.get("start", -1)
            end   = cam.get("end", 99999)
            ctype = cam.get("type", "")
            # [E21] captura intensidade do efeito HD
            intensity = cam.get("intensity", "medio")
            for b in blocos:
                if b["start"] >= start and b["start"] <= end:
                    b["camera_fx"]           = ctype
                    b["camera_fx_intensity"] = intensity
                    _cam_aplicados += 1
        
        # Log de diagnóstico de quantos efeitos foram aplicados
        _n_zooms   = sum(1 for b in blocos if b.get("zoom_trigger"))
        _n_motion  = sum(1 for b in blocos if b.get("motion_trigger"))
        _n_cam_fx  = sum(1 for b in blocos if b.get("camera_fx"))
        _n_sfx     = sum(1 for b in blocos if b.get("sfx_trigger"))
        _n_speed   = sum(1 for b in blocos if b.get("speed_factor", 1.0) != 1.0)
        print(f"[IA-DECISOES] Zoom={_n_zooms} | Motion={_n_motion} | Camera={_n_cam_fx} | SFX={_n_sfx} | Speed={_n_speed}", flush=True)
        logging.info(f"[IA-DECISOES] Efeitos injetados nos blocos: zoom={_n_zooms} motion={_n_motion} camera={_n_cam_fx} sfx={_n_sfx} speed={_n_speed}")

        for info in decisoes.get("infograficos", []):
            start = info.get("start", -1)
            end = info.get("end", 99999)
            text = info.get("text", "")
            tipo = info.get("type", "bottom")
            for b in blocos:
                if b["start"] >= start and b["start"] <= end:
                    b["infografico_text"] = text
                    b["infografico_type"] = tipo

        for leg in decisoes.get("legenda_cor", []):
            start = leg.get("start", -1)
            end   = leg.get("end", 99999)
            color = leg.get("color", "")
            for b in blocos:
                if b["start"] >= start and b["start"] <= end:
                    b["legenda_cor"] = color

        # [E22] Deteccao de multiplos falantes — atribui cor por speaker_id
        # Paleta: speaker 1=branco(padrao), 2=amarelo, 3=azul, 4=verde, 5=rosa, 6+=laranja
        _paleta_falantes = {
            1: "",          # voz principal — cor padrao do tema (sem override)
            2: "amarelo",
            3: "azul",
            4: "verde",
            5: "rosa",
            6: "laranja",
        }
        cfg_e22 = self.config_manager.get("diretor_ia", {})
        if cfg_e22.get("cores_por_falante", False):
            for sp in decisoes.get("falantes", []):
                start    = sp.get("start", -1)
                end      = sp.get("end", 99999)
                try:
                    spk_id = int(sp.get("speaker_id", 1))
                except (ValueError, TypeError):
                    spk_id = 2  # Fallback seguro caso a IA retorne um nome ao invés de numero
                cor_spk  = _paleta_falantes.get(spk_id, "laranja")
                if not cor_spk:  # falante 1: sem override
                    continue
                for b in blocos:
                    if b["start"] >= start and b["start"] <= end:
                        # Só aplica se a cor ainda não foi definida por legenda_cor emocional
                        if not b.get("legenda_cor"):
                            b["legenda_cor"]   = cor_spk
                            b["falante_id"]    = spk_id
                logging.info(f"[E22] Falante #{spk_id} ({cor_spk}) mapeado: {start:.1f}s–{end:.1f}s")

    def _injetar_broll_por_tag(self, bloco, tag):
        """Busca o arquivo de B-Roll baseado na tag fornecida pelo Gemini."""
        estetica_cfg = self.config_manager.get("estetica_canal", {})
        overlay_dirs = estetica_cfg.get("overlay_dirs", [])
        if not overlay_dirs: return
        tags_mapping = self.auto_map_folders_to_tags(overlay_dirs)
        
        for folder, tags in tags_mapping.items():
            if tag.lower() in [t.lower() for t in tags]:
                try:
                    arquivos = [f for f in os.listdir(folder) if f.lower().endswith(('.mp4', '.mov', '.png'))]
                    if arquivos:
                        bloco["broll_path"] = os.path.join(folder, random.choice(arquivos))
                except Exception:
                    pass
                break

    def _aplicar_censura(self, blocos):
        """Censura por regex: determinístico, não usa LLM."""
        censura_words_str = self.config_manager.get("estetica_canal", {}).get("censura_words", "")
        if not censura_words_str:
            return
        bad_words = {w.strip().lower() for w in censura_words_str.split(",") if w.strip()}
        for bloco in blocos:
            word_clean = re.sub(r'[^\w\s]', '', bloco.get("word", "")).lower()
            if word_clean in bad_words:
                bloco["is_censored"] = True
                bloco["word"]        = "***"

    def _aplicar_enfase_gemini(self, blocos, cfg):
        """
        [ETAPA 13 — GEMINI REAL] Análise semântica de ênfase via LLM.
        Envia o roteiro completo e recebe de volta os índices das palavras/frases de impacto.
        """
        # Monta o contexto completo do roteiro (limita a 3000 caracteres para não gastar tokens)
        texto_roteiro = " ".join(b.get("word", "") for b in blocos)[:3000]

        prompt = f"""Você é um diretor de vídeo especialista em retenção de audiência no YouTube.
Analise o roteiro abaixo e identifique as palavras ou frases que têm ALTO IMPACTO emocional, surpresa, ou ênfase — ideais para aplicar um zoom (punch-in) ou texto animado na tela.

Roteiro: "{texto_roteiro}"

Responda SOMENTE com um JSON contendo uma lista de strings (palavras exatas do roteiro que merecem destaque):
{{"palavras_destaque": ["palavra1", "palavra2", "frase de impacto"]}}

Máximo 8 itens. Escolha apenas o que realmente importa para a retenção."""

        resposta = self._chamar_gemini(prompt)
        palavras_destaque = set()

        if resposta:
            try:
                resposta_limpa    = re.sub(r'```(?:json)?\s*|\s*```', '', resposta).strip()
                data              = json.loads(resposta_limpa)
                palavras_destaque = {p.lower() for p in data.get("palavras_destaque", [])}
                logging.info(f"[GeminiIA] Palavras de destaque detectadas: {palavras_destaque}")
            except Exception as e:
                logging.warning(f"[GeminiIA] Falha ao parsear ênfase: {e}")

        # Aplica triggers nos blocos que contenham as palavras de destaque
        for bloco in blocos:
            word = bloco.get("word", "").lower().strip()
            # Verifica match exato ou se o bloco contém a palavra de destaque
            if any(dest in word or word in dest for dest in palavras_destaque) or \
               "!" in bloco.get("word", "") or "?" in bloco.get("word", ""):
                if cfg.get("punch_in",     False): bloco["zoom_trigger"]   = True
                if cfg.get("motion_design",False): bloco["motion_trigger"] = True

        # Fallback: se Gemini não retornou nada, usa heurística
        if not palavras_destaque:
            self._aplicar_enfase_heuristico(blocos, cfg)

    def _aplicar_enfase_heuristico(self, blocos, cfg):
        """Fallback heurístico: detecta ênfase por pontuação e palavras de impacto."""
        PALAVRAS_IMPACTO = {
            "incrível", "impossível", "nunca", "sempre", "segredo", "grátis",
            "urgente", "agora", "atenção", "importante", "exclusivo", "revelação",
            "cuidado", "erro", "perigo", "descoberta", "surpreendente", "inacreditável"
        }
        for bloco in blocos:
            word = bloco.get("word", "")
            word_clean = re.sub(r'[^\w]', '', word).lower()
            if "!" in word or "?" in word or word_clean in PALAVRAS_IMPACTO:
                if cfg.get("punch_in",     False): bloco["zoom_trigger"]   = True
                if cfg.get("motion_design",False): bloco["motion_trigger"] = True

    def _aplicar_broll_contextual(self, blocos):
        """[Etapas 13 e 14] Cruza o roteiro com as tags das pastas para injetar B-Roll.
        CORRECAO: aplica B-Roll apenas em blocos selecionados semanticamente,
        sem inundar todos os blocos com o mesmo arquivo (evita loop de 1 video)."""
        estetica_cfg = self.config_manager.get("estetica_canal", {})
        overlay_dirs = estetica_cfg.get("overlay_dirs", [])
        if not overlay_dirs:
            return

        tags_mapping = self.auto_map_folders_to_tags(overlay_dirs)
        if not tags_mapping:
            return

        # Apenas 1 B-Roll a cada 8 blocos para evitar repetição massiva
        _broll_interval = 8
        _last_broll_idx = -_broll_interval  # Permite o primeiro logo no inicio
        
        for idx, bloco in enumerate(blocos):
            # Nao injeta se ja tem B-Roll ou se está no intervalo de cooldown
            if bloco.get('broll_path'):
                _last_broll_idx = idx
                continue
            if idx - _last_broll_idx < _broll_interval:
                continue
                
            word = bloco.get("word", "").lower()
            for folder, tags in tags_mapping.items():
                if any(t in word for t in tags):
                    try:
                        arquivos = [f for f in os.listdir(folder)
                                    if f.lower().endswith(('.mp4', '.mov', '.png'))]
                        if arquivos:
                            bloco["broll_path"] = os.path.join(folder, random.choice(arquivos))
                            bloco["broll_tag"]  = tags[0]
                            _last_broll_idx = idx
                            break
                    except Exception:
                        pass

    # ─────────────────────────────────────────────────────────
    # SEÇÃO 5: MOTOR DE PROMPT NATURAL REAL (Etapa 15)
    # ─────────────────────────────────────────────────────────

    def _processar_prompt_natural(self, blocos, user_prompt):
        """
        [ETAPA 15 — GEMINI REAL] Processa comandos em linguagem natural do usuário.
        O Gemini interpreta o pedido e retorna quais blocos devem ser removidos ou modificados.
        """
        # Monta sumário de blocos com índice e tempo
        sumario = []
        for idx, b in enumerate(blocos):
            t = b.get("start", 0)
            w = b.get("word", "")
            sumario.append(f"[{idx}] {t:.1f}s: {w}")
        sumario_str = "\n".join(sumario[:200])  # Limita para não estourar contexto

        prompt = f"""Você é um assistente de edição de vídeo. O usuário deu a seguinte instrução:
"{user_prompt}"

Abaixo está a transcrição numerada (índice, tempo, palavra) do vídeo:
{sumario_str}

Com base na instrução do usuário, retorne um JSON com:
1. "remover_indices": lista de índices que devem ser REMOVIDOS do vídeo (ex: a intro, pausas)
2. "acao": descrição curta do que foi feito

Responda SOMENTE com JSON. Exemplo: {{"remover_indices": [0,1,2,3,4], "acao": "Removida a introdução (primeiros 5 blocos)"}}
Se não houver nada para remover, retorne {{"remover_indices": [], "acao": "Nenhuma alteração necessária"}}"""

        resposta = self._chamar_gemini(prompt)

        if resposta:
            try:
                resposta_limpa  = re.sub(r'```(?:json)?\s*|\s*```', '', resposta).strip()
                data            = json.loads(resposta_limpa)
                indices_remover = set(data.get("remover_indices", []))
                acao            = data.get("acao", "")

                if indices_remover:
                    blocos_filtrados = [b for i, b in enumerate(blocos) if i not in indices_remover]
                    logging.info(f"[GeminiIA] Prompt natural executado: '{acao}' | {len(indices_remover)} blocos removidos.")
                    return blocos_filtrados
                else:
                    logging.info(f"[GeminiIA] Prompt natural: {acao}")
            except Exception as e:
                logging.warning(f"[GeminiIA] Falha ao processar prompt natural: {e}")

        return blocos

    # ─────────────────────────────────────────────────────────
    # SEÇÃO 6: UTILITÁRIOS
    # ─────────────────────────────────────────────────────────

    def _remover_silencias_hibrido(self, blocos):
        """[ETAPA 10] Remove pausas e hesitações curtas, preservando triggers da IA."""
        resultado      = []
        palavras_vazias = {"", "...", "hmm", "ah", "eh", "uh", "um", "mm", "né", "tipo"}

        for b in blocos:
            word = re.sub(r'[^\w]', '', b.get("word", "")).lower().strip()
            dur  = b.get("end", 0) - b.get("start", 0)
            tem_trigger = any([b.get("is_censored"), b.get("zoom_trigger"),
                               b.get("motion_trigger"), b.get("broll_path"), b.get("sfx_trigger")])

            if tem_trigger:
                resultado.append(b)
            elif word in palavras_vazias and dur < 0.25:
                pass  # Descarta silêncio/hesitação
            else:
                resultado.append(b)

        return resultado

    def testar_conexao_gemini(self):
        """
        Testa se a conexão com o Gemini está funcionando.
        Retorna (bool, str): (sucesso, mensagem)
        """
        if not self._gemini_keys:
            return False, "Nenhuma API Key do Gemini configurada na aba Configuração Global."

        resposta = self._chamar_gemini('{"teste": true}')
        if resposta is not None:
            return True, f"✅ Conexão com Gemini estabelecida! ({len(self._gemini_keys)} chaves disponíveis e rotativas)"
        return False, "❌ Falha na conexão. Verifique a chave de API e a internet. (Todas as chaves falharam)"
