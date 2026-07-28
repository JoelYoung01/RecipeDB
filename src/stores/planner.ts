import { endOfDay } from "@/lib/media";
import type { PlannedRecipeDetail } from "@/types";
import { post } from "@/utils";
import { defineStore } from "pinia";
import { ref } from "vue";

function rangeKey(start: Date, end: Date) {
  return `${start.toISOString()}|${end.toISOString()}`;
}

export const usePlannerStore = defineStore("planner", () => {
  const plannedRecipes = ref<PlannedRecipeDetail[]>([]);
  const loading = ref(false);
  const refreshing = ref(false);
  const loadedKey = ref<string | null>(null);
  let inflight: Promise<void> | null = null;
  let inflightKey: string | null = null;

  async function ensureRange(start: Date, end: Date, opts?: { force?: boolean }) {
    const key = rangeKey(start, end);
    if (loadedKey.value === key && !opts?.force) return;
    if (inflight && inflightKey === key && !opts?.force) return inflight;

    const soft = plannedRecipes.value.length > 0;
    if (soft) refreshing.value = true;
    else loading.value = true;

    inflightKey = key;
    inflight = (async () => {
      try {
        plannedRecipes.value = await post<PlannedRecipeDetail[]>("/planned-recipe/time-frame/", {
          start: start.toISOString(),
          end: endOfDay(end).toISOString()
        });
        loadedKey.value = key;
      } finally {
        loading.value = false;
        refreshing.value = false;
        inflight = null;
        inflightKey = null;
      }
    })();

    return inflight;
  }

  function plansInRange(start: Date, end: Date) {
    const startMs = start.getTime();
    const endMs = endOfDay(end).getTime();
    return plannedRecipes.value.filter((p) => {
      const t = new Date(p.planned_for).getTime();
      return t >= startMs && t <= endMs;
    });
  }

  function invalidate() {
    loadedKey.value = null;
  }

  return {
    plannedRecipes,
    loading,
    refreshing,
    loadedKey,
    ensureRange,
    plansInRange,
    invalidate
  };
});
