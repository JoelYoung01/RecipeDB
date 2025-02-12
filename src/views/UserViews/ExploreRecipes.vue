<script setup lang="ts">
import { get } from "@/utils";
// import { useSessionStore } from "@/stores/session";

// const sessionStore = useSessionStore();

const recipes = ref<any[]>();
const searchText = ref<string>();

async function getPublicRecipes() {
  recipes.value = await get("/recipe/public/");
}

getPublicRecipes();
</script>

<template>
  <v-container>
    <v-text-field
      v-model="searchText"
      variant="outlined"
      prepend-inner-icon="mdi-magnify"
      clearable
      hide-details
      placeholder="Search for a Recipe"
      type="search"
      rounded
    />
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
