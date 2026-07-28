<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { addDays, endOfDay, mediaUrl, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/media";
import { paths } from "@/sitemap";
import type { PlannedRecipeDetail } from "@/types/PlannedRecipe";
import type { RecipeDashboard } from "@/types/Recipe";
import { del, get, post } from "@/utils";
import { ChevronRight, Sparkles, Trash2 } from "@lucide/vue";
import { computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const WEEK_COUNT = 8;
const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function fromQueryOrToday(): Date {
  const q = typeof route.query.date === "string" ? route.query.date : "";
  if (/^\d{4}-\d{2}-\d{2}$/.test(q)) {
    const [y, m, d] = q.split("-").map(Number);
    return startOfDay(new Date(y, m - 1, d));
  }
  return startOfDay();
}

const selectedDate = ref(fromQueryOrToday());
const plannedRecipes = ref<PlannedRecipeDetail[]>([]);
const recipes = ref<RecipeDashboard[]>([]);
const showRecipeDialog = ref(false);
const selectedIds = ref<number[]>([]);
const loading = ref(true);

const today = startOfDay();
const currentWeekStart = startOfWeekMonday(today);

const weeks = computed(() =>
  Array.from({ length: WEEK_COUNT }, (_, weekIndex) => {
    const weekStart = addDays(currentWeekStart, weekIndex * 7);
    const days = Array.from({ length: 7 }, (_, dayIndex) => addDays(weekStart, dayIndex));
    return { weekIndex, weekStart, days };
  })
);

const rangeStart = computed(() => currentWeekStart);
const rangeEnd = computed(() => endOfDay(addDays(currentWeekStart, WEEK_COUNT * 7 - 1)));

const plannedByDay = computed(() => {
  const map = new Map<string, PlannedRecipeDetail[]>();
  for (const p of plannedRecipes.value) {
    const key = p.planned_for.slice(0, 10);
    const list = map.get(key) ?? [];
    list.push(p);
    map.set(key, list);
  }
  return map;
});

const currentPlannedRecipes = computed(
  () => plannedByDay.value.get(toDateKey(selectedDate.value)) ?? []
);

const currentWeekGapDays = computed(() => {
  const days = weeks.value[0]?.days ?? [];
  return days.filter((d) => (plannedByDay.value.get(toDateKey(d)) ?? []).length === 0);
});

const formattedSelectedDate = computed(() => {
  const date = selectedDate.value;
  const currentYear = new Date().getFullYear();
  const weekday = date.toLocaleString("en-US", { weekday: "long" });
  const month = date.toLocaleString("en-US", { month: "short" });
  const day = date.getDate();
  const year = date.getFullYear();
  const datePart = year === currentYear ? `${month} ${day}` : `${month} ${day}, ${year}`;
  return `${weekday} · ${datePart}`;
});

function weekLabel(weekStart: Date, weekIndex: number): string {
  if (weekIndex === 0) return "This week";
  if (weekIndex === 1) return "Next week";
  const end = addDays(weekStart, 6);
  const opts: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  return `${weekStart.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
}

function selectDay(date: Date) {
  selectedDate.value = startOfDay(date);
}

function openFillGaps(days?: Date[]) {
  const keys = (days ?? currentWeekGapDays.value).map(toDateKey);
  router.push({
    path: paths.plannerFill,
    query: keys.length ? { days: keys.join(",") } : {}
  });
}

function openPlanWeek(weekDays: Date[]) {
  router.push({
    path: paths.plannerFill,
    query: { days: weekDays.map(toDateKey).join(",") }
  });
}

async function getPlannedRecipes() {
  try {
    plannedRecipes.value = await post<PlannedRecipeDetail[]>("/planned-recipe/time-frame/", {
      start: rangeStart.value.toISOString(),
      end: rangeEnd.value.toISOString()
    });
    selectedIds.value = currentPlannedRecipes.value.map((p) => p.recipe.id);
  } catch (error) {
    console.error("Error fetching planned recipes:", error);
  }
}

async function getRecipes() {
  try {
    recipes.value = await get("/recipe/user/");
  } catch (error) {
    console.error("Error fetching recipes:", error);
  }
}

function openAssign() {
  selectedIds.value = currentPlannedRecipes.value.map((p) => p.recipe.id);
  showRecipeDialog.value = true;
}

function toggleRecipe(id: number) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((x) => x !== id);
  } else {
    selectedIds.value = [...selectedIds.value, id];
  }
}

async function assignRecipe() {
  const existing = currentPlannedRecipes.value;
  const existingIds = existing.map((p) => p.recipe.id);
  const added = selectedIds.value.filter((id) => !existingIds.includes(id));
  const removed = existing.filter((pr) => !selectedIds.value.includes(pr.recipe.id));

  try {
    await Promise.all([
      ...added.map((id) =>
        post("/planned-recipe/", {
          recipe_id: id,
          planned_for: selectedDate.value.toISOString()
        })
      ),
      ...removed.map((pr) => del(`/planned-recipe/${pr.id}/`))
    ]);
    await getPlannedRecipes();
    showRecipeDialog.value = false;
  } catch (error) {
    console.error("Error assigning recipe:", error);
  }
}

async function removePlanned(planned: PlannedRecipeDetail) {
  try {
    await del(`/planned-recipe/${planned.id}/`);
    await getPlannedRecipes();
  } catch (er) {
    console.error(er);
  }
}

watch(selectedDate, () => {
  selectedIds.value = currentPlannedRecipes.value.map((p) => p.recipe.id);
});

onMounted(async () => {
  loading.value = true;
  await Promise.all([getPlannedRecipes(), getRecipes()]);
  loading.value = false;
});
</script>

<template>
  <div class="px-4 pt-5 pb-4">
    <div class="flex items-start justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold">Planner</h1>
        <p class="mt-1 text-sm text-muted-foreground">This week up top — scroll for more</p>
      </div>
      <Button
        size="sm"
        class="shrink-0 gap-1.5"
        :disabled="!currentWeekGapDays.length && loading"
        @click="openFillGaps()"
      >
        <Sparkles class="size-3.5" />
        Fill gaps
      </Button>
    </div>

    <div class="mt-4 space-y-5">
      <section v-for="week in weeks" :key="week.weekIndex" class="space-y-2">
        <div
          class="sticky top-0 z-10 -mx-4 flex items-center justify-between gap-2 border-b border-border/80 bg-background/95 px-4 py-2 backdrop-blur-sm"
        >
          <div>
            <h2 class="text-sm font-semibold">{{ weekLabel(week.weekStart, week.weekIndex) }}</h2>
            <p class="text-[11px] text-faint">
              {{ week.days.filter((d) => (plannedByDay.get(toDateKey(d)) ?? []).length).length }}
              / 7 planned
            </p>
          </div>
          <button
            type="button"
            class="inline-flex items-center gap-0.5 text-[12.5px] font-semibold text-[#22c55e] transition-opacity active:opacity-70"
            @click="openPlanWeek(week.days)"
          >
            Plan week
            <ChevronRight class="size-3.5" />
          </button>
        </div>

        <div class="overflow-hidden rounded-xl border border-border bg-card">
          <button
            v-for="(day, dayIndex) in week.days"
            :key="toDateKey(day)"
            type="button"
            class="flex w-full items-center gap-3 border-b border-border px-3 py-2.5 text-left transition-colors last:border-b-0"
            :class="
              toDateKey(day) === toDateKey(selectedDate)
                ? 'bg-[rgba(34,197,94,0.1)]'
                : 'active:bg-secondary/50'
            "
            @click="selectDay(day)"
          >
            <div class="w-11 shrink-0 text-center">
              <div
                class="text-[10px] font-semibold uppercase tracking-wide"
                :class="toDateKey(day) === toDateKey(today) ? 'text-[#22c55e]' : 'text-faint'"
              >
                {{ DAY_LABELS[dayIndex] }}
              </div>
              <div
                class="mt-0.5 text-base font-bold leading-none"
                :class="toDateKey(day) === toDateKey(today) ? 'text-[#22c55e]' : 'text-foreground'"
              >
                {{ day.getDate() }}
              </div>
            </div>

            <div class="min-w-0 flex-1">
              <template v-if="(plannedByDay.get(toDateKey(day)) ?? []).length">
                <div class="flex items-center gap-2">
                  <img
                    v-for="planned in (plannedByDay.get(toDateKey(day)) ?? []).slice(0, 1)"
                    :key="planned.id"
                    :src="mediaUrl(planned.recipe.cover_image?.url)"
                    :alt="planned.recipe.name"
                    class="size-9 shrink-0 rounded-lg object-cover"
                  />
                  <div class="min-w-0">
                    <p class="truncate text-sm font-semibold">
                      {{ (plannedByDay.get(toDateKey(day)) ?? [])[0]?.recipe.name }}
                    </p>
                    <p
                      v-if="(plannedByDay.get(toDateKey(day)) ?? []).length > 1"
                      class="truncate text-[11px] text-muted-foreground"
                    >
                      +{{ (plannedByDay.get(toDateKey(day)) ?? []).length - 1 }} more
                    </p>
                    <p v-else class="truncate text-[11px] text-muted-foreground">Dinner planned</p>
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="flex items-center gap-2">
                  <span class="size-1.5 rounded-full bg-[#3f3f46]" />
                  <span class="text-sm text-muted-foreground">Open night</span>
                </div>
              </template>
            </div>
          </button>
        </div>
      </section>
    </div>

    <div class="mt-5 rounded-xl border border-border bg-card p-4">
      <h2 class="font-semibold">{{ formattedSelectedDate }}</h2>

      <div v-if="currentPlannedRecipes.length" class="mt-3 space-y-2">
        <div
          v-for="planned in currentPlannedRecipes"
          :key="planned.id"
          class="flex items-start gap-2"
        >
          <RecipeCard :recipe="planned.recipe" size="sm" class="flex-1" />
          <Button
            size="icon-sm"
            variant="ghost"
            class="text-destructive"
            @click="removePlanned(planned)"
          >
            <Trash2 class="size-4" />
          </Button>
        </div>
      </div>
      <p v-else class="mt-3 text-sm text-muted-foreground">No recipes planned for this date</p>

      <div class="mt-4 grid grid-cols-2 gap-2">
        <Button variant="outline" @click="openAssign">
          {{ currentPlannedRecipes.length ? "Change" : "Add recipes" }}
        </Button>
        <Button variant="secondary" class="gap-1.5" @click="openFillGaps([selectedDate])">
          <Sparkles class="size-3.5" />
          Autofill
        </Button>
      </div>
    </div>

    <Dialog v-model:open="showRecipeDialog">
      <DialogContent class="max-h-[80dvh] max-w-sm overflow-hidden border-border bg-card">
        <DialogHeader>
          <DialogTitle>Select recipes</DialogTitle>
        </DialogHeader>
        <div class="max-h-[50dvh] space-y-2 overflow-y-auto pr-1">
          <button
            v-for="recipe in recipes"
            :key="recipe.id"
            type="button"
            class="flex w-full items-center gap-3 rounded-xl border px-2 py-2 text-left transition-colors"
            :class="
              selectedIds.includes(recipe.id)
                ? 'border-[rgba(34,197,94,0.45)] bg-[rgba(34,197,94,0.12)]'
                : 'border-border bg-secondary/40'
            "
            @click="toggleRecipe(recipe.id)"
          >
            <img
              :src="mediaUrl(recipe.cover_image?.url)"
              :alt="recipe.name"
              class="size-12 shrink-0 rounded-lg object-cover"
            />
            <span class="min-w-0">
              <span class="block truncate text-sm font-semibold">{{ recipe.name }}</span>
              <span class="block truncate text-xs text-muted-foreground">{{
                recipe.description
              }}</span>
            </span>
          </button>
          <p v-if="!recipes.length" class="py-6 text-center text-sm text-muted-foreground">
            Add recipes first.
          </p>
        </div>
        <DialogFooter class="gap-2">
          <Button variant="outline" @click="showRecipeDialog = false">Cancel</Button>
          <Button :disabled="!selectedIds.length" @click="assignRecipe">Assign</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
