from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import select

from api.core.authentication import (
    authenticate_password_user,
    can_resend_otp,
    create_access_token,
    create_access_token_for_user,
    get_user_by_email,
    issue_email_otp,
    register_password_user,
    verify_access_token,
    verify_email_redirect_path,
    verify_google_token,
    verify_user_email_otp,
)
from api.core.config import settings
from api.core.database import SessionDep
from api.models import EmailVerificationChallenge, Token, User
from api.schemas import (
    AuthRedirectResponse,
    GoogleLoginPayload,
    PasswordLoginPayload,
    RegisterPayload,
    ResendVerificationPayload,
    TokenResponse,
    VerifyEmailPayload,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _dev_otp_field(otp: str | None) -> str | None:
    if settings.ENVIRONMENT == "development":
        return otp
    return None


@router.post("/register/", response_model=AuthRedirectResponse, status_code=201)
def register_with_password(payload: RegisterPayload, session: SessionDep):
    user, otp = register_password_user(
        email=payload.email,
        password=payload.password,
        display_name=payload.display_name,
        session=session,
    )
    body = AuthRedirectResponse(
        code="verification_required",
        message="Account created. Check your email for a verification code.",
        redirect_to=verify_email_redirect_path(user.email),
        email=user.email,
        dev_otp=_dev_otp_field(otp),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=body.model_dump(),
        headers={"Location": body.redirect_to},
    )


@router.post("/login/", response_model=TokenResponse)
def login_with_password(payload: PasswordLoginPayload, session: SessionDep):
    user = authenticate_password_user(
        email=payload.email, password=payload.password, session=session
    )
    if not user.email_verified:
        # Server directs the client to the verification page via 403 + Location.
        challenge = session.exec(
            select(EmailVerificationChallenge).where(
                EmailVerificationChallenge.user_id == user.id
            )
        ).first()
        otp = None
        if can_resend_otp(challenge):
            otp = issue_email_otp(user, session)

        detail = {
            "code": "email_not_verified",
            "message": "Email address is not verified. Enter the code we sent you.",
            "redirect_to": verify_email_redirect_path(user.email),
            "email": user.email,
        }
        if settings.ENVIRONMENT == "development" and otp:
            detail["dev_otp"] = otp

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers={"Location": detail["redirect_to"]},
        )

    return create_access_token_for_user(user, session)


@router.post("/verify-email/", response_model=TokenResponse)
def verify_email(payload: VerifyEmailPayload, session: SessionDep):
    user = verify_user_email_otp(email=payload.email, otp=payload.otp, session=session)
    return create_access_token_for_user(user, session)


@router.post("/resend-verification/", response_model=AuthRedirectResponse)
def resend_verification(payload: ResendVerificationPayload, session: SessionDep):
    """
    Resend a verification OTP. Always returns a generic success body so callers
    cannot enumerate registered emails.
    """
    generic = AuthRedirectResponse(
        code="verification_resent",
        message="If an unverified account exists for that email, a new code was sent.",
        redirect_to=verify_email_redirect_path(str(payload.email)),
        email=str(payload.email).strip().lower(),
        dev_otp=None,
    )

    user = get_user_by_email(session, str(payload.email))
    if user is None or user.email_verified or not user.hashed_password:
        return generic

    challenge = session.exec(
        select(EmailVerificationChallenge).where(
            EmailVerificationChallenge.user_id == user.id
        )
    ).first()

    if not can_resend_otp(challenge):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Please wait before requesting another verification code "
                f"(cooldown {settings.EMAIL_OTP_RESEND_COOLDOWN_SECONDS}s)."
            ),
        )

    otp = issue_email_otp(user, session)
    generic.dev_otp = _dev_otp_field(otp)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=generic.model_dump(),
        headers={"Location": generic.redirect_to},
    )


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
