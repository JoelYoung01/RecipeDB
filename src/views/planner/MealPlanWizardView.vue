<script setup lang="ts">
import WizardPrefsFields from "@/components/planner/WizardPrefsFields.vue";
import WizardProgressPanel from "@/components/planner/WizardProgressPanel.vue";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useMealPlanWizardPrefs } from "@/composables/useMealPlanWizardPrefs";
import { addDays, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/media";
import { paths } from "@/sitemap";
import {
  emptyWizardPrefs,
  type MealPlanWizardProgressEvent,
  type MealPlanWizardSession,
  type MealPlanWizardStep
} from "@/types";
import { get, patch, post, postSse } from "@/utils";
import { ArrowLeft, Check, LoaderCircle, RefreshCw, Sparkles } from "@lucide/vue";
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
const assignments = ref<Record<string, string>>({});
let abortController: AbortController | null = null;

const today = startOfDay();
const weekStart = startOfWeekMonday(today);
const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

const selectCount = computed(() => session.value?.select_count ?? selectedDays.value.length);

const canContinueDays = computed(() => selectedDays.value.length > 0);

const canContinueSelect = computed(
  () => selectedIdeaIds.value.length === selectCount.value && selectCount.value > 0
);

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

function parseDaysFromQuery(): string[] {
  const raw = typeof route.query.days === "string" ? route.query.days : "";
  if (!raw) return [];
  return raw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => /^\d{4}-\d{2}-\d{2}$/.test(s));
}

function toggleDay(key: string) {
  if (selectedDays.value.includes(key)) {
    selectedDays.value = selectedDays.value.filter((d) => d !== key);
  } else {
    selectedDays.value = [...selectedDays.value, key].sort();
  }
}

function dayLabel(key: string) {
  const [y, m, d] = key.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

async function ensureSession(): Promise<MealPlanWizardSession> {
  if (session.value) return session.value;
  const created = await post<MealPlanWizardSession>("/meal-plan-wizard/sessions/", {
    days: selectedDays.value,
    prefs: localPrefs.value
  });
  session.value = created;
  return created;
}

async function syncDaysAndPrefs() {
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
  if (selectedIdeaIds.value.includes(id)) {
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

async function runBuild(refinement?: string) {
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
      { refinement: refinement || null },
      (event) => {
        if (event.status === "done") return;
        liveEvents.value = [...liveEvents.value, event];
        if (event.status === "error") error.value = event.message;
      },
      abortController.signal
    );
    await refreshSession();
    // Default zip assignments
    const next: Record<string, string> = {};
    const days = session.value?.days ?? [];
    const recipes = session.value?.built_recipes ?? [];
    days.forEach((day, i) => {
      if (recipes[i]) next[day] = recipes[i].idea_id;
    });
    assignments.value = next;
    refineText.value = "";
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
    await runBuild(text);
  }
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
    const payload = {
      assignments: Object.entries(assignments.value).map(([day, idea_id]) => ({
        day,
        idea_id
      }))
    };
    await post(`/meal-plan-wizard/sessions/${session.value.id}/commit/`, payload);
    router.push(paths.planner);
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Could not save plan";
  } finally {
    busy.value = false;
  }
}

function recipeForIdea(ideaId: string) {
  return session.value?.built_recipes.find((r) => r.idea_id === ideaId);
}

