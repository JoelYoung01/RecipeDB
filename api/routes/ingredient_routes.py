from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlmodel import select

from api.core.authentication import CurrentUserDep, get_admin_user, verify_access_token
from api.core.database import SessionDep
from api.models import Ingredient
from api.schemas import IngredientCreate, IngredientDetail, IngredientUpdate

router = APIRouter(
    prefix="/ingredient",
    dependencies=[Depends(verify_access_token)],
    tags=["Ingredient"],
)


@router.post(
    "/",
    response_model=IngredientDetail,
)
def create_ingredient(
    ingredient: IngredientCreate, currentUser: CurrentUserDep, session: SessionDep
):
    ingredient_data = ingredient.model_dump(exclude_unset=True)
    ingredient_data["created_on"] = datetime.now(timezone.utc)
    ingredient_data["created_by_id"] = currentUser.id
    db_ingredient = Ingredient.model_validate(ingredient_data)
    session.add(db_ingredient)
    session.commit()
    session.refresh(db_ingredient)
    return db_ingredient


@router.put(
    "/{ingredient_id:int}/",
    response_model=IngredientDetail,
)
def update_ingredient(
    ingredient_id: int,
    ingredient: IngredientUpdate,
    currentUser: CurrentUserDep,
    session: SessionDep,
):
    existing_ingredient = session.exec(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    ).first()

    if not existing_ingredient:
        raise HTTPException(
            status_code=404, detail=f"Ingredient with id {ingredient_id} not found."
        )

    if currentUser.id != existing_ingredient.created_by_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the creator of this ingredient.",
        )

    update_stmt = (
        update(Ingredient)
        .where(Ingredient.id == ingredient_id)
        .values(**ingredient.model_dump(exclude_unset=True))
        .execution_options(synchronize_session="fetch")
    )
    session.exec(update_stmt)
    session.commit()
    session.refresh(existing_ingredient)
    return existing_ingredient


@router.delete("/{ingredient_id:int}/", dependencies=[Depends(get_admin_user)])
def delete_ingredient(ingredient_id: int, session: SessionDep):
    existing_ingredient = session.exec(
        select(Ingredient).where(Ingredient.id == ingredient_id)
    ).first()
    if not existing_ingredient:
        raise HTTPException(
            status_code=404, detail=f"Ingredient with id {ingredient_id} not found."
        )

    session.delete(existing_ingredient)
    session.commit()
