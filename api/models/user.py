from sqlmodel import Field, Relationship, SQLModel


# from api.models.permission import Permission


class User(SQLModel, table=True):
    id: int | None = Field(default=None, index=True, primary_key=True)
    avatar_url: str | None
    username: str
    email: str
    display_name: str
    admin: bool = False
    disabled: bool = False
    google_user_id: str | None = None

    tokens: list["Token"] = Relationship(back_populates="user")  # type: ignore # noqa: F821

    # permissions: list["Permission"] = Relationship()
