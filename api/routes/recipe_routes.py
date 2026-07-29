from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, update
from sqlalchemy.orm import selectinload
from sqlmodel import and_, or_, select

from api.core.authentication import CurrentUserDep, verify_access_token
from api.core.database import SessionDep
from api.core.image_gen.service import generate_recipe_cover_upload
from api.models import Ingredient, Recipe
from api.schemas import (
    CountResponse,
    RecipeCard,
    RecipeCoverGenerateRequest,
    RecipeCreate,
    RecipeDetail,
    RecipeUpdate,
    UploadFileResponse,
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


@router.post("/generate-cover/", response_model=UploadFileResponse)
def generate_recipe_cover(
    body: RecipeCoverGenerateRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    """Fetch/generate a cover image from the active image provider (default: broke).

    Creates an Upload owned by the current user. The client should set
    ``cover_image_id`` on create/update — same pattern as manual upload.
    """
    ingredients = [
        {"name": ing.name} for ing in body.ingredients if (ing.name or "").strip()
    ]
    upload = generate_recipe_cover_upload(
        user=current_user,
        db=session,
        title=body.name,
        description=body.description,
        ingredients=ingredients,
    )
    if upload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No suitable cover image found. Try a clearer recipe name, "
            "or upload a photo instead.",
        )
    return upload


@unauth_router.get("/public/", response_model=list[RecipeDetail])
def get_public_recipes(
    session: SessionDep,
    user: int = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    stmt = (
        select(Recipe)
        .where(Recipe.public)
        .options(
            selectinload(Recipe.cover_image),
            selectinload(Recipe.created_by),
            selectinload(Recipe.ingredients),
        )
        .offset(offset)
        .limit(limit)
    )

    if user:
        stmt = stmt.where(Recipe.created_by_id == user)

    recipes = session.exec(stmt).all()
    return recipes


@router.get("/all/", response_model=list[RecipeCard])
def get_all_recipes(
    current_user: CurrentUserDep,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
):
    recipes = session.exec(
        select(Recipe)
        .where(or_(Recipe.public, Recipe.created_by == current_user))
        .options(selectinload(Recipe.cover_image))
        .offset(offset)
        .limit(limit)
    ).all()
    return recipes


@router.get("/user/", response_model=list[RecipeCard])
def get_users_recipes(
    current_user: CurrentUserDep,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
):
    recipes = session.exec(
        select(Recipe)
        .where(Recipe.created_by == current_user)
        .options(selectinload(Recipe.cover_image))
        .order_by(Recipe.created_on.desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return recipes


@router.get("/user/count/", response_model=CountResponse)
def get_users_recipe_count(current_user: CurrentUserDep, session: SessionDep):
    count = session.exec(
        select(func.count())
        .select_from(Recipe)
        .where(Recipe.created_by == current_user)
    ).one()
    return CountResponse(count=count)


@router.get("/user/recent/", response_model=list[RecipeCard])
def get_users_recently_added_recipes(current_user: CurrentUserDep, session: SessionDep):
    recipes = session.exec(
        select(Recipe)
        .where(Recipe.created_by == current_user)
        .options(selectinload(Recipe.cover_image))
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
    recipe = session.exec(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(
            selectinload(Recipe.cover_image),
            selectinload(Recipe.created_by),
            selectinload(Recipe.ingredients),
        )
    ).first()
    if not recipe:
        raise HTTPException(
            status_code=404, detail=f"Recipe with id {recipe_id} not found."
        )
    return recipe


@router.get("/search/", response_model=list[RecipeCard])
def search_recipes(
    searchText: str,
    current_user: CurrentUserDep,
    session: SessionDep,
    offset=0,
    limit: Annotated[int, Query(le=100)] = 50,
):
    if not searchText:
        recipes = session.exec(
            select(Recipe)
            .where(Recipe.public)
            .options(selectinload(Recipe.cover_image))
            .limit(25)
        ).all()
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
        .options(selectinload(Recipe.cover_image))
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

    db_recipe = Recipe.model_validate(rec_dict)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


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
