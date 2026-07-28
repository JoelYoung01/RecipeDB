import { inject, provide, type InjectionKey, type Ref } from "vue";

const addMenuOpenKey: InjectionKey<Ref<boolean>> = Symbol("addMenuOpen");

export function provideAddMenu() {
  const open = ref(false);
  provide(addMenuOpenKey, open);
  return open;
}

export function useAddMenu() {
  const open = inject(addMenuOpenKey, null);
  if (!open) {
    throw new Error("useAddMenu() must be used within AppShell");
  }
  return open;
}
