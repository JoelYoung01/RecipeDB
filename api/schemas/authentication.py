from pydantic import BaseModel

from api.schemas.user import UserResponse


class GoogleLoginPayload(BaseModel):
    credential: str


class TokenResponse(BaseModel):
    access_token: str
    user: UserResponse
