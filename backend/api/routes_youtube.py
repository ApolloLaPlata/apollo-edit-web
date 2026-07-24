from fastapi import APIRouter, Query, HTTPException
import urllib.request
import urllib.parse
import re
import json

router = APIRouter()

@router.get("/api/search-youtube")
async def search_youtube(q: str = Query(..., description="Termo de busca")):
    query = q
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'})
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8')
        
        match = re.search(r'var ytInitialData = (\{.*?\});<\/script>', html)
        if not match:
            raise HTTPException(status_code=500, detail="Falha ao ler ytInitialData")
            
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
                        video_id = v['videoId']
                        thumbnails = v.get('thumbnail', {}).get('thumbnails', [])
                        thumbnail = thumbnails[-1]['url'] if thumbnails else ""
                        author = v.get('ownerText', {}).get('runs', [{}])[0].get('text', 'Desconhecido')
                        views = v.get('viewCountText', {}).get('simpleText', '0')
                        duration = v.get('lengthText', {}).get('simpleText', '0:00')
                        
                        videos.append({
                            "id": video_id,
                            "videoId": video_id,
                            "title": title,
                            "thumbnail": thumbnail,
                            "author": author,
                            "channelTitle": author,
                            "views": views,
                            "viewCount": views,
                            "duration": duration
                        })
                    except Exception:
                        continue
                        
        return {"videos": videos}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
