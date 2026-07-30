import { secureStorage } from "@/lib/secure-storage";
import { create } from "zustand";

const APP_LOCK_KEY = "julep.app_lock";

interface AppLockState {
  /** True once the persisted preference has been read. */
  ready: boolean;
  /** User preference: require biometric unlock when opening the app. */
  enabled: boolean;
  /** Whether the app is currently behind the biometric gate. */
  locked: boolean;
  /** Restore the persisted preference. Cold starts begin locked when enabled. */
  bootstrap: () => Promise<void>;
  setEnabled: (on: boolean) => Promise<void>;
  /** Called when the app is backgrounded; a no-op unless the lock is enabled. */
  lock: () => void;
  unlock: () => void;
}

let bootstrapStarted = false;

/** Test hook — lets Jest re-run bootstrap in isolation. */
export function resetAppLockBootstrapForTests() {
  bootstrapStarted = false;
}

export const useAppLockStore = create<AppLockState>((set, get) => ({
  ready: false,
  enabled: false,
  locked: false,

  async bootstrap() {
    if (bootstrapStarted) return;
    bootstrapStarted = true;
    const stored = await secureStorage.get(APP_LOCK_KEY);
    const enabled = stored === "1";
    set({ ready: true, enabled, locked: enabled });
  },

  async setEnabled(on) {
    if (on) await secureStorage.set(APP_LOCK_KEY, "1");
    else await secureStorage.remove(APP_LOCK_KEY);
    // Never lock the session the user is currently using.
    set({ enabled: on, locked: false });
  },

  lock() {
    if (get().enabled) set({ locked: true });
  },

  unlock() {
    set({ locked: false });
  }
}));
