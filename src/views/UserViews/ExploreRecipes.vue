<script setup lang="ts">
import RecipeCard from "@/components/RecipeCard.vue";
import { get } from "@/utils";

const recipes = ref<any[]>([]);
const loading = ref(false);
const searched = ref(false);
const searchText = ref<string>("");

async function getResults() {
  if (loading.value) return;

  loading.value = true;
  try {
    recipes.value = await get(`/recipe/search/?searchText=${searchText.value}`);
  } catch (error) {
    console.error("Error fetching recipes:", error);
    recipes.value = [];
  } finally {
    loading.value = false;
    searched.value = true;
  }
}
</script>

<template>
  <v-container>
    <section>
      <v-text-field
        v-model="searchText"
        label="Search recipes"
        placeholder="Enter keywords to search..."
        clearable
        hide-details="auto"
        variant="outlined"
        rounded
        @keyup.enter="getResults"
      >
        <template #append-inner>
          <v-btn icon variant="text" :disabled="loading" @click="getResults">
            <v-icon>mdi-magnify</v-icon>
          </v-btn>
        </template>
      </v-text-field>
    </section>

    <section>
      <v-progress-linear v-if="loading" indeterminate color="primary" class="mb-4" />

      <RecipeCard
        v-for="recipe in recipes"
        :key="recipe.id"
        :recipe="recipe"
        class="mb-3"
        mode="public"
      />

      <v-alert
        v-if="!recipes.length && searchText && !loading && searched"
        type="info"
        variant="tonal"
      >
        No recipes found matching your search.
      </v-alert>
    </section>
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
