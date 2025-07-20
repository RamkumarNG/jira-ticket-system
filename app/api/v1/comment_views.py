import logging
import traceback
import uuid
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.dependencies import get_db
from app.schema.v1.comment import CommentCreateRequest, CommentUpdateRequest, CreateCommentResponse, ListCommentResponse, CommentGetResponse
from app.utils.comment import (
    _create_comment,
    _delete_comment,
    _get_comment_by_id,
    _get_comments_by_ticket_id,
    _update_comment,
    serialize_comment
)
from app.utils.user import _get_users
from app.schema.v1.common import RequestStatus

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("", response_model=CreateCommentResponse)
async def create_comment(
    request: Request,
    ticket_id: uuid.UUID,
    comment_data: CommentCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        db_user = await _get_users(db=db, username=comment_data.created_by)
        if len(db_user) == 0:
            return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request.state.id,
                "status": "failure",
                "message": f"User not found"
            }
        )
        new_comment = await _create_comment(
            content=comment_data.content,
            ticket_id=ticket_id,
            user_id=db_user[0].user_id,
            db=db
        )

        response = CreateCommentResponse(
            request_id=request.state.id,
            status=RequestStatus.success,
            message="Comment created successfully",
            data=serialize_comment(new_comment, username=comment_data.created_by)
        )
        return JSONResponse(content=jsonable_encoder(response), status_code=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request.state.id,
                "status": "failure",
                "message": f"Unexpected error: {str(e)}"
            }
        )

@router.get("", response_model=ListCommentResponse)
async def get_comments(
    request: Request,
    ticket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        comments = await _get_comments_by_ticket_id(ticket_id=ticket_id, db=db)

        response = ListCommentResponse(
            request_id=request.state.id,
            status=RequestStatus.success,
            message="Comments fetched successfully",
            data=[serialize_comment(c, c.user.username if c.user else "") for c in comments]
        )

        return JSONResponse(content=jsonable_encoder(response), status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request.state.id,
                "status": "failure",
                "message": f"Unexpected error: {str(e)}"
            }
        )

@router.put("/{comment_id}", response_model=CommentGetResponse)
async def update_comment(
    request: Request,
    comment_id: uuid.UUID,
    comment_data: CommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        updated_comment = await _update_comment(
            comment_id=comment_id,
            content=comment_data.content,
            db=db
        )

        response = CommentGetResponse(
            request_id=request.state.id,
            status=RequestStatus.success,
            message="Comment updated successfully",
            data=serialize_comment(updated_comment)
        )

        return JSONResponse(content=jsonable_encoder(response), status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request.state.id,
                "status": "failure",
                "message": f"Unexpected error: {str(e)}"
            }
        )

@router.delete("/{comment_id}")
async def delete_comment(
    request: Request,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        await _delete_comment(comment_id=comment_id, db=db)

        return JSONResponse(
            content={
                "request_id": request.state.id,
                "status": "success",
                "message": "Comment deleted successfully"
            },
            status_code=status.HTTP_200_OK
        )

    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "request_id": request.state.id,
                "status": "failure",
                "message": http_exc.detail
            }
        )
    except Exception as e:
        logger.exception(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "request_id": request.state.id,
                "status": "failure",
                "message": f"Unexpected error: {str(e)}"
            }
        )
