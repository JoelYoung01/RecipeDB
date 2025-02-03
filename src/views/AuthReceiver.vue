<script setup lang="ts">
import { onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const longWait = ref(false);
const somethingWrong = ref(false);
const message = computed<string>(() => {
  let msg = `Signing you in with ${route.meta.authType}...`;
  if (longWait.value) {
    msg = `Still signing in with ${route.meta.authType}...`;
  }

  return msg;
});

onMounted(() => {
  setTimeout(() => {
    longWait.value = true;
  }, 5000);

  setTimeout(() => {
    somethingWrong.value = true;
  }, 15000);
});
</script>

<template>
  <v-container class="text-center">
    <template v-if="somethingWrong">
      <h2 class="mb-2">It seems something has gone wrong while trying to sign in.</h2>
      <v-btn color="primary" to="/login">Try Again</v-btn>
    </template>
    <template v-else>
      <h2 class="mb-2">{{ message }}</h2>
      <v-progress-circular color="primary" indeterminate />
    </template>
  </v-container>
</template>
