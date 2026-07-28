<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { paths } from "@/sitemap";
import { ListPlus } from "@lucide/vue";
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="px-4 pt-5">
    <h1 class="text-xl font-bold">Shopping list</h1>
    <p class="mt-1 text-sm text-muted-foreground">
      Plan dinners first — a shopping list surface will land here without changing today’s API.
    </p>

    <div
      class="mt-8 flex flex-col items-center rounded-xl border border-border bg-card px-6 py-12 text-center"
    >
      <div
        class="mb-3 flex size-12 items-center justify-center rounded-xl bg-[rgba(34,197,94,0.15)]"
      >
        <ListPlus class="size-6 text-[#22c55e]" />
      </div>
      <p class="text-sm font-semibold">No list yet</p>
      <p class="mt-1 max-w-xs text-xs text-muted-foreground">
        This tab matches the app chrome from the home design. Persistence isn’t part of this
        rewrite.
      </p>
      <Button class="mt-5" @click="router.push(paths.planner)">Open planner</Button>
    </div>
  </div>
</template>
