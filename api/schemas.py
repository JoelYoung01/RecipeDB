from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, computed_field


class HealthResponse(BaseModel):
    status: str
    version: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    admin: bool
    disabled: bool
    email_verified: bool = False
    avatar_url: str | None = None
    last_login: datetime | None = None


class UserPublic(BaseModel):
    id: int
    display_name: str
    avatar_url: str | None = None


class GoogleLoginPayload(BaseModel):
    credential: str


class RegisterPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=1024)
    display_name: str = Field(min_length=1, max_length=100)


class PasswordLoginPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class VerifyEmailPayload(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=4, max_length=12)


class ResendVerificationPayload(BaseModel):
    email: EmailStr


class AuthRedirectResponse(BaseModel):
    """Server-directed next step for the SPA (e.g. email verification)."""

    code: str
    message: str
    redirect_to: str
    email: str | None = None
    # Only populated when ENVIRONMENT=development so local testing can skip SMTP.
    dev_otp: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    user: UserResponse


class UploadFileResponse(BaseModel):
    id: int
    name: str
    file_path: str
    created_on: datetime
    created_by_id: int

    @computed_field
    @property
    def url(self) -> str:
        return f"/uploads/{self.file_path}"


class RecipeSlim(BaseModel):
    id: int
    name: str
    description: str
    instructions: str
    notes: str | None = None
    created_on: datetime
    created_by_id: int
    public: bool
    prep_time: float | None = None
    cover_image_id: int | None = None


class RecipeDetail(RecipeSlim):
    created_by: "UserResponse"
    ingredients: list["IngredientDetail"]
    cover_image: UploadFileResponse | None


class RecipeDashboard(RecipeSlim):
    cover_image: UploadFileResponse | None


class RecipeCreate(BaseModel):
    name: str
    description: str
    instructions: str
    notes: str | None = None
    public: bool
    prep_time: float | None = None
    cover_image_id: int | None = None


class RecipeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    notes: str | None = None
    created_on: datetime | None = None
    public: bool | None = None
    prep_time: float | None = None
    cover_image_id: int | None = None


class TimeFrameRequest(BaseModel):
    start: datetime
    end: datetime


class PlannedRecipeSlim(BaseModel):
    id: int
    created_by_id: int
    created_on: datetime
    planned_for: datetime


class PlannedRecipeDetail(PlannedRecipeSlim):
    created_by: "UserResponse"
    recipe: "RecipeDashboard"


class PlannedRecipeCreate(BaseModel):
    recipe_id: int
    planned_for: str


class PlannedRecipeUpdate(BaseModel):
    recipe_id: int | None = None
    planned_for: str | None = None


class IngredientSlim(BaseModel):
    id: int
    name: str
    amount: float | None = None
    units: str | None = None
    details: str | None = None


class IngredientDetail(IngredientSlim):
    recipe: "RecipeSlim"


class IngredientCreate(BaseModel):
    name: str
    amount: float | None = None
    units: str | None = None
    details: str | None = None
    recipe_id: int


class IngredientUpdate(BaseModel):
    name: str | None = None
    amount: float | None = None
    units: str | None = None
    details: str | None = None


class UserUpdate(BaseModel):
    display_name: str | None = None
