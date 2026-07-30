import { checkSessionToken } from "@/api/auth";
import { secureStorage as storage } from "@/lib/secure-storage";
import type { UserResponse } from "@/types";
import { create } from "zustand";

const TOKEN_KEY = "julep.access_token";
const USER_KEY = "julep.session_user";

export type SessionStatus = "loading" | "authed" | "anon";

interface SessionState {
  status: SessionStatus;
  token: string | null;
  user: UserResponse | null;
  /** Restore + verify the persisted session. Runs once at app start. */
  bootstrap: () => Promise<void>;
  /** Persist a fresh token + user after a successful auth exchange. */
  setSession: (token: string, user: UserResponse) => Promise<void>;
  /** Update the cached user (e.g. display-name edit). */
  setUser: (user: UserResponse) => void;
  /** Sign out — clears persisted credentials. */
  clear: () => Promise<void>;
}

let bootstrapStarted = false;

export const useSessionStore = create<SessionState>((set) => ({
  status: "loading",
  token: null,
  user: null,

  async bootstrap() {
    if (bootstrapStarted) return;
    bootstrapStarted = true;

    const storedToken = await storage.get(TOKEN_KEY);
    if (!storedToken) {
      set({ status: "anon", token: null, user: null });
      return;
    }

    try {
      const session = await checkSessionToken(storedToken);
      if (session) {
        await storage.set(TOKEN_KEY, session.access_token);
        await storage.set(USER_KEY, JSON.stringify(session.user));
        set({ status: "authed", token: session.access_token, user: session.user });
      } else {
        await storage.remove(TOKEN_KEY);
        await storage.remove(USER_KEY);
        set({ status: "anon", token: null, user: null });
      }
    } catch {
      // Transient failure (offline / server hiccup): keep the stored session
      // instead of logging the user out; API calls surface errors normally.
      let cachedUser: UserResponse | null = null;
      try {
        const raw = await storage.get(USER_KEY);
        cachedUser = raw ? (JSON.parse(raw) as UserResponse) : null;
      } catch {
        cachedUser = null;
      }
      set({ status: "authed", token: storedToken, user: cachedUser });
    }
  },

  async setSession(token, user) {
    await storage.set(TOKEN_KEY, token);
    await storage.set(USER_KEY, JSON.stringify(user));
    set({ status: "authed", token, user });
  },

  setUser(user) {
    set({ user });
    void storage.set(USER_KEY, JSON.stringify(user));
  },

  async clear() {
    await storage.remove(TOKEN_KEY);
    await storage.remove(USER_KEY);
    set({ status: "anon", token: null, user: null });
  }
}));
