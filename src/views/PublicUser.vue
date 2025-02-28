<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import type { RecipeDetail, PublicUser } from "@/types";
import { get } from "@/utils";
import { onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const user = ref<PublicUser>();
const recipes = ref<RecipeDetail[]>([]);
const loading = ref(true);

async function getUser() {
  try {
    user.value = await get(`/user/${route.params.userId}/public/`);
  } catch (er) {
    console.error(er);
  }
}

async function getUserRecipes() {
  try {
    recipes.value = await get(`/recipe/public/?user=${route.params.userId}`);
    recipes.value.sort((a, b) => a.name.localeCompare(b.name));
  } catch (er) {
    console.error(er);
  }
}

onMounted(async () => {
  await getUser();
  await getUserRecipes();
  loading.value = false;
});
</script>

<template>
  <div v-if="loading" class="d-flex flex-column loading-container justify-center align-center">
    <v-progress-circular indeterminate size="large" color="primary" />
    <h4 class="mt-4">Loading User...</h4>
  </div>

  <v-container v-else-if="user">
    <h2>{{ user.display_name }}</h2>
    <div class="mb-2">{{ recipes.length }} recipe{{ recipes.length === 1 ? "" : "s" }}</div>

    <RecipeCard v-for="recipe in recipes" :key="recipe.id" :recipe="recipe" mode="copy" />
  </v-container>
</template>

<style scoped>
.loading-container {
  height: 50vh;
}
</style>
