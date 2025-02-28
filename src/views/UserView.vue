<script setup lang="ts">
import { useRoute } from "vue-router";

const route = useRoute();
</script>

<template>
  <RouterView />

  <v-app-bar location="bottom" dense color="primary" :elevation="2">
    <div class="flex-grow-1 d-flex justify-space-around">
      <v-btn variant="text" icon="mdi-home" to="/home" />
      <v-btn variant="text" icon="mdi-magnify" to="/discover" />
      <v-btn variant="text" icon="mdi-notebook" to="/my-recipes" />
      <v-btn variant="text" icon="mdi-calendar" to="/meal-planning" />
      <v-btn variant="text" icon>
        <v-icon icon="mdi-menu" />
        <v-menu activator="parent">
          <v-list density="compact">
            <v-list-item prepend-icon="mdi-account" to="/my-account"> My Account </v-list-item>
            <v-list-item
              :to="`/add-recipe?returnUrl=${route.fullPath}`"
              prepend-icon="mdi-plus-box"
            >
              Add Recipe
            </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
    </div>
  </v-app-bar>
</template>

<style scoped></style>
