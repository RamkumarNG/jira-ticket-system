import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database.models import CommentTable
from app.schema.v1.comment import CommentSerializer


async def _create_comment(
    content: str,
    ticket_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession
) -> CommentTable:
    new_comment = CommentTable(
        comment_id=uuid.uuid4(),
        content=content,
        ticket_id=ticket_id,
        user_id=user_id,
        created_at=datetime.utcnow()
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment


async def _get_comment_by_id(
    comment_id: uuid.UUID,
    db: AsyncSession
) -> CommentTable:
    result = await db.execute(
        select(CommentTable)
        .options(
            joinedload(CommentTable.user),
            joinedload(CommentTable.ticket)
        )
        .where(CommentTable.comment_id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    return comment


async def _get_comments_by_ticket_id(
    ticket_id: uuid.UUID,
    db: AsyncSession
) -> List[CommentTable]:
    result = await db.execute(
        select(CommentTable)
        .options(joinedload(CommentTable.user))
        .where(CommentTable.ticket_id == ticket_id)
        .order_by(CommentTable.created_at.asc())
    )
    return result.scalars().all()


async def _update_comment(
    comment_id: uuid.UUID,
    content: str,
    db: AsyncSession
) -> CommentTable:

    comment = await db.execute(
        select(CommentTable)
        .where(CommentTable.comment_id == comment_id)
    )

    comment.content = content
    await db.commit()
    await db.refresh(comment)

    return comment


async def _delete_comment(
    comment_id: uuid.UUID,
    db: AsyncSession
) -> bool:
    
    comment = await db.execute(
        select(CommentTable)
        .where(CommentTable.comment_id == comment_id)
    )

    await db.delete(comment)
    await db.commit()

    return True


def serialize_comment(comment: CommentTable, username: str='') -> dict:
    comment = {
        "comment_id": str(comment.comment_id),
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
        "created_by": username
    }

    return CommentSerializer(**(comment)).dict()
