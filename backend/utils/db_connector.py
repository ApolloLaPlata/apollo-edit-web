import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
import logging

logger = logging.getLogger(__name__)

class PostgresCursorWrapper:
    """
    Wrapper for psycopg2 cursor to make it act like sqlite3 cursor.
    Specifically, it converts sqlite3 '?' placeholders to psycopg2 '%s' placeholders.
    """
    def __init__(self, cursor):
        self._cursor = cursor
        
    def execute(self, query, params=None):
        # Convert sqlite3 '?' to postgres '%s'
        # Note: This is a simple replace. If '?' is used inside string literals in the SQL, it will break.
        # But for standard prepared statements, it works perfectly.
        postgres_query = query.replace('?', '%s')
        try:
            if params:
                self._cursor.execute(postgres_query, params)
            else:
                self._cursor.execute(postgres_query)
        except Exception as e:
            logger.error(f"[DB_CONNECTOR] Erro na query: {postgres_query} com params {params}. Erro: {e}")
            raise
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor.fetchall())
        
    @property
    def lastrowid(self):
        # Postgres usually uses RETURNING id, but for simple scripts that rely on lastrowid,
        # psycopg2 doesn't support lastrowid out of the box unless using RETURNING.
        # This might return None. We will need to be careful if code relies heavily on lastrowid.
        return None

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        # Use DictCursor so row['column_name'] works like sqlite3.Row
        pg_cursor = self._conn.cursor(cursor_factory=DictCursor)
        return PostgresCursorWrapper(pg_cursor)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

def get_db_connection(db_name="economy.db"):
    """
    Returns a database connection.
    If DATABASE_URL is set in environment, returns a Postgres connection (via psycopg2) wrapped to act like sqlite3.
    Otherwise, falls back to the original local sqlite3 database.
    """
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        try:
            conn = psycopg2.connect(database_url)
            return PostgresConnectionWrapper(conn)
        except Exception as e:
            logger.error(f"Falha ao conectar no PostgreSQL: {e}. Causa: {database_url}")
            raise
    else:
        # Fallback para o SQLite antigo (desenvolvimento local sem .env configurado)
        # Identifica de onde est sendo chamado e monta o path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # A maioria dos DBs ficava em backend/financial_agent/
        if "approval" in db_name:
            db_path = os.path.join(base_dir, "bots", db_name)
        elif "trend" in db_name or "market" in db_name or "pricing" in db_name or "traffic" in db_name:
            db_path = os.path.join(base_dir, "agents", db_name)
        else:
            db_path = os.path.join(base_dir, "financial_agent", db_name)
            
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
