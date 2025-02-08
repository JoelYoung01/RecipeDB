from datetime import datetime
from sqlmodel import Field, Relationship

from api.core.timezone_handler import UTCDateTime
from api.models import BaseIndexedDbModel
from api.models.permission import Permission, User_Permission


# from api.models.permission import Permission


class User(BaseIndexedDbModel, table=True):
    avatar_url: str | None
    username: str
    email: str
    display_name: str
    admin: bool = False
    disabled: bool = False
    google_user_id: str | None = None
    last_login: datetime | None = Field(sa_type=UTCDateTime)

    tokens: list["Token"] = Relationship(back_populates="user")  # type: ignore # noqa: F821
    permissions: list["Permission"] = Relationship(link_model=User_Permission)
