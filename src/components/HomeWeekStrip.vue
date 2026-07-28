<script setup lang="ts">
import { addDays, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/media";
import { computed, ref, watch } from "vue";

const props = defineProps<{
  plannedKeys: Set<string>;
}>();

const emit = defineEmits<{
  selectDay: [date: Date];
  weekChange: [weekStart: Date, weekDays: Date[]];
}>();

const DAY_LABELS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
const SWIPE_THRESHOLD = 48;

const today = startOfDay();
const thisWeekStart = startOfWeekMonday(today);

/** 0 = this week; negative = past; positive = future */
const weekOffset = ref(0);
const dragX = ref(0);
const dragging = ref(false);

const trackEl = ref<HTMLElement | null>(null);
let startX = 0;
let startY = 0;
let axis: "x" | "y" | null = null;
let activePointerId: number | null = null;
let pressedDayKey: string | null = null;

const weekStart = computed(() => addDays(thisWeekStart, weekOffset.value * 7));
const weekDays = computed(() =>
  Array.from({ length: 7 }, (_, i) => addDays(weekStart.value, i))
);

const weekLabel = computed(() => {
  if (weekOffset.value === 0) return "This week";
  if (weekOffset.value === -1) return "Last week";
  if (weekOffset.value === 1) return "Next week";
  const start = weekStart.value;
  const end = addDays(start, 6);
  const opts: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
  return `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
});

const trackStyle = computed(() => ({
  transform: `translate3d(${dragX.value}px, 0, 0)`,
  transition: dragging.value ? "none" : "transform 220ms ease-out"
}));

watch(
  weekDays,
  (days) => {
    emit("weekChange", weekStart.value, days);
  },
  { immediate: true }
);

function shiftWeek(delta: number) {
  weekOffset.value += delta;
  dragX.value = 0;
}

function goToThisWeek() {
  weekOffset.value = 0;
  dragX.value = 0;
}

function dayFromKey(key: string | null): Date | null {
  if (!key) return null;
  return weekDays.value.find((d) => toDateKey(d) === key) ?? null;
}

function onPointerDown(event: PointerEvent) {
  if (event.button !== 0) return;
  dragging.value = true;
  axis = null;
  activePointerId = event.pointerId;
  startX = event.clientX;
  startY = event.clientY;

  const target = event.target;
  const el = target instanceof Element ? target.closest("[data-day-key]") : null;
  pressedDayKey = el?.getAttribute("data-day-key") ?? null;

  trackEl.value?.setPointerCapture?.(event.pointerId);
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
  dragX.value = dx * 0.92;
}

function finishDrag() {
  if (!dragging.value) return;
  const dx = dragX.value;
  const key = pressedDayKey;
  dragging.value = false;
  activePointerId = null;
  pressedDayKey = null;
  const swiped = axis === "x" && Math.abs(dx) >= SWIPE_THRESHOLD;
  axis = null;

  if (swiped) {
    // Swipe left (negative dx) → next week; swipe right → previous week
    shiftWeek(dx < 0 ? 1 : -1);
    return;
  }

  dragX.value = 0;
  const day = dayFromKey(key);
  if (day) emit("selectDay", day);
}

function cancelDrag() {
  dragging.value = false;
  activePointerId = null;
  axis = null;
  dragX.value = 0;
  pressedDayKey = null;
}

function onPointerUp(event: PointerEvent) {
  if (activePointerId !== null && event.pointerId !== activePointerId) return;
  finishDrag();
}

defineExpose({
  weekStart,
  weekDays,
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
      ref="trackEl"
      class="touch-pan-y overflow-hidden"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="cancelDrag"
      @lostpointercapture="finishDrag"
    >
      <div class="grid grid-cols-7 gap-1 will-change-transform" :style="trackStyle">
        <div
          v-for="(day, i) in weekDays"
          :key="toDateKey(day)"
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
            :class="toDateKey(day) === toDateKey(today) ? 'font-bold text-[#22c55e]' : 'text-faint'"
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
            :class="plannedKeys.has(toDateKey(day)) ? 'bg-[#22c55e]' : 'bg-[#3f3f46]'"
          />
        </div>
      </div>
    </div>
  </div>
</template>
