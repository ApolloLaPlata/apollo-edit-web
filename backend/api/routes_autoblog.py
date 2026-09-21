from fastapi import APIRouter, HTTPException
import sqlite3
import os
import uuid
import datetime
import re

router = APIRouter(prefix="/api/autoblog", tags=["AutoBlog"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Caminho para o banco da fila de aprovação (criado no publisher.py)
APPROVAL_DB_PATH = os.path.join(BASE_DIR, "..", "bots", "approval_queue.db")
# Caminho para o banco de dados oficial do Next.js
NEXT_DB_PATH = os.path.join(BASE_DIR, "..", "..", "autoblog", "dev.db")

def get_approval_db():
    return sqlite3.connect(APPROVAL_DB_PATH)

def get_next_db():
    return sqlite3.connect(NEXT_DB_PATH)

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
    2. Move os dados para o dev.db (banco oficial do site Next.js).
    """
    conn_app = get_approval_db()
    cursor_app = conn_app.cursor()
    
    # Busca o draft
    cursor_app.execute("SELECT titulo, markdown, image_url, audio_path, duracao_segundos FROM approval_queue WHERE id = ? AND status = 'pending'", (draft_id,))
    draft = cursor_app.fetchone()
    if not draft:
        conn_app.close()
        raise HTTPException(status_code=404, detail="Rascunho não encontrado ou já processado.")
        
    titulo, markdown, image_url, audio_path, duracao_segundos = draft
    
    # Prepara inserção no Next.js (dev.db)
    blog_name = "Observador Econômico"
    conn_next = get_next_db()
    cursor_next = conn_next.cursor()
    
    # 1. Pega o ID do blog
    cursor_next.execute("SELECT id FROM Blog WHERE name = ?", (blog_name,))
    blog = cursor_next.fetchone()
    if not blog:
        conn_next.close()
        conn_app.close()
        raise HTTPException(status_code=500, detail="Blog padrão não encontrado no dev.db")
    
    blog_id = blog[0]
    post_id = "cl" + str(uuid.uuid4()).replace("-", "")[:23]
    slug = slugify(titulo) + "-" + str(uuid.uuid4())[:6]
    html_content = f"<div><h1>{titulo}</h1><p>{markdown}</p></div>"
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    try:
        # Inserção no banco Prisma (Next.js)
        # Nota: Adaptado para incluir áudio se os campos existissem no Prisma, 
        # mas mantendo os campos originais mapeados anteriormente.
        cursor_next.execute('''
            INSERT INTO Post (id, title, slug, contentMd, contentHtml, coverImage, author, isPublished, publishedAt, createdAt, updatedAt, blogId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (post_id, titulo, slug, markdown, html_content, image_url, "Redação IA", 1, now, now, now, blog_id))
        
        # Astroturfing: Geração de Comentários Fantasmas após publicação oficial
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
                        INSERT INTO Comment (id, authorName, authorAvatar, content, createdAt, postId)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (c_id, c['authorName'], avatar, c['content'], c_time, post_id))
        except Exception as ec:
            print(f"[AUTOBLOG API] Falha silenciosa ao injetar comentários: {ec}")

        conn_next.commit()
        
        # Marca como aprovado na fila original
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
    
    return {"status": "ok", "message": "Artigo aprovado e publicado com sucesso no AutoBlog!", "post_id": post_id}

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
