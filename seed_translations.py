import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
I18N_DIR = os.path.join(BASE_DIR, "web_ui", "i18n")

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def seed():
    with open(os.path.join(I18N_DIR, 'pt.json'), 'r', encoding='utf-8') as f:
        pt_data = flatten_dict(json.load(f))
        
    with open(os.path.join(I18N_DIR, 'en.json'), 'r', encoding='utf-8') as f:
        en_data = flatten_dict(json.load(f))
        
    with open(os.path.join(I18N_DIR, 'es.json'), 'r', encoding='utf-8') as f:
        es_data = flatten_dict(json.load(f))
        
    db = {"en": {}, "es": {}}
    
    # Check if existing DB
    db_path = os.path.join(I18N_DIR, "translations_db.json")
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
            
    for key, pt_str in pt_data.items():
        if key in en_data:
            db["en"][pt_str] = en_data[key]
        if key in es_data:
            db["es"][pt_str] = es_data[key]
            
    # Add manual static mappings since some buttons like "COMPRAR POR 80 CRISTAIS" might not map perfectly due to spacing
    db["en"]["💎 COMPRAR POR 80 CRISTAIS"] = "💎 BUY FOR 80 CRYSTALS"
    db["es"]["💎 COMPRAR POR 80 CRISTAIS"] = "💎 COMPRAR POR 80 CRISTALES"
    
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
        
    print("Banco populado com JSONs!")

if __name__ == "__main__":
    seed()
