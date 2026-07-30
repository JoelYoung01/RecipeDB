import { getErrorMessage, parseApiErrorBody } from "../errors";

const FALLBACK = "Something went wrong. Please try again.";

describe("parseApiErrorBody", () => {
  it("uses a plain string detail", () => {
    expect(parseApiErrorBody({ detail: "Incorrect email or password" }).userMessage).toBe(
      "Incorrect email or password"
    );
  });

  it("prefers user_message inside a structured detail", () => {
    const parsed = parseApiErrorBody({
      detail: {
        code: "email_not_verified",
        user_message: "Verify your email to continue.",
        message: "Email address is not verified"
      }
    });
    expect(parsed.userMessage).toBe("Verify your email to continue.");
  });

  it("joins FastAPI validation error arrays", () => {
    const parsed = parseApiErrorBody({
      detail: [{ msg: "field required" }, { msg: "value is not a valid integer" }]
    });
    expect(parsed.userMessage).toBe("field required; value is not a valid integer");
  });

  it("extracts top-level code", () => {
    expect(parseApiErrorBody({ code: "rate_limited", detail: "Slow down" }).code).toBe(
      "rate_limited"
    );
  });

  it("falls back for unknown shapes", () => {
    expect(parseApiErrorBody(null).userMessage).toBe(FALLBACK);
    expect(parseApiErrorBody("nope").userMessage).toBe(FALLBACK);
    expect(parseApiErrorBody({}).userMessage).toBe(FALLBACK);
  });
});

describe("getErrorMessage", () => {
  it("reads userMessage from ApiError-shaped objects", () => {
    expect(getErrorMessage({ userMessage: "No such recipe." })).toBe("No such recipe.");
  });

  it("strips (status) prefixes from Error messages", () => {
    expect(getErrorMessage(new Error("(404) Recipe not found"))).toBe("Recipe not found");
  });

  it("passes through plain strings", () => {
    expect(getErrorMessage("plain failure")).toBe("plain failure");
  });

  it("uses the fallback for anything else", () => {
    expect(getErrorMessage(undefined)).toBe(FALLBACK);
    expect(getErrorMessage(42, "custom fallback")).toBe("custom fallback");
  });
});
