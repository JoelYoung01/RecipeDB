<script setup lang="ts">
import AddMenuSheet from "@/components/AddMenuSheet.vue";
import AppTabBar from "@/components/AppTabBar.vue";
import { provideAddMenu } from "@/composables/useAddMenu";
import { RouterView } from "vue-router";

const addMenuOpen = provideAddMenu();
</script>

<template>
  <div class="relative flex h-full min-h-0 flex-col">
    <main
      data-app-scroll
      class="app-scroll min-h-0 flex-1 overflow-y-auto overscroll-y-contain pb-[calc(5.5rem+env(safe-area-inset-bottom))]"
    >
      <RouterView />
    </main>
    <AppTabBar v-model:open="addMenuOpen" />
    <AddMenuSheet v-model:open="addMenuOpen" />
  </div>
</template>
