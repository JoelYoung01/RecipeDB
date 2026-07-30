import { endOfDay } from "@/lib/dates";
import type { PlannedRecipeDetail } from "@/types";
import { del, post } from "./client";

/** Planned meals in [start, endOfDay(end)] (inclusive). */
export function fetchPlansBetween(start: Date, end: Date): Promise<PlannedRecipeDetail[]> {
  return post<PlannedRecipeDetail[]>("/planned-recipe/time-frame/", {
    start: start.toISOString(),
    end: endOfDay(end).toISOString()
  });
}

export function createPlan(recipeId: number, plannedFor: Date): Promise<PlannedRecipeDetail> {
  return post<PlannedRecipeDetail>("/planned-recipe/", {
    recipe_id: recipeId,
    planned_for: plannedFor.toISOString()
  });
}

export function deletePlan(plannedRecipeId: number): Promise<void> {
  return del(`/planned-recipe/${plannedRecipeId}`);
}
