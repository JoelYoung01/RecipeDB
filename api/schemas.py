from datetime import datetime
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str
    admin: bool
    disabled: bool
    avatar_url: str | None


class GoogleLoginPayload(BaseModel):
    credential: str


class TokenResponse(BaseModel):
    access_token: str
    user: UserResponse


class UploadFileResponse(BaseModel):
    filename: str
    path: str


class RecipeSlim(BaseModel):
    id: int
    name: str
    description: str
    instructions: str
    notes: str | None
    created_on: datetime
    public: bool
    prep_time: float | None
    cover_image: str | None


class RecipeDetail(RecipeSlim):
    created_by: "UserResponse"
    ingredients: list["IngredientDetail"]


class RecipeCreate(BaseModel):
    name: str
    description: str
    instructions: str
    notes: str | None
    created_on: datetime
    public: bool
    prep_time: float | None
    cover_image: str | None


class RecipeUpdate(BaseModel):
    name: str | None
    description: str | None
    instructions: str | None
    notes: str | None
    created_on: datetime | None
    public: bool | None
    prep_time: float | None
    cover_image: str | None


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
    recipe: "RecipeSlim"


class IngredientSlim(BaseModel):
    id: int
    name: str
    amount: float
    units: str
    details: str | None


class IngredientDetail(IngredientSlim):
    recipe: "RecipeSlim"


class IngredientCreate(BaseModel):
    name: str
    amount: float
    units: str
    details: str | None
    recipe_id: int


class IngredientUpdate(BaseModel):
    name: str | None
    amount: float | None
    units: str | None
    details: str | None
