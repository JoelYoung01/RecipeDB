import type { IngredientSlim } from "./Ingredient";
import type { UserResponse } from "./User";

export interface RecipeSlim {
  id: number;
  name: string;
  description: string;
  instructions: string;
  notes?: string;
  created_on: string;
  public: boolean;
  prep_time?: number;
  cover_image?: string;
}

export interface RecipeDetail extends RecipeSlim {
  created_by: UserResponse;
  ingredients: IngredientSlim[];
}

export interface RecipeCreate {
  name: string;
  description: string;
  instructions: string;
  notes?: string;
  created_on: string;
  public: boolean;
  prep_time?: number;
  cover_image?: string;
}
