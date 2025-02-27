<script setup lang="ts">
import { postFile } from "@/utils";

const model = defineModel<number>();

const loading = ref(false);
const uploading = ref(false);
const dialog = ref(false);
const fileUpload = ref();
const btnText = computed(() => (model.value ? "Change Image" : "Upload Image"));
const btnVariant = computed(() => (model.value ? "flat" : "outlined"));
const btnColor = computed(() => (model.value ? "primary" : undefined));

// TODO: update this component so that the following flows work:
// mounted => fetch existing detail if exists => preview

// upload image => immediately uploaded => previewed => on 'save', emit id

watch(fileUpload, async (val) => {
  if (!val) return;

  uploading.value = true;
  const payload = new FormData();
  payload.append("file", val);
  const result = await postFile(`upload/`, payload);
  model.value = result.id;
  uploading.value = false;
});

async function saveImage() {
  loading.value = true;

  setTimeout(() => {
    loading.value = false;
    dialog.value = false;
  }, 5000);
}
</script>

<template>
  <v-btn
    class="border-dashed"
    prepend-icon="mdi-image"
    :variant="btnVariant"
    :color="btnColor"
    @click="dialog = true"
  >
    {{ btnText }}
    <v-dialog v-model="dialog">
      <v-card>
        <v-card-text>
          <v-file-input
            v-model="fileUpload"
            variant="outlined"
            :loading="uploading"
            prepend-icon=""
            label="Select Image"
          />
        </v-card-text>
        <v-card-actions>
          <v-btn :disabled="loading" @click="dialog = false">Cancel</v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="flat"
            :loading="loading"
            prepend-icon="mdi-floppy"
            @click="saveImage"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>
</template>

<style scoped></style>
