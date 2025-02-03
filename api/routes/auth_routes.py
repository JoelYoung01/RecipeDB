from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from api.core.authentication import (
    create_access_token,
    verify_google_token,
    verify_access_token,
)
from api.core.database import SessionDep
from api.models.authentication import Token
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


@router.get("/verify-session/", tags=["Auth"], response_model=TokenResponse)
def verify_session(
    access_token: Annotated[Token, Depends(verify_access_token)],
):
    return access_token
