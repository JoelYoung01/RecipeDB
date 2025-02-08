from sqlmodel import Field
from api.models import BaseIndexedDbModel, BaseDbModel


class Permission(BaseIndexedDbModel, table=True):
    name: str


class User_Permission(BaseDbModel, table=True):
    user_id: int = Field(default=None, foreign_key="user.id", primary_key=True)
    permission_id: int = Field(
        default=None, foreign_key="permission.id", primary_key=True
    )
