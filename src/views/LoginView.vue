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
  <template v-if="sessionStore.loading">
    <h2 class="mt-5 text-center">Logging you in...</h2>
    <div class="d-flex justify-center mt-3">
      <v-progress-circular color="primary" indeterminate />
    </div>
  </template>
  <div v-else class="d-flex mt-10 justify-center">
    <GoogleLoginButton />
  </div>
</template>

<style scoped></style>
