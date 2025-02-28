<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import type { PlannedRecipeDetail, RecipeDashboard } from "@/types";
import { get, post } from "@/utils";
import { onMounted } from "vue";

const loading = ref(true);
const todayRecipes = ref<PlannedRecipeDetail[]>([]);
const recentRecipes = ref<RecipeDashboard[]>([]);

async function getTodaysRecipes() {
  try {
    const payload = {
      start: new Date(new Date().setHours(0, 0, 0, 0)),
      end: new Date(new Date().setHours(23, 59, 59, 999))
    };
    todayRecipes.value = await post(`/planned-recipe/time-frame/`, payload);
  } catch (er) {
    console.error(er);
  }
}

async function getRecentRecipes() {
  try {
    recentRecipes.value = await get(`/recipe/user/recent/`);
  } catch (er) {
    console.error(er);
  }
}

onMounted(async () => {
  await Promise.all([getTodaysRecipes(), getRecentRecipes()]);

  loading.value = false;
});
</script>

<template>
  <v-container>
    <section>
      <h2>Today's Menu</h2>
      <RecipeCard
        v-for="planned in todayRecipes"
        :key="planned.id"
        :recipe="planned.recipe"
        class="mb-3"
      />

      <div v-if="loading" class="d-flex justify-center">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <div v-else-if="todayRecipes.length == 0" class="my-3">
        You don't have any recipes planned for today!
        <v-btn color="primary" to="/meal-planning" class="mt-2" prepend-icon="mdi-calendar">
          Plan Meals
        </v-btn>
      </div>
    </section>
    <section>
      <h2>Recently Added</h2>
      <RecipeCard v-for="recipe in recentRecipes" :key="recipe.id" :recipe="recipe" class="mb-3" />

      <div v-if="loading" class="d-flex justify-center">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <div v-else-if="recentRecipes.length == 0" class="my-3">
        You don't have any recipes added yet!
        <v-btn color="primary" to="/add-recipe" class="mt-2" prepend-icon="mdi-plus">
          Add Recipe
        </v-btn>
      </div>
    </section>
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
