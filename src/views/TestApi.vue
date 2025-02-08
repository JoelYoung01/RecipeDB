<script setup lang="ts">
import { get } from "@/utils";

const recipes = ref<any[]>();

async function getPublicRecipes() {
  recipes.value = await get("/recipe/public/");
}

getPublicRecipes();
</script>

<template>
  <v-btn to="/">home</v-btn>
  TESTING API
  <pre>{{ recipes }}</pre>
</template>

<style scoped></style>
