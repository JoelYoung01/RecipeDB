<script setup lang="ts">
import SwipeRow from "@/components/SwipeRow.vue";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { paths } from "@/sitemap";
import { useGroceryStore } from "@/stores/grocery";
import type { GroceryItem } from "@/types";
import { Eye, EyeOff, ShoppingCart, Trash2 } from "@lucide/vue";
import { computed, onActivated, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

defineOptions({ name: "ShoppingListView" });

const router = useRouter();
const groceryStore = useGroceryStore();

const showDismissed = ref(false);

const visibleItems = computed(() => {
  if (showDismissed.value) {
    return groceryStore.items.filter((i) => !i.deleted);
  }
  return groceryStore.items.filter((i) => !i.dismissed && !i.deleted);
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

const activeCount = computed(
  () =>
    groceryStore.activeCount ?? groceryStore.items.filter((i) => !i.dismissed && !i.deleted).length
);
const dismissedCount = computed(
  () => groceryStore.items.filter((i) => i.dismissed && !i.deleted).length
);

const windowLabel = computed(() => {
  if (!groceryStore.windowStart || !groceryStore.windowEnd) return "";
  const start = new Date(groceryStore.windowStart);
  const end = new Date(groceryStore.windowEnd);
  const opts: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  return `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
});

const showSkeleton = computed(
  () => groceryStore.loading && groceryStore.items.length === 0 && !groceryStore.error
);

async function load(force = false) {
  try {
    await groceryStore.ensureLoaded({ force });
  } catch {
    /* store sets error */
  }
}

function onCheck(item: GroceryItem, checked: boolean | "indeterminate") {
  if (checked === true) {
    void groceryStore.setStatus(item, "dismissed");
  } else {
    void groceryStore.setStatus(item, null);
  }
}

function onDismiss(item: GroceryItem) {
  void groceryStore.setStatus(item, "dismissed");
}

function onDelete(item: GroceryItem) {
  void groceryStore.setStatus(item, "deleted");
}

function onViewRecipe(item: GroceryItem) {
  const recipe = item.recipes[0];
  if (!recipe) return;
  router.push({
    path: paths.recipeDetail(recipe.id),
    query: { returnUrl: paths.list }
  });
}

onMounted(() => load());
onActivated(() => load());
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
      v-if="!showSkeleton && dismissedCount > 0 && !showDismissed"
      class="mt-2 text-[11.5px] text-faint"
    >
      {{ dismissedCount }} dismissed · {{ activeCount }} remaining
    </p>

    <div v-if="showSkeleton" class="mt-5 flex flex-col gap-5">
      <section v-for="n in 3" :key="n" class="flex flex-col gap-2">
        <Skeleton class="h-3 w-20" />
        <div class="flex flex-col gap-1.5">
          <div
            v-for="m in 3"
            :key="m"
            class="flex items-start gap-3 rounded-xl border border-border bg-card px-3 py-3"
          >
            <Skeleton class="mt-0.5 size-4 rounded" />
            <div class="min-w-0 flex-1 space-y-2">
              <div class="flex justify-between gap-2">
                <Skeleton class="h-3.5 w-2/5" />
                <Skeleton class="h-3 w-12" />
              </div>
              <Skeleton class="h-2.5 w-3/5" />
            </div>
          </div>
        </div>
      </section>
    </div>

    <div
      v-else-if="groceryStore.error"
      class="mt-8 rounded-xl border border-border bg-card px-4 py-6 text-center"
    >
      <p class="text-sm text-muted-foreground">{{ groceryStore.error }}</p>
      <Button class="mt-4" size="sm" @click="load(true)">Retry</Button>
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
        {{ groceryStore.items.length === 0 ? "Nothing to shop for" : "All caught up" }}
      </p>
      <p class="mt-1 max-w-xs text-xs text-muted-foreground">
        <template v-if="groceryStore.items.length === 0">
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
      <Button
        v-if="groceryStore.items.length === 0"
        class="mt-5"
        @click="router.push(paths.planner)"
      >
        Open planner
      </Button>
    </div>

    <div v-else class="mt-5 flex flex-col gap-5">
      <section v-for="group in grouped" :key="group.category" class="flex flex-col gap-2">
        <h2 class="px-0.5 text-[11px] font-bold tracking-[0.08em] text-faint uppercase">
          {{ group.category }}
        </h2>
        <div class="flex flex-col gap-1.5">
          <SwipeRow v-for="item in group.items" :key="item.key" @swipe-right="onDismiss(item)">
            <template #hint>
              <div class="flex w-28 items-center bg-[rgba(34,197,94,0.22)] pl-4">
                <span class="text-xs font-semibold text-[#4ade80]">Dismiss</span>
              </div>
            </template>

            <template #actions="{ open, close }">
              <button
                type="button"
                class="flex flex-1 items-center justify-center bg-[#3f463f] text-foreground transition-opacity active:opacity-80"
                :tabindex="open ? 0 : -1"
                aria-label="View recipe"
                @click.stop="
                  close();
                  onViewRecipe(item);
                "
              >
                <Eye class="size-5" :stroke-width="2" />
              </button>
              <button
                type="button"
                class="flex flex-1 items-center justify-center bg-[#dc2626] text-primary-foreground transition-opacity active:opacity-80"
                :tabindex="open ? 0 : -1"
                aria-label="Remove from list"
                @click.stop="
                  close();
                  onDelete(item);
                "
              >
                <Trash2 class="size-5" :stroke-width="2" />
              </button>
            </template>

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
