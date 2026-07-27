from fastapi import APIRouter

from api.core.config import settings
from api.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health/", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.APP_VERSION)
