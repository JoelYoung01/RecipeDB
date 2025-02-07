from sqlmodel import Field

from api.models import Base


class Permission(Base, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    name: str
