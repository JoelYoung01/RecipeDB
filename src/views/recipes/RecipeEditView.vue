<script setup lang="ts">
import ImageUploadDialog from "@/components/ImageUploadDialog.vue";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { paths } from "@/sitemap";
import type { IngredientCreate, RecipeCreate, RecipeDetail } from "@/types";
import { ApiError, del, get, post, put } from "@/utils";
import { Plus, Trash2 } from "@lucide/vue";
import { computed, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

type IngredientForm = Partial<IngredientCreate> & { id?: number };

const router = useRouter();
const route = useRoute();

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

const creating = computed(() => route.name === "recipe-new");
const returnUrl = computed(() => {
  const param = Array.isArray(route.query.returnUrl)
    ? route.query.returnUrl.at(-1)
    : route.query.returnUrl;
  if (param) return param;

  if (creating.value) return paths.home;

  const detailParam = Array.isArray(route.query.detailReturnUrl)
    ? route.query.detailReturnUrl.at(-1)
    : route.query.detailReturnUrl;

  let url = paths.recipeDetail(String(route.params.recipeId));
  if (detailParam) url += `?returnUrl=${encodeURIComponent(detailParam)}`;
  return url;
});

const validForm = computed(
  () =>
    form.name &&
    form.description &&
    form.instructions &&
    ingredientForms.length > 0 &&
    ingredientForms.every((ing) => ing.name)
);
const canSave = computed(() => !!validForm.value && !saving.value && !loading.value);

async function getRecipeDetails() {
  if (creating.value) return;
  loading.value = true;
  try {
    recipeDetail.value = await get(`/recipe/${route.params.recipeId}/`);
    fillForms();
  } catch (er) {
    if ((er as ApiError).status === 404) {
      router.push({ name: "not-found" });
    } else {
      console.error(er);
    }
  }
  loading.value = false;
}

async function saveChanges() {
  if (saving.value || !canSave.value) return;
  saving.value = true;
  try {
    if (!form.prep_time && form.prep_time !== 0) form.prep_time = undefined;

    let recipeId: number;
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

  await Promise.all([
    ...newIngredients.map((ing) => post(`/ingredient/`, { ...ing, recipe_id: recipeId })),
    ...updateIngredients.map((ing) => put(`/ingredient/${ing.id}/`, ing)),
    ...deleteIngredients.map((ing) => del(`/ingredient/${ing.id}/`))
  ]);
}

function fillForms() {
  if (!recipeDetail.value) return;
  for (const key of Object.keys(form) as (keyof typeof form)[]) {
    // @ts-expect-error keyed assign from detail
    form[key] = recipeDetail.value[key] ?? null;
  }
  ingredientForms.splice(0);
  for (const ingredient of recipeDetail.value.ingredients) {
    ingredientForms.push({
      id: ingredient.id,
      name: ingredient.name,
      amount: ingredient.amount,
      units: ingredient.units,
      details: ingredient.details
    });
  }
}

function addIngredient() {
  ingredientForms.push({ ...defaultIngredient });
}

function removeIngredient(index: number) {
  ingredientForms.splice(index, 1);
}

onMounted(() => {
  if (creating.value && ingredientForms.length === 0) addIngredient();
  getRecipeDetails();
});
</script>

<template>
  <div class="px-4 pt-5 pb-24">
    <h1 class="text-xl font-bold">{{ creating ? "New recipe" : "Edit recipe" }}</h1>

    <form class="mt-4 flex flex-col gap-4" @submit.prevent="saveChanges">
      <ImageUploadDialog v-model="form.cover_image_id" />

      <div class="space-y-2">
        <Label for="name">Name</Label>
        <Input id="name" v-model="form.name" class="h-11 rounded-xl bg-card" required />
      </div>

      <div class="space-y-2">
        <Label for="description">Description</Label>
        <Textarea
          id="description"
          v-model="form.description"
          class="min-h-24 rounded-xl bg-card"
          required
        />
      </div>

      <div class="space-y-2">
        <Label for="instructions">Instructions</Label>
        <Textarea
          id="instructions"
          v-model="form.instructions"
          class="min-h-32 rounded-xl bg-card"
          required
        />
      </div>

      <div class="space-y-2">
        <Label for="notes">Notes</Label>
        <Textarea id="notes" v-model="form.notes" class="min-h-20 rounded-xl bg-card" />
      </div>

      <div class="space-y-2">
        <Label for="prep">Prep time (min)</Label>
        <Input
          id="prep"
          v-model.number="form.prep_time"
          type="number"
          min="0"
          class="h-11 rounded-xl bg-card"
        />
      </div>

      <label class="flex items-center gap-2 text-sm">
        <Checkbox :model-value="!!form.public" @update:model-value="form.public = !!$event" />
        Public recipe
      </label>

      <div class="flex items-center justify-between">
        <h2 class="text-sm font-semibold">Ingredients</h2>
        <Button type="button" size="icon-sm" variant="ghost" @click="addIngredient">
          <Plus class="size-4" />
        </Button>
      </div>

      <div
        v-for="(ingredient, index) in ingredientForms"
        :key="index"
        class="grid grid-cols-[1fr_4.5rem_4rem_1fr_auto] gap-1.5"
      >
        <Input
          v-model="ingredient.name"
          placeholder="Name"
          class="h-9 rounded-lg bg-card text-xs"
        />
        <Input
          v-model.number="ingredient.amount"
          type="number"
          placeholder="Amt"
          class="h-9 rounded-lg bg-card text-xs"
        />
        <Input
          v-model="ingredient.units"
          placeholder="Unit"
          class="h-9 rounded-lg bg-card text-xs"
        />
        <Input
          v-model="ingredient.details"
          placeholder="Details"
          class="h-9 rounded-lg bg-card text-xs"
        />
        <Button type="button" size="icon-sm" variant="destructive" @click="removeIngredient(index)">
          <Trash2 class="size-3.5" />
        </Button>
      </div>
    </form>

    <div
      class="fixed bottom-[calc(5.5rem+env(safe-area-inset-bottom))] left-1/2 z-30 flex w-full max-w-md -translate-x-1/2 gap-2 px-4"
    >
      <Button
        variant="outline"
        class="flex-1 border-border bg-card"
        :disabled="saving"
        @click="router.push(returnUrl)"
      >
        Cancel
      </Button>
      <Button class="flex-1" :disabled="!canSave" @click="saveChanges">
        {{ saving ? "Saving…" : "Save" }}
      </Button>
    </div>
  </div>
</template>