onMounted(() => {
  localPrefs.value = { ...savedPrefs.value };
  const fromQuery = parseDaysFromQuery();
  if (fromQuery.length) {
    selectedDays.value = fromQuery;
  } else {
    // Default: all days in the current week selected (user can deselect)
    selectedDays.value = weekDays.map(toDateKey);
  }
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
        v-if="session?.stubbed !== false"
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
      <p class="text-sm text-muted-foreground">
        Deselect nights you already have plans for. We’ll cover the rest.
      </p>
      <div class="mt-3 overflow-hidden rounded-xl border border-border bg-card">
        <button
          v-for="(day, i) in weekDays"
          :key="toDateKey(day)"
          type="button"
          class="flex w-full items-center gap-3 border-b border-border px-3 py-3 text-left last:border-b-0"
          :class="selectedDays.includes(toDateKey(day)) ? 'bg-[rgba(34,197,94,0.1)]' : 'opacity-60'"
          @click="toggleDay(toDateKey(day))"
        >
          <span
            class="flex size-5 items-center justify-center rounded-md border"
            :class="
              selectedDays.includes(toDateKey(day))
                ? 'border-[#16a34a] bg-[#16a34a] text-white'
                : 'border-border'
            "
          >
            <Check v-if="selectedDays.includes(toDateKey(day))" class="size-3.5" />
          </span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-semibold">{{ DAY_LABELS[i] }} · {{ day.getDate() }}</p>
            <p class="text-[11px] text-muted-foreground">
              {{ toDateKey(day) === toDateKey(today) ? "Today" : dayLabel(toDateKey(day)) }}
            </p>
          </div>
        </button>
      </div>
      <p class="mt-2 text-xs text-faint">{{ selectedDays.length }} night(s) selected</p>
      <Button
        type="button"
        class="mt-4 w-full"
        data-testid="wizard-continue-days"
        :disabled="!canContinueDays || busy"
        @click="goForwardFromDays"
      >
        Continue
      </Button>
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
          Choose <span class="font-semibold text-foreground">{{ selectCount }}</span> of
          {{ session?.ideas.length ?? 0 }} ideas
        </p>
        <p class="text-xs tabular-nums text-faint">
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
            selectedIdeaIds.includes(idea.id)
              ? 'border-[rgba(34,197,94,0.45)] bg-[rgba(34,197,94,0.12)]'
              : 'border-border bg-card'
          "
          @click="toggleIdea(idea.id)"
        >
          <span
            class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-md border"
            :class="
              selectedIdeaIds.includes(idea.id)
                ? 'border-[#16a34a] bg-[#16a34a] text-white'
                : 'border-border'
            "
          >
            <Check v-if="selectedIdeaIds.includes(idea.id)" class="size-3.5" />
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
        Assign each built recipe to a night, then save to your planner.
      </p>

      <div class="space-y-3">
        <div
          v-for="day in session?.days ?? []"
          :key="day"
          class="rounded-xl border border-border bg-card p-3"
        >
          <p class="text-xs font-semibold uppercase tracking-wide text-faint">
            {{ dayLabel(day) }}
          </p>
          <select
            class="mt-2 w-full rounded-lg border border-border bg-secondary px-3 py-2 text-sm"
            :value="assignments[day] || ''"
            @change="assignments[day] = ($event.target as HTMLSelectElement).value"
          >
            <option disabled value="">Choose recipe</option>
            <option
              v-for="recipe in session?.built_recipes ?? []"
              :key="recipe.idea_id"
              :value="recipe.idea_id"
            >
              {{ recipe.title }}
            </option>
          </select>
          <p
            v-if="assignments[day] && recipeForIdea(assignments[day])"
            class="mt-2 line-clamp-2 text-xs text-muted-foreground"
          >
            {{ recipeForIdea(assignments[day])?.description }}
          </p>
        </div>
      </div>

      <details class="rounded-xl border border-border bg-card px-3 py-2">
        <summary class="cursor-pointer text-sm font-semibold">Adjust goals / diet</summary>
        <div class="mt-3 pb-2">
          <WizardPrefsFields v-model="localPrefs" />
          <Button size="sm" variant="secondary" class="mt-2" :disabled="busy" @click="runIdeate()">
            Apply & re-ideate (drops later steps)
          </Button>
        </div>
      </details>

      <div class="rounded-xl border border-border bg-card p-3">
        <p class="text-sm font-semibold">Refine recipes</p>
        <p class="mt-0.5 text-xs text-muted-foreground">
          Continues the build conversation with your notes.
        </p>
        <Textarea
          v-model="refineText"
          class="mt-2 min-h-16"
          placeholder="Make Tuesday spicier, cut cook time, use chicken instead of tofu…"
        />
        <Button
          variant="secondary"
          size="sm"
          class="mt-2 gap-1.5"
          :disabled="busy || !refineText.trim()"
          @click="applyRefinement"
        >
          <RefreshCw class="size-3.5" />
          Rebuild with feedback
        </Button>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <Button variant="outline" :disabled="busy" @click="rewindTo('select')">Back</Button>
        <Button :disabled="busy" @click="commitPlan">Save to planner</Button>
      </div>
    </section>
  </div>
</template>
