import logging
import asyncio
import uuid

from fastapi import APIRouter, Request, Depends, Query, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.schema.v1.ticket import TicketCreateRequest, CreateTicketResponse, TicketGetResponse, CreateTicket, ListTicketResponse
from app.schema.v1.common import RequestStatus
from app.core.database.dependencies import get_db
from app.utils.project import check_project_exists
from app.utils.user import check_user_exists
from app.utils.ticket import _create_ticket, _get_ticket_by_id, _get_tickets, _delete_ticket

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("")
async def list_tickets(
    request: Request,
    db: AsyncSession = Depends(get_db),
    project_name: str = Query(None, description="Filter by project name"),
    user_name: str = Query(None, description="Filter by user name"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(10, ge=1, description="Number of tickets per page")
):
    try:
        tickets = await _get_tickets(db=db, project_name=project_name, user_name=user_name, page=page, size=size)
        result = []
        for ticket in tickets:
            result.append(
                CreateTicket(
                    ticket_id = ticket.ticket_id,
                    title = ticket.title,
                    description = ticket.description,
                    status = ticket.status,
                    created_at = ticket.created_at,
                    project_name = ticket.project.name,
                    created_by = ticket.created_by_user.username,
                )
            )

        response = ListTicketResponse(
            request_id = request.state.id,
            status = RequestStatus.success,
            message= "Ticket details fetched successfully",
            data = result
        )

        return JSONResponse(
            jsonable_encoder(response),
            status_code = status.HTTP_200_OK
        )
    
    except HTTPException as http_exc:
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "status_code": http_exc.status_code,
                "status": "failure",
                "message": http_exc.detail,
                "request_id": request.state.id,
            }
        )

    except Exception as e:
        logger.exception(f"Unexpected error while listing ticket: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status": "failure",
                "message": "An unexpected error occurred while listing all tickets."
            }
        )

@router.post("", response_model = CreateTicketResponse, status_code = status.HTTP_201_CREATED)
async def create_ticket(
    request: Request,
    ticket_data: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        user_task = check_user_exists(user_name=ticket_data.created_by, db=db)
        project_task = check_project_exists(project_name=ticket_data.project_name, db=db)

        user, project = await asyncio.gather(user_task, project_task)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        new_ticket = await _create_ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            project_id=project.project_id,
            user_id=user.user_id,
            status=ticket_data.status,
            db=db
        )

        response = CreateTicketResponse(
            request_id = request.state.id,
            status = RequestStatus.success,
            message = "Ticket details",
            data = CreateTicket(
                ticket_id=new_ticket.ticket_id,
                title=new_ticket.title,
                description=new_ticket.description,
                status=new_ticket.status,
                project_name=ticket_data.project_name,
                created_by=ticket_data.created_by,
                created_at=new_ticket.created_at.isoformat()
            )
        )

        response = jsonable_encoder(response)
        return JSONResponse(response, status_code=status.HTTP_200_OK)


    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.exception(f"Unexpected error while creating ticket: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status": "failure",
                "message": "An unexpected error occurred while creating the ticket."
            }
        )

@router.get("/{ticket_id}")
async def get_ticket_by_id(request: Request, ticket_id: uuid.UUID, db: AsyncSession=Depends(get_db)):
    try:
        ticket = await _get_ticket_by_id(ticket_id=ticket_id, db=db)

        response = TicketGetResponse(
            request_id= request.state.id,
            status= RequestStatus.success,
            message= "Ticket details fetched successfully",
            data = CreateTicket(
                ticket_id = ticket.ticket_id,
                title = ticket.title,
                description = ticket.description,
                status = ticket.status,
                created_at = ticket.created_at,
                created_by = ticket.project.name,
                project_name = ticket.created_by_user.username,
            )
        )

        response = jsonable_encoder(response)
        return JSONResponse(response, status_code=status.HTTP_200_OK)
    
    except HTTPException as http_exc:
        logger.warning(f"Ticket not found: {ticket_id} -> {http_exc.detail}")
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "status_code": http_exc.status_code,
                "status": "failure",
                "message": http_exc.detail,
                "request_id": request.state.id,
            }
        )

    except Exception as e:
        logger.exception(f"Unexpected error while getting ticket: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status": "failure",
                "message": "An unexpected error occurred while getting the ticket."
            }
        )

@router.delete("/{ticket_id}")
async def delete_ticket_by_id(request: Request, ticket_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        await _delete_ticket(ticket_id=ticket_id, db=db)
        return JSONResponse(
            content={
                "request_id": request.state.id,
                "status": RequestStatus.success,
                "message": "Ticket deleted successfully"
            },
            status_code= status.HTTP_200_OK
        )

    except HTTPException as http_exc:
        logger.warning(f"Ticket not found: {ticket_id} -> {http_exc.detail}")
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "status_code": http_exc.status_code,
                "status": "failure",
                "message": http_exc.detail,
                "request_id": request.state.id,
            }
        )

    except Exception as e:
        logger.exception(f"Unexpected error while deleting ticket: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "status": "failure",
                "message": "An unexpected error occurred while deleting the ticket."
            }
        )
