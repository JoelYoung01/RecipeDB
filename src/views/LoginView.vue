<script setup lang="ts">
import chefHat from "@/assets/chef-hat.png";
import GoogleLoginButton from "@/components/GoogleLoginButton.vue";
import { Button } from "@/components/ui/button";
import { useSessionStore } from "@/stores/session";
import { paths } from "@/sitemap";
import { loginAsDevUser } from "@/utils";
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const session = useSessionStore();
const route = useRoute();
const router = useRouter();
const appTitle = import.meta.env.VITE_APP_TITLE;
const isDev = import.meta.env.DEV;
const devLoggingIn = ref(false);

watch(
  () => session.currentUser,
  (user) => {
    if (!user) return;
    const redirect =
      typeof route.query.redirectUrl === "string" ? route.query.redirectUrl : paths.home;
    router.replace(redirect);
  },
  { immediate: true }
);

async function continueAsDevUser() {
  if (devLoggingIn.value) return;
  devLoggingIn.value = true;
  await loginAsDevUser();
  devLoggingIn.value = false;
}
</script>

<template>
  <div
    class="app-scroll flex h-full min-h-0 flex-col items-center justify-center gap-8 overflow-y-auto overscroll-y-contain bg-gradient-to-b from-[#111113] via-background to-background px-6"
  >
    <div class="flex flex-col items-center gap-3 text-center">
      <img :src="chefHat" alt="" class="size-20 object-contain" />
      <h1 class="text-3xl font-bold tracking-tight text-foreground">
        {{ appTitle }}
      </h1>
      <p class="max-w-xs text-sm text-muted-foreground">
        Save recipes, plan the week, and see what’s for dinner tonight.
      </p>
    </div>

    <div class="flex w-full flex-col items-center gap-3">
      <template v-if="isDev">
        <Button
          class="h-11 w-[280px] rounded-lg"
          :disabled="devLoggingIn"
          @click="continueAsDevUser"
        >
          {{ devLoggingIn ? "Signing in…" : "Continue as test user" }}
        </Button>
        <p class="text-xs text-faint">Local dev bypass · seeded admin user</p>
        <div class="my-1 h-px w-[280px] bg-border" />
        <p class="text-xs text-muted-foreground">Or use Google</p>
      </template>
      <GoogleLoginButton />
      <p v-if="!isDev" class="text-xs text-faint">Sign in with Google to continue</p>
    </div>
  </div>
</template>
