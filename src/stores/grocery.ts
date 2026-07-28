import type { GroceryItem, GroceryListResponse, GrocerySummaryResponse } from "@/types";
import { get, put } from "@/utils";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useGroceryStore = defineStore("grocery", () => {
  const items = ref<GroceryItem[]>([]);
  const windowStart = ref<string | null>(null);
  const windowEnd = ref<string | null>(null);
  const loading = ref(false);
  const refreshing = ref(false);
  const loaded = ref(false);
  const error = ref<string | null>(null);
  const activeCount = ref<number | null>(null);
  let listInflight: Promise<void> | null = null;
  let summaryInflight: Promise<number> | null = null;

  const activeItems = computed(() => items.value.filter((i) => !i.dismissed && !i.deleted));

  async function fetchSummary(force = false): Promise<number> {
    if (!force && activeCount.value !== null) return activeCount.value;
    if (summaryInflight) return summaryInflight;
    summaryInflight = (async () => {
      try {
        const res = await get<GrocerySummaryResponse>("/grocery/summary/");
        activeCount.value = res.active_count;
        windowStart.value = res.window_start;
        windowEnd.value = res.window_end;
        return res.active_count;
      } finally {
        summaryInflight = null;
      }
    })();
    return summaryInflight;
  }

  async function ensureLoaded(opts?: { force?: boolean }) {
    if (loaded.value && !opts?.force) return;
    if (listInflight) return listInflight;

    const soft = loaded.value && items.value.length > 0;
    if (soft) refreshing.value = true;
    else loading.value = true;
    error.value = null;

    listInflight = (async () => {
      try {
        const data = await get<GroceryListResponse>("/grocery/");
        items.value = data.items;
        windowStart.value = data.window_start;
        windowEnd.value = data.window_end;
        activeCount.value = data.items.filter((i) => !i.dismissed && !i.deleted).length;
        loaded.value = true;
      } catch (er) {
        console.error(er);
        error.value = "Couldn’t load your grocery list.";
        throw er;
      } finally {
        loading.value = false;
        refreshing.value = false;
        listInflight = null;
      }
    })();

    return listInflight;
  }

  function patchLocal(key: string, patch: Partial<GroceryItem>) {
    items.value = items.value.map((item) => (item.key === key ? { ...item, ...patch } : item));
    activeCount.value = items.value.filter((i) => !i.dismissed && !i.deleted).length;
  }

  async function setStatus(item: GroceryItem, status: "dismissed" | "deleted" | null) {
    const previous = { dismissed: item.dismissed, deleted: item.deleted };
    patchLocal(item.key, {
      dismissed: status === "dismissed",
      deleted: status === "deleted"
    });
    try {
      await put("/grocery/state/", { item_key: item.key, status });
    } catch (er) {
      console.error(er);
      patchLocal(item.key, previous);
      throw er;
    }
  }

  function invalidate() {
    loaded.value = false;
    activeCount.value = null;
  }

  return {
    items,
    windowStart,
    windowEnd,
    loading,
    refreshing,
    loaded,
    error,
    activeCount,
    activeItems,
    fetchSummary,
    ensureLoaded,
    setStatus,
    patchLocal,
    invalidate
  };
});
