export interface GroceryQuantity {
  amount: number | null;
  units: string | null;
}

export interface GroceryRecipeRef {
  id: number;
  name: string;
}

export interface GroceryItem {
  key: string;
  name: string;
  category: string;
  quantities: GroceryQuantity[];
  quantity_display: string;
  recipes: GroceryRecipeRef[];
  recipe_titles: string;
  source_ingredient_ids: number[];
  dismissed: boolean;
  deleted: boolean;
}

export interface GroceryListResponse {
  window_start: string;
  window_end: string;
  items: GroceryItem[];
}
