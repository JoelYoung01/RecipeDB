<script setup lang="ts">
import type { MealPlanWizardProgressEvent } from "@/types";
import { computed, nextTick, watch } from "vue";

const props = defineProps<{
  events: MealPlanWizardProgressEvent[];
  running: boolean;
  title: string;
  subtitle?: string;
}>();

const logEl = ref<HTMLElement | null>(null);

const progress = computed(() => {
  const last = [...props.events].reverse().find((e) => typeof e.progress === "number");
  return Math.max(0, Math.min(1, last?.progress ?? (props.running ? 0.05 : 0)));
});

const pulseLabel = computed(() => {
  const last = props.events[props.events.length - 1];
  if (!last) return props.running ? "Warming up…" : "Waiting";
  return last.message;
});

watch(
  () => props.events.length,
  async () => {
    await nextTick();
    logEl.value?.scrollTo({ top: logEl.value.scrollHeight, behavior: "smooth" });
  }
);
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-border bg-card">
    <div class="relative overflow-hidden px-4 pb-4 pt-5">
      <div
        class="pointer-events-none absolute -right-8 -top-10 size-36 rounded-full bg-[rgba(34,197,94,0.12)] blur-2xl"
        :class="running ? 'animate-pulse' : ''"
      />
      <div
        class="pointer-events-none absolute -left-10 bottom-0 size-28 rounded-full bg-[rgba(34,197,94,0.08)] blur-2xl"
      />

      <p class="text-[11px] font-bold uppercase tracking-[0.08em] text-success-soft">
        {{ running ? "Live" : "Pipeline" }}
      </p>
      <h3 class="mt-1 text-lg font-bold">{{ title }}</h3>
      <p v-if="subtitle" class="mt-1 text-sm text-muted-foreground">{{ subtitle }}</p>

      <div class="relative mt-4 h-1.5 overflow-hidden rounded-full bg-secondary">
        <div
          class="h-full rounded-full bg-[#16a34a] transition-[width] duration-500 ease-out"
          :style="{ width: `${progress * 100}%` }"
        />
        <div
          v-if="running"
          class="absolute inset-y-0 w-1/3 animate-[wizard-shimmer_1.4s_ease-in-out_infinite] bg-gradient-to-r from-transparent via-[rgba(134,239,172,0.55)] to-transparent"
        />
      </div>

      <div class="mt-3 flex items-center gap-2">
        <span
          class="relative flex size-2.5"
          :class="running ? '' : 'opacity-40'"
        >
          <span
            v-if="running"
            class="absolute inline-flex size-full animate-ping rounded-full bg-[#22c55e] opacity-60"
          />
          <span class="relative inline-flex size-2.5 rounded-full bg-[#22c55e]" />
        </span>
        <p class="min-w-0 flex-1 truncate text-sm font-medium text-foreground/90">
          {{ pulseLabel }}
        </p>
        <span class="text-xs tabular-nums text-faint">{{ Math.round(progress * 100) }}%</span>
      </div>
    </div>

    <div
      ref="logEl"
      class="max-h-48 space-y-2 overflow-y-auto border-t border-border bg-elevated/80 px-4 py-3"
    >
      <div
        v-for="(event, i) in events"
        :key="`${event.stage}-${i}-${event.message}`"
        class="flex gap-2 text-[12.5px] leading-snug"
        :class="
          event.status === 'error'
            ? 'text-destructive'
            : event.status === 'complete'
              ? 'text-[#86efac]'
              : 'text-muted-foreground'
        "
      >
        <span class="mt-1.5 size-1 shrink-0 rounded-full bg-current opacity-70" />
        <span class="wizard-log-line">{{ event.message }}</span>
      </div>
      <p v-if="!events.length" class="text-sm text-faint">Waiting for the first signal…</p>
    </div>
  </div>
</template>

<style scoped>
@keyframes wizard-shimmer {
  0% {
    transform: translateX(-120%);
  }
  100% {
    transform: translateX(320%);
  }
}

.wizard-log-line {
  animation: wizard-fade-in 280ms ease-out;
}

@keyframes wizard-fade-in {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
