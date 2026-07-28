<script setup lang="ts">
import { addMenuActions } from "@/sitemap";
import { CalendarDays, Camera, Link2, PenLine, ShoppingCart } from "@lucide/vue";
import { useRouter } from "vue-router";

const open = defineModel<boolean>("open", { default: false });
const router = useRouter();

const icons = {
  "import-link": Link2,
  "import-photo": Camera,
  "recipe-scratch": PenLine,
  "plan-meal": CalendarDays,
  "shop-item": ShoppingCart
} as const;

const createActions = addMenuActions.filter((a) => a.group === "create");
const quickActions = addMenuActions.filter((a) => a.group === "quick");

function go(href: string) {
  open.value = false;
  router.push(href);
}
</script>

<template>
  <Teleport to="body">
    <Transition name="scrim">
      <div
        v-if="open"
        class="fixed inset-0 z-50 bg-black/55"
        aria-hidden="true"
        @click="open = false"
      />
    </Transition>
    <Transition name="sheet">
      <div
        v-if="open"
        role="dialog"
        aria-modal="true"
        aria-label="Add new"
        class="fixed bottom-0 left-1/2 z-50 w-full max-w-md -translate-x-1/2 rounded-t-[20px] border border-b-0 border-border bg-card px-4 pt-2.5 pb-[calc(5.5rem+env(safe-area-inset-bottom))] shadow-[0_-12px_40px_rgba(0,0,0,0.6)]"
      >
        <div class="mx-auto mb-3.5 h-1 w-9 rounded-full bg-[#3f3f46]" />
        <p class="px-1 pb-2.5 text-xs font-semibold tracking-[0.06em] text-faint uppercase">
          Add new
        </p>
        <div class="flex flex-col gap-1.5">
          <button
            v-for="action in createActions"
            :key="action.id"
            type="button"
            class="flex items-center gap-3.5 rounded-xl px-2.5 py-3 text-left transition-colors active:opacity-80"
            :class="action.highlighted ? 'bg-secondary' : 'hover:bg-secondary/60'"
            @click="go(action.href)"
          >
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-[10px] bg-[rgba(34,197,94,0.15)]"
            >
              <component
                :is="icons[action.id]"
                class="size-[17px] text-[#22c55e]"
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
            class="flex items-center gap-3.5 rounded-xl px-2.5 py-3 text-left transition-colors hover:bg-secondary/60 active:opacity-80"
            @click="go(action.href)"
          >
            <span
              class="flex size-9 shrink-0 items-center justify-center rounded-[10px] border border-border bg-secondary"
            >
              <component
                :is="icons[action.id]"
                class="size-[17px] text-muted-foreground"
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
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.scrim-enter-active,
.scrim-leave-active {
  transition: opacity 0.2s ease;
}
.scrim-enter-from,
.scrim-leave-to {
  opacity: 0;
}
.sheet-enter-active,
.sheet-leave-active {
  transition:
    transform 0.25s cubic-bezier(0.32, 0.72, 0, 1),
    opacity 0.2s ease;
}
.sheet-enter-from,
.sheet-leave-to {
  transform: translate(-50%, 100%);
  opacity: 0.6;
}
</style>
