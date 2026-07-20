import os
import time
import shutil
import subprocess
import requests
import random
import json
import uuid
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, List, Dict

# =========================================================================
# ⚙️ CHAVE MESTRE DE AUTOMAÇÃO DE IP (VPN)
# =========================================================================
# False: Modo Produtividade (Emite apenas bip e aguarda o seu clique no mouse)
# True:  Modo Madrugada (Assume o mouse do PC, foca na tela do VPN e clica sozinho)
MODO_MADRUGADA = False  
# =========================================================================


# Foram removidos o GerenciadorTor e GerenciadorProxy por decisão do usuário, 
# para focar exclusivamente na automação via VPN.


# ─────────────────────────────────────────────────────────────
# GERENCIADOR VPN (ProtonVPN automático)
# ─────────────────────────────────────────────────────────────

class GerenciadorVPN:
    """
    Controla o ProtonVPN automaticamente para rotação de IP.
    Usa o CLI do ProtonVPN (protonvpn-cli ou o executável do app Windows).
    Detecta automaticamente o caminho de instalação.
    """
    # Caminhos possíveis do executável ProtonVPN no Windows
    CAMINHOS_PROTON = [
        r"C:\Program Files\Proton\VPN\ProtonVPN.exe",
        r"C:\Program Files\Proton\VPN\ProtonVPN.Launcher.exe",
        r"C:\Program Files (x86)\Proton\VPN\ProtonVPN.exe",
        r"C:\Program Files (x86)\Proton\VPN\ProtonVPN.Launcher.exe",
        r"C:\Program Files\Proton VPN\ProtonVPN.exe",
        r"C:\Program Files (x86)\Proton VPN\ProtonVPN.exe",
        # Caminhos de instalação "por usuário" (AppData)
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"ProtonVPN\ProtonVPN.exe"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Proton\VPN\ProtonVPN.exe"),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Proton\VPN\ProtonVPN.Launcher.exe"),
    ]

    def __init__(self, config_manager=None):
        self.config = config_manager
        self._proton_exe: Optional[str] = None
        self._proton_cli_disponivel: Optional[bool] = None
        self._ip_anterior: str = ""

    # ----- Detecção -----

    def _encontrar_proton_exe(self) -> Optional[str]:
        """Localiza o executável do ProtonVPN."""
        import shutil
        
        # 1. Tenta primeiro o caminho customizado no config.json
        if self.config and hasattr(self.config, "get"):
            caminho_cfg = self.config.get("automacao_vpn.caminho_proton_exe", "")
            if caminho_cfg and os.path.exists(caminho_cfg):
                print(f"✅ [VPN] Usando caminho do config.json: {caminho_cfg}")
                return caminho_cfg

        # 2. Tenta no PATH do sistema
        cli = shutil.which("protonvpn-cli") or shutil.which("ProtonVPN")
        if cli:
            print(f"✅ [VPN] ProtonVPN encontrado no PATH: {cli}")
            return cli

        # 3. Busca nos caminhos padrão conhecidos
        print(f"🔍 [VPN] Procurando ProtonVPN em caminhos padrão...")
        for caminho in self.CAMINHOS_PROTON:
            if caminho and os.path.exists(caminho):
                print(f"✅ [VPN] Encontrado em: {caminho}")
                return caminho
        
        # Log de falha detalhado
        print("❌ [VPN] ProtonVPN não encontrado nos locais padrão:")
        for c in self.CAMINHOS_PROTON: print(f"   - {c}")
        return None

    def esta_disponivel(self) -> bool:
        """Verifica se o ProtonVPN está instalado e pode ser controlado."""
        if self._proton_exe is None:
            self._proton_exe = self._encontrar_proton_exe()
        return self._proton_exe is not None

    # ----- Controle -----

    def _executar(self, *args, timeout: int = 15) -> bool:
        """Executa um comando ProtonVPN e retorna True se bem-sucedido."""
        try:
            cmd = [self._proton_exe] + list(args)
            print(f"🔧 [VPN] Executando: {' '.join(cmd)}")
            result = subprocess.run(cmd, timeout=timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            saida = (result.stdout + result.stderr).decode("utf-8", errors="replace")
            if saida.strip():
                print(f"   ↳ {saida.strip()[:200]}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("⚠️ [VPN] Comando expirou.")
            return False
        except Exception as e:
            print(f"⚠️ [VPN] Erro ao executar comando: {e}")
            return False

    def _obter_ip(self) -> str:
        try:
            return requests.get("https://api.ipify.org", timeout=6).text.strip()
        except Exception:
            return ""

    def desconectar(self) -> bool:
        pass # Removido a pedido do usuário (Modo Semi-Automático)

    def conectar_rapido(self) -> bool:
        pass # Removido a pedido do usuário (Modo Semi-Automático)

    def tocar_alarme_bloqueio(self):
        """Emite uma sequência de beeps usando biblioteca nativa do Windows para alertar sobre o bloqueio."""
        import winsound
        try:
            for _ in range(3):
                winsound.Beep(1000, 500) # Frequência 1000Hz por 500ms
                time.sleep(0.1)
        except Exception:
            pass

    def executar_macro_madrugada(self) -> bool:
        """Automação absoluta: Foca na janela do VPN e clica fisicamente usando o mouse via PyAutoGUI."""
        print("🤖 [VPN] MODO MADRUGADA: Assumindo o controle do Mouse para clicar na Janela...")
        import sys
        import subprocess
        
        # Script isolado para proteger de erros COM e fazer a mágica mecânica
        script_isolado = f'''
import sys
import time
import subprocess

try:
    import pyautogui
    import pygetwindow as gw
except ImportError:
    print("📦 [VPN] Instalando dependências de Macro (pyautogui e pygetwindow)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui", "pygetwindow", "pyscreeze", "Pillow"])
    import pyautogui
    import pygetwindow as gw

try:
    # 1. Pesquisa por janelas com Proton VPN ou Urban VPN
    alvos = gw.getWindowsWithTitle("Proton VPN") + gw.getWindowsWithTitle("Urban VPN")
    if not alvos:
        print("FALHA_JANELA_NAO_ENCONTRADA")
        sys.exit(0)
        
    win = alvos[0]
    
    # 2. Traz a janela para frente para que o clique não seja bloqueado
    try:
        if win.isMinimized:
            win.restore()
        win.activate()
    except Exception:
        # Método alternativo forçado para focar janela no Windows
        win.minimize()
        win.restore()
        
    time.sleep(1.5) # Dá tempo pro Windows renderizar a tela na nossa frente
    
    # 3. Matemática de Coordenadas (Ajuste fino guiado pelas imagens do usuário)
    # rel_x = 0.48: Pega a metade esquerda da tela do Mapa (Pega o 'Alterar servidor' E o 'Conectar').
    # rel_y = 0.28: Desce um pouco para não clicar no 'Conexões Gratuitas' e bate na quina do botão. (A pedido do usuário, esta é a métrica final)
    rel_x = int(win.width * 0.48)
    rel_y = int(win.height * 0.28)
    
    abs_x = win.left + rel_x
    abs_y = win.top + rel_y
    
    # Executa o salto fantasma do Mouse e clica
    # Failsafe aborta se o usuário brigar empurrando o mouse pro canto esquerdo da tela
    pyautogui.FAILSAFE = True  
    pyautogui.moveTo(abs_x, abs_y, duration=0.3)
    pyautogui.click()
    
    print("CLIQUE_MACRO_SUCESSO")
except Exception as e:
    print(f"ERRO_MACRO: {{e}}")
'''
        try:
            resultado = subprocess.run(
                [sys.executable, "-c", script_isolado],
                capture_output=True, text=True, timeout=15
            )
            saida = resultado.stdout.strip()
            
            if "CLIQUE_MACRO_SUCESSO" in saida:
                print("✅ [VPN] Mouse acionado fisicamente e botão clicado!")
                return True
            else:
                print(f"❌ [VPN] O Macro falhou com a resposta: {saida}")
                return False
        except Exception as e:
            print(f"❌ [VPN] Ocorreu um erro letal no subprocesso do PyAutoGUI: {e}")
            return False

    def trocar_servidor(self) -> bool:
        """
        Desconecta e reconecta ao servidor mais rápido disponível.
        Verifica se o IP realmente mudou.
        Retorna True se conseguiu trocar o IP.
        """
        if not self.esta_disponivel():
            print("❌ [VPN] ProtonVPN não encontrado. Instale em: https://protonvpn.com/download")
            return False

        ip_antes = self._obter_ip()
        print(f"🌐 [VPN] IP atual antes da troca: {ip_antes}")

        # Desconecta e reconecta
        self.desconectar()
        time.sleep(3)
        self.conectar_rapido()

        # Aguarda novo IP (máx 20s)
        print("⏳ [VPN] Aguardando novo IP...")
        for _ in range(20):
            time.sleep(1)
            ip_depois = self._obter_ip()
            if ip_depois and ip_depois != ip_antes:
                print(f"✅ [VPN] IP trocado com sucesso: {ip_antes} → {ip_depois}")
                return True

        ip_depois = self._obter_ip()
        if ip_depois != ip_antes:
            print(f"✅ [VPN] IP trocado: {ip_antes} → {ip_depois}")
            return True
        else:
            print(f"⚠️ [VPN] IP não mudou após troca ({ip_depois}). Talvez o mesmo servidor foi selecionado.")
            return False


# ─────────────────────────────────────────────────────────────
# PROVEDOR PRINCIPAL
# ─────────────────────────────────────────────────────────────

class OpenAIFMProvider:
    """Provedor de Síntese TTS utilizando o OpenAI.fm de forma gratuita via Selenium.
    Inclui rotação automática de proxies para contornar limites de IP."""
    
    def __init__(self, config_manager=None):
        self.config = config_manager
        self.vpn = GerenciadorVPN(config_manager=config_manager)
        self.proxy_ativo = None  # Mantido por compatibilidade de assinatura, mas não usamos proxy no Chrome, a VPN faz a troca pro SO inteiro.
        self._usando_vpn = False  # True quando VPN foi ativada para bypass
        
    def _configurar_navegador(self, pasta_download: str, proxy: Optional[str] = None):
        """Configura o navegador Chrome com opções anti-detecção, diretório customizado e proxy opcional."""
        import tempfile
        import sys
        import subprocess
        
        try:
            import undetected_chromedriver as uc
        except ImportError:
            print("📦 Instalando 'undetected-chromedriver' para burlar detecção do Cloudflare...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "undetected-chromedriver"])
            import undetected_chromedriver as uc

        options = uc.ChromeOptions()
        
        # Perfil isolado para garantir preferências limpas de download
        perfil_temp = tempfile.mkdtemp(prefix="chrome_openai_fm_")
        options.add_argument(f"--user-data-dir={perfil_temp}")
        
        # Configurar proxy se fornecido
        if proxy:
            if proxy.startswith("socks"):
                options.add_argument(f"--proxy-server={proxy}")
                print(f"🧅 [Modo 4] Via Tor: {proxy}")
            else:
                options.add_argument(f"--proxy-server=http://{proxy}")
                print(f"🔀 [Modo 4] Via proxy HTTP: {proxy}")
        
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "download.default_directory": pasta_download,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "savefile.default_directory": pasta_download,
            "safebrowsing.enabled": True,
            "safebrowsing.disable_download_protection": True
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--window-size=1280,720")
        
        # Iniciar o UC Driver (undetected) com o binário correto da versão do Chrome do sistema
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        try:
            driver = uc.Chrome(options=options, headless=False, driver_executable_path=driver_path)
        except Exception as e:
            # Em caso de falha severa do UC, tenta forçar versão ou usa nativo (Fallback raro)
            print(f"⚠️ [Modo 4] Falha inicial do Undetected Chromedriver: {e}. Tentando inicialização alternativa...")
            driver = uc.Chrome(options=options, headless=False)
            
        # Forçar pasta de download via CDP
        try:
            driver.execute_cdp_cmd('Browser.setDownloadBehavior', {
                'behavior': 'allow',
                'downloadPath': pasta_download
            })
        except Exception:
            pass
        
        return driver

    def _checar_limite_ip(self, driver) -> bool:
        """Verifica se o modal de 'Download limit reached' apareceu na página."""
        try:
            texto_pagina = driver.find_element(By.TAG_NAME, "body").text
            return "Download limit reached" in texto_pagina or "download limit" in texto_pagina.lower()
        except Exception:
            return False

    def _fechar_modal_limite(self, driver):
        """Fecha o modal de limite se estiver aberto."""
        try:
            btn_ok = driver.find_element(By.XPATH, "//button[text()='Okay' or text()='OK' or text()='ok']")
            btn_ok.click()
            time.sleep(0.5)
        except Exception:
            pass

    def _selecionar_voz(self, driver, voz_nome: str) -> bool:
        """Procura e clica no card da voz escolhida."""
        try:
            print(f"🔍 [Modo 4] Procurando voz: {voz_nome}")
            time.sleep(2)
            
            voice_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='button']"))
            )
            
            for card in voice_cards:
                try:
                    texto_card = card.text.lower()
                    if voz_nome.lower() in texto_card:
                        driver.execute_script("arguments[0].scrollIntoView(true);", card)
                        time.sleep(0.5)
                        card.click()
                        print(f"✅ [Modo 4] Voz selecionada: {voz_nome}")
                        time.sleep(1)
                        return True
                except Exception:
                    continue
            
            print(f"❌ [Modo 4] Voz '{voz_nome}' não encontrada na página.")
            return False
        except Exception as e:
            print(f"❌ [Modo 4] Erro ao selecionar voz: {e}")
            return False

    def _preencher_campo(self, driver, texto: str, is_script: bool) -> bool:
        """Preenche SCRIPT ou VIBE pelos IDs estáveis da página."""
        try:
            time.sleep(1)
            campo_id = "prompt" if is_script else "input"
            
            textarea = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, campo_id))
            )
            
            driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
            time.sleep(0.5)
            textarea.click()
            time.sleep(0.5)
            
            from selenium.webdriver.common.keys import Keys
            textarea.send_keys(Keys.CONTROL + "a")
            textarea.send_keys(Keys.DELETE)
            
            time.sleep(0.5)
            textarea.send_keys(texto[:2000])
            time.sleep(1)
            return True
        except Exception as e:
            tipo = "SCRIPT" if is_script else "VIBE"
            print(f"❌ [Modo 4] Erro ao preencher {tipo}: {e}")
            return False

    def _esperar_arquivos(self, pasta_download: str, arquivos_pre_existentes: set, timeout: int = 90) -> Optional[str]:
        """Aguarda um arquivo NOVO aparecer. Compara com snapshot pré-download para não pegar arquivos antigos."""
        import pathlib
        
        pastas_busca = [pasta_download]
        downloads_padrao = os.path.join(str(pathlib.Path.home()), 'Downloads')
        if os.path.abspath(downloads_padrao) != os.path.abspath(pasta_download):
            pastas_busca.append(downloads_padrao)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            for pasta in pastas_busca:
                if not os.path.exists(pasta):
                    continue
                for arquivo in sorted(os.listdir(pasta), key=lambda f: os.path.getmtime(os.path.join(pasta, f)), reverse=True):
                    if arquivo.startswith('openai-fm') and (arquivo.endswith('.mp3') or arquivo.endswith('.wav')) and not arquivo.endswith('.crdownload'):
                        caminho_completo = os.path.join(pasta, arquivo)
                        if caminho_completo in arquivos_pre_existentes:
                            continue
                        if os.path.exists(caminho_completo) and os.path.getsize(caminho_completo) > 1024:
                            print(f"📁 [Modo 4] NOVO arquivo detectado em: {pasta} -> {arquivo}")
                            return caminho_completo
            time.sleep(1)
        return None

    def _tentar_geracao(self, driver, voice_name: str, vibe_text: str, text: str,
                         download_dir: str, arquivos_pre_existentes: set) -> Optional[str]:
        """
        Tenta uma única geração no driver já aberto.
        Retorna o path do arquivo baixado, ou None se falhou/limite atingido.
        """
        # Step 1: Selecionar voz
        if not self._selecionar_voz(driver, voice_name):
            return None
        
        # Step 2: Preencher campos
        if not self._preencher_campo(driver, vibe_text, is_script=False):
            return None
        if not self._preencher_campo(driver, text, is_script=True):
            return None
        
        # Scroll down
        driver.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
        time.sleep(1)
        
        # Step 3: Encontrar botão de Download
        # Timeout alto pois o site precisa gerar o áudio no servidor antes de liberar o botão
        try:
            download_button = WebDriverWait(driver, 90).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='button' and .//span[text()='Download']]"))
            )
        except Exception:
            if self._checar_limite_ip(driver):
                print("🚫 [Modo 4] Limite de IP detectado antes do Download!")
                return "LIMITE_IP"
            print("❌ [Modo 4] Botão Download não encontrado (timeout).")
            return None
        
        if not download_button.is_displayed():
            if self._checar_limite_ip(driver):
                return "LIMITE_IP"
            return None
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
        time.sleep(1)
        
        # Tirar snapshot de arquivos existentes ANTES do clique
        import pathlib
        snapshot_atual = set()
        for pasta_scan in [download_dir, os.path.join(str(pathlib.Path.home()), 'Downloads')]:
            if os.path.exists(pasta_scan):
                for f in os.listdir(pasta_scan):
                    if f.startswith('openai-fm'):
                        snapshot_atual.add(os.path.join(pasta_scan, f))
        # Unir com snapshot inicial passado
        todos_pre_existentes = arquivos_pre_existentes | snapshot_atual
        
        # Clicar via JS
        driver.execute_script("arguments[0].click();", download_button)
        print("💾 [Modo 4] Download iniciado - aguardando síntese + salvamento...")
        
        # Aguardar 2 segundos e verificar modal de limite
        time.sleep(2)
        if self._checar_limite_ip(driver):
            print("🚫 [Modo 4] Limite de IP detectado após clicar Download!")
            self._fechar_modal_limite(driver)
            return "LIMITE_IP"
        
        # Esperar arquivo
        arquivo = self._esperar_arquivos(download_dir, todos_pre_existentes, timeout=90)
        return arquivo

    def generate_tts(self, text: str, voice_name: str, vibe_text: str, output_path: str, **kwargs) -> bool:
        """
        Orquestra a automação com rotação automática de proxy quando o limite de IP é atingido.
        Fluxo: Tenta sem proxy → detecta limite → busca proxies → rotaciona até conseguir.
        """
        if not voice_name:
            print("❌ [Modo 4] Nenhuma voz configurada para o personagem (OpenAI.fm)")
            return False

        import pathlib
        temp_dir = self.config.get_path("temp_dir") if self.config else "temp"
        download_dir = os.path.abspath(temp_dir)
        os.makedirs(download_dir, exist_ok=True)
        
        # Limpar arquivos openai-fm antigos em AMBAS as pastas
        downloads_padrao = os.path.join(str(pathlib.Path.home()), 'Downloads')
        for pasta_limpeza in [download_dir, downloads_padrao]:
            if not os.path.exists(pasta_limpeza): continue
            for arquivo in os.listdir(pasta_limpeza):
                if arquivo.startswith('openai-fm') and (arquivo.endswith('.mp3') or arquivo.endswith('.wav')):
                    try: os.remove(os.path.join(pasta_limpeza, arquivo))
                    except: pass

        # Snapshot inicial (após limpeza) para referência
        arquivos_pre_existentes = set()
        for pasta_scan in [download_dir, downloads_padrao]:
            if os.path.exists(pasta_scan):
                for f in os.listdir(pasta_scan):
                    if f.startswith('openai-fm'):
                        arquivos_pre_existentes.add(os.path.join(pasta_scan, f))

        MAX_TENTATIVAS_PROXY = 6
        # Retoma o proxy já ativo da sessão (sticky proxy entre gerações)
        proxy_atual = self.proxy_ativo
        if proxy_atual:
            print(f"🔀 [Modo 4] Retomando proxy ativo da sessão: {proxy_atual}")
        else:
            print(f"🌐 [Modo 4] Inicializando com IP direto")
        
        for tentativa in range(MAX_TENTATIVAS_PROXY + 1):
            driver = None
            try:
                label_ip = f"proxy: {proxy_atual}" if proxy_atual else "IP direto"
                print(f"🌐 [Modo 4] Tentativa {tentativa+1}/{MAX_TENTATIVAS_PROXY+1} | {voice_name} | {label_ip}")
                    
                driver = self._configurar_navegador(download_dir, proxy=proxy_atual)
                driver.get("https://www.openai.fm/")
                time.sleep(2)
                
                # Verificar limite já na abertura da página
                if self._checar_limite_ip(driver):
                    print("🚫 [Modo 4] Limite detectado logo na abertura! Trocando IP via VPN...")
                    self.proxy_ativo = None  # Limpa proxy ativo pois está bloqueado
                    driver.quit()
                    driver = None
                    proxy_atual = self._obter_proximo_proxy()
                    if proxy_atual is None:
                        print("❌ [Modo 4] Sem mais proxies disponíveis.")
                        return False
                    continue
                
                # Tentar gerar
                resultado = self._tentar_geracao(
                    driver, voice_name, vibe_text, text,
                    download_dir, arquivos_pre_existentes
                )
                
                if resultado == "LIMITE_IP":
                    print("🚫 [Modo 4] Limite de IP detectado! Solicitando troca via VPN...")
                    self.proxy_ativo = None
                    driver.quit()
                    driver = None
                    self._obter_proximo_proxy()  # Aciona a troca de VPN
                    if not self._usando_vpn:
                        print("❌ [Modo 4] Sem VPN disponível. Falha total.")
                        return False
                    continue
                
                if resultado and os.path.exists(resultado) and os.path.getsize(resultado) > 1024:
                    # SUCESSO - Persistir proxy que funcionou para próximas gerações da sessão
                    self.proxy_ativo = proxy_atual
                    if proxy_atual:
                        print(f"✅ [Modo 4] Proxy {proxy_atual} funcionou! Mantendo para próximas gerações.")
                    return self._converter_e_salvar(resultado, output_path)
                
                print(f"❌ [Modo 4] Tentativa {tentativa+1} falhou (arquivo não encontrado).")  
                if driver:
                    driver.quit()
                    driver = None
                self.proxy_ativo = None
                self._obter_proximo_proxy()
                if not self._usando_vpn:
                    print("❌ [Modo 4] Sem VPN disponível para nova tentativa. Abortando.")
                    return False
                    
            except Exception as e:
                print(f"❌ [Modo 4] Exceção na tentativa {tentativa+1}: {e}")
                self.proxy_ativo = None
                self._obter_proximo_proxy()
                if not self._usando_vpn:
                    import traceback; traceback.print_exc()
                    return False
            finally:
                if driver:
                    try: driver.quit()
                    except: pass
        
        print("❌ [Modo 4] Todas as tentativas com proxy esgotadas.")
        return False

    def _obter_proximo_proxy(self) -> Optional[str]:
        """
        Estratégia Exclusiva de Bypass Híbrida:
        Lê a variável do config.json (Controlada pela interface).
        Se ativada, puxa a macro que controla o mouse.
        Se desativada, toca o Bip aguardando o usuário.
        """
        # Puxando pelo ConfigManager nativo do app para termos certeza de não pegar path errado
        modo_madrugada_painel = False
        try:
            from config_manager import ConfigManager
            cfg = ConfigManager()
            modo_madrugada_painel = cfg.get("modo_madrugada", False)
        except Exception as e:
            print(f"❌ [DEBUG] Erro ao ler ConfigManager: {e}")
            modo_madrugada_painel = False
            
        ip_antigo = self.vpn._obter_ip()
        
        print("\n" + "="*50)
        print("⏳ [VPN] LIMITE DE IP DETECTADO NO OPENAI.FM!")
        print(f"🌐 SO/IP Atual: {ip_antigo}")
        
        if modo_madrugada_painel:
            if self.vpn.esta_disponivel():
                sucesso = self.vpn.executar_macro_madrugada()
                if not sucesso:
                    print("🔊 [VPN] Macro falhou! Tocando alarme de emergência, mude manualmente!")
                    self.vpn.tocar_alarme_bloqueio()
            else:
                self.vpn.tocar_alarme_bloqueio()
        else:
            # Dispara o Alarme Sonoro do Windows para alertar o usuário a clicar no VPN 
            if self.vpn.esta_disponivel():
                print("🔊 [VPN] Modo Produtividade (AFK Off). POR FAVOR, dê 1 clique no VPN agora.")
                self.vpn.tocar_alarme_bloqueio()
            else:
                print("🔊 [VPN] Tocando alarme! Troque seu IP!")
                self.vpn.tocar_alarme_bloqueio()
        
        # 2. Loop inteligente de espera (aguarda a troca de IP efetivar)
        tentativas_espera = 60 # 60 * 5 seg = 5 minutos de paciência extra
        for i in range(tentativas_espera):
            ip_atual = self.vpn._obter_ip()
            if ip_atual and ip_atual != ip_antigo and ip_atual != "":
                print(f"\n✅ [VPN] MUDANÇA DE IP DETECTADA COM SUCESSO!")
                print(f"🌐 NOVO IP: {ip_atual}")
                print("🚀 Retomando a geração imediatamente...")
                self._usando_vpn = True
                return None # Chrome assume a rede nativa e continua
            
            # Printa uma bolinha a cada 5 segundos pro usuário saber que o script não travou
            print(".", end="", flush=True)
            time.sleep(5)
            
        print("\n❌ [VPN] Tempo limite esgotado esperando a troca de IP.")
        self._usando_vpn = False
        return None

    def _converter_e_salvar(self, arquivo_baixado: str, output_path: str) -> bool:
        """Converte o arquivo baixado para o formato destino via FFmpeg."""
        if output_path.endswith('.wav'):
            cmd = ['ffmpeg', '-y', '-i', arquivo_baixado, '-acodec', 'pcm_s16le', '-ar', '44100', output_path]
        else:
            if not output_path.endswith('.mp3'):
                output_path = output_path.rsplit('.', 1)[0] + '.mp3'
            cmd = ['ffmpeg', '-y', '-i', arquivo_baixado, '-b:a', '192k', output_path]
            
        print(f"🔄 [Modo 4] Convertendo {os.path.basename(arquivo_baixado)} -> {os.path.basename(output_path)}...")
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ [Modo 4] Êxito! Áudio salvo em: {output_path}")
            try: os.remove(arquivo_baixado)
            except: pass
            return True
        else:
            print("❌ [Modo 4] Falha no FFmpeg ao realizar conversão.")
            return False
