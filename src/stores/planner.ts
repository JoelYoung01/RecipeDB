import { endOfDay } from "@/lib/media";
import type { PlannedRecipeDetail } from "@/types";
import { post } from "@/utils";
import { defineStore } from "pinia";
import { ref } from "vue";

function rangeKey(start: Date, end: Date) {
  return `${start.toISOString()}|${end.toISOString()}`;
}

/** True when [coverStart, coverEnd] fully contains [start, end]. */
function covers(coverStart: Date, coverEnd: Date, start: Date, end: Date) {
  return coverStart.getTime() <= start.getTime() && coverEnd.getTime() >= endOfDay(end).getTime();
}

export const usePlannerStore = defineStore("planner", () => {
  const plannedRecipes = ref<PlannedRecipeDetail[]>([]);
  const loading = ref(false);
  const refreshing = ref(false);
  /** Exact key of the last successful fetch (start|end ISO). */
  const loadedKey = ref<string | null>(null);
  const loadedStart = ref<Date | null>(null);
  const loadedEnd = ref<Date | null>(null);
  /** Bumps on every invalidate/reset so views can react even when arrays look similar. */
  const revision = ref(0);
  let inflight: Promise<void> | null = null;
  let inflightKey: string | null = null;

  async function ensureRange(start: Date, end: Date, opts?: { force?: boolean }) {
    const key = rangeKey(start, end);
    if (!opts?.force) {
      if (loadedKey.value === key) return;
      // Reuse a wider cache (e.g. Planner’s 8 weeks) for Home’s 3-week window.
      if (
        loadedStart.value &&
        loadedEnd.value &&
        covers(loadedStart.value, loadedEnd.value, start, end)
      ) {
        return;
      }
    }
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
        loadedStart.value = start;
        loadedEnd.value = endOfDay(end);
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
    loadedStart.value = null;
    loadedEnd.value = null;
    revision.value += 1;
  }

  function reset() {
    plannedRecipes.value = [];
    loading.value = false;
    refreshing.value = false;
    invalidate();
  }

  return {
    plannedRecipes,
    loading,
    refreshing,
    loadedKey,
    revision,
    ensureRange,
    plansInRange,
    invalidate,
    reset
  };
});
