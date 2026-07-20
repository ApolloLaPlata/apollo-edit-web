import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'economy.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            coins INTEGER DEFAULT 1500,
            crystals INTEGER DEFAULT 300,
            fuel INTEGER DEFAULT 100
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            user_id TEXT,
            item_id TEXT,
            quantity INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, item_id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            user_id TEXT,
            status TEXT DEFAULT 'QUEUED',
            job_type TEXT,
            parameters TEXT,
            result_url TEXT,
            progress INTEGER DEFAULT 0,
            notified BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        c.execute('ALTER TABLE jobs ADD COLUMN notified BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.commit()
    
    # Check if default user exists
    c.execute('SELECT * FROM users WHERE user_id = "default_user"')
    if not c.fetchone():
        c.execute('INSERT INTO users (user_id, coins, crystals, fuel) VALUES ("default_user", 1500, 300, 100)')
        c.execute('INSERT INTO inventory (user_id, item_id, quantity) VALUES ("default_user", "nitro_t4", 1)')
        conn.commit()
    conn.close()

def get_balance(user_id="default_user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT coins, crystals, fuel FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"coins": row[0], "crystals": row[1], "fuel": row[2]}
    return {"coins": 0, "crystals": 0, "fuel": 0}

def get_inventory(user_id="default_user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT item_id, quantity FROM inventory WHERE user_id = ? AND quantity > 0', (user_id,))
    rows = c.fetchall()
    conn.close()
    inventory = {}
    for item_id, quantity in rows:
        inventory[item_id] = quantity
    return inventory

def deduct_currency(amount, currency_type="coins", user_id="default_user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f'SELECT {currency_type} FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    if not row or row[0] < amount:
        conn.close()
        return False
    
    c.execute(f'UPDATE users SET {currency_type} = {currency_type} - ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()
    return True

def add_currency(amount, currency_type="coins", user_id="default_user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(f'UPDATE users SET {currency_type} = {currency_type} + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()
    return True

def add_item(item_id, quantity=1, user_id="default_user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO inventory (user_id, item_id, quantity) VALUES (?, ?, ?) ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?', 
              (user_id, item_id, quantity, quantity))
    conn.commit()
    conn.close()
    return True

def use_item(item_id, user_id="default_user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    row = c.fetchone()
    if not row or row[0] <= 0:
        conn.close()
        return False
    
    c.execute('UPDATE inventory SET quantity = quantity - 1 WHERE user_id = ? AND item_id = ?', (user_id, item_id))
    conn.commit()
    conn.close()
    return True

def get_all_users_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*), SUM(coins), SUM(crystals) FROM users')
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "total_users": row[0] or 0,
            "total_coins": row[1] or 0,
            "total_crystals": row[2] or 0
        }
    return {"total_users": 0, "total_coins": 0, "total_crystals": 0}

# Job Management Functions
def create_job(job_id, user_id, job_type, parameters):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO jobs (job_id, user_id, status, job_type, parameters) 
        VALUES (?, ?, 'QUEUED', ?, ?)
    ''', (job_id, user_id, job_type, json.dumps(parameters)))
    conn.commit()
    conn.close()

def update_job_status(job_id, status, progress=None, result_url=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = 'UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP'
    params = [status]
    
    if progress is not None:
        query += ', progress = ?'
        params.append(progress)
        
    if result_url is not None:
        query += ', result_url = ?'
        params.append(result_url)
        
    query += ' WHERE job_id = ?'
    params.append(job_id)
    
    c.execute(query, tuple(params))
    conn.commit()
    conn.close()

def get_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT job_id, status, job_type, result_url, progress, created_at, parameters FROM jobs WHERE job_id = ?', (job_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "job_id": row[0],
            "status": row[1],
            "type": row[2],
            "result_url": row[3],
            "progress": row[4],
            "created_at": row[5],
            "parameters": json.loads(row[6]) if row[6] else {}
        }
    return None

def get_user_jobs(user_id="default_user", limit=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT job_id, status, job_type, result_url, progress, created_at, parameters FROM jobs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    jobs = []
    for row in rows:
        jobs.append({
            "job_id": row[0],
            "status": row[1],
            "type": row[2],
            "result_url": row[3],
            "progress": row[4],
            "created_at": row[5],
            "parameters": json.loads(row[6]) if row[6] else {}
        })
    return jobs

def get_unnotified_jobs(user_id="default_user"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT job_id, job_type, result_url FROM jobs WHERE user_id = ? AND status = 'COMPLETED' AND notified = 0", (user_id,))
    rows = c.fetchall()
    conn.close()
    jobs = []
    for row in rows:
        jobs.append({
            "job_id": row[0],
            "type": row[1],
            "result_url": row[2]
        })
    return jobs

def mark_jobs_notified(job_ids):
    if not job_ids: return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    placeholders = ','.join('?' * len(job_ids))
    c.execute(f"UPDATE jobs SET notified = 1 WHERE job_id IN ({placeholders})", tuple(job_ids))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
