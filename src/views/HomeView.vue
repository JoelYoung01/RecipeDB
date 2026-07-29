<script setup lang="ts">
import HomeWeekStrip from "@/components/HomeWeekStrip.vue";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatPrepTime, mediaUrl, startOfDay, toDateKey } from "@/lib/media";
import { paths } from "@/sitemap";
import { useGroceryStore } from "@/stores/grocery";
import { usePlannerStore } from "@/stores/planner";
import { useRecipesStore } from "@/stores/recipes";
import { useSessionStore } from "@/stores/session";
import { Plus, Search, ShoppingCart, User } from "@lucide/vue";
import { computed, onActivated, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

defineOptions({ name: "HomeView" });

const router = useRouter();
const session = useSessionStore();
const recipesStore = useRecipesStore();
const groceryStore = useGroceryStore();
const plannerStore = usePlannerStore();

const loading = ref(true);
const plansReady = ref(false);
const visibleWeekDays = ref<Date[]>([]);
const weekRange = ref<{ start: Date; end: Date } | null>(null);

const today = startOfDay();

const weekdayName = computed(() => today.toLocaleDateString(undefined, { weekday: "long" }));

/** Derived from the shared planner store so KeepAlive tabs stay in sync. */
const weekPlans = computed(() => {
  if (!weekRange.value) return [];
  return plannerStore.plansInRange(weekRange.value.start, weekRange.value.end);
});

const plannedKeys = computed(() => {
  const set = new Set<string>();
  for (const p of weekPlans.value) {
    set.add(p.planned_for.slice(0, 10));
  }
  return set;
});

const plannedCount = computed(() => {
  let n = 0;
  for (const d of visibleWeekDays.value) {
    if (plannedKeys.value.has(toDateKey(d))) n += 1;
  }
  return n;
});

const gapDays = computed(() =>
  visibleWeekDays.value.filter((d) => !plannedKeys.value.has(toDateKey(d)))
);

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

const showHeroSkeleton = computed(() => loading.value && !plansReady.value && !tonight.value);

const recipeCount = computed(() => recipesStore.count ?? 0);
const groceryCount = computed(() => groceryStore.activeCount ?? 0);

async function loadWeekPlans(rangeStart: Date, rangeEnd: Date) {
  weekRange.value = { start: rangeStart, end: rangeEnd };
  try {
    await plannerStore.ensureRange(rangeStart, rangeEnd);
    plansReady.value = true;
  } catch (er) {
    console.error(er);
    plansReady.value = true;
  } finally {
    loading.value = false;
  }
}

async function loadBadges() {
  try {
    await Promise.all([recipesStore.fetchCount(), groceryStore.fetchSummary()]);
  } catch (er) {
    console.error(er);
  }
}

function onWeekChange(_weekStart: Date, days: Date[], rangeStart: Date, rangeEnd: Date) {
  visibleWeekDays.value = days;
  void loadWeekPlans(rangeStart, rangeEnd);
}

function openDay(date: Date) {
  router.push({ path: paths.planner, query: { date: toDateKey(date) } });
}

function openFillGaps() {
  router.push({
    path: paths.plannerFill,
    query: {
      days: gapDays.value.map(toDateKey).join(",")
    }
  });
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

async function refreshHome() {
  await loadBadges();
  if (weekRange.value) {
    await loadWeekPlans(weekRange.value.start, weekRange.value.end);
  }
}

onMounted(() => {
  void loadBadges();
});
onActivated(() => {
  void refreshHome();
});

// If another page invalidates planner while Home is cached, refetch the visible window.
watch(
  () => plannerStore.revision,
  () => {
    if (weekRange.value) {
      void loadWeekPlans(weekRange.value.start, weekRange.value.end);
    }
  }
);
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
          <template v-else-if="showHeroSkeleton">
            <Skeleton class="mt-1.5 h-6 w-40 bg-white/20" />
            <Skeleton class="mt-2 h-3 w-28 bg-white/15" />
          </template>
          <template v-else>
            <p class="mt-0.5 text-xl font-bold leading-tight text-white">Nothing planned</p>
            <p class="mt-0.5 text-xs text-white/80">Pick something for tonight</p>
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
      <HomeWeekStrip
        :planned-keys="plannedKeys"
        @week-change="onWeekChange"
        @select-day="openDay"
      />
      <div class="mt-2.5 flex items-center justify-between">
        <p class="text-xs text-muted-foreground">{{ plannedCount }} of 7 dinners planned</p>
        <button
          type="button"
          class="text-[12.5px] font-semibold text-[#22c55e] transition-opacity active:opacity-70"
          @click="openFillGaps"
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
        <span class="text-[11.5px] text-faint">
          <template v-if="recipesStore.count === null">
            <Skeleton class="inline-block h-3 w-10 align-middle" />
          </template>
          <template v-else>{{ recipeCount }} saved</template>
        </span>
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
          <template v-if="groceryStore.activeCount === null">·</template>
          <template v-else>{{ groceryCount }}</template>
        </span>
      </button>
    </section>
  </div>
</template>
