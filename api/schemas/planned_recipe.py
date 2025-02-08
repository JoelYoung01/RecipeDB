from datetime import datetime

from pydantic import BaseModel

from api.schemas.recipe import RecipeSlim
from api.schemas.user import UserResponse


class TimeFrameRequest(BaseModel):
    start: datetime
    end: datetime


class PlannedRecipeSlim(BaseModel):
    id: int
    created_by_id: int
    created_on: datetime
    planned_for: datetime


class PlannedRecipeDetail(PlannedRecipeSlim):
    created_by: UserResponse
    recipe: RecipeSlim
