from datetime import datetime
from enum import Enum
from sqlmodel import Relationship, SQLModel, Field

from api.core.timezone_handler import UTCDateTime


# Create common Base to be used by all models
class BaseDbModel(SQLModel):
    __abstract__ = True


class BaseIndexedDbModel(BaseDbModel):
    __abstract__ = True
    id: int | None = Field(default=None, index=True, primary_key=True)


class User_Permission(BaseDbModel, table=True):
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    permission_id: int = Field(
        default=None, foreign_key="permission.id", primary_key=True
    )


class User(BaseIndexedDbModel, table=True):
    avatar_url: str | None
    username: str
    email: str
    display_name: str
    admin: bool = False
    disabled: bool = False
    google_user_id: str | None = None
    last_login: datetime | None = Field(sa_type=UTCDateTime)

    tokens: list["Token"] = Relationship(back_populates="user")
    permissions: list["Permission"] = Relationship(link_model=User_Permission)


class TokenType(Enum):
    Access = 10


class Token(BaseIndexedDbModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    access_token: str
    token_type: TokenType

    user: "User" = Relationship(back_populates="tokens")


class Permission(BaseIndexedDbModel, table=True):
    name: str


class Recipe(BaseIndexedDbModel, table=True):
    created_by_id: int = Field(foreign_key="user.id")
    created_on: datetime = Field(sa_type=UTCDateTime)
    name: str
    description: str
    instructions: str
    notes: str | None
    public: bool = False

    created_by: "User" = Relationship()
    ingredients: list["Ingredient"] = Relationship(back_populates="recipe")


class Ingredient(BaseIndexedDbModel, table=True):
    name: str
    amount: float
    units: str
    details: str | None
    recipe_id: int = Field(foreign_key="recipe.id")

    recipe: "Recipe" = Relationship(back_populates="ingredients")


class PlannedRecipe(BaseIndexedDbModel, table=True):
    recipe_id: int = Field(foreign_key="recipe.id")
    created_by_id: int = Field(foreign_key="user.id")
    created_on: datetime = Field(sa_type=UTCDateTime)
    planned_for: datetime = Field(sa_type=UTCDateTime)

    created_by: User = Relationship()
    recipe: Recipe = Relationship()
