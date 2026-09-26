import sqlite3
import uuid
import datetime
import re
import os
import sqlite3
from backend.utils.db_connector import get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Banco temporário para a aprovação biométrica do Pocket Director
APPROVAL_DB_PATH = os.path.join(BASE_DIR, "approval_queue.db")
# Banco final do Next.js (que o Pocket Director usará após aprovar)
NEXT_DB_PATH = os.path.join(BASE_DIR, "..", "frontend", "dev.db")

def init_approval_db():
    conn = get_db_connection("economy.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approval_queue (
            id TEXT PRIMARY KEY,
            titulo TEXT,
            markdown TEXT,
            image_url TEXT,
            audio_path TEXT,
            duracao_segundos REAL,
            status TEXT DEFAULT 'pending',
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Inicializa o banco de aprovação assim que o módulo é importado
init_approval_db()

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def publicar_artigo(titulo, markdown, image_url, blog_name="Observador Econômico", audio_path=None, duracao_segundos=0):
    """
    Recebe os dados orquestrados e SALVA NA FILA DE APROVAÇÃO BIOMÉTRICA (approval_queue.db).
    O post só irá para o Next.js (dev.db) após o usuário aprovar pelo celular (Pocket Director).
    """
    print(f"[PUBLISHER] Redirecionando artigo '{titulo}' para a Fila de Aprovação Biométrica...")
    
    try:
        conn = get_db_connection("economy.db")
        cursor = conn.cursor()
        
        post_id = "draft_" + str(uuid.uuid4()).replace("-", "")[:16]
        now = datetime.datetime.utcnow().isoformat() + "Z"
        
        cursor.execute('''
            INSERT INTO approval_queue (id, titulo, markdown, image_url, audio_path, duracao_segundos, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
        ''', (post_id, titulo, markdown, image_url, audio_path, duracao_segundos, now))
        
        conn.commit()
        print(f"[PUBLISHER] [ OK ] Rascunho enfileirado com sucesso! (Draft ID: {post_id})")
        if duracao_segundos > 0:
            print(f"[PUBLISHER] [ OK ] Metadados de Áudio anexados: {duracao_segundos:.2f}s | {audio_path}")
            
    except Exception as e:
        print(f"[PUBLISHER] [ERRO] Falha ao enfileirar no approval_queue.db: {e}")
    finally:
        conn.close()
