from datetime import datetime
from pydantic import BaseModel, computed_field


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    admin: bool
    disabled: bool
    avatar_url: str | None = None
    last_login: datetime | None = None


class UserPublic(BaseModel):
    id: int
    display_name: str
    avatar_url: str | None = None


class GoogleLoginPayload(BaseModel):
    credential: str


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
