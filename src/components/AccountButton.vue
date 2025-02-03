<script setup lang="ts">
import { useSessionStore } from "@/stores/session";
import GoogleLoginButton from "./GoogleLoginButton.vue";

const sessionStore = useSessionStore();

const dialogVisible = ref(false);
const title = computed(() => {
  if (sessionStore.currentUser) return "Account";
  else return "Sign In";
});

function logout() {
  sessionStore.logout();
  window.location.reload();
}
</script>

<template>
  <v-btn variant="text" icon>
    <v-avatar>
      <v-img alt="Profile Image" :src="sessionStore.currentUser?.avatar_url">
        <template #placeholder>
          <v-icon class="text-white h-100" icon="mdi-account" size="large" />
        </template>
      </v-img>
    </v-avatar>

    <v-dialog v-model="dialogVisible" activator="parent" max-width="300">
      <v-card>
        <v-card-title class="text-center">{{ title }}</v-card-title>
        <v-card-text v-if="sessionStore.currentUser">
          <div class="d-flex flex-column align-center">
            <v-avatar size="75" class="mb-2">
              <v-img alt="Profile Image" :src="sessionStore.currentUser.avatar_url">
                <template #placeholder>
                  <v-icon icon="mdi-account-circle" size="75" />
                </template>
              </v-img>
            </v-avatar>
            {{ sessionStore.currentUser.display_name }}
            <v-btn color="primary" class="mt-4" @click="logout">Sign Out</v-btn>
          </div>
        </v-card-text>
        <v-card-text v-else>
          <div class="d-flex justify-center">
            <GoogleLoginButton />
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-btn>
</template>

<style scoped></style>
