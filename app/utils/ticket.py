import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.database.models import TicketTable, ProjectTable, TicketStatus

async def _create_ticket(title: str, description: str, project_id: str, user_id: str, db: AsyncSession, status: str='',):
    new_ticket = TicketTable(
        ticket_id=uuid.uuid4(),
        title=title,
        description=description,
        status=status,
        project_id=str(project_id),
        created_by=str(user_id),
        created_at=datetime.utcnow()
    )

    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    return new_ticket

async def _get_ticket_by_id(ticket_id: uuid.UUID, db: AsyncSession):

    ticket_db_entry = await db.execute(
        select(
            TicketTable
        )
        .options(
            joinedload(TicketTable.project),
            joinedload(TicketTable.created_by_user)
        )
        .where(
            TicketTable.ticket_id == ticket_id
        )
    )
    ticket = ticket_db_entry.scalar_one_or_none()

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    
    return ticket

async def _get_tickets(
        db: AsyncSession,
        project_name: Optional[str] = None,
        user_name: Optional[str] = None,
        ticket_title: Optional[str] = None,
        page: int = 1,
        size: int = 10,
):

    stmt = select(
        TicketTable
    ).options(
        joinedload(TicketTable.project),
        joinedload(TicketTable.created_by_user)
    )

    if project_name:
        stmt = stmt.join(
            TicketTable.project
        ).where(
            ProjectTable.name.ilike(f"%{project_name}%")
        )
    
    if ticket_title:
        stmt = stmt.where(TicketTable.title == ticket_title)

    stmt = stmt.offset((page - 1) * size).limit(size)

    tickets = await db.execute(stmt)

    tickets = tickets.scalars().unique().all()

    return tickets

async def _delete_ticket(ticket_id: uuid.UUID, db: AsyncSession):
    ticket_db_entry = await db.execute(
        select(TicketTable).where(TicketTable.ticket_id == ticket_id)
    )
    ticket = ticket_db_entry.scalar_one_or_none()

    # If no ticket found, raise 404 Not Found exception
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    
    # Delete the ticket
    await db.delete(ticket)
    await db.commit()

    return True

async def _update_ticket(ticket_id: uuid.UUID, db: AsyncSession, title: Optional[str] = None, description: Optional[str] = None, status: Optional[TicketStatus] = None,):
    # Fetch the existing ticket
    result = await db.execute(
        select(TicketTable)
        .where(TicketTable.ticket_id == ticket_id)
        .options(
            joinedload(TicketTable.created_by_user),
            joinedload(TicketTable.project)
        )
    )
    ticket = result.scalar_one_or_none()

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    # Update only provided fields
    if title is not None:
        ticket.title = title
    if description is not None:
        ticket.description = description
    if status is not None:
        ticket.status = status

    await db.commit()
    await db.refresh(ticket)

    return ticket
