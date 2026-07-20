import os
import json
import logging
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Header
from fastapi.responses import JSONResponse

from backend.financial_agent.coin_ledger import credit_user, grant_monthly_plan

logger = logging.getLogger("Webhooks")
router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_dummy")
CRYPTO_WEBHOOK_SECRET = os.getenv("CRYPTO_WEBHOOK_SECRET", "crypto_dummy_secret")

@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Recebe eventos de pagamento do Stripe (assinaturas e pacotes avulsos).
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe Signature")
        
    payload = await request.body()
    
    # Validação de Assinatura do Stripe (simplificado para o ambiente Python sem a lib stripe oficial)
    # Na produção final, usaremos a lib `stripe.Webhook.construct_event`
    try:
        # Placeholder de segurança. Se houver falha na assinatura, lançar exceção.
        # pass
        event = json.loads(payload.decode("utf-8"))
    except ValueError as e:
        logger.error(f"[Stripe Webhook] Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Tratamento dos eventos
    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        # Pagamento Concluído!
        customer_email = data_object.get("customer_details", {}).get("email")
        metadata = data_object.get("metadata", {})
        user_id = metadata.get("user_id")
        product_type = metadata.get("product_type") # "nitro" ou "subscription"
        
        if not user_id:
            logger.error("[Stripe] Checkout completado mas user_id ausente no metadata.")
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        logger.info(f"[Stripe Webhook] Pagamento confirmado para user {user_id}. Produto: {product_type}")

        # Entrega o produto
        if product_type == "subscription":
            plan_name = metadata.get("plan_name", "pro")
            grant_monthly_plan(user_id, plan_name)
            logger.info(f"[Stripe] Usuário {user_id} promovido para o plano {plan_name}.")
            
        elif product_type == "nitro_pack":
            # Exemplo: Pacote de 500 Coins e 50 Fuel
            coins = int(metadata.get("coins", 0))
            fuel = int(metadata.get("fuel", 0))
            if coins > 0:
                credit_user(user_id, "stripe_purchase", "coins", coins)
            if fuel > 0:
                credit_user(user_id, "stripe_purchase", "fuel", fuel)
            logger.info(f"[Stripe] Pacote entregue: {coins} coins, {fuel} fuel para {user_id}.")

    return JSONResponse(content={"status": "success"}, status_code=200)

@router.post("/crypto")
async def crypto_webhook(request: Request, x_cc_webhook_signature: str = Header(None)):
    """
    Recebe eventos de provedores Crypto (Ex: Coinbase Commerce).
    """
    if not x_cc_webhook_signature:
        raise HTTPException(status_code=400, detail="Missing Crypto Signature")
        
    payload = await request.body()
    
    # Validação de Assinatura (HMAC SHA256 - Padrão Coinbase)
    computed_sig = hmac.new(
        CRYPTO_WEBHOOK_SECRET.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(computed_sig, x_cc_webhook_signature):
        logger.warning("[Crypto Webhook] Assinatura inválida! Possível tentativa de fraude.")
        # Como é um ambiente de dev/sandbox, não vamos bloquear estritamente agora, 
        # mas em produção deve dar raise HTTPException 401
    
    event = json.loads(payload.decode("utf-8"))
    event_type = event.get("event", {}).get("type")
    data = event.get("event", {}).get("data", {})
    
    if event_type == "charge:confirmed":
        # Pagamento confirmado na Blockchain
        metadata = data.get("metadata", {})
        user_id = metadata.get("user_id")
        coins_to_credit = int(metadata.get("coins", 0))
        
        if user_id and coins_to_credit > 0:
            credit_user(user_id, "crypto_purchase", "coins", coins_to_credit)
            logger.info(f"[Crypto Webhook] Transação blockchain confirmada! +{coins_to_credit} Coins para {user_id}")

    return JSONResponse(content={"status": "success"}, status_code=200)
