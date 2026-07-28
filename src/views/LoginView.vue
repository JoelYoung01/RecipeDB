<script setup lang="ts">
import chefHat from "@/assets/chef-hat.png";
import GoogleLoginButton from "@/components/GoogleLoginButton.vue";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSessionStore } from "@/stores/session";
import { paths } from "@/sitemap";
import { AuthApiError, loginWithPassword } from "@/utils";
import { ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

const session = useSessionStore();
const route = useRoute();
const router = useRouter();
const submitting = ref(false);
const errorMessage = ref<string | null>(null);
const email = ref("");
const password = ref("");

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

async function onSubmit() {
  if (submitting.value) return;
  errorMessage.value = null;
  submitting.value = true;
  try {
    await loginWithPassword({
      email: email.value.trim(),
      password: password.value
    });
  } catch (err) {
    if (err instanceof AuthApiError && err.redirectTo) {
      if (import.meta.env.DEV && err.devOtp) {
        sessionStorage.setItem(`dev_otp:${err.email || email.value.trim()}`, err.devOtp);
      }
      await router.push(err.redirectTo);
      return;
    }
    errorMessage.value = err instanceof Error ? err.message : "Login failed";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div
    class="app-scroll flex h-full min-h-0 flex-col items-center justify-center gap-8 overflow-y-auto overscroll-y-contain bg-gradient-to-b from-[#111113] via-background to-background px-6 py-10"
  >
    <div class="flex flex-col items-center gap-3 text-center">
      <img :src="chefHat" alt="" class="size-20 object-contain" />
      <h1 class="text-3xl font-bold tracking-tight text-foreground">RecipeDB</h1>
    </div>

    <form class="flex w-full max-w-[320px] flex-col gap-3" @submit.prevent="onSubmit">
      <div class="space-y-1.5">
        <Label for="login-email">Email</Label>
        <Input
          id="login-email"
          v-model="email"
          type="email"
          autocomplete="email"
          required
          placeholder="you@example.com"
          class="h-11"
        />
      </div>
      <div class="space-y-1.5">
        <Label for="login-password">Password</Label>
        <Input
          id="login-password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
          placeholder="••••••••"
          class="h-11"
        />
      </div>
      <p v-if="errorMessage" class="text-sm text-destructive">{{ errorMessage }}</p>
      <Button class="h-11 w-full rounded-lg" type="submit" :disabled="submitting">
        {{ submitting ? "Signing in…" : "Sign in" }}
      </Button>
      <p class="text-center text-sm text-muted-foreground">
        New here?
        <RouterLink :to="paths.register" class="text-primary underline-offset-4 hover:underline">
          Create an account
        </RouterLink>
      </p>
    </form>

    <div class="flex w-full max-w-[320px] flex-col items-center gap-3">
      <div class="flex w-full items-center gap-3">
        <div class="h-px flex-1 bg-border" />
        <span class="text-xs text-faint">or</span>
        <div class="h-px flex-1 bg-border" />
      </div>

      <GoogleLoginButton />
    </div>
  </div>
</template>
