import os
import sys
import json
import glob
import subprocess
import threading
import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class JobNotifier:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        if job_id in self.active_connections:
            try:
                self.active_connections[job_id].remove(websocket)
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]
            except ValueError:
                pass

    async def broadcast(self, job_id: str, message: dict):
        if job_id in self.active_connections:
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

job_notifier = JobNotifier()

app = FastAPI(title="Apollo Studio Web Engine")

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_UI_DIR = os.path.join(BASE_DIR, "web_ui")

# VariÃ¡vel Global de Workspace (injetada pelo apollo_studio.py)
CURRENT_WORKSPACE = "Default"
CURRENT_WORKSPACE_PATH = ""

# Modelos
class TTSRequest(BaseModel):
    texto: str
    voz: str
    engine: str

class CopilotRequest(BaseModel):
    prompt: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Retorna o Hub Central traduzido"""
    lang = request.cookies.get("apollo_lang", "pt")
    
    if lang in ["en", "es", "zh", "ja", "ru"]:
        hub_path = os.path.join(WEB_UI_DIR, lang, "apollo_os.html")
        if not os.path.exists(hub_path):
            hub_path = os.path.join(WEB_UI_DIR, "apollo_os.html")
    else:
        hub_path = os.path.join(WEB_UI_DIR, "apollo_os.html")
        
    if os.path.exists(hub_path):
        response = HTMLResponse(content=open(hub_path, 'r', encoding='utf-8').read(), status_code=200)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return HTMLResponse(content="<h1>Hub nÃ£o encontrado</h1>", status_code=404)

@app.get("/apollo-master", response_class=HTMLResponse)
async def read_apollo_master():
    """Rota Secreta do Master Admin"""
    path = os.path.join(WEB_UI_DIR, "apollo-master", "index.html")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content="<h1>Admin não encontrado</h1>", status_code=404)

@app.get("/admin", response_class=HTMLResponse)
async def read_admin():
    path = os.path.join(WEB_UI_DIR, "admin.html")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/admin_login", response_class=HTMLResponse)
async def read_admin_login():
    path = os.path.join(WEB_UI_DIR, "admin_login.html")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/apollo-master/login", response_class=HTMLResponse)
async def read_apollo_master_login():
    """Rota Secreta de Login do Master Admin"""
    path = os.path.join(WEB_UI_DIR, "apollo-master", "login.html")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(content="<h1>Login nÃ£o encontrado</h1>", status_code=404)

@app.get("/{filename}.html")
async def serve_html(request: Request, filename: str):
    """Serve arquivos HTML com traduÃ§Ã£o nativa baseada em cookie"""
    lang = request.cookies.get("apollo_lang", "pt")
    
    response = None
    if lang in ["en", "es", "zh", "ja", "ru"]:
        lang_path = os.path.join(WEB_UI_DIR, lang, f"{filename}.html")
        if os.path.exists(lang_path):
            response = FileResponse(lang_path)
            
    if response is None:
        pt_path = os.path.join(WEB_UI_DIR, f"{filename}.html")
        if os.path.exists(pt_path):
            response = FileResponse(pt_path)
        else:
            raise HTTPException(status_code=404, detail="Page not found")
            
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

class PresignedURLRequest(BaseModel):
    filename: str
    content_type: str

@app.post("/api/s3/presigned")
async def generate_presigned_url(req: PresignedURLRequest):
    """
    Gera uma Presigned URL (S3 / Cloudflare R2) para que o frontend
    faÃ§a o upload de arquivos pesados (ex: 2GB) direto do navegador,
    sem sobrecarregar o servidor VPS com trÃ¡fego.
    """
    # ATENÃÃO: As credenciais devem vir do config.json do Workspace no futuro
    # Por seguranÃ§a, estamos mockando a configuraÃ§Ã£o atÃ© o usuÃ¡rio prover as chaves R2/S3
    AWS_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "MOCK_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("S3_SECRET_KEY", "MOCK_SECRET_KEY")
    ENDPOINT_URL = os.getenv("S3_ENDPOINT", "https://MOCK-R2.cloudflarestorage.com")
    BUCKET_NAME = os.getenv("S3_BUCKET", "apollo-edit-pro")
    
    s3_client = boto3.client(
        's3',
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="auto"
    )
    
    try:
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': f"uploads/{req.filename}",
                'ContentType': req.content_type
            },
            ExpiresIn=3600 # VÃ¡lido por 1 hora
        )
        return {"success": True, "presigned_url": response, "file_key": f"uploads/{req.filename}"}
    except ClientError as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# =====================================================================
# ### INÍCIO DA LÓGICA DE ADMINISTRAÇÃO E AUTENTICAÇÃO (SAAS) ###
# =====================================================================
# AVISO DE REFATORAÇÃO FUTURA: Estas rotas controlam o painel Master,
# chaves de API e saldo de usuários. Futuramente mover para: /src/api/admin_routes.py
# =====================================================================

class AdminLoginRequest(BaseModel):
    password: str

@app.post("/api/admin/login")
async def admin_login(req: AdminLoginRequest):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        master_pw = cm.get("admin_config.master_password", "ApolloAdmin2026")
        
        result = await llm_cascade.generate_script(
            user_id=1, 
            theme=req.input_text, 
            modality=req.format, 
            tone=req.tone,
            profile_context=req.profile_context,
            model_choice=req.model_choice
        )
        return {"success": True, "text": result}
        
        if req.password == master_pw:
            return {"success": True, "token": "apollo_admin_token_secure_v1"}
        return {"success": False, "error": "Senha incorreta"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/admin/dashboard")
async def admin_get_dashboard(token: str = None):
    try:
        from config_manager import ConfigManager
        from backend.financial_agent import economy_db
        from backend.cloud_tools import account_manager
        
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        
        eco_stats = economy_db.get_all_users_stats()
        estimated_revenue = eco_stats.get("total_coins", 0) * 0.01
        
        total_api_spend = 0.0
        api_config = cm.get("api_config", {})
        for provider, p_data in api_config.items():
            keys = p_data.get("api_keys", [])
            for k in keys:
                total_api_spend += float(k.get("estimated_spend", 0.0))
                
        cloud_accounts = account_manager.update_balances()
        total_cloud_spend = sum([float(a.get("last_spend", 0.0)) for a in cloud_accounts])
        
        profit = estimated_revenue - total_api_spend - total_cloud_spend
        
        from chat_ai_manager import ChatAIManager
        ai = ChatAIManager(cm)
        
        prompt = f"""Você é o Agente Financeiro Autônomo.
Resumo atual do sistema:
- Usuários Totais: {eco_stats.get("total_users")}
- Receita Estimada (Coins): ${estimated_revenue:.2f}
- Custo de APIs de IA: ${total_api_spend:.2f}
- Custo de Computação Cloud: ${total_cloud_spend:.2f}
- Lucro Estimado: ${profit:.2f}

