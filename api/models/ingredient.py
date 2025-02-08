from sqlmodel import Field

from api.models import BaseIndexedDbModel


class Ingredient(BaseIndexedDbModel, table=True):
    name: str
    amount: float
    units: str
    details: str | None

    recipe_id: int = Field(foreign_key="recipe.id")
