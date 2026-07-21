import sqlite3
import uuid
import datetime
import re

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "frontend", "dev.db")

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def publicar_artigo(titulo, markdown, image_url, blog_name="Observador Econômico"):
    """
    Recebe os dados orquestrados e salva diretamente no banco de dados
    do Next.js (SQLite) para que o frontend exiba em tempo real.
    """
    print(f"[PUBLISHER] Injetando artigo '{titulo}' no banco de dados do CMS...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Pega o ID do blog
    cursor.execute("SELECT id FROM Blog WHERE name = ?", (blog_name,))
    blog = cursor.fetchone()
    if not blog:
        print("[ERRO] Blog não encontrado no banco de dados!")
        return
    blog_id = blog[0]
    
    # 2. Gera os dados para a tabela Post
    post_id = "cl" + str(uuid.uuid4()).replace("-", "")[:23]
    slug = slugify(titulo) + "-" + str(uuid.uuid4())[:6]
    
    # Conversão super básica de Markdown para HTML apenas para fallback
    html_content = f"<div><h1>{titulo}</h1><p>{markdown}</p></div>"
    
    now = datetime.datetime.utcnow().isoformat() + "Z"
    
    # 3. Insere no banco (tabela Post gerada pelo Prisma)
    try:
        cursor.execute('''
            INSERT INTO Post (id, title, slug, contentMd, contentHtml, coverImage, author, isPublished, publishedAt, createdAt, updatedAt, blogId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post_id,
            titulo,
            slug,
            markdown,
            html_content,
            image_url,
            "Redação IA",
            1, # isPublished = True
            now,
            now,
            now,
            blog_id
        ))
        conn.commit()
        print(f"[PUBLISHER] [ OK ] Sucesso! Artigo '{titulo}' publicado no Next.js (Post ID: {post_id})")
        
        # 4. Geração de Comentários Fantasmas (Astroturfing)
        try:
            from writer import gerar_comentarios_fantasmas
            import random
            
            # Decide randomicamente gerar entre 3 e 8 comentários para parecer orgânico
            qtd = random.randint(3, 8)
            comentarios = gerar_comentarios_fantasmas(titulo, qtd)
            
            if comentarios:
                for c in comentarios:
                    c_id = "cl" + str(uuid.uuid4()).replace("-", "")[:23]
                    # Gera um avatar aleatório consistente pro nome
                    avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={c['authorName'].replace(' ', '')}"
                    # Simula comentários feitos nas últimas 2 horas
                    minutos_atras = random.randint(1, 120)
                    c_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=minutos_atras)).isoformat() + "Z"
                    
                    cursor.execute('''
                        INSERT INTO Comment (id, authorName, authorAvatar, content, createdAt, postId)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        c_id,
                        c['authorName'],
                        avatar,
                        c['content'],
                        c_time,
                        post_id
                    ))
                conn.commit()
                print(f"[PUBLISHER] [ OK ] Injetados {len(comentarios)} comentários fantasmas!")
        except Exception as ec:
            print(f"[PUBLISHER] [AVISO] Falha ao injetar comentários fantasmas: {ec}")
            
    except Exception as e:
        print(f"[PUBLISHER] [ERRO] Falha ao publicar: {e}")
        
    conn.close()
