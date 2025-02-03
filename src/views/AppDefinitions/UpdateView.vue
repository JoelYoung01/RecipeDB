<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";
import type { AppDefinition } from "@/types";
import { onMounted } from "vue";
import { ApiError, del, get, post, put } from "@/utils";

const route = useRoute();
const router = useRouter();

const detail = ref<AppDefinition>();
const form = reactive({
  id: null as number | null,
  name: null as string | null,
  start_date: null as string | null,
  due_date: null as string | null,
  description: null as string | null
});
const defaultReq = {
  id: null as number | null,
  name: null as string | null,
  description: null as string | null
};
const formValid = ref(false);
const requirementForms = reactive<(typeof defaultReq)[]>([]);

const creating = computed(() => {
  return !route.params.app_definition_id;
});
const canSubmit = computed(() => {
  return formValid.value && requirementForms.length > 0;
});
const cancelTo = computed(() => {
  if (creating.value) return `/app-definition/list`;
  return `/app-definition/${route.params.app_definition_id}/detail`;
});

const required = (val: string) => !!val || "Required";
function addReq() {
  requirementForms.push({ ...defaultReq });
}
function delReq(index: number) {
  requirementForms.splice(index, 1);
}
function processDate(dateString: string | null) {
  if (!dateString) {
    return null;
  } else if (dateString.includes("T")) {
    if (!dateString.includes("Z")) dateString += "Z";
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  } else {
    return new Date(`${dateString}T00:00:00`).toISOString().replace("Z", ""); // Assume midnight local time
  }
}

function fillForm() {
  if (!detail.value) return;
  for (const key in form) {
    form[key as keyof typeof form] = (detail.value[key as keyof typeof detail.value] ??
      null) as any;
  }

  for (const reqDetail of detail.value.requirements) {
    const reqForm = { ...defaultReq };
    for (const key in defaultReq) {
      reqForm[key as keyof typeof reqForm] = (reqDetail[key as keyof typeof reqDetail] ??
        null) as any;
    }
    requirementForms.push(reqForm);
  }
}

async function loadAppDefinition() {
  try {
    detail.value = await get(`/app-definition/${route.params.app_definition_id}/`);
    fillForm();
  } catch (er) {
    if ((er as ApiError).status === 404) {
      router.push(`/definition-not-found`);
    } else {
      console.error(er);
    }
  }
}

async function save() {
  try {
    let appDefId = null;

    if (creating.value) {
      const data = await post("/app-definition/", form);
      appDefId = data.id;
    } else {
      const data = await put(`/app-definition/${route.params.app_definition_id}/`, form);
      appDefId = data.id;
    }

    const createRequirements = requirementForms
      .filter((reqForm) => !reqForm.id)
      .map((req) => post(`/requirement/`, { ...req, app_definition_id: appDefId }));

    const updateRequirements = requirementForms
      .filter((reqForm) => reqForm.id)
      .map((req) => put(`/requirement/${req.id}/`, req));

    const deleteRequirements =
      detail.value?.requirements
        .filter((reqDetail) => !requirementForms.some((reqForm) => reqForm.id === reqDetail.id))
        .map((req) => del(`/requirement/${req.id}/`)) ?? [];

    await Promise.all([...createRequirements, ...updateRequirements, ...deleteRequirements]);
    router.push(`/app-definition/${appDefId}/detail`);
  } catch (er) {
    console.error(er);
  }
}

onMounted(() => {
  if (!creating.value) {
    loadAppDefinition();
  }
});
</script>

<template>
  <v-container>
    <v-form v-model="formValid" class="d-flex flex-column gap-2">
      <v-card class="d-flex align-center pa-3 gap-2">
        <h1>{{ creating ? "Create New" : "Update" }} App Definition</h1>

        <v-spacer />

        <v-btn prepend-icon="mdi-close" color="secondary" :to="cancelTo"> Cancel </v-btn>
        <v-btn prepend-icon="mdi-floppy" color="success" :disabled="!canSubmit" @click="save()">
          Save Changes
        </v-btn>
      </v-card>
      <v-card class="pa-3">
        <h2>Details</h2>
        <v-row>
          <v-col cols="4">
            <v-text-field v-model="form.name" :rules="[required]" label="Name" />
          </v-col>
          <v-col cols="4">
            <v-text-field
              label="Start Date"
              :rules="[required]"
              type="date"
              :model-value="processDate(form.start_date)"
              @update:model-value="form.start_date = processDate($event)"
            />
            <v-text-field
              label="Due Date"
              :rules="[required]"
              type="date"
              :model-value="processDate(form.due_date)"
              @update:model-value="form.due_date = processDate($event)"
            />
          </v-col>
          <v-col cols="4">
            <v-textarea v-model="form.description" label="Description"></v-textarea>
          </v-col>
        </v-row>
      </v-card>

      <v-card class="pa-3">
        <div class="d-flex align-end">
          <h2>Requirements</h2>
          <v-spacer />
          <v-btn prepend-icon="mdi-plus" color="primary" size="small" @click="addReq()">
            Add Requirement
          </v-btn>
        </div>
        <v-table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th class="action-col"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(reqForm, i) in requirementForms ?? []" :key="i">
              <td>
                <v-text-field
                  v-model="reqForm.name"
                  density="compact"
                  hide-details
                  class="py-1"
                  :rules="[required]"
                />
              </td>
              <td>
                <v-text-field
                  v-model="reqForm.description"
                  density="compact"
                  hide-details
                  class="py-1"
                  :rules="[required]"
                />
              </td>
              <td>
                <v-btn size="small" icon="mdi-delete" color="red" @click="delReq(i)" />
              </td>
            </tr>
            <tr v-if="requirementForms.length === 0">
              <td colspan="2">
                <v-btn prepend-icon="mdi-plus" color="primary" @click="addReq()">
                  Add Requirement
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card>
    </v-form>
  </v-container>
</template>

<style scoped>
.action-col {
  /* Basis of 0 shrinks col as much as possible */
  width: 0rem;
}
</style>
