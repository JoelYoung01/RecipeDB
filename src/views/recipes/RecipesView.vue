<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import RecipeCardSkeleton from "@/components/RecipeCardSkeleton.vue";
import { Input } from "@/components/ui/input";
import { useRecipesStore } from "@/stores/recipes";
import type { RecipeCard as RecipeCardType } from "@/types";
import { Search } from "@lucide/vue";
import { computed, onActivated, onMounted, ref, watch } from "vue";

defineOptions({ name: "RecipesView" });

const recipesStore = useRecipesStore();

const searchText = ref("");
const searchResults = ref<RecipeCardType[] | null>(null);
const searching = ref(false);

const displayList = computed(() => {
  if (searchResults.value) {
    return [...searchResults.value].sort(
      (a, b) => new Date(b.created_on).getTime() - new Date(a.created_on).getTime()
    );
  }
  return recipesStore.sorted;
});

const showSkeleton = computed(
  () =>
    (recipesStore.loading && !recipesStore.recipes.length) ||
    (searching.value && !searchResults.value?.length && !!searchText.value.trim())
);

async function loadMine() {
  await recipesStore.ensureLoaded();
}

async function runSearch() {
  const q = searchText.value.trim();
  if (!q) {
    searchResults.value = null;
    searching.value = false;
    await recipesStore.ensureLoaded();
    return;
  }
  searching.value = true;
  try {
    searchResults.value = await recipesStore.search(q);
  } catch (er) {
    console.error(er);
  }
  searching.value = false;
}

let debounce: ReturnType<typeof setTimeout> | undefined;
watch(searchText, () => {
  clearTimeout(debounce);
  debounce = setTimeout(runSearch, 300);
});

onMounted(loadMine);
onActivated(() => {
  if (!searchText.value.trim()) {
    void recipesStore.ensureLoaded();
  }
});
</script>

<template>
  <div class="px-4 pt-5 pb-2">
    <h1 class="text-xl font-bold">Recipes</h1>
    <p class="mt-1 text-sm text-muted-foreground">Your library and public finds</p>

    <div class="relative mt-4">
      <Search
        class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-faint"
      />
      <Input
        v-model="searchText"
        type="search"
        placeholder="Search recipes…"
        class="h-11 rounded-xl border-border bg-card pl-10"
      />
    </div>

    <div class="mt-4 flex flex-col gap-2">
      <template v-if="showSkeleton">
        <RecipeCardSkeleton v-for="n in 4" :key="n" />
      </template>
      <template v-else>
        <RecipeCard v-for="recipe in displayList" :key="recipe.id" :recipe="recipe" />
        <p
          v-if="displayList.length === 0"
          class="rounded-xl border border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground"
        >
          {{
            searchText.trim()
              ? "No recipes matched that search."
              : "No recipes yet — add one with +"
          }}
        </p>
        <button
          v-else-if="!searchText.trim() && recipesStore.hasMore"
          type="button"
          class="mt-1 rounded-xl border border-border bg-card px-4 py-3 text-sm font-semibold text-[#22c55e] transition-opacity active:opacity-70"
          :disabled="recipesStore.refreshing"
          @click="recipesStore.loadMore()"
        >
          {{ recipesStore.refreshing ? "Loading…" : "Load more" }}
        </button>
      </template>
    </div>
  </div>
</template>
