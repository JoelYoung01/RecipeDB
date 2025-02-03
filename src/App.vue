<script setup lang="ts">
import { RouterView, useRoute } from "vue-router";
import AccountButton from "./components/AccountButton.vue";

const route = useRoute();

const title = import.meta.env.VITE_APP_TITLE;

const mainClassList = computed(() => {
  let classes = "";

  if (route.meta.useShadedBackground) {
    classes += "shaded-bg";
  }

  return classes;
});
</script>

<template>
  <v-app>
    <v-app-bar dense color="primary" :elevation="2" class="pe-4">
      <v-app-bar-title>
        <RouterLink class="text-decoration-none text-white" to="/">{{ title }}</RouterLink>
      </v-app-bar-title>

      <v-btn variant="text" prepend-icon="mdi-list-box" to="/app-definition/list" class="mx-1">
        Definitions
      </v-btn>

      <v-btn variant="text" prepend-icon="mdi-home" to="/" class="mx-1"> Home </v-btn>

      <AccountButton class="ms-3" />
    </v-app-bar>

    <v-main :class="mainClassList">
      <RouterView />
    </v-main>
  </v-app>
</template>

<style scoped>
.shaded-bg {
  background-color: whitesmoke;
}
</style>
