<script setup lang="ts">
import defaultUser from "@/assets/account-circle.svg";
import { useSessionStore } from "@/stores/session";
import { ref, computed } from "vue";
import { put } from "@/utils/api";
import { useRouter } from "vue-router";

const router = useRouter();
const sessionStore = useSessionStore();
const editingDisplayName = ref(false);
const newDisplayName = ref(sessionStore.currentUser?.display_name || "");
const loading = ref(false);

const lastLoginDate = computed(() => {
  if (!sessionStore.currentUser?.last_login) return "Never";
  return new Date(sessionStore.currentUser.last_login).toLocaleString();
});

function logOut() {
  sessionStore.logout();
  router.push("/login");
}

async function updateDisplayName() {
  if (!sessionStore.currentUser) return;
  loading.value = true;
  try {
    await put(`/user/${sessionStore.currentUser.id}`, {
      display_name: newDisplayName.value
    });
    if (sessionStore.currentUser) {
      sessionStore.currentUser.display_name = newDisplayName.value;
    }
    editingDisplayName.value = false;
  } catch (error) {
    console.error("Failed to update display name:", error);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <v-container>
    <h1 class="text-center text-h5 font-weight-bold">My Account</h1>

    <div class="mb-6">
      <div class="d-flex justify-center profile-image-container">
        <v-img
          :src="sessionStore.currentUser?.avatar_url"
          alt="User Avatar"
          aspect-ratio="1"
          cover
          round
        >
          <template #placeholder>
            <v-img :src="defaultUser" />
          </template>
        </v-img>
      </div>

      <v-list width="100%">
        <v-list-item>
          <template #prepend>
            <v-icon icon="mdi-account" size="x-large" />
          </template>
          <v-list-item-title>Display Name</v-list-item-title>
          <v-list-item-subtitle>
            <div v-if="!editingDisplayName" class="d-flex align-center">
              {{ sessionStore.currentUser?.display_name }}
              <v-btn
                icon="mdi-pencil"
                variant="text"
                size="small"
                class="ms-2"
                @click="editingDisplayName = true"
              />
            </div>
            <div v-else class="d-flex align-center">
              <v-text-field
                v-model="newDisplayName"
                variant="outlined"
                density="compact"
                hide-details
                class="me-2"
                :loading="loading"
              />
              <v-btn
                icon="mdi-check"
                variant="text"
                size="small"
                color="success"
                :loading="loading"
                @click="updateDisplayName"
              />
              <v-btn
                icon="mdi-close"
                variant="text"
                size="small"
                color="error"
                :disabled="loading"
                @click="editingDisplayName = false"
              />
            </div>
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <template #prepend>
            <v-icon icon="mdi-at" size="x-large" />
          </template>
          <v-list-item-title>Username</v-list-item-title>
          <v-list-item-subtitle>{{ sessionStore.currentUser?.username }}</v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <template #prepend>
            <v-icon icon="mdi-email" size="x-large" />
          </template>
          <v-list-item-title>Email</v-list-item-title>
          <v-list-item-subtitle>{{ sessionStore.currentUser?.email }}</v-list-item-subtitle>
        </v-list-item>

        <v-list-item>
          <template #prepend>
            <v-icon icon="mdi-clock" size="x-large" />
          </template>
          <v-list-item-title>Last Login</v-list-item-title>
          <v-list-item-subtitle>{{ lastLoginDate }}</v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </div>

    <div class="d-flex justify-center">
      <v-btn color="primary" @click="logOut()">Log Out</v-btn>
    </div>
  </v-container>
</template>

<style scoped>
section {
  margin-bottom: 2rem;
}

.profile-image-container > * {
  flex: 30% 0 0;
}
</style>
