from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, computed_field


class HealthResponse(BaseModel):
    status: str
    version: str


class MigrationUpgradeResponse(BaseModel):
    previous_revision: str | None
    current_revision: str | None
    head_revision: str | None
    upgraded: bool
    message: str


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


class AppleLoginPayload(BaseModel):
    identity_token: str
    # Apple shares the user's name only on FIRST authorization, and only with
    # the client — it is never inside the identity token.
    full_name: str | None = None


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


class RecipeCoverIngredientHint(BaseModel):
    name: str | None = None


class RecipeCoverGenerateRequest(BaseModel):
    """Fields used to search/generate a cover; works before a recipe is saved."""

    name: str = Field(min_length=1)
    description: str | None = None
    ingredients: list[RecipeCoverIngredientHint] = Field(default_factory=list)


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


class RecipeCard(BaseModel):
    """List/card payload — omits instructions/notes for faster first paint."""

    id: int
    name: str
    description: str
    created_on: datetime
    created_by_id: int
    public: bool
    prep_time: float | None = None
    cover_image_id: int | None = None
    cover_image: UploadFileResponse | None = None


class CountResponse(BaseModel):
    count: int


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
    recipe: "RecipeCard"


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


class GroceryQuantity(BaseModel):
    amount: float | None = None
    units: str | None = None


class GroceryRecipeRef(BaseModel):
    id: int
    name: str


class GroceryItem(BaseModel):
    key: str
    name: str
    category: str
    quantities: list[GroceryQuantity]
    quantity_display: str
    recipes: list[GroceryRecipeRef]
    recipe_titles: str
    source_ingredient_ids: list[int]
    dismissed: bool = False
    deleted: bool = False


class GroceryListResponse(BaseModel):
    window_start: datetime
    window_end: datetime
    items: list[GroceryItem]


class GrocerySummaryResponse(BaseModel):
    window_start: datetime
    window_end: datetime
    active_count: int


class GroceryItemStateUpdate(BaseModel):
    item_key: str
    status: str | None = None  # "dismissed" | "deleted" | null to clear


# --- Meal plan wizard ---


class MealPlanWizardPrefs(BaseModel):
    goals: str = ""
    dietary_restrictions: str = ""
    preferred_ingredients: str = ""
    max_cook_minutes: int | None = None
    servings: int | None = None
    cuisine_notes: str = ""
    extra_notes: str = ""


class MealPlanWizardCreate(BaseModel):
    days: list[str] = Field(min_length=1)
    prefs: MealPlanWizardPrefs | None = None


class MealPlanWizardDaysUpdate(BaseModel):
    days: list[str] = Field(min_length=1)


class MealPlanWizardIdea(BaseModel):
    id: str
    title: str
    justification: str = ""


class MealPlanWizardBuiltRecipe(BaseModel):
    idea_id: str
    title: str
    description: str
    instructions: str
    notes: str | None = None
    prep_time: float | None = None
    ingredients: list[dict] = Field(default_factory=list)
    source: str = "generated"
    existing_recipe_id: int | None = None
    created_recipe_id: int | None = None


class MealPlanWizardProgressEvent(BaseModel):
    stage: str
    status: str
    message: str
    progress: float
    data: dict | None = None


class MealPlanWizardSessionResponse(BaseModel):
    id: str
    days: list[str]
    prefs: MealPlanWizardPrefs
    step: str
    idea_target_count: int
    select_count: int
    ideas: list[MealPlanWizardIdea]
    selected_idea_ids: list[str]
    built_recipes: list[MealPlanWizardBuiltRecipe]
    progress_log: list[MealPlanWizardProgressEvent]
    stubbed: bool = True


class MealPlanWizardSelectRequest(BaseModel):
    idea_ids: list[str]


class MealPlanWizardRefineRequest(BaseModel):
    refinement: str | None = None
    """Optional idea ids to regenerate on a refine turn. Omit to rebuild all."""
    idea_ids: list[str] | None = None


class MealPlanWizardRewindRequest(BaseModel):
    to_step: str


class MealPlanWizardDayAssignment(BaseModel):
    day: str
    idea_id: str


class MealPlanWizardCommitRequest(BaseModel):
    assignments: list[MealPlanWizardDayAssignment] | None = None
