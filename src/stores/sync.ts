import { useGroceryStore } from "@/stores/grocery";
import { usePlannerStore } from "@/stores/planner";
import { useRecipesStore } from "@/stores/recipes";

/**
 * Cross-store invalidation for client caches kept alive across tabs.
 * Call after any mutation that should refresh Home / Planner / Grocery / Recipes.
 */

/** Planned meals changed (manual assign/remove or wizard commit). */
export function syncAfterPlanMutation(opts?: { recipesChanged?: boolean }) {
  usePlannerStore().invalidate();
  useGroceryStore().invalidate();
  if (opts?.recipesChanged) {
    useRecipesStore().invalidate();
  }
}

/** Recipe create / update / delete — list + grocery may both shift. */
export function syncAfterRecipeMutation() {
  useRecipesStore().invalidate();
  useGroceryStore().invalidate();
}

/** Clear all domain caches (e.g. on logout). */
export function resetClientData() {
  usePlannerStore().reset();
  useGroceryStore().reset();
  useRecipesStore().reset();
}
