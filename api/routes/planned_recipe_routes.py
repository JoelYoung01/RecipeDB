from fastapi import APIRouter, Depends
from sqlmodel import select

from api.core.authentication import CurrentUserDep, verify_access_token
from api.core.database import SessionDep
from api.models import PlannedRecipe
from api.schemas import PlannedRecipeDetail, TimeFrameRequest

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


# TODO: Add post / patch / delete routes here
