from datetime import datetime
from typing import List, Optional, Union, Tuple, Dict
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field

from app.schema.v1.common import ResponseStructure

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class TicketCreateRequest(BaseModel):
    title: str
    description: Optional[str] = Field("", description="Description of the ticket")
    status: Optional[TicketStatus] = TicketStatus.OPEN
    project_name: str
    created_by: str

class Ticket(BaseModel):
    ticket_id: UUID
    title: str
    description: Optional[str]
    status: Optional[TicketStatus]
    project_id: str
    created_by: str

class CreateTicket(BaseModel):
    ticket_id: UUID
    title: str
    description: Optional[str]
    status: Optional[TicketStatus]
    project_name: str
    created_by: str
    created_at: datetime

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None

class CreateTicketResponse(ResponseStructure):
    data: CreateTicket

class TicketGetResponse(ResponseStructure):
    data: CreateTicket

class ListTicketResponse(ResponseStructure):
    data: List[CreateTicket]