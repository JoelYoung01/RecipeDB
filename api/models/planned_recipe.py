from datetime import datetime

from sqlmodel import Field, Relationship

from api.core.timezone_handler import UTCDateTime
from api.models import BaseIndexedDbModel
from api.models.ingredient import Ingredient
from api.models.user import User


class Recipe(BaseIndexedDbModel, table=True):
    created_by_id: int = Field(foreign_key="user.id")
    created_on: datetime = Field(sa_type=UTCDateTime)

    planned_for: datetime = Field(sa_type=UTCDateTime)

    created_by: User = Relationship()
    ingredients: list["Ingredient"] = Relationship()
