from datetime import UTC, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlmodel import select

from api.core.authentication import CurrentUserDep, verify_access_token
from api.core.database import SessionDep
from api.models import PlannedRecipe
from api.schemas import (
    PlannedRecipeCreate,
    PlannedRecipeDetail,
    PlannedRecipeUpdate,
    TimeFrameRequest,
)

router = APIRouter(
    prefix="/planned-recipe",
    dependencies=[Depends(verify_access_token)],
    tags=["Planned Recipe"],
)


@router.post("/time-frame/", response_model=list[PlannedRecipeDetail])
def get_recipes_in_time_frame(
    body: TimeFrameRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    recipes = session.exec(
        select(PlannedRecipe).where(
            PlannedRecipe.created_by == current_user,
            PlannedRecipe.planned_for >= body.start,
            PlannedRecipe.planned_for <= body.end,
        )
    ).all()
    return recipes


@router.post("/", response_model=PlannedRecipeDetail)
def create_planned_recipe(
    planned_recipe: PlannedRecipeCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    pr_dict = planned_recipe.model_dump()
    pr_dict["created_by_id"] = current_user.id
    pr_dict["created_on"] = datetime.now(UTC)

    db_planned_recipe = PlannedRecipe.model_validate(pr_dict)
    session.add(db_planned_recipe)
    session.commit()
    session.refresh(db_planned_recipe)
    return db_planned_recipe


@router.put("/{planned_recipe_id}", response_model=PlannedRecipeDetail)
def update_planned_recipe(
    planned_recipe_id: int,
    planned_recipe: PlannedRecipeUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    db_planned_recipe = session.get(PlannedRecipe, planned_recipe_id)
    if not db_planned_recipe:
        raise HTTPException(status_code=404, detail="Planned recipe not found")
    if db_planned_recipe.created_by != current_user:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this planned recipe"
        )

    update_stmt = (
        update(PlannedRecipe)
        .where(PlannedRecipe.id == planned_recipe_id)
        .values(**planned_recipe.model_dump(exclude_unset=True))
        .execution_options(synchronize_session="fetch")
    )
    session.exec(update_stmt)
    session.commit()
    session.refresh(db_planned_recipe)
    return db_planned_recipe


@router.delete("/{planned_recipe_id}")
def delete_planned_recipe(
    planned_recipe_id: int,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    db_planned_recipe = session.get(PlannedRecipe, planned_recipe_id)
    if not db_planned_recipe:
        raise HTTPException(status_code=404, detail="Planned recipe not found")
    if db_planned_recipe.created_by != current_user:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this planned recipe"
        )

    session.delete(db_planned_recipe)
    session.commit()
    return {"message": "Planned recipe deleted successfully"}
