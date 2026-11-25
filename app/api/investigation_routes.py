
import logging

from fastapi import APIRouter, HTTPException, Request

from app.api.schemas import InvestigationRequest

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/investigations",
    tags=["Investigations"]
)


@router.post("")
def create_investigation(
    payload: InvestigationRequest,
    request: Request
):
    """
    Run an incident investigation and return a validated RCA report.
    """

    investigation_service = getattr(
        request.app.state,
        "investigation_service",
        None
    )

    if investigation_service is None:
        raise HTTPException(
            status_code=503,
            detail="Investigation service is not available."
        )

    try:
        result = investigation_service.investigate(
            query=payload.query,
            top_k=payload.top_k,
            max_hops=payload.max_hops
        )

        return result

    except Exception:
        logger.exception("Incident investigation failed")

        raise HTTPException(
            status_code=500,
            detail="The incident investigation could not be completed."
        )
