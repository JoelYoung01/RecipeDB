<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { addDays, endOfDay, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/media";
import { usePlannerStore } from "@/stores/planner";
import { syncAfterPlanMutation } from "@/stores/sync";
import type { PlannedRecipeDetail, RecipeCard } from "@/types";
import { post, toast } from "@/utils";
import { Check } from "@lucide/vue";
import { computed, ref, watch } from "vue";

const props = defineProps<{ recipe: RecipeCard | null }>();
const open = defineModel<boolean>("open", { required: true });

/** Days offered in the picker; the planner range fetched is wider (8 weeks). */
const DAY_COUNT = 14;

const plannerStore = usePlannerStore();

const baseDate = ref(startOfDay());
const selectedKey = ref<string | null>(null);
const loadingDays = ref(false);
const saving = ref(false);

const plannedByKey = computed(() => {
  const map = new Map<string, PlannedRecipeDetail[]>();
  for (const p of plannerStore.plannedRecipes) {
    const key = p.planned_for.slice(0, 10);
    const list = map.get(key) ?? [];
    list.push(p);
    map.set(key, list);
  }
  return map;
});

const days = computed(() =>
  Array.from({ length: DAY_COUNT }, (_, i) => {
    const date = addDays(baseDate.value, i);
    const key = toDateKey(date);
    return {
      date,
      key,
      label:
        i === 0
          ? "Tonight"
          : i === 1
            ? "Tomorrow"
            : date.toLocaleDateString(undefined, { weekday: "long" }),
      dateLabel: date.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      planned: plannedByKey.value.get(key) ?? []
    };
  })
);

const firstOpenKey = computed(() => days.value.find((d) => d.planned.length === 0)?.key ?? null);

const description = computed(() => {
  const name = props.recipe?.name ?? "this recipe";
  return firstOpenKey.value && !loadingDays.value
    ? `Pick a night for “${name}” — the next open one is preselected.`
    : `Pick a night for “${name}”.`;
});

watch(open, async (isOpen) => {
  if (!isOpen || !props.recipe) return;
  baseDate.value = startOfDay();
  selectedKey.value = null;
  loadingDays.value = true;
  try {
    // Same window as the planner view so both share the store cache.
    const weekStart = startOfWeekMonday(baseDate.value);
    await plannerStore.ensureRange(weekStart, endOfDay(addDays(weekStart, 55)));
  } catch (er) {
    console.error(er);
    toast.fromError(er, "Couldn’t load your meal plan.");
  }
  loadingDays.value = false;
  selectedKey.value = firstOpenKey.value ?? days.value[0]?.key ?? null;
});

async function schedule() {
  const recipe = props.recipe;
  const day = days.value.find((d) => d.key === selectedKey.value);
  if (!recipe || !day || saving.value) return;
  saving.value = true;
  try {
    await post("/planned-recipe/", {
      recipe_id: recipe.id,
      planned_for: day.date.toISOString()
    });
    syncAfterPlanMutation();
    open.value = false;
    toast.success(
      `Planned for ${day.label === "Tonight" ? "tonight" : `${day.label}, ${day.dateLabel}`}.`
    );
  } catch (er) {
    console.error(er);
    toast.fromError(er, "Couldn’t add this recipe to your plan.");
  }
  saving.value = false;
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="max-w-sm border-border bg-card">
      <DialogHeader>
        <DialogTitle>Add to plan</DialogTitle>
        <DialogDescription>{{ description }}</DialogDescription>
      </DialogHeader>

      <div class="max-h-[45dvh] overflow-y-auto rounded-xl border border-border">
        <template v-if="loadingDays">
          <div
            v-for="n in 5"
            :key="n"
            class="flex items-center gap-3 border-b border-border px-3 py-3 last:border-b-0"
          >
            <div class="min-w-0 flex-1 space-y-1.5">
              <Skeleton class="h-3.5 w-24" />
              <Skeleton class="h-2.5 w-14" />
            </div>
            <Skeleton class="h-3 w-10" />
          </div>
        </template>
        <template v-else>
          <button
            v-for="day in days"
            :key="day.key"
            type="button"
            class="flex w-full items-center gap-3 border-b border-border px-3 py-2.5 text-left transition-colors last:border-b-0"
            :class="day.key === selectedKey ? 'bg-[rgba(34,197,94,0.1)]' : 'active:bg-secondary/50'"
            @click="selectedKey = day.key"
          >
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold">{{ day.label }}</p>
              <p class="text-[11px] text-faint">{{ day.dateLabel }}</p>
            </div>
            <span v-if="day.planned.length === 0" class="text-[11px] font-semibold text-[#4ade80]">
              Open
            </span>
            <span v-else class="max-w-[45%] truncate text-[11px] text-faint">
              {{ day.planned[0].recipe.name
              }}<template v-if="day.planned.length > 1"> +{{ day.planned.length - 1 }}</template>
            </span>
            <Check
              v-if="day.key === selectedKey"
              class="size-4 shrink-0 text-[#22c55e]"
              :stroke-width="2.5"
            />
          </button>
        </template>
      </div>

      <DialogFooter class="gap-2">
        <Button variant="outline" :disabled="saving" @click="open = false">Cancel</Button>
        <Button :disabled="!selectedKey || loadingDays || saving" @click="schedule">
          {{ saving ? "Adding…" : "Add to plan" }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
