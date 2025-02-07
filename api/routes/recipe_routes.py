from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import update
from sqlmodel import or_, select

from api.core.authentication import CurrentUserDep, get_admin_user, verify_access_token
from api.core.database import SessionDep
from api.models.recipe import Recipe
from api.schemas.recipe import RecipeCreate, RecipeDetail, RecipeSlim, RecipeUpdate

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


@router.get("/user/", response_model=list[RecipeSlim])
def get_active_apps(current_user: CurrentUserDep, session: SessionDep):
    recipes = session.exec(
        select(Recipe).where(Recipe.created_by == current_user)
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


@router.post(
    "/",
    response_model=RecipeDetail,
)
def create_recipe(recipe: RecipeCreate, session: SessionDep):
    db_app_dev = Recipe.model_validate(recipe)
    session.add(db_app_dev)
    session.commit()
    session.refresh(db_app_dev)
    return db_app_dev


@router.put(
    "/{recipe_id:int}/",
    response_model=RecipeDetail,
    dependencies=[Depends(get_admin_user)],
)
def update_recipe(recipe_id: int, recipe: RecipeUpdate, session: SessionDep):
    existing_recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if existing_recipe:
        update_stmt = (
            update(Recipe)
            .where(Recipe.id == recipe_id)
            .values(**recipe.model_dump(exclude_unset=True))
            .execution_options(synchronize_session="fetch")
        )
        session.exec(update_stmt)
        session.commit()
        session.refresh(existing_recipe)
        return existing_recipe
    else:
        raise HTTPException(
            status_code=404, detail=f"Recipe with id {recipe_id} not found."
        )


@router.delete("/{recipe_id:int}/", dependencies=[Depends(get_admin_user)])
def delete_recipe(recipe_id: int, session: SessionDep):
    existing_recipe = session.exec(select(Recipe).where(Recipe.id == recipe_id)).first()
    if existing_recipe:
        session.delete(existing_recipe)
        session.commit()
    else:
        raise HTTPException(
            status_code=404, detail=f"Recipe with id {recipe_id} not found."
        )
