import uuid
import enum
from datetime import datetime


from sqlalchemy.orm import registry
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text, DateTime
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

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@mapper_registry.mapped
@dataclass
class UserTable:
    __tablename__ = "users"

    user_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: str = Column(String, unique=True, nullable=False, index=True)
    status: UserStatus = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    api_key: uuid.UUID = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    email: str = Column(String, unique=True, nullable=False, index=True)

    tickets_created = relationship("TicketTable", back_populates="created_by_user", foreign_keys="TicketTable.created_by")
    tickets_assigned = relationship("TicketTable", back_populates="assignee_user", foreign_keys="TicketTable.assignee_id")
    comments = relationship("CommentTable", back_populates="user")


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
    priority: TicketPriority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    story_points: int = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    project_id: UUID = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    created_by: UUID = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    assignee_id: UUID = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)

    # Relationships
    project = relationship("ProjectTable", back_populates="tickets")
    created_by_user = relationship("UserTable", back_populates="tickets_created", foreign_keys=[created_by])
    assignee_user = relationship("UserTable", back_populates="tickets_assigned", foreign_keys=[assignee_id])
    comments = relationship("CommentTable", back_populates="ticket", cascade="all, delete-orphan")

@mapper_registry.mapped
@dataclass
class CommentTable:
    __tablename__ = "comments"

    comment_id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    ticket_id: UUID = Column(UUID(as_uuid=True), ForeignKey("tickets.ticket_id"))
    user_id: UUID = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    ticket = relationship("TicketTable", back_populates="comments")
    user = relationship("UserTable", back_populates="comments")
