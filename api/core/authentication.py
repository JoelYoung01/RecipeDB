from typing import Annotated
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select


from api.core.database import SessionDep
from api.models import Token, TokenType, User
from api.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM]
        )
        user_id: str | None = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = session.exec(select(User).where(User.id == user_id)).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_admin_user(
    current_active_user: Annotated[User, Depends(get_current_active_user)],
):
    if not current_active_user.admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return current_active_user


def get_or_create_user_from_google_token(google_token, session: SessionDep):
    db_user = session.exec(
        select(User).where(User.google_user_id == google_token["sub"])
    ).first()

    if db_user is None:
        new_user = {
            "username": google_token["email"],
            "email": google_token["email"],
            "display_name": google_token["name"],
            "google_user_id": google_token["sub"],
            "avatar_url": google_token["picture"],
            "last_login": datetime.now(tz=timezone.utc),
        }
        db_user = User.model_validate(new_user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    return db_user


def create_access_token(google_token, session: SessionDep):
    user = get_or_create_user_from_google_token(google_token, session)

    # Create a long-lived session token
    access_token = jwt.encode(
        {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        },
        settings.SECRET_KEY,
        algorithm=settings.HASH_ALGORITHM,
    )

    db_token = Token.model_validate(
        {
            "access_token": access_token,
            "token_type": TokenType.Access,
            "user_id": user.id,
        }
    )

    session.add(db_token)

    # Update last_login timestamp
    user.last_login = datetime.now(timezone.utc)
    session.add(user)

    session.commit()
    session.refresh(db_token)

    return db_token


def verify_access_token(
    access_token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> Token:
    try:
        # Verify the session token
        jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.HASH_ALGORITHM]
        )
        db_token = session.exec(
            select(Token).where(Token.access_token == access_token)
        ).first()
        return db_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_google_token(encoded_google_token: str):
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_req

    request = google_req.Request()
    decoded_token = id_token.verify_oauth2_token(
        encoded_google_token, request, settings.VITE_GOOGLE_CLIENT_ID
    )
    return decoded_token


CurrentUserDep = Annotated[User, Depends(get_current_active_user)]
