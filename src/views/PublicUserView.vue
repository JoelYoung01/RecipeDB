<script setup lang="ts">
import defaultUser from "@/assets/account-circle.svg";
import RecipeCard from "@/components/RecipeCard.vue";
import type { PublicUser, RecipeDashboard } from "@/types";
import { get, toast } from "@/utils";
import { onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const user = ref<PublicUser | null>(null);
const recipes = ref<RecipeDashboard[]>([]);
const loading = ref(true);

onMounted(async () => {
  loading.value = true;
  try {
    const id = route.params.userId;
    const [profile, list] = await Promise.all([
      get<PublicUser>(`/user/${id}/public/`),
      get<RecipeDashboard[]>(`/recipe/public/?user=${id}`)
    ]);
    user.value = profile;
    recipes.value = list;
  } catch (er) {
    console.error(er);
    toast.fromError(er, "Couldn’t load this cook’s profile.");
  }
  loading.value = false;
});
</script>

<template>
  <div class="px-4 pt-5">
    <div class="flex items-center gap-3">
      <img
        :src="user?.avatar_url || defaultUser"
        alt=""
        class="size-14 rounded-full object-cover ring-2 ring-border"
      />
      <div>
        <h1 class="text-xl font-bold">{{ user?.display_name || "Cook" }}</h1>
        <p class="text-sm text-muted-foreground">Public recipes</p>
      </div>
    </div>

    <p v-if="loading" class="mt-8 text-center text-sm text-muted-foreground">Loading…</p>
    <div v-else class="mt-5 flex flex-col gap-2">
      <RecipeCard v-for="recipe in recipes" :key="recipe.id" :recipe="recipe" mode="public" />
      <p
        v-if="!recipes.length"
        class="rounded-xl border border-border bg-card px-4 py-8 text-center text-sm text-muted-foreground"
      >
        No public recipes yet.
      </p>
    </div>
  </div>
</template>
