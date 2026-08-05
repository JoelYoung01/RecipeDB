<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSessionStore } from "@/stores/session";
import type { Household, PendingHouseholdInvite } from "@/types";
import {
  acceptHouseholdInvite,
  fetchHousehold,
  fetchPendingHouseholdInvites,
  inviteToHousehold,
  leaveHousehold,
  removeHouseholdMember,
  renameHousehold,
  revokeHouseholdInvite
} from "@/utils/household";
import { toast } from "@/utils/toast";
import { Users } from "@lucide/vue";
import { computed, onMounted, ref } from "vue";

const sessionStore = useSessionStore();
const household = ref<Household | null>(null);
const pendingInvites = ref<PendingHouseholdInvite[]>([]);
const loading = ref(true);
const inviteEmail = ref("");
const nameDraft = ref("");
const editingName = ref(false);
const busy = ref(false);
const lastInviteToken = ref<string | null>(null);
const inviteCode = ref("");

const isOwner = computed(() => household.value?.my_role === "owner");
const shared = computed(() => (household.value?.member_count ?? 0) > 1);

async function load() {
  loading.value = true;
  try {
    const [hh, pending] = await Promise.all([fetchHousehold(), fetchPendingHouseholdInvites()]);
    household.value = hh;
    pendingInvites.value = pending;
  } catch (error) {
    toast.fromError(error, "Couldn’t load household.");
  } finally {
    loading.value = false;
  }
}

async function onInvite() {
  const email = inviteEmail.value.trim().toLowerCase();
  if (!email || busy.value) return;
  busy.value = true;
  try {
    const invite = await inviteToHousehold(email);
    inviteEmail.value = "";
    lastInviteToken.value = invite.token ?? null;
    await load();
    toast.success(`Invite ready for ${email}.`);
  } catch (error) {
    toast.fromError(error, "Couldn’t create that invite.");
  } finally {
    busy.value = false;
  }
}

async function onRename() {
  const name = nameDraft.value.trim();
  if (!name || busy.value) return;
  busy.value = true;
  try {
    household.value = await renameHousehold(name);
    editingName.value = false;
    toast.success("Household renamed.");
  } catch (error) {
    toast.fromError(error, "Couldn’t rename household.");
  } finally {
    busy.value = false;
  }
}

async function onLeave() {
  if (!shared.value) return;
  if (
    !confirm("Leave this household? Shared recipes, plans, and the grocery list stay with them.")
  ) {
    return;
  }
  busy.value = true;
  try {
    household.value = await leaveHousehold();
    toast.success("You left the household.");
  } catch (error) {
    toast.fromError(error, "Couldn’t leave the household.");
  } finally {
    busy.value = false;
  }
}

async function onRemove(userId: number) {
  if (!confirm("Remove this member from the household?")) return;
  busy.value = true;
  try {
    await removeHouseholdMember(userId);
    await load();
    toast.success("Member removed.");
  } catch (error) {
    toast.fromError(error, "Couldn’t remove that member.");
  } finally {
    busy.value = false;
  }
}

async function onAccept(token: string) {
  busy.value = true;
  try {
    household.value = await acceptHouseholdInvite(token);
    pendingInvites.value = await fetchPendingHouseholdInvites();
    toast.success("Joined household. Recipes and plans are shared now.");
  } catch (error) {
    toast.fromError(error, "Couldn’t accept that invite.");
  } finally {
    busy.value = false;
  }
}

async function onRevoke(inviteId: number) {
  busy.value = true;
  try {
    await revokeHouseholdInvite(inviteId);
    await load();
  } catch (error) {
    toast.fromError(error, "Couldn’t revoke invite.");
  } finally {
    busy.value = false;
  }
}

async function copyToken(token: string) {
  try {
    await navigator.clipboard.writeText(token);
    toast.success("Invite code copied.");
  } catch {
    toast.fromError(new Error("Couldn’t copy invite code."));
  }
}

onMounted(load);
</script>

