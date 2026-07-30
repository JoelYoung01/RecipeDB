<script setup lang="ts">
import { cn } from "@/lib/utils";
import { computed, ref } from "vue";

/**
 * Swipeable list row. Drag right past the commit threshold to fire
 * `swipe-right` (quick action), drag left to reveal the `actions` tray.
 * Content may itself be interactive (whole-row buttons, checkboxes): pointer
 * capture is deferred until the drag axis locks horizontal, so plain taps keep
 * their native click behavior and clicks after a drag are suppressed.
 */
const props = withDefaults(
  defineProps<{
    disabled?: boolean;
    class?: string;
    /** Width (px) of the action tray revealed by swiping left. */
    actionWidth?: number;
    canSwipeLeft?: boolean;
    canSwipeRight?: boolean;
  }>(),
  {
    disabled: false,
    class: undefined,
    actionWidth: 128,
    canSwipeLeft: true,
    canSwipeRight: true
  }
);

const emit = defineEmits<{
  /** Row swiped right past the commit threshold (released). */
  swipeRight: [];
}>();

const COMMIT_THRESHOLD = 72;
const OPEN_THRESHOLD = 40;
const MAX_RIGHT = 180;

const offset = ref(0);
const dragging = ref(false);
const openLeft = ref(false);
const rowEl = ref<HTMLElement | null>(null);

let startX = 0;
let startY = 0;
let startOffset = 0;
let axis: "x" | "y" | null = null;
let activePointerId: number | null = null;
let settling = false;
let suppressClick = false;

const style = computed(() => ({
  transform: `translate3d(${offset.value}px, 0, 0)`,
  transition: dragging.value ? "none" : "transform 180ms ease-out"
}));

const minOffset = computed(() => (props.canSwipeLeft ? -props.actionWidth : 0));
const maxOffset = computed(() => (props.canSwipeRight ? MAX_RIGHT : 0));

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function onPointerDown(event: PointerEvent) {
  if (props.disabled || event.button !== 0) return;

  suppressClick = false;
  dragging.value = true;
  settling = false;
  axis = null;
  activePointerId = event.pointerId;
  startX = event.clientX;
  startY = event.clientY;
  startOffset = offset.value;
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value || props.disabled || settling) return;
  if (activePointerId === null || event.pointerId !== activePointerId) return;
  // Stale mouse drag: released outside the row before capture engaged.
  if (event.buttons === 0) {
    cancelDrag();
    return;
  }

  const dx = event.clientX - startX;
  const dy = event.clientY - startY;

  if (axis === null) {
    if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return;
    axis = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
    if (axis === "y") {
      cancelDrag();
      return;
    }
    rowEl.value?.setPointerCapture?.(event.pointerId);
  }

  event.preventDefault();
  offset.value = clamp(startOffset + dx, minOffset.value, maxOffset.value);
}

function releaseCapture() {
  const pid = activePointerId;
  activePointerId = null;
  if (pid !== null && rowEl.value?.hasPointerCapture?.(pid)) {
    try {
      rowEl.value.releasePointerCapture(pid);
    } catch {
      /* already released */
    }
  }
}

function cancelDrag() {
  dragging.value = false;
  axis = null;
  releaseCapture();
  offset.value = openLeft.value ? -props.actionWidth : 0;
}

function settleDrag() {
  if (!dragging.value || settling) return;
  settling = true;

  const finalAxis = axis;
  const finalOffset = offset.value;
  dragging.value = false;
  axis = null;
  releaseCapture();

  if (finalAxis !== "x") {
    offset.value = openLeft.value ? -props.actionWidth : 0;
    settling = false;
    return;
  }

  suppressClick = true;

  if (props.canSwipeRight && finalOffset >= COMMIT_THRESHOLD) {
    offset.value = 0;
    openLeft.value = false;
    settling = false;
    emit("swipeRight");
    return;
  }

  if (props.canSwipeLeft && finalOffset <= -OPEN_THRESHOLD) {
    offset.value = -props.actionWidth;
    openLeft.value = true;
  } else {
    offset.value = 0;
    openLeft.value = false;
  }
  settling = false;
}

function onPointerUp(event: PointerEvent) {
  if (activePointerId === null || event.pointerId !== activePointerId) return;
  settleDrag();
}

function onPointerCancel(event: PointerEvent) {
  if (activePointerId === null || event.pointerId !== activePointerId) return;
  cancelDrag();
}

function close() {
  offset.value = 0;
  openLeft.value = false;
}

function onClickCapture(event: MouseEvent) {
  if (suppressClick) {
    suppressClick = false;
    event.preventDefault();
    event.stopPropagation();
    return;
  }
  if (openLeft.value) {
    event.preventDefault();
    event.stopPropagation();
    close();
  }
}

defineExpose({ close });
</script>

<template>
  <div :class="cn('relative overflow-hidden rounded-xl', props.class)">
    <div v-if="canSwipeRight" class="absolute inset-y-0 left-0 flex" aria-hidden="true">
      <slot name="hint" />
    </div>

    <div
      v-if="canSwipeLeft"
      class="absolute inset-y-0 right-0 z-0 flex items-stretch"
      :style="{ width: `${actionWidth}px` }"
    >
      <slot name="actions" :open="openLeft" :close="close" />
    </div>

    <div
      ref="rowEl"
      class="relative z-10 cursor-grab touch-pan-y bg-card select-none active:cursor-grabbing"
      :style="style"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerCancel"
      @click.capture="onClickCapture"
    >
      <slot :open="openLeft" />
    </div>
  </div>
</template>
