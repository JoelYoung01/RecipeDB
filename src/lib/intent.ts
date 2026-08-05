/**
 * Named product intents we care about measuring (engagement / placement tests).
 * Mirrored in `mobile/src/lib/intent.ts`.
 */
export type IntentName = "planner.plan_week_fab";

export interface IntentStat {
  count: number;
  lastAt: string;
}

export type IntentProps = Record<string, string | number | boolean | null | undefined>;

const STORAGE_KEY = "souskit.intent-counts.v1";

type IntentStore = Partial<Record<IntentName, IntentStat>>;

function readStore(): IntentStore {
  try {
    const raw = globalThis.localStorage?.getItem(STORAGE_KEY);
    if (!raw) return {};
    return JSON.parse(raw) as IntentStore;
  } catch {
    return {};
  }
}

function writeStore(store: IntentStore): void {
  try {
    globalThis.localStorage?.setItem(STORAGE_KEY, JSON.stringify(store));
  } catch {
    /* private mode */
  }
}

/**
 * Record that the user triggered a product intent.
 * Persists a local counter so we can inspect engagement without a telemetry backend.
 */
export function trackIntent(name: IntentName, props?: IntentProps): void {
  const store = readStore();
  const prev = store[name];
  const next: IntentStat = {
    count: (prev?.count ?? 0) + 1,
    lastAt: new Date().toISOString()
  };
  store[name] = next;
  writeStore(store);

  if (import.meta.env.DEV) {
    console.info(`[intent] ${name}`, { ...props, count: next.count });
  }
}

/** Snapshot of persisted intent counters (for debugging / future dashboards). */
export function getIntentCounts(): IntentStore {
  return readStore();
}
