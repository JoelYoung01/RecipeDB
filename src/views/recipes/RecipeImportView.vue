<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { paths } from "@/sitemap";
import { syncAfterRecipeMutation } from "@/stores/sync";
import type { RecipeDetail } from "@/types";
import { getErrorMessage, post, toast } from "@/utils";
import { Camera, Link2, LoaderCircle, PenLine } from "@lucide/vue";
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const method = computed(() => {
  const m = route.query.method;
  return m === "photo" ? "photo" : "link";
});

const url = ref("");
const importing = ref(false);
const error = ref("");

const canImport = computed(() => {
  const value = url.value.trim();
  return Boolean(value) && !importing.value;
});

async function importFromUrl() {
  if (!canImport.value) return;
  importing.value = true;
  error.value = "";
  try {
    const recipe = await post<RecipeDetail>("/recipe/import-from-url/", {
      url: url.value.trim()
    });
    syncAfterRecipeMutation();
    toast.success("Recipe imported — review and save any edits.");
    router.push(paths.recipeEdit(recipe.id));
  } catch (er) {
    console.error(er);
    error.value = getErrorMessage(er, "Couldn’t import that recipe.");
    toast.fromError(er, "Couldn’t import that recipe.");
  }
  importing.value = false;
}
</script>

<template>
  <div class="px-4 pt-5">
    <h1 class="text-xl font-bold">Import a recipe</h1>
    <p class="mt-1 text-sm text-muted-foreground">
      Paste a link to a recipe website and we’ll pull ingredients and steps.
    </p>

    <div class="mt-5 flex gap-2">
      <Button
        type="button"
        size="sm"
        :variant="method === 'link' ? 'default' : 'outline'"
        @click="router.replace(`${paths.recipeImport}?method=link`)"
      >
        <Link2 class="size-4" />
        Link
      </Button>
      <Button
        type="button"
        size="sm"
        :variant="method === 'photo' ? 'default' : 'outline'"
        @click="router.replace(`${paths.recipeImport}?method=photo`)"
      >
        <Camera class="size-4" />
        Photo
      </Button>
    </div>

    <div class="mt-5 rounded-xl border border-border bg-card p-4">
      <template v-if="method === 'link'">
        <Label for="import-url" class="text-muted-foreground">Recipe URL</Label>
        <Input
          id="import-url"
          v-model="url"
          type="url"
          inputmode="url"
          autocomplete="url"
          placeholder="https://…"
          class="mt-2 h-11 rounded-xl border-border bg-secondary"
          :disabled="importing"
          @keydown.enter.prevent="importFromUrl"
        />
        <Button class="mt-4 w-full" :disabled="!canImport" @click="importFromUrl">
          <LoaderCircle v-if="importing" class="size-4 animate-spin" />
          {{ importing ? "Importing…" : "Import from link" }}
        </Button>
        <p v-if="error" class="mt-3 text-xs text-destructive">{{ error }}</p>
        <p v-else class="mt-3 text-xs text-faint">
          Works best with recipe blogs and sites that list ingredients in writing. Social video
          links aren’t supported yet.
        </p>
      </template>
      <template v-else>
        <div
          class="flex min-h-[180px] flex-col items-center justify-center rounded-xl border border-dashed border-border bg-secondary/50 px-4 text-center"
        >
          <Camera class="mb-2 size-8 text-[#22c55e]" />
          <p class="text-sm font-semibold">Scan a photo</p>
          <p class="mt-1 text-xs text-muted-foreground">
            Cookbook pages and handwritten cards — not available yet.
          </p>
        </div>
        <Button class="mt-4 w-full" disabled>Choose photo</Button>
      </template>
    </div>

    <Button
      variant="outline"
      class="mt-4 w-full border-border"
      @click="router.push(paths.recipeNew)"
    >
      <PenLine class="size-4" />
      Write from scratch instead
    </Button>
  </div>
</template>
