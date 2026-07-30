import { fetchPlansBetween } from "@/api/planner";
import { toDateKey } from "@/lib/dates";
import type { PlannedRecipeDetail } from "@/types";
import { useQuery } from "@tanstack/react-query";

/** Planned meals in [start, end], keyed by local date for cache reuse. */
export function usePlansRange(start: Date, end: Date) {
  return useQuery({
    queryKey: ["plans", toDateKey(start), toDateKey(end)],
    queryFn: () => fetchPlansBetween(start, end)
  });
}

/** Date key of a plan — matches the web app (leading date of the ISO string). */
export function planDayKey(plan: PlannedRecipeDetail): string {
  return plan.planned_for.slice(0, 10);
}

/** Group plans by YYYY-MM-DD of planned_for. */
export function groupPlansByDay(
  plans: PlannedRecipeDetail[] | undefined
): Map<string, PlannedRecipeDetail[]> {
  const map = new Map<string, PlannedRecipeDetail[]>();
  for (const plan of plans ?? []) {
    const key = planDayKey(plan);
    const bucket = map.get(key);
    if (bucket) bucket.push(plan);
    else map.set(key, [plan]);
  }
  return map;
}
