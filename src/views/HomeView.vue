<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  addDays,
  endOfDay,
  formatPrepTime,
  mediaUrl,
  startOfDay,
  startOfWeekMonday,
  toDateKey
} from "@/lib/media";
import { useSessionStore } from "@/stores/session";
import { paths } from "@/sitemap";
import type { GroceryListResponse, PlannedRecipeDetail } from "@/types";
import { get, post } from "@/utils";
import { Plus, Search, ShoppingCart, User } from "@lucide/vue";
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const session = useSessionStore();

const loading = ref(true);
const weekPlans = ref<PlannedRecipeDetail[]>([]);
const recipeCount = ref(0);
const groceryCount = ref(0);

const today = startOfDay();
const weekStart = startOfWeekMonday(today);
const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
const dayLabels = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];

const weekdayName = computed(() => today.toLocaleDateString(undefined, { weekday: "long" }));

const plannedKeys = computed(() => {
  const set = new Set<string>();
  for (const p of weekPlans.value) {
    set.add(p.planned_for.slice(0, 10));
  }
  return set;
});

const plannedCount = computed(() => {
  let n = 0;
  for (const d of weekDays) {
    if (plannedKeys.value.has(toDateKey(d))) n += 1;
  }
  return n;
});

const tonight = computed(() => {
  const key = toDateKey(today);
  return weekPlans.value.find((p) => p.planned_for.startsWith(key)) ?? null;
});

const tonightImage = computed(() => mediaUrl(tonight.value?.recipe.cover_image?.url));
const tonightMeta = computed(() => {
  if (!tonight.value) return "";
  const prep = formatPrepTime(tonight.value.recipe.prep_time);
  return prep || "Tonight’s plan";
});

async function load() {
  loading.value = true;
  try {
    const weekEnd = endOfDay(addDays(weekStart, 6));
    const [plans, recipes, grocery] = await Promise.all([
      post<PlannedRecipeDetail[]>("/planned-recipe/time-frame/", {
        start: weekStart.toISOString(),
        end: weekEnd.toISOString()
      }),
      get<{ id: number }[]>("/recipe/user/"),
      get<GroceryListResponse>("/grocery/")
    ]);
    weekPlans.value = plans;
    recipeCount.value = recipes.length;
    groceryCount.value = grocery.items.filter((i) => !i.dismissed && !i.deleted).length;
  } catch (er) {
    console.error(er);
  }
  loading.value = false;
}

function openDay(date: Date) {
  router.push({ path: paths.planner, query: { date: toDateKey(date) } });
}

function cookTonight() {
  if (!tonight.value) {
    router.push(paths.planner);
    return;
  }
  router.push({
    path: paths.recipeDetail(tonight.value.recipe.id),
    query: { returnUrl: paths.home }
  });
}

onMounted(load);
</script>

