<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <div
    class="mx-auto flex h-dvh w-full max-w-md flex-col overflow-hidden bg-background text-foreground"
  >
    <RouterView />
  </div>
</template>
