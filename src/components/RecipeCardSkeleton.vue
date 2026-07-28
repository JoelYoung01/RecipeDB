<script setup lang="ts">
import { Skeleton } from "@/components/ui/skeleton";
</script>

<template>
  <div
    class="flex w-full items-stretch gap-3 overflow-hidden rounded-xl border border-border bg-card p-3"
  >
    <Skeleton class="size-20 shrink-0 rounded-lg" />
    <div class="flex min-w-0 flex-1 flex-col gap-2 py-0.5">
      <Skeleton class="h-4 w-3/5" />
      <Skeleton class="h-3 w-full" />
      <Skeleton class="h-3 w-2/3" />
      <Skeleton class="mt-1 h-3 w-16" />
    </div>
  </div>
</template>
