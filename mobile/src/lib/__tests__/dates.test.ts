import {
  addDays,
  endOfDay,
  formatPrepTime,
  parseDateKey,
  startOfDay,
  startOfWeekMonday,
  toDateKey
} from "../dates";

describe("startOfWeekMonday", () => {
  it("returns Monday for a mid-week date", () => {
    // 2026-07-30 is a Thursday → week starts Monday 2026-07-27
    expect(toDateKey(startOfWeekMonday(new Date(2026, 6, 30)))).toBe("2026-07-27");
  });

  it("returns the previous Monday for a Sunday", () => {
    // 2026-08-02 is a Sunday → week starts Monday 2026-07-27
    expect(toDateKey(startOfWeekMonday(new Date(2026, 7, 2)))).toBe("2026-07-27");
  });

  it("returns the same day for a Monday", () => {
    expect(toDateKey(startOfWeekMonday(new Date(2026, 6, 27)))).toBe("2026-07-27");
  });
});

describe("toDateKey / parseDateKey", () => {
  it("round-trips a local date", () => {
    const date = startOfDay(new Date(2026, 0, 5));
    expect(parseDateKey(toDateKey(date))?.getTime()).toBe(date.getTime());
  });

  it("pads months and days", () => {
    expect(toDateKey(new Date(2026, 2, 4))).toBe("2026-03-04");
  });

  it("rejects malformed keys", () => {
    expect(parseDateKey("2026-3-4")).toBeNull();
    expect(parseDateKey("not-a-date")).toBeNull();
    expect(parseDateKey("")).toBeNull();
  });
});

describe("addDays / startOfDay / endOfDay", () => {
  it("adds days across month boundaries", () => {
    expect(toDateKey(addDays(new Date(2026, 0, 31), 1))).toBe("2026-02-01");
  });

  it("startOfDay zeroes the time", () => {
    const d = startOfDay(new Date(2026, 5, 15, 13, 45, 30));
    expect([d.getHours(), d.getMinutes(), d.getSeconds()]).toEqual([0, 0, 0]);
  });

  it("endOfDay maxes the time", () => {
    const d = endOfDay(new Date(2026, 5, 15, 13, 45, 30));
    expect([d.getHours(), d.getMinutes(), d.getSeconds()]).toEqual([23, 59, 59]);
  });
});

describe("formatPrepTime", () => {
  it("formats minutes only", () => {
    expect(formatPrepTime(45)).toBe("45 min");
  });

  it("formats whole hours", () => {
    expect(formatPrepTime(120)).toBe("2h");
  });

  it("formats hours and minutes", () => {
    expect(formatPrepTime(95)).toBe("1h 35m");
  });

  it("returns empty for missing values", () => {
    expect(formatPrepTime(null)).toBe("");
    expect(formatPrepTime(undefined)).toBe("");
  });
});
