<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { formatPrepTime, mediaUrl } from "@/lib/media";
import { useSessionStore } from "@/stores/session";
import { syncAfterRecipeMutation } from "@/stores/sync";
import { paths } from "@/sitemap";
import type { RecipeDetail } from "@/types";
import { ApiError, del, get } from "@/utils";
import { ArrowLeft, Pencil } from "@lucide/vue";
import { computed, onMounted } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

const sessionStore = useSessionStore();
const router = useRouter();
const route = useRoute();

const recipe = ref<RecipeDetail>();
const deleteOpen = ref(false);
const loading = ref(false);

const owned = computed(() => recipe.value?.created_by.id === sessionStore.currentUser?.id);
const returnUrl = computed(() => {
  const param = Array.isArray(route.query.returnUrl)
    ? route.query.returnUrl.at(-1)
    : route.query.returnUrl;
  return param || paths.home;
});
const imageUrl = computed(() => mediaUrl(recipe.value?.cover_image?.url));
const formattedTime = computed(() => formatPrepTime(recipe.value?.prep_time) || "—");

async function getRecipeDetails() {
  loading.value = true;
  try {
    recipe.value = await get(`/recipe/${route.params.recipeId}/`);
  } catch (er) {
    if ((er as ApiError).status === 404) {
      router.push({ name: "not-found" });
    } else {
      console.error(er);
    }
  }
  loading.value = false;
}

async function deleteRecipe() {
  if (!owned.value) return;
  loading.value = true;
  try {
    await del(`/recipe/${route.params.recipeId}/`);
    syncAfterRecipeMutation();
    router.push(returnUrl.value);
  } catch (er) {
    console.error(er);
  }
  loading.value = false;
}

function scrollToIngredients() {
  document.getElementById("ingredients")?.scrollIntoView({ behavior: "smooth" });
}

onMounted(getRecipeDetails);
</script>

<template>
  <div v-if="recipe" class="relative">
    <div class="relative h-56 overflow-hidden">
      <img :src="imageUrl" :alt="recipe.name" class="size-full object-cover" />
      <div class="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-background" />
      <div class="absolute inset-x-0 top-0 flex items-center justify-between p-3">
        <Button
          size="icon-sm"
          variant="secondary"
          class="rounded-full bg-black/40 text-white backdrop-blur"
          :aria-label="'Back'"
          @click="router.push(returnUrl)"
        >
          <ArrowLeft class="size-4" />
        </Button>
        <Button
          v-if="owned"
          size="icon-sm"
          class="rounded-full"
          :aria-label="'Edit'"
          @click="
            router.push({
              path: paths.recipeEdit(String(route.params.recipeId)),
              query: { detailReturnUrl: returnUrl }
            })
          "
        >
          <Pencil class="size-4" />
        </Button>
      </div>
    </div>

    <div class="-mt-4 rounded-t-2xl border border-border bg-card px-5 pt-5 pb-8">
      <div class="flex items-start justify-between gap-3">
        <h1 class="text-xl font-bold leading-tight">{{ recipe.name }}</h1>
        <Button size="sm" class="shrink-0" @click="scrollToIngredients">Cook</Button>
      </div>

      <p v-if="!owned" class="mt-2 text-sm text-muted-foreground">
        Created by
        <RouterLink
          :to="paths.publicUser(recipe.created_by_id)"
          class="font-medium text-[#22c55e] hover:underline"
        >
          {{ recipe.created_by.display_name }}
        </RouterLink>
      </p>

      <div class="mt-4 grid grid-cols-2 gap-2">
        <div class="rounded-xl border border-border bg-secondary/50 px-3 py-3 text-center">
          <p class="text-xs text-muted-foreground">Total time</p>
          <p class="mt-1 text-sm font-semibold">{{ formattedTime }}</p>
        </div>
        <div class="rounded-xl border border-border bg-secondary/50 px-3 py-3 text-center">
          <p class="text-xs text-muted-foreground">Ingredients</p>
          <p class="mt-1 text-sm font-semibold">{{ recipe.ingredients.length }}</p>
        </div>
      </div>

      <section class="mt-5">
        <h2 class="mb-1 text-sm font-semibold">About</h2>
        <p class="text-sm text-muted-foreground whitespace-pre-wrap">{{ recipe.description }}</p>
        <p v-if="recipe.public && owned" class="mt-2 text-xs text-[#4ade80]">
          This recipe is public.
        </p>
      </section>

      <section id="ingredients" class="mt-5 scroll-mt-4">
        <h2 class="mb-2 text-sm font-semibold">Ingredients</h2>
        <ul class="space-y-1.5 text-sm">
          <li
            v-for="ingredient in recipe.ingredients"
            :key="ingredient.id"
            class="rounded-lg bg-secondary/40 px-3 py-2"
          >
            <span class="text-muted-foreground"
              >{{ ingredient.amount }} {{ ingredient.units }}</span
            >
            — {{ ingredient.name }}
            <span v-if="ingredient.details" class="text-faint"> ({{ ingredient.details }}) </span>
          </li>
        </ul>
      </section>

      <section class="mt-5">
        <h2 class="mb-1 text-sm font-semibold">Instructions</h2>
        <pre class="font-sans text-sm whitespace-pre-wrap text-muted-foreground">{{
          recipe.instructions
        }}</pre>
      </section>

      <section v-if="recipe.notes" class="mt-5">
        <h2 class="mb-1 text-sm font-semibold">Notes</h2>
        <pre class="font-sans text-sm whitespace-pre-wrap text-muted-foreground">{{
          recipe.notes
        }}</pre>
      </section>

      <Button v-if="owned" variant="destructive" size="sm" class="mt-8" @click="deleteOpen = true">
        Delete recipe
      </Button>
    </div>

    <Dialog v-model:open="deleteOpen">
      <DialogContent class="max-w-sm border-border bg-card">
        <DialogHeader>
          <DialogTitle>Delete recipe?</DialogTitle>
          <DialogDescription>This can’t be undone.</DialogDescription>
        </DialogHeader>
        <DialogFooter class="gap-2">
          <Button variant="outline" :disabled="loading" @click="deleteOpen = false">Cancel</Button>
          <Button variant="destructive" :disabled="loading" @click="deleteRecipe">Delete</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>

  <div v-else-if="loading" class="px-4 pt-20 text-center text-sm text-muted-foreground">
    Loading…
  </div>
</template>
