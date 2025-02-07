from sqlmodel import SQLModel


class IngredientDetail(SQLModel):
    id: int
    name: str
    amount: float
    units: str
    details: str | None

    recipe_id: int


class IngredientCreate(SQLModel):
    name: str
    amount: float
    units: str
    details: str | None

    recipe_id: int


class IngredientUpdate(SQLModel):
    name: str | None
    amount: float | None
    units: str | None
    details: str | None
