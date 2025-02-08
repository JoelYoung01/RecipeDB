from enum import Enum
from sqlmodel import Field, Relationship

from api.models import BaseIndexedDbModel


class TokenType(Enum):
    Access = 10


class Token(BaseIndexedDbModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    access_token: str
    token_type: TokenType

    user: "User" = Relationship(back_populates="tokens")  # type: ignore  # noqa: F821
