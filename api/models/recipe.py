from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship

from api.models import Base
from api.models.ingredient import Ingredient
from api.models.user import User


class Recipe(Base, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    created_by_id: int = Field(sa_column=Column(ForeignKey("user.id")))
    created_on: datetime
    name: str
    description: str
    instructions: str
    notes: str | None
    public: bool = False

    created_by: User = Relationship()
    ingredients: list["Ingredient"] = Relationship()
