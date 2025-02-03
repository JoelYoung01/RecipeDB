<script setup lang="ts">
import type { AppDefinitionDashboard, AppSubmissionDetail } from "@/types";
import { get } from "@/utils";
import { useSessionStore } from "@/stores/session";
import AppDefinitionCard from "@/components/AppDefinitionCard.vue";
import AppSubmissionModal from "@/components/AppSubmissionModal.vue";

const sessionStore = useSessionStore();

const appDefinitions = ref<AppDefinitionDashboard[]>();
const submissions = ref<AppSubmissionDetail[]>([]);
const activeApps = ref<AppDefinitionDashboard[]>();
const submitCardVisible = ref(false);
const submitDefinition = ref<AppDefinitionDashboard>();

const completeApps = computed(() => {
  return appDefinitions.value?.filter((app) => new Date(app.due_date + "Z") < new Date());
});

function onSubmitClick(definition: AppDefinitionDashboard) {
  submitDefinition.value = definition;
  submitCardVisible.value = true;
}

function appSubmissions(appId: number) {
  return submissions.value.filter((s) => s.app_definition_id === appId);
}

async function getAppDefinitions() {
  try {
    appDefinitions.value = await get(`/app-definition/`);
    activeApps.value = await get(`/app-definition/active/`);
  } catch (er) {
    console.error(er);
  }
}

async function getSubmissions() {
  try {
    submissions.value = await get("/app-submission/");
  } catch (er) {
    console.error(er);
  }
}

watch(
  () => sessionStore.currentUser,
  (value) => {
    if (value) {
      getAppDefinitions();
      getSubmissions();
    }
  },
  { immediate: true }
);
</script>

<template>
  <v-container>
    <section>
      <h2>Active App</h2>
      <v-alert v-if="!activeApps?.length" type="info"> No Active Apps found in db. </v-alert>
      <v-row v-else>
        <v-col v-for="definition in activeApps" :key="definition.id" cols="4">
          <AppDefinitionCard
            :definition="definition"
            :submissions="appSubmissions(definition.id)"
            @add-submit="onSubmitClick(definition)"
          />
        </v-col>
      </v-row>
    </section>

    <section>
      <h2>Completed Applications</h2>
      <v-alert v-if="!completeApps?.length" type="info"> No Completed Apps found in db. </v-alert>
      <v-row v-else>
        <v-col v-for="definition in completeApps" :key="definition.id" cols="4">
          <AppDefinitionCard
            :definition="definition"
            :submissions="appSubmissions(definition.id)"
            @add-submit="onSubmitClick(definition)"
          />
        </v-col>
      </v-row>
    </section>

    <AppSubmissionModal
      v-model="submitCardVisible"
      :definition="submitDefinition"
      @submit="getSubmissions()"
    />
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}
</style>
