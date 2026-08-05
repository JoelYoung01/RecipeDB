import AsyncStorage from "@react-native-async-storage/async-storage";
import { getIntentCounts, trackIntent } from "../intent";

const mockMemory = new Map<string, string>();

jest.mock("@react-native-async-storage/async-storage", () => ({
  getItem: jest.fn((key: string) => Promise.resolve(mockMemory.get(key) ?? null)),
  setItem: jest.fn((key: string, value: string) => {
    mockMemory.set(key, value);
    return Promise.resolve();
  }),
  clear: jest.fn(() => {
    mockMemory.clear();
    return Promise.resolve();
  })
}));

describe("trackIntent", () => {
  beforeEach(async () => {
    mockMemory.clear();
    jest.clearAllMocks();
    await AsyncStorage.clear();
  });

  it("increments and persists planner.plan_week_fab", async () => {
    await trackIntent("planner.plan_week_fab", { weekStart: "2026-08-03" });
    await trackIntent("planner.plan_week_fab", { weekStart: "2026-08-03" });

    const counts = await getIntentCounts();
    expect(counts["planner.plan_week_fab"]?.count).toBe(2);
    expect(counts["planner.plan_week_fab"]?.lastAt).toMatch(/^\d{4}-\d{2}-\d{2}T/);
  });
});