<template>
  <div class="flex min-h-[calc(100dvh-5.5rem)] flex-col">
    <!-- Tonight hero -->
    <section class="relative h-[300px] shrink-0 overflow-hidden">
      <img
        v-if="tonight"
        :src="tonightImage"
        :alt="tonight.recipe.name"
        class="absolute inset-0 size-full object-cover"
      />
      <div
        v-else
        class="absolute inset-0 bg-[repeating-linear-gradient(45deg,#232326_0_10px,#1d1d20_10px_20px)]"
      />
      <div
        class="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-[rgba(9,9,11,0.95)]"
      />

      <div class="absolute inset-x-0 top-0 flex items-center justify-between px-5 pt-4">
        <h1 class="text-base font-bold text-white">{{ weekdayName }}</h1>
        <button
          type="button"
          class="flex size-[34px] items-center justify-center rounded-full bg-white/15 text-white backdrop-blur-sm transition-opacity active:opacity-80"
          aria-label="Account"
          @click="router.push(paths.account)"
        >
          <img
            v-if="session.currentUser?.avatar_url"
            :src="session.currentUser.avatar_url"
            alt=""
            class="size-full rounded-full object-cover"
          />
          <User v-else class="size-4" :stroke-width="2" />
        </button>
      </div>

      <div class="absolute inset-x-0 bottom-0 flex items-end justify-between gap-3 px-5 pb-4">
        <div class="min-w-0">
          <p class="text-[11px] font-bold tracking-[0.08em] text-success-soft">TONIGHT</p>
          <template v-if="tonight">
            <p class="mt-0.5 text-xl font-bold leading-tight text-white">
              {{ tonight.recipe.name }}
            </p>
            <p class="mt-0.5 text-xs text-white/80">{{ tonightMeta }}</p>
          </template>
          <template v-else>
            <p class="mt-0.5 text-xl font-bold leading-tight text-white">Nothing planned</p>
            <p class="mt-0.5 text-xs text-white/80">
              {{ loading ? "Loading…" : "Pick something for tonight" }}
            </p>
          </template>
        </div>
        <Button
          class="shrink-0 rounded-[11px] px-4 py-2.5 text-[13px] font-semibold"
          @click="cookTonight"
        >
          {{ tonight ? "Cook" : "Plan" }}
        </Button>
      </div>
    </section>

    <!-- Week strip -->
    <section class="px-5 pt-3.5">
      <div class="grid grid-cols-7 gap-1">
        <button
          v-for="(day, i) in weekDays"
          :key="toDateKey(day)"
          type="button"
          class="rounded-lg py-1.5 text-center transition-colors"
          :class="
            toDateKey(day) === toDateKey(today)
              ? 'border border-[rgba(34,197,94,0.35)] bg-[rgba(34,197,94,0.12)]'
              : ''
          "
          @click="openDay(day)"
        >
          <div
            class="text-[10px] font-semibold"
            :class="toDateKey(day) === toDateKey(today) ? 'font-bold text-[#22c55e]' : 'text-faint'"
          >
            {{ dayLabels[i] }}
          </div>
          <div
            class="mx-auto mt-1.5 size-1.5 rounded-full"
            :class="plannedKeys.has(toDateKey(day)) ? 'bg-[#22c55e]' : 'bg-[#3f3f46]'"
          />
        </button>
      </div>
      <div class="mt-2.5 flex items-center justify-between">
        <p class="text-xs text-muted-foreground">{{ plannedCount }} of 7 dinners planned</p>
        <button
          type="button"
          class="text-[12.5px] font-semibold text-[#22c55e] transition-opacity active:opacity-70"
          @click="router.push(paths.planner)"
        >
          Fill the gaps →
        </button>
      </div>
    </section>

    <!-- Action rows -->
    <section class="flex flex-1 flex-col gap-2 overflow-hidden px-5 pt-4">
      <button
        type="button"
        class="flex items-center gap-3 rounded-xl border border-border bg-card px-3.5 py-3.5 text-left transition-opacity active:opacity-80"
        @click="router.push(`${paths.recipeImport}?method=link`)"
      >
        <Plus class="size-[18px] shrink-0 text-[#22c55e]" :stroke-width="2" />
        <span class="flex-1 text-sm font-semibold">Import a recipe</span>
        <span class="text-[11.5px] text-faint">link · photo · manual</span>
      </button>

      <button
        type="button"
        class="flex items-center gap-3 rounded-xl border border-border bg-card px-3.5 py-3.5 text-left transition-opacity active:opacity-80"
        @click="router.push(paths.recipes)"
      >
        <Search class="size-[18px] shrink-0 text-[#22c55e]" :stroke-width="2" />
        <span class="flex-1 text-sm font-semibold">Find a recipe</span>
        <span class="text-[11.5px] text-faint"> {{ recipeCount }} saved </span>
      </button>

      <button
        type="button"
        class="flex items-center gap-3 rounded-xl border border-border bg-card px-3.5 py-3.5 text-left transition-opacity active:opacity-80"
        @click="router.push(paths.list)"
      >
        <ShoppingCart class="size-[18px] shrink-0 text-[#22c55e]" :stroke-width="2" />
        <span class="flex-1 text-sm font-semibold">Grocery</span>
        <span
          class="rounded-full border border-[rgba(34,197,94,0.35)] bg-[rgba(34,197,94,0.12)] px-2 py-0.5 text-[11px] font-bold text-[#4ade80]"
        >
          {{ groceryCount }}
        </span>
      </button>
    </section>
  </div>
</template>
