from datetime import datetime
from enum import Enum

from pydantic import computed_field
from sqlmodel import Field, Relationship, SQLModel

from api.models.requirement import Requirement, RequirementDetailSchema
from api.models.app_submission import AppSubmission


class AppDefinitionStatus(Enum):
    Active = 10
    Complete = 20
    Future = 30


class AppDefinition(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    name: str
    start_date: datetime
    due_date: datetime
    description: str

    requirements: list["Requirement"] = Relationship()
    submissions: list["AppSubmission"] = Relationship()

    @computed_field
    @property
    def status(self) -> AppDefinitionStatus:
        if self.start_date > datetime.now():
            return AppDefinitionStatus.Future
        elif self.due_date < datetime.now():
            return AppDefinitionStatus.Complete
        else:
            return AppDefinitionStatus.Active


class AppDefinitionDashboardSchema(SQLModel):
    id: int
    name: str
    start_date: datetime
    due_date: datetime
    description: str

    @computed_field
    @property
    def status(self) -> AppDefinitionStatus:
        if self.start_date > datetime.now():
            return AppDefinitionStatus.Future
        elif self.due_date < datetime.now():
            return AppDefinitionStatus.Complete
        else:
            return AppDefinitionStatus.Active


class AppDefinitionDetailSchema(SQLModel):
    id: int
    name: str
    start_date: datetime
    due_date: datetime
    description: str
    requirements: list[RequirementDetailSchema]


class AppDefinitionCreateSchema(SQLModel):
    name: str
    start_date: datetime
    due_date: datetime
    description: str


class AppDefinitionUpdateSchema(SQLModel):
    name: str | None = None
    start_date: datetime | None = None
    due_date: datetime | None = None
    description: str | None = None
