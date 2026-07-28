<script setup lang="ts">
import AddMenuSheet from "@/components/AddMenuSheet.vue";
import AppTabBar from "@/components/AppTabBar.vue";
import { provideAddMenu } from "@/composables/useAddMenu";
import { RouterView } from "vue-router";

const addMenuOpen = provideAddMenu();
</script>

<template>
  <div class="relative flex min-h-dvh flex-col">
    <main class="flex-1 pb-[calc(5.5rem+env(safe-area-inset-bottom))]">
      <RouterView />
    </main>
    <AppTabBar v-model:open="addMenuOpen" />
    <AddMenuSheet v-model:open="addMenuOpen" />
  </div>
</template>
