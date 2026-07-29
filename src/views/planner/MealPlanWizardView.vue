<script setup lang="ts">
import WizardPrefsFields from "@/components/planner/WizardPrefsFields.vue";
import WizardProgressPanel from "@/components/planner/WizardProgressPanel.vue";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useMealPlanWizardPrefs } from "@/composables/useMealPlanWizardPrefs";
import { addDays, endOfDay, formatPrepTime, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/media";
import { paths } from "@/sitemap";
import {
  emptyWizardPrefs,
  type MealPlanWizardBuiltRecipe,
  type MealPlanWizardProgressEvent,
  type MealPlanWizardSession,
  type MealPlanWizardStep,
  type PlannedRecipeDetail
} from "@/types";
import { get, patch, post, postSse } from "@/utils";
import { ArrowLeft, Check, ChevronDown, LoaderCircle, RefreshCw, Sparkles } from "@lucide/vue";
import { computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const { prefs: savedPrefs, save: persistPrefs } = useMealPlanWizardPrefs();

const DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

type UiStep = "days" | "prefs" | "ideate" | "select" | "build" | "review";

const uiStep = ref<UiStep>("days");
const session = ref<MealPlanWizardSession | null>(null);
const localPrefs = ref(emptyWizardPrefs());
const selectedDays = ref<string[]>([]);
const selectedIdeaIds = ref<string[]>([]);
const liveEvents = ref<MealPlanWizardProgressEvent[]>([]);
const running = ref(false);
const error = ref("");
const refineText = ref("");
const busy = ref(false);
const loadingDays = ref(true);
/** Existing dinner titles keyed by YYYY-MM-DD for this week. */
const plannedTitles = ref<Record<string, string>>({});
/** Day keys expanded on the review screen. */
const expandedDays = ref<string[]>([]);
/** Idea ids marked for regeneration on refine. */
const regenIdeaIds = ref<string[]>([]);
let abortController: AbortController | null = null;

const today = startOfDay();
/** The single week this wizard session is scoped to (always 7 days). */
const weekDays = ref<Date[]>(
  Array.from({ length: 7 }, (_, i) => addDays(startOfWeekMonday(today), i))
);

const weekDayKeys = computed(() => weekDays.value.map(toDateKey));
const weekKeySet = computed(() => new Set(weekDayKeys.value));

const selectCount = computed(() => session.value?.select_count ?? selectedDays.value.length);

const canContinueDays = computed(() => selectedDays.value.length > 0);

const skippedCount = computed(() => weekDayKeys.value.length - selectedDays.value.length);

const openNightKeys = computed(() => weekDayKeys.value.filter((key) => !plannedTitles.value[key]));

const alreadyPlannedCount = computed(() => Object.keys(plannedTitles.value).length);

/** Readonly day → recipe pairs in plan order (no reassignment). */
const planRows = computed(() => {
  const days = session.value?.days ?? [];
  const recipes = session.value?.built_recipes ?? [];
  return days.map((day, i) => ({
    day,
    recipe: recipes[i] ?? null
  }));
});

const canRefineRecipes = computed(
  () => Boolean(refineText.value.trim()) && regenIdeaIds.value.length > 0 && !busy.value
);

const weekHeading = computed(() => {
  const start = weekDays.value[0];
  if (!start) return "This week";
  const thisWeek = startOfWeekMonday(today);
  const nextWeek = addDays(thisWeek, 7);
  if (toDateKey(start) === toDateKey(thisWeek)) return "This week";
  if (toDateKey(start) === toDateKey(nextWeek)) return "Next week";
  const end = weekDays.value[6] ?? start;
  const opts: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  return `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
});

const canContinueSelect = computed(
  () => selectedIdeaIds.value.length === selectCount.value && selectCount.value > 0
);

const selectionFull = computed(
  () => selectedIdeaIds.value.length >= selectCount.value && selectCount.value > 0
);

function isIdeaSelected(id: string) {
  return selectedIdeaIds.value.includes(id);
}

function isIdeaDisabled(id: string) {
  // Once the quota is filled, lock unselected ideas so it's obvious you're done.
  // Selected ones stay clickable so the user can swap.
  return selectionFull.value && !isIdeaSelected(id);
}

const STEP_ORDER: UiStep[] = ["days", "prefs", "ideate", "select", "build", "review"];

const stepIndex = computed(() => STEP_ORDER.indexOf(uiStep.value));

function previousStep(step: UiStep): UiStep {
  if (step === "prefs") return "days";
  if (step === "ideate") return "prefs";
  if (step === "select") return "prefs";
  if (step === "build") return "select";
  if (step === "review") return "select";
  return "days";
}

async function goBack() {
  if (uiStep.value === "days") {
    router.push(paths.planner);
    return;
  }
  const target = previousStep(uiStep.value);
  // Transitional pipeline screens: abandon in-flight work and return.
  abortController?.abort();
  running.value = false;
  await rewindTo(target);
}

const headerTitle = computed(() => {
  switch (uiStep.value) {
    case "days":
      return "Which nights?";
    case "prefs":
      return "Set the vibe";
    case "ideate":
      return "Cooking up ideas";
    case "select":
      return "Pick your dinners";
    case "build":
      return "Building recipes";
    case "review":
      return "Lock the plan";
    default:
      return "Plan meals";
  }
});

function parseDateKey(key: string): Date | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(key)) return null;
  const [y, m, d] = key.split("-").map(Number);
  return startOfDay(new Date(y, m - 1, d));
}

function parseDaysFromQuery(): string[] {
  const raw = typeof route.query.days === "string" ? route.query.days : "";
  if (!raw) return [];
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => Boolean(parseDateKey(s)));
}

function weekFromSeed(seed: Date): Date[] {
  const start = startOfWeekMonday(seed);
  return Array.from({ length: 7 }, (_, i) => addDays(start, i));
}

function clampDaysToWeek(keys: string[], weekKeys: string[]): string[] {
  const allowed = new Set(weekKeys);
  return [...new Set(keys.filter((k) => allowed.has(k)))].sort();
}

function isDaySelected(key: string) {
  return selectedDays.value.includes(key);
}

function plannedTitleFor(key: string): string | null {
  return plannedTitles.value[key] ?? null;
}

function toggleDay(key: string) {
  // Only the 7 nights in this wizard's week can be toggled.
  if (!weekKeySet.value.has(key)) return;
  if (isDaySelected(key)) {
    selectedDays.value = selectedDays.value.filter((d) => d !== key);
  } else {
    selectedDays.value = clampDaysToWeek([...selectedDays.value, key], weekDayKeys.value);
  }
}

function selectAllOpenNights() {
  selectedDays.value = [...openNightKeys.value];
}

function clearWeekDays() {
  selectedDays.value = [];
}

function dayLabel(key: string) {
  const date = parseDateKey(key);
  if (!date) return key;
  return date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

async function loadPlannedForWeek(days: Date[]): Promise<Record<string, string>> {
  if (!days.length) return {};
  const start = days[0]!;
  const end = days[days.length - 1]!;
  try {
    const plans = await post<PlannedRecipeDetail[]>("/planned-recipe/time-frame/", {
      start: startOfDay(start).toISOString(),
      end: endOfDay(end).toISOString()
    });
    const titles: Record<string, string> = {};
    for (const plan of plans) {
      const key = plan.planned_for.slice(0, 10);
      // Keep the first dinner title if multiple are planned that day.
      if (!titles[key]) titles[key] = plan.recipe.name;
    }
    return titles;
  } catch (er) {
    console.error(er);
    return {};
  }
}

function planningDays(): string[] {
  return clampDaysToWeek(selectedDays.value, weekDayKeys.value);
}

async function ensureSession(): Promise<MealPlanWizardSession> {
  if (session.value) return session.value;
  const created = await post<MealPlanWizardSession>("/meal-plan-wizard/sessions/", {
    days: planningDays(),
    prefs: localPrefs.value
  });
  session.value = created;
  return created;
}

async function syncDaysAndPrefs() {
  // Keep selection strictly inside this week's 7 nights before talking to the API.
  selectedDays.value = planningDays();
  persistPrefs(localPrefs.value);
  const s = await ensureSession();
  const [daysRes, prefsRes] = await Promise.all([
    patch<MealPlanWizardSession>(`/meal-plan-wizard/sessions/${s.id}/days/`, {
      days: selectedDays.value
    }),
    patch<MealPlanWizardSession>(`/meal-plan-wizard/sessions/${s.id}/prefs/`, localPrefs.value)
  ]);
  session.value = prefsRes ?? daysRes;
  selectedIdeaIds.value = session.value.selected_idea_ids;
}

function goForwardFromDays() {
  if (!canContinueDays.value) return;
  error.value = "";
  // Days → prefs is local; the server session is created when ideation starts.
  uiStep.value = "prefs";
}

async function refreshSession() {
  if (!session.value) return;
  session.value = await get<MealPlanWizardSession>(
    `/meal-plan-wizard/sessions/${session.value.id}/`
  );
}

async function runIdeate(refinement?: string) {
  error.value = "";
  busy.value = true;
  running.value = true;
  liveEvents.value = [];
  uiStep.value = "ideate";
  try {
    await syncDaysAndPrefs();
    const s = session.value!;
    abortController?.abort();
    abortController = new AbortController();
    await postSse<MealPlanWizardProgressEvent>(
      `/meal-plan-wizard/sessions/${s.id}/ideate/`,
      { refinement: refinement || null },
      (event) => {
        if (event.status === "done") return;
        liveEvents.value = [...liveEvents.value, event];
        if (event.status === "error") error.value = event.message;
      },
      abortController.signal
    );
    await refreshSession();
    selectedIdeaIds.value = session.value?.selected_idea_ids ?? [];
    refineText.value = "";
    if (!error.value) uiStep.value = "select";
  } catch (e) {
    if ((e as Error).name !== "AbortError") {
      error.value = e instanceof Error ? e.message : "Ideation failed";
    }
  } finally {
    running.value = false;
    busy.value = false;
  }
}

function toggleIdea(id: string) {
  if (isIdeaDisabled(id)) return;
  if (isIdeaSelected(id)) {
    selectedIdeaIds.value = selectedIdeaIds.value.filter((x) => x !== id);
    return;
  }
  if (selectedIdeaIds.value.length >= selectCount.value) return;
  selectedIdeaIds.value = [...selectedIdeaIds.value, id];
}

async function confirmSelectionAndBuild(refinement?: string) {
  const current = session.value;
  if (!current || !canContinueSelect.value) return;
  error.value = "";
  busy.value = true;
  try {
    // Allow prefs edits on select step to apply (drops future if changed)
    persistPrefs(localPrefs.value);
    const afterPrefs = await patch<MealPlanWizardSession>(
      `/meal-plan-wizard/sessions/${current.id}/prefs/`,
      localPrefs.value
    );
    session.value = afterPrefs;
    if (!afterPrefs.ideas.length) {
      await runIdeate();
      return;
    }
    session.value = await post<MealPlanWizardSession>(
      `/meal-plan-wizard/sessions/${afterPrefs.id}/select/`,
      { idea_ids: selectedIdeaIds.value }
    );
    await runBuild(refinement);
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Could not continue";
    busy.value = false;
  }
}

async function runBuild(refinement?: string, ideaIds?: string[]) {
  if (!session.value) return;
  error.value = "";
  busy.value = true;
  running.value = true;
  liveEvents.value = [];
  uiStep.value = "build";
  try {
    abortController?.abort();
    abortController = new AbortController();
    await postSse<MealPlanWizardProgressEvent>(
      `/meal-plan-wizard/sessions/${session.value.id}/build/`,
      {
        refinement: refinement || null,
        idea_ids: ideaIds?.length ? ideaIds : null
      },
      (event) => {
        if (event.status === "done") return;
        liveEvents.value = [...liveEvents.value, event];
        if (event.status === "error") error.value = event.message;
      },
      abortController.signal
    );
    await refreshSession();
    refineText.value = "";
    regenIdeaIds.value = [];
    if (!error.value) uiStep.value = "review";
  } catch (e) {
    if ((e as Error).name !== "AbortError") {
      error.value = e instanceof Error ? e.message : "Build failed";
    }
  } finally {
    running.value = false;
    busy.value = false;
  }
}

async function applyRefinement() {
  const text = refineText.value.trim();
  if (!text) return;
  if (uiStep.value === "select" || uiStep.value === "ideate") {
    await runIdeate(text);
  } else if (uiStep.value === "review" || uiStep.value === "build") {
    if (!regenIdeaIds.value.length) {
      error.value = "Mark at least one dinner to regenerate.";
      return;
    }
    await runBuild(text, [...regenIdeaIds.value]);
  }
}

function toggleExpanded(day: string) {
  if (expandedDays.value.includes(day)) {
    expandedDays.value = expandedDays.value.filter((d) => d !== day);
  } else {
    expandedDays.value = [...expandedDays.value, day];
  }
}

function isExpanded(day: string) {
  return expandedDays.value.includes(day);
}

function toggleRegen(ideaId: string) {
  if (regenIdeaIds.value.includes(ideaId)) {
    regenIdeaIds.value = regenIdeaIds.value.filter((id) => id !== ideaId);
  } else {
    regenIdeaIds.value = [...regenIdeaIds.value, ideaId];
  }
}

function isMarkedForRegen(ideaId: string) {
  return regenIdeaIds.value.includes(ideaId);
}

function markAllForRegen() {
  regenIdeaIds.value = (session.value?.built_recipes ?? []).map((r) => r.idea_id);
}

function clearRegenMarks() {
  regenIdeaIds.value = [];
}

function formatIngredient(ing: MealPlanWizardBuiltRecipe["ingredients"][number]): string {
  const bits = [
    ing.amount != null ? String(ing.amount) : "",
    ing.units || "",
    ing.name,
    ing.details ? `(${ing.details})` : ""
  ].filter(Boolean);
  return bits.join(" ");
}

async function rewindTo(step: UiStep) {
  if (!session.value) {
    uiStep.value = step;
    return;
  }
  if (step === "days" || step === "prefs") {
    // Clear future on server when leaving LLM stages
    if (session.value.ideas.length || session.value.built_recipes.length) {
      try {
        session.value = await post(`/meal-plan-wizard/sessions/${session.value.id}/rewind/`, {
          to_step: step
        });
      } catch (e) {
        console.error(e);
      }
    }
    selectedIdeaIds.value = [];
    liveEvents.value = [];
    uiStep.value = step;
    return;
  }
  try {
    const rewound = await post<MealPlanWizardSession>(
      `/meal-plan-wizard/sessions/${session.value.id}/rewind/`,
      { to_step: step as MealPlanWizardStep }
    );
    session.value = rewound;
    selectedIdeaIds.value = rewound.selected_idea_ids;
    uiStep.value = step;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Could not go back";
  }
}

async function commitPlan() {
  if (!session.value) return;
  error.value = "";
  busy.value = true;
  try {
    // Zip order: day[i] ↔ built_recipes[i]
    await post(`/meal-plan-wizard/sessions/${session.value.id}/commit/`, {});
    router.push(paths.planner);
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Could not save plan";
  } finally {
    busy.value = false;
  }
}

onMounted(async () => {
  localPrefs.value = { ...savedPrefs.value };
  const fromQuery = parseDaysFromQuery();
  // Scope the wizard to one week: prefer the week of the first queried day.
  const seed = fromQuery.length ? parseDateKey(fromQuery[0]!) ?? today : today;
  weekDays.value = weekFromSeed(seed);
  const keys = weekDayKeys.value;

  loadingDays.value = true;
  plannedTitles.value = await loadPlannedForWeek(weekDays.value);
  loadingDays.value = false;

  // Auto-skip nights that already have a dinner. Prefer the caller's day list
  // (fill-gaps / plan-week / autofill), then drop anything already planned.
  const preferred = fromQuery.length ? clampDaysToWeek(fromQuery, keys) : [...keys];
  selectedDays.value = preferred.filter((key) => !plannedTitles.value[key]);
});

onUnmounted(() => {
  abortController?.abort();
});
</script>

<template>
  <div class="px-4 pt-4 pb-6">
    <div class="flex items-center gap-2">
      <button
        type="button"
        class="flex size-9 items-center justify-center rounded-full border border-border bg-card text-muted-foreground transition-opacity active:opacity-70"
        aria-label="Back"
        @click="goBack"
      >
        <ArrowLeft class="size-4" />
      </button>
      <div class="min-w-0 flex-1">
        <p class="text-[11px] font-bold uppercase tracking-[0.08em] text-success-soft">
          Meal plan wizard
        </p>
        <h1 class="truncate text-lg font-bold">{{ headerTitle }}</h1>
      </div>
      <span
        v-if="session?.stubbed === true"
        class="rounded-full border border-border bg-secondary px-2 py-0.5 text-[10px] font-semibold text-faint"
      >
        Stub LLM
      </span>
    </div>

    <!-- Step dots -->
    <div class="mt-3 flex items-center gap-1.5">
      <button
        v-for="(s, i) in STEP_ORDER"
        :key="s"
        type="button"
        class="h-1 flex-1 rounded-full transition-colors"
        :class="i <= stepIndex ? 'bg-[#16a34a]' : 'bg-secondary'"
        :disabled="i >= stepIndex || running || s === 'ideate' || s === 'build'"
        @click="i < stepIndex && s !== 'ideate' && s !== 'build' && rewindTo(s)"
      />
    </div>

    <p
      v-if="error"
      class="mt-3 rounded-xl border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive"
    >
      {{ error }}
    </p>

    <!-- DAYS -->
    <section v-if="uiStep === 'days'" class="mt-5">
      <div class="flex items-start justify-between gap-3">
        <div class="min-w-0">
          <p class="text-sm font-semibold text-foreground">{{ weekHeading }}</p>
          <p class="mt-0.5 text-sm text-muted-foreground">
            <template v-if="loadingDays">Checking what’s already planned…</template>
            <template v-else-if="alreadyPlannedCount">
              Nights with a dinner are skipped — tap one to replan it anyway.
            </template>
            <template v-else>
              Tap nights to plan. Highlighted nights get a dinner; the rest are skipped.
            </template>
          </p>
        </div>
        <div class="flex shrink-0 gap-2">
          <button
            type="button"
            class="text-[12px] font-semibold text-[#22c55e] transition-opacity active:opacity-70"
            @click="selectAllOpenNights"
          >
            Open
          </button>
          <button
            type="button"
            class="text-[12px] font-semibold text-faint transition-opacity active:opacity-70"
            @click="clearWeekDays"
          >
            None
          </button>
        </div>
      </div>

      <div class="mt-3 overflow-hidden rounded-xl border border-border bg-card">
        <button
          v-for="(day, i) in weekDays"
          :key="toDateKey(day)"
          type="button"
          class="flex w-full items-center gap-3 border-b border-border px-3 py-3 text-left transition-colors last:border-b-0"
          :class="
            isDaySelected(toDateKey(day))
              ? 'bg-[rgba(34,197,94,0.14)]'
              : 'bg-transparent opacity-70'
          "
          :aria-pressed="isDaySelected(toDateKey(day))"
          @click="toggleDay(toDateKey(day))"
        >
          <span
            class="flex size-5 shrink-0 items-center justify-center rounded-md border transition-colors"
            :class="
              isDaySelected(toDateKey(day))
                ? 'border-[#16a34a] bg-[#16a34a] text-white'
                : 'border-border bg-secondary/40'
            "
          >
            <Check v-if="isDaySelected(toDateKey(day))" class="size-3.5" />
          </span>
          <div class="min-w-0 flex-1">
            <p
              class="text-sm font-semibold"
              :class="isDaySelected(toDateKey(day)) ? 'text-foreground' : 'text-muted-foreground'"
            >
              {{ DAY_LABELS[i] }} · {{ day.getDate() }}
              <span
                v-if="toDateKey(day) === toDateKey(today)"
                class="ml-1 text-[11px] font-bold uppercase tracking-wide text-[#22c55e]"
              >
                Today
              </span>
            </p>
            <p
              v-if="plannedTitleFor(toDateKey(day))"
              class="mt-0.5 truncate text-[12px]"
              :class="isDaySelected(toDateKey(day)) ? 'text-muted-foreground' : 'text-[#86efac]/80'"
            >
              {{
                isDaySelected(toDateKey(day))
                  ? `Replace · ${plannedTitleFor(toDateKey(day))}`
                  : plannedTitleFor(toDateKey(day))
              }}
            </p>
            <p v-else class="mt-0.5 text-[11px] text-muted-foreground">
              {{ isDaySelected(toDateKey(day)) ? "Open night" : "Skipping" }}
            </p>
          </div>
          <span
            class="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="
              isDaySelected(toDateKey(day))
                ? 'bg-[rgba(34,197,94,0.18)] text-[#86efac]'
                : plannedTitleFor(toDateKey(day))
                  ? 'bg-secondary text-muted-foreground'
                  : 'bg-secondary text-faint'
            "
          >
            {{
              isDaySelected(toDateKey(day))
                ? plannedTitleFor(toDateKey(day))
                  ? "Replan"
                  : "Plan"
                : plannedTitleFor(toDateKey(day))
                  ? "Kept"
                  : "Skip"
            }}
          </span>
        </button>
      </div>

      <p class="mt-2 text-xs text-faint">
        <template v-if="loadingDays">Loading plans…</template>
        <template v-else>
          Planning {{ selectedDays.length }} of {{ weekDayKeys.length }}
          <span v-if="alreadyPlannedCount"> · {{ alreadyPlannedCount }} already planned </span>
          <span v-else-if="skippedCount"> · skipping {{ skippedCount }}</span>
        </template>
      </p>
      <Button
        type="button"
        class="mt-4 w-full"
        data-testid="wizard-continue-days"
        :disabled="!canContinueDays || busy || loadingDays"
        @click="goForwardFromDays"
      >
        Continue with {{ selectedDays.length }} night{{ selectedDays.length === 1 ? "" : "s" }}
      </Button>
      <p
        v-if="!loadingDays && !selectedDays.length && alreadyPlannedCount"
        class="mt-2 text-center text-xs text-muted-foreground"
      >
        Every night already has a dinner. Tap one to replan it, or head back.
      </p>
    </section>

    <!-- PREFS -->
    <section v-else-if="uiStep === 'prefs'" class="mt-5">
      <p class="mb-4 text-sm text-muted-foreground">
        Everything here is optional. We’ll remember goals and diet for next time.
      </p>
      <WizardPrefsFields v-model="localPrefs" />
      <div class="mt-5 grid grid-cols-2 gap-2">
        <Button variant="outline" :disabled="busy" @click="rewindTo('days')">Back</Button>
        <Button class="gap-1.5" :disabled="busy" @click="runIdeate()">
          <Sparkles class="size-3.5" />
          Generate ideas
        </Button>
      </div>
    </section>

    <!-- IDEATE / BUILD progress -->
    <section v-else-if="uiStep === 'ideate' || uiStep === 'build'" class="mt-5 space-y-4">
      <WizardProgressPanel
        :events="liveEvents"
        :running="running"
        :title="uiStep === 'ideate' ? 'Ideating dinners' : 'Writing full recipes'"
        :subtitle="
          uiStep === 'ideate'
            ? `Aiming for ${session?.idea_target_count ?? selectedDays.length + 5} options`
            : `Building ${selectCount} recipes from your picks`
        "
      />
      <div v-if="!running && error" class="grid grid-cols-2 gap-2">
        <Button variant="outline" @click="rewindTo('prefs')">Edit prefs</Button>
        <Button @click="uiStep === 'ideate' ? runIdeate() : runBuild()">Retry</Button>
      </div>
      <div v-else class="flex items-center justify-center gap-2 py-2 text-sm text-muted-foreground">
        <LoaderCircle class="size-4 animate-spin" />
        Hang tight — the pipeline is moving…
      </div>
    </section>

    <!-- SELECT -->
    <section v-else-if="uiStep === 'select'" class="mt-5 space-y-4">
      <div class="flex items-end justify-between gap-2">
        <p class="text-sm text-muted-foreground">
          <template v-if="selectionFull">
            All set — deselect one if you want to swap.
          </template>
          <template v-else>
            Choose <span class="font-semibold text-foreground">{{ selectCount }}</span> of
            {{ session?.ideas.length ?? 0 }} ideas
          </template>
        </p>
        <p
          class="text-xs tabular-nums"
          :class="selectionFull ? 'font-semibold text-[#86efac]' : 'text-faint'"
        >
          {{ selectedIdeaIds.length }} / {{ selectCount }}
        </p>
      </div>

      <div class="space-y-2">
        <button
          v-for="idea in session?.ideas ?? []"
          :key="idea.id"
          type="button"
          class="flex w-full items-start gap-3 rounded-xl border px-3 py-3 text-left transition-colors"
          :class="
            isIdeaSelected(idea.id)
              ? 'border-[rgba(34,197,94,0.45)] bg-[rgba(34,197,94,0.12)]'
              : isIdeaDisabled(idea.id)
                ? 'cursor-not-allowed border-border/60 bg-card/40 opacity-40'
                : 'border-border bg-card'
          "
          :disabled="isIdeaDisabled(idea.id)"
          :aria-disabled="isIdeaDisabled(idea.id)"
          @click="toggleIdea(idea.id)"
        >
          <span
            class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-md border"
            :class="
              isIdeaSelected(idea.id)
                ? 'border-[#16a34a] bg-[#16a34a] text-white'
                : 'border-border'
            "
          >
            <Check v-if="isIdeaSelected(idea.id)" class="size-3.5" />
          </span>
          <span class="min-w-0">
            <span class="block text-sm font-semibold leading-snug">{{ idea.title }}</span>
          </span>
        </button>
      </div>

      <details class="rounded-xl border border-border bg-card px-3 py-2">
        <summary class="cursor-pointer text-sm font-semibold">Adjust goals / diet</summary>
        <div class="mt-3 pb-2">
          <WizardPrefsFields v-model="localPrefs" />
        </div>
      </details>

      <div class="rounded-xl border border-border bg-card p-3">
        <p class="text-sm font-semibold">Refine ideas</p>
        <p class="mt-0.5 text-xs text-muted-foreground">
          Tweaks re-run ideation with prior context — not from scratch.
        </p>
        <Textarea
          v-model="refineText"
          class="mt-2 min-h-16"
          placeholder="More vegetarian options, less pasta, add a spicy night…"
        />
        <Button
          variant="secondary"
          size="sm"
          class="mt-2 gap-1.5"
          :disabled="busy || !refineText.trim()"
          @click="applyRefinement"
        >
          <RefreshCw class="size-3.5" />
          Re-run with feedback
        </Button>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <Button variant="outline" :disabled="busy" @click="rewindTo('prefs')">Back</Button>
        <Button :disabled="!canContinueSelect || busy" @click="confirmSelectionAndBuild()">
          Build recipes
        </Button>
      </div>
    </section>

    <!-- REVIEW -->
    <section v-else-if="uiStep === 'review'" class="mt-5 space-y-4">
      <p class="text-sm text-muted-foreground">
        Here’s your week. Expand a night for the full recipe, or mark dinners to regenerate.
      </p>

      <div class="space-y-2">
        <div
          v-for="row in planRows"
          :key="row.day"
          class="overflow-hidden rounded-xl border border-border bg-card"
          :class="
            row.recipe && isMarkedForRegen(row.recipe.idea_id)
              ? 'border-[rgba(34,197,94,0.4)]'
              : ''
          "
        >
          <button
            type="button"
            class="flex w-full items-start gap-3 px-3 py-3 text-left transition-colors active:bg-secondary/40"
            @click="toggleExpanded(row.day)"
          >
            <ChevronDown
              class="mt-0.5 size-4 shrink-0 text-faint transition-transform"
              :class="isExpanded(row.day) ? 'rotate-0' : '-rotate-90'"
            />
            <div class="min-w-0 flex-1">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-faint">
                {{ dayLabel(row.day) }}
              </p>
              <p class="mt-0.5 text-sm font-semibold leading-snug">
                {{ row.recipe?.title || "Untitled dinner" }}
              </p>
              <p v-if="row.recipe?.prep_time" class="mt-0.5 text-[11px] text-muted-foreground">
                {{ formatPrepTime(row.recipe.prep_time) }}
              </p>
            </div>
            <label
              v-if="row.recipe"
              class="mt-0.5 flex shrink-0 cursor-pointer items-center gap-1.5 rounded-md border border-border px-2 py-1 text-[10px] font-semibold"
              :class="
                isMarkedForRegen(row.recipe.idea_id)
                  ? 'border-[rgba(34,197,94,0.45)] bg-[rgba(34,197,94,0.12)] text-[#86efac]'
                  : 'text-faint'
              "
              @click.stop
            >
              <input
                type="checkbox"
                class="size-3.5 accent-[#16a34a]"
                :checked="isMarkedForRegen(row.recipe.idea_id)"
                @change="toggleRegen(row.recipe.idea_id)"
              />
              Regen
            </label>
          </button>

          <div
            v-if="row.recipe && isExpanded(row.day)"
            class="space-y-3 border-t border-border px-3 pb-3 pt-2"
          >
            <p v-if="row.recipe.description" class="text-sm text-muted-foreground">
              {{ row.recipe.description }}
            </p>

            <div v-if="row.recipe.ingredients?.length">
              <p class="text-xs font-semibold uppercase tracking-wide text-faint">Ingredients</p>
              <ul class="mt-1.5 space-y-1">
                <li
                  v-for="(ing, idx) in row.recipe.ingredients"
                  :key="`${row.recipe.idea_id}-ing-${idx}`"
                  class="text-sm text-foreground/90"
                >
                  {{ formatIngredient(ing) }}
                </li>
              </ul>
            </div>

            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-faint">Instructions</p>
              <p class="mt-1.5 whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
                {{ row.recipe.instructions }}
              </p>
            </div>

            <p v-if="row.recipe.notes" class="text-xs text-muted-foreground">
              Notes: {{ row.recipe.notes }}
            </p>
          </div>
        </div>
      </div>

      <div class="rounded-xl border border-border bg-card p-3">
        <div class="flex items-center justify-between gap-2">
          <p class="text-sm font-semibold">Refine recipes</p>
          <div class="flex gap-2">
            <button
              type="button"
              class="text-[11.5px] font-semibold text-[#22c55e] transition-opacity active:opacity-70"
              @click="markAllForRegen"
            >
              Mark all
            </button>
            <button
              type="button"
              class="text-[11.5px] font-semibold text-faint transition-opacity active:opacity-70"
              @click="clearRegenMarks"
            >
              Clear
            </button>
          </div>
        </div>
        <p class="mt-0.5 text-xs text-muted-foreground">
          Mark dinners above, then describe changes. Prior turns stay in context so the week
          stays coherent.
        </p>
        <p class="mt-1.5 text-xs tabular-nums text-faint">
          {{ regenIdeaIds.length }} marked for regeneration
        </p>
        <Textarea
          v-model="refineText"
          class="mt-2 min-h-16"
          placeholder="Make the pasta spicier, cut cook time on Tuesday, swap tofu for chicken…"
        />
        <Button
          variant="secondary"
          size="sm"
          class="mt-2 gap-1.5"
          :disabled="!canRefineRecipes"
          @click="applyRefinement"
        >
          <RefreshCw class="size-3.5" />
          Regenerate marked
          <span v-if="regenIdeaIds.length">({{ regenIdeaIds.length }})</span>
        </Button>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <Button variant="outline" :disabled="busy" @click="rewindTo('select')">Back</Button>
        <Button :disabled="busy" @click="commitPlan">Save to planner</Button>
      </div>
    </section>
  </div>
</template>
