<script setup lang="ts">
import type { RecipeDashboard } from "@/types";
import defaultImage from "@/assets/default-recipe.jpg";

type SizeOption = "sm" | "md" | "lg";

interface Props {
  recipe: RecipeDashboard;
  size?: SizeOption;
}

const props = withDefaults(defineProps<Props>(), {
  size: "md"
});

const loading = ref(false);

const imageCols = computed(() => ({ sm: 3, md: 5, lg: 6 })[props.size]);
const imageUrl = computed(() => {
  if (loading.value) return "";
  if (!props.recipe.cover_image?.url) return defaultImage;

  let url = props.recipe.cover_image.url;

  if (import.meta.env.DEV) {
    url = `http://localhost:8000${url}`;
  }

  return url;
});
</script>

<template>
  <v-card :to="`/recipe/${recipe.id}/detail`" flat>
    <v-row dense>
      <v-col :cols="imageCols">
        <v-img :src="imageUrl" cover aspect-ratio="1" class="rounded">
          <template #placeholder>
            <v-row class="fill-height ma-0" align="center" justify="center">
              <v-progress-circular indeterminate color="primary" />
            </v-row>
          </template>
        </v-img>
      </v-col>
      <v-col>
        <div class="text-truncate-2 mb-1 font-weight-bold">{{ recipe.name }}</div>
        <div v-if="size !== 'sm'" class="text-truncate-2 mb-2">{{ recipe.description }}</div>
        <div class="text-disabled d-flex align-center gap-1">
          <v-icon icon="mdi-clock" size="small" />
          {{ recipe.prep_time ?? "-" }} minutes
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<style scoped>
.text-truncate-2 {
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
