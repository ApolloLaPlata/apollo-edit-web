import os
import jwt
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-apollo-dev-123")
JWT_ALGORITHM = "HS256"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Dependência do FastAPI para verificar o JWT Token.
    Se o token for válido, retorna os dados do usuário.
    Se não for, levanta erro 401 Unauthorized.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido: Sem User ID")
        return {"user_id": user_id, "email": email}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado. Faça login novamente.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido ou forjado.")

async def get_optional_user(request: Request) -> Dict[str, Any]:
    """
    Verifica se o usuário enviou token, mas não bloqueia se não enviar.
    Útil para rotas públicas que agem diferente se o usuário estiver logado.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"user_id": payload.get("sub"), "email": payload.get("email")}
    except Exception:
        return None
