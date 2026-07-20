"""



coin_ledger.py Ã¢ÂÂ Carteira de Moedas do Apollo por UsuÃÂ¡rio



==========================================================



Gerencia o sistema completo de moedas do Apollo Edit Web:



  - Apollo Coins     Ã¢ÂÂ moeda universal gratuita (ganha por tempo/ads)



  - Chips LLM        Ã¢ÂÂ para uso dos modelos de linguagem



  - GPU Tokens       Ã¢ÂÂ para uso das GPUs de render



  - CombustÃÂ­vel      Ã¢ÂÂ para operaÃÂ§ÃÂµes pesadas do pipeline



  - Cristais de API  Ã¢ÂÂ para chamadas externas (TTS, imagens, etc.)







Integra com o banco economy.db jÃÂ¡ existente, extendendo-o.



"""







import sqlite3

from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys and WAL mode for better concurrency
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()




import os



import logging



from dataclasses import dataclass



from typing import Optional







logger = logging.getLogger("CoinLedger")







DB_PATH = os.path.join(os.path.dirname(__file__), "economy.db")







# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



# DEFINIÃÂÃÂO DAS MOEDAS



# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



CURRENCY_TYPES = ["coins", "chips_llm", "gpu_tokens", "fuel", "crystals"]







CURRENCY_LABELS = {



    "coins":      "Apollo Coins",



    "chips_llm":  "Chips LLM",



    "gpu_tokens": "GPU Tokens",



    "fuel":       "CombustÃÂ­vel",



    "crystals":   "Cristais de API",



}







# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



# COTAS MENSAIS POR PLANO



# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



PLAN_MONTHLY_GRANTS = {



    "free": {



        "coins":      500,



        "chips_llm":  0,



        "gpu_tokens": 0,



        "fuel":       50,



        "crystals":   0,



        "max_channels": 1,



        "parallel_renders": 1,



    },



    "pro": {



        "coins":      3000,



        "chips_llm":  500,



        "gpu_tokens": 200,



        "fuel":       300,



        "crystals":   100,



        "max_channels": 5,



        "parallel_renders": 3,



    },



    "master": {



        "coins":      6000,



        "chips_llm":  1200,



        "gpu_tokens": 500,



        "fuel":       700,



        "crystals":   250,



        "max_channels": 15,



        "parallel_renders": 8,



    },



}







# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



# CUSTO DAS OPERAÃÂÃÂES (em moedas)



# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



OPERATION_COSTS = {



    # GeraÃÂ§ÃÂ£o de texto / roteiro



    "generate_script_short":   {"coins": 50,  "chips_llm": 10},



    "generate_script_long":    {"coins": 120, "chips_llm": 25},







    # GeraÃÂ§ÃÂ£o de imagem



    "generate_image_flux":     {"coins": 80,  "gpu_tokens": 5,  "crystals": 2},



    "generate_image_sd":       {"coins": 60,  "gpu_tokens": 4},







    # GeraÃÂ§ÃÂ£o de vÃÂ­deo



    "generate_video_ltx":      {"coins": 250, "gpu_tokens": 20, "fuel": 10},



    "generate_video_wan":      {"coins": 350, "gpu_tokens": 30, "fuel": 15},







    # TTS (texto para voz)



    "tts_basic":               {"coins": 30,  "crystals": 1},



    "tts_premium_clone":       {"coins": 80,  "crystals": 5},







    # Render / exportaÃÂ§ÃÂ£o de timeline



    "render_free_tier":        {"coins": 100, "fuel": 20, "gpu_tokens": 5},



    "render_nitro_t4":         {"coins": 200, "fuel": 40, "gpu_tokens": 15},   # + compra de Nitro



    "render_nitro_master_a100":{"coins": 400, "fuel": 80, "gpu_tokens": 40},   # + compra de Nitro Master







    # OperaÃÂ§ÃÂµes de canal



    "auto_publish_youtube":    {"coins": 20,  "fuel": 5},



    "download_video":          {"coins": 10},



}











# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



# INICIALIZAÃÂÃÂO DO BANCO



# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



