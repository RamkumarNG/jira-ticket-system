import uuid
import enum
from datetime import datetime


from sqlalchemy.orm import registry
from sqlalchemy import Column, String, ForeignKey, Enum, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncEngine
from dataclasses import dataclass

mapper_registry = registry()

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

@mapper_registry.mapped
@dataclass
class UserTable:
    __tablename__ = "users"

    user_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: str = Column(String, unique=True, nullable=False, index=True)
    status: UserStatus = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    api_key: uuid.UUID = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    email: str = Column(String, unique=True, nullable=False, index=True)

    tickets_created = relationship("TicketTable", back_populates="created_by_user")


@mapper_registry.mapped
@dataclass
class ProjectTable:
    __tablename__ = "projects"

    project_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String, nullable=False, unique=True)

    tickets = relationship("TicketTable", back_populates="project")

@mapper_registry.mapped
@dataclass
class TicketTable:
    __tablename__ = "tickets"

    ticket_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: str = Column(String, nullable=False)
    description: str = Column(Text)
    status: TicketStatus = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    project_id: str = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    project = relationship("ProjectTable", back_populates="tickets")

    created_by: str = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    created_by_user = relationship("UserTable", back_populates="tickets_created")

