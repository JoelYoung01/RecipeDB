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

watch(searchText, () => (searched.value = false));
</script>

<template>
  <v-container>
    <section>
      <div class="d-flex align-center gap-2">
        <v-text-field
          v-model="searchText"
          label="Search recipes"
          placeholder="Enter keywords to search..."
          clearable
          hide-details="auto"
          variant="outlined"
          rounded
          @keyup.enter="getResults"
        />
        <v-btn icon color="primary" :loading="loading" @click="getResults">
          <v-icon>mdi-magnify</v-icon>
        </v-btn>
      </div>

      <v-alert
        v-if="!recipes.length && !searchText && !loading && !searched"
        type="info"
        variant="tonal"
        class="mt-2"
      >
        Search Recipes by entering text in the search bar above!
      </v-alert>
      <v-alert
        v-else-if="!recipes.length && searchText && !loading && searched"
        type="info"
        variant="tonal"
        class="mt-2"
      >
        No recipes found matching your search.
      </v-alert>
    </section>

    <section>
      <RecipeCard
        v-for="recipe in recipes"
        :key="recipe.id"
        :recipe="recipe"
        class="mb-3"
        mode="public"
      />
    </section>
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
