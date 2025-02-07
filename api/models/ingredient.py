from sqlalchemy import Column, ForeignKey
from sqlmodel import Field

from api.models import Base


class Ingredient(Base, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    name: str
    amount: float
    units: str
    details: str | None

    recipe_id: int = Field(sa_column=Column(ForeignKey("recipe.id")))
