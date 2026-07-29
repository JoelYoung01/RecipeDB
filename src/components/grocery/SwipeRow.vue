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
const DISMISS_THRESHOLD = 72;
const OPEN_THRESHOLD = 40;

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

const style = computed(() => ({
  transform: `translate3d(${offset.value}px, 0, 0)`,
  transition: dragging.value ? "none" : "transform 180ms ease-out"
}));

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function isInteractive(target: EventTarget | null) {
  if (!(target instanceof Element)) return false;
  return Boolean(
    target.closest(
      'button, a, input, textarea, select, [role="checkbox"], [data-slot="checkbox"]'
    )
  );
}

function onPointerDown(event: PointerEvent) {
  if (props.disabled || event.button !== 0) return;
  if (isInteractive(event.target)) return;

  dragging.value = true;
  settling = false;
  axis = null;
  activePointerId = event.pointerId;
  startX = event.clientX;
  startY = event.clientY;
  startOffset = offset.value;
  rowEl.value?.setPointerCapture?.(event.pointerId);
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value || props.disabled || settling) return;
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
  offset.value = clamp(startOffset + dx, -ACTION_WIDTH, 180);
}

function cancelDrag() {
  dragging.value = false;
  axis = null;
  const pid = activePointerId;
  activePointerId = null;
  if (pid !== null && rowEl.value?.hasPointerCapture?.(pid)) {
    try {
      rowEl.value.releasePointerCapture(pid);
    } catch {
      /* already released */
    }
  }
  if (!openLeft.value) offset.value = 0;
}

function settleDrag() {
  if (!dragging.value || settling) return;
  settling = true;

  const finalAxis = axis;
  const finalOffset = offset.value;
  dragging.value = false;
  axis = null;

  const pid = activePointerId;
  activePointerId = null;
  if (pid !== null && rowEl.value?.hasPointerCapture?.(pid)) {
    try {
      rowEl.value.releasePointerCapture(pid);
    } catch {
      /* already released */
    }
  }

  if (finalAxis !== "x") {
    if (!openLeft.value) offset.value = 0;
    settling = false;
    return;
  }

  if (finalOffset >= DISMISS_THRESHOLD) {
    offset.value = 0;
    openLeft.value = false;
    settling = false;
    emit("dismiss");
    return;
  }

  if (finalOffset <= -OPEN_THRESHOLD) {
    offset.value = -ACTION_WIDTH;
    openLeft.value = true;
  } else {
    offset.value = 0;
    openLeft.value = false;
  }
  settling = false;
}

function onPointerUp(event: PointerEvent) {
  if (activePointerId !== null && event.pointerId !== activePointerId) return;
  settleDrag();
}

function close() {
  offset.value = 0;
  openLeft.value = false;
}

function onContentClick() {
  if (openLeft.value) close();
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
    <div
      class="absolute inset-y-0 left-0 flex w-28 items-center justify-start bg-[rgba(34,197,94,0.22)] pl-4"
      aria-hidden="true"
    >
      <span class="text-xs font-semibold text-[#4ade80]">Dismiss</span>
    </div>

    <div class="absolute inset-y-0 right-0 z-0 flex w-32 items-stretch">
      <button
        type="button"
        class="flex flex-1 items-center justify-center bg-[#3f463f] text-foreground transition-opacity active:opacity-80"
        :tabindex="openLeft ? 0 : -1"
        aria-label="View recipe"
        @click.stop="onView"
      >
        <Eye class="size-5" :stroke-width="2" />
      </button>
      <button
        type="button"
        class="flex flex-1 items-center justify-center bg-[#dc2626] text-primary-foreground transition-opacity active:opacity-80"
        :tabindex="openLeft ? 0 : -1"
        aria-label="Remove from list"
        @click.stop="onDelete"
      >
        <Trash2 class="size-5" :stroke-width="2" />
      </button>
    </div>

    <div
      ref="rowEl"
      :class="
        cn(
          'relative z-10 cursor-grab touch-pan-y bg-card select-none active:cursor-grabbing',
          props.class
        )
      "
      :style="style"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
      @click="onContentClick"
    >
      <slot :open="openLeft" />
    </div>
  </div>
</template>
