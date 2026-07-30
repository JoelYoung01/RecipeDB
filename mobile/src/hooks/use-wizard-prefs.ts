import { emptyWizardPrefs, type MealPlanWizardPrefs } from "@/types";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "julep.meal-plan-wizard-prefs.v1";

/** Wizard preferences persisted on-device across sessions. */
export function useWizardPrefs() {
  const [prefs, setPrefs] = useState<MealPlanWizardPrefs>(emptyWizardPrefs());
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    AsyncStorage.getItem(STORAGE_KEY)
      .then((raw) => {
        if (cancelled || !raw) return;
        try {
          setPrefs({ ...emptyWizardPrefs(), ...(JSON.parse(raw) as Partial<MealPlanWizardPrefs>) });
        } catch {
          /* corrupted — start fresh */
        }
      })
      .finally(() => {
        if (!cancelled) setLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const savePrefs = useCallback((next: MealPlanWizardPrefs) => {
    setPrefs(next);
    void AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, []);

  return { prefs, savePrefs, loaded };
}
