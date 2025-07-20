from fastapi import APIRouter

from app.api.v1 import ticket_views, user_views, comment_views

api_router = APIRouter()
api_router.include_router(ticket_views.router, prefix="/v1/tickets", tags=["tickets"])
api_router.include_router(user_views.router, prefix="/v1/users", tags=["users"])
api_router.include_router(comment_views.router, prefix="/v1/tickets/{ticket_id}/comments", tags=["comments"])
