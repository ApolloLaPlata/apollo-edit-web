"""
routes_economy.py — Rotas da Economia e Mercado Negro
=====================================================
Expõe a carteira do usuário, histórico e sistema de venda
(Mercado Negro) para o Frontend.
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
import logging

from backend.financial_agent.coin_ledger import get_wallet, get_transaction_history, charge_operation, credit_user, get_db_connection
from backend.middleware.auth_guard import get_current_user

logger = logging.getLogger("EconomyRoutes")
router = APIRouter(prefix="/api/economy", tags=["Economy"])

class SellRequest(BaseModel):
    item_type: str  # ex: 'nitro', 'chips_llm'
    amount: int

@router.get("/wallet")
async def fetch_wallet(current_user: dict = Depends(get_current_user)):
    """Retorna o saldo completo da carteira e o plano."""
    user_id = current_user["user_id"]
    wallet = get_wallet(user_id)
    if not wallet:
        return {"user_id": user_id, "coins": 0, "chips_llm": 0, "gpu_tokens": 0, "fuel": 0, "crystals": 0, "plan": "free"}
    return wallet

@router.get("/history")
async def fetch_history(limit: int = 20, current_user: dict = Depends(get_current_user)):
    """Retorna o extrato da conta (histórico de transações)."""
    user_id = current_user["user_id"]
    return {"history": get_transaction_history(user_id, limit)}

@router.post("/sell")
async def black_market_sell(req: SellRequest, current_user: dict = Depends(get_current_user)):
    """
    Mercado Negro: Permite vender moedas ou itens premium
    de volta para o sistema por Apollo Coins (taxa com deságio).
    """
    user_id = current_user["user_id"]
    wallet = get_wallet(user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Carteira não encontrada.")
        
    current_amount = wallet.get(req.item_type, 0)
    if current_amount < req.amount:
        raise HTTPException(status_code=400, detail=f"Saldo insuficiente de {req.item_type}.")
        
    # Taxas de Conversão do Mercado Negro
    conversion_rates = {
        "chips_llm": 2,    # 1 Chip = 2 Coins
        "gpu_tokens": 5,   # 1 Token GPU = 5 Coins
        "fuel": 1,         # 1 Combustível = 1 Coin
        "crystals": 10     # 1 Cristal = 10 Coins
    }
    
    if req.item_type not in conversion_rates:
        raise HTTPException(status_code=400, detail="Item não negociável no Mercado Negro.")
        
    earned_coins = req.amount * conversion_rates[req.item_type]

    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Usa whitelist ou verificação do req.item_type pra evitar injetar nome da coluna dinâmico
        safe_col = req.item_type if req.item_type in conversion_rates else None
        if not safe_col:
            raise HTTPException(status_code=400, detail="Item invalido")

        # 1. Debita o recurso vendido
        c.execute(f"UPDATE users SET {safe_col} = {safe_col} - ? WHERE user_id = ?", (req.amount, user_id))
        c.execute("INSERT INTO transactions (user_id, operation, currency, amount, direction) VALUES (?, ?, ?, ?, 'debit')",
                  (user_id, f"sold_in_black_market", safe_col, req.amount))
                  
        # 2. Credita as Apollo Coins
        c.execute(f"UPDATE users SET coins = coins + ? WHERE user_id = ?", (earned_coins, user_id))
        c.execute("INSERT INTO transactions (user_id, operation, currency, amount, direction) VALUES (?, ?, ?, ?, 'credit')",
                  (user_id, f"black_market_payout", "coins", earned_coins))
                  
        conn.commit()
    
    logger.info(f"[Mercado Negro] 🕵️ Usuário {user_id} vendeu {req.amount} {safe_col} por {earned_coins} Coins.")
    
    return {
        "status": "success",
        "message": f"Venda realizada com sucesso! Você ganhou {earned_coins} Apollo Coins.",
        "earned_coins": earned_coins,
        "wallet": get_wallet(user_id)
    }

@router.post("/charge")
async def execute_charge(operation: str = Body(...), metadata: dict = Body(None), current_user: dict = Depends(get_current_user)):
    """Rota interna/frontend para realizar uma cobrança."""
    user_id = current_user["user_id"]
    result = charge_operation(user_id, operation, metadata)
    if not result["success"]:
        raise HTTPException(status_code=402, detail=result)
    return result
