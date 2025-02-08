<script setup lang="ts"></script>

<template>
  <v-app-bar location="bottom" dense color="primary" :elevation="2">
    <div class="flex-grow-1 d-flex justify-space-around">
      <v-btn variant="text" icon="mdi-home" to="/home" />
      <v-btn variant="text" icon="mdi-magnify" to="/discover" />
      <v-btn variant="text" icon="mdi-notebook" to="/my-recipes" />
      <v-btn variant="text" icon="mdi-account" to="/my-account" />
      <v-btn variant="text" icon>
        <v-icon icon="mdi-menu" />
        <v-menu activator="parent">
          <v-list density="compact">
            <v-list-item to="/add-recipe" prepend-icon="mdi-plus-box"> Add Recipe </v-list-item>
          </v-list>
        </v-menu>
      </v-btn>
    </div>
  </v-app-bar>

  <RouterView />
</template>

<style scoped></style>
