import { useToastStore, type ToastInput, type ToastVariant } from "@/stores/toast";
import { getErrorMessage } from "./errors";

/** Imperative toast helpers (safe outside setup via Pinia). */
export const toast = {
  push(input: ToastInput | string) {
    return useToastStore().push(input);
  },
  dismiss(id: number) {
    useToastStore().dismiss(id);
  },
  clear() {
    useToastStore().clear();
  },
  error(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return useToastStore().error(message, opts);
  },
  success(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return useToastStore().success(message, opts);
  },
  info(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return useToastStore().info(message, opts);
  },
  warning(message: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return useToastStore().warning(message, opts);
  },
  /** Show an error toast from any caught value. */
  fromError(error: unknown, fallback?: string, opts?: Omit<ToastInput, "message" | "variant">) {
    return useToastStore().error(getErrorMessage(error, fallback), opts);
  }
};

export type { ToastInput, ToastVariant };
