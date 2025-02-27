<script setup lang="ts">
import GoogleLoginButton from "@/components/GoogleLoginButton.vue";
import { useSessionStore } from "@/stores/session";
import { useRoute, useRouter } from "vue-router";

const sessionStore = useSessionStore();
const router = useRouter();
const route = useRoute();

// TODO: Add support for when login fails

watch(
  () => sessionStore.currentUser,
  (value) => {
    if (!value) return;

    const redirect = Array.isArray(route.query.redirectUrl)
      ? route.query.redirectUrl[0]
      : route.query.redirectUrl;
    if (redirect) {
      router.push(redirect);
    } else {
      router.push("/");
    }
  },
  {
    immediate: true
  }
);
</script>

<template>
  <v-container>
    <template v-if="sessionStore.loading">
      <h2 class="mt-5 text-center">Logging you in...</h2>
      <div class="d-flex justify-center mt-3">
        <v-progress-circular color="primary" indeterminate />
      </div>
    </template>
    <template v-else>
      <h1 class="mt-5 text-center">Welcome!</h1>
      <h3 class="text-center">Sign in to use the app</h3>
      <div class="d-flex mt-10 justify-center">
        <GoogleLoginButton />
      </div>
    </template>
  </v-container>
</template>

<style scoped></style>
