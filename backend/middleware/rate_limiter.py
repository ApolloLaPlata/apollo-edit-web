import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger("RateLimiter")

ip_requests = {}
RATE_LIMIT = 300 # Aumentado para 300 para no bloquear o Vercel
TIME_WINDOW = 60 # Em segundos (1 minuto)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Tenta pegar o IP real (via Vercel/Nginx)
        client_ip = request.headers.get("x-forwarded-for")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host
            
        if request.url.path.startswith("/api/ws") or request.url.path.startswith("/api/studio/modal/"):
            # Ignora rate limit para WebSockets e rotas do proxy do Modal (que j so seguras via x-apollo-lock)
            return await call_next(request)

        current_time = time.time()
        
        if client_ip in ip_requests:
            ip_requests[client_ip] = [t for t in ip_requests[client_ip] if current_time - t < TIME_WINDOW]
        else:
            ip_requests[client_ip] = []
            
        if len(ip_requests[client_ip]) >= RATE_LIMIT:
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down. (Rate Limit Exceeded)", "ip": client_ip}
            )
            
        ip_requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
