from sqlalchemy import Column, ForeignKey
from sqlmodel import Field, SQLModel


class Requirement(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    name: str
    description: str
    app_definition_id: int = Field(sa_column=Column(ForeignKey("appdefinition.id")))


class RequirementDetailSchema(SQLModel):
    id: int
    name: str
    description: str
    app_definition_id: int


class RequirementCreateSchema(SQLModel):
    name: str
    description: str
    app_definition_id: int


class RequirementUpdateSchema(SQLModel):
    name: str | None = None
    description: str | None = None
    app_definition_id: int | None = None
