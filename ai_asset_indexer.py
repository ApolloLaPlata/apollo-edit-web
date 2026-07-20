import os
import json
import re

TARGET_DIRS = [
    r"H:\CINE PACK",
    r"H:\MEUS EFEITOS",
    r"H:\PACK DE EDIÇÃO",
    r"H:\PACK DE EFEITOS - Assets Pack"
]

VIDEO_EXT = {'.mp4', '.mov', '.webm', '.avi'}
AUDIO_EXT = {'.mp3', '.wav', '.aac', '.m4a'}

def generate_tags(file_name, file_path):
    # Remove extension
    name_no_ext = os.path.splitext(file_name)[0]
    
    # Tokenize the name and path by non-alphanumeric chars
    path_str = file_path.replace("\\", " ").replace("/", " ")
    combined = f"{name_no_ext} {path_str}".lower()
    
    words = re.findall(r'[a-z]+', combined)
    
    # Filter common useless words
    stopwords = {'h', 'cine', 'pack', 'de', 'edição', 'efeitos', 'assets', 'meus', 'copy', 'of', 'and', 'the'}
    tags = list(set([w for w in words if len(w) > 2 and w not in stopwords]))
    
    return tags

def index_assets():
    assets = {
        'video': [],
        'audio': []
    }
    
    for d in TARGET_DIRS:
        if not os.path.exists(d):
            print(f"Aviso: Diretório não encontrado: {d}")
            continue
            
        print(f"Varrendo: {d}")
        for root, dirs, files in os.walk(d):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                full_path = os.path.join(root, file)
                
                if ext in VIDEO_EXT:
                    assets['video'].append({
                        'name': file,
                        'path': full_path,
                        'tags': generate_tags(file, full_path)
                    })
                elif ext in AUDIO_EXT:
                    assets['audio'].append({
                        'name': file,
                        'path': full_path,
                        'tags': generate_tags(file, full_path)
                    })
                    
    # Save the output
    out_path = r"E:\MEUS PROGRAMAS\APOLLO_STUDIO\ai_assets.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)
        
    print(f"Indexação concluída! {len(assets['video'])} vídeos e {len(assets['audio'])} áudios mapeados.")
    print(f"Salvo em: {out_path}")

if __name__ == "__main__":
    index_assets()
