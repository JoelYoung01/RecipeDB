<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { paths } from "@/sitemap";
import { Camera, Link2, PenLine } from "@lucide/vue";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const method = computed(() => {
  const m = route.query.method;
  return m === "photo" ? "photo" : "link";
});

const url = ref("");
</script>

<template>
  <div class="px-4 pt-5">
    <h1 class="text-xl font-bold">Import a recipe</h1>
    <p class="mt-1 text-sm text-muted-foreground">
      Import tooling isn’t wired to the API yet — use these entry points or write from scratch.
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
          placeholder="https://…"
          class="mt-2 h-11 rounded-xl border-border bg-secondary"
          disabled
        />
        <Button class="mt-4 w-full" disabled>Import from link</Button>
        <p class="mt-3 text-xs text-faint">Coming soon — paste a URL and we’ll pull the recipe.</p>
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
