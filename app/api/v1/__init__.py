from fastapi import APIRouter

from app.api.v1 import ticket_views, user_views

api_router = APIRouter()
api_router.include_router(ticket_views.router, prefix="/v1/tickets", tags=["tickets"])
api_router.include_router(user_views.router, prefix="/v1/users", tags=["users"])
