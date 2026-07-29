<script setup lang="ts">
import Toaster from "@/components/toast/Toaster.vue";
import { RouterView } from "vue-router";
</script>

<template>
  <div
    class="relative mx-auto flex h-dvh w-full max-w-md flex-col overflow-hidden bg-background text-foreground"
  >
    <Toaster />
    <RouterView />
  </div>
</template>
