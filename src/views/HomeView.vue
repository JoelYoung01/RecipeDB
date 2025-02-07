<script setup lang="ts">
import { get } from "@/utils";
// import { useSessionStore } from "@/stores/session";

// const sessionStore = useSessionStore();

const recipes = ref<any[]>();

async function getPublicRecipes() {
  recipes.value = await get("/recipe/public/");
}

getPublicRecipes();
</script>

<template>
  <v-container> CONTENT </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
