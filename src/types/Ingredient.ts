import type { RecipeSlim } from "./Recipe";

export interface IngredientSlim {
  id: number;
  name: string;
  amount: number;
  units: string;
  details?: string;
}

export interface IngredientDetail extends IngredientSlim {
  recipe: RecipeSlim;
}
