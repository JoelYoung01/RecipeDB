import { defineStore } from "pinia";
import { computed, ref } from "vue";

export type ToastVariant = "error" | "success" | "info" | "warning";

export type ToastInput = {
  message: string;
  title?: string;
  variant?: ToastVariant;
  /** Auto-dismiss in ms. Use 0 to keep until dismissed. Default varies by variant. */
  duration?: number;
};

export type ToastItem = {
  id: number;
  message: string;
  title?: string;
  variant: ToastVariant;
  duration: number;
};

const DEFAULT_DURATIONS: Record<ToastVariant, number> = {
  error: 6500,
  warning: 5500,
  info: 4000,
  success: 3500
};

let nextId = 1;

export const useToastStore = defineStore("toast", () => {
  const toasts = ref<ToastItem[]>([]);
  const timers = new Map<number, ReturnType<typeof setTimeout>>();

  const stack = computed(() => toasts.value);

  function dismiss(id: number) {
    const timer = timers.get(id);
    if (timer) {
      clearTimeout(timer);
      timers.delete(id);
    }
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  function clear() {
    for (const id of timers.keys()) {
      const timer = timers.get(id);
      if (timer) clearTimeout(timer);
    }
    timers.clear();
    toasts.value = [];
  }

  function push(input: ToastInput | string) {
    const normalized: ToastInput = typeof input === "string" ? { message: input } : input;
    const message = normalized.message?.trim();
    if (!message) return null;

    const variant = normalized.variant ?? "info";
    const duration =
      normalized.duration !== undefined ? normalized.duration : DEFAULT_DURATIONS[variant];

    const item: ToastItem = {
      id: nextId++,
      message,
      title: normalized.title,
      variant,
      duration
    };

    toasts.value = [...toasts.value, item];

    if (duration > 0) {
      timers.set(
        item.id,
        setTimeout(() => dismiss(item.id), duration)
      );
    }

    return item.id;
  }

  function error(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return push({ ...opts, message, variant: "error" });
  }

  function success(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return push({ ...opts, message, variant: "success" });
  }

  function info(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return push({ ...opts, message, variant: "info" });
  }

  function warning(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return push({ ...opts, message, variant: "warning" });
  }

  return {
    toasts,
    stack,
    push,
    dismiss,
    clear,
    error,
    success,
    info,
    warning
  };
});
