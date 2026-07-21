import sqlite3
import uuid
import datetime

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "frontend", "dev.db")

def init_seed():
    print("[SEED] Inicializando banco de dados com configurações padrão...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se já existe um blog
    cursor.execute("SELECT id FROM Blog LIMIT 1")
    blog = cursor.fetchone()
    
    if not blog:
        blog_id = "cl" + str(uuid.uuid4()).replace("-", "")[:23] # Simulando CUID do Prisma
        now = datetime.datetime.utcnow().isoformat() + "Z"
        
        cursor.execute('''
            INSERT INTO Blog (id, domain, name, niche, description, theme, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (blog_id, "observadoreconomico.com", "Observador Econômico", "Finanças", "O melhor blog financeiro autônomo.", "dark", now, now))
        
        # Criar categoria padrão
        cat_id = "cl" + str(uuid.uuid4()).replace("-", "")[:23]
        cursor.execute('''
            INSERT INTO Category (id, name, slug, blogId)
            VALUES (?, ?, ?, ?)
        ''', (cat_id, "Mercado", "mercado", blog_id))
        
        conn.commit()
        print(f"[SEED] [ OK ] Blog base 'Observador Econômico' criado com sucesso. (ID: {blog_id})")
    else:
        print(f"[SEED] O blog base já existe. (ID: {blog[0]})")
        
    conn.close()

if __name__ == "__main__":
    init_seed()
