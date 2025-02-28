<script setup lang="ts">
import type { RecipeDetail } from "@/types";
import defaultImage from "@/assets/default-recipe.jpg";

type SizeOption = "sm" | "md" | "lg";
type ModeOption = "default" | "public";

interface Props {
  recipe: Partial<RecipeDetail>;
  size?: SizeOption;
  mode?: ModeOption;
}

const props = withDefaults(defineProps<Props>(), {
  size: "md",
  mode: "default"
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
        <div v-if="mode === 'default'" class="text-disabled d-flex align-center gap-1">
          <v-icon icon="mdi-clock" size="small" />
          {{ recipe.prep_time ?? "-" }} minutes
        </div>
        <div v-else-if="mode === 'public'" class="text-disabled created-by">
          Created by {{ recipe.created_by?.display_name ?? "-" }}
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

.created-by {
  font-size: small;
}
</style>
