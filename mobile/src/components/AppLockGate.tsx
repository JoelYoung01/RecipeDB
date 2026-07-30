import { LockScreen } from "@/components/LockScreen";
import { useAppLockStore } from "@/stores/app-lock";
import { useSessionStore } from "@/stores/session";
import { useEffect } from "react";
import { AppState, Platform } from "react-native";

/**
 * Renders the biometric LockScreen over the whole app while it is locked,
 * and re-locks whenever the app is backgrounded (native only).
 */
export function AppLockGate() {
  const sessionStatus = useSessionStore((s) => s.status);
  const enabled = useAppLockStore((s) => s.enabled);
  const locked = useAppLockStore((s) => s.locked);

  useEffect(() => {
    if (Platform.OS === "web") return;
    const sub = AppState.addEventListener("change", (state) => {
      if (state === "background") useAppLockStore.getState().lock();
    });
    return () => sub.remove();
  }, []);

  if (sessionStatus !== "authed" || !enabled || !locked) return null;
  return <LockScreen />;
}
