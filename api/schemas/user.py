from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    admin: bool
    disabled: bool
    avatar_url: str | None
