import AsyncStorage from "@react-native-async-storage/async-storage";
import { getIntentCounts, trackIntent } from "../intent";

jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock")
);

describe("trackIntent", () => {
  beforeEach(async () => {
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
