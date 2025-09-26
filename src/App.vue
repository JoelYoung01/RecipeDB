<script setup lang="ts">
import { RouterView, useRoute } from "vue-router";

const route = useRoute();

const mainClassList = computed(() => {
  let classes = "";

  if (route.meta.useShadedBackground) {
    classes += "shaded-bg";
  }

  return classes;
});
</script>

<template>
  <v-app>
    <v-main :class="mainClassList">
      <RouterView />
    </v-main>
  </v-app>
</template>

<style scoped>
.shaded-bg {
  background-color: whitesmoke;
}

main {
  max-width: 480px;
  margin: 0 auto;
}
</style>
