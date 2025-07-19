import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
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
    print('---->', user)

    if user:
        return user

    new_user = UserTable(
        user_id=uuid.uuid4(),
        username=user_name,
        status=UserStatus.ACTIVE,
        api_key=uuid.uuid4(),
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

async def _get_user_by_id(user_id: uuid.UUID, db: AsyncSession):
    user_db_entry = await db.execute(
        select(UserTable).where(UserTable.user_id == user_id)
    )
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
):
    stmt = select(UserTable)

    print(f'username:::::{username}')

    if username:
        stmt = stmt.where(UserTable.username.ilike(f"%{username}%"))
    
    if status:
        stmt = stmt.where(UserTable.status == status)

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
