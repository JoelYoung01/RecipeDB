import type { UserResponse } from "@/types/User";
import { AuthLoginEvent, checkSessionToken, loginAsDevUser } from "@/utils";
import { defineStore } from "pinia";
import { ref } from "vue";

export const TOKEN_STORAGE_KEY = "access_token";
const SKIP_DEV_AUTO_LOGIN_KEY = "skip_dev_auto_login";

export const useSessionStore = defineStore("session", () => {
  const access_token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY));
  const currentUser = ref<UserResponse | null>(null);
  /** True until the first session check finishes (avoids auth redirect races). */
  const loading = ref(true);
  let checking = false;

  function shouldAutoDevLogin() {
    return import.meta.env.DEV && sessionStorage.getItem(SKIP_DEV_AUTO_LOGIN_KEY) !== "1";
  }

  async function tryDevLogin() {
    const session = await loginAsDevUser();
    if (session) {
      sessionStorage.removeItem(SKIP_DEV_AUTO_LOGIN_KEY);
      return true;
    }
    return false;
  }

  async function checkSession() {
    if (checking) return;
    checking = true;
    loading.value = true;
    access_token.value = localStorage.getItem(TOKEN_STORAGE_KEY);

    if (access_token.value === null) {
      if (shouldAutoDevLogin() && (await tryDevLogin())) {
        loading.value = false;
        checking = false;
        return;
      }
      logout({ skipDevAutoLogin: false });
      loading.value = false;
      checking = false;
      return;
    }

    const session = await checkSessionToken(access_token.value);

    if (session) {
      currentUser.value = session.user;
      access_token.value = session.access_token;
    } else if (shouldAutoDevLogin()) {
      logout({ skipDevAutoLogin: false });
      if (!(await tryDevLogin())) {
        logout({ skipDevAutoLogin: false });
      }
    } else {
      logout({ skipDevAutoLogin: false });
    }

    loading.value = false;
    checking = false;
  }

  function logout(options?: { skipDevAutoLogin?: boolean }) {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    access_token.value = null;
    currentUser.value = null;
    // After an explicit sign-out in Vite dev, don't immediately re-auth until
    // a new tab clears sessionStorage (or the user signs in again).
    if (import.meta.env.DEV && options?.skipDevAutoLogin !== false) {
      sessionStorage.setItem(SKIP_DEV_AUTO_LOGIN_KEY, "1");
    }
  }

  window.addEventListener(AuthLoginEvent, ((event: CustomEvent) => {
    localStorage.setItem(TOKEN_STORAGE_KEY, event.detail.access_token);
    access_token.value = event.detail.access_token;
    currentUser.value = event.detail.user;
    loading.value = false;
    sessionStorage.removeItem(SKIP_DEV_AUTO_LOGIN_KEY);
  }) as EventListener);

  checkSession();
  return { currentUser, loading, checkSession, logout };
});
