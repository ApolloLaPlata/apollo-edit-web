import os
import glob
import json
import time
import shutil
from bs4 import BeautifulSoup, NavigableString

# Config paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_UI_DIR = os.path.join(BASE_DIR, "web_ui")
I18N_DIR = os.path.join(WEB_UI_DIR, "i18n")
LANGUAGES = ["en", "es", "zh", "ja", "ru"]

def is_valid_text(text):
    text = text.strip()
    if not text:
        return False
    if len(text) < 2:
        return False
    # Check if it has letters
    if not any(c.isalpha() for c in text):
        return False
    # Ignore pure numbers or simple punctuation
    return True

def extract_strings_from_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    strings = set()
    for element in soup.find_all(string=True):
        if element.parent.name in ['script', 'style', 'code', 'pre']:
            continue
        text = element.strip()
        if is_valid_text(text):
            # Limpar um pouco as quebras de linha excessivas
            text = " ".join(text.split())
            strings.add(text)
    return strings, soup

def translate_batch_gemini(texts, target_lang):
    """
    Usa a API do Gemini local para traduzir um lote de textos.
    """
    # Importar o Gemini dinamicamente
    import sys
    sys.path.append(BASE_DIR)
    from config_manager import ConfigManager
    from gemini_api import GeminiAPI
    
    cm = ConfigManager(os.path.join(BASE_DIR, "config.json"))
    gemini = GeminiAPI(cm)
    
    if not gemini.api_key:
        print("⚠️ Gemini API Key não configurada. Usando fallback de cópia original.")
        return {t: t for t in texts}
        
    lang_map = {"en": "English", "es": "Spanish", "zh": "Chinese (Simplified)", "ja": "Japanese"}
    lang_name = lang_map.get(target_lang, "English")
    
    # Prepara o JSON de entrada
    input_dict = {str(i): text for i, text in enumerate(texts)}
    
    system_prompt = f"""You are a professional translator for a Video Editing Web Application called Apollo Edit.
Translate the following JSON string values from Portuguese to {lang_name}.
Preserve exactly the same meaning, keep it concise for UI elements.
CRITICAL: Return ONLY a valid JSON object matching the exact keys provided, with the translated values."""

    prompt = f"Translate to {lang_name}:\n```json\n" + json.dumps(input_dict, ensure_ascii=False, indent=2) + "\n```"
    
    result = gemini.generate_content(prompt, system_prompt)
    if not result:
        return None
        
    try:
        # Extrair JSON do markdown se necessário
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
            
        translated_dict = json.loads(result.strip())
        
        # Mapear de volta para os textos originais
        final_map = {}
        for i, text in enumerate(texts):
            final_map[text] = translated_dict.get(str(i), text)
        return final_map
        
    except Exception as e:
        print(f"❌ Erro ao parsear JSON do Gemini para {target_lang}: {e}")
        return None

