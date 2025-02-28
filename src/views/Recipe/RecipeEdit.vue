<script setup lang="ts">
import ImageUploadModal from "@/components/ImageUploadModal.vue";
import type { RecipeCreate, RecipeDetail, IngredientCreate } from "@/types";
import { ApiError, get, post, put, required, isNumber, del } from "@/utils";
import { onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

type IngredientForm = Partial<IngredientCreate> & { id?: number };

const router = useRouter();
const route = useRoute();

// TODO: Allow users to copy recipes

const defaultIngredient: IngredientForm = {
  id: undefined,
  name: undefined,
  amount: undefined,
  units: undefined,
  details: undefined
};

const recipeDetail = ref<RecipeDetail>();
const saving = ref(false);
const loading = ref(false);
const form = reactive<Partial<RecipeCreate>>({
  name: undefined,
  description: undefined,
  instructions: undefined,
  notes: undefined,
  created_on: undefined,
  public: false,
  prep_time: undefined,
  cover_image_id: undefined
});
const ingredientForms = reactive<IngredientForm[]>([]);

const creating = computed(() => route.params.recipeId === undefined);
const returnUrl = computed(() => {
  const param = Array.isArray(route.query.returnUrl)
    ? route.query.returnUrl.at(-1)
    : route.query.returnUrl;
  if (param) return param;

  if (creating.value) return "/home";

  const detailParam = Array.isArray(route.query.detailReturnUrl)
    ? route.query.detailReturnUrl.at(-1)
    : route.query.detailReturnUrl;

  let returnUrl = `/recipe/${route.params.recipeId}/detail`;
  if (detailParam) returnUrl += `?returnUrl=${detailParam}`;

  return returnUrl;
});
const validForm = computed(
  () =>
    form.name &&
    form.description &&
    form.instructions &&
    ingredientForms.length > 0 &&
    ingredientForms.every((ing) => ing.name)
);
const canSave = computed(() => validForm.value && !saving.value && !loading.value);

async function getRecipeDetails() {
  if (creating.value) return;

  loading.value = true;
  try {
    recipeDetail.value = await get(`/recipe/${route.params.recipeId}/`);
    fillForms();
  } catch (er) {
    if ((er as ApiError).status === 404) {
      router.push("/not-found");
    } else {
      console.error();
    }
  }
  loading.value = false;
}

async function saveChanges() {
  if (saving.value || !canSave.value) return;

  saving.value = true;
  try {
    if (!form.prep_time && form.prep_time !== 0) form.prep_time = undefined;

    let recipeId = null;
    if (creating.value) {
      const result = await post(`/recipe/`, form);
      recipeId = result.id;
    } else {
      const result = await put(`/recipe/${route.params.recipeId}/`, form);
      recipeId = result.id;
    }

    await saveIngredients(recipeId);

    router.push(returnUrl.value);
  } catch (er) {
    console.error(er);
  }
  saving.value = false;
}

async function saveIngredients(recipeId: number) {
  const existingIngredients = recipeDetail.value?.ingredients ?? [];

  const newIngredients = ingredientForms.filter((ingredient) => !ingredient.id);
  const updateIngredients = ingredientForms.filter((ingredient) => ingredient.id);
  const deleteIngredients = existingIngredients.filter(
    (ingredient) => !ingredientForms.some((formIngredient) => formIngredient.id === ingredient.id)
  );

  const promises = [];

  promises.push(
    ...newIngredients.map((ing) => post(`/ingredient/`, { ...ing, recipe_id: recipeId }))
  );
  promises.push(...updateIngredients.map((ing) => put(`/ingredient/${ing.id}/`, ing)));
  promises.push(...deleteIngredients.map((ing) => del(`/ingredient/${ing.id}/`)));

  await Promise.all(promises);
}

function fillForms() {
  if (!recipeDetail.value) return;
  for (const key in form) {
    // @ts-expect-error It works stop yelling
    form[key] = recipeDetail.value[key] ?? null;
  }

  ingredientForms.splice(0);
  for (const ingredient of recipeDetail.value.ingredients) {
    const iForm = { ...defaultIngredient };
    for (const key in iForm) {
      // @ts-expect-error Stop yelling
      iForm[key] = ingredient[key];
    }
    ingredientForms.push(iForm);
  }
}

function addIngredient() {
  ingredientForms.push({ ...defaultIngredient });
}

function removeIngredient(index: number) {
  ingredientForms.splice(index, 1);
}

onMounted(() => {
  getRecipeDetails();
});
</script>

<template>
  <v-container>
    <v-form :disabled="loading" @submit.prevent="saveChanges()">
      <div class="d-flex">
        <ImageUploadModal v-model="form.cover_image_id" class="mb-3" />
        <v-spacer />

        <v-btn disabled color="secondary" variant="outlined" prepend-icon="mdi-import">
          Import
        </v-btn>
      </div>

      <v-text-field v-model="form.name" variant="solo" :rules="[required]" label="Name" />
      <v-textarea
        v-model="form.description"
        auto-grow
        variant="solo"
        :rules="[required]"
        label="Description"
      />
      <v-textarea
        v-model="form.instructions"
        auto-grow
        variant="solo"
        :rules="[required]"
        label="Instructions"
      />
      <v-textarea v-model="form.notes" auto-grow variant="solo" label="Notes" />
      <v-text-field
        v-model.number="form.prep_time"
        :rules="[isNumber]"
        variant="solo"
        type="number"
        label="Prep Time (min)"
      />
      <v-checkbox v-model="form.public" label="Public Recipe" density="compact" />

      <div class="d-flex align-center">
        <h4>Ingredients</h4>
        <v-spacer />
        <v-btn icon="mdi-plus" variant="text" size="x-small" @click="addIngredient" />
      </div>
      <section id="ingredients-inputs">
        <v-row no-gutters class="mb-1">
          <v-col cols="4" class="pe-1"> Name </v-col>
          <v-col cols="2" class="pe-1"> Amount </v-col>
          <v-col cols="2" class="pe-1"> Units </v-col>
          <v-col cols="3"> Details </v-col>
        </v-row>
        <v-row
          v-for="(ingredient, index) in ingredientForms"
          :key="index"
          no-gutters
          class="mb-1 align-center"
        >
          <v-col cols="4" class="pe-1">
            <v-text-field
              v-model="ingredient.name"
              :rules="[required]"
              hide-details
              density="compact"
              variant="solo"
            />
          </v-col>
          <v-col cols="2" class="pe-1">
            <v-text-field
              v-model="ingredient.amount"
              hide-details
              :rules="[required]"
              density="compact"
              variant="solo"
              type="number"
            />
          </v-col>
          <v-col cols="2" class="pe-1">
            <v-text-field
              v-model="ingredient.units"
              hide-details
              density="compact"
              variant="solo"
            />
          </v-col>
          <v-col cols="3" class="pe-1">
            <v-text-field
              v-model="ingredient.details"
              hide-details
              density="compact"
              variant="solo"
            />
          </v-col>
          <v-col cols="1">
            <v-btn icon="mdi-delete" size="30" color="error" @click="removeIngredient(index)" />
          </v-col>
        </v-row>
      </section>
    </v-form>

    <div class="actions-spacer"></div>

    <div class="actions d-flex gap-2">
      <v-btn variant="tonal" :to="returnUrl" :disabled="saving">Cancel</v-btn>
      <v-btn color="success" :loading="saving" :disabled="!canSave" @click="saveChanges()">
        Save
      </v-btn>
    </div>
  </v-container>
</template>

<style scoped>
.actions {
  position: fixed;
  bottom: 4.5rem;
  right: 0.5rem;
}

.actions-spacer {
  height: 2.5rem;
}

#ingredients-inputs {
  font-size: 0.75rem;
}
#ingredients-inputs :deep(input) {
  padding: 0.25rem 0.25rem;
  min-height: 1rem;
  /* font-size: 0.75rem; */
}
</style>
