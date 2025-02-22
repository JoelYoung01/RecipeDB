from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import MetaData
from sqlmodel import Relationship, SQLModel, Field

from api.core.timezone_handler import UTCDateTime


# Create common Base to be used by all models
class BaseDbModel(SQLModel):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_`%(constraint_name)s`",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

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
    avatar_url: str | None = None
    username: str
    email: str
    display_name: str
    admin: bool = False
    disabled: bool = False
    google_user_id: str | None = None
    last_login: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), sa_type=UTCDateTime
    )

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


class Upload(BaseIndexedDbModel, table=True):
    created_by_id: int = Field(foreign_key="user.id")
    created_on: datetime = Field(sa_type=UTCDateTime)
    file_path: str

    created_by: "User" = Relationship()


class Recipe(BaseIndexedDbModel, table=True):
    created_by_id: int = Field(foreign_key="user.id")
    created_on: datetime = Field(sa_type=UTCDateTime)
    name: str
    description: str
    instructions: str
    notes: str | None
    public: bool = False
    prep_time: float | None = None
    cover_image_id: int | None = Field(foreign_key="upload.id", default=None)

    created_by: "User" = Relationship()
    ingredients: list["Ingredient"] = Relationship(
        back_populates="recipe",
        cascade_delete=True,
    )
    planned: list["PlannedRecipe"] = Relationship(back_populates="recipe")
    cover_image: "Upload" = Relationship()


class Ingredient(BaseIndexedDbModel, table=True):
    created_by_id: int = Field(foreign_key="user.id")
    created_on: datetime = Field(sa_type=UTCDateTime)
    name: str
    amount: float | None = None
    units: str | None = None
    details: str | None = None
    recipe_id: int = Field(foreign_key="recipe.id")

    recipe: "Recipe" = Relationship(back_populates="ingredients")
    created_by: "User" = Relationship()


class PlannedRecipe(BaseIndexedDbModel, table=True):
    recipe_id: int = Field(foreign_key="recipe.id")
    created_by_id: int = Field(foreign_key="user.id")
    created_on: datetime = Field(sa_type=UTCDateTime)
    planned_for: datetime = Field(sa_type=UTCDateTime)

    created_by: "User" = Relationship()
    recipe: "Recipe" = Relationship()
