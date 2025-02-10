import type { RecipeSlim } from "./Recipe";
import type { UserResponse } from "./User";

export interface PlannedRecipeSlim {
  id: number;
  created_by_id: number;
  created_on: string;
  planned_for: string;
}

export interface PlannedRecipeDetail extends PlannedRecipeSlim {
  created_by: UserResponse;
  recipe: RecipeSlim;
}