def init_ledger():



    """Garante que as colunas extras existem no banco jÃÂ¡ criado pelo economy_db.py."""



    conn = sqlite3.connect(DB_PATH)



    c = conn.cursor()







    # Tenta adicionar as colunas novas (ignora se jÃÂ¡ existirem)



    new_columns = [



        ("chips_llm",  "INTEGER DEFAULT 0"),



        ("gpu_tokens", "INTEGER DEFAULT 0"),



        ("plan",       "TEXT DEFAULT 'free'"),





        ("email", "TEXT DEFAULT NULL"),



        ("password_hash", "TEXT DEFAULT NULL"),



    ]



    for col_name, col_def in new_columns:



        try:



            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")



            logger.info(f"[Ledger] Coluna '{col_name}' adicionada ao banco.")



        except sqlite3.OperationalError:



            pass  # Coluna jÃÂ¡ existe







    # Tabela de transaÃÂ§ÃÂµes



    c.execute("""



        CREATE TABLE IF NOT EXISTS transactions (



            id INTEGER PRIMARY KEY AUTOINCREMENT,



            user_id TEXT NOT NULL,



            operation TEXT NOT NULL,



            currency TEXT NOT NULL,



            amount INTEGER NOT NULL,



            direction TEXT NOT NULL,  -- 'debit' ou 'credit'



            balance_after INTEGER,



            created_at TEXT DEFAULT (datetime('now')),



            metadata TEXT



        )



    """)







    conn.commit()



    conn.close()



    logger.info("[Ledger] Ã¢ÂÂ Banco de ledger inicializado.")











# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



# OPERAÃÂÃÂES PRINCIPAIS



# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ



def get_wallet(user_id: str) -> dict:



    """Retorna a carteira completa do usuÃÂ¡rio."""



    conn = sqlite3.connect(DB_PATH)



    c = conn.cursor()



    c.execute(



        "SELECT coins, chips_llm, gpu_tokens, fuel, crystals, plan, plan_expires_at "



        "FROM users WHERE user_id = ?",



        (user_id,)



    )



    row = c.fetchone()



    conn.close()







    if not row:



        return {}







    return {



        "user_id": user_id,



        "coins":      row[0],



        "chips_llm":  row[1],



        "gpu_tokens": row[2],



        "fuel":       row[3],



        "crystals":   row[4],



        "plan":       row[5] or "free",



        "plan_expires_at": row[6],



    }











def can_afford(user_id: str, operation: str) -> tuple[bool, dict]:



    """



    Verifica se o usuÃÂ¡rio tem saldo suficiente para uma operaÃÂ§ÃÂ£o.



    Retorna (True/False, detalhes_do_custo).



    """



    cost = OPERATION_COSTS.get(operation, {})



    if not cost:



        return False, {"error": f"OperaÃÂ§ÃÂ£o '{operation}' nÃÂ£o reconhecida."}







    wallet = get_wallet(user_id)



    if not wallet:



        return False, {"error": "UsuÃÂ¡rio nÃÂ£o encontrado."}







    shortfalls = {}



    for currency, amount in cost.items():



        if wallet.get(currency, 0) < amount:



            shortfalls[currency] = {



                "needed": amount,



                "have": wallet.get(currency, 0),



                "missing": amount - wallet.get(currency, 0),



            }







    if shortfalls:



        return False, {"shortfalls": shortfalls, "cost": cost}







    return True, {"cost": cost}











def charge_operation(user_id: str, operation: str, metadata: Optional[dict] = None) -> dict:



    """



    Cobra as moedas de uma operaÃÂ§ÃÂ£o do usuÃÂ¡rio.



    Retorna {"success": True/False, "wallet": wallet_atualizada}.



    """



    affordable, details = can_afford(user_id, operation)



    if not affordable:



        return {"success": False, "reason": "Saldo insuficiente.", "details": details}







    cost = details["cost"]



    conn = sqlite3.connect(DB_PATH)



    c = conn.cursor()







    for currency, amount in cost.items():



        if currency in CURRENCY_TYPES:



            c.execute(



                f"UPDATE users SET {currency} = {currency} - ? WHERE user_id = ?",



                (amount, user_id)



            )



            # Registra a transaÃÂ§ÃÂ£o



            c.execute(



                "INSERT INTO transactions (user_id, operation, currency, amount, direction, metadata) "



                "VALUES (?, ?, ?, ?, 'debit', ?)",



                (user_id, operation, currency, amount, str(metadata or {}))



            )







    conn.commit()



    conn.close()







    logger.info(f"[Ledger] Ã°ÂÂÂ¸ {user_id} cobrado por '{operation}': {cost}")



    return {"success": True, "cost": cost, "wallet": get_wallet(user_id)}











