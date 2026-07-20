import sqlite3
import os
from typing import List, Dict, Any, Optional
import json

class DatabaseManager:
    _instance = None
    
    def __new__(cls, db_path: str = "apollo_database.db"):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self, db_path: str = "apollo_database.db"):
        if getattr(self, '_initialized', False):
            return
            
        # O banco de dados fica na raiz do Apollo Studio
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
        self._init_db()
        self._initialized = True
        
    def get_connection(self):
        """Retorna uma conexão com o banco de dados (auto-commit, check_same_thread=False)"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
        
    def _init_db(self):
        """Inicializa as tabelas se não existirem"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela Canais (Workspaces)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS canais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    path_config TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela Histórico de Vídeos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historico_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canal_id INTEGER,
                    job_id TEXT UNIQUE,
                    titulo TEXT,
                    filepath TEXT,
                    status TEXT,
                    progresso INTEGER DEFAULT 0,
                    mensagem_erro TEXT,
                    config_json TEXT,
                    data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_fim TIMESTAMP,
                    FOREIGN KEY (canal_id) REFERENCES canais (id)
                )
            ''')
            
            # Tabela Tokens e Uso de API
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historico_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    canal_id INTEGER,
                    api_nome TEXT,
                    tokens_usados INTEGER,
                    custo_estimado REAL,
                    data_uso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (canal_id) REFERENCES canais (id)
                )
            ''')
            
            # Tabela Memória Ativa (Inter-Tab Communication)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memoria_ativa (
                    chave TEXT PRIMARY KEY,
                    valor_json TEXT,
                    canal_id INTEGER,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (canal_id) REFERENCES canais (id)
                )
            ''')
            
            conn.commit()

    # --- CANAIS ---
    
    def registrar_canal(self, nome: str, path_config: str) -> int:
        """Registra um novo canal ou atualiza seu caminho"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM canais WHERE nome = ?", (nome,))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE canais SET path_config = ? WHERE id = ?", (path_config, row['id']))
                return row['id']
            else:
                cursor.execute("INSERT INTO canais (nome, path_config) VALUES (?, ?)", (nome, path_config))
                return cursor.lastrowid
                
    def get_canal_id(self, nome: str) -> Optional[int]:
        """Obtém o ID numérico do canal pelo nome"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM canais WHERE nome = ?", (nome,))
            row = cursor.fetchone()
            return row['id'] if row else None
            
    # --- VIDEOS / RENDER ---
    
    def registrar_video(self, canal_id: int, job_id: str, titulo: str, config_json: str, status: str = "pendente"):
        """Insere um novo vídeo na fila/histórico"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO historico_videos 
                (canal_id, job_id, titulo, config_json, status, progresso)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (canal_id, job_id, titulo, config_json, status, 0))
            conn.commit()
            
    def atualizar_status_video(self, job_id: str, status: str, progresso: int = None, filepath: str = None, erro: str = None):
        """Atualiza o status de um vídeo em renderização"""
        query = "UPDATE historico_videos SET status = ?"
        params = [status]
        
        if progresso is not None:
            query += ", progresso = ?"
            params.append(progresso)
        if filepath:
            query += ", filepath = ?"
            params.append(filepath)
        if erro:
            query += ", mensagem_erro = ?"
            params.append(erro)
            
        if status in ['concluido', 'erro']:
            query += ", data_fim = CURRENT_TIMESTAMP"
            
        query += " WHERE job_id = ?"
        params.append(job_id)
        
        with self.get_connection() as conn:
            conn.execute(query, tuple(params))
            conn.commit()
            
    def buscar_videos_dashboard(self, canal_id: int = None, limit: int = 100) -> List[Dict]:
        """Busca vídeos para alimentar o dashboard (otimizado via SQL)"""
        query = '''
            SELECT v.id, v.job_id, v.titulo, v.status, v.progresso, v.filepath, v.mensagem_erro, v.data_inicio, v.data_fim, c.nome as canal_nome
            FROM historico_videos v
            LEFT JOIN canais c ON v.canal_id = c.id
        '''
        params = []
        
        if canal_id:
            query += " WHERE v.canal_id = ?"
            params.append(canal_id)
            
        query += " ORDER BY v.data_inicio DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
    def buscar_pendentes(self) -> List[Dict]:
        """Busca a lista de vídeos pendentes na fila para o Gerenciador de Render"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.*, c.nome as canal_nome 
                FROM historico_videos v 
                LEFT JOIN canais c ON v.canal_id = c.id 
                WHERE v.status IN ('pendente', 'renderizando') 
                ORDER BY v.data_inicio ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    # --- MEMORIA ATIVA ---
    
    def set_memoria(self, chave: str, valor: Any, canal_id: int = None):
        """Salva uma informação de estado na memória ativa."""
        valor_json = json.dumps(valor)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO memoria_ativa (chave, valor_json, canal_id, data_atualizacao)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(chave) DO UPDATE SET 
                    valor_json=excluded.valor_json, 
                    canal_id=excluded.canal_id, 
                    data_atualizacao=CURRENT_TIMESTAMP
            ''', (chave, valor_json, canal_id))
            conn.commit()
            
    def get_memoria(self, chave: str, default: Any = None) -> Any:
        """Recupera uma informação da memória ativa."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT valor_json FROM memoria_ativa WHERE chave = ?", (chave,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row['valor_json'])
                except:
                    return row['valor_json']
            return default

    # --- TOKENS E CUSTOS ---
    
    def gravar_uso_api(self, canal_id: int, api_nome: str, tokens_usados: int = 0, custo_estimado: float = 0.0):
        """Grava o uso de uma API (tokens ou geracao de imagens)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO historico_tokens (canal_id, api_nome, tokens_usados, custo_estimado)
                VALUES (?, ?, ?, ?)
            ''', (canal_id, api_nome, tokens_usados, custo_estimado))
            conn.commit()
            
    def buscar_estatisticas_api(self, canal_id: int = None) -> Dict:
        """Retorna as estatisticas de uso de API (hoje)"""
        query_hoje = "SELECT api_nome, SUM(tokens_usados) as tokens_hoje, SUM(custo_estimado) as custo_hoje FROM historico_tokens WHERE date(data_uso) = date('now', 'localtime')"
        params = []
        if canal_id:
            query_hoje += " AND canal_id = ?"
            params.append(canal_id)
        query_hoje += " GROUP BY api_nome"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_hoje, params)
            rows = cursor.fetchall()
            
            stats = {}
            for row in rows:
                stats[row['api_nome']] = {
                    'tokens_hoje': row['tokens_hoje'],
                    'custo_hoje': row['custo_hoje']
                }
            return stats

# Singleton de exportação amigável
db = DatabaseManager()