<template>
  <div class="mt-6 space-y-3">
    <div
      v-if="pendingInvites.length"
      class="space-y-3 rounded-xl border border-primary/40 bg-card p-4"
    >
      <p class="text-sm font-semibold text-primary">Household invites</p>
      <div v-for="invite in pendingInvites" :key="invite.id" class="space-y-2">
        <p class="text-sm">
          {{ invite.invited_by_name }} invited you to {{ invite.household_name }}
        </p>
        <Button size="sm" :disabled="busy" @click="onAccept(invite.token)"> Join household </Button>
      </div>
    </div>

    <div class="rounded-xl border border-border bg-card p-4">
      <div class="flex items-center gap-2 text-muted-foreground">
        <Users class="size-4" />
        <p class="text-xs uppercase tracking-wide">Household</p>
      </div>

      <div v-if="loading" class="mt-3 text-sm text-muted-foreground">Loading…</div>
      <template v-else-if="household">
        <div v-if="!editingName" class="mt-2 flex items-center justify-between gap-2">
          <p class="font-semibold">{{ household.name }}</p>
          <Button
            v-if="isOwner"
            size="sm"
            variant="ghost"
            @click="
              nameDraft = household!.name;
              editingName = true;
            "
          >
            Rename
          </Button>
        </div>
        <div v-else class="mt-2 flex gap-2">
          <Input v-model="nameDraft" class="h-9 rounded-lg bg-secondary" />
          <Button size="sm" :disabled="busy" @click="onRename">Save</Button>
          <Button size="sm" variant="outline" @click="editingName = false">Cancel</Button>
        </div>

        <p class="mt-1 text-xs text-muted-foreground">
          {{ household.member_count }}/{{ household.max_members }} people · shared recipes, planner,
          and grocery list
        </p>

        <div class="mt-4 space-y-3">
          <div
            v-for="member in household.members"
            :key="member.user_id"
            class="flex items-center justify-between gap-2"
          >
            <div>
              <p class="text-sm font-semibold">
                {{ member.display_name
                }}{{ member.user_id === sessionStore.currentUser?.id ? " (you)" : "" }}
              </p>
              <p class="text-xs text-muted-foreground">{{ member.role }} · {{ member.email }}</p>
            </div>
            <Button
              v-if="isOwner && member.user_id !== sessionStore.currentUser?.id"
              size="sm"
              variant="outline"
              :disabled="busy"
              @click="onRemove(member.user_id)"
            >
              Remove
            </Button>
          </div>
        </div>

        <div v-if="isOwner" class="mt-5 space-y-2 border-t border-border pt-4">
          <p class="text-xs text-muted-foreground">Invite by email</p>
          <div class="flex gap-2">
            <Input
              v-model="inviteEmail"
              type="email"
              placeholder="partner@example.com"
              class="h-9 rounded-lg bg-secondary"
            />
            <Button size="sm" :disabled="busy" @click="onInvite">Invite</Button>
          </div>
          <button
            v-if="lastInviteToken"
            type="button"
            class="text-left text-xs text-primary"
            @click="copyToken(lastInviteToken)"
          >
            Invite code ready — tap to copy
          </button>

          <div v-if="household.pending_invites.length" class="mt-2 space-y-2">
            <p class="text-xs text-muted-foreground">Pending invites</p>
            <div
              v-for="invite in household.pending_invites"
              :key="invite.id"
              class="flex items-center justify-between gap-2"
            >
              <p class="text-sm">{{ invite.email }}</p>
              <div class="flex gap-1">
                <Button
                  v-if="invite.token"
                  size="sm"
                  variant="outline"
                  @click="copyToken(invite.token!)"
                >
                  Copy
                </Button>
                <Button size="sm" variant="ghost" :disabled="busy" @click="onRevoke(invite.id)">
                  Revoke
                </Button>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-5 space-y-2 border-t border-border pt-4">
          <p class="text-xs text-muted-foreground">Have an invite code?</p>
          <div class="flex gap-2">
            <Input
              v-model="inviteCode"
              placeholder="Paste invite code"
              class="h-9 rounded-lg bg-secondary"
            />
            <Button
              size="sm"
              :disabled="busy || !inviteCode.trim()"
              @click="
                onAccept(inviteCode.trim()).then(() => {
                  inviteCode = '';
                })
              "
            >
              Join
            </Button>
          </div>
        </div>

        <Button
          v-if="shared"
          variant="outline"
          class="mt-5 w-full"
          :disabled="busy"
          @click="onLeave"
        >
          Leave household
        </Button>
      </template>
    </div>
  </div>
</template>
