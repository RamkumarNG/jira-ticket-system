from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.schema.v1.common import ResponseStructure


class CommentBase(BaseModel):
    content: str


class CommentCreateRequest(CommentBase):
    created_by: str

class CommentUpdateRequest(CommentBase):
    pass  # You can extend this if needed later


class Comment(BaseModel):
    comment_id: UUID
    content: str
    ticket_id: UUID
    created_by: UUID
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class CommentGetResponse(ResponseStructure):
    comment_id: UUID
    content: str
    created_by: str
    created_at: Optional[datetime]

class CommentSerializer(BaseModel):
    comment_id: UUID
    content: str
    created_by: str
    created_at: Optional[datetime]


class CreateCommentResponse(ResponseStructure):
    data: CommentSerializer


class ListCommentResponse(ResponseStructure):
    data: List[CommentSerializer]
