<script setup lang="ts">
import GoogleLoginButton from "@/components/GoogleLoginButton.vue";
import chefHat from "@/assets/chef-hat.png";
import { useSessionStore } from "@/stores/session";
import { paths } from "@/sitemap";
import { watch } from "vue";
import { useRoute, useRouter } from "vue-router";

const session = useSessionStore();
const route = useRoute();
const router = useRouter();
const appTitle = import.meta.env.VITE_APP_TITLE;

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
</script>

<template>
  <div
    class="flex min-h-dvh flex-col items-center justify-center gap-8 bg-gradient-to-b from-[#111113] via-background to-background px-6"
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
      <GoogleLoginButton />
      <p class="text-xs text-faint">Sign in with Google to continue</p>
    </div>
  </div>
</template>