Escreva um relatório de 1 parágrafo focado na saúde financeira. Seja direto e analítico."""
        
        ai_res = ai.send_message("agente_financeiro", prompt)
        ai_report = ai_res.get("text", "Erro ao conectar com a IA Financeira.")
        
        return {
            "success": True, 
            "stats": {
                "total_users": eco_stats.get("total_users", 0),
                "profit_estimated": f"${profit:.2f}",
                "credits_spent": f"${total_api_spend + total_cloud_spend:.2f}",
                "api_spend": total_api_spend,
                "cloud_spend": total_cloud_spend,
                "renders_today": 0
            },
            "financial_ai_report": ai_report,
            "cloud_accounts": cloud_accounts
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/admin/market_analyst/recommendations")
async def market_analyst_recommendations(token: str = None):
    try:
        from config_manager import ConfigManager
        from backend.financial_agent import economy_db
        import random
        
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        eco_stats = economy_db.get_all_users_stats()
        
        # In a real scenario, this could query an LLM for structured JSON.
        # For immediate actionable market solutions, we dynamically generate them based on basic rules:
        recommendations = []
        
        # Rule 1: High API Cost
        recommendations.append({
            "id": "high_dalle_cost",
            "type": "warning",
            "title": "Custo Elevado: Geração Visual",
            "description": "Custo das APIs de imagem está acima da média. Recomendação do Agente: Alterar fallback para infraestrutura Modal local (Flux). Economia estimada: R$ 450/dia.",
            "action_label": "Redirecionar para Modal",
            "action_payload": {"action": "set_image_fallback", "value": "modal"}
        })
        
        # Rule 2: Engagement Spike
        recommendations.append({
            "id": "engagement_spike",
            "type": "opportunity",
            "title": "Pico de Engajamento: Jogo de Corrida",
            "description": f"Retenção no minigame subiu. Usuários totais: {eco_stats.get('total_users', 0)}. Recomendação: Aumentar o custo em 'Gasolina' dos renders para forçar mais tempo de gameplay (AdSense).",
            "action_label": "Aumentar Custo (+5%)",
            "action_payload": {"action": "increase_gas_cost", "value": 1.05}
        })
        
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        return {"success": False, "error": str(e)}

class MarketActionPayload(BaseModel):
    token: str = None
    action: str
    value: str | float | int

@app.post("/api/admin/market_analyst/apply")
async def market_analyst_apply(payload: MarketActionPayload):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        
        if payload.action == "set_image_fallback":
            # Update config
            cm.set("image_fallback_engine", payload.value)
            return {"success": True, "message": f"Motor de fallback alterado para {payload.value}"}
            
        elif payload.action == "increase_gas_cost":
            current_mult = cm.get("gas_cost_multiplier", 1.0)
            new_mult = current_mult * float(payload.value)
            cm.set("gas_cost_multiplier", new_mult)
            return {"success": True, "message": f"Multiplicador de gasolina ajustado para {new_mult:.2f}x"}
            
        return {"success": False, "error": "Ação desconhecida."}
    except Exception as e:
        return {"success": False, "error": str(e)}

class UserRoleRequest(BaseModel):
    token: str = None
    user_id: str
    new_role: str

@app.get("/api/master/users")
async def master_get_users(token: str = None):
    try:
        from backend.financial_agent import economy_db
        import sqlite3
        conn = sqlite3.connect(economy_db.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, plan FROM users")
        rows = c.fetchall()
        conn.close()
        
        users_list = []
        for r in rows:
            users_list.append({
                "id": r[0],
                "username": r[0],
                "email": f"{r[0]}@apollo.local",
                "role": r[1]
            })
            
        return {"success": True, "users": users_list}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/master/users/role")
async def master_update_user_role(req: UserRoleRequest):
    try:
        from backend.financial_agent import subscription_manager
        import sqlite3
        from backend.financial_agent import economy_db
        
        if req.new_role == "Banned":
            # Ban logic: set coins to 0, or add a ban flag
            conn = sqlite3.connect(economy_db.DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE users SET coins = 0, plan = 'Banned' WHERE user_id = ?", (req.user_id,))
            conn.commit()
            conn.close()
        else:
            subscription_manager.activate_plan(req.user_id, req.new_role.lower())
            
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/admin/keys")
async def admin_get_keys(token: str = None):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        return {"success": True, "api_config": cm.get("api_config", {})}
    except Exception as e:
        return {"success": False, "error": str(e)}

class APIKeysUpdateRequest(BaseModel):
    token: str = None
    provider: str
    keys: list

@app.post("/api/admin/keys/update")
async def admin_update_keys(req: APIKeysUpdateRequest):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        
        # Verify provider exists or initialize it
        api_config = cm.get("api_config", {})
        if req.provider not in api_config:
            api_config[req.provider] = {}
            
        # Update just the keys array for this provider
        api_config[req.provider]["api_keys"] = req.keys
        
        # Save back
        cm.set("api_config", api_config)
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

class CloudAccountRequest(BaseModel):
    provider: str
    name: str
    workspace: str = ""
    token_id: str
    token_secret: str

@app.get("/api/admin/cloud_accounts")
async def admin_get_cloud_accounts():
    try:
        from backend.cloud_tools import account_manager
        accounts = account_manager.update_balances()
        safe_accounts = []
        for acc in accounts:
            safe_acc = dict(acc)
            # Mask the secret token
            if safe_acc.get("token_secret") and len(safe_acc["token_secret"]) > 4:
                safe_acc["token_secret"] = "********" + safe_acc["token_secret"][-4:]
            else:
                safe_acc["token_secret"] = "***"
            safe_accounts.append(safe_acc)
        return {"success": True, "accounts": safe_accounts}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/admin/cloud_accounts")
async def admin_add_cloud_account(req: CloudAccountRequest):
    try:
        from backend.cloud_tools import account_manager
        acc = account_manager.add_account(req.provider, req.name, req.workspace, req.token_id, req.token_secret)
        return {"success": True, "account_id": acc["id"]}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/admin/cloud_accounts/{acc_id}")
async def admin_delete_cloud_account(acc_id: str):
    try:
        from backend.cloud_tools import account_manager
        account_manager.delete_account(acc_id)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/admin/cloud_accounts/{acc_id}/activate")
async def admin_activate_cloud_account(acc_id: str, provider: str):
    try:
        from backend.cloud_tools import account_manager
        account_manager.toggle_active(acc_id, provider)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

class UserCreditRequest(BaseModel):
    token: str
    user_id: int
    amount: int
    action: str # "add" or "deduct"

@app.get("/api/admin/users")
async def admin_get_users(token: str = None):
    try:
        import user_database
        users = user_database.get_all_users()
        return {"success": True, "users": users}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/admin/users/credits")
async def admin_manage_credits(req: UserCreditRequest):
    try:
        import user_database
        if req.action == "add":
            res = user_database.add_credits(req.user_id, req.amount)
        else:
            res = user_database.deduct_credits(req.user_id, req.amount)
            
        if res:
            return {"success": True}
        return {"success": False, "error": "Falha ao gerenciar crÃ©ditos"}
    except Exception as e:
        return {"success": False, "error": str(e)}

class NewUserRequest(BaseModel):
    token: str
    username: str
    password: str
    initial_credits: int = 100

@app.post("/api/admin/users/create")
async def admin_create_user(req: NewUserRequest):
    try:
        import user_database
        res = user_database.create_user(req.username, req.password, req.initial_credits)
        if res:
            return {"success": True}
        return {"success": False, "error": "UsuÃ¡rio jÃ¡ existe ou erro no banco"}
    except Exception as e:
        return {"success": False, "error": str(e)}
        
# --- FIM ROTAS DE ADMINISTRAÃÃO ---

# =====================================================================
# ### INÍCIO DA LÓGICA DO PAINEL DO USUÁRIO E GAMIFICAÇÃO ###
# =====================================================================
# AVISO DE REFATORAÇÃO FUTURA: Perfil, experiência, inventário e itens RPG.
# Futuramente mover para: /src/api/user_routes.py e /src/api/rpg_routes.py
# =====================================================================

@app.get("/api/user/profile")
async def get_user_profile():
    import user_database
    conn = user_database.get_connection()
    cursor = conn.cursor()
    
    # Busca os dados base do usuário (assumindo ID 1 como master provisório)
    cursor.execute("""
        SELECT username, credits, role, level, xp, country, rank_points, is_banned
        FROM users WHERE id = 1
    """)
    user = cursor.fetchone()
    
    # Se o usuário não existir (banco recém-criado), criamos o usuário admin
    if not user:
        user_database.create_user("Admin", "admin123", 5000, "Master")
        cursor.execute("UPDATE users SET level = 10, xp = 1500, country = 'BR' WHERE id = 1")
        conn.commit()
        cursor.execute("""
            SELECT username, credits, role, level, xp, country, rank_points, is_banned
            FROM users WHERE id = 1
        """)
        user = cursor.fetchone()
        
    username, credits, role, level, xp, country, rank_points, is_banned = user
    
    # Ler saldos de gas e cristais do banco de dados
    cursor.execute("SELECT gas, crystals FROM users WHERE id = 1")
    currency_row = cursor.fetchone()
    gas = currency_row[0] if currency_row else 100
    cristais = currency_row[1] if currency_row else 0

    # Busca os cosméticos desbloqueados no inventário
    cursor.execute("""
        SELECT s.name, s.type, s.id
        FROM user_inventory i
        JOIN store_items s ON i.item_id = s.id
        WHERE i.user_id = 1
    """)
    inventory = cursor.fetchall()
    unlocked_cosmetics = [item[2] for item in inventory if item[1] == 'border']

    # Busca cosméticos equipados
    cursor.execute("""
        SELECT equipped_border_id, equipped_title_id
        FROM user_equipped WHERE user_id = 1
    """)
    equipped = cursor.fetchone()
    equipped_border = equipped[0] if equipped else None
    
    # Fetch system settings for module access and globals
    cursor.execute("SELECT setting_key, setting_value FROM system_settings")
    module_settings = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()

    return {
        "name": username,
        "avatar": f"https://ui-avatars.com/api/?name={username.replace(' ', '+')}&background=8b5cf6&color=fff&size=128&font-weight=bold",
        "credits": credits,
        "gas": gas,
        "cristais": cristais,
        "is_hacker": role.lower() == 'hacker',
        "is_pro": role.lower() == 'pro',
        "is_master": role.lower() == 'master',
        "is_banned": bool(is_banned),
        "role": role,
        "xp_litros": xp,
        "level": level,
        "rank_global": f"#{max(1, 1000 - rank_points)}",
        "pais": country,
        "unlocked_cosmetics": unlocked_cosmetics,
        "equipped_border": equipped_border,
        "module_settings": module_settings
    }

class LogVisitRequest(BaseModel):
    page_name: str

@app.post("/api/log_visit")
async def log_page_visit_endpoint(req: LogVisitRequest):
    import user_database
    # Assumindo user ID 1 localmente
    res = user_database.log_page_visit(1, req.page_name)
    
    # Retornar settings de página para que o auth.js possa aplicar bloqueios de acesso
    try:
        conn = user_database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT setting_key, setting_value FROM system_settings WHERE setting_key LIKE 'page_%'")
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
    except Exception:
        settings = {}
    
    return {"success": res, "settings": settings}

@app.post("/api/rpg/buy_item")
async def buy_item(req: Request):
    check_user_status()
    try:
        data = await req.json()
        item_id_str = data.get("item_id")
        
        import user_database
        conn = user_database.get_connection()
        cursor = conn.cursor()
        
        # Obter custo do item (Mock) - Poderia vir do banco se populado
        cost = data.get("cost", 0)
        
        # Simular desconto de cristais (Como nÃ£o temos coluna cristais, vamos usar dummy success)
        cursor.execute("INSERT INTO user_inventory (user_id, item_id) VALUES (1, ?)", (item_id_str,))
        
        # Equipar automaticamente ao comprar
        cursor.execute("SELECT user_id FROM user_equipped WHERE user_id = 1")
        if cursor.fetchone():
            cursor.execute("UPDATE user_equipped SET equipped_border_id = ? WHERE user_id = 1", (item_id_str,))
        else:
            cursor.execute("INSERT INTO user_equipped (user_id, equipped_border_id) VALUES (1, ?)", (item_id_str,))
            
        conn.commit()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Item comprado e equipado!"})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

@app.post("/api/rpg/equip")
async def equip_item(req: Request):
    check_user_status()
    try:
        data = await req.json()
        item_id_str = data.get("item_id")
        type = data.get("type", "border")
        
        import user_database
        conn = user_database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM user_equipped WHERE user_id = 1")
        if cursor.fetchone():
            if type == 'border':
                cursor.execute("UPDATE user_equipped SET equipped_border_id = ? WHERE user_id = 1", (item_id_str,))
        else:
            if type == 'border':
                cursor.execute("INSERT INTO user_equipped (user_id, equipped_border_id) VALUES (1, ?)", (item_id_str,))
                
        conn.commit()
        conn.close()
        
        return JSONResponse({"success": True, "message": "Item equipado!"})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

class ChatMessage(BaseModel):
    message: str

def check_feature(feature_key: str):
    """Verifica no BD se a ferramenta foi desligada (kill-switch)."""
    import user_database
    conn = user_database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = ?", (feature_key,))
    res = cursor.fetchone()
    conn.close()
    if res and res[0] == 'off':
        raise HTTPException(status_code=503, detail="Ferramenta em manutenção pelo Administrador.")
    return True

def check_user_status(user_id: int = 1):
    """Verifica se o usuário está banido."""
    import user_database
    conn = user_database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    if res and res[0]:
        raise HTTPException(status_code=403, detail="Acesso Bloqueado. Conta suspensa.")
    return True

@app.post("/api/chat")
async def chat_interaction(msg: ChatMessage):
    check_user_status()
    check_feature('feature_grok') # Exemplo: amarrado a feature_grok
    import time
    time.sleep(1) # Simular latÃªncia
    return {
        "response": f"Processando sua requisiÃ§Ã£o: '{msg.message}'. Como Apollo Copilot da V2, estou configurando os agentes para iniciar a construÃ§Ã£o do seu vÃ­deo utilizando os bancos de dados do seu canal..."
    }

# =====================================================================
# ### INÍCIO DA LÓGICA DE PROXY (MOTORES EXTERNOS / LIGHTNING AI) ###
# =====================================================================
# AVISO DE REFATORAÇÃO FUTURA: Estes endpoints bypassam o CORS para falar
# com o Lightning AI e geradores de imagem/áudio externos.
# Futuramente mover para: /src/api/proxy_routes.py
# =====================================================================

@app.post("/api/lightning_proxy")
async def lightning_proxy(request: Request):
    try:
        import requests
        data = await request.json()
        headers = {
            "Authorization": request.headers.get("Authorization", ""),
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://lightning.ai/api/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=30
        )
        
        try:
            resp_json = response.json()
        except Exception:
            resp_json = {"error": {"message": response.text}}
            
        return JSONResponse(status_code=response.status_code, content=resp_json)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": {"message": str(e)}})

@app.post("/api/media_proxy")
async def media_proxy(request: Request):
    """
    Proxy Universal para o "Pendrive Mágico da Nuvem".
    Recebe do frontend a URL alvo, os cabeçalhos e o corpo da requisição.
    Bypassa o CORS para gerar Imagem, Áudio, Vídeo e Música em qualquer API.
    """
    try:
        import requests
        data = await request.json()
        
        target_url = data.pop("target_url", "")
        if not target_url:
            return JSONResponse(status_code=400, content={"error": "target_url não fornecida"})
            
        target_headers = data.pop("target_headers", {})
        
        # Faz a requisição para a API externa
        response = requests.post(
            target_url,
            json=data,
            headers=target_headers,
            timeout=120 # Timeout maior para geração de mídia pesada
        )
        
        try:
            resp_json = response.json()
        except:
            resp_json = {"raw_content": response.text}
            
        return JSONResponse(status_code=response.status_code, content=resp_json)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# =====================================================================
# ### INÍCIO DA LÓGICA DO BOT DE WHATSAPP E CHATBOT (LLM CASCADE) ###
# =====================================================================
# AVISO DE REFATORAÇÃO FUTURA: Controle do Cão de Guarda (Node.js) e do
# LLM Cascade para responder mensagens via Web ou WhatsApp.
# Futuramente mover para: /src/api/whatsapp_routes.py
# =====================================================================

@app.get("/api/whatsapp/status")
async def whatsapp_status():
    try:
        import urllib.request
        import json
        req = urllib.request.Request("http://127.0.0.1:5001/api/status")
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode())
            return {"running": True, "status": data.get("status"), "qr": data.get("qr")}
    except Exception:
        return {"running": False, "status": "OFFLINE"}

@app.post("/api/whatsapp/start")
async def start_whatsapp():
    import subprocess
    import os
    bat_path = os.path.join(CURRENT_WORKSPACE_PATH, "start_whatsapp.bat")
    # Usa START do Windows para abrir em janela oculta ou minimizada se desejar, 
    # mas o cmd /c com CREATE_NO_WINDOW faria ele rodar sem tela nenhuma. 
    # Como o bat tem "pause", melhor rodar escondido sem a janela travando,
    # Ou só executar o node direto.
    # Vamos rodar via subprocess sem janela para integrar ao fundo:
    # subprocess.Popen(["node", "index.js"], cwd=os.path.join(CURRENT_WORKSPACE_PATH, "whatsapp_bot"), creationflags=subprocess.CREATE_NO_WINDOW)
    # Mas como o bat já existe, executamos ele minimizado:
    subprocess.Popen(f'start /min "WhatsApp Bridge" cmd /c "{bat_path}"', shell=True)
    return {"success": True}

unified_chat_history = []
whatsapp_last_contact = None

@app.get("/api/chat/sync")
async def chat_sync():
    return {"success": True, "history": unified_chat_history}

@app.post("/api/chat/send")
async def chat_send(request: Request):
    try:
        data = await request.json()
        msg_text = data.get("message")
        agent_id = data.get("agent_id", "PRIME")
        system_prompt = data.get("system_prompt", "")
        api_key = data.get("api_key")
        
        from config_manager import ConfigManager
        
        if agent_id == "PRIME":
            cm = ConfigManager(os.path.join(BASE_DIR, "config.json"))
        else:
            cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
            
        if agent_id == "PRIME":
            unified_chat_history.append({"role": "user", "content": msg_text})
            
            # Espelhamento: Envia a pergunta que foi digitada no painel web para o WhatsApp do ADMIN
            admin_group_id = cm.get("whatsapp_group_id")
            if admin_group_id:
                try:
                    import urllib.request
                    import json
                    req = urllib.request.Request("http://127.0.0.1:5001/api/send", method="POST")
                    req.add_header('Content-Type', 'application/json')
                    out_data = json.dumps({"to": admin_group_id, "message": f"🤖 [Painel Web]: {msg_text}"}).encode('utf-8')
                    urllib.request.urlopen(req, data=out_data)
                except Exception as e:
                    print(f"[WhatsApp] Falha ao enviar cópia da pergunta web: {e}")
        
        if api_key:
            chat_cfg = cm.get("api_config.lightning_chat", {})
            if chat_cfg.get("api_key") != api_key:
                chat_cfg["api_key"] = api_key
                cm.set("api_config.lightning_chat", chat_cfg)
            
        # O histórico precisa ser o unificado se for o PRIME
        prompt_with_history = msg_text
        if agent_id == "PRIME" and len(unified_chat_history) > 1:
            history_text = "\n".join([f"{item['role'].upper()}: {item['content']}" for item in unified_chat_history[-10:]])
            prompt_with_history = f"Histórico Recente:\n{history_text}\n\nMensagem Atual:\n{msg_text}"
            
        # O painel Web é usado apenas pelo admin (Chefe). Conectando direto no Lightning AI.
        import requests
        chat_cfg = cm.get("api_config", {}).get("lightning_chat", {})
        used_api_key = api_key if api_key else chat_cfg.get("api_key", "")
        base_url = chat_cfg.get("base_url", "https://lightning.ai/api/v1/chat/completions")
        if base_url.endswith("v1/"):
            base_url = "https://lightning.ai/api/v1/chat/completions"
            
        response_text = ""
        if not used_api_key:
            response_text = "⚠️ [Apollo Prime] A Chave da API da Lightning não está configurada neste Canal."
        else:
            headers = {
                "Authorization": f"Bearer {used_api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "nvidia-nemotron-3-ultra-550b-a55b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_with_history}
                ]
            }
            try:
                resp = requests.post(base_url, json=payload, headers=headers, timeout=30)
                if resp.status_code == 200:
                    resp_json = resp.json()
                    response_text = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    response_text = f"⚠️ [Lightning API Error] Falha de comunicação (Status {resp.status_code})"
            except Exception as e:
                response_text = f"⚠️ [Network Error] Falha ao contatar a Lightning AI: {str(e)}"
        
        if response_text:
            if agent_id == "PRIME":
                unified_chat_history.append({"role": "model", "content": response_text})
                # Encaminhar resposta pro WhatsApp do ADMIN
                admin_group_id = cm.get("whatsapp_group_id")
                if admin_group_id:
                    try:
                        import urllib.request
                        import json
                        req = urllib.request.Request("http://127.0.0.1:5001/api/send", method="POST")
                        req.add_header('Content-Type', 'application/json')
                        out_data = json.dumps({"to": admin_group_id, "message": response_text}).encode('utf-8')
                        urllib.request.urlopen(req, data=out_data)
                    except Exception as e:
                        print(f"[WhatsApp] Falha ao enviar cópia web: {e}")
            
            return {"success": True, "reply": response_text}
        return {"success": False, "error": "No response"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    global whatsapp_last_contact
    try:
        msg = await request.json()
        from config_manager import ConfigManager
        
        sender = msg.get("from", "")
        recipient = msg.get("to", "")
        
        # Se a mensagem foi digitada pelo dono do celular, o ID do Grupo está no 'to'. 
        # Se foi digitada por outra pessoa no grupo, está no 'from'.
        group_id = recipient if "@g.us" in recipient else sender
        
        whatsapp_last_contact = group_id
        user_text = msg.get("body", "")
        
        # Procura qual workspace é o dono desse group_id
        target_workspace_path = None
        
        # 1. Verifica o workspace ADMIN primeiro (BASE_DIR)
        cm_admin = ConfigManager(os.path.join(BASE_DIR, "config.json"))
        if cm_admin.get("whatsapp_group_id") == group_id:
            target_workspace_path = BASE_DIR
        
        # 2. Verifica o workspace principal aberto
        if not target_workspace_path:
            cm_main = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
            if cm_main.get("whatsapp_group_id") == group_id:
                target_workspace_path = CURRENT_WORKSPACE_PATH
            
        # 3. Verifica os sub-workspaces
        if not target_workspace_path:
            workspaces_dir = os.path.join(BASE_DIR, "Workspaces")
            if os.path.exists(workspaces_dir):
                for ws in os.listdir(workspaces_dir):
                    ws_path = os.path.join(workspaces_dir, ws)
                    if os.path.isdir(ws_path):
                        cfg_path = os.path.join(ws_path, "config.json")
                        if os.path.exists(cfg_path):
                            try:
                                with open(cfg_path, 'r', encoding='utf-8') as f:
                                    cfg = json.load(f)
                                    if cfg.get("whatsapp_group_id") == group_id:
                                        target_workspace_path = ws_path
                                        break
                            except:
                                pass
                                
        # 4. Se não encontrou NENHUM workspace dono deste grupo, ignora a mensagem silenciosamente
        if not target_workspace_path:
            print(f"[Aviso] Mensagem ignorada de grupo ou contato desconhecido/não configurado: {group_id}")
            return {"success": True, "message": "Ignored - unknown group"}
                            
        cm = ConfigManager(os.path.join(target_workspace_path, "config.json"))     
        
        # O unified_chat_history reflete o chat do painel ADMIN (Apollo Prime)
        if target_workspace_path == BASE_DIR:
            unified_chat_history.append({"role": "user", "content": user_text})
        
        system_prompt = cm.get("ai_system_prompt", "Você é o assistente virtual deste canal.")
        system_prompt += "\n\nATENÇÃO: Você está falando com o usuário através de um grupo do WhatsApp. Responda de forma direta, irônica e concisa, como o robô do sistema. Evite formatações longas."
        
        # Carrega histórico persistente do canal (usaremos uma versão simplificada aqui)
        prompt_with_history = f"Mensagem Atual do Usuário:\n{user_text}"
        if target_workspace_path == BASE_DIR:
            history_text = "\n".join([f"{item['role'].upper()}: {item['content']}" for item in unified_chat_history[-10:]])
            prompt_with_history = f"Histórico Recente:\n{history_text}\n\n{prompt_with_history}"
        
        # ========================================================
        # ROBO DE ATENDIMENTO: CONECTANDO DIRETO AO LIGHTNING AI
        # ========================================================
        import requests
        chat_cfg = cm.get("api_config", {}).get("lightning_chat", {})
        api_key = chat_cfg.get("api_key", "")
        # Fallback de seguranca caso o config.json esteja quebrado (como estava antes)
        base_url = chat_cfg.get("base_url", "https://lightning.ai/api/v1/chat/completions")
        if base_url.endswith("v1/"):
            base_url = "https://lightning.ai/api/v1/chat/completions"
            
        response_text = ""
        if not api_key:
            response_text = "⚠️ [Apollo Prime] A Chave da API da Lightning não está configurada neste Canal. Configure no Painel Web primeiro."
        else:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "nvidia-nemotron-3-ultra-550b-a55b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_with_history}
                ]
            }
            try:
                resp = requests.post(base_url, json=payload, headers=headers, timeout=30)
                if resp.status_code == 200:
                    resp_json = resp.json()
                    response_text = resp_json.get("choices", [{}])[0].get("message", {}).get("content", "Erro vazio da API.")
                else:
                    response_text = f"⚠️ [Lightning API Error] Falha de comunicação (Status {resp.status_code})"
            except Exception as e:
                response_text = f"⚠️ [Network Error] Falha ao contatar a Lightning AI: {str(e)}"
            
        unified_chat_history.append({"role": "model", "content": response_text})
        import urllib.request
        import json
        req = urllib.request.Request("http://127.0.0.1:5001/api/send", method="POST")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"to": group_id, "message": response_text}).encode('utf-8')
        try:
            urllib.request.urlopen(req, data=data)
        except Exception as e:
            print(f"[WhatsApp] Falha ao responder pro Node.js: {e}")
            
        # Tenta enviar a mesma mensagem para o Painel Web, se ele estiver aberto (broadcast local)
        # O histórico unificado já fez isso acima, então o painel será atualizado via sync
        
        return {"success": True, "reply": response_text}
    except Exception as e:
        print(f"[WhatsApp Webhook Error] {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/whatsapp/gerar_grupo")
async def gerar_grupo_whatsapp(request: Request):
    """
    Endpoint chamado pelo painel Web para gerar um grupo no Node.js
    e atrelar o ID desse grupo ao ADMIN do site (Apollo Edit Web).
    """
    try:
        import urllib.request
        import json
        
        # Cria o grupo com o nome do ADMIN
        req = urllib.request.Request("http://127.0.0.1:5001/api/create_group", method="POST")
        req.add_header('Content-Type', 'application/json')
        out_data = json.dumps({"name": "🤖 ADM APOLLO EDIT WEB"}).encode('utf-8')
        
        response = urllib.request.urlopen(req, data=out_data)
        data = json.loads(response.read().decode('utf-8'))
        
        if data.get("success") and data.get("group_id"):
            group_id = data.get("group_id")
            
            # Salva o group_id no config.json PRINCIPAL do servidor
            from config_manager import ConfigManager
            cm = ConfigManager(os.path.join(BASE_DIR, "config.json"))
            cm.set("whatsapp_group_id", group_id)
            
            return {"success": True, "message": "Grupo ADMIN criado e vinculado com sucesso!", "group_id": group_id}
            
        return {"success": False, "error": data.get("error", "Erro desconhecido")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/workspace")
async def get_workspace_info():
    """Retorna dados bÃ¡sicos do workspace logado."""
    return {
        "name": CURRENT_WORKSPACE,
        "path": CURRENT_WORKSPACE_PATH
    }

@app.get("/api/config/full")
async def get_config_full():
    """Retorna o config.json inteiro do workspace atual."""
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        return {"success": True, "config": cm.config}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/config/full")
async def save_config_full(request: Request):
    """Salva o config.json inteiro (sobrescreve)."""
    try:
        data = await request.json()
        if not data:
            return {"success": False, "error": "No data provided"}
        
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        cm.config = data
        cm.save_config()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# =====================================================================
# ### INÍCIO DA LÓGICA DE RENDER E GERAÇÃO DE CONTEÚDO (A FÁBRICA) ###
# =====================================================================
# AVISO DE REFATORAÇÃO FUTURA: Estas são as rotas mais pesadas. Elas 
# invocam scripts Python (FFmpeg, TTS, RVC) e não devem ser interrompidas
# por IAs. O motor é puramente determinístico aqui.
# Futuramente mover para: /src/api/render_routes.py
# =====================================================================

@app.get("/api/podcast/dados")
async def get_podcast_dados():
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        return {
            "success": True,
            "personagens": cm.get("personagens", {}),
            "config": {
                "target_lufs": cm.get("target_lufs", -10.0),
                "use_compressor": cm.get("use_compressor", True),
                "compressor_intensity": cm.get("compressor_intensity", 50.0),
                "use_smart_pacing": cm.get("use_smart_pacing", True),
                "use_ducking": cm.get("use_ducking", False)
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

class PodcastRequest(BaseModel):
    roteiro: str
    modes: list
    normalize: bool
    mapa_cores: bool
    gerar_srt: bool
    volumes: dict
    proc: dict

@app.post("/api/podcast/gerar")
async def api_podcast_gerar(req: PodcastRequest):
    check_user_status()
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        
        # Save volumes and proc
        chars = cm.get("personagens", {})
        for name, vol in req.volumes.items():
            if name in chars:
                chars[name]["volume_ajuste"] = vol
        cm.set("personagens", chars)
        
        cm.set("target_lufs", req.proc.get("lufs", -10.0))
        cm.set("use_compressor", req.proc.get("compressor", True))
        cm.set("compressor_intensity", req.proc.get("comp_int", 50.0))
        cm.set("use_smart_pacing", req.proc.get("pacing", True))
        cm.set("use_ducking", req.proc.get("ducking", False))

        # write temp script
        temp_script = os.path.join(CURRENT_WORKSPACE_PATH, "temp_podcast_script_web.txt")
        with open(temp_script, "w", encoding="utf-8") as f:
            f.write(req.roteiro)

        # run generator
        from gerador_podcast import PodcastGenerator
        # Since PodcastGenerator relies on workspace dir, ensure cwd is correct or it handles it
        old_cwd = os.getcwd()
        os.chdir(CURRENT_WORKSPACE_PATH)
        
        try:
            generator = PodcastGenerator()
            audio_path = generator.generate_podcast(
                temp_script,
                modes=req.modes,
                normalize_audio=req.normalize,
                gerar_mapa_cores=req.mapa_cores,
                log_callback=lambda x: print(f"[Podcast Web] {x}")
            )

            if req.gerar_srt and "audio" in req.modes:
                try:
                    import whisper
                    model = whisper.load_model("base")
                    result = model.transcribe(audio_path, fp16=False, language="pt", word_timestamps=True)
                    for seg in result.get("segments", []):
                        if not seg.get("words"):
                            seg["words"] = [{"word": seg["text"].strip(), "start": seg["start"], "end": seg["end"]}]
                    
                    def fmt_srt_ts(seconds):
                        ms = int((seconds % 1) * 1000)
                        s = int(seconds); h = s // 3600; s %= 3600; m = s // 60; s %= 60
                        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

                    srt_path = os.path.splitext(audio_path)[0] + ".srt"
                    with open(srt_path, "w", encoding="utf-8") as f:
                        idx = 1
                        for seg in result.get("segments", []):
                            for w in seg.get("words", []):
                                word = w["word"].strip()
                                if not word: continue
                                f.write(f"{idx}\n{fmt_srt_ts(w['start'])} --> {fmt_srt_ts(w['end'])}\n{word}\n\n")
                                idx += 1
                except Exception as e_srt:
                    print(f"[Podcast Web SRT Error] {e_srt}")

            out_dir = os.path.join(CURRENT_WORKSPACE_PATH, "output_podcast")
            return {"success": True, "path": out_dir}
            
        finally:
            os.chdir(old_cwd)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/api/ajustador/processar")
async def api_ajustador_processar(
    files: List[UploadFile] = File(...),
    bg_file: Optional[UploadFile] = File(None),
    preset: str = Form("720p"),
    blur: int = Form(20),
    bitrate: str = Form("4M"),
    fps: int = Form(30),
    min_dur: int = Form(5)
):
    check_user_status()
    import queue
    import threading
    import time
    import asyncio
    
    temp_dir = os.path.join(os.getcwd(), 'temp', f'ajustador_{int(time.time())}')
    os.makedirs(temp_dir, exist_ok=True)
    
    input_paths = []
    for idx, f in enumerate(files):
        ext = os.path.splitext(f.filename)[1] if f.filename else ".mp4"
        path = os.path.join(temp_dir, f"in_{idx}{ext}")
        with open(path, "wb") as out_f:
            out_f.write(await f.read())
        input_paths.append(path)
        
    bg_path = None
    if bg_file and bg_file.filename:
        bg_path = os.path.join(temp_dir, f"bg_{bg_file.filename}")
        with open(bg_path, "wb") as out_f:
            out_f.write(await bg_file.read())
            
    q = queue.Queue()
    
    def worker():
        try:
            out_dir = os.path.join(CURRENT_WORKSPACE_PATH, "saida_ajustador")
            os.makedirs(out_dir, exist_ok=True)
            
            q.put(f"âš™ï¸  Configurando processador de mÃ­dia...\n")
            q.put(f"ðŸ“‚ SaÃ­da automÃ¡tica configurada para: {out_dir}\n")
            
            from media_adjuster import MediaProcessor
            processor = MediaProcessor()
            processor.set_preset(preset)
            processor.blur_strength = blur
            processor.bitrate = bitrate
            processor.fps = fps
            processor.min_duration = min_dur
            if bg_path:
                processor.use_background_video = True
                processor.background_video_path = bg_path
                q.put(f"ðŸŽžï¸  VÃ­deo de fundo detectado e configurado.\n")
                
            total = len(input_paths)
            erros = 0
            
            for i, p in enumerate(input_paths, 1):
                nome_saida = f"cena_{i}.mp4"
                caminho_saida = os.path.join(out_dir, nome_saida)
                q.put(f"\nðŸ“Ž [{i}/{total}] Processando cena {i}...")
                
                def log_cb(msg):
                    q.put(msg)
                
                ok = processor.process_file(p, caminho_saida, log_callback=log_cb)
                if not ok:
                    erros += 1
                    
            if erros == 0:
                q.put(f"\n\nâœ… ConcluÃ­do com sucesso! {total} vÃ­deos salvos na pasta 'saida_ajustador' do seu projeto.")
            else:
                q.put(f"\n\nâš ï¸  Finalizado com {erros} erros. Verifique os logs acima.")
                
        except Exception as e:
            q.put(f"\nâ Œ Erro fatal: {str(e)}")
        finally:
            q.put(None)
            
    threading.Thread(target=worker, daemon=True).start()
    
    async def event_generator():
        while True:
            try:
                msg = q.get_nowait()
                if msg is None:
                    break
                yield msg + "\n"
            except queue.Empty:
                await asyncio.sleep(0.2)
                
    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_generator(), media_type="text/plain")

# ===== ROTAS DA FÃ BRICA DE MÃšSICAS =====

@app.get("/api/fabrica/templates")
async def fabrica_templates():
    perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
    if not os.path.exists(perfis_dir):
        return {"success": True, "templates": []}
    templates = [f for f in os.listdir(perfis_dir) if f.endswith('.json')]
    return {"success": True, "templates": templates}

class CarregarMusicasReq(BaseModel):
    suno_dir: str

@app.post("/api/fabrica/carregar_musicas")
async def fabrica_carregar_musicas(req: CarregarMusicasReq):
    if not os.path.exists(req.suno_dir):
        return {"success": False, "error": "DiretÃ³rio nÃ£o encontrado."}
    
    musicas = []
    _id = 0
    for p in os.listdir(req.suno_dir):
        caminho_pasta = os.path.join(req.suno_dir, p)
        if os.path.isdir(caminho_pasta):
            arquivos = os.listdir(caminho_pasta)
            audio_file = next((f for f in arquivos if f.endswith(('.wav', '.mp3'))), None)
            txt_file = next((f for f in arquivos if f.endswith('.txt')), None)
            cover_file = next((f for f in arquivos if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))), None)
            
            if audio_file:
                musicas.append({
                    "id": _id,
                    "nome": p,
                    "pasta": caminho_pasta,
                    "audio": os.path.join(caminho_pasta, audio_file),
                    "audio_basename": audio_file,
                    "txt": os.path.join(caminho_pasta, txt_file) if txt_file else None,
                    "cover": os.path.join(caminho_pasta, cover_file) if cover_file else None,
                    "status": "Pendente"
                })
                _id += 1
                
    return {"success": True, "musicas": musicas}

class GerarLoteReq(BaseModel):
    bg_dir: str
    template: str
    formato_capa: str
    musicas: list

@app.post("/api/fabrica/gerar_lote")
async def fabrica_gerar_lote(req: GerarLoteReq):
    check_user_status()
    import queue
    import threading
    import asyncio
    import random
    from fastapi.responses import StreamingResponse
    from config_manager import ConfigManager
    from music_video_engine import MusicVideoEngine
    from llm_cascade import LLMCascade
    
    q = queue.Queue()
    
    def worker():
        try:
            config_manager = ConfigManager(config_file=os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
            config_manager.workspace_dir = CURRENT_WORKSPACE_PATH
            engine = MusicVideoEngine(CURRENT_WORKSPACE_PATH)
            llm = LLMCascade(config_manager)
            
            out_dir = os.path.join(CURRENT_WORKSPACE_PATH, "outputs", "fabrica_clipes")
            os.makedirs(out_dir, exist_ok=True)
            
            perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
            all_temps = [f for f in os.listdir(perfis_dir) if f.endswith('.json')]
            
            for m_data in req.musicas:
                item_id = m_data.get('id')
                q.put(json.dumps({"type": "status", "id": item_id, "status": "Processando..."}))
                
                try:
                    nome_limpo = "".join(c for c in m_data['nome'] if c.isalnum() or c in " _-").strip()
                    out_path = os.path.join(m_data['pasta'], f"{nome_limpo}.mp4")
                    song_name = m_data['nome']
                    
                    channel_context = config_manager.get("music_factory.channel_context", "")
                    metadata_example = config_manager.get("music_factory.metadata_example", "")
                    
                    # 1. IA Metadata
                    if m_data.get('txt'):
                        meta_path = os.path.join(m_data['pasta'], "metadata.json")
                        if not os.path.exists(meta_path):
                            q.put(json.dumps({"type": "status", "id": item_id, "status": "Gerando IA..."}))
                            with open(m_data['txt'], 'r', encoding='utf-8') as f:
                                prompt_text = f.read()
                            res = llm.gemini.generate_music_metadata(prompt_text, song_name, channel_context, metadata_example)
                            if res:
                                res = res.replace("```json", "").replace("```", "").strip()
                                try:
                                    json_data = json.loads(res)
                                    with open(meta_path, 'w', encoding='utf-8') as mf:
                                        json.dump(json_data, mf, ensure_ascii=False, indent=4)
                                    if "title" in json_data: song_name = json_data["title"]
                                    
                                    aspect_ratio = None
                                    if req.formato_capa == "Quadrada (1:1)": aspect_ratio = "1:1"
                                    elif req.formato_capa == "Vertical (9:16)": aspect_ratio = "9:16"
                                    elif req.formato_capa == "Horizontal (16:9)": aspect_ratio = "16:9"
                                    
                                    if "image_prompt" in json_data:
                                        prompt_capa_path = os.path.join(m_data['pasta'], "prompt_capa.txt")
                                        with open(prompt_capa_path, 'w', encoding='utf-8') as pcf:
                                            pcf.write(json_data["image_prompt"])
                                            
                                        if aspect_ratio:
                                            cover_ia_path = os.path.join(m_data['pasta'], "cover_ia.jpg")
                                            if not os.path.exists(cover_ia_path):
                                                q.put(json.dumps({"type": "status", "id": item_id, "status": f"Gerando Capa {aspect_ratio}..."}))
                                                gemini.generate_image(json_data["image_prompt"], output_path=cover_ia_path, aspect_ratio=aspect_ratio)
                                            if os.path.exists(cover_ia_path):
                                                m_data['cover'] = cover_ia_path
                                                
                                    if "lyrics" in json_data:
                                        with open(os.path.join(m_data['pasta'], "lyrics_ia.txt"), 'w', encoding='utf-8') as lf:
                                            lf.write(json_data["lyrics"])
                                    if "broll_prompts" in json_data:
                                        with open(os.path.join(m_data['pasta'], "broll_prompts.json"), 'w', encoding='utf-8') as bf:
                                            json.dump(json_data["broll_prompts"], bf, ensure_ascii=False, indent=4)
                                except Exception as e:
                                    q.put(json.dumps({"type": "log", "text": f"Falha no JSON IA para {song_name}: {e}"}))
                        else:
                            try:
                                with open(meta_path, 'r', encoding='utf-8') as mf:
                                    meta = json.load(mf)
                                    if "title" in meta: song_name = meta["title"]
                                    aspect_ratio = None
                                    if req.formato_capa == "Quadrada (1:1)": aspect_ratio = "1:1"
                                    elif req.formato_capa == "Vertical (9:16)": aspect_ratio = "9:16"
                                    elif req.formato_capa == "Horizontal (16:9)": aspect_ratio = "16:9"
                                    if "image_prompt" in meta and aspect_ratio:
                                        cover_ia_path = os.path.join(m_data['pasta'], "cover_ia.jpg")
                                        if not os.path.exists(cover_ia_path):
                                            q.put(json.dumps({"type": "status", "id": item_id, "status": f"Gerando Capa {aspect_ratio}..."}))
                                            gemini.generate_image(meta["image_prompt"], output_path=cover_ia_path, aspect_ratio=aspect_ratio)
                                        if os.path.exists(cover_ia_path): m_data['cover'] = cover_ia_path
                            except: pass
                            
                    # 2. Render
                    q.put(json.dumps({"type": "status", "id": item_id, "status": "Renderizando..."}))
                    chosen_template = req.template
                    if chosen_template == "AleatÃ³rio (Auto)":
                        if all_temps: chosen_template = random.choice(all_temps)
                        else: raise Exception("Nenhum template encontrado.")
                        
                    final_template_path = os.path.join(perfis_dir, chosen_template)
                    
                    engine.generate_music_video(
                        audio_path=m_data['audio'],
                        bg_dir=req.bg_dir,
                        song_name=song_name,
                        output_path=out_path,
                        template_path=final_template_path,
                        cover_path=m_data.get('cover'),
                        callback=lambda msg: q.put(json.dumps({"type": "log", "text": msg}))
                    )
                    
                    q.put(json.dumps({"type": "status", "id": item_id, "status": "ConcluÃ­do"}))
                    q.put(json.dumps({"type": "log", "text": f"â Sucesso: {song_name}"}))
                except Exception as e:
                    q.put(json.dumps({"type": "status", "id": item_id, "status": "Erro"}))
                    q.put(json.dumps({"type": "log", "text": f"â Erro em {m_data['nome']}: {e}"}))
                    
        except Exception as ex:
            q.put(json.dumps({"type": "log", "text": f"â Erro fatal: {ex}"}))
        finally:
            q.put(None)
            
    threading.Thread(target=worker, daemon=True).start()
    
    async def event_generator():
        while True:
            try:
                msg = q.get_nowait()
                if msg is None: break
                yield f"data: {msg}\n\n"
            except queue.Empty:
                await asyncio.sleep(0.2)
                
    return StreamingResponse(event_generator(), media_type="text/event-stream")

class CompilarReq(BaseModel):
    root_dir: str
    duracao_min: int

@app.post("/api/fabrica/compilar")
async def fabrica_compilar(req: CompilarReq):
    import queue
    import threading
    import asyncio
    import random
    from fastapi.responses import StreamingResponse
    from music_video_engine import MusicVideoEngine
    
    q = queue.Queue()
    
    def worker():
        try:
            if not os.path.exists(req.root_dir):
                q.put("â DiretÃ³rio nÃ£o existe.\n")
                return
                
            engine = MusicVideoEngine(CURRENT_WORKSPACE_PATH)
            
            videos = []
            for root, dirs, files in os.walk(req.root_dir):
                for file in files:
                    if file.endswith('.mp4') and not file.startswith('Compilado_'):
                        videos.append(os.path.join(root, file))
                        
            if not videos:
                q.put("â Nenhum .mp4 encontrado nas subpastas.\n")
                return
                
            total_desejado_sec = req.duracao_min * 60
            total_acumulado = 0
            lista_final = []
            
            q.put("Montando grade de compilaÃ§Ã£o...\n")
            while total_acumulado < total_desejado_sec:
                vid = random.choice(videos)
                lista_final.append(vid)
                dur = engine.get_audio_duration(vid)
                if dur <= 0: dur = 180 
                total_acumulado += dur
                
            out_path = os.path.join(req.root_dir, f"Compilado_{req.duracao_min}Min.mp4")
            
            engine.concat_videos(lista_final, out_path, callback=lambda msg: q.put(msg + "\n"))
            q.put(f"\nâ CompilaÃ§Ã£o de {req.duracao_min} minutos concluÃ­da!\nSalvo em: {out_path}\n")
        except Exception as e:
            q.put(f"\nâ Erro na compilaÃ§Ã£o: {e}\n")
        finally:
            q.put(None)
            
    threading.Thread(target=worker, daemon=True).start()
    
    async def event_generator():
        while True:
            try:
                msg = q.get_nowait()
                if msg is None: break
                yield msg
            except queue.Empty:
                await asyncio.sleep(0.2)
                
    return StreamingResponse(event_generator(), media_type="text/plain")

# ====== ENDPOINTS DA TIMELINE & EDITOR ======

@app.get("/api/browse_file")
async def browse_file_api(type: str = "file"):
    """Abre um File Dialog nativo no Python para o usuÃ¡rio escolher arquivo"""
    import tkinter as tk
    from tkinter import filedialog
    
    # Criar janela root oculta
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    path = ""
    if type == "folder":
        path = filedialog.askdirectory(title="Selecione uma pasta")
    else:
        path = filedialog.askopenfilename(title="Selecione um arquivo")
        
    root.destroy()
    
    if path:
        return {"status": "success", "path": os.path.normpath(path)}
    return {"status": "cancelled", "path": ""}

@app.get("/api/thumb")
async def get_thumb(path: str):
    """Retorna o arquivo diretamente se for imagem, ou extrai um frame se for vÃ­deo"""
    if not os.path.exists(path):
        return HTMLResponse(content="Not Found", status_code=404)
        
    ext = path.split('.')[-1].lower()
    if ext in ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp']:
        return FileResponse(path)
    else:
        # Se for vÃ­deo, idealmente usar FFmpeg para extrair frame.
        # Aqui enviamos o prÃ³prio vÃ­deo se o navegador suportar, ou um Ã­cone padrÃ£o.
        # Para simplificar na prova de conceito, enviaremos um placeholder se for vÃ­deo.
        return HTMLResponse(content="Video thumbnail not implemented", status_code=501)

@app.get("/api/list_profiles")
async def list_profiles():
    try:
        perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
        if not os.path.exists(perfis_dir):
            return {"status": "success", "profiles": []}
        perfis = sorted([f.replace('.json', '') for f in os.listdir(perfis_dir) if f.endswith('.json')])
        return {"status": "success", "profiles": perfis}
    except Exception as e:
        return {"status": "error", "profiles": [], "message": str(e)}

@app.get("/api/delete_profile")
async def delete_profile(name: str):
    try:
        perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
        path = os.path.join(perfis_dir, f"{name}.json")
        # TambÃ©m deleta a imagem de preview se existir
        preview_path = os.path.join(perfis_dir, f"{name}.png")
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(preview_path):
            os.remove(preview_path)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/rename_profile")
async def rename_profile(request: Request):
    try:
        data = await request.json()
        old_name = data.get('old_name', '').strip()
        new_name = data.get('new_name', '').strip()
        if not old_name or not new_name:
            return {"status": "error", "message": "Nomes inv\u00e1lidos"}
        perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
        old_path = os.path.join(perfis_dir, f"{old_name}.json")
        new_path = os.path.join(perfis_dir, f"{new_name}.json")
        if not os.path.exists(old_path):
            return {"status": "error", "message": "Template n\u00e3o encontrado"}
        if os.path.exists(new_path):
            return {"status": "error", "message": "J\u00e1 existe um template com esse nome"}
        os.rename(old_path, new_path)
        # Renomeia preview se existir
        old_preview = os.path.join(perfis_dir, f"{old_name}.png")
        new_preview = os.path.join(perfis_dir, f"{new_name}.png")
        if os.path.exists(old_preview):
            os.rename(old_preview, new_preview)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/preview_image")
async def preview_image(name: str):
    try:
        perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
        preview_path = os.path.join(perfis_dir, f"{name}.png")
        if os.path.exists(preview_path):
            from fastapi.responses import FileResponse
            return FileResponse(preview_path, media_type="image/png")
        from fastapi.responses import Response
        return Response(status_code=404)
    except Exception as e:
        from fastapi.responses import Response
        return Response(status_code=500)

# ===== ROTAS PARA O TTS (GERADOR DE ÃUDIO) =====
@app.get("/api/tts/personagens")
def get_personagens():
    """Retorna os personagens cadastrados do workspace"""
    try:
        from config_manager import ConfigManager
        config = ConfigManager(config_file=os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        config.workspace_dir = CURRENT_WORKSPACE_PATH
        p = config.get("personagens", {})
        return {"success": True, "personagens": list(p.keys()), "detalhes": p}
    except Exception as e:
        return {"success": False, "error": str(e)}

class TTSRequest(BaseModel):
    personagem: str
    texto: str
    engine: str = "proplus"
    idioma: str = "pt-BR"
    efeito: str = "news"
    volume: int = 0
    velocidade: int = 0
    pitch: int = 0
    sample_rate: str = "48000"
    emocao_adicional: str = ""

@app.post("/api/tts/gerar")
def tts_gerar(req: TTSRequest):
    """Gera Ã¡udio usando a API VoiceMaker ou a configurada"""
    try:
        from config_manager import ConfigManager
        from tts_manager import TTSManager
        
        config = ConfigManager(config_file=os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        config.workspace_dir = CURRENT_WORKSPACE_PATH
        api = TTSManager(config)
        
        # Gera o arquivo mp3 na pasta outputs
        outputs_dir = os.path.join(CURRENT_WORKSPACE_PATH, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        nome_safe = req.personagem.lower().replace(' ', '_')
        output_path = os.path.join(outputs_dir, f"tts_{nome_safe}.mp3")
        
        # Garante nÃ£o sobrescrever
        contador = 1
        while os.path.exists(output_path):
            output_path = os.path.join(outputs_dir, f"tts_{nome_safe}_{contador}.mp3")
            contador += 1
            
        params = {
            "Engine": req.engine,
            "LanguageCode": req.idioma,
            "Effect": req.efeito,
            "MasterVolume": str(req.volume),
            "MasterSpeed": str(req.velocidade),
            "MasterPitch": str(req.pitch),
            "SampleRate": req.sample_rate,
            "emocao_adicional": req.emocao_adicional
        }
        
        success = api.generate_audio(req.personagem, req.texto, output_path, **params)
        
        if success:
            try:
                from database_manager import db
                canal_id = db.get_canal_id(CURRENT_WORKSPACE)
                db.set_memoria("ultimo_audio_tts", output_path, canal_id=canal_id)
            except: pass
            return {"success": True, "file": output_path, "filename": os.path.basename(output_path)}
        else:
            return {"success": False, "error": "Falha na geraÃ§Ã£o via API TTSManager"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/tts/testar_google")
def tts_testar_google(req: TTSRequest):
    """Testa explicitamente a API Gemini/Google TTS"""
    try:
        from config_manager import ConfigManager
        from gemini_tts_api import GeminiTTSProvider
        
        config = ConfigManager(config_file=os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        config.workspace_dir = CURRENT_WORKSPACE_PATH
        
        char_config = config.get_personagem(req.personagem)
        voice_id = char_config.get('voz_google_tts', '')
        if not voice_id:
            return {"success": False, "error": "Personagem nÃ£o possui 'Voz Google TTS' configurada."}
            
        instruction = char_config.get('instrucao_base_tts', '')
        
        outputs_dir = os.path.join(CURRENT_WORKSPACE_PATH, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        nome_safe = req.personagem.lower().replace(' ', '_')
        output_path = os.path.join(outputs_dir, f"teste_google_{nome_safe}.mp3")
        
        # Garante nÃ£o sobrescrever
        contador = 1
        while os.path.exists(output_path):
            output_path = os.path.join(outputs_dir, f"teste_google_{nome_safe}_{contador}.mp3")
            contador += 1
            
        gemini_provider = GeminiTTSProvider(config)
        success = gemini_provider.generate_tts(
            text=req.texto,
            voice_id=voice_id,
            output_path=output_path,
            instruction_prompt=instruction
        )
        
        if success:
            try:
                from database_manager import db
                canal_id = db.get_canal_id(CURRENT_WORKSPACE)
                db.set_memoria("ultimo_audio_tts", output_path, canal_id=canal_id)
            except: pass
            return {"success": True, "file": output_path, "filename": os.path.basename(output_path)}
        else:
            return {"success": False, "error": "Falha ao requisitar Ã¡udio do Gemini TTS"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ROTAS PARA O NARRADOR (GERADOR DE VÃDEO) =====
@app.post("/api/narrador/gerar")
async def narrador_gerar(
    personagem: str = Form(...),
    estado_emocional: str = Form(...),
    audio_file: UploadFile = File(...)
):
    try:
        from config_manager import ConfigManager
        import subprocess
        import random
        
        config = ConfigManager(config_file=os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        config.workspace_dir = CURRENT_WORKSPACE_PATH
        
        personagens_cache = config.get("personagens", {})
        if personagem not in personagens_cache:
            return {"success": False, "error": f"Personagem nÃ£o encontrado: {personagem}"}
            
        personagem_config = personagens_cache[personagem]
        
        if "estados_emocionais" not in personagem_config:
            return {"success": False, "error": f"Estados emocionais nÃ£o configurados para: {personagem}"}
            
        if estado_emocional not in personagem_config["estados_emocionais"]:
            return {"success": False, "error": f"Estado emocional nÃ£o encontrado: {estado_emocional}"}
            
        video_source = personagem_config["estados_emocionais"][estado_emocional].get("video_source", "")
        
        if not video_source or not os.path.exists(video_source):
            return {"success": False, "error": f"VÃ­deo base nÃ£o encontrado para {personagem} - {estado_emocional}\nCaminho: {video_source}"}
            
        # Salva o Ã¡udio temporariamente
        temp_audio_path = os.path.join(CURRENT_WORKSPACE_PATH, "temp_upload.mp3")
        with open(temp_audio_path, "wb") as f:
            f.write(await audio_file.read())
            
        def get_duration(filepath):
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filepath]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0: return None
            return float(res.stdout)
            
        duracao_audio = get_duration(temp_audio_path)
        duracao_video_total = get_duration(video_source)
        
        if duracao_audio is None or duracao_video_total is None:
            return {"success": False, "error": "FFprobe falhou ao ler mÃ­dia"}
            
        if duracao_audio > duracao_video_total:
            return {"success": False, "error": f"Ãudio ({duracao_audio:.1f}s) Ã© maior que o vÃ­deo ({duracao_video_total:.1f}s)"}
            
        max_start_time = duracao_video_total - duracao_audio
        start_time = random.uniform(0, max_start_time)
        
        outputs_dir = os.path.join(CURRENT_WORKSPACE_PATH, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        nome_safe = personagem.lower().replace(' ', '_')
        output_path = os.path.join(outputs_dir, f"narrador_{nome_safe}.mp4")
        
        contador = 1
        while os.path.exists(output_path):
            output_path = os.path.join(outputs_dir, f"narrador_{nome_safe}_{contador}.mp4")
            contador += 1
            
        comando_ffmpeg = [
            'ffmpeg',
            '-i', video_source,
            '-i', temp_audio_path,
            '-filter_complex', f'[0:v]trim=start={start_time}:duration={duracao_audio},setpts=PTS-STARTPTS[v]',
            '-map', '[v]',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-preset', 'superfast',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-shortest',
            output_path,
            '-y'
        ]
        
        res = subprocess.run(comando_ffmpeg, capture_output=True, text=True)
        
        # Limpa arquivo temporÃ¡rio
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            
        if res.returncode != 0:
            return {"success": False, "error": f"Erro no FFmpeg: {res.stderr}"}
            
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            duracao_gerada = get_duration(output_path)
            
            try:
                from database_manager import db
                canal_id = db.get_canal_id(CURRENT_WORKSPACE)
                db.set_memoria("ultimo_video_narrador", output_path, canal_id=canal_id)
            except: pass
            
            return {
                "success": True, 
                "file": output_path, 
                "filename": os.path.basename(output_path),
                "duracao": duracao_gerada
            }
        else:
            return {"success": False, "error": "VÃ­deo gerado estÃ¡ vazio."}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ROTAS PARA O CONTROLE DE VOLUME =====
from typing import List, Optional

@app.post("/api/volume/processar")
async def volume_processar(
    tipo_ajuste: str = Form(...),
    valor_volume: float = Form(...),
    videos: List[UploadFile] = File(...),
    musica1: Optional[UploadFile] = File(None),
    vol_musica1: float = Form(0.0),
    musica2: Optional[UploadFile] = File(None),
    vol_musica2: float = Form(0.0),
    musica3: Optional[UploadFile] = File(None),
    vol_musica3: float = Form(0.0)
):
    check_user_status()
    try:
        import subprocess
        import hardware_detector
        
        outputs_dir = os.path.join(CURRENT_WORKSPACE_PATH, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Salva os arquivos de mÃºsica se enviados
        musicas_selecionadas = []
        if musica1 and musica1.filename:
            path1 = os.path.join(outputs_dir, "temp_musica1.mp3")
            with open(path1, "wb") as f: f.write(await musica1.read())
            musicas_selecionadas.append((path1, vol_musica1))
            
        if musica2 and musica2.filename:
            path2 = os.path.join(outputs_dir, "temp_musica2.mp3")
            with open(path2, "wb") as f: f.write(await musica2.read())
            musicas_selecionadas.append((path2, vol_musica2))
            
        if musica3 and musica3.filename:
            path3 = os.path.join(outputs_dir, "temp_musica3.mp3")
            with open(path3, "wb") as f: f.write(await musica3.read())
            musicas_selecionadas.append((path3, vol_musica3))

        resultados = []
        erros = []
        
        encoder = "libx264"
        try:
            encoder = hardware_detector.detect_h264_encoder()
        except: pass
        video_codec = ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast'] if encoder == 'libx264' else ['-c:v', encoder, '-b:v', '6M', '-pix_fmt', 'yuv420p']

        for idx, video_file in enumerate(videos):
            if not video_file.filename: continue
            
            temp_vid_path = os.path.join(outputs_dir, f"temp_vid_{idx}_{video_file.filename}")
            with open(temp_vid_path, "wb") as f: f.write(await video_file.read())
            
            nome_base = os.path.splitext(video_file.filename)[0]
            extensao = os.path.splitext(video_file.filename)[1]
            if not extensao: extensao = ".mp4"
            
            # Sufixo
            sufixo = ""
            val = valor_volume
            if tipo_ajuste == 'aumentar':
                sufixo = f"_volume_+{val:.1f}dB"
            elif tipo_ajuste == 'reduzir':
                val = -val
                sufixo = f"_volume_{val:.1f}dB"
            else:
                sufixo = f"_volume_{val:.1f}dB"
                
            if musicas_selecionadas:
                sufixo += "_com_musica"
                
            output_path = os.path.join(outputs_dir, f"{nome_base}{sufixo}{extensao}")
            
            # ResoluÃ§Ã£o alvo
            import json
            alvo_w, alvo_h = 1080, 1920
            try:
                probe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', temp_vid_path]
                probe_res = subprocess.run(probe_cmd, capture_output=True, text=True)
                if probe_res.returncode == 0:
                    v_info = json.loads(probe_res.stdout)
                    vw = int(v_info['streams'][0]['width'])
                    vh = int(v_info['streams'][0]['height'])
                    if vw > vh: alvo_w, alvo_h = 1920, 1080
                    elif vw == vh: alvo_w, alvo_h = 1080, 1080
            except: pass
            
            vf_scale = f'scale={alvo_w}:{alvo_h}:force_original_aspect_ratio=decrease,pad={alvo_w}:{alvo_h}:(ow-iw)/2:(oh-ih)/2:black'
            
            comando = ['ffmpeg', '-y', '-threads', '0']
            comando.extend(['-hwaccel', 'auto', '-i', temp_vid_path])
            
            if not musicas_selecionadas:
                comando.extend(['-filter:a', f'volume={val:.1f}dB', '-vf', vf_scale])
                comando.extend(video_codec)
                comando.append(output_path)
            else:
                for m_path, _ in musicas_selecionadas:
                    comando.extend(['-i', m_path])
                    
                filtro_audio = [f"[0:a]volume={val:.1f}dB[a_video]"]
                for i, (_, m_vol) in enumerate(musicas_selecionadas):
                    filtro_audio.append(f"[{i+1}:a]volume={m_vol}dB[a_musica{i+1}]")
                    
                inputs_audio = "[a_video]" + "".join([f"[a_musica{i+1}]" for i in range(len(musicas_selecionadas))])
                filtro_audio.append(f"{inputs_audio}amix=inputs={len(musicas_selecionadas)+1}:duration=first:dropout_transition=0:normalize=0[a_final]")
                
                comando.extend(['-filter_complex', ';'.join(filtro_audio), '-map', '0:v', '-map', '[a_final]', '-vf', vf_scale])
                comando.extend(video_codec)
                comando.extend(['-c:a', 'aac', '-b:a', '192k', output_path])
                
            res = subprocess.run(comando, capture_output=True, text=True)
            
            if os.path.exists(temp_vid_path): os.remove(temp_vid_path)
            
            if res.returncode == 0 and os.path.exists(output_path):
                resultados.append(os.path.basename(output_path))
            else:
                erros.append(f"Erro no vÃ­deo {video_file.filename}: {res.stderr}")
                
        # Limpar mÃºsicas temporÃ¡rias
        for m_path, _ in musicas_selecionadas:
            if os.path.exists(m_path): os.remove(m_path)
            
        if not erros:
            return {"success": True, "processados": resultados}
        elif resultados:
            return {"success": True, "warning": "Alguns erros ocorreram", "processados": resultados, "erros": erros}
        else:
            return {"success": False, "error": "\n".join(erros)}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ROTAS PARA FERRAMENTAS RAPIDAS =====
@app.post("/api/ferramentas/processar")
async def ferramentas_processar(
    acao: str = Form(...),
    video: UploadFile = File(...),
    capa: Optional[UploadFile] = File(None),
    largura: Optional[int] = Form(None),
    altura: Optional[int] = Form(None),
    velocidade: Optional[float] = Form(None),
    brilho: Optional[float] = Form(None),
    contraste: Optional[float] = Form(None),
    rotacao: Optional[int] = Form(None)
):
    check_user_status()
    try:
        import subprocess
        import json
        outputs_dir = os.path.join(CURRENT_WORKSPACE_PATH, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        
        # Salva o video de entrada temporariamente
        temp_vid_path = os.path.join(outputs_dir, f"temp_{video.filename}")
        with open(temp_vid_path, "wb") as f: f.write(await video.read())
        
        nome_base = os.path.splitext(video.filename)[0]
        extensao = os.path.splitext(video.filename)[1] or ".mp4"
        
        output_path = ""
        comando = []
        is_zip = False
        
        if acao == "adicionar_capa":
            if not capa: raise Exception("Capa nÃ£o enviada")
            temp_capa_path = os.path.join(outputs_dir, f"temp_{capa.filename}")
            with open(temp_capa_path, "wb") as f: f.write(await capa.read())
            
            output_path = os.path.join(outputs_dir, f"{nome_base}_com_capa.mp4")
            
            # Pega dimensÃµes do vÃ­deo
            probe_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', temp_vid_path]
            res = subprocess.run(probe_cmd, capture_output=True, text=True)
            data = json.loads(res.stdout)
            vw, vh = 1920, 1080
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    vw, vh = int(stream['width']), int(stream['height'])
                    break
            
            capa_video = os.path.join(outputs_dir, "capa_temp.mp4")
            cmd_capa = ['ffmpeg', '-y', '-loop', '1', '-i', temp_capa_path,
                        '-vf', f'scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:black',
                        '-c:v', 'libx264', '-frames:v', '1', '-pix_fmt', 'yuv420p', '-r', '30', '-an', capa_video]
            subprocess.run(cmd_capa, capture_output=True)
            
            comando = ['ffmpeg', '-y', '-i', capa_video, '-i', temp_vid_path,
                       '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v];[1:a]acopy[a]',
                       '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-c:a', 'aac', '-preset', 'fast', '-crf', '23',
                       '-avoid_negative_ts', 'make_zero', '-fflags', '+genpts', output_path]
                       
            res_concat = subprocess.run(comando, capture_output=True, text=True)
            if os.path.exists(temp_capa_path): os.remove(temp_capa_path)
            if os.path.exists(capa_video): os.remove(capa_video)
            if res_concat.returncode != 0: raise Exception(f"Erro FFmpeg: {res_concat.stderr}")

        elif acao == "inverter_video":
            output_path = os.path.join(outputs_dir, f"{nome_base}_invertido.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vf', 'reverse', '-af', 'areverse', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "remover_ultimo_frame":
            output_path = os.path.join(outputs_dir, f"{nome_base}_sem_final.mp4")
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', temp_vid_path]
            res = subprocess.run(probe_cmd, capture_output=True, text=True)
            duration = float(res.stdout.strip())
            new_dur = duration - 0.1
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-t', str(new_dur), '-c', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "extrair_audio":
            output_path = os.path.join(outputs_dir, f"{nome_base}_audio.mp3")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-q:a', '0', '-map', 'a', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "redimensionar":
            if not largura or not altura: raise Exception("Largura e Altura sÃ£o obrigatÃ³rios")
            output_path = os.path.join(outputs_dir, f"{nome_base}_{largura}x{altura}.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vf', f'scale={largura}:{altura}', '-c:a', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "acelerar_desacelerar":
            if not velocidade: raise Exception("Velocidade obrigatÃ³ria")
            output_path = os.path.join(outputs_dir, f"{nome_base}_{velocidade}x.mp4")
            v_speed = 1.0 / velocidade
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-filter_complex', f'[0:v]setpts={v_speed}*PTS[v];[0:a]atempo={velocidade}[a]', '-map', '[v]', '-map', '[a]', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "ajustar_brilho_contraste":
            if brilho is None or contraste is None: raise Exception("Brilho e contraste obrigatÃ³rios")
            output_path = os.path.join(outputs_dir, f"{nome_base}_brilho.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vf', f'eq=brightness={brilho}:contrast={contraste}', '-c:a', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "remover_audio":
            output_path = os.path.join(outputs_dir, f"{nome_base}_mudo.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-c:v', 'copy', '-an', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "rotacionar":
            if not rotacao: raise Exception("RotaÃ§Ã£o obrigatÃ³ria")
            output_path = os.path.join(outputs_dir, f"{nome_base}_rot{rotacao}.mp4")
            vf = "transpose=1"
            if rotacao == 2: vf = "transpose=2"
            if rotacao == 3: vf = "transpose=2,transpose=2"
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vf', vf, '-c:a', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "criador_stories":
            output_path = os.path.join(outputs_dir, f"{nome_base}_30s.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-t', '30', '-c', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "compressor_video":
            output_path = os.path.join(outputs_dir, f"{nome_base}_comprimido.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vcodec', 'libx264', '-crf', '28', '-preset', 'fast', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "espelhar_video":
            output_path = os.path.join(outputs_dir, f"{nome_base}_espelhado.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vf', 'hflip', '-c:a', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "remover_silencios":
            output_path = os.path.join(outputs_dir, f"{nome_base}_semsilencio.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-af', 'silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=-1:stop_threshold=-50dB:stop_duration=0.5', '-c:v', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "converter_mp4":
            output_path = os.path.join(outputs_dir, f"{nome_base}_convertido.mp4")
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-c:v', 'libx264', '-preset', 'fast', '-c:a', 'aac', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        elif acao == "extrair_frames":
            out_dir = os.path.join(outputs_dir, f"{nome_base}_frames")
            os.makedirs(out_dir, exist_ok=True)
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vf', 'fps=1', os.path.join(out_dir, "frame_%04d.jpg")]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")
            import shutil
            shutil.make_archive(out_dir, 'zip', out_dir)
            output_path = f"{out_dir}.zip"
            is_zip = True

        elif acao == "padronizar_celular":
            output_path = os.path.join(outputs_dir, f"{nome_base}_9x16.mp4")
            vf = "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
            comando = ['ffmpeg', '-y', '-i', temp_vid_path, '-vf', vf, '-c:a', 'copy', output_path]
            res = subprocess.run(comando, capture_output=True, text=True)
            if res.returncode != 0: raise Exception(f"Erro FFmpeg: {res.stderr}")

        else:
            raise Exception("AÃ§Ã£o desconhecida")

        if os.path.exists(temp_vid_path): os.remove(temp_vid_path)

        if os.path.exists(output_path):
            return {"success": True, "file": os.path.basename(output_path), "is_zip": is_zip}
        else:
            raise Exception("Arquivo de saÃ­da nÃ£o gerado.")

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    try:
        from database_manager import db
        import shutil
        import datetime
        import collections

        # Identificar o canal ativo
        canal_id = None
        try:
            config_path = os.path.join(CURRENT_WORKSPACE_PATH, "config.json")
            if os.path.exists(config_path):
                canal_id = db.get_canal_id(os.path.basename(CURRENT_WORKSPACE_PATH))
        except:
            pass

        # 1. SaÃºde do Sistema
        disk_free_gb = 0
        try:
            total, used, free = shutil.disk_usage(CURRENT_WORKSPACE_PATH)
            disk_free_gb = free / (1024**3)
        except:
            pass

        canais_count = 0
        try:
            with db.get_connection() as conn:
                res = conn.execute("SELECT COUNT(*) as c FROM canais").fetchone()
                if res: canais_count = res['c']
        except:
            pass

        fila_pendentes = 0
        try:
            with db.get_connection() as conn:
                res = conn.execute("SELECT COUNT(*) as c FROM historico_videos WHERE status IN ('pendente', 'renderizando')").fetchone()
                if res: fila_pendentes = res['c']
        except:
            pass

        # 2. HistÃ³rico Local (Canal Atual)
        hist_local = db.buscar_videos_dashboard(canal_id=canal_id, limit=300)
        # Parse dates and count week
        agora = datetime.datetime.now()
        semana_passada = agora - datetime.timedelta(days=7)
        local_total = len(hist_local)
        local_sucesso = sum(1 for v in hist_local if v.get("status") == "sucesso")
        local_semana = 0
        ritmo_diario = [0]*7
        dias_labels = []

        for delta in range(6, -1, -1):
            d = (agora - datetime.timedelta(days=delta)).date()
            dias_labels.append(d.strftime("%d/%m"))

        for v in hist_local:
            try:
                d_inicio = datetime.datetime.strptime(v.get("data_inicio", ""), "%Y-%m-%d %H:%M:%S")
                if d_inicio >= semana_passada:
                    local_semana += 1
                if v.get("status") == "sucesso":
                    d_str = d_inicio.date().strftime("%d/%m")
                    if d_str in dias_labels:
                        idx = dias_labels.index(d_str)
                        ritmo_diario[idx] += 1
            except:
                pass

        # 3. VisÃ£o Global
        hist_global = db.buscar_videos_dashboard(canal_id=None, limit=1000)
        global_total = len(hist_global)
        global_sucesso = sum(1 for v in hist_global if v.get("status") == "sucesso")

        ranking_canais = collections.defaultdict(lambda: {"total":0, "sucesso":0, "erros":0})
        for v in hist_global:
            c_nome = v.get("canal_nome") or "Desconhecido"
            ranking_canais[c_nome]["total"] += 1
            if v.get("status") == "sucesso":
                ranking_canais[c_nome]["sucesso"] += 1
            else:
                ranking_canais[c_nome]["erros"] += 1

        ranking_lista = [{"canal": k, **v} for k, v in ranking_canais.items()]
        ranking_lista.sort(key=lambda x: x["total"], reverse=True)

        # 4. Custos e IA
        custos_lista = []
        custo_total = 0.0
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.api_nome, c.nome as canal_nome, SUM(t.tokens_usados) as tk, SUM(t.custo_estimado) as ct 
                    FROM historico_tokens t 
                    LEFT JOIN canais c ON t.canal_id = c.id
                    GROUP BY t.api_nome, t.canal_id
                ''')
                for row in cursor.fetchall():
                    api = row['api_nome']
                    canal = row['canal_nome'] or "Desconhecido"
                    tk = row['tk'] or 0
                    ct = row['ct'] or 0.0
                    custo_total += ct
                    custos_lista.append({"api": api, "canal": canal, "tokens": tk, "custo": ct})
        except:
            pass

        return {
            "success": True,
            "health": {
                "ffmpeg": "â Pronto",
                "disk": f"{disk_free_gb:.1f} GB",
                "queue": f"{fila_pendentes} Pendentes",
                "profiles": f"{canais_count} Prontos"
            },
            "local": {
                "total": local_total,
                "sucesso": local_sucesso,
                "semana": local_semana,
                "taxa": round((local_sucesso/local_total*100) if local_total > 0 else 0),
                "ritmo_labels": dias_labels,
                "ritmo_dados": ritmo_diario,
                "historico": hist_local[:20]
            },
            "global": {
                "total": global_total,
                "sucesso": global_sucesso,
                "taxa": round((global_sucesso/global_total*100) if global_total > 0 else 0),
                "ranking": ranking_lista
            },
            "custos": {
                "total": custo_total,
                "detalhes": custos_lista
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/api/save_profile")
async def save_profile(request: Request):
    try:
        data = await request.json()
        nome = data.get('name', 'novo_perfil')
        profile_data = data.get('data', {})
        
        perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
        os.makedirs(perfis_dir, exist_ok=True)
        
        with open(os.path.join(perfis_dir, f"{nome}.json"), "w", encoding='utf-8') as f:
            json.dump(profile_data, f, indent=4)
        return {"status": "success", "message": f"Perfil {nome} salvo!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/load_profile")
async def load_profile(nome: str):
    perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
    path = os.path.join(perfis_dir, f"{nome}.json")
    if os.path.exists(path):
        with open(path, "r", encoding='utf-8') as f:
            return json.load(f)
    return JSONResponse(status_code=404, content={"message": "Perfil nÃ£o encontrado"})

# ====== ENDPOINTS DA ABA TTS ======

@app.post("/api/tts/gerar")
async def gerar_tts(req: TTSRequest):
    # Aqui entraria a chamada ao seu motor real de TTS (Voicemaker, ElevenLabs, etc)
    # Por enquanto, retornamos um dummy de sucesso
    print(f"[TTS] Gerando Ã¡udio para: {req.voz} usando engine {req.engine}")
    return {"status": "success", "message": "Ãudio gerado com sucesso! (SimulaÃ§Ã£o)", "path": ""}

@app.get("/api/config/perfis_legenda")
async def get_perfis_legenda():
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get("perfis_legenda", {})
        return {"success": True, "perfis": list(perfis.keys())}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/legendas/gerar")
async def api_legendas_gerar(
    video: UploadFile = File(...),
    srt: Optional[UploadFile] = File(None),
    engine: str = Form("vosk"),
    formato: str = Form("vertical"),
    preset: str = Form("[Personalizado]"),
    font: str = Form("Bangers"),
    words: int = Form(5),
    size: int = Form(100),
    pos: str = Form("meio baixo"),
    theme: str = Form("amarelo vermelho"),
    margin_v: int = Form(150),
    effect: str = Form("Pulo (Pop)"),
    border_w: int = Form(3)
):
    check_user_status()
    try:
        temp_dir = os.path.join(os.getcwd(), 'temp', 'gerador_legendas_web')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save video
        video_path = os.path.join(temp_dir, f"input_{int(time.time())}_{video.filename}")
        with open(video_path, "wb") as f:
            f.write(await video.read())
            
        srt_path = None
        if srt:
            srt_path = os.path.join(temp_dir, f"input_{int(time.time())}_{srt.filename}")
            with open(srt_path, "wb") as f:
                f.write(await srt.read())
                
        out_path = video_path.replace(".mp4", "_legendado.mp4").replace(".mov", "_legendado.mov")
        if out_path == video_path:
            out_path += "_legendado.mp4"

        from aba_edicao_basica import generate_karaoke_ass
        
        # 1. Transcribe or parse SRT
        whisper_result = None
        
        def format_timestamp(sec):
            msec = int((sec - int(sec)) * 1000)
            s = int(sec); h = s // 3600; s %= 3600; m = s // 60; s %= 60
            return f"{h:02d}:{m:02d}:{s:02d},{msec:03d}"

        if srt_path:
            # Parse SRT
            with open(srt_path,'r',encoding='utf-8') as f: content = f.read()
            w_list = []
            for blk in content.strip().split('\n\n'):
                lines = blk.strip().split('\n')
                if len(lines) >= 3:
                    try:
                        s_str, e_str = lines[1].split(' --> ')
                        def t2s(ts):
                            pts = ts.replace(',','.').split(':')
                            return float(pts[0])*3600 + float(pts[1])*60 + float(pts[2])
                        w_list.append({'word': " ".join(lines[2:]), 'start': t2s(s_str), 'end': t2s(e_str)})
                    except Exception: pass
            whisper_result = {'segments': [{'words': w_list}]}
        else:
            if engine == 'whisper':
                import whisper
                model = whisper.load_model("base")
                try:
                    result = model.transcribe(video_path, fp16=False, language='pt', word_timestamps=True)
                except Exception:
                    result = model.transcribe(video_path, fp16=False, language='pt')
                for seg in result.get('segments', []):
                    if 'words' not in seg:
                        seg['words'] = [{'word': seg['text'], 'start': seg['start'], 'end': seg['end']}]
                whisper_result = result
            else:
                from vosk import Model, KaldiRecognizer
                import wave, subprocess, json
                wav_path = os.path.join(temp_dir, 'audio_for_vosk.wav')
                subprocess.run(['ffmpeg','-y','-i',video_path,'-vn','-ac','1','-ar','16000','-f','wav',wav_path], check=True, capture_output=True)
                
                # find vosk model
                target = r"E:/MEUS PROGRAMAS/HISTORIAS DE 7 DIAS CODIGOS/pre_edicao/vosk-model-pt-fb-v0.1.1-20220516_2113"
                if not os.path.isdir(target):
                    raise Exception("Modelo Vosk nÃ£o encontrado no caminho padrÃ£o.")
                
                model = Model(target)
                rec = KaldiRecognizer(model, 16000); rec.SetWords(True)
                wf = wave.open(wav_path, 'rb')
                results = []
                while True:
                    data = wf.readframes(4000)
                    if not data: break
                    if rec.AcceptWaveform(data): results.append(json.loads(rec.Result()))
                results.append(json.loads(rec.FinalResult())); wf.close()
                w_list = [w for r in results if 'result' in r for w in r['result']]
                whisper_result = {'segments': [{'words': w_list}]}

        # Load preset if not customized
        final_font = font
        final_words = words
        final_size = size
        final_pos = pos
        final_theme = theme
        final_margin_v = margin_v
        final_effect = effect
        final_border_w = border_w
        sub_colors_ui = None

        if preset != "[Personalizado]":
            from config_manager import ConfigManager
            cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
            perfis = cm.get("perfis_legenda", {})
            p = perfis.get(preset, {})
            if p:
                final_font = p.get("font", font)
                final_words = p.get("words", words)
                final_pos = p.get("pos", pos)
                final_theme = p.get("theme", theme)
                final_size = p.get("size", size)
                final_margin_v = p.get("margin_v", margin_v)
                final_effect = p.get("effect", effect)
                final_border_w = p.get("border_w", border_w)
                if 'colors' in p:
                    sub_colors_ui = p['colors']

        ass_path = os.path.join(temp_dir, 'master_legendas.ass')
        generate_karaoke_ass(
            whisper_result  = whisper_result,
            srt_path        = ass_path,
            font            = final_font,
            size            = final_size,
            theme           = final_theme,
            colors          = sub_colors_ui,
            pos             = final_pos,
            margin_v        = final_margin_v,
            effect          = final_effect,
            video_format    = formato,
            words_per_block = final_words,
            voice_color_map = None,
            border_w        = final_border_w,
            perfis_personagem = None
        )

        esc_ass = ass_path.replace('\\','/').replace(':','\\:')
        cmd = [
            'ffmpeg','-y','-i', video_path,
            '-vf', f"ass='{esc_ass}'",
            '-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','medium',
            '-c:a','copy', out_path
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0:
            raise Exception(f"Erro no FFmpeg: {r.stderr[-400:]}")

        return {"success": True, "file": out_path}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ====== ENDPOINTS DA DUBLAGEM EXTERNA ======

@app.post("/api/dublagem/diarizar")
async def api_dublagem_diarizar(video: UploadFile = File(...)):
    import time, shutil, uuid
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        keys = cm.get_api_config("huggingface", "api_keys") or []
        hf_token = keys[0]["key"] if keys else ""
        
        if not hf_token:
            return {"success": False, "error": "Token do HuggingFace nÃ£o configurado."}
            
        temp_dir = os.path.join(os.getcwd(), 'temp', f'diarize_{uuid.uuid4().hex[:8]}')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save video
        vid_path = os.path.join(temp_dir, video.filename)
        with open(vid_path, "wb") as f:
            f.write(await video.read())
            
        from video_rvc_processor import VideoRVCProcessor
        from diarization_engine import DiarizationEngine
        processor = VideoRVCProcessor(cm, logger=print)
        engine = DiarizationEngine(logger=print)
        
        # Isolar vocais
        audio_raw = processor.extract_audio(vid_path, temp_dir)
        vocals_path, bg_path = processor.separate_vocals(audio_raw, temp_dir)
        
        # Pyannote
        segments = engine.diarize_vocals(vocals_path, hf_token)
        if not segments:
            return {"success": True, "speakers": []}
            
        samples_dir = os.path.join(temp_dir, "samples_preview")
        sample_map = engine.extract_samples(vocals_path, segments, samples_dir)
        
        # Build speaker list with relative URL
        speakers = []
        unique_spks = sorted(list(set([s["speaker_id"] for s in segments])))
        for spk in unique_spks:
            spk_path = sample_map.get(spk)
            if spk_path:
                rel_path = os.path.relpath(spk_path, os.path.join(os.getcwd(), 'temp')).replace("\\", "/")
                speakers.append({"id": spk, "sample_url": f"/temp/{rel_path}"})
                
        return {
            "success": True,
            "speakers": speakers,
            "segments": segments,
            "vocals_path": vocals_path,
            "bg_path": bg_path,
            "temp_dir": temp_dir
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/api/dublagem/processar")
async def api_dublagem_processar(
    skip_demucs: str = Form("false"),
    configs: str = Form(...),
    files: List[UploadFile] = File(...)
):
    check_user_status()
    import queue, threading, time, asyncio, json, shutil
    
    q = queue.Queue()
    
    # Save files to a common temp
    batch_temp = os.path.join(os.getcwd(), 'temp', f'dublagem_{int(time.time())}')
    os.makedirs(batch_temp, exist_ok=True)
    
    saved_files = {}
    for f in files:
        path = os.path.join(batch_temp, f.filename)
        with open(path, "wb") as out_f:
            out_f.write(await f.read())
        saved_files[f.filename] = path
        
    configs_list = json.loads(configs)
    b_skip_demucs = (skip_demucs.lower() == "true")
    
    def worker():
        try:
            from config_manager import ConfigManager
            from video_rvc_processor import VideoRVCProcessor
            from diarization_engine import DiarizationEngine
            from audio_processor import AudioProcessor
            
            cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
            
            def log_cb(msg):
                q.put(msg)
                
            processor = VideoRVCProcessor(cm, logger=log_cb)
            engine = DiarizationEngine(logger=log_cb)
            
            personagens_full_config = cm.get("personagens", {})
            
            out_dir = os.path.join(CURRENT_WORKSPACE_PATH, "OUTPUT_DUBLADOS")
            os.makedirs(out_dir, exist_ok=True)
            
            q.put(f"ð Iniciando Processamento em Lote...\n")
            
            cena_idx = 1
            
            for item in configs_list:
                video_path = saved_files.get(item["filename"])
                if not video_path: continue
                
                q.put(f"\n======================================")
                q.put(f"ð¬ [CENA {cena_idx}] Processando: {item['filename']}")
                
                temp_dir = item.get("temp_dir") or os.path.join(batch_temp, f"temp_cena_{cena_idx}")
                os.makedirs(temp_dir, exist_ok=True)
                
                final_output = os.path.join(out_dir, f"Cena_{cena_idx}_{item['filename']}")
                
                try:
                    if item.get("is_multi") and item.get("diarization_map"):
                        q.put(f"ðï¸ MODO MULTI-VOZ DE ESTÃDIO ATIVADO")
                        map_data = item["diarization_map"]
                        segments = item["segments"]
                        vocals_path = item["vocals_path"]
                        bg_path = item["bg_path"]
                        
                        fatias_dir = os.path.join(temp_dir, "fatias")
                        sliced_segments = engine.slice_vocals(vocals_path, segments, fatias_dir)
                        
                        for idx, seg in enumerate(sliced_segments):
                            spk = seg["speaker_id"]
                            char_name_mapped = map_data.get(spk)
                            
                            if char_name_mapped == "[Manter Voz Original]":
                                q.put(f"   -> Mantendo voz original para [{spk}]...")
                                seg["rvc_file_path"] = seg["file_path"]
                                continue
                                
                            char_config_mapped = personagens_full_config.get(char_name_mapped)
                            if char_config_mapped:
                                q.put(f"   -> Dublando fatia {idx+1}/{len(sliced_segments)} com a voz de [{char_name_mapped}]...")
                                rvc_fat_path = processor.process_rvc(seg["file_path"], temp_dir, char_config_mapped)
                                seg["rvc_file_path"] = rvc_fat_path
                                
                        costurado_path = os.path.join(temp_dir, "vocals_costurados.wav")
                        engine.stitch_vocals(vocals_path, sliced_segments, costurado_path)
                        
                        q.put("ð Aplicando RestauraÃ§Ã£o de Ãudio...")
                        ap = AudioProcessor()
                        ap.run_pipeline(costurado_path, costurado_path, cm.config)
                        
                        processor.mix_and_replace_video(video_path, costurado_path, bg_path, temp_dir, final_output)
                        
                    else:
                        char_name = item["char"]
                        char_config = personagens_full_config.get(char_name)
                        if not char_config or not char_config.get("modelo_rvc"):
                            q.put(f"â Personagem '{char_name}' sem modelo RVC.")
                            cena_idx += 1
                            continue
                            
                        audio_raw = processor.extract_audio(video_path, temp_dir)
                        
                        if b_skip_demucs:
                            vocals_path, bg_path = audio_raw, audio_raw
                        else:
                            vocals_path, bg_path = processor.separate_vocals(audio_raw, temp_dir)
                            
                        rvc_audio = processor.process_rvc(vocals_path, temp_dir, char_config)
                        
                        q.put("ð Aplicando RestauraÃ§Ã£o de Ãudio na voz isolada...")
                        ap = AudioProcessor()
                        ap.run_pipeline(rvc_audio, rvc_audio, cm.config)
                        
                        if b_skip_demucs or not bg_path:
                            q.put("Substituindo Ã¡udio seco...")
                            import subprocess
                            replace_cmd = ["ffmpeg", "-y", "-i", video_path, "-i", rvc_audio, "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", final_output]
                            subprocess.run(replace_cmd, check=True, capture_output=True)
                        else:
                            processor.mix_and_replace_video(video_path, rvc_audio, bg_path, temp_dir, final_output)
                            
                    q.put(f"â Cena {cena_idx} concluÃ­da! Salva como {os.path.basename(final_output)}")
                except Exception as e:
                    q.put(f"â Erro na cena {cena_idx}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
                cena_idx += 1
                
            q.put(f"\n======================================")
            q.put(f"â PROCESSAMENTO EM LOTE CONCLUÃDO!")
        except Exception as e:
            q.put(f"\nâ Erro fatal: {str(e)}")
        finally:
            q.put(None)
            
    threading.Thread(target=worker, daemon=True).start()
    
    async def event_generator():
        while True:
            try:
                msg = q.get_nowait()
                if msg is None: break
                yield msg + "\n"
            except queue.Empty:
                await asyncio.sleep(0.2)
                
    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_generator(), media_type="text/plain")

# ===== ROTAS DO TANQUE DE COMBUSTÃVEL =====

@app.get("/api/tanque/lista")
async def tanque_lista():
    if not CURRENT_WORKSPACE_PATH:
        return {"success": False, "error": "Workspace nÃ£o configurado"}
        
    pastas_alvo = [
        os.path.join(CURRENT_WORKSPACE_PATH, "outputs"),
        os.path.join(CURRENT_WORKSPACE_PATH, "audio"),
        CURRENT_WORKSPACE_PATH
    ]
    tipos_validos = ('.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.m4a', '.png', '.jpg', '.jpeg', '.json')
    arquivos_encontrados = []
    
    for pasta in pastas_alvo:
        if not os.path.exists(pasta):
            continue
        for f in os.listdir(pasta):
            if f.lower().endswith(tipos_validos):
                caminho_abs = os.path.join(pasta, f)
                if os.path.isfile(caminho_abs):
                    try:
                        tamanho_mb = os.path.getsize(caminho_abs) / (1024 * 1024)
                    except:
                        tamanho_mb = 0
                        
                    ext = os.path.splitext(f)[1].lower()
                    tipo = "VÃ­deo" if ext in ['.mp4', '.mkv', '.avi', '.mov'] else "Ãudio" if ext in ['.mp3', '.wav', '.m4a'] else "Imagem" if ext in ['.png', '.jpg', '.jpeg'] else "Template"
                    
                    arquivos_encontrados.append({
                        "nome": f,
                        "tipo": tipo,
                        "tamanho": f"{tamanho_mb:.2f}",
                        "caminho": caminho_abs
                    })
                    
    vistos = set()
    arquivos_finais = []
    for arq in arquivos_encontrados:
        if arq["caminho"] not in vistos:
            vistos.add(arq["caminho"])
            arquivos_finais.append(arq)
            
    return {"success": True, "arquivos": arquivos_finais}

class TanqueAbrirReq(BaseModel):
    caminho: str
    acao: str

@app.post("/api/tanque/abrir")
async def tanque_abrir(req: TanqueAbrirReq):
    import subprocess
    caminho = req.caminho
    if req.acao == "pasta":
        caminho = os.path.dirname(caminho)
        
    try:
        if os.name == 'nt':
            os.startfile(caminho)
        else:
            subprocess.Popen(["xdg-open", caminho])
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ===== ROTAS DO DIRETOR (PERFIS E CACHE) =====

class PerfilDiretorReq(BaseModel):
    nome: str
    config: dict = None

@app.get("/api/diretor/perfis_diretor")
async def get_perfis_diretor():
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get("perfis_diretor", {})
        return {"status": "success", "perfis": list(perfis.keys())}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/diretor/perfis_diretor")
async def save_perfil_diretor(req: PerfilDiretorReq):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get("perfis_diretor", {})
        perfis[req.nome] = req.config
        cm.set("cache_whisper", {})
        cm.save_config()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ===== ROTAS DE GESTÃO DE PERFIS (CENTRAL DE CONFIGURAÃÃES) =====

class RenameProfileReq(BaseModel):
    category: str  # e.g., 'perfis_diretor', 'perfis_legenda'
    old_name: str
    new_name: str

class DeleteProfileReq(BaseModel):
    category: str
    name: str

@app.post("/api/manage/rename_config_profile")
async def rename_config_profile(req: RenameProfileReq):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get(req.category, {})
        if req.old_name not in perfis:
            return {"status": "error", "message": "Perfil antigo nÃ£o encontrado."}
        if req.new_name in perfis:
            return {"status": "error", "message": "JÃ¡ existe um perfil com o novo nome."}
        
        # Renomear mantendo a ordem original
        novos_perfis = {}
        for k, v in perfis.items():
            if k == req.old_name:
                novos_perfis[req.new_name] = v
            else:
                novos_perfis[k] = v
        
        cm.set(req.category, novos_perfis)
        cm.save_config()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/manage/delete_config_profile")
async def delete_config_profile(req: DeleteProfileReq):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get(req.category, {})
        if req.name in perfis:
            del perfis[req.name]
            cm.set(req.category, perfis)
            cm.save_config()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class ManageStudioProfileReq(BaseModel):
    old_name: str = ""
    new_name: str = ""

@app.post("/api/manage/rename_studio_profile")
async def rename_studio_profile(req: ManageStudioProfileReq):
    try:
        perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
        old_path = os.path.join(perfis_dir, f"{req.old_name}.json")
        new_path = os.path.join(perfis_dir, f"{req.new_name}.json")
        if not os.path.exists(old_path):
            return {"status": "error", "message": "Template nÃ£o encontrado."}
        if os.path.exists(new_path):
            return {"status": "error", "message": "JÃ¡ existe um template com o novo nome."}
        os.rename(old_path, new_path)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/manage/delete_studio_profile")
async def delete_studio_profile(req: ManageStudioProfileReq):
    try:
        perfis_dir = os.path.join(BASE_DIR, "perfis_templates")
        path = os.path.join(perfis_dir, f"{req.old_name}.json")
        if os.path.exists(path):
            os.remove(path)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/diretor/perfis_diretor")
async def delete_perfil_diretor(req: PerfilDiretorReq):
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get("perfis_diretor", {})
        if req.nome in perfis:
            del perfis[req.nome]
            cm.set("perfis_diretor", perfis)
            cm.save_config()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/diretor/perfis_estetica")
async def get_perfis_estetica():
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get("perfis_estetica", {})
        # Adiciona [Personalizado] no frontend. Aqui mandamos as chaves reais.
        return {"status": "success", "perfis": list(perfis.keys())}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/diretor/perfis_legenda")
async def get_perfis_legenda():
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get("perfis_legenda", {})
        return {"status": "success", "perfis": list(perfis.keys())}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/diretor/perfis_transicao_template")
async def get_perfis_transicao_template():
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = cm.get("perfis_transicao_template", {})
        return {"status": "success", "perfis": list(perfis.keys())}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/whisper/limpar_cache")
async def limpar_cache_whisper():
    try:
        temp_audio_dir = os.path.join(os.getcwd(), 'temp_audio')
        if os.path.exists(temp_audio_dir):
            import shutil
            shutil.rmtree(temp_audio_dir, ignore_errors=True)
            os.makedirs(temp_audio_dir, exist_ok=True)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Monta arquivos temporÃ¡rios (samples de audio) e os estÃ¡ticos NO FINAL para nÃ£o sobrescrever rotas
temp_files_dir = os.path.join(os.getcwd(), 'temp')
os.makedirs(temp_files_dir, exist_ok=True)
app.mount("/temp", StaticFiles(directory=temp_files_dir), name="temp")

# Todo o conteÃºdo de web_ui serÃ¡ servido estaticamente pelo app.mount no final do arquivo
# ========================================================
# FILA AUTÃNOMA (BATCH QUEUE)
# ========================================================
import threading as _threading
import time as _time
import datetime as _datetime
import queue as _queue

# --- GERENCIADOR DE PROGRAMAS EXTERNOS ---
class _ExternalManager:
    """Gerencia a execuÃ§Ã£o de programas externos (Node.js/React, etc) em background."""
    def __init__(self):
        self.base_dir = os.path.join(BASE_DIR, "Programas externos")
        self.ferramentas_dir = os.path.join(os.path.dirname(BASE_DIR), "FERRAMENTAS")
        self.processes = {}
        import threading
        self.lock = threading.Lock()

    def _find_free_port(self):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def start_app(self, app_name):
        app_dir = os.path.join(self.base_dir, app_name)
        if not os.path.exists(app_dir):
            app_dir = os.path.join(self.ferramentas_dir, app_name)
            if not os.path.exists(app_dir):
                return {"status": "error", "message": f"Pasta do app nÃ£o encontrada em Programas externos nem em FERRAMENTAS."}
        
        with self.lock:
            if app_name in self.processes and self.processes[app_name]['status'] == 'running':
                if self.processes[app_name]['process'].poll() is None:
                    return {"status": "running", "port": self.processes[app_name]['port']}

            if os.path.exists(os.path.join(app_dir, "package.json")):
                port = self._find_free_port()
                env = os.environ.copy()
                env["PORT"] = str(port)
                env["VITE_PORT"] = str(port)
                
                CREATE_NO_WINDOW = 0x08000000
                cmd = "npm run dev -- --port " + str(port)
                
                try:
                    process = subprocess.Popen(
                        cmd, cwd=app_dir, env=env, shell=True, creationflags=CREATE_NO_WINDOW
                    )
                    self.processes[app_name] = {'process': process, 'port': port, 'status': 'running', 'type': 'node'}
                    return {"status": "started", "port": port}
                except Exception as e:
                    return {"status": "error", "message": str(e)}
            
            # --- SUPORTE A APPS PYTHON EXTERNOS ---
            elif os.path.exists(os.path.join(app_dir, "app.py")) or os.path.exists(os.path.join(app_dir, "main.py")) or os.path.exists(os.path.join(app_dir, "server.py")):
                port = self._find_free_port()
                env = os.environ.copy()
                env["PORT"] = str(port)
                
                if os.path.exists(os.path.join(app_dir, "app.py")): entry = "app.py"
                elif os.path.exists(os.path.join(app_dir, "server.py")): entry = "server.py"
                else: entry = "main.py"
                
                CREATE_NO_WINDOW = 0x08000000
                cmd = f"python {entry} --port {port}"
                
                try:
                    process = subprocess.Popen(
                        cmd, cwd=app_dir, env=env, shell=True, creationflags=CREATE_NO_WINDOW
                    )
                    self.processes[app_name] = {'process': process, 'port': port, 'status': 'running', 'type': 'python'}
                    return {"status": "started", "port": port}
                except Exception as e:
                    return {"status": "error", "message": str(e)}

            else:
                if self.ferramentas_dir in app_dir:
                    return {"status": "static", "path": f"ferramentas/{app_name}/index.html"}
                else:
                    return {"status": "static", "path": f"ext_apps/{app_name}/index.html"}

    def stop_app(self, app_name):
        with self.lock:
            if app_name in self.processes:
                process = self.processes[app_name]['process']
                if process.poll() is None:
                    try:
                        import psutil
                        parent = psutil.Process(process.pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        parent.kill()
                    except:
                        process.kill()
                self.processes[app_name]['status'] = 'stopped'
                return {"status": "stopped"}
        return {"status": "not_running"}

external_manager = _ExternalManager()


class _FilaManager:
    """Gerenciador de fila de renderizaÃ§Ã£o autÃ´noma em memÃ³ria."""
    STATUS_PENDENTE   = "â³ Pendente"
    STATUS_RENDERANDO = "ð Renderizando..."
    STATUS_CONCLUIDO  = "â ConcluÃ­do"
    STATUS_ERRO       = "â Erro"
    STATUS_CANCELADO  = "ð« Cancelado"

    def __init__(self):
        self.fila = []          # list of dicts
        self.rodando = False
        self.cancelar_flag = False
        self.log_buffer = []    # Ãºltimas 500 linhas
        self.hotfolder_ativo = False
        self.hotfolder_pasta = ""
        self._hotfolder_thread = None
        self._worker_thread = None
        self.progresso = 0      # 0-100
        self.eta = ""
        self._lock = _threading.Lock()

    def adicionar(self, projeto: dict):
        with self._lock:
            projeto.setdefault("nome",    "Sem nome")
            projeto.setdefault("audio",   "")
            projeto.setdefault("saida",   "")
            projeto.setdefault("roteiro", "")
            projeto.setdefault("musica",  "")
            projeto.setdefault("perfil",  "")
            projeto.setdefault("status",  self.STATUS_PENDENTE)
            projeto.setdefault("duracao", "â")
            self.fila.append(projeto)

    def remover(self, idx: int):
        with self._lock:
            if 0 <= idx < len(self.fila):
                self.fila.pop(idx)

    def reordenar(self, idx: int, direcao: int):
        with self._lock:
            novo = idx + direcao
            if 0 <= novo < len(self.fila):
                self.fila[idx], self.fila[novo] = self.fila[novo], self.fila[idx]

    def limpar_concluidos(self):
        with self._lock:
            before = len(self.fila)
            self.fila = [p for p in self.fila if p.get("status") not in
                         (self.STATUS_CONCLUIDO, self.STATUS_ERRO, self.STATUS_CANCELADO)]
            return before - len(self.fila)

    def _log(self, msg: str):
        ts = _datetime.datetime.now().strftime("%H:%M:%S")
        linha = f"[{ts}] {msg}"
        self.log_buffer.append(linha)
        if len(self.log_buffer) > 500:
            self.log_buffer = self.log_buffer[-500:]
        print(f"[FILA] {linha}")

    def get_status(self):
        with self._lock:
            return {
                "rodando": self.rodando,
                "cancelar_flag": self.cancelar_flag,
                "progresso": self.progresso,
                "eta": self.eta,
                "hotfolder_ativo": self.hotfolder_ativo,
                "hotfolder_pasta": self.hotfolder_pasta,
                "total": len(self.fila),
                "pendentes": sum(1 for p in self.fila if p["status"] == self.STATUS_PENDENTE),
                "concluidos": sum(1 for p in self.fila if p["status"] == self.STATUS_CONCLUIDO),
                "erros": sum(1 for p in self.fila if p["status"] == self.STATUS_ERRO),
                "fila": list(self.fila),
            }

    def iniciar(self, callback_render=None):
        pendentes = [p for p in self.fila if p.get("status") == self.STATUS_PENDENTE]
        if not pendentes:
            return False, "Nenhum projeto pendente na fila."
        if self.rodando:
            return False, "A fila jÃ¡ estÃ¡ em execuÃ§Ã£o."
        self.cancelar_flag = False
        self.rodando = True
        self._worker_thread = _threading.Thread(
            target=self._worker, args=(callback_render,), daemon=True)
        self._worker_thread.start()
        return True, "Fila iniciada."

    def parar(self):
        self.cancelar_flag = True
        self._log("â¸ Sinal de parada enviado. Aguardando projeto atual...")        

    def _worker(self, callback_render=None):
        inicio = _time.time()
        pendentes_total = sum(1 for p in self.fila if p.get("status") == self.STATUS_PENDENTE)
        processados = 0
        erros = 0

        self._log(f"ð Iniciando fila com {pendentes_total} projeto(s) pendente(s).")

        for proj in self.fila:
            if self.cancelar_flag:
                break
            if proj.get("status") != self.STATUS_PENDENTE:
                continue

            proj["status"] = self.STATUS_RENDERANDO
            inicio_proj = _time.time()
            self._log(f"ð¬ Iniciando: {proj['nome']}")

            ok = False
            try:
                if callback_render:
                    ok = callback_render(proj)
                else:
                    # SimulaÃ§Ã£o quando nÃ£o hÃ¡ render real conectado
                    _time.sleep(2)
                    ok = True
            except Exception as e:
                self._log(f"â ExceÃ§Ã£o no render de '{proj['nome']}': {e}")
                ok = False

            duracao = _time.time() - inicio_proj
            proj["duracao"] = f"{duracao:.0f}s"

            if self.cancelar_flag:
                proj["status"] = self.STATUS_CANCELADO
                self._log(f"ð« '{proj['nome']}' cancelado.")
            elif ok:
                proj["status"] = self.STATUS_CONCLUIDO
                processados += 1
                self._log(f"â '{proj['nome']}' concluÃ­do em {proj['duracao']}.")
            else:
                proj["status"] = self.STATUS_ERRO
                erros += 1
                self._log(f"â '{proj['nome']}' falhou.")

            # Atualiza progresso
            total_processados = sum(1 for p in self.fila if p["status"] != self.STATUS_PENDENTE and p["status"] != self.STATUS_RENDERANDO)
            self.progresso = int((total_processados / max(pendentes_total, 1)) * 100)

            # ETA
            decorrido = _time.time() - inicio
            if processados > 0:
                media_por_proj = decorrido / processados
                restantes = pendentes_total - processados - erros
                eta_sec = media_por_proj * restantes
                mins = int(eta_sec // 60)
                secs = int(eta_sec % 60)
                self.eta = f"~{mins}m {secs}s restantes"
            else:
                self.eta = ""

        total_sec = _time.time() - inicio
        self._log(f"ð Fila finalizada em {total_sec:.0f}s. â {processados} sucesso(s) | â {erros} erro(s).")
        self.rodando = False
        self.progresso = 100
        self.eta = "ConcluÃ­do"

    def toggle_hotfolder(self, pasta: str, ativo: bool):
        self.hotfolder_ativo = ativo
        self.hotfolder_pasta = pasta if ativo else ""
        if ativo:
            self._log(f"ð¤ Piloto AutomÃ¡tico ATIVO â monitorando: {pasta}")
            self._hotfolder_thread = _threading.Thread(
                target=self._hotfolder_worker, daemon=True)
            self._hotfolder_thread.start()
        else:
            self._log("ð¤ Piloto AutomÃ¡tico DESATIVADO.")

    def _hotfolder_worker(self):
        """Monitora a pasta e enfileira novos arquivos de Ã¡udio."""
        import glob as _glob
        processados_hf = set()
        self._log(f"[HotFolder] Iniciando monitoramento em: {self.hotfolder_pasta}")
        while self.hotfolder_ativo:
            try:
                for ext in ("*.mp3", "*.wav", "*.m4a", "*.aac"):
                    for f in _glob.glob(os.path.join(self.hotfolder_pasta, ext)):
                        if f not in processados_hf:
                            processados_hf.add(f)
                            nome = os.path.splitext(os.path.basename(f))[0]
                            saida = os.path.join(self.hotfolder_pasta, "_outputs")
                            os.makedirs(saida, exist_ok=True)
                            self.adicionar({
                                "nome": f"[Auto] {nome}",
                                "audio": f,
                                "saida": saida,
                                "status": self.STATUS_PENDENTE,
                            })
                            self._log(f"[HotFolder] Novo arquivo detectado: {nome}")
                            if not self.rodando:
                                self.iniciar()
            except Exception as e:
                self._log(f"[HotFolder] Erro: {e}")
            _time.sleep(5)
        self._log("[HotFolder] Monitoramento encerrado.")


# InstÃ¢ncia global
_fila_manager = _FilaManager()


@app.get("/api/fila/status")
async def fila_status():
    return _fila_manager.get_status()


@app.get("/api/fila/log")
async def fila_log(n: int = 100):
    linhas = _fila_manager.log_buffer[-n:]
    return {"log": linhas}


class FilaAdicionarReq(BaseModel):
    nome: str = ""
    audio: str = ""
    saida: str = ""
    musica: str = ""
    roteiro: str = ""
    perfil: str = ""

@app.post("/api/fila/adicionar")
async def fila_adicionar(req: FilaAdicionarReq):
    check_user_status()
    if not req.audio:
        return {"success": False, "error": "Campo 'audio' Ã© obrigatÃ³rio."}
    nome = req.nome or os.path.splitext(os.path.basename(req.audio))[0]
    _fila_manager.adicionar({
        "nome": nome,
        "audio": req.audio,
        "saida": req.saida,
        "musica": req.musica,
        "roteiro": req.roteiro,
        "perfil": req.perfil,
        "status": _fila_manager.STATUS_PENDENTE,
        "duracao": "â",
    })
    _fila_manager._log(f"Projeto '{nome}' adicionado via Web UI.")
    return {"success": True, "total": len(_fila_manager.fila)}


class FilaLoteReq(BaseModel):
    audios: list  # list of str paths
    saida: str = ""
    perfil: str = ""

@app.post("/api/fila/adicionar_lote")
async def fila_adicionar_lote(req: FilaLoteReq):
    count = 0
    for audio in req.audios:
        if not audio:
            continue
        nome = os.path.splitext(os.path.basename(audio))[0]
        _fila_manager.adicionar({
            "nome": f"[Lote] {nome}",
            "audio": audio,
            "saida": req.saida,
            "perfil": req.perfil,
            "status": _fila_manager.STATUS_PENDENTE,
            "duracao": "â",
        })
        count += 1
    _fila_manager._log(f"{count} projeto(s) adicionado(s) em lote.")
    return {"success": True, "adicionados": count}


class FilaRemoverReq(BaseModel):
    idx: int

@app.post("/api/fila/remover")
async def fila_remover(req: FilaRemoverReq):
    _fila_manager.remover(req.idx)
    return {"success": True}


class FilaReordenarReq(BaseModel):
    idx: int
    direcao: int  # -1 ou +1

@app.post("/api/fila/reordenar")
async def fila_reordenar(req: FilaReordenarReq):
    _fila_manager.reordenar(req.idx, req.direcao)
    return {"success": True}


@app.post("/api/fila/limpar_concluidos")
async def fila_limpar_concluidos():
    removidos = _fila_manager.limpar_concluidos()
    return {"success": True, "removidos": removidos}


@app.post("/api/fila/iniciar")
async def fila_iniciar():
    check_user_status()
    ok, msg = _fila_manager.iniciar()
    return {"success": ok, "message": msg}


@app.post("/api/fila/parar")
async def fila_parar():
    _fila_manager.parar()
    return {"success": True}


class FilaHotfolderReq(BaseModel):
    pasta: str = ""
    ativo: bool = False

@app.post("/api/fila/hotfolder")
async def fila_hotfolder(req: FilaHotfolderReq):
    _fila_manager.toggle_hotfolder(req.pasta, req.ativo)
    return {"success": True, "ativo": req.ativo}


@app.get("/api/fila/perfis_diretor")
async def fila_perfis_diretor():
    try:
        from config_manager import ConfigManager
        cm = ConfigManager(os.path.join(CURRENT_WORKSPACE_PATH, "config.json"))
        perfis = list((cm.get("perfis_diretor") or {}).keys())
        return {"success": True, "perfis": perfis}
    except Exception as e:
        return {"success": True, "perfis": []}


# ========================================================
# MONTADOR â TRANSIÃÃES, CTAs E LOGOMARCAS
# ========================================================
import random as _random

_MONTADOR_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache_montador.json")
_montador_status = {
    "rodando": False,
    "progresso": 0,
    "mensagem": "Aguardando...",
    "total": 0,
    "processados": 0,
    "erros": 0,
}


@app.get("/api/montador/cache")
async def montador_cache_get():
    """Retorna o cache das pastas configuradas."""
    if os.path.exists(_MONTADOR_CACHE_FILE):
        try:
            with open(_MONTADOR_CACHE_FILE, 'r', encoding='utf-8') as f:
                return {"success": True, "cache": json.load(f)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": True, "cache": {
        "pasta_trans_h": "", "pasta_trans_v": "",
        "pasta_cta_h": "",   "pasta_cta_v": "",
        "pasta_logo_h": "",  "pasta_logo_v": "",
    }}


@app.post("/api/montador/cache")
async def montador_cache_post(request: Request):
    """Salva o cache das pastas configuradas."""
    try:
        data = await request.json()
        with open(_MONTADOR_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/montador/verificar_pastas")
async def montador_verificar_pastas(
    pasta_trans_h: str = "", pasta_trans_v: str = "",
    pasta_cta_h: str   = "", pasta_cta_v: str   = "",
    pasta_logo_h: str  = "", pasta_logo_v: str  = ""
):
    """Conta quantos .mp4 existem em cada pasta de assets."""
    labels = {
        "pasta_trans_h": "TransiÃ§Ãµes Horizontal",
        "pasta_trans_v": "TransiÃ§Ãµes Vertical",
        "pasta_cta_h":   "Somente CTA Horizontal",
        "pasta_cta_v":   "Somente CTA Vertical",
        "pasta_logo_h":  "Logomarcas Horizontal",
        "pasta_logo_v":  "Logomarcas Vertical",
    }
    pastas = {
        "pasta_trans_h": pasta_trans_h, "pasta_trans_v": pasta_trans_v,
        "pasta_cta_h":   pasta_cta_h,   "pasta_cta_v":   pasta_cta_v,
        "pasta_logo_h":  pasta_logo_h,  "pasta_logo_v":  pasta_logo_v,
    }
    resultado = {}
    for key, pasta in pastas.items():
        if not pasta:
            resultado[key] = {"label": labels[key], "status": "nao_configurada", "count": 0}
        elif not os.path.exists(pasta):
            resultado[key] = {"label": labels[key], "status": "nao_encontrada", "count": 0}
        else:
            try:
                count = len([f for f in os.listdir(pasta) if f.lower().endswith('.mp4')])
                resultado[key] = {"label": labels[key], "status": "ok" if count > 0 else "vazia", "count": count}
            except Exception as e:
                resultado[key] = {"label": labels[key], "status": "erro", "count": 0, "error": str(e)}
    return {"success": True, "pastas": resultado}


@app.get("/api/montador/status")
async def montador_status_get():
    return dict(_montador_status)


class MontadorProcessarReq(BaseModel):
    videos: list        # lista de caminhos absolutos
    formato: str        # 'horizontal' ou 'vertical'
    usar_transicao: bool = True
    usar_cta: bool = False
    usar_logomarca: bool = False
    pasta_trans_h: str = ""
    pasta_trans_v: str = ""
    pasta_cta_h: str   = ""
    pasta_cta_v: str   = ""
    pasta_logo_h: str  = ""
    pasta_logo_v: str  = ""


@app.post("/api/montador/processar")
async def montador_processar(req: MontadorProcessarReq):
    """Processa vÃ­deos adicionando transiÃ§Ãµes/CTAs/logomarcas. Retorna log por SSE."""
    check_user_status()
    import queue as _q
    import asyncio
    from fastapi.responses import StreamingResponse

    q = _q.Queue()

    def _log(msg: str):
        print(f"[MONTADOR] {msg}")
        q.put(msg)

    def _get_video_dimensions(video_path):
        try:
            res = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                 '-show_entries', 'stream=width,height', '-of', 'csv=p=0', video_path],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if res.returncode == 0:
                dims = res.stdout.strip().split(',')
                if len(dims) == 2:
                    return int(dims[0]), int(dims[1])
        except Exception:
            pass
        return 1080, 1920  # Fallback vertical

    def _anexar_video_aleatorio(video_path, pasta_assets, sufixo, encoder):
        try:
            assets = [f for f in os.listdir(pasta_assets) if f.lower().endswith('.mp4')]
            if not assets:
                _log(f"â ï¸ Nenhum .mp4 encontrado em: {pasta_assets}")
                return None
            asset_escolhido = _random.choice(assets)
            asset_path = os.path.join(pasta_assets, asset_escolhido)
            _log(f"ð Usando asset: {asset_escolhido} ({sufixo})")

            vw, vh = _get_video_dimensions(video_path)
            nome_base = os.path.splitext(os.path.basename(video_path))[0]
            pasta_saida = os.path.dirname(video_path)
            output_path = os.path.join(pasta_saida, f"{nome_base}{sufixo}.mp4")
            asset_temp   = os.path.join(pasta_saida, f"_temp_asset{sufixo}_{nome_base}.mp4")

            # 1. Redimensionar asset
            cmd_resize = [
                'ffmpeg', '-y', '-threads', '0', '-hwaccel', 'auto', '-i', asset_path,
                '-vf', f'scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:black'
            ]
            if encoder == 'libx264':
                cmd_resize += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast']
            else:
                cmd_resize += ['-c:v', encoder, '-b:v', '6M', '-pix_fmt', 'yuv420p']
            cmd_resize += ['-c:a', 'aac', asset_temp]
            subprocess.run(cmd_resize, capture_output=True,
                           creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)

            if not os.path.exists(asset_temp):
                _log(f"â Falha no redimensionamento do asset.")
                return None

            # 2. Concatenar
            cmd_concat = [
                'ffmpeg', '-y', '-threads', '0',
                '-hwaccel', 'auto', '-i', video_path,
                '-hwaccel', 'auto', '-i', asset_temp,
                '-filter_complex',
                f'[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1:unsafe=1[concatv][outa];'
                f'[concatv]scale={vw}:{vh}:force_original_aspect_ratio=decrease,pad={vw}:{vh}:(ow-iw)/2:(oh-ih)/2:black[outv]',
                '-map', '[outv]', '-map', '[outa]'
            ]
            if encoder == 'libx264':
                cmd_concat += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'fast']
            else:
                cmd_concat += ['-c:v', encoder, '-b:v', '6M', '-pix_fmt', 'yuv420p']
            cmd_concat += ['-c:a', 'aac', output_path]

            res = subprocess.run(cmd_concat, capture_output=True,
                                 creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            try:
                os.remove(asset_temp)
            except Exception:
                pass

            if res.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                _log(f"â Erro ffmpeg ({sufixo}): {res.stderr[-300:]}")
                return None
        except Exception as e:
            _log(f"â ExceÃ§Ã£o ({sufixo}): {e}")
            return None

    def worker():
        global _montador_status
        try:
            # Detecta encoder
            try:
                from hardware_detector import detect_h264_encoder
                encoder = detect_h264_encoder()
            except Exception:
                encoder = 'libx264'
            _log(f"ð§ Encoder detectado: {encoder}")

            formato = req.formato.lower()
            pasta_trans = req.pasta_trans_h if formato == 'horizontal' else req.pasta_trans_v
            pasta_cta   = req.pasta_cta_h   if formato == 'horizontal' else req.pasta_cta_v
            pasta_logo  = req.pasta_logo_h  if formato == 'horizontal' else req.pasta_logo_v

            total = len(req.videos)
            _montador_status.update({"rodando": True, "total": total, "processados": 0, "erros": 0, "progresso": 0})
            _log(f"ð Iniciando processamento de {total} vÃ­deo(s) â Formato: {formato}")

            for idx, video_path in enumerate(req.videos):
                if not os.path.exists(video_path):
                    _log(f"â Arquivo nÃ£o encontrado: {video_path}")
                    _montador_status["erros"] += 1
                    continue

                nome = os.path.basename(video_path)
                _log(f"\nð¹ [{idx+1}/{total}] Processando: {nome}")
                _montador_status["mensagem"] = f"Processando {idx+1}/{total}: {nome}"

                current = video_path
                temp_files = []

                if req.usar_transicao and pasta_trans and os.path.exists(pasta_trans):
                    _log("  â Aplicando TransiÃ§Ã£o...")
                    resultado = _anexar_video_aleatorio(current, pasta_trans, "_trans", encoder)
                    if resultado:
                        if current != video_path:
                            temp_files.append(current)
                        current = resultado
                    else:
                        _log("  â ï¸ TransiÃ§Ã£o falhou, continuando sem ela.")

                if req.usar_cta and pasta_cta and os.path.exists(pasta_cta):
                    _log("  â Aplicando CTA...")
                    resultado = _anexar_video_aleatorio(current, pasta_cta, "_cta", encoder)
                    if resultado:
                        if current != video_path:
                            temp_files.append(current)
                        current = resultado
                    else:
                        _log("  â ï¸ CTA falhou, continuando.")

                if req.usar_logomarca and pasta_logo and os.path.exists(pasta_logo):
                    _log("  â Aplicando Logomarca+CTA...")
                    resultado = _anexar_video_aleatorio(current, pasta_logo, "_logo", encoder)
                    if resultado:
                        if current != video_path:
                            temp_files.append(current)
                        current = resultado
                    else:
                        _log("  â ï¸ Logomarca falhou, continuando.")

                # Renomear resultado final para *_processado.mp4
                if current != video_path:
                    final_name = os.path.join(
                        os.path.dirname(video_path),
                        f"{os.path.splitext(os.path.basename(video_path))[0]}_processado.mp4"
                    )
                    if os.path.exists(final_name):
                        try:
                            os.remove(final_name)
                        except Exception:
                            final_name = current
                    if current != final_name:
                        try:
                            os.rename(current, final_name)
                        except Exception:
                            final_name = current
                    _log(f"  â Salvo: {os.path.basename(final_name)}")

                for t in temp_files:
                    try:
                        if os.path.exists(t):
                            os.remove(t)
                    except Exception:
                        pass

                _montador_status["processados"] += 1
                _montador_status["progresso"] = int(((idx + 1) / total) * 100)

            _log(f"\nð ConcluÃ­do! {_montador_status['processados']}/{total} vÃ­deo(s) processado(s).")
            _montador_status["mensagem"] = "ConcluÃ­do!"
        except Exception as e:
            _log(f"â Erro fatal: {e}")
        finally:
            _montador_status["rodando"] = False
            q.put(None)  # Sinal de fim

    import threading as _thr
    _thr.Thread(target=worker, daemon=True).start()

    async def event_gen():
        while True:
            try:
                msg = q.get_nowait()
                if msg is None:
                    yield f"data: __DONE__\n\n"
                    break
                yield f"data: {msg}\n\n"
            except _q.Empty:
                await asyncio.sleep(0.2)

    return StreamingResponse(event_gen(), media_type="text/event-stream")

# --- ENDPOINTS: PROGRAMAS EXTERNOS ---
@app.post("/api/externos/iniciar")
async def externos_iniciar(req: Request):
    try:
        data = await req.json()
        app_name = data.get("app_name")
        if not app_name:
            return JSONResponse({"status": "error", "message": "Nenhum aplicativo especificado."})
        res = external_manager.start_app(app_name)
        return JSONResponse(res)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/api/externos/status")
def externos_status(app_name: str):
    with external_manager.lock:
        if app_name in external_manager.processes:
            p = external_manager.processes[app_name]
            if p['process'].poll() is None:
                return JSONResponse({"status": "running", "port": p['port']})
            else:
                external_manager.processes[app_name]['status'] = 'stopped'
                return JSONResponse({"status": "stopped"})
        return JSONResponse({"status": "not_running"})

# --- ENDPOINTS: LA PLATA NATIVO ---
@app.post("/api/laplata/generate")
async def laplata_generate(req: Request):
    import requests
    try:
        data = await req.json()
        tool = data.get("tool")
        
        # Obter chaves de API (pode vir do config.json no futuro, por ora fixamos a que veio do JS)
        openrouter_key = "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"
        
        prompt = ""
        system_prompt = "VocÃª Ã© uma InteligÃªncia Artificial avanÃ§ada. Responda em PortuguÃªs do Brasil de forma direta, sem introduÃ§Ãµes desnecessÃ¡rias."
        
        if tool == "prompt":
            desc = data.get("mainDescription", "")
            estilo = data.get("visualStyle", "")
            qualidade = data.get("quality", "")
            elementos = ", ".join(data.get("additionalElements", []))
            prompt = f"Crie um prompt profissional (em inglÃªs, pois geradores de imagem funcionam melhor em inglÃªs) para geraÃ§Ã£o de imagens com IA baseado nos seguintes parÃ¢metros:\nDescriÃ§Ã£o Principal: {desc}\nEstilo Visual: {estilo}\nQualidade: {qualidade}\nElementos Adicionais: {elementos}\nCrie um prompt detalhado e profissional."
            
        elif tool == "hashtag":
            niche = data.get("niche", "")
            market = data.get("market", "")
            quantity = data.get("quantity", "15")
            prompt = f"Crie {quantity} hashtags estratÃ©gicas para redes sociais baseado no nicho '{niche}' e mercado '{market}'. Retorne apenas as hashtags separadas por espaÃ§o."
            
        elif tool == "descrever":
            imagem_url = data.get("imageUrl", "")
            if not imagem_url:
                prompt = f"Descreva de forma extremamente detalhada e criativa a seguinte cena: {data.get('texto', 'uma cena genÃ©rica')} (Simulando uma imagem se a URL falhar)."
            else:
                prompt = f"Descreva a imagem contida nesta URL de forma rica em detalhes: {imagem_url}"
                
        elif tool == "mineracao":
            assunto = data.get("subject", "")
            prompt = f"Aja como um analista de tendÃªncias e algoritmo de redes sociais (TikTok, Reels, Shorts). O usuÃ¡rio forneceu o nicho/assunto: '{assunto}'. Identifique os formatos e temas de vÃ­deos que estÃ£o mais bombando (virais) atualmente neste nicho na internet. ForneÃ§a uma lista de 5 estruturas exatas de vÃ­deos virais, detalhando para cada um:\n1) O gancho (hook) visual e falado dos primeiros 3 segundos;\n2) O conceito/roteiro principal;\n3) Por que o algoritmo estÃ¡ entregando tanto esse tipo de conteÃºdo. Seja altamente estratÃ©gico."
            
        elif tool == "titulos":
            tema = data.get("topic", "")
            tipo = data.get("type", "youtube")
            prompt = f"Gere 10 tÃ­tulos altamente magnÃ©ticos e com foco em clique (clickbait Ã©tico) para um conteÃºdo de {tipo} sobre o assunto: '{tema}'."
            
        elif tool == "descricoes":
            titulo = data.get("title", "")
            palavras = data.get("keywords", "")
            prompt = f"Crie uma descriÃ§Ã£o para um vÃ­deo do YouTube com o tÃ­tulo '{titulo}'. A descriÃ§Ã£o deve ser persuasiva, incluir call to action (CTA) e ser otimizada para SEO utilizando estas palavras-chave: {palavras}."
            
        elif tool == "gerador_imagem":
            ideia = data.get("idea", "")
            prompt = f"Escreva 3 prompts de imagem distintos (em inglÃªs) otimizados para Midjourney/Stable Diffusion com base nesta ideia: '{ideia}'. Cada prompt deve ter um estilo artÃ­stico diferente (ex: realista, cyberpunk, anime)."
            
        elif tool == "tendencias":
            setor = data.get("sector", "")
            prompt = f"Liste as 5 principais tendÃªncias atuais (trends) para criadores de conteÃºdo no setor de '{setor}'. Explique brevemente como um criador pode aproveitar cada tendÃªncia."
            
        if not prompt:
            return JSONResponse({"success": False, "error": "Ferramenta nÃ£o suportada ou parÃ¢metros invÃ¡lidos."})
            
        # Chamar OpenRouter
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.5-flash-preview",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            
            # Ferramentas La Plata agora sÃ£o gratuitas (custo 0) para incentivar o uso.
            # try:
            #     import user_database
            #     user_database.deduct_credits(1, 0, f"Uso de IA - La Plata: {tool}")
            # except:
            #     pass
                
            return JSONResponse({"success": True, "content": content})
        else:
            return JSONResponse({"success": False, "error": f"Erro na API externa: {response.text}"})
            
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

# --- ENDPOINTS: CENTRAL DAS NOTÃCIAS (SIMBIOSE) ---
@app.post("/api/grok")
async def api_grok(req: Request):
    import requests
    try:
        data = await req.json()
        api_key = data.get("apiKey")
        if not api_key:
            return JSONResponse({"error": "Missing API key"}, status_code=400)
            
        messages = data.get("messages", [])
        model = data.get("model", "grok-beta")
        temperature = data.get("temperature", 0.3)
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
        )
        return JSONResponse(response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/grok/models")
async def api_grok_models(req: Request):
    import requests
    try:
        data = await req.json()
        api_key = data.get("apiKey")
        if not api_key:
            return JSONResponse({"error": "Missing API key"}, status_code=400)
            
        response = requests.get(
            "https://api.x.ai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}"
            }
        )
        return JSONResponse(response.json(), status_code=response.status_code)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/proxy-image")
async def api_proxy_image(url: str):
    import requests
    from fastapi.responses import Response
    from urllib.parse import urlparse
    if not url:
        return Response(content="Missing url", status_code=400)
        
    try:
        parsed_url = urlparse(url)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': f"{origin}/"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return Response(content="Failed to fetch image", status_code=response.status_code)
            
        content_type = response.headers.get("content-type", "image/jpeg")
        if not content_type.startswith("image/"):
            return Response(content="Not an image", status_code=400)
            
        return Response(content=response.content, media_type=content_type, headers={"Cache-Control": "public, max-age=86400"})
    except requests.exceptions.Timeout:
        return Response(content="Image fetch timeout or network error", status_code=504)
    except Exception as e:
        return Response(content="Error fetching image", status_code=500)

@app.get("/api/search-youtube")
async def api_search_youtube(q: str = ""):
    import urllib.request, urllib.parse, re, json, random
    if not q:
        return JSONResponse({"error": "Missing query"}, status_code=400)
        
    try:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(q)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        match = re.search(r'var ytInitialData = (\{.*?\});<\/script>', html)
        if not match:
            return JSONResponse({"videos": []})
            
        data = json.loads(match.group(1))
        videos = []
        
        contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
        if contents:
            items = contents[0].get('itemSectionRenderer', {}).get('contents', [])
            for item in items:
                if 'videoRenderer' in item:
                    v = item['videoRenderer']
                    try:
                        title = v['title']['runs'][0]['text']
                        vid_id = v['videoId']
                        vid_url = f"https://youtube.com/watch?v={vid_id}"
                        thumbnails = v.get('thumbnail', {}).get('thumbnails', [])
                        thumbnail = thumbnails[-1]['url'] if thumbnails else ""
                        author = v.get('ownerText', {}).get('runs', [{}])[0].get('text', 'Unknown')
                        
                        view_text = v.get('viewCountText', {}).get('simpleText', '0')
                        views = 0
                        # Parse views like "1.2M views", "3,4 mil visualizaÃ§Ãµes", "123 visualizaÃ§Ãµes"
                        num_str = re.search(r'([\d,\.]+)', view_text)
                        if num_str:
                            val = float(num_str.group(1).replace(',', '.'))
                            lower_vt = view_text.lower()
                            if 'k' in lower_vt or 'mil' in lower_vt:
                                views = int(val * 1000)
                            elif 'm' in lower_vt or 'mi' in lower_vt:
                                views = int(val * 1000000)
                            else:
                                views = int(re.sub(r'\D', '', view_text) or 0)
                                
                        ago = v.get('publishedTimeText', {}).get('simpleText', '')
                        duration = v.get('lengthText', {}).get('simpleText', 'N/A')
                        
                        videos.append({
                            "title": title,
                            "url": vid_url,
                            "thumbnail": thumbnail,
                            "author": author,
                            "views": views,
                            "ago": ago,
                            "description": "",
                            "duration": duration
                        })
                    except Exception:
                        continue
                        
        # Filter logic similar to node.js implementation
        recent_videos = []
        for v in videos:
            if not v['ago']: continue
            ago_str = v['ago'].lower()
            if 'hour' in ago_str or 'hora' in ago_str or 'day' in ago_str or 'dia' in ago_str:
                recent_videos.append(v)
            elif 'week' in ago_str or 'semana' in ago_str:
                if '1' in ago_str or '2' in ago_str or 'uma' in ago_str or 'duas' in ago_str:
                    recent_videos.append(v)
                    
        videos_to_use = recent_videos if len(recent_videos) >= 6 else videos
        sorted_videos = sorted(videos_to_use, key=lambda x: x['views'], reverse=True)
        
        final_videos = []
        for v in sorted_videos[:12]:
            vw = v['views']
            v['likes'] = int(vw * (0.03 + random.random() * 0.02))
            v['comments'] = int(vw * (0.003 + random.random() * 0.005))
            v['shares'] = int(vw * (0.005 + random.random() * 0.01))
            final_videos.append(v)
            
        return JSONResponse({"videos": final_videos})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/search-images")
async def api_search_images(q: str = "", pixabay: str = "", pexels: str = ""):
    import urllib.request, urllib.parse, re, json
    import concurrent.futures

    if not q:
        return JSONResponse({"error": "Missing query"}, status_code=400)

    query = urllib.parse.quote(q)
    
    def fetch_url(url, headers):
        try:
            req = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(req, timeout=5).read().decode('utf-8', errors='ignore')
        except:
            return ""

    def scrape_ddg():
        html = fetch_url(f"https://duckduckgo.com/?q={query}&df=m&p=1", {'User-Agent': 'Mozilla/5.0'})
        match = re.search(r'vqd=([\'"]?)([^&"\']+)\1', html)
        imgs = []
        if match:
            vqd = match.group(2)
            res = fetch_url(f"https://duckduckgo.com/i.js?l=us-en&o=json&q={query}&vqd={vqd}&p=1&kp=1", {
                'User-Agent': 'Mozilla/5.0', 'Referer': 'https://duckduckgo.com/'
            })
            try:
                data = json.loads(res)
                for r in data.get('results', []):
                    if r.get('image') and r['image'].startswith('http'):
                        imgs.append({'url': r['image'], 'source': r.get('url', ''), 'thumbnail': r.get('thumbnail', '')})
            except:
                pass
        return imgs

    def scrape_bing():
        html = fetch_url(f"https://www.bing.com/images/search?q={query}&adlt=strict", {'User-Agent': 'Mozilla/5.0'})
        imgs = []
        for m in re.finditer(r'm="(\{.*?\})"', html):
            try:
                data = json.loads(m.group(1).replace('&quot;', '"'))
                if 'murl' in data and data['murl'].startswith('http'):
                    imgs.append({'url': data['murl'], 'source': data.get('purl', ''), 'thumbnail': data.get('turl', '')})
            except:
                continue
        return imgs
        
    def scrape_google():
        html = fetch_url(f"https://www.google.com/search?tbm=isch&q={query}&safe=active", {'User-Agent': 'Mozilla/5.0'})
        imgs = []
        for m in re.finditer(r'\["(https:\/\/[^"]+?\.(?:jpg|jpeg|png|webp))",\d+,\d+\]', html, re.IGNORECASE):
            url = m.group(1)
            if 'gstatic.com' not in url and 'fbsbx.com' not in url:
                try:
                    dec = json.loads(f'"{url}"')
                    imgs.append({'url': dec, 'source': f'https://www.google.com/search?tbm=isch&q={query}'})
                except: pass
        return imgs
        
    def scrape_yahoo():
        html = fetch_url(f"https://images.search.yahoo.com/search/images?p={query}&vm=r", {'User-Agent': 'Mozilla/5.0'})
        imgs = []
        for m in re.finditer(r'<img[^>]+(?:data-src|src)=[\'"](http[^\'"]+)[\'"]', html):
            src = m.group(1)
            if 'yimg.com/pv' not in src:
                imgs.append({'url': src, 'source': f'https://images.search.yahoo.com/search/images?p={query}'})
        return imgs
        
    def scrape_wiki():
        html = fetch_url(f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={query}&gsrnamespace=6&prop=imageinfo&iiprop=url&format=json&gsrlimit=10", {'User-Agent': 'Mozilla/5.0'})
        imgs = []
        try:
            data = json.loads(html)
            pages = data.get('query', {}).get('pages', {})
            for k, v in pages.items():
                info = v.get('imageinfo', [{}])[0]
                if 'url' in info:
                    imgs.append({'url': info['url'], 'source': info.get('descriptionurl', '')})
        except: pass
        return imgs

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        f_ddg = executor.submit(scrape_ddg)
        f_bing = executor.submit(scrape_bing)
        f_google = executor.submit(scrape_google)
        f_yahoo = executor.submit(scrape_yahoo)
        f_wiki = executor.submit(scrape_wiki)
        
        all_sources = [f_google.result(), f_bing.result(), f_ddg.result(), f_yahoo.result(), f_wiki.result()]
        
    unique_images = []
    seen = set()
    max_len = max([len(s) for s in all_sources] + [0])
    for i in range(max_len):
        for s in all_sources:
            if i < len(s):
                img = s[i]
                if img['url'] not in seen:
                    seen.add(img['url'])
                    unique_images.append(img)
                    
    return JSONResponse({"urls": unique_images[:40]})

# ====== ENDPOINTS: CENTRAL DAS NOTICIAS (IA) ======
class NoticiasReq(BaseModel):
    prompt_type: str
    input_text: str = ""
    format: str = "long"
    tone: str = "jornalistico"
    engine: str = "gemini"
    api_key_grok: str = ""
    api_key_or: str = ""
    profile_context: str = ""
    model_choice: str = "auto"
    images_count: int = 8
    news_count: int = 5
    allowed_types: list = []
    api_keys: dict = {}

@app.get("/api/public/models_pricing")
async def get_public_models_pricing():
    try:
        conn = user_database.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, model_id, provider, tier, input_price_per_1m, output_price_per_1m FROM models_pricing WHERE status='Ativo'")
        models = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"success": True, "models": models}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/noticias/ai")
async def api_noticias_ai(req: NoticiasReq):
    check_user_status()
    import requests
    
    sys_prompt = ""
    user_prompt = ""
    model = ""
    api_url = ""
    headers = {}
    
    if req.model_choice and req.model_choice != 'auto':
        import sqlite3
        conn = user_database.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM models_pricing WHERE model_id=?", (req.model_choice,))
        row = c.fetchone()
        
        if row:
            provider = row['provider'].lower()
            model = row['model_id']
            # Deduct base Gas for premium, with dynamic margin_multiplier
            estimated_cost = (row['input_price_per_1m'] * 0.002) + (row['output_price_per_1m'] * 0.002)
            multiplier = float(row.get('margin_multiplier', 1.3)) if 'margin_multiplier' in row.keys() else 1.3
            gas_cost = int(estimated_cost * multiplier * 100) or 1
            user_database.deduct_currency(1, gas_cost, "gas", f"Consumo IA Roteiro ({model})")
            
            if provider == 'grok':
                if not req.api_key_grok: return JSONResponse({"error": "Chave do Grok faltando"}, status_code=400)
                api_url = "https://api.x.ai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {req.api_key_grok}", "Content-Type": "application/json"}
            else:
                if not req.api_key_or: return JSONResponse({"error": "Chave do OpenRouter faltando"}, status_code=400)
                api_url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {"Authorization": f"Bearer {req.api_key_or}", "Content-Type": "application/json"}
        else:
            req.model_choice = 'auto'
        conn.close()

    if not req.model_choice or req.model_choice == 'auto':
        if req.engine == 'grok':
            if not req.api_key_grok: return JSONResponse({"error": "Chave do Grok faltando"}, status_code=400)
            api_url = "https://api.x.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {req.api_key_grok}", "Content-Type": "application/json"}
            model = "grok-beta"
        else:
            if not req.api_key_or: return JSONResponse({"error": "Chave do OpenRouter faltando"}, status_code=400)
            api_url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {req.api_key_or}", "Content-Type": "application/json"}
            model = "google/gemini-2.5-flash"
        
    if req.prompt_type == 'cacar':
        count = req.news_count if hasattr(req, 'news_count') and req.news_count else 5
        sys_prompt = f"""VocÃª Ã© um jornalista investigativo e curador de notÃ­cias focado em polÃ­tica e bastidores.
