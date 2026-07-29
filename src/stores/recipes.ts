import type { RecipeCard } from "@/types";
import { get } from "@/utils";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

const PAGE_SIZE = 50;

export const useRecipesStore = defineStore("recipes", () => {
  const recipes = ref<RecipeCard[]>([]);
  const loading = ref(false);
  const refreshing = ref(false);
  const loaded = ref(false);
  const count = ref<number | null>(null);
  const hasMore = ref(false);
  const revision = ref(0);
  let listInflight: Promise<void> | null = null;
  let countInflight: Promise<number> | null = null;

  const sorted = computed(() =>
    [...recipes.value].sort(
      (a, b) => new Date(b.created_on).getTime() - new Date(a.created_on).getTime()
    )
  );

  async function fetchCount(force = false): Promise<number> {
    if (!force && count.value !== null) return count.value;
    if (countInflight) return countInflight;
    countInflight = (async () => {
      try {
        const res = await get<{ count: number }>("/recipe/user/count/");
        count.value = res.count;
        return res.count;
      } finally {
        countInflight = null;
      }
    })();
    return countInflight;
  }

  async function ensureLoaded(opts?: { force?: boolean }) {
    if (loaded.value && !opts?.force) return;
    if (listInflight) return listInflight;

    const soft = loaded.value && recipes.value.length > 0;
    if (soft) refreshing.value = true;
    else loading.value = true;

    listInflight = (async () => {
      try {
        const page = await get<RecipeCard[]>(`/recipe/user/?limit=${PAGE_SIZE}&offset=0`);
        recipes.value = page;
        hasMore.value = page.length >= PAGE_SIZE;
        loaded.value = true;
        count.value = hasMore.value ? Math.max(count.value ?? 0, page.length) : page.length;
      } finally {
        loading.value = false;
        refreshing.value = false;
        listInflight = null;
      }
    })();

    return listInflight;
  }

  async function loadMore() {
    if (!hasMore.value || loading.value || refreshing.value) return;
    refreshing.value = true;
    try {
      const page = await get<RecipeCard[]>(
        `/recipe/user/?limit=${PAGE_SIZE}&offset=${recipes.value.length}`
      );
      recipes.value = [...recipes.value, ...page];
      hasMore.value = page.length >= PAGE_SIZE;
      if (!hasMore.value) count.value = recipes.value.length;
    } finally {
      refreshing.value = false;
    }
  }

  async function search(query: string): Promise<RecipeCard[]> {
    const q = query.trim();
    if (!q) {
      await ensureLoaded({ force: true });
      return recipes.value;
    }
    return get<RecipeCard[]>(`/recipe/search/?searchText=${encodeURIComponent(q)}`);
  }

  function invalidate() {
    loaded.value = false;
    count.value = null;
    revision.value += 1;
  }

  function reset() {
    recipes.value = [];
    loading.value = false;
    refreshing.value = false;
    hasMore.value = false;
    invalidate();
  }

  return {
    recipes,
    sorted,
    loading,
    refreshing,
    loaded,
    count,
    hasMore,
    revision,
    fetchCount,
    ensureLoaded,
    loadMore,
    search,
    invalidate,
    reset
  };
});
