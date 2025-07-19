import uuid
from datetime import datetime
from typing import List, Optional, Union, Tuple, Dict

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.database.models import TicketTable, ProjectTable, UserTable

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
