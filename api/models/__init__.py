# ruff: noqa: F401, E402
from sqlmodel import SQLModel, Field


# Create common Base to be used by all models
class BaseDbModel(SQLModel):
    __abstract__ = True


class BaseIndexedDbModel(BaseDbModel):
    __abstract__ = True
    id: int | None = Field(default=None, index=True, primary_key=True)


# Models in this app.
# Must be imported so that Alembic can scan the Base class metadata to generate migrations.
from api.models.authentication import Token
from api.models.user import User
from api.models.permission import Permission
from api.models.ingredient import Ingredient
from api.models.recipe import Recipe
from api.models.planned_recipe import PlannedRecipe
