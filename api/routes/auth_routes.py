from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from api.core.authentication import (
    create_access_token,
    verify_google_token,
    verify_access_token,
)
from api.core.config import settings
from api.core.database import SessionDep
from api.models import Token, User
from api.schemas.authentication import GoogleLoginPayload, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login-google/", response_model=TokenResponse)
def login_with_google(payload: GoogleLoginPayload, session: SessionDep):
    try:
        google_token = verify_google_token(payload.credential)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(google_token, session)
    return access_token


@router.get("/verify-session/", response_model=TokenResponse)
def verify_session(
    access_token: Annotated[Token, Depends(verify_access_token)],
):
    return access_token


@router.get("/promote-superuser/", dependencies=[Depends(verify_access_token)])
def promote_superuser(session: SessionDep):
    if not settings.SUPERUSER_GID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Superuser GID specified.",
        )

    super_user = session.exec(
        select(User).where(User.google_user_id == settings.SUPERUSER_GID)
    ).first()

    if super_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified user not found.",
        )

    if super_user.admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already admin.",
        )

    super_user.admin = True
    session.add(super_user)
    session.commit()

    return {"message": "User promoted to admin successfully"}
