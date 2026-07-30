import {
  RECIPE_PAGE_SIZE,
  fetchRecipe,
  fetchRecipeCount,
  fetchRecipePage,
  searchRecipes
} from "@/api/recipes";
import type { RecipeCard } from "@/types";
import { keepPreviousData, useInfiniteQuery, useQuery } from "@tanstack/react-query";

function byNewest(a: RecipeCard, b: RecipeCard): number {
  return new Date(b.created_on).getTime() - new Date(a.created_on).getTime();
}

/** Paged personal recipe list (newest first), with load-more support. */
export function useRecipeList() {
  return useInfiniteQuery({
    queryKey: ["recipes", "list"],
    queryFn: ({ pageParam }) => fetchRecipePage(pageParam),
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages) =>
      lastPage.length >= RECIPE_PAGE_SIZE
        ? allPages.reduce((n, page) => n + page.length, 0)
        : undefined,
    select: (data) => [...data.pages.flat()].sort(byNewest)
  });
}

export function useRecipeCount() {
  return useQuery({
    queryKey: ["recipes", "count"],
    queryFn: fetchRecipeCount,
    select: (r) => r.count
  });
}

export function useRecipeSearch(searchText: string) {
  const trimmed = searchText.trim();
  return useQuery({
    queryKey: ["recipes", "search", trimmed],
    queryFn: () => searchRecipes(trimmed),
    enabled: trimmed.length > 0,
    placeholderData: keepPreviousData
  });
}

export function useRecipe(recipeId: number | string | undefined) {
  return useQuery({
    queryKey: ["recipes", "detail", String(recipeId)],
    queryFn: () => fetchRecipe(recipeId!),
    enabled: recipeId !== undefined && recipeId !== null && recipeId !== ""
  });
}
