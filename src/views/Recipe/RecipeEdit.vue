<script setup lang="ts">
import type { RecipeCreate, RecipeDetail } from "@/types";
import { ApiError, get } from "@/utils";
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const router = useRouter();
const route = useRoute();

const recipeDetail = ref<RecipeDetail>();
const validForm = ref(false);
const saving = ref(false);
const form = reactive<Partial<RecipeCreate>>({
  name: undefined,
  description: undefined,
  instructions: undefined,
  notes: undefined,
  created_on: undefined,
  public: false,
  prep_time: undefined,
  cover_image: undefined
});

const backPath = computed(() => {
  const back = window.history.state.back;
  if (back && !back.includes("/login?")) {
    return back;
  }

  return `/home`;
});

async function getRecipeDetails() {
  try {
    recipeDetail.value = await get(`/recipe/${route.params.recipeId}/`);
    fillForm();
  } catch (er) {
    if ((er as ApiError).status === 404) {
      router.push("/not-found");
    } else {
      console.error();
    }
  }
}

async function saveChanges() {
  //
}

function fillForm() {
  if (!recipeDetail.value) return;
  for (const key in form) {
    // @ts-expect-error It works stop yelling
    form[key] = recipeDetail.value[key] ?? null;
  }
}

onMounted(() => {
  getRecipeDetails();
});
</script>

<template>
  <v-container>
    <v-form v-model="validForm">
      <v-text-field variant="solo" label="Name" />
      <v-textarea variant="solo" label="Description" />
      <v-textarea variant="solo" label="Instructions" />
      <v-textarea variant="solo" label="Notes" />
      <v-text-field variant="solo" type="number" label="Prep Time (min)" />
    </v-form>

    <div class="actions d-flex gap-2">
      <v-btn variant="tonal" :to="backPath" :disabled="saving">Cancel</v-btn>
      <v-btn color="success" :loading="saving" @click="saveChanges()">Save</v-btn>
    </div>
  </v-container>
</template>

<style scoped>
.actions {
  position: fixed;
  bottom: 4.5rem;
  right: 0.5rem;
}
</style>
