<script setup lang="ts">
import { cn } from "@/lib/utils";
import { tabByRouteName, tabs, type SiteRouteName, type TabId } from "@/sitemap";
import { BookOpen, CalendarDays, Home, List, Plus } from "@lucide/vue";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const open = defineModel<boolean>("open", { default: false });

const route = useRoute();
const router = useRouter();

const activeTab = computed<TabId | undefined>(() => {
  if (open.value) return "add";
  return tabByRouteName[route.name as SiteRouteName];
});

const icons: Record<TabId, typeof Home> = {
  home: Home,
  recipes: BookOpen,
  add: Plus,
  planner: CalendarDays,
  list: List
};

function onTab(id: TabId) {
  if (id === "add") {
    open.value = !open.value;
    return;
  }
  open.value = false;
  const tab = tabs.find((t) => t.id === id);
  if (tab?.path) router.push(tab.path);
}
</script>

<template>
  <nav
    class="fixed bottom-0 left-1/2 z-[60] w-full max-w-md -translate-x-1/2 border-t border-border bg-elevated px-2 pt-2 pb-[calc(0.75rem+env(safe-area-inset-bottom))]"
    aria-label="Primary"
  >
    <div class="grid grid-cols-5 items-end">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="flex flex-col items-center gap-0.5 outline-none"
        :class="tab.id === 'add' ? '' : 'py-0.5'"
        :aria-current="activeTab === tab.id ? 'page' : undefined"
        @click="onTab(tab.id)"
      >
        <template v-if="tab.id === 'add'">
          <span
            class="flex size-[50px] -mt-7 items-center justify-center rounded-full border-4 border-background bg-primary text-primary-foreground shadow-[0_4px_12px_rgba(22,163,74,0.4)] transition-transform duration-200"
            :class="open ? 'rotate-45' : ''"
          >
            <Plus class="size-[22px]" :stroke-width="2.5" />
          </span>
          <span class="mt-0.5 text-[10px] font-medium text-muted-foreground">
            {{ open ? "Close" : tab.label }}
          </span>
        </template>
        <template v-else>
          <component
            :is="icons[tab.id]"
            class="size-[21px] transition-colors"
            :class="activeTab === tab.id ? 'text-[#22c55e]' : 'text-muted-foreground'"
            :stroke-width="2"
          />
          <span
            :class="
              cn(
                'text-[10px] transition-colors',
                activeTab === tab.id
                  ? 'font-semibold text-[#22c55e]'
                  : 'font-medium text-muted-foreground'
              )
            "
          >
            {{ tab.label }}
          </span>
        </template>
      </button>
    </div>
  </nav>
</template>
