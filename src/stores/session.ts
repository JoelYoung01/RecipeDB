import { resetClientData } from "@/stores/sync";
import type { UserResponse } from "@/types/User";
import { AuthLoginEvent, checkSessionToken } from "@/utils";
import { defineStore } from "pinia";
import { ref } from "vue";

export const TOKEN_STORAGE_KEY = "access_token";

export const useSessionStore = defineStore("session", () => {
  const access_token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY));
  const currentUser = ref<UserResponse | null>(null);
  /** True until the first session check finishes (avoids auth redirect races). */
  const loading = ref(true);
  let checking = false;

  async function checkSession() {
    if (checking) return;
    checking = true;
    loading.value = true;
    access_token.value = localStorage.getItem(TOKEN_STORAGE_KEY);

    if (access_token.value === null) {
      logout();
      loading.value = false;
      checking = false;
      return;
    }

    const session = await checkSessionToken(access_token.value);

    if (session) {
      currentUser.value = session.user;
      access_token.value = session.access_token;
    } else {
      logout();
    }

    loading.value = false;
    checking = false;
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    access_token.value = null;
    currentUser.value = null;
    resetClientData();
  }

  window.addEventListener(AuthLoginEvent, ((event: CustomEvent) => {
    localStorage.setItem(TOKEN_STORAGE_KEY, event.detail.access_token);
    access_token.value = event.detail.access_token;
    currentUser.value = event.detail.user;
    loading.value = false;
  }) as EventListener);

  checkSession();
  return { currentUser, loading, checkSession, logout };
});
