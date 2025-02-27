from datetime import UTC, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import update
from sqlmodel import and_, or_, select

from api.core.authentication import CurrentUserDep, verify_access_token
from api.core.database import SessionDep
from api.models import Recipe, Ingredient
from api.schemas import (
    RecipeCreate,
    RecipeDashboard,
    RecipeDetail,
    RecipeSlim,
    RecipeUpdate,
)

router = APIRouter(
    prefix="/recipe",
    dependencies=[Depends(verify_access_token)],
    tags=["Recipe"],
)
unauth_router = APIRouter(
    prefix="/recipe",
    tags=["Recipe"],
)


@unauth_router.get("/public/")
def get_public_recipes(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    recipes = session.exec(
        select(Recipe).where(Recipe.public).offset(offset).limit(limit)
    ).all()
    return recipes


@router.get("/all/", response_model=list[RecipeSlim])
def get_all_recipes(
    current_user: CurrentUserDep,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    recipes = session.exec(
        select(Recipe)
        .where(or_(Recipe.public, Recipe.created_by == current_user))
        .offset(offset)
        .limit(limit)
    ).all()
    return recipes


@router.get("/user/", response_model=list[RecipeDashboard])
def get_users_recipes(current_user: CurrentUserDep, session: SessionDep):
    recipes = session.exec(
        select(Recipe).where(Recipe.created_by == current_user)
    ).all()
    return recipes


@router.get("/user/recent/", response_model=list[RecipeDashboard])
def get_users_recently_added_recipes(current_user: CurrentUserDep, session: SessionDep):
    recipes = session.exec(
        select(Recipe)
        .where(Recipe.created_by == current_user)
        .order_by(Recipe.created_on.desc())
        .limit(5)
    ).all()
    return recipes


@router.get(
    "/{recipe_id:int}/",
    response_model=RecipeDetail,
)
def get_recipe_by_id(
    recipe_id: int,
    session: SessionDep,
):
    recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if not recipe:
        raise HTTPException(
            status_code=404, detail=f"Recipe with id {recipe_id} not found."
        )
    return recipe


@router.get("/search/", response_model=list[RecipeDashboard])
def search_recipes(
    searchText: str,
    current_user: CurrentUserDep,
    session: SessionDep,
    offset=0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    if not searchText:
        recipes = session.exec(select(Recipe).where(Recipe.public).limit(25)).all()
        return recipes

    query = (
        select(Recipe)
        .distinct()
        .join(Recipe.ingredients, isouter=True)
        .where(
            and_(
                or_(Recipe.public, Recipe.created_by == current_user),
                or_(
                    Recipe.name.ilike(f"%{searchText}%"),
                    Recipe.description.ilike(f"%{searchText}%"),
                    Recipe.instructions.ilike(f"%{searchText}%"),
                    Recipe.notes.ilike(f"%{searchText}%"),
                    Recipe.ingredients.any(
                        or_(
                            Ingredient.name.ilike(f"%{searchText}%"),
                            Ingredient.details.ilike(f"%{searchText}%"),
                        )
                    ),
                ),
            )
        )
        .offset(offset)
        .limit(limit)
    )

    recipes = session.exec(query).all()
    return recipes


@router.post(
    "/",
    response_model=RecipeDetail,
)
def create_recipe(
    recipe: RecipeCreate, currentUser: CurrentUserDep, session: SessionDep
):
    rec_dict = recipe.model_dump()
    rec_dict["created_on"] = datetime.now(UTC)
    rec_dict["created_by_id"] = currentUser.id

    db_app_dev = Recipe.model_validate(rec_dict)
    session.add(db_app_dev)
    session.commit()
    session.refresh(db_app_dev)
    return db_app_dev


@router.put(
    "/{recipe_id:int}/",
    response_model=RecipeDetail,
)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    currentUser: CurrentUserDep,
    session: SessionDep,
):
    existing_recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()

    if not existing_recipe:
        raise HTTPException(
            status_code=404, detail=f"Recipe with id {recipe_id} not found."
        )

    if currentUser.id != existing_recipe.created_by_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the creator of this recipe.",
        )

    update_stmt = (
        update(Recipe)
        .where(Recipe.id == recipe_id)
        .values(**recipe.model_dump())
        .execution_options(synchronize_session="fetch")
    )
    session.exec(update_stmt)
    session.commit()
    session.refresh(existing_recipe)
    return existing_recipe


@router.delete("/{recipe_id:int}/")
def delete_recipe(recipe_id: int, currentUser: CurrentUserDep, session: SessionDep):
    existing_recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()

    if not existing_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found.",
        )

    if existing_recipe.created_by_id != currentUser.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the creator of this recipe.",
        )

    session.delete(existing_recipe)
    session.commit()
