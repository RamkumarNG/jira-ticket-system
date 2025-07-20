from datetime import datetime
from typing import List, Optional
from uuid import UUID
from enum import Enum

from pydantic import BaseModel

from app.schema.v1.common import ResponseStructure
from app.schema.v1.ticket import Ticket
from app.schema.v1.comment import Comment

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    username: Optional[str]
    email: Optional[str]
    status: Optional[UserStatus]

    class Config:
        orm_mode = True  # To support updates with SQLAlchemy models

class User(BaseModel):
    user_id: UUID
    username: str
    email: str
    status: Optional[UserStatus] = UserStatus.ACTIVE
    created_at: Optional[datetime]

    tickets_created: Optional[List[Ticket]] = []
    tickets_assigned: Optional[List[Ticket]] = []
    # comments: Optional[List[Comment]] = []

class CreateUserResponse(ResponseStructure):
    data: User

class UserGetResponse(ResponseStructure):
    data: User

class ListUserResponse(ResponseStructure):
    data: List[User]
