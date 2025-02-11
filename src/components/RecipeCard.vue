<script setup lang="ts">
import type { RecipeSlim } from "@/types";
import defaultImage from "@/assets/default-recipe.jpg";

interface Props {
  recipe: RecipeSlim;
}

defineProps<Props>();
</script>

<template>
  <v-card :to="`/recipe/${recipe.id}/detail`">
    <v-row>
      <v-col cols="5">
        <v-img :src="defaultImage" cover aspect-ratio="1">
          <template #placeholder>
            <v-icon icon="mdi-chef-hat" />
          </template>
        </v-img>
      </v-col>
      <v-col>
        <div class="my-2">{{ recipe.name }}</div>
        <div class="text-disabled d-flex align-center gap-1">
          <v-icon icon="mdi-clock" size="small" />
          {{ recipe.prep_time ?? "-" }} minutes
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<style scoped></style>
