from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.core.config import Settings, get_settings
from app.schemas.contact import ContactRequest, ContactResponse
from app.schemas.error import ErrorResponse
from app.services.contact_service import ContactService

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ContactResponse,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    },
)
async def submit_contact(
    payload: ContactRequest,
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ContactResponse:
    """Accept a contact form submission and run the backend workflow."""
    client_ip = request.client.host if request.client else "unknown"
    return await ContactService(settings).submit(payload, client_ip=client_ip)
