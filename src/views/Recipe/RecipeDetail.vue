<script setup lang="ts">
import defaultImage from "@/assets/default-recipe.jpg";
import { useSessionStore } from "@/stores/session";
import type { RecipeDetail } from "@/types";
import { ApiError, get } from "@/utils";
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const sessionStore = useSessionStore();
const router = useRouter();
const route = useRoute();

const recipe = ref<RecipeDetail>();

const formattedTime = computed(() => {
  if (!recipe.value || !recipe.value.prep_time) return "-";

  const hours = Math.floor(recipe.value.prep_time / 60);
  const minutes = recipe.value.prep_time % 60;
  if (hours && minutes) {
    return `${hours} hours and ${minutes} minutes`;
  } else if (hours) {
    return `${hours} hours`;
  } else {
    return `${minutes} minutes`;
  }
});

const returnUrl = computed(() => {
  const back = window.history.state.back;

  if (back.includes("/login")) return false;

  if (back.includes("edit")) return "/home";

  return back;
});

async function getRecipeDetails() {
  try {
    recipe.value = await get(`/recipe/${route.params.recipeId}/`);
  } catch (er) {
    if ((er as ApiError).status === 404) {
      router.push("/not-found");
    } else {
      console.error(er);
    }
  }
}

function scrollToIngredients() {
  const element = document.getElementById("ingredients");
  if (element) {
    element.scrollIntoView({ behavior: "smooth" });
  }
}

onMounted(() => {
  getRecipeDetails();
});
</script>

<template>
  <div v-if="recipe" class="container">
    <v-img :src="defaultImage" class="background" cover />
    <div class="image-spacer d-flex pa-2">
      <v-btn
        v-if="returnUrl"
        :to="returnUrl"
        icon="mdi-arrow-left"
        variant="tonal"
        size="x-small"
      />
      <v-spacer />
      <v-btn
        v-if="recipe.created_by.id === sessionStore.currentUser?.id"
        icon="mdi-pencil"
        color="primary"
        size="x-small"
        :to="`/recipe/${route.params.recipeId}/edit`"
      />
    </div>
    <v-container class="content pa-5">
      <div class="d-flex align-center mb-2">
        <h3>{{ recipe.name }}</h3>
        <v-spacer />
        <v-btn size="small" color="primary" @click="scrollToIngredients"> Cook Now </v-btn>
      </div>

      <section>
        <v-row>
          <v-col>
            <v-card class="h-100 text-center text-body-2 pa-2">
              <p class="text-medium-emphasis">Total Time</p>
              <p>{{ formattedTime }}</p>
            </v-card>
          </v-col>
          <v-col>
            <v-card class="h-100 text-center text-body-2 pa-2">
              <p class="text-medium-emphasis">Ingredients</p>
              <p>{{ recipe.ingredients.length }}</p>
            </v-card>
          </v-col>
        </v-row>
      </section>

      <section>
        <h4>About Recipe</h4>
        <p>{{ recipe.description }}</p>
      </section>

      <section id="ingredients">
        <h4>Ingredients</h4>
        <div v-for="ingredient in recipe.ingredients" :key="ingredient.id">
          {{ ingredient.amount }} {{ ingredient.units }} - {{ ingredient.name }}
        </div>
      </section>

      <section>
        <h4>Instructions</h4>
        <pre>{{ recipe.instructions }}</pre>
      </section>

      <section>
        <h4>Notes</h4>
        <pre>{{ recipe.notes }}</pre>
      </section>
    </v-container>
  </div>
</template>

<style scoped>
section {
  margin-bottom: 1rem;
}

pre {
  font-family: inherit;
  white-space: pre-wrap;
}

.container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

/* Fixed background image covering the entire viewport */
.background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 15rem;
  background-size: cover;
  background-position: center;
}

.image-spacer {
  height: 14rem;
}
.action-spacer {
  height: 14rem;
}

/* v-container content scrolls on top of the background */
.content {
  background-color: white;
  border-top-left-radius: 1rem;
  border-top-right-radius: 1rem;
  position: relative;
  z-index: 1;
  overflow-y: auto;
}

.actions {
  position: fixed;
  bottom: 5rem;
  left: 0;
  width: 100%;
}
</style>
