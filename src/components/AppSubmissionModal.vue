<script setup lang="ts">
import type { AppDefinitionDashboard } from "@/types";
import { post } from "@/utils";

interface Props {
  modelValue: boolean;
  definition?: AppDefinitionDashboard;
}
const props = defineProps<Props>();
const emit = defineEmits<{
  "update:model-value": [value: boolean];
  submit: [];
}>();

const form = reactive({
  link: null as string | null
});
const validForm = computed(() => {
  return form.link;
});

function resetForm() {
  for (const key in form) {
    form[key as keyof typeof form] = null;
  }
}

async function onSubmit() {
  if (!props.definition) return;

  try {
    const payload = {
      ...form,
      app_definition_id: props.definition.id
    };

    await post(`/app-submission/`, payload);
    resetForm();
    emit("update:model-value", false);
    emit("submit");
  } catch (er) {
    console.error(er);
  }
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    max-width="500"
    @update:model-value="emit('update:model-value', $event)"
  >
    <v-card>
      <v-card-title>Create Submission</v-card-title>
      <v-card-text>
        <v-text-field v-model="form.link" label="App Link" />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn @click="emit('update:model-value', false)">Cancel</v-btn>
        <v-btn variant="flat" color="green" :disabled="!validForm" @click="onSubmit()">
          Submit
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
