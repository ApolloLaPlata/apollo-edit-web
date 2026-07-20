"""
routes_auth.py - Autenticação JWT e OAuth2
===========================================
Expõe rotas de login clássico, registro e Google OAuth2.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import jwt
import datetime
import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from backend.financial_agent.coin_ledger import get_user_by_email, create_user_record
from backend.middleware.i18n import get_locale_from_request, t
from backend.services.email_service import send_email_async, get_welcome_template

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Segredos
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-apollo-dev-123")
JWT_ALGORITHM = "HS256"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "dummy_google_client_id.apps.googleusercontent.com")

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str  # Token emitido pelo frontend Google Sign-In

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

@router.post("/register")
async def register(req: RegisterRequest, request: Request):
    locale = get_locale_from_request(request)
    user = get_user_by_email(req.email)
    
    if user:
        raise HTTPException(status_code=400, detail=t("auth.email_registered", locale))
    
    user_id = str(uuid.uuid4())
    hashed_pwd = get_password_hash(req.password)
    create_user_record(user_id, req.email, hashed_pwd)
    
    # Dispara E-mail de Boas-Vindas Assíncrono
    html_body = get_welcome_template(req.email.split('@')[0])
    await send_email_async(req.email, t("emails.welcome_subject", locale), html_body)
    
    return {"status": "success", "message": t("auth.user_created", locale), "user_id": user_id}

@router.post("/login")
async def login(req: LoginRequest, request: Request):
    locale = get_locale_from_request(request)
    user = get_user_by_email(req.email)
    
    if not user or not verify_password(req.password, user['password_hash']):
        raise HTTPException(status_code=401, detail=t("auth.invalid_credentials", locale))
    
    token_data = {"sub": user['user_id'], "email": user['email']}
    token = create_access_token(token_data)
    
    return {
        "status": "success",
        "access_token": token,
        "token_type": "bearer",
        "user_id": user['user_id']
    }

@router.post("/google")
async def google_login(req: GoogleLoginRequest, request: Request):
    locale = get_locale_from_request(request)
    try:
        # Verifica token do Google
        idinfo = id_token.verify_oauth2_token(req.credential, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email']
        
        user = get_user_by_email(email)
        if not user:
            # Cadastra novo usuário Google se não existir (senha vazia/nula)
            user_id = str(uuid.uuid4())
            create_user_record(user_id, email, "google_oauth_no_pwd")
            user = {'user_id': user_id, 'email': email}
            
            # Dispara E-mail de Boas-Vindas Assíncrono
            html_body = get_welcome_template(idinfo.get('given_name', email.split('@')[0]))
            await send_email_async(email, t("emails.welcome_subject", locale), html_body)
            
        token_data = {"sub": user['user_id'], "email": user['email']}
        token = create_access_token(token_data)
        
        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user_id": user['user_id']
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Google Token Inválido.")

