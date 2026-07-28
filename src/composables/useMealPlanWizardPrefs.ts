import { emptyWizardPrefs, type MealPlanWizardPrefs } from "@/types";
import { useLocalStorage } from "@vueuse/core";
import { computed } from "vue";

const STORAGE_KEY = "meal-plan-wizard-prefs-v1";

/** Persist sticky wizard inputs (goals / diet / servings / cuisine). */
export function useMealPlanWizardPrefs() {
  const stored = useLocalStorage<Partial<MealPlanWizardPrefs>>(STORAGE_KEY, {});

  const prefs = computed<MealPlanWizardPrefs>({
    get: () => ({
      ...emptyWizardPrefs(),
      ...stored.value,
      // Ephemeral-ish fields still restore if present, but preferred ingredients
      // often change week to week — still useful to remember last entry.
      preferred_ingredients: stored.value.preferred_ingredients ?? "",
      extra_notes: stored.value.extra_notes ?? ""
    }),
    set: (value) => {
      stored.value = {
        goals: value.goals,
        dietary_restrictions: value.dietary_restrictions,
        preferred_ingredients: value.preferred_ingredients,
        max_cook_minutes: value.max_cook_minutes,
        servings: value.servings,
        cuisine_notes: value.cuisine_notes,
        extra_notes: value.extra_notes
      };
    }
  });

  function save(next: MealPlanWizardPrefs) {
    prefs.value = next;
  }

  return { prefs, save, stored };
}
