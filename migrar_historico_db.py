import os
import json
import uuid
from database_manager import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIST_FILE = os.path.join(BASE_DIR, "historico_renders.json")

def migrar_historico():
    if not os.path.exists(HIST_FILE):
        print("historico_renders.json não encontrado.")
        return
        
    try:
        with open(HIST_FILE, 'r', encoding='utf-8') as f:
            historico = json.load(f)
            
        print(f"Lendo {len(historico)} registros de historico_renders.json...")
        
        # Pega ou cria o canal genérico 'Default' para vídeos sem perfil
        default_canal_id = db.registrar_canal("Legado_Geral", "")
        
        for item in historico:
            perfil = item.get("perfil", "").strip()
            if perfil:
                canal_id = db.registrar_canal(perfil, "")
            else:
                canal_id = default_canal_id
                
            job_id = f"legacy_{uuid.uuid4().hex[:8]}"
            titulo = os.path.basename(item.get("saida", "Video_Desconhecido"))
            filepath = item.get("saida", "")
            status = item.get("status", "concluido")
            erro = item.get("detalhe", "")
            
            # Formatar a data se possível ou deixar DB preencher
            # A data vem no formato 'YYYY-MM-DD HH:MM:SS'
            data_inicio = item.get("data")
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO historico_videos 
                    (canal_id, job_id, titulo, filepath, status, mensagem_erro, data_inicio, data_fim)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (canal_id, job_id, titulo, filepath, status, erro, data_inicio, data_inicio))
                
        print("Migração de histórico para SQLite concluída!")
        
    except Exception as e:
        print(f"Erro na migração: {e}")

if __name__ == "__main__":
    migrar_historico()
