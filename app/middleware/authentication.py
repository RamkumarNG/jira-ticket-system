from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
class AuthenticationMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request:Request, call_next):

        # Skip authentication for docs and openapi
        if request.url.path in ["/docs", "/openapi.json", "/health_ping", "/ping"]:
            response = await call_next(request)
            return response
        
        api_key = request.headers.get("x-api-key")
        
        if api_key != settings.ADMIN_API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized: Invalid or missing API key"}
            )
        
        response = await call_next(request)
        return response

