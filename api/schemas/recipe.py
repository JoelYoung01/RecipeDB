from datetime import datetime

from sqlmodel import SQLModel

from api.models import User
from api.schemas.ingredient import IngredientDetail


class RecipeSlim(SQLModel):
    id: int | None
    name: str
    description: str
    instructions: str
    notes: str | None
    created_on: datetime
    public: bool


class RecipeDetail(SQLModel):
    id: int | None
    name: str
    description: str
    instructions: str
    notes: str | None
    created_on: datetime
    public: bool

    created_by: User
    ingredients: list["IngredientDetail"]


class RecipeCreate(SQLModel):
    name: str
    description: str
    instructions: str
    notes: str | None
    created_on: datetime
    public: bool

    created_by: User


class RecipeUpdate(SQLModel):
    name: str | None
    description: str | None
    instructions: str | None
    notes: str | None
    created_on: datetime | None
    public: bool | None

    created_by: User | None
