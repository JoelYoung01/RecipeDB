<script setup lang="ts">
import { post } from "@/utils";
import { onMounted } from "vue";

const todayRecipes = ref<any[]>();

async function getTodaysRecipes() {
  try {
    const payload = {
      start: new Date(new Date().setHours(0, 0, 0, 0)),
      end: new Date(new Date().setHours(23, 59, 59, 999))
    };
    todayRecipes.value = await post(`/planned-recipe/time-frame/`, payload);
  } catch (er) {
    console.error(er);
  }
}

onMounted(() => {
  getTodaysRecipes();
});
</script>

<template>
  <v-container>
    <section>
      <h2>Today's Menu</h2>
    </section>
    <section>
      <h2>Recently Added</h2>
    </section>
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