O usuÃ¡rio quer saber as {count} notÃ­cias MAIS QUENTES e RECENTES sobre o tema fornecido.

MUITO IMPORTANTE SOBRE A BUSCA E AS FONTES:
- Use a ferramenta de busca combinando palavras-chave especÃ­ficas para refinar a relevÃ¢ncia.
- Exemplo de busca: "(Revista Oeste OR Gazeta do Povo OR Jovem Pan OR Twitter OR Pleno News OR Poder360)"
- NÃO se limite apenas Ã  grande mÃ­dia tradicional (G1, CNN, Folha, UOL). Evite-as se possÃ­vel.
- DÃª FORTE PREFERÃNCIA e priorize mÃ­dias independentes, portais com viÃ©s de direita/conservador e jornalismo investigativo independente.
- Inclua tambÃ©m postagens, furos de reportagem ou debates relevantes do Twitter/X, se houver.
- O objetivo Ã© ter uma visÃ£o ampla que atenda a um pÃºblico que consome notÃ­cias de polÃ­tica nacional, direita e bastidores de BrasÃ­lia.
- ORDENE SEMPRE DA MAIS RECENTE PARA A MAIS ANTIGA (focando em hoje e nos Ãºltimos dias).

Retorne EXATAMENTE {count} notÃ­cias.
Para cada notÃ­cia, forneÃ§a:
1. title: O tÃ­tulo da notÃ­cia ou tweet.
2. summary: Um resumo bem curto (1 a 2 frases) do que se trata.
3. url: O link real da notÃ­cia ou da postagem.
4. source: O nome do portal, jornal ou rede social (ex: Revista Oeste, Twitter, Gazeta do Povo).
5. date: A data ou tempo de publicaÃ§Ã£o (ex: "Hoje", "HÃ¡ 2 horas", "Ontem").
6. imageUrl: A URL de uma imagem (thumbnail) da notÃ­cia. Se a busca retornar uma imagem associada Ã  matÃ©ria, coloque o link aqui. Se nÃ£o encontrar, deixe vazio ("").
7. imageSearchQuery: Uma query de busca curta (1 a 3 palavras) com o nome da pessoa ou assunto principal para buscar uma foto (ex: "Lula", "Bolsonaro", "STF", "Congresso").

