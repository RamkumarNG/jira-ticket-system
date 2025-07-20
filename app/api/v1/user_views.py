import logging
import traceback
import uuid
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status, Request, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.core.database.models import UserTable, UserStatus
from app.schema.v1.common import RequestStatus
from app.core.database.dependencies import get_db
from app.schema.v1.user import UserCreateRequest, UserUpdateRequest, ListUserResponse, UserGetResponse, CreateUserResponse, User
from app.utils.user import _create_user, _get_user_by_id, _get_users, _delete_user, serialize_user
from app.utils.ticket import serialize_ticket
from app.utils.comment import serialize_comment

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        existing_user = await _get_user_by_id(user_id=user_data.user_id, db=db)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists.")

        new_user = await _create_user(
            user_id=uuid.uuid4(),
            username=user_data.username,
            email=user_data.email,
            password_hash=user_data.password_hash,
            status=UserStatus.ACTIVE,
            db=db
        )

        response = CreateUserResponse(
            request_id=request.state.id,
            status="success",
            message="User created successfully",
            data=new_user
        )

        return JSONResponse(
            content=response.dict(),
            status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "failure",
                "message": f"An unexpected error occurred: {str(e)}",
                "request_id": request.state.id
            }
        )

@router.get("/{user_id}", response_model=UserGetResponse)
async def get_user_by_id(
    request: Request,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    include_created: bool = Query(False),
    include_assigned: bool = Query(False),
):
    try:
        user = await _get_user_by_id(user_id=user_id, db=db, include_assigned=include_assigned, include_created=include_created)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
        user_data = {
            "user_id": str(user.user_id),
            "username": user.username,
            "email": user.email,
            "status": user.status if user.status else None,
        }

        include_map = {
            "tickets_created": include_created,
            "tickets_assigned": include_assigned,
        }

        for key, include in include_map.items():
            if include:
                user_data[key] = [serialize_ticket(t) for t in getattr(user, key)]

        print(f'user_data::::{user_data}')
        response = UserGetResponse(
            request_id=request.state.id,
            status=RequestStatus.success,
            message="User details fetched successfully",
            data=user_data
        )

        return JSONResponse(
            jsonable_encoder(response),
            status_code=status.HTTP_200_OK
        )
    
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "status": "failure",
                "message": http_exc.detail,
                "request_id": request.state.id
            }
        )
    
    except Exception as e:
        logger.exception(f"Traceback while getting user by id: {traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "failure",
                "message": f"An unexpected error occurred: {str(e)}",
                "request_id": request.state.id
            }
        )

@router.get("")
async def list_users(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    email: str = Query(None),
):
    try:
        users = await _get_users(db=db, page=page, size=size, email=email)
        print(users)
        serilaizer_user = [
            User(
                user_id = _user.user_id,
                username = _user.username,
                email = _user.email,
                status = _user.status if _user.status else UserStatus.INACTIVE,
            )
            for _user in users
        ]     

        response = ListUserResponse (
            request_id = request.state.id,
            status =  RequestStatus.success,
            message = "Users fetched successfully",
            data = serilaizer_user
        )

        return JSONResponse(
            jsonable_encoder(response),
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "failure",
                "message": f"An unexpected error occurred: {str(e)}",
                "request_id": request.state.id
            }
        )


@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: uuid.UUID,
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_user = await _get_user_by_id(user_id=user_id, db=db)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
        if user_data.email:
            db_user.email = user_data.email
        if user_data.status:
            db_user.status = user_data.status
        if user_data.username:
            db_user.username = user_data.username
        
        data = User(**asdict(db_user))
        
        await db.commit()

        response = UserGetResponse(
            request_id=request.state.id,
            status=RequestStatus.success,
            message="User updated successfully",
            data=data
        )

        return JSONResponse(
            jsonable_encoder(response),
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        logger.exception(f"Traceback while updating user: {traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "failure",
                "message": f"An unexpected error occurred: {str(e)}",
                "request_id": request.state.id
            }
        )


@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await _get_user_by_id(user_id=user_id, db=db)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
        await _delete_user(user_id=user_id, db=db)

        return JSONResponse(
            content={
                "request_id": request.state.id,
                "status": "success",
                "message": "User deleted successfully"
            },
            status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "failure",
                "message": f"An unexpected error occurred: {str(e)}",
                "request_id": request.state.id
            }
        )
