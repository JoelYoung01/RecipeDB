import { getErrorMessage } from "@/api/errors";
import { create } from "zustand";

export type ToastVariant = "success" | "error" | "info" | "warning";

export interface ToastInput {
  message: string;
  variant?: ToastVariant;
  duration?: number;
}

export interface Toast {
  id: number;
  message: string;
  variant: ToastVariant;
  duration: number;
}

interface ToastState {
  toasts: Toast[];
  push: (input: ToastInput | string) => number;
  dismiss: (id: number) => void;
  clear: () => void;
}

const DEFAULT_DURATION = 3500;
const MAX_TOASTS = 3;
let nextId = 1;

export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],

  push(input) {
    const parsed: ToastInput = typeof input === "string" ? { message: input } : input;
    const toast: Toast = {
      id: nextId++,
      message: parsed.message,
      variant: parsed.variant ?? "info",
      duration: parsed.duration ?? DEFAULT_DURATION
    };
    set((state) => ({ toasts: [...state.toasts.slice(-(MAX_TOASTS - 1)), toast] }));
    setTimeout(() => get().dismiss(toast.id), toast.duration);
    return toast.id;
  },

  dismiss(id) {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },

  clear() {
    set({ toasts: [] });
  }
}));

/** Imperative helpers, usable outside components. */
export const toast = {
  success(message: string) {
    return useToastStore.getState().push({ message, variant: "success" });
  },
  error(message: string) {
    return useToastStore.getState().push({ message, variant: "error" });
  },
  info(message: string) {
    return useToastStore.getState().push({ message, variant: "info" });
  },
  warning(message: string) {
    return useToastStore.getState().push({ message, variant: "warning" });
  },
  /** Show an error toast from any caught value. */
  fromError(error: unknown, fallback?: string) {
    return useToastStore.getState().push({
      message: getErrorMessage(error, fallback),
      variant: "error"
    });
  }
};
