import { AuthErrorEvent, loginWithGoogle } from "@/utils";
import type { InjectionKey, Ref } from "vue";
import { ref } from "vue";

export const googleAccountsLoadedKey = Symbol() as InjectionKey<Ref<boolean>>;

async function handleGoogleCredential(response: { credential?: string }) {
  if (!response.credential) {
    const message = "Google sign-in did not return a credential.";
    window.dispatchEvent(new CustomEvent(AuthErrorEvent, { detail: { message } }));
    console.error(message);
    return;
  }
  try {
    await loginWithGoogle({ credential: response.credential });
  } catch (er) {
    // loginWithGoogle already dispatches AuthErrorEvent for API failures.
    console.error(er);
  }
}

/**
 * Docs for js API:
 * https://developers.google.com/identity/gsi/web/reference/js-reference
 *
 * Intentionally does not call `google.accounts.id.prompt()` — One Tap / FedCM
 * prompts should only appear when the user chooses Google sign-in on the login page.
 */
export function install(app: any) {
  const loaded = ref(false);
  app.provide(googleAccountsLoadedKey, loaded);

  // @ts-expect-error This exists, trust me bro (https://developers.google.com/identity/gsi/web/reference/js-reference#onGoogleLibraryLoad)
  window.onGoogleLibraryLoad = () => {
    google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      auto_select: false,
      callback: handleGoogleCredential,
      use_fedcm_for_prompt: true
    });

    loaded.value = true;
  };

  setTimeout(() => {
    if (!loaded.value) {
      console.error(
        "Google Library is still not loaded after 5 seconds, something is probably wrong. Did you add the cdn script?"
      );
    }
  }, 5000);
}
