from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated
from urllib.parse import urlencode

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from api.core.config import settings
from api.core.database import SessionDep
from api.core.email import send_verification_otp_email
from api.core.security import (
    generate_otp,
    hash_otp,
    hash_password,
    otp_expiry,
    validate_password_strength,
    verify_otp,
    verify_password,
)
from api.models import EmailVerificationChallenge, Token, TokenType, User

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
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "email_not_verified",
                "message": "Email address is not verified",
                "redirect_to": verify_email_redirect_path(current_user.email),
                "email": current_user.email,
            },
        )
    return current_user


async def get_admin_user(
    current_active_user: Annotated[User, Depends(get_current_active_user)],
):
    if not current_active_user.admin:
        raise HTTPException(status_code=403, detail="User is not admin")
    return current_active_user


def normalize_email(email: str) -> str:
    return email.strip().lower()


def verify_email_redirect_path(email: str) -> str:
    query = urlencode({"email": normalize_email(email)})
    return f"{settings.VERIFY_EMAIL_PATH}?{query}"


def get_user_by_email(session: SessionDep, email: str) -> User | None:
    return session.exec(
        select(User).where(User.email == normalize_email(email))
    ).first()


def issue_email_otp(user: User, session: SessionDep) -> str:
    """Create/replace an OTP challenge and send it. Returns plaintext OTP."""
    otp = generate_otp()
    now = datetime.now(tz=timezone.utc)
    challenge = session.exec(
        select(EmailVerificationChallenge).where(
            EmailVerificationChallenge.user_id == user.id
        )
    ).first()

    if challenge is None:
        challenge = EmailVerificationChallenge(
            user_id=user.id,
            otp_hash=hash_otp(otp, user.email),
            expires_at=otp_expiry(now),
            attempts=0,
            last_sent_at=now,
        )
    else:
        challenge.otp_hash = hash_otp(otp, user.email)
        challenge.expires_at = otp_expiry(now)
        challenge.attempts = 0
        challenge.last_sent_at = now

    session.add(challenge)
    session.commit()
    session.refresh(challenge)

    send_verification_otp_email(user.email, otp)
    return otp


def can_resend_otp(challenge: EmailVerificationChallenge | None) -> bool:
    if challenge is None or challenge.last_sent_at is None:
        return True
    last = challenge.last_sent_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    elapsed = (datetime.now(tz=timezone.utc) - last).total_seconds()
    return elapsed >= settings.EMAIL_OTP_RESEND_COOLDOWN_SECONDS


def register_password_user(
    *,
    email: str,
    password: str,
    display_name: str,
    session: SessionDep,
) -> tuple[User, str]:
    strength_error = validate_password_strength(password)
    if strength_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=strength_error
        )

    normalized = normalize_email(email)
    existing = get_user_by_email(session, normalized)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        username=normalized,
        email=normalized,
        display_name=display_name.strip(),
        hashed_password=hash_password(password),
        email_verified=False,
        admin=False,
        disabled=False,
        last_login=None,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    otp = issue_email_otp(user, session)
    return user, otp


# Precomputed Argon2 hash used only to keep missing-user login timing similar.
_DUMMY_PASSWORD_HASH = hash_password("invalid-password-placeholder")


def authenticate_password_user(
    *, email: str, password: str, session: SessionDep
) -> User:
    user = get_user_by_email(session, email)
    hashed = user.hashed_password if user is not None else None
    if not hashed or not verify_password(password, hashed):
        if not hashed:
            verify_password(password, _DUMMY_PASSWORD_HASH)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def email_not_verified_http_exception(email: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "email_not_verified",
            "message": "Email address is not verified. Enter the code we sent you.",
            "redirect_to": verify_email_redirect_path(email),
            "email": normalize_email(email),
        },
        headers={"Location": verify_email_redirect_path(email)},
    )


def verify_user_email_otp(*, email: str, otp: str, session: SessionDep) -> User:
    user = get_user_by_email(session, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code.",
        )

    if user.email_verified:
        return user

    challenge = session.exec(
        select(EmailVerificationChallenge).where(
            EmailVerificationChallenge.user_id == user.id
        )
    ).first()

    if challenge is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code pending. Request a new one.",
        )

    expires_at = challenge.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(tz=timezone.utc) > expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Request a new one.",
        )

    if challenge.attempts >= settings.EMAIL_OTP_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many invalid attempts. Request a new code.",
        )

    if not verify_otp(otp.strip(), user.email, challenge.otp_hash):
        challenge.attempts += 1
        session.add(challenge)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code.",
        )

    user.email_verified = True
    session.add(user)
    session.delete(challenge)
    session.commit()
    session.refresh(user)
    return user


def get_or_create_user_from_google_token(google_token, session: SessionDep):
    db_user = session.exec(
        select(User).where(User.google_user_id == google_token["sub"])
    ).first()

    if db_user is None:
        email = normalize_email(google_token["email"])
        # Link an existing password account with the same verified Google email.
        db_user = get_user_by_email(session, email)
        if db_user is None:
            new_user = {
                "username": email,
                "email": email,
                "display_name": google_token.get("name") or email.split("@")[0],
                "google_user_id": google_token["sub"],
                "avatar_url": google_token.get("picture"),
                "email_verified": True,
                "last_login": datetime.now(tz=timezone.utc),
            }
            db_user = User.model_validate(new_user)
            session.add(db_user)
        else:
            db_user.google_user_id = google_token["sub"]
            db_user.email_verified = True
            if not db_user.avatar_url and google_token.get("picture"):
                db_user.avatar_url = google_token["picture"]
            session.add(db_user)
        session.commit()
        session.refresh(db_user)
    elif not db_user.email_verified:
        db_user.email_verified = True
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    return db_user


def create_access_token_for_user(user: User, session: SessionDep) -> Token:
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

    user.last_login = datetime.now(timezone.utc)
    session.add(user)

    session.commit()
    session.refresh(db_token)

    return db_token


def create_access_token(google_token, session: SessionDep):
    user = get_or_create_user_from_google_token(google_token, session)
    return create_access_token_for_user(user, session)


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
    from google.auth.transport import requests as google_req
    from google.oauth2 import id_token

    request = google_req.Request()
    decoded_token = id_token.verify_oauth2_token(
        encoded_google_token, request, settings.VITE_GOOGLE_CLIENT_ID
    )
    return decoded_token


CurrentUserDep = Annotated[User, Depends(get_current_active_user)]
AdminUserDep = Annotated[User, Depends(get_admin_user)]
