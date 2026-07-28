<script setup lang="ts">
import AddMenuSheet from "@/components/AddMenuSheet.vue";
import AppTabBar from "@/components/AppTabBar.vue";
import { provideAddMenu } from "@/composables/useAddMenu";
import { onMounted } from "vue";
import { RouterView } from "vue-router";

const addMenuOpen = provideAddMenu();

/** Tab roots kept alive so revisits paint instantly from cache. */
const cachedTabViews = ["HomeView", "RecipesView", "PlannerView", "ShoppingListView"];

onMounted(() => {
  // Prefetch sibling tab chunks during idle so the first switch isn’t blank.
  const prefetch = () => {
    void import("@/views/HomeView.vue");
    void import("@/views/recipes/RecipesView.vue");
    void import("@/views/planner/PlannerView.vue");
    void import("@/views/list/ShoppingListView.vue");
  };
  if (typeof requestIdleCallback === "function") {
    requestIdleCallback(prefetch, { timeout: 1500 });
  } else {
    setTimeout(prefetch, 200);
  }
});
</script>

<template>
  <div class="relative flex h-full min-h-0 flex-col">
    <main
      data-app-scroll
      class="app-scroll min-h-0 flex-1 overflow-y-auto overscroll-y-contain pb-[calc(5.5rem+env(safe-area-inset-bottom))]"
    >
      <RouterView v-slot="{ Component: Page, route }">
        <Transition name="page" mode="out-in">
          <KeepAlive :include="cachedTabViews">
            <component :is="Page" :key="String(route.name ?? route.path)" />
          </KeepAlive>
        </Transition>
      </RouterView>
    </main>
    <AppTabBar v-model:open="addMenuOpen" />
    <AddMenuSheet v-model:open="addMenuOpen" />
  </div>
</template>
