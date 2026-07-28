<script setup lang="ts">
import SwipeRow from "@/components/grocery/SwipeRow.vue";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { paths } from "@/sitemap";
import type { GroceryItem, GroceryListResponse } from "@/types";
import { get, put } from "@/utils";
import { EyeOff, ShoppingCart } from "@lucide/vue";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const loading = ref(true);
const error = ref<string | null>(null);
const showDismissed = ref(false);
const items = ref<GroceryItem[]>([]);
const windowLabel = ref("");

const visibleItems = computed(() => {
  if (showDismissed.value) {
    return items.value.filter((i) => !i.deleted);
  }
  return items.value.filter((i) => !i.dismissed && !i.deleted);
});

const grouped = computed(() => {
  const map = new Map<string, GroceryItem[]>();
  for (const item of visibleItems.value) {
    const list = map.get(item.category) ?? [];
    list.push(item);
    map.set(item.category, list);
  }
  return Array.from(map.entries()).map(([category, categoryItems]) => ({
    category,
    items: categoryItems
  }));
});

const activeCount = computed(() => items.value.filter((i) => !i.dismissed && !i.deleted).length);
const dismissedCount = computed(() => items.value.filter((i) => i.dismissed && !i.deleted).length);

function formatWindow(startIso: string, endIso: string) {
  const start = new Date(startIso);
  const end = new Date(endIso);
  const opts: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  return `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
}

async function load() {
  loading.value = true;
  error.value = null;
  try {
    const data = await get<GroceryListResponse>("/grocery/");
    items.value = data.items;
    windowLabel.value = formatWindow(data.window_start, data.window_end);
  } catch (er) {
    console.error(er);
    error.value = "Couldn’t load your grocery list.";
  }
  loading.value = false;
}

function patchLocal(key: string, patch: Partial<GroceryItem>) {
  items.value = items.value.map((item) => (item.key === key ? { ...item, ...patch } : item));
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
  }
}

function onCheck(item: GroceryItem, checked: boolean | "indeterminate") {
  if (checked === true) {
    void setStatus(item, "dismissed");
  } else {
    void setStatus(item, null);
  }
}

function onDismiss(item: GroceryItem) {
  void setStatus(item, "dismissed");
}

function onDelete(item: GroceryItem) {
  void setStatus(item, "deleted");
}

function onViewRecipe(item: GroceryItem) {
  const recipe = item.recipes[0];
  if (!recipe) return;
  router.push({
    path: paths.recipeDetail(recipe.id),
    query: { returnUrl: paths.list }
  });
}

onMounted(load);
</script>

<template>
  <div class="px-4 pt-5 pb-4">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <h1 class="text-xl font-bold">Grocery</h1>
        <p class="mt-1 text-sm text-muted-foreground">
          Ingredients for the next 7 days
          <span v-if="windowLabel" class="text-faint"> · {{ windowLabel }}</span>
        </p>
      </div>
      <Button
        variant="outline"
        size="sm"
        class="shrink-0 border-border bg-card text-xs"
        :class="showDismissed ? 'border-[rgba(34,197,94,0.45)] text-[#4ade80]' : ''"
        @click="showDismissed = !showDismissed"
      >
        <EyeOff class="size-3.5" />
        {{ showDismissed ? "Hide dismissed" : "Show dismissed" }}
      </Button>
    </div>

    <p
      v-if="!loading && dismissedCount > 0 && !showDismissed"
      class="mt-2 text-[11.5px] text-faint"
    >
      {{ dismissedCount }} dismissed · {{ activeCount }} remaining
    </p>

    <div v-if="loading" class="mt-10 text-center text-sm text-muted-foreground">
      Loading grocery list…
    </div>

    <div
      v-else-if="error"
      class="mt-8 rounded-xl border border-border bg-card px-4 py-6 text-center"
    >
      <p class="text-sm text-muted-foreground">{{ error }}</p>
      <Button class="mt-4" size="sm" @click="load">Retry</Button>
    </div>

    <div
      v-else-if="visibleItems.length === 0"
      class="mt-8 flex flex-col items-center rounded-xl border border-border bg-card px-6 py-12 text-center"
    >
      <div
        class="mb-3 flex size-12 items-center justify-center rounded-xl bg-[rgba(34,197,94,0.15)]"
      >
        <ShoppingCart class="size-6 text-[#22c55e]" />
      </div>
      <p class="text-sm font-semibold">
        {{ items.length === 0 ? "Nothing to shop for" : "All caught up" }}
      </p>
      <p class="mt-1 max-w-xs text-xs text-muted-foreground">
        <template v-if="items.length === 0">
          Plan meals for the next week and ingredients will show up here automatically.
        </template>
        <template v-else>
          Dismissed items are hidden.
          <button
            type="button"
            class="text-[#22c55e] underline-offset-2 hover:underline"
            @click="showDismissed = true"
          >
            Show dismissed
          </button>
        </template>
      </p>
      <Button v-if="items.length === 0" class="mt-5" @click="router.push(paths.planner)">
        Open planner
      </Button>
    </div>

    <div v-else class="mt-5 flex flex-col gap-5">
      <section v-for="group in grouped" :key="group.category" class="flex flex-col gap-2">
        <h2 class="px-0.5 text-[11px] font-bold tracking-[0.08em] text-faint uppercase">
          {{ group.category }}
        </h2>
        <div class="flex flex-col gap-1.5">
          <SwipeRow
            v-for="item in group.items"
            :key="item.key"
            @dismiss="onDismiss(item)"
            @delete="onDelete(item)"
            @view="onViewRecipe(item)"
          >
            <div
              class="flex items-start gap-3 border border-border px-3 py-3"
              :class="item.dismissed ? 'opacity-55' : ''"
            >
              <Checkbox
                class="mt-0.5"
                :model-value="item.dismissed"
                :aria-label="`Mark ${item.name} done`"
                @update:model-value="(v) => onCheck(item, v)"
              />
              <div class="min-w-0 flex-1">
                <div class="flex items-baseline justify-between gap-2">
                  <p
                    class="text-sm font-semibold leading-snug"
                    :class="item.dismissed ? 'line-through text-muted-foreground' : ''"
                  >
                    {{ item.name }}
                  </p>
                  <p
                    v-if="item.quantity_display"
                    class="shrink-0 text-[12.5px] font-medium text-[#86efac]"
                  >
                    {{ item.quantity_display }}
                  </p>
                </div>
                <p class="mt-0.5 truncate text-[11.5px] text-muted-foreground">
                  {{ item.recipe_titles }}
                </p>
              </div>
            </div>
          </SwipeRow>
        </div>
      </section>
    </div>
  </div>
</template>
