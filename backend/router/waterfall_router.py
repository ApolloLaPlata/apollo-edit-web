import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional

# Importando o nosso novo cliente nativo da Lightning
from backend.api.lightning_client import LightningClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# O Cofre Central de Chaves (Para testes, preencha o .env)
CLOUD_ACCOUNTS = {
    "lightning": [
        {"account_id": "lightning_1", "api_key": os.environ.get("LIGHTNING_KEY_1", "dummy_L1"), "status": "active"},
        {"account_id": "lightning_2", "api_key": os.environ.get("LIGHTNING_KEY_2", "dummy_L2"), "status": "active"},
        {"account_id": "lightning_3", "api_key": os.environ.get("LIGHTNING_KEY_3", "dummy_L3"), "status": "active"},
        {"account_id": "lightning_4", "api_key": os.environ.get("LIGHTNING_KEY_4", "dummy_L4"), "status": "active"},
    ],
    "openrouter": [
        {"account_id": "openrouter_main", "api_key": os.environ.get("OPENROUTER_KEY", "dummy_OR"), "status": "active"}
    ],
    "meta_fleet": [{"account_id": f"meta_acc_{i}", "status": "idle"} for i in range(1, 8)],
    "beam": [{"account_id": "beam_1", "api_key": "YOUR_BEAM_KEY", "credits": 30.0}],
}

from backend.cloud_tools.account_pool import account_pool

