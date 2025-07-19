from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

ADMIN_API_KEY = "123456789"

class AuthenticationMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request:Request, call_next):
        api_key = request.headers.get("x-api-key")

        if api_key != ADMIN_API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized: Invalid or missing API key"}
            )
        
        response = await call_next(request)
        return response


    
    