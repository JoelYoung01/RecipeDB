import { splitInstructionSteps } from "../instructions";

describe("splitInstructionSteps", () => {
  it("splits numbered steps on newlines and drops blanks", () => {
    expect(
      splitInstructionSteps("1. Rinse rice.\n\n2. Cook rice.\n3. Serve.")
    ).toEqual(["1. Rinse rice.", "2. Cook rice.", "3. Serve."]);
  });

  it("normalizes Windows newlines", () => {
    expect(splitInstructionSteps("1. Mix.\r\n2. Bake.")).toEqual(["1. Mix.", "2. Bake."]);
  });

  it("returns empty for blank input", () => {
    expect(splitInstructionSteps("   \n\n  ")).toEqual([]);
  });
});
