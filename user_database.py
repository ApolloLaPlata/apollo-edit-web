import sqlite3
import os
import hashlib
from datetime import datetime

# Define o caminho do banco de dados relativo ao script atual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "apollo_users.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializa o banco de dados e cria as tabelas necessárias se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            credits INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            role TEXT DEFAULT 'Livre',
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            country TEXT DEFAULT 'BR',
            rank_points INTEGER DEFAULT 0
        )
    ''')
    
    # Cria a tabela de log de transações para auditoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # MASTER SAAS TABLES
    # Controle de ferramentas (Ligar/Desligar)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Log de uso de APIs para calcular lucro
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_usage_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            api_name TEXT,
            credits_cost INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Campanhas de publicidade
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ad_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            image_url TEXT,
            link_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            views INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Registro de Renders (Vídeos Exportados)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS render_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            project_name TEXT,
            duration_seconds INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Suporte ao cliente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            message TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Registro de visitas por página
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            page_name TEXT,
            visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Campanhas de publicidade/banners
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ad_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            image_url TEXT,
            link_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- SISTEMA RPG & LOJA ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL, -- 'border', 'title', 'cosmetic', 'gas', 'crystals'
            description TEXT,
            price_gas INTEGER DEFAULT 0,
            price_crystals INTEGER DEFAULT 0,
            image_url TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id INTEGER,
            quantity INTEGER DEFAULT 1,
            acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (item_id) REFERENCES store_items(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_equipped (
            user_id INTEGER PRIMARY KEY,
            equipped_border_id INTEGER,
            equipped_title_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (equipped_border_id) REFERENCES store_items(id),
            FOREIGN KEY (equipped_title_id) REFERENCES store_items(id)
        )
    ''')

    # Migração: Tenta adicionar colunas caso a tabela já exista do modelo antigo
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Livre'")
    except sqlite3.OperationalError: pass
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1")
    except sqlite3.OperationalError: pass
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")
    except sqlite3.OperationalError: pass
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN country TEXT DEFAULT 'BR'")
    except sqlite3.OperationalError: pass
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN rank_points INTEGER DEFAULT 0")
    except sqlite3.OperationalError: pass
    
    # Migrações V2
    try:
        cursor.execute("ALTER TABLE ad_campaigns ADD COLUMN clicks INTEGER DEFAULT 0")
    except sqlite3.OperationalError: pass

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError: pass

    # Migrações V3 (Economia Backend)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN gas INTEGER DEFAULT 100")
    except sqlite3.OperationalError: pass

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN crystals INTEGER DEFAULT 0")
    except sqlite3.OperationalError: pass

    # Novas tabelas para o Sistema de Orquestração (N8N) e Custos de IA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models_pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id TEXT UNIQUE NOT NULL,
            provider TEXT NOT NULL,
            tier TEXT DEFAULT 'Premium',
            input_price_per_1m REAL DEFAULT 0.0,
            output_price_per_1m REAL DEFAULT 0.0,
            rpm_limit INTEGER DEFAULT 0,
            tpm_limit INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Ativo',
            margin_multiplier REAL DEFAULT 1.3,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_orchestrator_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_order INTEGER NOT NULL,
            role_name TEXT NOT NULL,
            default_model_id TEXT,
            is_dynamic BOOLEAN DEFAULT 0,
            system_prompt TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_analysis_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_text TEXT NOT NULL,
            recommended_actions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_trends_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            trending_score INTEGER DEFAULT 0,
            analysis_text TEXT NOT NULL,
            source_url TEXT,
            is_approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Retorna o hash SHA-256 da senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str, initial_credits: int = 100, role: str = 'Livre') -> bool:
    """Cria um novo usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, credits, role) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), initial_credits, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> dict:
    """Verifica credenciais e retorna o usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username, credits, role, is_banned, gas, crystals FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0], 
            "username": user[1], 
            "credits": user[2], 
            "role": user[3], 
            "is_banned": bool(user[4] if len(user) > 4 else False),
            "gas": user[5] if len(user) > 5 else 100,
            "crystals": user[6] if len(user) > 6 else 0
        }
    return None

def get_all_users() -> list:
    """Retorna todos os usuários (apenas para Admin)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, credits, role, created_at, is_banned, gas, crystals FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": u[0], 
            "username": u[1], 
            "credits": u[2], 
            "role": u[3], 
            "created_at": u[4], 
            "is_banned": bool(u[5] if len(u) > 5 else False),
            "gas": u[6] if len(u) > 6 else 100,
            "crystals": u[7] if len(u) > 7 else 0
        }
        for u in users
    ]

def add_credits(user_id: int, amount: int, description: str = "Recarga Administrativa") -> bool:
    """Adiciona créditos para um usuário."""
    return add_currency(user_id, amount, 'credits', description)

def deduct_credits(user_id: int, amount: int, description: str = "Uso de Ferramenta Premium") -> bool:
    """Deduz créditos de um usuário se ele tiver saldo suficiente."""
    return deduct_currency(user_id, amount, 'credits', description)

def add_currency(user_id: int, amount: int, currency_type: str = 'credits', description: str = "Recarga") -> bool:
    """Adiciona moeda (credits, gas, crystals) para um usuário."""
    if amount <= 0:
        return False
    if currency_type not in ['credits', 'gas', 'crystals']:
        return False
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"UPDATE users SET {currency_type} = {currency_type} + ? WHERE id = ?", (amount, user_id))
        if cursor.rowcount > 0:
            cursor.execute("INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)",
                           (user_id, amount, f"{description} ({currency_type})"))
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Erro ao adicionar {currency_type}: {e}")
        return False
    finally:
        conn.close()

def deduct_currency(user_id: int, amount: int, currency_type: str = 'credits', description: str = "Consumo") -> bool:
    """Deduz moeda de um usuário se ele tiver saldo suficiente."""
    if amount <= 0:
        return False
    if currency_type not in ['credits', 'gas', 'crystals']:
        return False
        
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {currency_type} FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        if not result or result[0] < amount:
            return False 
            
        cursor.execute(f"UPDATE users SET {currency_type} = {currency_type} - ? WHERE id = ?", (amount, user_id))
        cursor.execute("INSERT INTO transactions (user_id, amount, description) VALUES (?, ?, ?)",
                       (user_id, -amount, f"{description} ({currency_type})"))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao deduzir {currency_type}: {e}")
        return False
    finally:
        conn.close()

def update_password(user_id: int, new_password: str) -> bool:
    """Atualiza a senha do usuário."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_user(user_id: int) -> bool:
    """Remove um usuário (Admin)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

# Inicializa o DB ao importar o módulo
init_db()

def log_page_visit(user_id: int, page_name: str) -> bool:
    """Registra a visita a uma página."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO page_visits (user_id, page_name) VALUES (?, ?)", (user_id, page_name))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao logar visita: {e}")
        return False
    finally:
        conn.close()

def get_page_visits_stats() -> list:
    """Retorna as estatísticas de visitas por página para o admin."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT page_name, COUNT(*) as views FROM page_visits GROUP BY page_name ORDER BY views DESC")
        return [{"page_name": r[0], "views": r[1]} for r in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao buscar stats de visitas: {e}")
        return []
    finally:
        conn.close()
