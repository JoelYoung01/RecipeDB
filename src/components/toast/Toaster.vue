<script setup lang="ts">
import { useToastStore, type ToastVariant } from "@/stores/toast";
import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle2, Info, X, AlertTriangle } from "@lucide/vue";
import { computed } from "vue";

const store = useToastStore();
const toasts = computed(() => store.stack);

const variantStyles: Record<ToastVariant, string> = {
  error: "border-destructive/50 bg-card text-foreground",
  success: "border-primary/40 bg-card text-foreground",
  info: "border-border bg-card text-foreground",
  warning: "border-amber-500/45 bg-card text-foreground"
};

const iconClass: Record<ToastVariant, string> = {
  error: "text-destructive",
  success: "text-[#22c55e]",
  info: "text-muted-foreground",
  warning: "text-amber-400"
};
</script>

<template>
  <div
    class="pointer-events-none absolute inset-x-0 top-0 z-[80] flex flex-col gap-2 px-3 pt-[max(0.75rem,env(safe-area-inset-top))]"
    aria-live="polite"
    aria-relevant="additions text"
  >
    <TransitionGroup name="toast-stack">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex w-full items-start gap-2.5 rounded-xl border px-3 py-2.5 shadow-none"
        :class="variantStyles[toast.variant]"
        role="status"
      >
        <AlertCircle
          v-if="toast.variant === 'error'"
          class="mt-0.5 size-4 shrink-0"
          :class="iconClass.error"
        />
        <CheckCircle2
          v-else-if="toast.variant === 'success'"
          class="mt-0.5 size-4 shrink-0"
          :class="iconClass.success"
        />
        <AlertTriangle
          v-else-if="toast.variant === 'warning'"
          class="mt-0.5 size-4 shrink-0"
          :class="iconClass.warning"
        />
        <Info v-else class="mt-0.5 size-4 shrink-0" :class="iconClass.info" />

        <div class="min-w-0 flex-1">
          <p v-if="toast.title" class="text-sm font-semibold leading-snug tracking-tight">
            {{ toast.title }}
          </p>
          <p
            :class="
              cn(
                'text-sm leading-snug text-muted-foreground',
                toast.title ? 'mt-0.5' : 'font-medium text-foreground'
              )
            "
          >
            {{ toast.message }}
          </p>
        </div>

        <button
          type="button"
          class="rounded-md p-1 text-faint transition-opacity hover:text-foreground active:opacity-70"
          aria-label="Dismiss notification"
          @click="store.dismiss(toast.id)"
        >
          <X class="size-3.5" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-stack-enter-active,
.toast-stack-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}
.toast-stack-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}
.toast-stack-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
.toast-stack-move {
  transition: transform 180ms ease;
}
</style>
