import type { IngredientSlim } from "./Ingredient";
import type { UploadSlim } from "./Upload";
import type { UserResponse } from "./User";

export interface RecipeSlim {
  id: number;
  name: string;
  description: string;
  instructions: string;
  notes?: string;
  created_on: string;
  created_by_id: number;
  public: boolean;
  prep_time?: number;
  cover_image_id?: number;
}

export interface RecipeDetail extends RecipeSlim {
  created_by: UserResponse;
  ingredients: IngredientSlim[];
  cover_image?: UploadSlim;
}

export interface RecipeDashboard extends RecipeSlim {
  cover_image?: UploadSlim;
}

export interface RecipeCreate {
  name: string;
  description: string;
  instructions: string;
  notes?: string;
  created_on: string;
  public: boolean;
  prep_time?: number;
  cover_image_id?: number;
}
