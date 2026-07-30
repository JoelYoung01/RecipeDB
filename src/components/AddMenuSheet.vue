<script setup lang="ts">
import { addMenuActions } from "@/sitemap";
import { CalendarDays, Camera, Link2, PenLine, ShoppingCart, Sparkles } from "@lucide/vue";
import { ref, watch } from "vue";
import { useRouter } from "vue-router";

const open = defineModel<boolean>("open", { default: false });
const router = useRouter();

const icons = {
  "import-link": Link2,
  "import-photo": Camera,
  "recipe-generate": Sparkles,
  "recipe-scratch": PenLine,
  "plan-meal": CalendarDays,
  "shop-item": ShoppingCart
} as const;

const createActions = addMenuActions.filter((a) => a.group === "create");
const quickActions = addMenuActions.filter((a) => a.group === "quick");

const dragY = ref(0);
const dragging = ref(false);

const CLOSE_DISTANCE = 100;
const CLOSE_VELOCITY = 0.55;
const TAP_SLOP = 6;

let pointerId: number | null = null;
let startY = 0;
let lastY = 0;
let lastT = 0;
let velocity = 0;
let moved = false;

function resetDrag() {
  dragY.value = 0;
  dragging.value = false;
  pointerId = null;
  moved = false;
  velocity = 0;
}

watch(open, (isOpen) => {
  if (isOpen) resetDrag();
});

function onHandlePointerDown(e: PointerEvent) {
  if (e.pointerType === "mouse" && e.button !== 0) return;
  pointerId = e.pointerId;
  (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  dragging.value = true;
  moved = false;
  startY = e.clientY;
  lastY = e.clientY;
  lastT = performance.now();
  velocity = 0;
}

function onHandlePointerMove(e: PointerEvent) {
  if (!dragging.value || e.pointerId !== pointerId) return;
  const dy = e.clientY - startY;
  dragY.value = Math.max(0, dy);
  if (Math.abs(dy) > TAP_SLOP) moved = true;

  const now = performance.now();
  const dt = now - lastT;
  if (dt > 0) velocity = (e.clientY - lastY) / dt;
  lastY = e.clientY;
  lastT = now;
}

function endDrag(e: PointerEvent) {
  if (!dragging.value || e.pointerId !== pointerId) return;
  dragging.value = false;
  pointerId = null;

  // Tap the handle bar to close
  if (!moved) {
    open.value = false;
    return;
  }

  if (dragY.value >= CLOSE_DISTANCE || velocity >= CLOSE_VELOCITY) {
    open.value = false;
    return;
  }

  dragY.value = 0;
}

function onHandlePointerCancel(e: PointerEvent) {
  if (e.pointerId !== pointerId) return;
  dragging.value = false;
  pointerId = null;
  dragY.value = 0;
}

function go(href: string) {
  open.value = false;
  router.push(href);
}

function onAfterLeave() {
  resetDrag();
}
</script>

<template>
  <Teleport to="body">
    <Transition name="scrim">
      <div
        v-if="open"
        class="fixed inset-0 z-50 bg-background/70"
        aria-hidden="true"
        @click="open = false"
      />
    </Transition>
    <Transition name="sheet" @after-leave="onAfterLeave">
      <div
        v-if="open"
        role="dialog"
        aria-modal="true"
        aria-label="Add new"
        class="sheet-panel fixed inset-x-0 bottom-0 z-50 mx-auto w-full max-w-md rounded-t-[20px] border border-b-0 border-border bg-card px-4 pb-[calc(5.5rem+env(safe-area-inset-bottom))]"
        :class="{ 'is-dragging': dragging }"
        :style="{ '--drag-y': `${dragY}px` }"
      >
        <div
          class="flex cursor-grab touch-none items-center justify-center pt-3 pb-2 active:cursor-grabbing"
          aria-label="Drag or tap to close"
          @pointerdown="onHandlePointerDown"
          @pointermove="onHandlePointerMove"
          @pointerup="endDrag"
          @pointercancel="onHandlePointerCancel"
        >
          <div class="h-1 w-9 rounded-full bg-[#3f463f]" />
        </div>
        <p class="px-1 pb-2.5 text-xs font-semibold tracking-[0.06em] text-faint uppercase">
          Add new
        </p>
        <div class="flex flex-col gap-1.5">
          <button
            v-for="action in createActions"
            :key="action.id"
            type="button"
            class="flex items-center gap-3.5 rounded-xl px-3 py-3 text-left transition-colors active:opacity-80"
            :class="action.highlighted ? 'bg-secondary' : 'hover:bg-secondary/60'"
            @click="go(action.href)"
          >
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-[10px] bg-[rgba(34,197,94,0.15)]"
            >
              <component
                :is="icons[action.id]"
                class="size-[17px] text-[#22c55e]/55"
                :stroke-width="2"
              />
            </span>
            <span class="min-w-0 flex-1">
              <span class="block text-[14.5px] font-semibold">{{ action.title }}</span>
              <span class="block text-[11.5px] text-muted-foreground">{{
                action.description
              }}</span>
            </span>
          </button>

          <div class="my-1.5 mx-1 h-px bg-border" />

          <button
            v-for="action in quickActions"
            :key="action.id"
            type="button"
            class="flex items-center gap-3.5 rounded-xl px-3 py-3 text-left transition-colors hover:bg-secondary/60 active:opacity-80"
            @click="go(action.href)"
          >
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-[10px] border border-border bg-secondary"
            >
              <component :is="icons[action.id]" class="size-[17px] text-faint" :stroke-width="2" />
            </span>
            <span class="min-w-0 flex-1">
              <span class="block text-[14.5px] font-semibold">{{ action.title }}</span>
              <span class="block text-[11.5px] text-muted-foreground">{{
                action.description
              }}</span>
            </span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.sheet-panel {
  --drag-y: 0px;
  transform: translate3d(0, var(--drag-y), 0);
  transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1);
  will-change: transform;
}

.sheet-panel.is-dragging {
  transition: none;
}

.sheet-enter-active {
  transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1);
}

.sheet-leave-active {
  transition: transform 0.28s cubic-bezier(0.32, 0.72, 0, 1);
}

.sheet-enter-from,
.sheet-leave-to {
  transform: translate3d(0, 100%, 0);
}

.scrim-enter-active,
.scrim-leave-active {
  transition: opacity 0.22s ease;
}

.scrim-enter-from,
.scrim-leave-to {
  opacity: 0;
}
</style>