class WaterfallRouter:
    """
    O PONTEIRO UNIVERSAL DO SISTEMA.
    Toda requisição de IA (Admin, Usuário, Roteirista, Cão de Guarda) DEVE passar por aqui.
    """
    def __init__(self):
        # Apenas mantendo contas legadas temporárias que ainda não foram migradas para o pool
        self.accounts = {
            "openrouter": [
                {"account_id": "openrouter_main", "api_key": os.environ.get("OPENROUTER_KEY", "dummy_OR"), "status": "active"}
            ],
            "beam": [{"account_id": "beam_1", "api_key": "YOUR_BEAM_KEY", "credits": 30.0}],
        }
        
        # Semáforos para evitar Rate Limit
        self.account_locks = {}
        for provider, acc_list in self.accounts.items():
            for acc in acc_list:
                acc_id = acc.get("account_id")
                if acc_id:
                    self.account_locks[acc_id] = asyncio.Semaphore(2)

        self.proxies = []

    async def _get_next_lightning_account(self) -> Optional[dict]:
        """Solicita uma conta disponível do Account Pool central"""
        acc = await account_pool.pick(role="general")
        if not acc:
            return None
        return {"account_id": acc.id, "api_key": acc.api_key}

    async def request_ai_generation(self, prompt: str, system_prompt: Optional[str] = None, user_preferred_model: Optional[str] = None) -> Dict[str, Any]:
        """
        A BASE DE TUDO: O Roteador Central de Inteligência.
        1. Tenta usar a Lightning AI (rodízio de 4 contas) como PRIMAZIA.
        2. Se o usuário pediu um modelo específico que só tem no OpenRouter (ex: GPT-4, Gemini), ou se a Lightning falhar 4 vezes, cai pro OpenRouter.
        """
        logger.info(f"[GATEWAY CENTRAL] Requisição recebida. Modelo preferido do usuário: {user_preferred_model}")
        
        # Se o usuário exigiu um modelo proprietário pesado (GPT-4/Gemini), bypassa a Lightning e vai direto pro OpenRouter (Terciário)
        if user_preferred_model and ("gpt" in user_preferred_model.lower() or "gemini" in user_preferred_model.lower()):
            logger.info("[GATEWAY CENTRAL] Usuário escolheu modelo proprietário. Roteando direto para OpenRouter.")
            return await self._execute_openrouter(prompt, system_prompt, user_preferred_model)

        # O MODELO PADRÃO DA NOSSA INFRAESTRUTURA: Rápido e gratuito na Lightning
        target_model = user_preferred_model if user_preferred_model else "meta-llama/Llama-3-70b-chat-hf"

        # TENTATIVA 1 a 4: RODÍZIO LIGHTNING AI (Primazia Absoluta)
        for attempt in range(4):
            acc = await self._get_next_lightning_account()
            if not acc:
                logger.error("[GATEWAY CENTRAL] Nenhuma conta Lightning ativa encontrada no Pool!")
                break
                
            acc_id = acc["account_id"]
            api_key = acc["api_key"]
            
            logger.info(f"[GATEWAY CENTRAL] Tentando Lightning AI (Conta: {acc_id}) - Tentativa {attempt + 1}/4")
            
            try:
                # Usa o nosso cliente Python nativo que criamos
                client = LightningClient(api_key=api_key)
                
                # Execução assíncrona simulada (deve ser jogada num threadpool no mundo real ou usar lib async)
                # Para evitar bloquear o event loop do FastAPI
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: client.generate_text(prompt, model=target_model, system_prompt=system_prompt)
                )
                
                logger.info(f"[GATEWAY CENTRAL] Sucesso via Lightning ({acc_id})!")
                account_pool.report_success(acc_id)
                return {
                    "status": "success",
                    "provider": "lightning",
                    "account_id": acc_id,
                    "model_used": target_model,
                    "content": response
                }
                
            except Exception as e:
                logger.warning(f"[GATEWAY CENTRAL] Falha na conta Lightning {acc_id}: {e}. Marcando como offline temporariamente e rotacionando...")
                account_pool.report_error(acc_id)
                continue
                
        # TENTATIVA FINAL: FALLBACK PARA OPENROUTER (O Pneu de Estepe)
        logger.warning("[GATEWAY CENTRAL] Todas as 4 contas Lightning falharam ou estouraram limite. Acionando Camada Terciária (OpenRouter).")
        return await self._execute_openrouter(prompt, system_prompt, target_model)

    async def _execute_openrouter(self, prompt: str, system_prompt: Optional[str], model: str) -> Dict[str, Any]:
        """Executa a chamada na camada terciária (OpenRouter)"""
        acc = self.accounts["openrouter"][0]
        # Aqui entraria a chamada real requests.post para a API do OpenRouter
        await asyncio.sleep(1) # Simulação
        return {
            "status": "success",
            "provider": "openrouter",
            "account_id": acc["account_id"],
            "model_used": model,
            "content": "[Simulação] Resposta gerada com segurança via OpenRouter Fallback."
        }

    async def route_task(self, task_type: str, payload: Dict[str, Any], use_nitro: bool = False) -> Dict[str, Any]:
        """
        Mantendo retrocompatibilidade para tarefas de mídia pesada (Beam, Meta Fleet).
        Para tarefas de Inteligência (Texto), agora se deve usar request_ai_generation diretamente.
        """
        logger.info(f"Roteando tarefa de Mídia/Sistema tipo: {task_type} (Nitro: {use_nitro})")
        
        return {"status": "error", "message": f"Tipo de tarefa desconhecido: {task_type}"}

    # ==============================================================
    # Motor Furtivo (Stealth Engine)
    # ==============================================================
    
    def get_stealth_headers(self) -> Dict[str, str]:
        """Gera headers mascarados para confundir sistemas antifraude."""
        import random
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        accept_languages = [
            "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "en-US,en;q=0.9",
            "es-ES,es;q=0.9,en;q=0.8",
            "fr-FR,fr;q=0.9,en-US;q=0.8"
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": random.choice(accept_languages),
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive"
        }

    # ==============================================================
    # Simuladores de Execução (Assíncronos com POLLING)
    # ==============================================================

    async def _simulate_meta_fleet_execution(self, task_type, payload, meta_acc):
        """Dispara a automação Headless do Playwright (Meta)"""
        import asyncio
        acc_id = meta_acc["account_id"]
        logger.info(f"[Meta Fleet] Roteando para a frota autônoma. Conta: {acc_id}")
        
        # Bloqueia a conta para que não peguemos tarefas simultâneas para o mesmo browser
        meta_acc["status"] = "busy"
        try:
            # Tenta importar o Robô (pode falhar se Playwright não estiver instalado)
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from meta_robot import meta_fleet_commander, PLAYWRIGHT_AVAILABLE
            except ImportError:
                return {"status": "error", "message": "Meta Robot Module not found."}

            if not PLAYWRIGHT_AVAILABLE:
                logger.warning(f"[{acc_id}] Playwright não está instalado. Simulando delay de Frota Fantasma...")
                await asyncio.sleep(4)
                return {
                    "status": "success", 
                    "provider": "meta_fleet", 
                    "account_id": acc_id, 
                    "image_url": "https://via.placeholder.com/800x600.png?text=Meta+Playwright+Simulation",
                    "note": "Instale o Playwright para a automação real."
                }
            
            # Execução Real Headless
            prompt = payload.get("prompt", "Gere uma imagem aleatória")
            
            # Carrega a conta silenciosamente
            await meta_fleet_commander.load_account(acc_id)
            
            # Gera o vídeo navegando pelo site invisível
            result = await meta_fleet_commander.generate_video(acc_id, prompt)
            
            # Retorna o resultado para o Frontend
            if result.get("status") == "success":
                # Idealmente o arquivo deveria ser servido via URL, aqui estamos retornando o path local
                return {
                    "status": "success",
                    "provider": "meta_fleet",
                    "account_id": acc_id,
                    "file_path": result.get("file_path"),
                    "note": "Gerado 100% via Automação Headless"
                }
            else:
                return result

        finally:
            # Libera a conta para o próximo pedido
            meta_acc["status"] = "idle"

    async def _simulate_nanobanana_fleet_execution(self, task_type, payload, hf_acc):
        """Dispara a automação Headless do Playwright (NanoBanana/HuggingFace)"""
        import asyncio
        acc_id = hf_acc["account_id"]
        logger.info(f"[NanoBanana Fleet] Roteando para a frota autônoma. Conta: {acc_id}")
        
        hf_acc["status"] = "busy"
        try:
            try:
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
                from nanobanana_robot import nanobanana_fleet_commander, PLAYWRIGHT_AVAILABLE
            except ImportError:
                return {"status": "error", "message": "NanoBanana Robot Module not found."}

            if not PLAYWRIGHT_AVAILABLE:
                logger.warning(f"[{acc_id}] Playwright não está instalado. Simulando delay de Frota Fantasma NanoBanana...")
                await asyncio.sleep(4)
                return {
                    "status": "success", 
                    "provider": "nanobanana_fleet", 
                    "account_id": acc_id, 
                    "image_url": "https://via.placeholder.com/1024x1024.png?text=Flux+NanoBanana+Simulation",
                    "note": "Instale o Playwright para a automação real."
                }
            
            prompt = payload.get("prompt", "Gere uma imagem de alta qualidade")
            
            await nanobanana_fleet_commander.load_account(acc_id)
            result = await nanobanana_fleet_commander.generate_image(acc_id, prompt)
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "provider": "nanobanana_fleet",
                    "account_id": acc_id,
                    "image_url": result.get("image_url"),
                    "note": "Gerado 100% via Automação Headless do Flow"
                }
            else:
                return result

        finally:
            hf_acc["status"] = "idle"

    async def _simulate_lightning_execution(self, task_type, payload, acc):
        import asyncio
        await asyncio.sleep(1) # Rápido (1s)
        return {"status": "success", "provider": "lightning", "account_id": acc["account_id"], "data": f"Resultado de {task_type} gerado no Lightning"}

    async def _simulate_tier2_execution(self, task_type, payload, t2):
        import asyncio
        import random
        
        acc_id = t2["account"]["account_id"]
        
        # ==============================================================
        # STEALTH: Semáforo de Concorrência
        # Aguarda na fila se esta conta já estiver no limite de chamadas
        # ==============================================================
        logger.info(f"[{t2['provider']}] Checando semáforo para conta {acc_id}...")
        async with self.account_locks[acc_id]:
            logger.info(f"[{t2['provider']}] Semáforo aberto para {acc_id}. Iniciando requisição segura.")
            
            # O Roteador "veste a máscara" antes de pedir
            stealth_headers = self.get_stealth_headers()
            logger.info(f"[{t2['provider']}] Disfarce ativado: {stealth_headers['User-Agent'][:40]}...")
            
            # NOTA STEALTH (TLS Fingerprint):
            # No futuro, em vez de aiohttp/requests, usaremos:
            # from curl_cffi.requests import AsyncSession
            # async with AsyncSession(impersonate="chrome110", proxies=self.proxies) as s:
            #     response = await s.post(...)
            
            # ESTRATÉGIA DE POLLING: Não enviamos Webhook. 
            # Nós pedimos o ID da tarefa e o Python fica checando de tempo em tempo.
            task_id = "task_998877"
            logger.info(f"[{t2['provider']}] Tarefa enviada. ID recebido: {task_id}. Iniciando Polling Furtivo...")
            
            # Loop de Polling com ORGANIC JITTER (Comportamento Humano)
            for attempt in range(1, 4):
                # Em vez de sleep exato de 2s (robótico), usamos Jitter: 2.0s + aleatório entre 0.1 e 1.5s
                jitter = random.uniform(0.1, 1.5)
                wait_time = 2.0 + jitter
                logger.info(f"[{t2['provider']}] Polling tentativa {attempt}: Esperando {wait_time:.2f}s como um humano...")
                await asyncio.sleep(wait_time)
            
            logger.info(f"[{t2['provider']}] Tarefa {task_id} concluída!")
            
            # Desconta um valor simbólico do saldo falso
            t2['account']['credits'] -= 0.01 
            
            # Simulando um B-Roll
            if task_type == "image_gen":
                image_url = "https://via.placeholder.com/800x600.png?text=Flux+Image+Generated"
                return {"status": "success", "provider": t2["provider"], "account_id": acc_id, "image_url": image_url}
            
            return {"status": "success", "provider": t2["provider"], "account_id": acc_id, "data": f"Executado em GPU Dedicada no {t2['provider']}"}

    async def _simulate_replicate_execution(self, task_type, payload):
        import asyncio
        await asyncio.sleep(2)
        if task_type == "image_gen":
            image_url = "https://via.placeholder.com/800x600.png?text=Replicate+Fallback+Image"
            return {"status": "success", "provider": "replicate", "image_url": image_url}
        return {"status": "success", "provider": "replicate", "data": "Processado no Replicate"}
        
    async def _simulate_openrouter_execution(self, task_type, payload):
        import asyncio
        await asyncio.sleep(1)
        return {"status": "success", "provider": "openrouter", "reply": "Resposta do OpenRouter"}

# Instância global do roteador
router_instance = WaterfallRouter()
