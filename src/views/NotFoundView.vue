<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { paths } from "@/sitemap";
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="flex min-h-dvh flex-col items-center justify-center gap-4 px-6 text-center">
    <p class="text-sm font-semibold tracking-wide text-[#22c55e]">404</p>
    <h1 class="text-2xl font-bold">Page not found</h1>
    <p class="text-sm text-muted-foreground">That route isn’t on the map.</p>
    <Button @click="router.push(paths.home)">Go home</Button>
  </div>
</template>
