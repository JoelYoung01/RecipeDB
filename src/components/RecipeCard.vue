<script setup lang="ts">
import type { UploadSlim, RecipeSlim } from "@/types";
import defaultImage from "@/assets/default-recipe.jpg";
import { get } from "@/utils";

interface Props {
  recipe: RecipeSlim;
}

const props = defineProps<Props>();

const loading = ref(false);
const upload = ref<UploadSlim>();

const imageUrl = computed(() => {
  if (loading.value) return "";
  if (!upload.value) return defaultImage

  let url = upload.value.url

  if (import.meta.env.DEV) {
    url = `http://localhost:8000${url}`
  }

  return url
})

async function getImageDetails() {
  if (!props.recipe.cover_image_id) return

  loading.value = true
  try {
    upload.value = await get(`/upload/${props.recipe.cover_image_id}/`)
  } catch (er) {
    console.error(er)
  }
  loading.value = false
}

watch(() => props.recipe.cover_image_id, getImageDetails, { immediate: true})
</script>

<template>
  <v-card :to="`/recipe/${recipe.id}/detail`">
    <v-row>
      <v-col cols="5">
        <v-img :src="imageUrl" cover aspect-ratio="1">
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
