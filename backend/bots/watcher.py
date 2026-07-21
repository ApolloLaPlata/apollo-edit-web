import urllib.request
import urllib.parse
import re
import json
import random

def buscar_pautas_recentes(niche):
    """
    Motor de captura de tendências herdeiro do Apollo Edit Web.
    Realiza scraping da API interna (ytInitialData) do YouTube
    para encontrar os tópicos mais quentes das últimas horas/dias.
    """
    print(f"[WATCHER] Acordando... Caçando pautas quentes para o nicho: {niche} no YouTube...")
    
    # Adicionamos "noticias" ou "urgente" para filtrar conteúdo mais voltado para blogs
    query = f"{niche} noticias hoje"
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
        
        match = re.search(r'var ytInitialData = (\{.*?\});<\/script>', html)
        if not match:
            print("[WATCHER] [ERRO] Falha ao ler ytInitialData")
            return _fallback_pauta(niche)
            
        data = json.loads(match.group(1))
        videos = []
        
        contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
        
        if contents:
            items = contents[0].get('itemSectionRenderer', {}).get('contents', [])
            for item in items:
                if 'videoRenderer' in item:
                    v = item['videoRenderer']
                    try:
                        title = v['title']['runs'][0]['text']
                        ago = v.get('publishedTimeText', {}).get('simpleText', '')
                        
                        # Filtramos apenas coisas recentes (horas ou dias recentes)
                        if ago:
                            ago_str = ago.lower()
                            if 'hour' in ago_str or 'hora' in ago_str or 'day' in ago_str or 'dia' in ago_str or 'minuto' in ago_str:
                                videos.append({
                                    "title": title,
                                    "source": f"YouTube (Há {ago})"
                                })
                    except Exception:
                        continue
        
        if videos:
            # Pega um dos 5 primeiros para ter variedade
            pauta_escolhida = random.choice(videos[:5])
            print(f"[WATCHER] [ OK ] Pauta de Ouro Encontrada: '{pauta_escolhida['title']}'")
            return [pauta_escolhida]
        else:
            print("[WATCHER] [AVISO] Nenhum vídeo super recente encontrado, usando fallback.")
            return _fallback_pauta(niche)
            
    except Exception as e:
        print(f"[WATCHER] [ERRO] Falha no scraper: {e}")
        return _fallback_pauta(niche)

def _fallback_pauta(niche):
    return [{"title": f"As novas tendências do mercado de {niche} para este mês", "source": "Fallback AI"}]
