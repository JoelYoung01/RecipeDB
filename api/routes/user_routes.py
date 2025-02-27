from fastapi import APIRouter, HTTPException, status
from sqlalchemy import update
from sqlmodel import select

from api.core.authentication import CurrentUserDep
from api.core.database import SessionDep
from api.models import User
from api.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/user", tags=["User"])


@router.put("/{user_id:int}/", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile.",
        )

    update_stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**user_update.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    session.exec(update_stmt)
    session.commit()
    session.refresh(current_user)
    return current_user
