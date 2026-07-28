<script setup lang="ts">
import { googleAccountsLoadedKey } from "@/plugins/googleAuth";
import { inject, nextTick, useTemplateRef, watch } from "vue";

const loaded = inject(googleAccountsLoadedKey, ref(false));
const button = useTemplateRef<HTMLDivElement>("button");

function render() {
  if (!button.value) {
    throw new Error("No button found when attempting to render google login button.");
  }

  google.accounts.id.renderButton(button.value, {
    type: "standard",
    theme: "filled_black",
    size: "large",
    text: "signin_with",
    shape: "rectangular",
    width: 280
  });
}

watch(
  loaded,
  (newValue) => {
    if (newValue) {
      nextTick(render);
    }
  },
  { immediate: true }
);
</script>

<template>
  <div ref="button" class="flex justify-center"></div>
</template>