def build_static_site():
    print("🚀 Iniciando Apollo SSG (Static Site Generator) para I18N...")
    
    db_path = os.path.join(I18N_DIR, "translations_db.json")
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            translations_db = json.load(f)
    else:
        translations_db = {"en": {}, "es": {}}
        
    # 1. Coletar todas as strings de todos os arquivos HTML
    html_files = [f for f in glob.glob(os.path.join(WEB_UI_DIR, "*.html"))]
    all_strings = set()
    html_soups = {}
    
    print(f"📁 Encontrados {len(html_files)} arquivos HTML.")
    
    for html_file in html_files:
        strings, soup = extract_strings_from_html(html_file)
        all_strings.update(strings)
        html_soups[html_file] = soup
        
    print(f"📝 Total de {len(all_strings)} strings únicas identificadas para tradução.")
    
    # 2. Traduzir strings faltantes para cada idioma
    for lang in LANGUAGES:
        if lang not in translations_db:
            translations_db[lang] = {}
            
        missing_texts = [t for t in all_strings if t not in translations_db[lang]]
        
        if missing_texts:
            print(f"🌐 Traduzindo {len(missing_texts)} strings para [{lang}] usando Gemini...")
            
            # Dividir em lotes de 50 para não estourar o limite de tokens
            batch_size = 50
            for i in range(0, len(missing_texts), batch_size):
                batch = missing_texts[i:i+batch_size]
                print(f"   -> Processando lote {i//batch_size + 1}/{(len(missing_texts)+batch_size-1)//batch_size}...")
                
                while True:
                    translated_batch = translate_batch_gemini(batch, lang)
                    if translated_batch is not None:
                        break
                    print("⚠️ Tradução falhou (possível Rate Limit). Aguardando 10 segundos antes de tentar novamente...")
                    time.sleep(10)
                
                # Atualizar o DB em memória
                for orig_text, trans_text in translated_batch.items():
                    translations_db[lang][orig_text] = trans_text
                
                # Salvar progresso
                with open(db_path, 'w', encoding='utf-8') as f:
                    json.dump(translations_db, f, ensure_ascii=False, indent=4)
                
                time.sleep(5) # Rate limit: 15 RPM (um a cada 4s no mínimo)
    
    print("✅ Banco de traduções atualizado!")
    
    # 3. Gerar os HTMLs traduzidos e salvar nas pastas
    for lang in LANGUAGES:
        out_dir = os.path.join(WEB_UI_DIR, lang)
        os.makedirs(out_dir, exist_ok=True)
        
        for html_file, soup in html_soups.items():
            filename = os.path.basename(html_file)
            
            # Criar uma cópia isolada da árvore DOM para não modificar o soup original
            soup_copy = BeautifulSoup(str(soup), 'html.parser')
            
            # Traduzir textos nativamente
            for element in soup_copy.find_all(string=True):
                if element.parent.name in ['script', 'style', 'code', 'pre']:
                    continue
                text = element.strip()
                if is_valid_text(text):
                    clean_text = " ".join(text.split())
                    translated_text = translations_db[lang].get(clean_text, text)
                    # Mantém o texto traduzido preservando espaços ao redor, se houver
                    new_string = element.replace(text, translated_text)
                    element.replace_with(new_string)
            
            # Ajustar links de iframe (ex: YouTube)
            for iframe in soup_copy.find_all('iframe'):
                if iframe.has_attr('src'):
                    src = iframe['src']
                    translated_src = translations_db[lang].get(src, src)
                    if translated_src != src:
                        iframe['src'] = translated_src

            # Ajustar caminhos de vídeo mp4
            for video in soup_copy.find_all('video'):
                if video.has_attr('src'):
                    src = video['src']
                    translated_src = translations_db[lang].get(src, src)
                    if translated_src != src:
                        video['src'] = translated_src
                    elif '.mp4' in src:
                        base, ext = os.path.splitext(src)
                        if not base.endswith(f"_{lang}"):
                            video['src'] = f"{base}_{lang}{ext}"
                            
            # Ajustar scripts para carregar a partir do diretório raiz
            for script in soup_copy.find_all('script'):
                if script.has_attr('src'):
                    src = script['src']
                    if not src.startswith('http') and not src.startswith('/'):
                        # Ajusta os imports para ../
                        script['src'] = f"../{src}"
                        
            # Ajustar CSS links
            for link in soup_copy.find_all('link'):
                if link.has_attr('href') and link['rel'] == ['stylesheet']:
                    href = link['href']
                    if not href.startswith('http') and not href.startswith('/'):
                        link['href'] = f"../{href}"
                        
            # Ajustar links href
            for a in soup_copy.find_all('a'):
                if a.has_attr('href'):
                    href = a['href']
                    if href.endswith('.html') and not href.startswith('http') and not href.startswith('/'):
                        # O link no HTML da pasta EN continua apontando para o arquivo HTML da pasta EN.
                        # Ex: 'hub.html' permanece 'hub.html', e o browser vai pra `/en/hub.html`
                        pass

            # Ajustar caminhos de img
            for img in soup_copy.find_all('img'):
                if img.has_attr('src'):
                    src = img['src']
                    if not src.startswith('http') and not src.startswith('data:') and not src.startswith('/'):
                        img['src'] = f"../{src}"
            
            # Salvar
            out_file = os.path.join(out_dir, filename)
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(str(soup_copy))
                
        print(f"🎉 Geração de HTMLs finalizada para o idioma: {lang}")

if __name__ == "__main__":
    build_static_site()
