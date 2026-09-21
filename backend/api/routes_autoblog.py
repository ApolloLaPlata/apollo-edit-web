from fastapi import APIRouter, HTTPException
import sqlite3
import os
import uuid
import datetime
import re
import psycopg2
from huggingface_hub import HfApi

router = APIRouter(prefix="/api/autoblog", tags=["AutoBlog"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Caminho para o banco da fila de aprovação (criado no publisher.py) - CONTINUA LOCAL (SQLite)
APPROVAL_DB_PATH = os.path.join(BASE_DIR, "..", "bots", "approval_queue.db")

def get_approval_db():
    return sqlite3.connect(APPROVAL_DB_PATH)

def get_postgres_conn():
    # URL do Supabase fornecida via Vercel/Ambiente
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise Exception("A variável de ambiente DATABASE_URL não está configurada para o Supabase.")
    return psycopg2.connect(db_url)

def upload_image_to_hf(local_image_path: str, filename: str) -> str:
    """Faz o upload de uma imagem local para a Conta 2 do Hugging Face (Dataset / CDN)"""
    hf_token = os.environ.get("HF_TOKEN_CONTA_2") or os.environ.get("HF_TOKEN")
    hf_repo = os.environ.get("HF_DATASET_REPO", "usuario/autoblog-cdn")
    
    if not hf_token:
        print("[AUTOBLOG API] Aviso: HF_TOKEN_CONTA_2 não configurado. Pulando upload pro HF e usando URL local.")
        return None

    try:
        api = HfApi(token=hf_token)
        # O caminho no repositório será public/images/...
        repo_path = f"images/{filename}"
        
        print(f"[AUTOBLOG API] Fazendo upload da imagem {filename} para o dataset HF {hf_repo}...")
        api.upload_file(
            path_or_fileobj=local_image_path,
            path_in_repo=repo_path,
            repo_id=hf_repo,
            repo_type="dataset"
        )
        
        # Constrói a URL de resolução pública
        public_url = f"https://huggingface.co/datasets/{hf_repo}/resolve/main/{repo_path}"
        print(f"[AUTOBLOG API] Upload concluído! URL Pública: {public_url}")
        return public_url
    except Exception as e:
        print(f"[AUTOBLOG API] Erro ao fazer upload para Hugging Face Dataset: {e}")
        return None

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

@router.get("/queue")
def list_pending_drafts():
    """
    Retorna todos os rascunhos que estão na fila aguardando aprovação biométrica (Pocket Director).
    """
    if not os.path.exists(APPROVAL_DB_PATH):
        return {"status": "ok", "drafts": []}

    conn = get_approval_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, titulo, markdown, image_url, audio_path, duracao_segundos, created_at FROM approval_queue WHERE status = 'pending' ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    drafts = []
    for r in rows:
        drafts.append({
            "id": r[0],
            "titulo": r[1],
            "markdown": r[2],
            "image_url": r[3],
            "audio_path": r[4],
            "duracao_segundos": r[5],
            "created_at": r[6]
        })
    return {"status": "ok", "drafts": drafts}

@router.post("/approve/{draft_id}")
def approve_draft(draft_id: str):
    """
    Aprova um rascunho:
    1. Muda o status no approval_queue.db para 'approved'.
    2. Envia a imagem para o HF CDN (Conta 2).
    3. Move os dados para o PostgreSQL (Supabase / Neon), que é o banco do Next.js.
    """
    conn_app = get_approval_db()
    cursor_app = conn_app.cursor()
    
    # Busca o draft no SQLite
    cursor_app.execute("SELECT titulo, markdown, image_url, audio_path, duracao_segundos FROM approval_queue WHERE id = ? AND status = 'pending'", (draft_id,))
    draft = cursor_app.fetchone()
    if not draft:
        conn_app.close()
        raise HTTPException(status_code=404, detail="Rascunho não encontrado ou já processado.")
        
    titulo, markdown, image_url, audio_path, duracao_segundos = draft
    
    # -- Missão 2: Upload CDN Hugging Face --
    final_image_url = image_url
    if image_url and image_url.startswith("/uploads/"):
        filename = os.path.basename(image_url)
        local_path = os.path.join(BASE_DIR, "..", "..", "autoblog", "public", "uploads", filename)
        
        if os.path.exists(local_path):
            hf_url = upload_image_to_hf(local_path, filename)
            if hf_url:
                final_image_url = hf_url

    # Prepara inserção no Next.js (Agora Postgres Cloud)
    blog_name = "Observador Econômico"
    
    try:
        conn_next = get_postgres_conn()
        cursor_next = conn_next.cursor()
    except Exception as e:
        conn_app.close()
        raise HTTPException(status_code=500, detail=f"Erro de conexão Postgres (Supabase): {e}")
    
    # 1. Pega o ID do blog
    cursor_next.execute('SELECT id FROM "Blog" WHERE name = %s', (blog_name,))
    blog = cursor_next.fetchone()
    if not blog:
        conn_next.close()
        conn_app.close()
        raise HTTPException(status_code=500, detail="Blog padrão não encontrado no PostgreSQL (Supabase)")
    
    blog_id = blog[0]
    post_id = "cl" + str(uuid.uuid4()).replace("-", "")[:23]
    slug = slugify(titulo) + "-" + str(uuid.uuid4())[:6]
    html_content = f"<div><h1>{titulo}</h1><p>{markdown}</p></div>"
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    try:
        # Inserção no banco Prisma (Next.js / Postgres)
        cursor_next.execute('''
            INSERT INTO "Post" (id, title, slug, "contentMd", "contentHtml", "coverImage", author, "isPublished", "publishedAt", "createdAt", "updatedAt", "blogId")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (post_id, titulo, slug, markdown, html_content, final_image_url, "Redação IA", 1, now, now, now, blog_id))
        
        # Astroturfing: Geração de Comentários Fantasmas
        try:
            from backend.bots.writer import gerar_comentarios_fantasmas
            import random
            
            qtd = random.randint(3, 8)
            comentarios = gerar_comentarios_fantasmas(titulo, qtd)
            
            if comentarios:
                for c in comentarios:
                    c_id = "cl" + str(uuid.uuid4()).replace("-", "")[:23]
                    avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={c['authorName'].replace(' ', '')}"
                    minutos_atras = random.randint(1, 120)
                    c_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=minutos_atras)).isoformat() + "Z"
                    
                    cursor_next.execute('''
                        INSERT INTO "Comment" (id, "postId", "authorName", "authorAvatar", content, "createdAt")
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (c_id, post_id, c['authorName'], avatar, c['content'], c_time))
        except Exception as ec:
            print(f"[AUTOBLOG API] Falha silenciosa ao injetar comentários no Postgres: {ec}")

        conn_next.commit()
        
        # Marca como aprovado na fila original do SQLite
        cursor_app.execute("UPDATE approval_queue SET status = 'approved' WHERE id = ?", (draft_id,))
        conn_app.commit()
        
    except Exception as e:
        conn_next.rollback()
        conn_app.rollback()
        conn_next.close()
        conn_app.close()
        raise HTTPException(status_code=500, detail=str(e))

    conn_next.close()
    conn_app.close()
    
    return {"status": "ok", "message": "Artigo aprovado e publicado com sucesso no Supabase e HF!", "post_id": post_id}

@router.post("/reject/{draft_id}")
def reject_draft(draft_id: str):
    """
    Rejeita um rascunho da fila.
    """
    conn = get_approval_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE approval_queue SET status = 'rejected' WHERE id = ?", (draft_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Rascunho não encontrado.")
        
    conn.commit()
    conn.close()
    return {"status": "ok", "message": "Artigo rejeitado com sucesso."}
