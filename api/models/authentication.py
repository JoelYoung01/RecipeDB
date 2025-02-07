from enum import Enum
from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, Relationship

from . import Base


class TokenType(Enum):
    Access = 10


class Token(Base, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    user_id: int = Field(sa_column=Column(ForeignKey("user.id")))
    access_token: str
    token_type: TokenType

    user: "User" = Relationship(back_populates="tokens")  # type: ignore  # noqa: F821
