from typing import Optional, Tuple
import logging, uuid, time, json

from starlette.middleware.base import BaseHTTPMiddleware, _StreamingResponse
from fastapi import Request

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Auth Middleware
        """
        request_id = (
            str(uuid.uuid1())
            if not request.headers.get("x-request-id")
            else request.headers.get("x-request-id")
        )

        request.state.id = request_id
        request.state.tic = time.time()

        response: _StreamingResponse = await call_next(request)

        return response
