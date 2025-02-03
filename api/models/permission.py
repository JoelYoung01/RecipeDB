from sqlmodel import Field, SQLModel


class Permission(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    name: str