def credit_user(user_id: str, currency: str, amount: int, reason: str = "credit") -> bool:



    """Adiciona moedas ao usuÃÂ¡rio (bÃÂ´nus, assinatura, etc.)."""



    if currency not in CURRENCY_TYPES:



        return False







    conn = sqlite3.connect(DB_PATH)



    c = conn.cursor()







    # Garante que o usuÃÂ¡rio existe



    c.execute(



        "INSERT OR IGNORE INTO users (user_id, coins, chips_llm, gpu_tokens, fuel, crystals) "



        "VALUES (?, 0, 0, 0, 0, 0)",



        (user_id,)



    )



    c.execute(



        f"UPDATE users SET {currency} = {currency} + ? WHERE user_id = ?",



        (amount, user_id)



    )



    c.execute(



        "INSERT INTO transactions (user_id, operation, currency, amount, direction) VALUES (?, ?, ?, ?, 'credit')",



        (user_id, reason, currency, amount)



    )



    conn.commit()



    conn.close()



    logger.info(f"[Ledger] Ã°ÂÂÂ° +{amount} {currency} para {user_id} ({reason})")



    return True











def grant_monthly_plan(user_id: str, plan: str = "free") -> dict:



    """



    Concede as moedas mensais do plano ao usuÃÂ¡rio.



    Chamado automaticamente no dia de renovaÃÂ§ÃÂ£o da assinatura.



    """



    grants = PLAN_MONTHLY_GRANTS.get(plan, PLAN_MONTHLY_GRANTS["free"])







    for currency in ["coins", "chips_llm", "gpu_tokens", "fuel", "crystals"]:



        amount = grants.get(currency, 0)



        if amount > 0:



            credit_user(user_id, currency, amount, reason=f"monthly_grant_{plan}")







    logger.info(f"[Ledger] Ã°ÂÂÂ ConcessÃÂ£o mensal do plano '{plan}' aplicada para {user_id}.")



    return grants











def get_transaction_history(user_id: str, limit: int = 50) -> list:



    """Retorna o histÃÂ³rico de transaÃÂ§ÃÂµes do usuÃÂ¡rio."""



    conn = sqlite3.connect(DB_PATH)



    c = conn.cursor()



    c.execute(



        "SELECT operation, currency, amount, direction, created_at, metadata "



        "FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",



        (user_id, limit)



    )



    rows = c.fetchall()



    conn.close()



    return [



        {"operation": r[0], "currency": r[1], "amount": r[2],



         "direction": r[3], "created_at": r[4], "metadata": r[5]}



        for r in rows



    ]











# Inicializa ao importar



init_ledger()







# ==========================================================



# GESTÃO DE USUÃRIOS



# ==========================================================




# ==========================================================
# GESTO DE USURIOS
# ==========================================================
def get_user_by_email(email: str) -> Optional[dict]:
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT user_id, email, password_hash FROM users WHERE email = ?', (email,))
        row = c.fetchone()
    if row:
        return {'user_id': row[0], 'email': row[1], 'password_hash': row[2]}
    return None

def create_user_record(user_id: str, email: str, password_hash: str):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO users (user_id, email, password_hash, coins, crystals, fuel, chips_llm, gpu_tokens, plan) VALUES (?, ?, ?, 500, 10, 50, 100, 20, ?)', (user_id, email, password_hash, 'free'))
        conn.commit()
    logger.info(f"[Ledger] Usuario criado: {email} ({user_id})")

