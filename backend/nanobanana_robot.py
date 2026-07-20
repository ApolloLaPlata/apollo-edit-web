import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("NanoBananaRobot")
logger.setLevel(logging.INFO)

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class NanoBananaFleet:
    """
    Exército Robótico para geração de imagens via NanoBanana/Flux no HuggingFace.
    """
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.cookies_dir = os.path.join(os.path.dirname(__file__), 'cookies')
        os.makedirs(self.cookies_dir, exist_ok=True)

    async def start_fleet(self):
        if not PLAYWRIGHT_AVAILABLE:
            return
        if not self.playwright:
            self.playwright = await async_playwright().start()
            # Inicia em modo Headless (invisível) para produção, ou False para debug
            self.browser = await self.playwright.chromium.launch(headless=True)
            logger.info("[NanoBanana Fleet] Navegador Chromium base iniciado.")

    async def load_account(self, account_id: str):
        """Carrega a sessão salva para evitar login manual no HuggingFace."""
        if not self.browser:
            await self.start_fleet()
            
        if account_id in self.contexts:
            return # Já está carregada na memória
            
        cookie_path = os.path.join(self.cookies_dir, f"{account_id}_hf_cookies.json")
        
        # Cria contexto anônimo
        context = await self.browser.new_context()
        
        if os.path.exists(cookie_path):
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                await context.add_cookies(cookies)
            logger.info(f"[{account_id}] Cookies do HuggingFace injetados com sucesso.")
        else:
            logger.warning(f"[{account_id}] Arquivo de cookies não encontrado: {cookie_path}. O Robô pode ser bloqueado.")

        page = await context.new_page()
        
        # Oculta propriedades de automação (Stealth Mode básico)
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.contexts[account_id] = context
        self.pages[account_id] = page

    async def generate_image(self, account_id: str, prompt: str) -> Dict[str, Any]:
        """Acessa a interface do HuggingFace/NanoBanana, digita o prompt e raspa a imagem."""
        if account_id not in self.pages:
            await self.load_account(account_id)
            
        page = self.pages[account_id]
        
        try:
            logger.info(f"[{account_id}] Acessando HuggingFace Space do NanoBanana (Flux)...")
            
            # URL ALVO (Pode mudar, o AI Mechanic irá monitorar isso futuramente)
            # Exemplo de URL fictícia baseada no Flow/HuggingFace
            target_url = "https://huggingface.co/spaces/black-forest-labs/FLUX.1-schnell" 
            
            await page.goto(target_url, wait_until="networkidle")
            
            # ------------------------------------------------------------------
            # ATENÇÃO: Os seletores abaixo são o calcanhar de aquiles do Web Scraping.
            # Se o HuggingFace mudar o layout, este robô quebra e o AI Mechanic entra em ação.
            # ------------------------------------------------------------------
            
            # 1. Encontra a caixa de texto
            # Note que em Spaces Gradio as iframes complicam, assumindo acesso direto aos elementos do Gradio
            text_box_selector = 'textarea[data-testid="textbox"]'
            
            # Espera a caixa carregar
            await page.wait_for_selector(text_box_selector, timeout=15000)
            
            # Limpa e digita o prompt
            await page.fill(text_box_selector, prompt)
            
            # 2. Clica no botão gerar
            generate_btn_selector = 'button:has-text("Generate")'
            await page.click(generate_btn_selector)
            
            logger.info(f"[{account_id}] Prompt enviado: '{prompt}'. Aguardando processamento da GPU gratuita...")
            
            # 3. Espera a imagem aparecer
            # Isso pode levar 5 a 20 segundos dependendo da fila do HuggingFace
            image_selector = 'img[data-testid="image"]'
            await page.wait_for_selector(image_selector, timeout=45000) # 45s de limite
            
            # 4. Raspa a URL da imagem (ou o base64)
            image_element = await page.query_selector(image_selector)
            img_url = await image_element.get_attribute("src")
            
            logger.info(f"[{account_id}] Imagem capturada com sucesso!")
            
            return {
                "status": "success",
                "image_url": img_url,
                "note": "Gerado via NanoBanana Fleet (HuggingFace Spaces)"
            }

        except Exception as e:
            logger.error(f"[{account_id}] Falha ao gerar imagem no NanoBanana: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def shutdown(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
nanobanana_fleet_commander = NanoBananaFleet()
