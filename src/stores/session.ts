import { inject, ref } from "vue";
import { defineStore } from "pinia";
import { AuthLoginEvent, checkSessionToken } from "@/utils";
import { googleAccountsLoadedKey } from "@/plugins/googleAuth";
import type { UserResponse } from "@/types/User";

export const TOKEN_STORAGE_KEY = "access_token";

export const useSessionStore = defineStore("session", () => {
  const googleLibraryLoaded = inject(googleAccountsLoadedKey, ref(false));
  const access_token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY));
  const currentUser = ref<UserResponse | null>(null);
  const loading = ref(false);

  async function checkSession() {
    if (loading.value) return;
    loading.value = true;
    access_token.value = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (access_token.value === null) {
      logout();
      loading.value = false;
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
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    access_token.value = null;
    currentUser.value = null;
  }

  // Add event listener for login events
  window.addEventListener(AuthLoginEvent, ((event: CustomEvent) => {
    localStorage.setItem(TOKEN_STORAGE_KEY, event.detail.access_token);
    access_token.value = event.detail.access_token;
    currentUser.value = event.detail.user;
  }) as EventListener);

  watch(
    googleLibraryLoaded,
    (val) => {
      if (val && !access_token.value) {
        google.accounts.id.prompt();
      }
    },
    { immediate: true }
  );

  checkSession();
  return { currentUser, loading, checkSession, logout };
});
