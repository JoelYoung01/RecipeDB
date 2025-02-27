<script setup lang="ts">
import type { UploadSlim } from "@/types";
import { del, get, postFile } from "@/utils";
import { useTemplateRef } from "vue";

interface Props {
  maxSizeMb?: number;
}

const model = defineModel<number>();
const props = withDefaults(defineProps<Props>(), { maxSizeMb: 5 });
const inputRef = useTemplateRef("fileInput");

const loading = ref(false);
const uploading = ref(false);
const deleting = ref(false);
const dialog = ref(false);
const errorMsg = ref<string>("");
const fileUpload = ref();
const fileDetail = ref<UploadSlim>();
const btnText = computed(() => (model.value ? "Change Image" : "Upload Image"));
const btnVariant = computed(() => (model.value ? "flat" : "outlined"));
const btnColor = computed(() => (model.value ? "primary" : undefined));
const imageUrl = computed(() =>
  import.meta.env.DEV ? `http://localhost:8000${fileDetail.value?.url}` : fileDetail.value?.url
);

// TODO: update this component so that the following flows work:
// mounted => fetch existing detail if exists => preview

// upload image => immediately uploaded => previewed => on 'save', emit id

function triggerFileInput() {
  inputRef.value?.click();
}

function handleFileUpload(evt: any) {
  processFile(evt.target.files[0]);
}

async function processFile(file: any) {
  errorMsg.value = "";

  // Check file size
  const fileSizeMB = file.size / (1024 * 1024);
  if (fileSizeMB > props.maxSizeMb) {
    errorMsg.value = `Image size exceeds ${props.maxSizeMb}MB limit`;
    return;
  }

  // Clear existing file if necessary
  clearFile();

  fileUpload.value = file;
}

async function clearFile() {
  if (!model.value) return;
  deleting.value = true;
  await del(`/upload/${model.value}/`);
  model.value = undefined;
  deleting.value = false;
}

watch(fileUpload, async (val) => {
  if (!val) return;

  uploading.value = true;
  try {
    const payload = new FormData();
    payload.append("file", val);
    fileDetail.value = await postFile<UploadSlim>(`upload/`, payload);
    model.value = fileDetail.value.id;
  } catch (er) {
    console.error(er);
    errorMsg.value = `${er}`;
  }
  uploading.value = false;
});

watch(
  model,
  async (val) => {
    if (!val) {
      fileDetail.value = undefined;
      if (inputRef.value) {
        inputRef.value.value = "";
      }
      return;
    }

    loading.value = true;
    try {
      fileDetail.value = await get(`/upload/${val}/`);
    } catch (er) {
      console.error(er);
      errorMsg.value = `${er}`;
    }
    loading.value = false;
  },
  { immediate: true }
);
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
        <div class="upload-area" @click="triggerFileInput">
          <v-img v-if="fileDetail" :src="imageUrl" cover height="250" class="rounded">
            <template #placeholder>
              <v-row class="fill-height ma-0" align="center" justify="center">
                <v-progress-circular indeterminate color="primary" />
              </v-row>
            </template>
          </v-img>

          <v-container v-else class="d-flex flex-column align-center justify-center py-8">
            <v-icon
              icon="mdi-cloud-upload-outline"
              size="large"
              color="primary"
              class="mb-2"
            ></v-icon>
            <div class="text-center">
              <div class="text-h6">Upload recipe photo</div>
              <div class="text-subtitle-2 text-medium-emphasis">Tap to browse</div>
              <div class="text-caption mt-2">
                <v-chip size="x-small" class="text-caption">JPG</v-chip>
                <v-chip size="x-small" class="text-caption mx-1">PNG</v-chip>
                <v-chip size="x-small" class="text-caption">WEBP</v-chip>
              </div>
            </div>
          </v-container>
        </div>

        <v-alert v-if="errorMsg" type="error" class="mx-2">{{ errorMsg }}</v-alert>

        <input
          ref="fileInput"
          type="file"
          class="d-none"
          accept="image/*"
          @change="handleFileUpload"
        />

        <v-card-actions>
          <v-btn
            v-if="model"
            variant="outlined"
            color="danger"
            prepend-icon="mdi-delete"
            :loading="deleting"
            @click="clearFile"
          >
            Clear Image
          </v-btn>
          <v-spacer />
          <v-btn
            color="primary"
            variant="flat"
            :disabled="deleting || uploading"
            @click="dialog = false"
          >
            Done
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-card class="recipe-image-uploader" variant="outlined"> </v-card>
    </v-dialog>
  </v-btn>
</template>

<style scoped></style>
