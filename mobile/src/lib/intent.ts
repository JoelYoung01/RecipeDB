import AsyncStorage from "@react-native-async-storage/async-storage";

/**
 * Named product intents we care about measuring (engagement / placement tests).
 * Add new names here as CTAs move or experiments ship.
 */
export type IntentName = "planner.plan_week_fab";

export interface IntentStat {
  count: number;
  lastAt: string;
}

export type IntentProps = Record<string, string | number | boolean | null | undefined>;

const STORAGE_KEY = "souskit.intent-counts.v1";

type IntentStore = Partial<Record<IntentName, IntentStat>>;

async function readStore(): Promise<IntentStore> {
  try {
    const raw = await AsyncStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as IntentStore;
  } catch {
    return {};
  }
}

async function writeStore(store: IntentStore): Promise<void> {
  try {
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch {
    /* storage full / private mode */
  }
}

/**
 * Record that the user triggered a product intent.
 * Persists a local counter so we can inspect engagement without a telemetry backend.
 */
export async function trackIntent(name: IntentName, props?: IntentProps): Promise<void> {
  const store = await readStore();
  const prev = store[name];
  const next: IntentStat = {
    count: (prev?.count ?? 0) + 1,
    lastAt: new Date().toISOString()
  };
  store[name] = next;
  await writeStore(store);

  if (__DEV__) {
    // eslint-disable-next-line no-console
    console.info(`[intent] ${name}`, { ...props, count: next.count });
  }
}

/** Snapshot of persisted intent counters (for debugging / future dashboards). */
export async function getIntentCounts(): Promise<IntentStore> {
  return readStore();
}
