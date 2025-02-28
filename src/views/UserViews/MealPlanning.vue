<script setup lang="ts">
import defaultImage from "@/assets/default-recipe.jpg";
import type { PlannedRecipeDetail } from "@/types/PlannedRecipe";
import type { RecipeDashboard } from "@/types/Recipe";
import { get, post } from "@/utils";
import { onMounted } from "vue";

const selectedDate = ref(new Date());
const plannedRecipes = ref<PlannedRecipeDetail[]>([]);
const recipes = ref<RecipeDashboard[]>([]);
const showRecipeDialog = ref(false);
const selectedRecipes = ref<RecipeDashboard[]>([]);

const formattedSelectedDate = computed(() => {
  const date = selectedDate.value;
  const currentYear = new Date().getFullYear();
  const month = date.toLocaleString("en-US", { month: "short" });
  const day = date.getDate();
  const year = date.getFullYear();

  if (year === currentYear) {
    return `${month} ${day}`;
  }
  return `${month} ${day} ${year}`;
});

const currentPlannedRecipes = computed(() =>
  plannedRecipes.value.filter((r) =>
    r.planned_for.startsWith(selectedDate.value.toISOString().slice(0, 10))
  )
);

async function getPlannedRecipes() {
  try {
    // Get the start and end of the current month
    const date = selectedDate.value;
    const start = new Date(date.getFullYear(), date.getMonth(), 1);
    const end = new Date(date.getFullYear(), date.getMonth() + 1, 0);

    const response = await post<PlannedRecipeDetail[]>("/planned-recipe/time-frame/", {
      start: start.toISOString(),
      end: end.toISOString()
    });
    plannedRecipes.value = response;
  } catch (error) {
    console.error("Error fetching planned recipes:", error);
  }
}

async function getRecipes() {
  try {
    recipes.value = await get("/recipe/user/");
  } catch (error) {
    console.error("Error fetching recipes:", error);
  }
}

async function assignRecipe() {
  if (!selectedRecipes.value.length) return;

  try {
    const promises = selectedRecipes.value.map((sr) =>
      post("/planned-recipe/", {
        recipe_id: sr.id,
        planned_for: selectedDate.value.toISOString()
      })
    );
    await Promise.all(promises);
    await getPlannedRecipes();
    showRecipeDialog.value = false;
    selectedRecipes.value = [];
  } catch (error) {
    console.error("Error assigning recipe:", error);
  }
}

function getRecipeImageUrl(recipe: RecipeDashboard) {
  if (!recipe.cover_image) return defaultImage;
  let url = recipe.cover_image.url;

  if (import.meta.env.DEV) {
    url = "http://localhost:8000" + url;
  }

  return url;
}

onMounted(() => {
  getPlannedRecipes();
  getRecipes();
});
</script>

<template>
  <h3 class="mt-2 mx-3 text-h4 mb-0">Meal Planning</h3>

  <v-date-picker v-model="selectedDate" show-adjacent-months hide-header class="w-100" />

  <v-card class="mx-2">
    <v-card-title> Selected Date: {{ formattedSelectedDate }} </v-card-title>
    <v-card-text>
      <div v-if="currentPlannedRecipes.length">
        <h3>Planned Recipe(s):</h3>
        <v-card
          v-for="planned in currentPlannedRecipes"
          :key="planned.id"
          variant="outlined"
          class="mt-2"
        >
          <v-card-title>
            {{ planned.recipe.name }}
          </v-card-title>
          <v-card-text>
            {{ planned.recipe.description }}
          </v-card-text>
        </v-card>
      </div>
      <div v-else>
        <p>No recipes planned for this date</p>
      </div>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" @click="showRecipeDialog = true">
        {{ currentPlannedRecipes.length ? "Change Recipe" : "Add Recipe" }}
      </v-btn>
    </v-card-actions>
  </v-card>

  <!-- Recipe Selection Dialog -->
  <v-dialog v-model="showRecipeDialog" max-width="500px">
    <v-card>
      <v-card-title>Select Recipe</v-card-title>
      <v-autocomplete
        v-model="selectedRecipes"
        :items="recipes"
        item-title="name"
        variant="outlined"
        density="compact"
        class="px-4"
        multiple
        return-object
      >
        <template #item="{ props, item }">
          <v-list-item v-bind="props" :title="item.raw.name" :subtitle="item.raw.description">
            <template #prepend>
              <div class="me-2 my-n1 ms-n4">
                <v-img :src="getRecipeImageUrl(item.raw)" cover aspect-ratio="1" width="64">
                  <template #placeholder>
                    <v-row class="fill-height ma-0" align="center" justify="center">
                      <v-progress-circular indeterminate color="primary" />
                    </v-row>
                  </template>
                </v-img>
              </div>
            </template>
          </v-list-item>
        </template>
      </v-autocomplete>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" :disabled="!selectedRecipes.length" @click="assignRecipe">
          Assign Recipe
        </v-btn>
        <v-btn color="error" @click="showRecipeDialog = false">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
