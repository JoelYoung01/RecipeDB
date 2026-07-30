import { toast, useToastStore } from "../toast";

beforeEach(() => {
  jest.useFakeTimers();
  useToastStore.getState().clear();
});

afterEach(() => {
  jest.useRealTimers();
});

describe("toast store", () => {
  it("pushes toasts with variants", () => {
    toast.success("Saved.");
    toast.error("Broke.");
    const toasts = useToastStore.getState().toasts;
    expect(toasts).toHaveLength(2);
    expect(toasts[0]).toMatchObject({ message: "Saved.", variant: "success" });
    expect(toasts[1]).toMatchObject({ message: "Broke.", variant: "error" });
  });

  it("caps the stack at 3 toasts", () => {
    for (let i = 0; i < 5; i++) toast.info(`toast ${i}`);
    const toasts = useToastStore.getState().toasts;
    expect(toasts).toHaveLength(3);
    expect(toasts.map((t) => t.message)).toEqual(["toast 2", "toast 3", "toast 4"]);
  });

  it("auto-dismisses after the duration", () => {
    useToastStore.getState().push({ message: "temp", duration: 1000 });
    expect(useToastStore.getState().toasts).toHaveLength(1);
    jest.advanceTimersByTime(1100);
    expect(useToastStore.getState().toasts).toHaveLength(0);
  });

  it("dismisses a specific toast by id", () => {
    const id = toast.info("hello");
    toast.info("world");
    useToastStore.getState().dismiss(id);
    const toasts = useToastStore.getState().toasts;
    expect(toasts).toHaveLength(1);
    expect(toasts[0]!.message).toBe("world");
  });

  it("fromError extracts API error messages", () => {
    toast.fromError({ userMessage: "Recipe not found." });
    expect(useToastStore.getState().toasts[0]).toMatchObject({
      message: "Recipe not found.",
      variant: "error"
    });
  });
});
