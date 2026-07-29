<script setup lang="ts">
import { addDays, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/media";
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

defineProps<{
  plannedKeys: Set<string>;
}>();

const emit = defineEmits<{
  selectDay: [date: Date];
  /** Fired with the center week, plus a range covering prev/current/next for dots. */
  weekChange: [weekStart: Date, weekDays: Date[], rangeStart: Date, rangeEnd: Date];
}>();

const DAY_LABELS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
const SWIPE_THRESHOLD_RATIO = 0.22;
const SWIPE_VELOCITY = 0.45; // px/ms
const SNAP_MS = 280;

const today = startOfDay();
const thisWeekStart = startOfWeekMonday(today);

/** 0 = this week; negative = past; positive = future */
const weekOffset = ref(0);

const viewportEl = ref<HTMLElement | null>(null);
const trackEl = ref<HTMLElement | null>(null);
const viewportWidth = ref(0);

/** Pixel offset of the track. Resting position centers the middle (current) week. */
const translateX = ref(0);
const animating = ref(false);
const dragging = ref(false);

let startX = 0;
let startY = 0;
let startTranslate = 0;
let startTime = 0;
let axis: "x" | "y" | null = null;
let activePointerId: number | null = null;
let pressedDayKey: string | null = null;
let resizeObserver: ResizeObserver | null = null;

const centerWeekStart = computed(() => addDays(thisWeekStart, weekOffset.value * 7));

const panels = computed(() => {
  const center = weekOffset.value;
  return [
    { offset: center - 1, days: daysForOffset(center - 1) },
    { offset: center, days: daysForOffset(center) },
    { offset: center + 1, days: daysForOffset(center + 1) }
  ];
});

const weekLabel = computed(() => labelForOffset(weekOffset.value));

const restingTranslate = computed(() => -viewportWidth.value);

const trackStyle = computed(() => ({
  width: viewportWidth.value ? `${viewportWidth.value * 3}px` : "300%",
  transform: `translate3d(${translateX.value}px, 0, 0)`,
  transition: animating.value ? `transform ${SNAP_MS}ms cubic-bezier(0.22, 1, 0.36, 1)` : "none"
}));

const panelStyle = computed(() => ({
  width: viewportWidth.value ? `${viewportWidth.value}px` : "33.333%"
}));

watch(
  centerWeekStart,
  (start) => {
    const days = daysForOffset(weekOffset.value);
    const rangeStart = addDays(start, -7);
    const rangeEnd = addDays(start, 13);
    emit("weekChange", start, days, rangeStart, rangeEnd);
  },
  { immediate: true }
);

function daysForOffset(offset: number): Date[] {
  const start = addDays(thisWeekStart, offset * 7);
  return Array.from({ length: 7 }, (_, i) => addDays(start, i));
}

function labelForOffset(offset: number): string {
  if (offset === 0) return "This week";
  if (offset === -1) return "Last week";
  if (offset === 1) return "Next week";
  const start = addDays(thisWeekStart, offset * 7);
  const end = addDays(start, 6);
  const opts: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  return `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
}

function measure() {
  viewportWidth.value = viewportEl.value?.clientWidth ?? 0;
  if (!dragging.value && !animating.value) {
    translateX.value = restingTranslate.value;
  }
}

function dayFromKey(key: string | null): Date | null {
  if (!key) return null;
  for (const panel of panels.value) {
    const hit = panel.days.find((d) => toDateKey(d) === key);
    if (hit) return hit;
  }
  return null;
}

async function snapTo(delta: -1 | 0 | 1) {
  if (!viewportWidth.value) return;

  if (delta === 0) {
    animating.value = true;
    translateX.value = restingTranslate.value;
    window.setTimeout(() => {
      animating.value = false;
    }, SNAP_MS + 20);
    return;
  }

  animating.value = true;
  // Prev panel is at 0, current at -width, next at -2*width
  translateX.value = delta < 0 ? 0 : -viewportWidth.value * 2;

  await new Promise<void>((resolve) => {
    window.setTimeout(resolve, SNAP_MS + 20);
  });

  // Recenter without animation: shift the logical week, rebuild panels, reset translate.
  animating.value = false;
  weekOffset.value += delta;
  await nextTick();
  translateX.value = restingTranslate.value;
}

function goToThisWeek() {
  if (weekOffset.value === 0) return;
  const delta = weekOffset.value > 0 ? -1 : 1;
  // If we're adjacent, animate; otherwise jump.
  if (Math.abs(weekOffset.value) === 1) {
    void snapTo(delta as -1 | 1);
  } else {
    animating.value = false;
    weekOffset.value = 0;
    translateX.value = restingTranslate.value;
  }
}

function onPointerDown(event: PointerEvent) {
  if (event.button !== 0 || animating.value) return;
  dragging.value = true;
  axis = null;
  activePointerId = event.pointerId;
  startX = event.clientX;
  startY = event.clientY;
  startTranslate = translateX.value;
  startTime = performance.now();

  const target = event.target;
  const el = target instanceof Element ? target.closest("[data-day-key]") : null;
  pressedDayKey = el?.getAttribute("data-day-key") ?? null;

  viewportEl.value?.setPointerCapture?.(event.pointerId);
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) return;
  if (activePointerId !== null && event.pointerId !== activePointerId) return;

  const dx = event.clientX - startX;
  const dy = event.clientY - startY;

  if (axis === null) {
    if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
    axis = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
    if (axis === "y") {
      cancelDrag();
      return;
    }
  }

  if (axis !== "x") return;
  event.preventDefault();
  translateX.value = startTranslate + dx;
}

function finishDrag() {
  if (!dragging.value) return;
  const dx = translateX.value - startTranslate;
  const dt = Math.max(performance.now() - startTime, 1);
  const velocity = dx / dt;
  const key = pressedDayKey;
  const wasHorizontal = axis === "x";

  dragging.value = false;
  activePointerId = null;
  pressedDayKey = null;
  axis = null;

  const width = viewportWidth.value || 1;
  const distanceCommit = Math.abs(dx) >= width * SWIPE_THRESHOLD_RATIO;
  const velocityCommit = Math.abs(velocity) >= SWIPE_VELOCITY;
  const shouldFlip = wasHorizontal && (distanceCommit || velocityCommit);

  if (shouldFlip) {
    void snapTo(dx < 0 ? 1 : -1);
    return;
  }

  // Treat near-stationary releases as day taps, even if axis locked to x from jitter.
  const day = dayFromKey(key);
  if (day && Math.abs(dx) < 12) {
    translateX.value = restingTranslate.value;
    emit("selectDay", day);
    return;
  }

  if (wasHorizontal) {
    void snapTo(0);
    return;
  }

  translateX.value = restingTranslate.value;
  if (day) emit("selectDay", day);
}

function cancelDrag() {
  dragging.value = false;
  activePointerId = null;
  axis = null;
  pressedDayKey = null;
  translateX.value = restingTranslate.value;
}

function onPointerUp(event: PointerEvent) {
  if (activePointerId !== null && event.pointerId !== activePointerId) return;
  finishDrag();
}

onMounted(() => {
  measure();
  resizeObserver = new ResizeObserver(() => measure());
  if (viewportEl.value) resizeObserver.observe(viewportEl.value);
});

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
});

defineExpose({
  weekStart: centerWeekStart,
  weekOffset,
  goToThisWeek
});
</script>

<template>
  <div class="select-none">
    <div class="mb-2 flex items-center justify-between gap-2">
      <p class="text-xs font-semibold text-muted-foreground">{{ weekLabel }}</p>
      <button
        v-if="weekOffset !== 0"
        type="button"
        class="text-[11.5px] font-semibold text-[#22c55e] transition-opacity active:opacity-70"
        @click="goToThisWeek"
      >
        Jump to this week
      </button>
      <p v-else class="text-[11px] text-faint">Swipe for more weeks</p>
    </div>

    <div
      ref="viewportEl"
      class="touch-pan-y overflow-hidden"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="cancelDrag"
      @lostpointercapture="finishDrag"
    >
      <div ref="trackEl" class="flex will-change-transform" :style="trackStyle">
        <div
          v-for="panel in panels"
          :key="panel.offset"
          class="grid shrink-0 grid-cols-7 gap-1 px-0"
          :style="panelStyle"
        >
          <div
            v-for="(day, i) in panel.days"
            :key="`${panel.offset}-${toDateKey(day)}`"
            role="button"
            tabindex="0"
            :data-day-key="toDateKey(day)"
            class="cursor-pointer rounded-lg px-0.5 py-1.5 text-center transition-colors"
            :class="
              toDateKey(day) === toDateKey(today)
                ? 'border border-[rgba(34,197,94,0.35)] bg-[rgba(34,197,94,0.12)]'
                : 'border border-transparent'
            "
            @keydown.enter.prevent="emit('selectDay', day)"
            @keydown.space.prevent="emit('selectDay', day)"
          >
            <div
              class="text-[10px] font-semibold tracking-wide"
              :class="
                toDateKey(day) === toDateKey(today) ? 'font-bold text-[#22c55e]' : 'text-faint'
              "
            >
              {{ DAY_LABELS[i] }}
            </div>
            <div
              class="mt-0.5 text-[13px] font-bold leading-none tabular-nums"
              :class="toDateKey(day) === toDateKey(today) ? 'text-[#22c55e]' : 'text-foreground'"
            >
              {{ day.getDate() }}
            </div>
            <div
              class="mx-auto mt-1.5 size-1.5 rounded-full"
              :class="plannedKeys.has(toDateKey(day)) ? 'bg-[#22c55e]' : 'bg-[#3f463f]'"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