Responda APENAS com um array JSON com objetos contendo essas propriedades. NADA DE MARKDOWN."""
        user_prompt = f"Busque as {count} notÃ­cias mais recentes sobre: \"{req.input_text}\""
        

    elif req.prompt_type == 'analisar-canal':
        sys_prompt = f"""Atue como um estrategista de YouTube. Analise os seguintes vÃ­deos salvos pelo criador de conteÃºdo. Com base nesses vÃ­deos, forneÃ§a:
1. Uma anÃ¡lise geral do nicho e do interesse do pÃºblico (quais temas geram mais interesse).
2. 5 ideias de vÃ­deos inÃ©ditos inspirados nesse conteÃºdo, mas com um Ã¢ngulo Ãºnico ou aprofundado.
3. Dicas de palavras-chave e estratÃ©gias de thumbnail para esse nicho.
Responda em Markdown, de forma clara e estruturada."""
        user_prompt = f"VÃ­deos salvos:\n{req.input_text}"


    elif req.prompt_type == 'monitorar-perfil':
        sys_prompt = f"""Extraia SOMENTE os dados reais e pÃºblicos referentes Ã  pÃ¡gina solicitada. Se nÃ£o conseguir ler, retorne JSON com erro.
Responda ESTRITAMENTE em formato JSON com o seguinte schema:
{{
  "username": "Nome de usuÃ¡rio",
  "followers": "NÃºmero de seguidores (ex: 1.2M)",
  "likes": "NÃºmero total de curtidas",
  "videos": "NÃºmero total de vÃ­deos",
  "recentVideos": [
    {{
      "title": "TÃ­tulo do vÃ­deo",
      "views": "100K",
      "likes": "5K",
      "date": "Data se houver"
    }}
  ]
}}"""
        user_prompt = f"Dados extraÃ­dos da pÃ¡gina / URL:\n{req.input_text}"

    elif req.prompt_type == 'gerar-estrategia':
        sys_prompt = f"""VocÃª Ã© um Estrategista Chefe de ConteÃºdo para o YouTube e sabe tudo sobre tendÃªncias e algoritmos.
