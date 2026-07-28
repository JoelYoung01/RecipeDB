<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { mediaUrl, startOfDay, toDateKey } from "@/lib/media";
import type { PlannedRecipeDetail } from "@/types/PlannedRecipe";
import type { RecipeDashboard } from "@/types/Recipe";
import { del, get, post } from "@/utils";
import { CalendarDate, getLocalTimeZone, type DateValue } from "@internationalized/date";
import { Trash2 } from "@lucide/vue";
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

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

const calendarValue = computed<DateValue>({
  get: () => {
    const d = selectedDate.value;
    return new CalendarDate(d.getFullYear(), d.getMonth() + 1, d.getDate());
  },
  set: (val) => {
    if (!val) return;
    selectedDate.value = startOfDay(val.toDate(getLocalTimeZone()));
  }
});

const formattedSelectedDate = computed(() => {
  const date = selectedDate.value;
  const currentYear = new Date().getFullYear();
  const month = date.toLocaleString("en-US", { month: "short" });
  const day = date.getDate();
  const year = date.getFullYear();
  return year === currentYear ? `${month} ${day}` : `${month} ${day} ${year}`;
});

const currentPlannedRecipes = computed(() =>
  plannedRecipes.value.filter((r) => r.planned_for.startsWith(toDateKey(selectedDate.value)))
);

async function getPlannedRecipes() {
  try {
    const date = selectedDate.value;
    const start = new Date(date.getFullYear(), date.getMonth(), 1);
    const end = new Date(date.getFullYear(), date.getMonth() + 1, 0);
    start.setHours(0, 0, 0, 0);
    end.setHours(23, 59, 59, 999);

    const response = await post<PlannedRecipeDetail[]>("/planned-recipe/time-frame/", {
      start: start.toISOString(),
      end: end.toISOString()
    });
    plannedRecipes.value = response;
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
  // Refetch when month changes
  getPlannedRecipes();
});

onMounted(() => {
  getPlannedRecipes();
  getRecipes();
});
</script>

<template>
  <div class="px-4 pt-5 pb-4">
    <h1 class="text-xl font-bold">Planner</h1>
    <p class="mt-1 text-sm text-muted-foreground">Build the week, one dinner at a time</p>

    <div class="mt-4 overflow-hidden rounded-xl border border-border bg-card p-2">
      <Calendar v-model="calendarValue" class="w-full [--cell-size:--spacing(9)]" />
    </div>

    <div class="mt-4 rounded-xl border border-border bg-card p-4">
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

      <Button class="mt-4 w-full" @click="openAssign">
        {{ currentPlannedRecipes.length ? "Change recipes" : "Add recipes" }}
      </Button>
    </div>

    <Dialog v-model:open="showRecipeDialog">
      <DialogContent class="max-w-sm max-h-[80dvh] overflow-hidden border-border bg-card">
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
