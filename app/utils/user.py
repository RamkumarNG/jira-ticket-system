import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.models import UserTable, UserStatus


async def check_user_exists(user_name: str, db: AsyncSession):
    stm = select(UserTable).where(UserTable.username == user_name)
    result = await db.execute(stm)
    user = result.scalar_one_or_none()

    return user

async def create_default_user(db: AsyncSession, user_name: str = "admin") -> UserTable:
    stmt = select(UserTable).where(UserTable.username == user_name)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        return user

    new_user = UserTable(
        user_id=uuid.uuid4(),
        username=user_name,
        status=UserStatus.ACTIVE,
        api_key=uuid.uuid4(),
        email=f'{user_name}@gg.com'
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def _create_user(username: str, email: str, password: str, status: str, db: AsyncSession):
    new_user = UserTable(
        user_id=uuid.uuid4(),
        username=username,
        email=email,
        status=status,
        api_key=uuid.uuid4(),
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def _get_user_by_id(
        user_id: uuid.UUID,
        db: AsyncSession,
        include_created: bool = False,
        include_assigned: bool = False,
        include_comments: bool = False
):
    stmt = select(UserTable).where(UserTable.user_id == user_id)

    if include_created:
        stmt = stmt.options(selectinload(UserTable.tickets_created))
    if include_assigned:
        stmt = stmt.options(selectinload(UserTable.tickets_assigned))
    if include_comments:
        stmt = stmt.options(selectinload(UserTable.comments))

    user_db_entry = await db.execute(stmt)
    user = user_db_entry.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    return user

async def _get_users(
        db: AsyncSession,
        username: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        email: Optional[str] = None,
        include_created: bool = False,
        include_assigned: bool = False,
        include_comments: bool = False
):
    stmt = select(UserTable)

    if username:
        stmt = stmt.where(UserTable.username.ilike(f"%{username}%"))
    if status:
        stmt = stmt.where(UserTable.status == status)
    if email:
        stmt = stmt.where(UserTable.email == email)
    
    if include_created:
        stmt = stmt.options(selectinload(UserTable.tickets_created))
    if include_assigned:
        stmt = stmt.options(selectinload(UserTable.tickets_assigned))
    if include_comments:
        stmt = stmt.options(selectinload(UserTable.comments))


    stmt = stmt.offset((page - 1) * size).limit(size)

    users = await db.execute(stmt)

    users = users.scalars().unique().all()

    return users

async def _delete_user(user_id: uuid.UUID, db: AsyncSession):
    user_db_entry = await db.execute(
        select(UserTable).where(UserTable.user_id == user_id)
    )
    user = user_db_entry.scalar_one_or_none()

    # If no user found, raise 404 Not Found exception
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    # Delete the user
    await db.delete(user)
    await db.commit()

    return True


def serialize_user(user, include_created=False, include_assigned=False, include_comments=False) -> dict:
    user_data = {
        "id": str(user.user_id),
        "username": user.username,
        "email": user.email,
        "status": user.status,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

    if include_created:
        user_data["tickets_created"] = [serialize_ticket(t) for t in user.tickets_created]

    if include_assigned:
        user_data["tickets_assigned"] = [serialize_ticket(t) for t in user.tickets_assigned]

    if include_comments:
        user_data["comments"] = [
            {
                "id": str(c.comment_id),
                "content": c.content,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in user.comments
        ]

    return user_data
