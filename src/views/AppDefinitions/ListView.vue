<script setup lang="ts">
import { useSessionStore } from "@/stores/session";
import { AppDefinitionStatus, type AppDefinitionDashboard } from "@/types";
import { formatDate, get } from "@/utils";

const sessionStore = useSessionStore();

const appDefinitions = ref<AppDefinitionDashboard[]>([]);

async function getAppDefinitions() {
  appDefinitions.value = await get(`/app-definition/`);
}
function isActive(def: AppDefinitionDashboard) {
  return def.status === AppDefinitionStatus.Active;
}

getAppDefinitions();
</script>

<template>
  <v-container>
    <div class="d-flex">
      <h1>App Definitions</h1>

      <v-spacer />

      <v-btn
        v-if="sessionStore.currentUser?.admin"
        color="primary"
        prepend-icon="mdi-plus"
        to="/app-definition/create"
        >Create New</v-btn
      >
    </div>
    <v-row>
      <v-col v-for="definition in appDefinitions" :key="definition.id" cols="3">
        <v-card :to="`/app-definition/${definition.id}/detail`">
          <v-card-title class="d-flex align-center">
            <div class="me-2">{{ definition.name }}</div>
            <v-chip v-if="isActive(definition)" variant="elevated" color="success" size="small">
              Active
            </v-chip>
            <v-spacer />
            <span class="fs-7 text-disabled"
              >{{ formatDate(definition.start_date, true) }} -
              {{ formatDate(definition.due_date, true) }}</span
            >
          </v-card-title>
          <v-card-text>
            {{ definition.description }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.fs-7 {
  font-size: 0.75rem;
}
</style>
