<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import type { RecipeDetail } from "@/types";
import { get } from "@/utils";
import { onMounted } from "vue";

const recipes = ref<RecipeDetail[]>([]);
const loading = ref(false);

async function getRecipes() {
  loading.value = true;
  try {
    recipes.value = await get(`/recipe/user/`);
    recipes.value.sort(
      (a, b) => new Date(a.created_on).getTime() - new Date(b.created_on).getTime()
    );
  } catch (er) {
    console.error(er);
  }
}

onMounted(() => getRecipes());
</script>

<template>
  <v-container>
    <h1>My Recipes</h1>
    <RecipeCard
      v-for="recipe in recipes"
      :key="recipe.id"
      :recipe="recipe"
      size="sm"
      class="mb-3"
    />

    <div v-if="recipes.length == 0" class="my-3">
      You don't have any recipes added yet!
      <v-btn color="primary" to="/add-recipe" class="mt-2" prepend-icon="mdi-plus">
        Add Recipe
      </v-btn>
    </div>
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
