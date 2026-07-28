<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import type { ButtonVariants } from ".";
import { cn } from "@/lib/utils";
import { buttonVariants } from ".";

interface Props {
  variant?: ButtonVariants["variant"];
  size?: ButtonVariants["size"];
  class?: HTMLAttributes["class"];
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: "button"
});
</script>

<template>
  <button
    data-slot="button"
    :data-variant="variant"
    :data-size="size"
    :type="type"
    :disabled="disabled"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <slot />
  </button>
</template>
