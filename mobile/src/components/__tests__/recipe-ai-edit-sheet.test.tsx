import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import { RecipeAiEditSheet } from "@/components/RecipeAiEditSheet";

const aiEditRecipe = jest.fn();
const syncAfterRecipeMutation = jest.fn();
const toastSuccess = jest.fn();
const toastFromError = jest.fn();

jest.mock("@/api/recipes", () => ({
  aiEditRecipe: (...args: unknown[]) => aiEditRecipe(...args)
}));

jest.mock("@/hooks/sync", () => ({
  syncAfterRecipeMutation: () => syncAfterRecipeMutation()
}));

jest.mock("@/stores/toast", () => ({
  toast: {
    success: (...args: unknown[]) => toastSuccess(...args),
    fromError: (...args: unknown[]) => toastFromError(...args)
  }
}));

jest.mock("@/components/ui/sheet", () => {
  const React = require("react");
  const { View } = require("react-native");
  return {
    Sheet: ({
      visible,
      children
    }: {
      visible: boolean;
      onClose: () => void;
      children: React.ReactNode;
    }) => (visible ? <View testID="sheet">{children}</View> : null)
  };
});

describe("RecipeAiEditSheet", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("submits the instruction and closes on success", async () => {
    aiEditRecipe.mockResolvedValue({ id: 7, name: "Edited" });
    const onClose = jest.fn();

    await render(
      <RecipeAiEditSheet visible recipeId={7} onClose={onClose} />
    );

    const input = screen.getByPlaceholderText(
      "e.g. Make it dairy-free and cut prep time in half"
    );
    await fireEvent.changeText(input, "Make it spicy");
    await fireEvent.press(screen.getByText("Apply edit"));

    await waitFor(() => {
      expect(aiEditRecipe).toHaveBeenCalledWith(7, "Make it spicy");
      expect(syncAfterRecipeMutation).toHaveBeenCalled();
      expect(toastSuccess).toHaveBeenCalled();
      expect(onClose).toHaveBeenCalled();
    });
  });

  it("surfaces API errors without closing", async () => {
    aiEditRecipe.mockRejectedValue(new Error("nope"));
    const onClose = jest.fn();

    await render(
      <RecipeAiEditSheet visible recipeId={3} onClose={onClose} />
    );

    await fireEvent.changeText(
      screen.getByPlaceholderText("e.g. Make it dairy-free and cut prep time in half"),
      "Double the servings"
    );
    await fireEvent.press(screen.getByText("Apply edit"));

    await waitFor(() => {
      expect(toastFromError).toHaveBeenCalled();
      expect(onClose).not.toHaveBeenCalled();
    });
  });
});
