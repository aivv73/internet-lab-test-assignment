from fastapi import APIRouter, HTTPException, status

from app.schemas.contact import ContactRequest, ContactResponse
from app.schemas.error import ErrorResponse

router = APIRouter(prefix="/contact", tags=["contact"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ContactResponse,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ErrorResponse},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_501_NOT_IMPLEMENTED: {
            "description": "Temporary scaffold response until contact workflow is implemented."
        },
    },
)
async def submit_contact(_payload: ContactRequest) -> ContactResponse:
    """Accept a contact form submission.

    The HTTP contract is declared in this phase. The full workflow is implemented in later
    phases: rate limiting, AI analysis, persistence, email delivery, and metrics.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Contact workflow is not implemented yet.",
    )
