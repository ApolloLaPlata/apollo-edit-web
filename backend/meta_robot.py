import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("MetaRobot")
logger.setLevel(logging.INFO)

# O Playwright precisa ser instalado pelo usuário: pip install playwright && playwright install chromium
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class MetaPlaywrightFleet:
    """
    Exército Robótico Headless. 
    Mantém N navegadores invisíveis abertos, cada um logado via cookies salvos.
    """
    def __init__(self, cookies_dir: str):
        self.cookies_dir = cookies_dir
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        
        # Central de seletores (Se o Meta mudar o UI, mudamos apenas aqui)
        self.selectors = {
            "prompt_input": "textarea[placeholder*='Descreva']",
            "generate_btn": "button:has-text('Gerar')",
            "download_btn": "a[download]",
            "error_modal": "div.error-message"
        }

    async def start_fleet(self):
        """Inicializa o motor do Playwright e abre o Chromium invisível"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright não instalado. Execute: pip install playwright")
            return
            
        self.playwright = await async_playwright().start()
        # headless=True significa Invisível no servidor.
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("[Meta Fleet] Motor Headless Chromium Inicializado.")

    async def load_account(self, account_id: str):
        """Carrega uma conta específica usando Cookies salvos, bypassando o login"""
        if not self.browser:
            await self.start_fleet()
            
        cookie_file = os.path.join(self.cookies_dir, f"{account_id}_cookies.json")
        
        if not os.path.exists(cookie_file):
            logger.warning(f"[Meta Fleet] Sem cookies para {account_id}. Não é possível logar.")
            return

        # Cria um "Contexto" limpo (uma janela anônima só para essa conta)
        context = await self.browser.new_context(storage_state=cookie_file)
        page = await context.new_page()
        
        self.contexts[account_id] = context
        self.pages[account_id] = page
        logger.info(f"[Meta Fleet] Conta {account_id} carregada e autenticada silenciosamente.")

    async def generate_video(self, account_id: str, prompt: str) -> Dict[str, Any]:
        """A mágica principal: Dirige o navegador para gerar o vídeo"""
        if account_id not in self.pages:
            logger.error(f"[Meta Fleet] Conta {account_id} não está logada/carregada.")
            return {"status": "error", "message": "Account not loaded"}
            
        page = self.pages[account_id]
        
        try:
            logger.info(f"[{account_id}] Navegando para o estúdio do Meta...")
            # IMPORTANTE: Colocar a URL correta do gerador do Meta aqui
            await page.goto("https://www.meta.ai/imagine", wait_until="networkidle")
            
            # 1. Digita o prompt
            logger.info(f"[{account_id}] Injetando prompt: {prompt}")
            await page.fill(self.selectors["prompt_input"], prompt)
            
            # 2. Clica em Gerar
            logger.info(f"[{account_id}] Acionando botão de geração...")
            await page.click(self.selectors["generate_btn"])
            
            # 3. Espera Inteligente (Polling de Elemento)
            # Fica aguardando até 5 minutos pelo botão de download aparecer
            logger.info(f"[{account_id}] Aguardando a nuvem do Meta processar o vídeo...")
            
            async with page.expect_download(timeout=300000) as download_info:
                # Se houver um botão de download na interface para clicar, clicamos
                await page.click(self.selectors["download_btn"])
                
            download = await download_info.value
            
            # Salva o arquivo em um diretório temporário do Backend
            save_path = os.path.join("temp", f"{account_id}_video_{download.suggested_filename}")
            await download.save_as(save_path)
            
            logger.info(f"[{account_id}] Vídeo baixado com sucesso em {save_path}!")
            return {"status": "success", "file_path": save_path}
            
        except Exception as e:
            logger.error(f"[{account_id}] Falha na geração robótica: {str(e)}")
            # Aqui no futuro podemos adicionar código para tirar print (screenshot) do erro do Meta
            # await page.screenshot(path=f"error_{account_id}.png")
            return {"status": "error", "message": str(e)}

    async def shutdown(self):
        """Desliga todos os motores"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("[Meta Fleet] Todos os navegadores fantasmas foram desligados.")

# Instância global
meta_fleet_commander = MetaPlaywrightFleet(cookies_dir=os.path.join("backend", "cookies"))
