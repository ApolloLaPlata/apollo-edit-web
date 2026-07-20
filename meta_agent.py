import sqlite3
import user_database

def get_cheapest_model(tier="Free"):
    """
    Retorna o model_id do modelo mais barato ativo da tier especificada.
    Leva em conta o preço de input + output somados como heurística.
    """
    conn = user_database.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT model_id, provider, (input_price_per_1m + output_price_per_1m) as total_cost 
        FROM models_pricing 
        WHERE status = 'Ativo' AND tier = ?
        ORDER BY total_cost ASC
    ''', (tier,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def optimize_orchestrator_nodes():
    """
    Varre os nós do orquestrador marcados como 'is_dynamic' = 1,
    e atualiza o 'default_model_id' para o modelo mais barato da tier correspondente.
    Por padrão, assumimos que nós dinâmicos procuram o melhor modelo 'Free' para economizar,
    a menos que a role_name especifique premium.
    """
    conn = user_database.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM agent_orchestrator_nodes WHERE is_dynamic = 1")
    dynamic_nodes = cursor.fetchall()
    
    cheapest_free = get_cheapest_model("Free")
    cheapest_premium = get_cheapest_model("Premium")
    
    for node in dynamic_nodes:
        # Heurística: Se a role tem 'Crítico' ou 'Premium' no nome, usa Premium. Senão Free.
        # Ou você pode adicionar uma coluna 'target_tier' no futuro.
        target = cheapest_free
        if 'Crítico' in node['role_name'] or 'Premium' in node['role_name']:
            target = cheapest_premium or cheapest_free
            
        if target and node['default_model_id'] != target['model_id']:
            cursor.execute(
                "UPDATE agent_orchestrator_nodes SET default_model_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (target['model_id'], node['id'])
            )
            print(f"Meta-Agente otimizou Node '{node['role_name']}' para usar '{target['model_id']}'")
            
    conn.commit()
    conn.close()

def get_pipeline_execution_plan():
    """
    Retorna a pipeline ordenada com os modelos já resolvidos.
    """
    conn = user_database.get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_orchestrator_nodes ORDER BY step_order ASC")
    nodes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return nodes
