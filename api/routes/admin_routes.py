from fastapi import APIRouter, HTTPException, status

from api.core.authentication import AdminUserDep
from api.core.migrate import run_migrations
from api.schemas import MigrationUpgradeResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/migrations/upgrade/", response_model=MigrationUpgradeResponse)
def upgrade_migrations(_admin: AdminUserDep):
    """Apply any pending Alembic migrations (admin only)."""
    try:
        result = run_migrations()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {exc}",
        ) from exc

    if result["upgraded"]:
        message = (
            f"Upgraded database from {result['previous_revision']} "
            f"to {result['current_revision']}."
        )
    else:
        message = "Database is already at head; no migrations applied."

    return MigrationUpgradeResponse(
        previous_revision=result["previous_revision"],
        current_revision=result["current_revision"],
        head_revision=result["head_revision"],
        upgraded=bool(result["upgraded"]),
        message=message,
    )
