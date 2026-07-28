<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import { Input } from "@/components/ui/input";
import type { RecipeDashboard } from "@/types";
import { get } from "@/utils";
import { Search } from "@lucide/vue";
import { computed, onMounted, watch } from "vue";

const loading = ref(true);
const recipes = ref<RecipeDashboard[]>([]);
const searchText = ref("");
const searching = ref(false);

const sorted = computed(() =>
  [...recipes.value].sort(
    (a, b) => new Date(b.created_on).getTime() - new Date(a.created_on).getTime()
  )
);

async function loadMine() {
  loading.value = true;
  try {
    recipes.value = await get("/recipe/user/");
  } catch (er) {
    console.error(er);
  }
  loading.value = false;
}

async function search() {
  const q = searchText.value.trim();
  if (!q) {
    await loadMine();
    return;
  }
  searching.value = true;
  try {
    recipes.value = await get(`/recipe/search/?searchText=${encodeURIComponent(q)}`);
  } catch (er) {
    console.error(er);
  }
  searching.value = false;
}

let debounce: ReturnType<typeof setTimeout> | undefined;
watch(searchText, () => {
  clearTimeout(debounce);
  debounce = setTimeout(search, 300);
});

onMounted(loadMine);
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

    <p v-if="loading || searching" class="mt-6 text-center text-sm text-muted-foreground">
      Loading…
    </p>

    <div v-else class="mt-4 flex flex-col gap-2">
      <RecipeCard v-for="recipe in sorted" :key="recipe.id" :recipe="recipe" />
      <p
        v-if="sorted.length === 0"
        class="rounded-xl border border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground"
      >
        {{
          searchText.trim() ? "No recipes matched that search." : "No recipes yet — add one with +"
        }}
      </p>
    </div>
  </div>
</template>
