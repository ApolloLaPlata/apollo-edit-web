"""
routes_payments.py - Módulo de Pagamentos (Stripe)
=================================================
Geração de sessões de checkout e Webhooks para creditar
moedas aos usuários de forma autônoma.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import stripe
import os
import logging
from backend.financial_agent.coin_ledger import credit_user

logger = logging.getLogger("StripePayments")
router = APIRouter(prefix="/api/payments", tags=["Payments"])

# Chaves da Stripe (No futuro, pegar do .env real do cliente)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_dummy")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_dummy")

class CheckoutRequest(BaseModel):
    user_id: str
    package_id: str  # ex: 'coins_1000', 'nitro_100'

# Preços base (Poderiam vir de um DB, mas vamos usar hardcoded para simplificar)
PACKAGES = {
    "coins_1000": {"name": "1.000 Apollo Coins", "price_brl": 1000, "coins": 1000},
    "coins_5000": {"name": "5.000 Apollo Coins", "price_brl": 4000, "coins": 5000},
    "nitro_100":  {"name": "100 GPU Tokens", "price_brl": 2000, "gpu_tokens": 100},
}

@router.post("/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest):
    if req.package_id not in PACKAGES:
        raise HTTPException(status_code=400, detail="Pacote inválido.")
    
    pkg = PACKAGES[req.package_id]
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': pkg['name'],
                    },
                    'unit_amount': pkg['price_brl'], # Centavos (1000 = R$ 10,00)
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url="http://localhost:8000/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8000/cancel",
            metadata={
                "user_id": req.user_id,
                "package_id": req.package_id
            }
        )
        return {"status": "success", "url": session.url}
    except Exception as e:
        logger.error(f"Erro ao criar checkout Stripe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# --- INTEGRAÇÃO CRIPTO (Descentralizada) ---

class CryptoCheckoutRequest(BaseModel):
    user_id: str
    package_id: str  # ex: 'coins_1000'

@router.post("/crypto/create-invoice")
async def create_crypto_invoice(req: CryptoCheckoutRequest):
    """
    Simula a criação de uma fatura de pagamento via Cripto (ex: BTCPay Server ou Binance Pay).
    """
    if req.package_id not in PACKAGES:
        raise HTTPException(status_code=400, detail="Pacote inválido.")
    
    pkg = PACKAGES[req.package_id]
    
    # Simulação: no futuro isso chamará a API do BTCPay Server ou similar
    # e retornará um link de pagamento (QR Code) para o cliente.
    invoice_id = f"CRYPTO_INV_{req.user_id}_{req.package_id}_{os.urandom(4).hex()}"
    
    logger.info(f"Gerando Fatura Cripto {invoice_id} para o usuário {req.user_id}")
    
    return {
        "status": "success",
        "invoice_id": invoice_id,
        "payment_url": f"https://mock-crypto-gateway.apollo.com/pay/{invoice_id}",
        "amount_usd": pkg['price_brl'] / 500.0, # Conversão bruta simulada
        "currency": "USDT"
    }