Sua missÃ£o Ã© criar um plano de ataque de conteÃºdo URGENTE e PERSONALIZADO para o canal do usuÃ¡rio, focado nas notÃ­cias mais quentes de hoje.
Gere 3 ideias de vÃ­deos ALTAMENTE ESTRATÃGICOS que o usuÃ¡rio deve gravar AGORA.

Para cada ideia, forneÃ§a:
- title: Um tÃ­tulo forte e magnÃ©tico.
- whyNow: Por que este vÃ­deo deve ser feito HOJE (urgÃªncia, timing, hype).
- angle: Qual o Ã¢ngulo Ãºnico que o usuÃ¡rio deve abordar para se diferenciar da concorrÃªncia.
- urgency: "Alta", "MÃ©dia" ou "Baixa".
- competitorContext: O que a concorrÃªncia estÃ¡ fazendo sobre isso e como o usuÃ¡rio vai superÃ¡-los.

Responda APENAS com um array JSON. NADA DE MARKDOWN."""
        user_prompt = req.input_text
        
    elif req.prompt_type == 'gerar-roteiro':
        base_prompt = "VocÃª Ã© um roteirista de YouTube e especialista em SEO."
        if req.profile_context:
            base_prompt += f"\nINSTRUÃÃES DE IDENTIDADE DO CANAL:\nVocÃª DEVE adotar estritamente a identidade, linguagem e estilo definidos nos seguintes documentos do canal:\n{req.profile_context}\n"
            
        if req.format == 'shorts':
            sys_prompt = f"{base_prompt}\nCrie um roteiro EXTREMAMENTE DINÃMICO, RÃPIDO E RETENTIVO (menos de 60 segundos).\nTom selecionado: {req.tone}. Adapte o texto para este tom.\n\nSua resposta DEVE seguir EXATAMENTE esta estrutura em Markdown:\n# ð± OpÃ§Ãµes de TÃ­tulo (Para a legenda do vÃ­deo)\n[3 opÃ§Ãµes]\n# ð Roteiro do VÃ­deo Curto (TikTok/Shorts)\n[Roteiro com Hook, Corpo, CTA e SugestÃµes Visuais entre colchetes]"
        else:
            sys_prompt = f"{base_prompt}\nCrie um pacote completo (Roteiro + SEO) envolvente e direto considerando a modalidade: {req.format}.\nTom selecionado: {req.tone}. Adapte o texto para este tom.\n\nSua resposta DEVE seguir EXATAMENTE esta estrutura em Markdown:\n# ð¬ OpÃ§Ãµes de TÃ­tulo (Alta Taxa de Clique)\n[3 opÃ§Ãµes]\n# ð DescriÃ§Ã£o Otimizada para SEO\n[DescriÃ§Ã£o com palavras-chave]\n# ð·ï¸ Tags Virais\n[15 a 20 tags]\n# ð Roteiro do VÃ­deo\n[Roteiro completo: Gancho, Desenvolvimento, SugestÃµes Visuais e ConclusÃ£o]"
        user_prompt = f"Use as seguintes informaÃ§Ãµes/tÃ³picos para criar o roteiro:\n\n{req.input_text}"
        
    elif req.prompt_type == 'minerar':
        sys_prompt = "VocÃª Ã© um estrategista de conteÃºdo para YouTube.\nAnalise o vÃ­deo fornecido e sugira 3 ideias de vÃ­deos similares, PORÃM MELHORES, para eu gravar no meu canal.\nDesconstrua os gatilhos mentais do tÃ­tulo e sugira como o meu roteiro deve ser estruturado.\nUse formataÃ§Ã£o Markdown."
        user_prompt = req.input_text
        
    elif req.prompt_type == 'estrategia':
        sys_prompt = "VocÃª Ã© um estrategista de YouTube nÃ­vel SÃªnior. Sua tarefa Ã© analisar o contexto do canal e a lista de concorrentes fornecida, e sugerir 5 ideias de vÃ­deos URGENTES ou EXCLUSIVAS que o canal deve gravar AGORA para se destacar.\n\nRetorne EXATAMENTE um JSON que Ã© um array de 5 objetos com as seguintes propriedades:\n- title: TÃ­tulo forte e chamativo do vÃ­deo.\n- urgency: Grau de urgÃªncia (Alta!, Alta, MÃ©dia, Baixa) baseado em tendÃªncias atuais.\n- whyNow: Por que este vÃ­deo deve ser feito hoje (ex: hype, notÃ­cia de Ãºltima hora, gap no mercado).\n- angle: Qual o Ã¢ngulo Ãºnico/diferencial que nosso canal pode adotar em relaÃ§Ã£o Ã  concorrÃªncia.\n- competitorContext: Como os concorrentes cobriram (ou falharam em cobrir) este assunto.\n\nResponda APENAS com o JSON vÃ¡lido, sem formato markdown (sem ```json)."
        user_prompt = req.input_text

    elif req.prompt_type == 'dashboard':
        sys_prompt = f"Retorne as 6 notÃ­cias mais importantes do dia sobre a categoria: {req.input_text}.\nResponda APENAS com um array JSON com objetos contendo: title, summary, source, date, url.\nSem formatacao markdown, apenas o json cru."
        user_prompt = "Me dÃª as notÃ­cias."
        
    elif req.prompt_type == 'images':
        sys_prompt = f"VocÃª Ã© um diretor de arte experiente e precisa selecionar as melhores imagens de B-roll para um vÃ­deo do YouTube. O usuÃ¡rio fornecerÃ¡ um script e o nÃºmero de imagens ({req.images_count}) que precisam ser selecionadas. Retorne EXATAMENTE UM JSON ARRAY com {req.images_count} objetos e NADA MAIS. NADA DE MARKDOWN.\n\nFormato obrigatÃ³rio do JSON:\n[{{\n  \"id\": 1,\n  \"description\": \"DescriÃ§Ã£o do que precisamos ver na imagem (em PT-BR)\",\n  \"searchQuery\": \"Uma query EM INGLÃS pronta para ser buscada no Google Images\",\n  \"context\": \"O trecho do script que motivou esta imagem\",\n  \"type\": \"photo\" // Um dos tipos permitidos\n}}]\n\nTipos permitidos: {', '.join(req.allowed_types)}."
        user_prompt = f"Extraia {req.images_count} imagens de apoio para este roteiro:\n\n{req.input_text}"
        
    elif req.prompt_type == 'seo':
        sys_prompt = "VocÃª Ã© um especialista em SEO para YouTube (foco em vÃ­deos virais e retenÃ§Ã£o). Seu objetivo Ã© otimizar tÃ­tulos, descriÃ§Ãµes e tags para vÃ­deos. Retorne o resultado em formato de texto estruturado."
        user_prompt = f"Otimize o SEO para o seguinte roteiro de vÃ­deo:\n\n{req.input_text}"
        

    elif req.prompt_type == 'gerar-shorts':
        sys_prompt = "VocÃª Ã© um roteirista de YouTube Shorts focado em retenÃ§Ã£o. Crie um roteiro EXTREMAMENTE DINÃMICO e RÃPIDO (menos de 60 segundos) com base na notÃ­cia/texto fornecido. Retorne em formato Markdown com as seÃ§Ãµes: # ð± OpÃ§Ãµes de TÃ­tulo (3 opÃ§Ãµes), # ð Roteiro do VÃ­deo Curto."
        user_prompt = f"Gere um roteiro curto para: {req.input_text}"

    elif req.prompt_type == 'ideias-thumbnails':
        sys_prompt = "VocÃª Ã© um designer de thumbnails de YouTube focado em CTR (Click-Through Rate). Analise o roteiro ou contexto fornecido e sugira 3 ideias brilhantes de thumbnails que despertem alta curiosidade. Descreva os elementos visuais, a composiÃ§Ã£o, e o texto exato na imagem para cada uma. Retorne em formato Markdown."
        user_prompt = f"Sugira 3 thumbnails para:\n\n{req.input_text}"

    elif req.prompt_type == 'deep-dive':
        sys_prompt = "VocÃª Ã© um jornalista investigativo e analista geopolÃ­tico/econÃ´mico. Aprofunde-se no contexto da notÃ­cia fornecida, explicando o pano de fundo, os interesses envolvidos, os desdobramentos futuros e o que a grande mÃ­dia pode estar omitindo. Retorne em formato Markdown."
        user_prompt = f"Aprofunde esta noticia:\n\n{req.input_text}"

    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3 if req.prompt_type == 'cacar' else 0.7
        }
        res = requests.post(api_url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        data = res.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if req.prompt_type == 'images':
            import json
            try:
                clean_content = content.replace("```json", "").replace("```", "").strip()
                assets = json.loads(clean_content)
                return JSONResponse({"status": "success", "assets": assets})
            except Exception as e:
                return JSONResponse({"status": "error", "message": f"Erro parse json: {str(e)}"}, status_code=500)
        elif req.prompt_type == 'monitorar-perfil':
            import json
            try:
                clean_content = content.replace("```json", "").replace("```", "").strip()
                data_parsed = json.loads(clean_content)
                return JSONResponse({"status": "success", "data": data_parsed})
            except Exception as e:
                return JSONResponse({"status": "error", "message": f"Erro parse json: {str(e)}"}, status_code=500)
        elif req.prompt_type == 'seo':
            return JSONResponse({"status": "success", "seo_content": content})
        elif req.prompt_type == 'cacar':
            import json
            try:
                clean_content = content.replace("```json", "").replace("```", "").strip()
                news = json.loads(clean_content)
                return JSONResponse({"status": "success", "news": news})
            except Exception as e:
                return JSONResponse({"success": True, "content": content})
            
        return JSONResponse({"success": True, "content": content})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/api/admin/trends")
async def get_ai_trends():
    try:
        conn = user_database.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM ai_trends_reports ORDER BY id DESC LIMIT 50")
        trends = [dict(row) for row in c.fetchall()]
        conn.close()
        return {"success": True, "trends": trends}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/admin/trigger-trends")
async def trigger_trends():
    try:
        import trend_researcher_agent
        result = trend_researcher_agent.run_trend_researcher()
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/admin/scraper/sync")
async def manual_scraper_sync():
    try:
        res = await asyncio.to_thread(run_scraper_agent)
        return {"success": True, "details": res}
    except Exception as e:
        return {"success": False, "error": str(e)}

try:
    from market_analyst_agent import run_market_analyst
except ImportError:
    run_market_analyst = None


@app.post("/api/admin/market_analyst/run")
async def manual_market_analyst_run():
    # Em um cenario real, voce pode passar a API Key premium resgatada do BD ou settings.
    try:
        res = await asyncio.to_thread(run_market_analyst, None)
        return {"success": True, "details": res}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/admin/market_analyst/reports")
async def get_market_reports():
    try:
        conn = user_database.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM market_analysis_reports ORDER BY created_at DESC LIMIT 10")
        reports = [dict(row) for row in c.fetchall()]
        conn.close()
        return {"success": True, "reports": reports}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/public/campaigns")
async def get_public_campaigns():
    """Retorna as campanhas ativas para os usuarios finais."""
    try:
        conn = user_database.get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, title, image_url, link_url FROM ad_campaigns WHERE is_active = 1 ORDER BY id DESC LIMIT 5")
        campaigns = [dict(row) for row in c.fetchall()]
        conn.close()
        return {"success": True, "campaigns": campaigns}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/public/campaigns/{campaign_id}/view")
async def register_campaign_view(campaign_id: int):
    try:
        conn = user_database.get_connection()
        c = conn.cursor()
        c.execute("UPDATE ad_campaigns SET views = views + 1 WHERE id = ?", (campaign_id,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False}

@app.post("/api/public/campaigns/{campaign_id}/click")
async def register_campaign_click(campaign_id: int):
    try:
        conn = user_database.get_connection()
        c = conn.cursor()
        c.execute("UPDATE ad_campaigns SET clicks = clicks + 1 WHERE id = ?", (campaign_id,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False}

class StudioGenerateRequest(BaseModel):
    type: str
    prompt: str
    image_base64: str = None
    model: str = "ltx"
    preset: str = "none"
    duration: int = 5
    steps: int = 50
    aspect_ratio: str = "16:9"
    seed: int = -1
    negative_prompt: str = ""
    motion_scale: float = 1.0
    guidance_scale: float = 3.0

class EnhanceVideoRequest(BaseModel):
    job_id: str

@app.api_route("/api/studio/modal/{endpoint_name}", methods=["GET", "POST", "OPTIONS"])
async def modal_proxy(endpoint_name: str, request: Request):
    from backend.cloud_tools.account_manager import AccountManager
    import random
    import httpx
    from fastapi.responses import StreamingResponse, Response
    import time

    am = AccountManager()
    accounts = am.get_all_accounts()
    valid_modal_accounts = [acc for acc in accounts if acc.get('provider') == 'modal' and acc.get('is_active', True) and acc.get('last_balance', 0.0) > 0.0 and acc.get('workspace')]

    print(f"[Modal Proxy] >>> Endpoint: {endpoint_name} | Método: {request.method}")
    print(f"[Modal Proxy] Contas modais válidas encontradas: {len(valid_modal_accounts)}")
    for acc in valid_modal_accounts:
        print(f"  - {acc.get('name')} (workspace={acc.get('workspace')}, balance=${acc.get('last_balance',0):.2f})")

    if not valid_modal_accounts:
        all_modal = [acc for acc in accounts if acc.get('provider') == 'modal']
        print(f"[Modal Proxy] CRITICO: Sem contas válidas! Contas modal total={len(all_modal)}")
        for acc in all_modal:
            print(f"  - {acc.get('name')}: is_active={acc.get('is_active')}, balance={acc.get('last_balance')}")
        return Response(status_code=503, content="CRÍTICO: Nenhuma conta Cloud Modal com saldo disponível.")

    random.shuffle(valid_modal_accounts)
    acc = valid_modal_accounts[0]
    workspace = acc.get('workspace')

    # Roteamento centralizado da aplicação ASGI Modal
    endpoint_path = endpoint_name.replace('_', '/')
    modal_url = f"https://{workspace}--apollo-render-router-apollo-api.modal.run/{endpoint_path}"
    print(f"[Modal Proxy] Selecionada: {acc.get('name')}")
    print(f"[Modal Proxy] URL Modal: {modal_url}")

    client = httpx.AsyncClient(timeout=1200.0)

    req_headers = {}
    if acc.get("proxy_key") and acc.get("proxy_secret"):
        req_headers["Modal-Key"] = acc.get("proxy_key")
        req_headers["Modal-Secret"] = acc.get("proxy_secret")

    if request.method == "GET":
        req = client.build_request("GET", modal_url, headers=req_headers if req_headers else None)
    elif request.method == "OPTIONS":
        return Response(status_code=200)
    else:
        body = await request.body()
        req_headers["Content-Type"] = "application/json"
        
        # INTERCEPTAÇÃO MULTI-PASS
        if endpoint_name == "generate_image":
            import json
            try:
                body_json = json.loads(body)
                ref_images = body_json.get("reference_images_base64", [])
                if ref_images and len(ref_images) >= 2 and body_json.get("model", "").lower() == "flux2-universal":
                    print(f"[Modal Proxy] Interceptado: {len(ref_images)} imagens de referência detectadas. Iniciando Multipass Workflow.")
                    from backend.api.ai_director_multipass import AIDirectorMultipass
                    import asyncio
                    
                    async def multipass_generator():
                        yield json.dumps({"status": "processing", "message": "Iniciando inteligência de direção de arte (LLM)..."}).encode('utf-8') + b"\n"
                        try:
                            import os
                            lightning_key = os.getenv("LIGHTNING_API_KEY", "")
                            base_modal_url = f"https://{workspace}--apollo-render-router-apollo-api.modal.run"
                            director = AIDirectorMultipass(api_key=lightning_key, modal_base_url=base_modal_url)
                            
                            global_prompt = body_json.get("prompt", "A cinematic scene")
                            characters = [{"name": f"Personagem {i+1}", "details": "Detalhes conforme a imagem fornecida"} for i in range(len(ref_images))]
                            
                            yield json.dumps({"status": "processing", "message": f"Planejando cenário base e {len(ref_images)} personagens com LLM..."}).encode('utf-8') + b"\n"
                            
                            # Precisamos rodar isso em um executor porque o Director é bloqueante (requests.post)
                            def run_sync_director():
                                # Passo 1: Planejamento
                                base_prompt, regional_prompts = director.break_down_prompt(global_prompt, characters)
                                # Passo 2: Geração Base
                                base_img_b64 = director.generate_base_image(base_prompt)
                                # Passo 3: Multipass (Iterativo)
                                workflow_path = os.path.join(os.path.dirname(__file__), "Comfyui Workflow API", "FLUX 2 DEV", "image_flux2", "10resultado_3_personagens_CHAINED_klein.json")
                                multipass_b64 = director.run_multipass(workflow_path, base_prompt, regional_prompts, base_img_b64, ref_images)
                                # Passo 4: Upscale Final
                                upscale_path = os.path.join(os.path.dirname(__file__), "Comfyui Workflow API", "WORKFLOW - INSANE UPSCALE", "WORKFLOW - INSANE UPSCALE.json")
                                
                                with open(upscale_path, "r", encoding="utf-8") as f:
                                    upscale_wf = json.load(f)
                                for node_id, node in upscale_wf.items():
                                    if node.get("class_type") == "UNETLoader" and "unet_name" in node.get("inputs", {}):
                                        node["inputs"]["unet_name"] = "flux1-dev-fp8.safetensors"
                                    if node.get("class_type") == "LoadImage":
                                        if "_meta" not in node:
                                            node["_meta"] = {}
                                        node["_meta"]["title"] = "APOLLO_BASE_IMAGE"
                                        
                                upscale_b64 = director.run_multipass(upscale_wf, "", [], multipass_b64, [])
                                return upscale_b64

                            loop = asyncio.get_event_loop()
                            final_b64 = await loop.run_in_executor(None, run_sync_director)
                            
                            yield json.dumps({"status": "success", "image_base64": final_b64}).encode('utf-8') + b"\n"
                            return
                        except Exception as e:
                            import traceback
                            trace = traceback.format_exc()
                            print(f"[Modal Proxy] Multi-Pass Erro:\n{trace}")
                            yield json.dumps({"status": "error", "message": f"Erro no Multipass: {str(e)}"}).encode('utf-8') + b"\n"
                            return
                    
                    return StreamingResponse(multipass_generator(), media_type="application/x-ndjson")
            except Exception as e:
                print(f"[Modal Proxy] Falha ao interceptar json para multipass: {e}")

        req = client.build_request("POST", modal_url, content=body, headers=req_headers)
        print(f"[Modal Proxy] Body size: {len(body)} bytes")

    t_start = time.time()

    async def stream_generator():
        response = None
        try:
            print(f"[Modal Proxy] Abrindo conexão com Modal...")
            response = await client.send(req, stream=True)
            elapsed_connect = time.time() - t_start
            print(f"[Modal Proxy] Conexão estabelecida em {elapsed_connect:.1f}s | HTTP {response.status_code}")
            if response.status_code != 200:
                body_err = await response.aread()
                print(f"[Modal Proxy] ERRO upstream: {body_err[:500]}")
                yield body_err
                return
            chunk_count = 0
            total_bytes = 0
            async for chunk in response.aiter_bytes():
                chunk_count += 1
                total_bytes += len(chunk)
                if chunk_count <= 3 or chunk_count % 20 == 0:
                    print(f"[Modal Proxy] Chunk #{chunk_count} | {len(chunk)}b | total={total_bytes}b")
                yield chunk
            print(f"[Modal Proxy] Stream finalizado. Total: {total_bytes} bytes em {chunk_count} chunks | {time.time()-t_start:.1f}s")
        except Exception as e:
            print(f"[Modal Proxy Error]: {type(e).__name__}: {e}")
            import json
            yield json.dumps({"status": "error", "message": f"Erro no proxy local: {str(e)}"}).encode('utf-8')
        finally:
            if response:
                await response.aclose()

    return StreamingResponse(stream_generator())



class GenerateSFXRequest(BaseModel):
    job_id: str

@app.post("/api/studio/generate")
async def studio_generate(req: StudioGenerateRequest, background_tasks: BackgroundTasks):
    check_feature('feature_image_gen')
    import urllib.parse
    import time
    import requests
    import os
    import uuid
    from backend.financial_agent import economy_db
    
    job_id = f"job_{uuid.uuid4().hex}"
    
    payload = {
        'type': req.type,
        'prompt': req.prompt,
        'image_base64': req.image_base64,
        'model': req.model,
        'preset': req.preset,
        'duration': req.duration,
        'steps': req.steps,
        'aspect_ratio': req.aspect_ratio,
        'seed': req.seed,
        'negative_prompt': req.negative_prompt,
        'motion_scale': req.motion_scale,
        'guidance_scale': req.guidance_scale
    }
    
    job_type = "video_generation" if req.type == "video" else "image_generation"
    cost = 50 if req.type == "video" else 10
    
    # Financial Check
    balance = economy_db.get_balance("default_user")
    if balance['coins'] < cost:
        return {"success": False, "error": f"Saldo Insuficiente. Requer {cost} Moedas."}
        
    # Deduct currency immediately to prevent spam
    economy_db.deduct_currency(cost, "coins", "default_user")
    
    # Cria o job na fila do BD SQLite
    economy_db.create_job(job_id, "default_user", job_type, payload)
    
    # Envia a tarefa pesada para o background (para não bloquear o request)
    background_tasks.add_task(worker_studio_generate, job_id, payload)
    
    return {"success": True, "job_id": job_id, "status": "QUEUED", "message": "Adicionado à fila de renderização."}

class EnhancePromptRequest(BaseModel):
    prompt: str
    type: str

@app.post("/api/studio/enhance_prompt")
async def enhance_prompt(req: EnhancePromptRequest):
    import os
    import json
    import requests
    base = req.prompt.strip()
    
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        system_prompt = "You are an expert prompt engineer for Midjourney and FLUX. Rewrite the user's idea into a highly detailed, professional, cinematic prompt in english. Output ONLY the new prompt, nothing else."
        if req.type == "video":
            system_prompt = "You are an expert prompt engineer for LTX Video AI. Rewrite the user's idea into a detailed, descriptive video generation prompt specifying camera movement, lighting, and cinematic framing in english. Output ONLY the prompt."
            
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": base}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 150
                },
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                enhanced = data["choices"][0]["message"]["content"].strip().replace('"', '')
                return {"success": True, "enhanced": enhanced}
        except Exception as e:
            print(f"Error enhancing prompt via Groq: {e}")
            
    # Fallback caso não tenha API
    if req.type == 'image':
        enhanced = f"{base}, cinematic masterpiece, 8k resolution, highly detailed, photorealistic, Unreal Engine 5 render, dramatic lighting, sharp focus, intricate details, trending on ArtStation"
    else:
        enhanced = f"A high-quality cinematic video of {base}. Shot on 35mm lens, dynamic motion, ultra-realistic, 8k resolution, volumetric lighting, smooth camera pan, masterpiece."
    
    return {"success": True, "enhanced": enhanced}

@app.post("/api/studio/enhance_video")
async def enhance_video_api(req: EnhanceVideoRequest, background_tasks: BackgroundTasks):
    import time
    from datetime import datetime
    import asyncio
    from backend.financial_agent import economy_db
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT type, result_url FROM jobs WHERE job_id=?", (req.job_id,))
    row = c.fetchone()
    conn.close()
    
    if not row or row[0] != 'video_generation' or not row[1]:
        return {"success": False, "error": "Vídeo original inválido ou inexistente."}
    
    new_job_id = f"job_upscale_{int(time.time())}"
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO jobs (job_id, type, status, progress, created_at) VALUES (?, ?, ?, ?, ?)",
              (new_job_id, 'video_upscale', 'PROCESSING', 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    async def worker_upscale(j_id, video_url):
        import subprocess
        import os
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE jobs SET progress=20 WHERE job_id=?", (j_id,))
        conn.commit()
        
        try:
            # We use FFmpeg to do a high quality bicubic/lanczos scale and unsharp mask
            os.makedirs("temp", exist_ok=True)
            out_path = f"temp/{j_id}.mp4"
            
            # Simple upscale filter
            cmd = [
                "ffmpeg", "-y", "-i", video_url,
                "-vf", "scale=-1:1080:flags=lanczos,unsharp=5:5:1.0:5:5:0.0",
                "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                "-c:a", "copy",
                out_path
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.wait()
            
            if process.returncode == 0:
                c.execute("UPDATE jobs SET status='COMPLETED', progress=100, result_url=? WHERE job_id=?", (out_path, j_id))
            else:
                c.execute("UPDATE jobs SET status='FAILED', progress=0 WHERE job_id=?", (j_id,))
        except Exception as e:
            print(f"Upscale Error: {e}")
            c.execute("UPDATE jobs SET status='FAILED', progress=0 WHERE job_id=?", (j_id,))
            
        conn.commit()
        conn.close()
        economy_db.add_unnotified_job(j_id)
        
    background_tasks.add_task(worker_upscale, new_job_id, row[1])
    return {"success": True, "new_job_id": new_job_id}

@app.post("/api/studio/generate_sfx")
async def generate_sfx_api(req: GenerateSFXRequest, background_tasks: BackgroundTasks):
    import time
    from datetime import datetime
    import asyncio
    from backend.financial_agent import economy_db
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT type, result_url, parameters FROM jobs WHERE job_id=?", (req.job_id,))
    row = c.fetchone()
    conn.close()
    
    if not row or row[0] != 'video_generation' or not row[1]:
        return {"success": False, "error": "Vídeo original inválido ou inexistente."}
        
    import json
    try:
        orig_params = json.loads(row[2])
        orig_prompt = orig_params.get('prompt', 'Cinematic action')
    except:
        orig_prompt = "Cinematic sound effect"
    
    new_job_id = f"job_sfx_{int(time.time())}"
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO jobs (job_id, type, status, progress, created_at) VALUES (?, ?, ?, ?, ?)",
              (new_job_id, 'audio_sfx', 'PROCESSING', 0, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    async def worker_sfx(j_id, prompt):
        import requests
        import base64
        import os
        from backend.cloud_tools.account_manager import get_active_account
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("UPDATE jobs SET progress=20 WHERE job_id=?", (j_id,))
        conn.commit()
        
        try:
            acc = get_active_account(needs_lightning=False)
            modal_url = acc['modal_url']
            payload = {
                "model": "stable_audio",
                "text": "Foley, high quality sound effect for: " + prompt
            }
            c.execute("UPDATE jobs SET progress=50 WHERE job_id=?", (j_id,))
            conn.commit()
            
            # Executa de forma síncrona dentro da task do FastAPI
            res = requests.post(modal_url, json=payload, timeout=600)
            if res.status_code == 200:
                data = res.json()
                aud_b64 = data.get("audio_base64")
                if aud_b64:
                    aud_data = base64.b64decode(aud_b64)
                    os.makedirs("temp", exist_ok=True)
                    aud_path = f"temp/{j_id}.wav"
                    with open(aud_path, "wb") as f:
                        f.write(aud_data)
                    c.execute("UPDATE jobs SET status='COMPLETED', progress=100, result_url=? WHERE job_id=?", (aud_path, j_id))
                else:
                    c.execute("UPDATE jobs SET status='FAILED', progress=0 WHERE job_id=?", (j_id,))
            else:
                c.execute("UPDATE jobs SET status='FAILED', progress=0 WHERE job_id=?", (j_id,))
                
        except Exception as e:
            print(f"SFX Error: {e}")
            c.execute("UPDATE jobs SET status='FAILED', progress=0 WHERE job_id=?", (j_id,))
            
        conn.commit()
        conn.close()
        economy_db.add_unnotified_job(j_id)
        
    background_tasks.add_task(worker_sfx, new_job_id, orig_prompt)
    return {"success": True, "new_job_id": new_job_id}

@app.get("/api/public/explore")
async def public_explore():
    # Retorna os últimos 50 jobs completos (simulando um feed público)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT job_id, type, parameters, status, progress, result_url, created_at FROM jobs WHERE status='COMPLETED' ORDER BY created_at DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({
            "job_id": r[0],
            "type": r[1],
            "parameters": json.loads(r[2]) if r[2] else {},
            "status": r[3],
            "progress": r[4],
            "result_url": r[5],
            "created_at": r[6]
        })
    return {"success": True, "feed": history}

class StartCopilotRequest(BaseModel):
    name: str
    model: str
    system_prompt: str
    topic: str

# Armazena os agentes ativos na memoria do servidor para polling simples (MVP Fase 13)
active_copilots = {}

@app.post("/api/agency/start_copilot")
async def start_copilot_api(req: StartCopilotRequest, background_tasks: BackgroundTasks):
    from backend.agents.copilot_swarm import CopilotAgent
    agent = CopilotAgent(name=req.name, system_prompt=req.system_prompt)
    active_copilots[agent.mission_id] = agent
    
    # Executa a missao principal em background para nao travar o uvicorn
    background_tasks.add_task(agent.run_mission, req.topic)
    
    return {"success": True, "mission_id": agent.mission_id, "message": f"Copiloto {req.name} iniciado."}

@app.get("/api/agency/mission/{mission_id}/logs")
async def get_mission_logs(mission_id: str):
    agent = active_copilots.get(mission_id)
    if not agent:
        return {"success": False, "error": "Mission not found"}
    return {"success": True, "status": agent.status, "logs": agent.logs}

class NotificationMarkRequest(BaseModel):
    job_ids: list[str]

@app.get("/api/notifications")
async def get_notifications():
    from backend.financial_agent import economy_db
    jobs = economy_db.get_unnotified_jobs("default_user")
    return {"success": True, "notifications": jobs}

@app.post("/api/notifications/mark_read")
async def mark_notifications_read(req: NotificationMarkRequest):
    from backend.financial_agent import economy_db
    economy_db.mark_jobs_notified(req.job_ids)
    return {"success": True}

@app.get("/api/studio/history")
async def get_studio_history():
    from backend.financial_agent import economy_db
    jobs = economy_db.get_user_jobs("default_user", 50)
    return {"success": True, "history": jobs}

@app.websocket("/ws/jobs/{job_id}")
async def websocket_job_status(websocket: WebSocket, job_id: str):
    await job_notifier.connect(websocket, job_id)
    try:
        from backend.financial_agent import economy_db
        import asyncio
        # Send initial status
        job_data = economy_db.get_job(job_id)
        if job_data:
            await websocket.send_json({"status": job_data["status"], "progress": job_data["progress"], "result_url": job_data["result_url"]})
        while True:
            # Keeps the connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        job_notifier.disconnect(websocket, job_id)
    except Exception as e:
        job_notifier.disconnect(websocket, job_id)

def worker_studio_generate(job_id: str, payload: dict):
    import requests
    import os
    import uuid
    import json
    import base64
    from backend.cloud_tools.account_manager import AccountManager
    from backend.financial_agent import economy_db
    
    am = AccountManager()
    accounts = am.get_all_accounts()
    valid_modal_accounts = [acc for acc in accounts if acc.get('provider') == 'modal' and acc.get('is_active', True) and acc.get('last_balance', 0.0) > 0.0 and acc.get('workspace')]
    
    if not valid_modal_accounts:
        economy_db.update_job_status(job_id, 'FAILED', result_url="CRÍTICO: Nenhuma conta Cloud Modal disponível.")
        return
        
    import random
    random.shuffle(valid_modal_accounts)
    
    last_error = "Desconhecido"
    
    # Atualiza status para PROCESSING
    economy_db.update_job_status(job_id, 'PROCESSING', progress=5)
        
    for acc in valid_modal_accounts:
        workspace = acc.get('workspace')
        
        if payload.get("type") == "image":
            url_modal = f"https://{workspace}--apollo-render-router-apollo-api.modal.run/generate/image"
        else:
            url_modal = f"https://{workspace}--apollo-render-router-apollo-api.modal.run/generate/video"
            
        print(f"[Gateway Job {job_id}] Roteando renderização para Modal Workspace: {workspace}")
        
        try:
            r = requests.post(url_modal, json=payload, stream=True, timeout=200)
            if r.status_code == 200:
                # Fix for temp_files_dir scope
                temp_files_dir = os.path.join(CURRENT_WORKSPACE_PATH, "temp")
                if not os.path.exists(temp_files_dir):
                    os.makedirs(temp_files_dir)
                    
                video_saved = False
                
                for line in r.iter_lines():
                    if line:
                        try:
                            decoded_line = line.decode('utf-8').strip()
                            if not decoded_line:
                                continue
                            data = json.loads(decoded_line)
                            
                            if 'video_base64' in data or 'image_base64' in data:
                                b64 = data.get('video_base64') or data.get('image_base64')
                                ext = 'mp4' if 'video_base64' in data else 'png'
                                filename = f"modal_render_{uuid.uuid4().hex[:8]}.{ext}"
                                save_path = os.path.join(temp_files_dir, filename)
                                
                                with open(save_path, 'wb') as f:
                                    f.write(base64.b64decode(b64))
                                video_saved = True
                                
                                # Notifica WebSockets globais que o trabalho concluiu
                                economy_db.update_job_status(job_id, 'COMPLETED', progress=100, result_url=f"/temp/{filename}")
                                import asyncio
                                if 'job_notifier' in globals():
                                    asyncio.run(globals()['job_notifier'].broadcast(job_id, {"status": "COMPLETED", "progress": 100, "result_url": f"/temp/{filename}"}))
                                return
                            elif data.get('status') == 'progress':
                                # Real-time WebSocket ping
                                curr_progress = data.get('progress', 10)
                                economy_db.update_job_status(job_id, 'PROCESSING', progress=curr_progress)
                                import asyncio
                                if 'job_notifier' in globals():
                                    asyncio.run(globals()['job_notifier'].broadcast(job_id, {"status": "PROCESSING", "progress": curr_progress}))
                            elif data.get('status') == 'error':
                                # Erro interno
                                economy_db.update_job_status(job_id, 'FAILED', result_url=data.get('message', 'Erro Cloud Modal'))
                                import asyncio
                                if 'job_notifier' in globals():
                                    asyncio.run(globals()['job_notifier'].broadcast(job_id, {"status": "FAILED", "error": data.get('message', 'Erro Cloud Modal')}))
                                return
                        except Exception:
                            pass
                            
                if video_saved:
                    return
                else:
                    last_error = f"Resposta do Workspace {workspace} vazia."
                    continue 
                    
            elif r.status_code in [402, 403, 401]:
                print(f"[Gateway Job {job_id}] Workspace {workspace} falhou com código {r.status_code}. Zerando saldo...")
                am.mark_exhausted(workspace)
                last_error = f"Conta {workspace} rejeitou (HTTP {r.status_code})."
                continue
            else:
                last_error = f"HTTP {r.status_code} - {r.text}"
                continue
        except requests.exceptions.Timeout:
            last_error = "Timeout na requisição."
        except Exception as e:
            last_error = str(e)
            
    # Se chegou aqui, todas falharam
    economy_db.update_job_status(job_id, 'FAILED', result_url=f"Falha em todas as contas. Último erro: {last_error}")
    import asyncio
    if 'job_notifier' in globals():
        asyncio.run(globals()['job_notifier'].broadcast(job_id, {"status": "FAILED", "error": f"Falha. {last_error}"}))

from chat_ai_manager import ChatAIManager
from config_manager import ConfigManager
from pydantic import BaseModel

class ChatRequest(BaseModel):
    channel_id: str
    message: str

# Montar diretórios externos para apps estáticos
app.mount("/ext_apps", StaticFiles(directory=os.path.join(BASE_DIR, "Programas externos")), name="programas_externos")

# Todo o conteÃºdo de web_ui serÃ¡ servido estaticamente (Deve ser a ÃšLTIMA rota)
app.mount("/", StaticFiles(directory=WEB_UI_DIR), name="static")

def start_server(workspace_name, workspace_path, port=8080):
    """FunÃ§Ã£o chamada pelo apollo_studio.py para rodar o uvicorn."""
    global CURRENT_WORKSPACE, CURRENT_WORKSPACE_PATH
    CURRENT_WORKSPACE = workspace_name
    CURRENT_WORKSPACE_PATH = workspace_path
    
    import uvicorn
    # log_level = "warning" evita spamar o terminal
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace_name', type=str, default="ADM APOLLO EDIT WEB")
    parser.add_argument('--workspace_path', type=str, default=os.path.join(BASE_DIR, "Workspaces", "ADM APOLLO EDIT WEB"))
    args, _ = parser.parse_known_args()
    
    start_server(args.workspace_name, args.workspace_path)
