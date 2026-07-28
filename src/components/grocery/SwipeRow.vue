<script setup lang="ts">
import { cn } from "@/lib/utils";
import { Eye, Trash2 } from "@lucide/vue";
import { computed, ref } from "vue";

const props = withDefaults(
  defineProps<{
    disabled?: boolean;
    class?: string;
  }>(),
  { disabled: false, class: undefined }
);

const emit = defineEmits<{
  dismiss: [];
  delete: [];
  view: [];
}>();

const ACTION_WIDTH = 128;
const DISMISS_THRESHOLD = 96;
const OPEN_THRESHOLD = 48;

const offset = ref(0);
const dragging = ref(false);
const openLeft = ref(false);

let startX = 0;
let startY = 0;
let startOffset = 0;
let axis: "x" | "y" | null = null;

const style = computed(() => ({
  transform: `translate3d(${offset.value}px, 0, 0)`,
  transition: dragging.value ? "none" : "transform 180ms ease-out"
}));

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function onPointerDown(event: PointerEvent) {
  if (props.disabled) return;
  dragging.value = true;
  axis = null;
  startX = event.clientX;
  startY = event.clientY;
  startOffset = offset.value;
  (event.currentTarget as HTMLElement).setPointerCapture?.(event.pointerId);
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value || props.disabled) return;
  const dx = event.clientX - startX;
  const dy = event.clientY - startY;

  if (axis === null) {
    if (Math.abs(dx) < 6 && Math.abs(dy) < 6) return;
    axis = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
    if (axis === "y") {
      dragging.value = false;
      return;
    }
  }

  event.preventDefault();
  // Left swipe → negative offset (reveal actions). Right swipe → positive (dismiss).
  offset.value = clamp(startOffset + dx, -ACTION_WIDTH, 160);
}

function onPointerUp() {
  if (!dragging.value && axis !== "x") {
    dragging.value = false;
    axis = null;
    return;
  }
  dragging.value = false;

  if (offset.value >= DISMISS_THRESHOLD) {
    offset.value = 0;
    openLeft.value = false;
    emit("dismiss");
  } else if (offset.value <= -OPEN_THRESHOLD) {
    offset.value = -ACTION_WIDTH;
    openLeft.value = true;
  } else {
    offset.value = 0;
    openLeft.value = false;
  }
  axis = null;
}

function close() {
  offset.value = 0;
  openLeft.value = false;
}

function onDelete() {
  close();
  emit("delete");
}

function onView() {
  close();
  emit("view");
}

defineExpose({ close });
</script>

<template>
  <div class="relative overflow-hidden rounded-xl">
    <!-- Right-swipe dismiss hint -->
    <div
      class="absolute inset-y-0 left-0 flex w-28 items-center justify-start bg-[rgba(34,197,94,0.2)] pl-4"
      aria-hidden="true"
    >
      <span class="text-xs font-semibold text-[#4ade80]">Dismiss</span>
    </div>

    <!-- Left-swipe actions -->
    <div class="absolute inset-y-0 right-0 flex w-32 items-stretch" aria-hidden="true">
      <button
        type="button"
        class="flex flex-1 items-center justify-center bg-[#27272a] text-[#fafafa] transition-opacity active:opacity-80"
        tabindex="-1"
        @click="onView"
      >
        <Eye class="size-5" :stroke-width="2" />
      </button>
      <button
        type="button"
        class="flex flex-1 items-center justify-center bg-[#dc2626] text-white transition-opacity active:opacity-80"
        tabindex="-1"
        @click="onDelete"
      >
        <Trash2 class="size-5" :stroke-width="2" />
      </button>
    </div>

    <div
      :class="cn('relative z-10 touch-pan-y bg-card select-none', props.class)"
      :style="style"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <slot :open="openLeft" />
    </div>
  </div>
</template>
