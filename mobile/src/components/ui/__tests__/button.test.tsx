import { fireEvent, render, screen } from "@testing-library/react-native";
import { Text } from "react-native";
import { Button } from "../button";

describe("Button", () => {
  it("renders string children wrapped in Text", async () => {
    await render(<Button>Save recipe</Button>);
    expect(screen.getByText("Save recipe")).toBeOnTheScreen();
  });

  it("renders mixed element and string children", async () => {
    await render(
      <Button>
        <Text>icon</Text>
        Label
      </Button>
    );
    expect(screen.getByText("icon")).toBeOnTheScreen();
    expect(screen.getByText("Label")).toBeOnTheScreen();
  });

  it("fires onPress", async () => {
    const onPress = jest.fn();
    await render(<Button onPress={onPress}>Tap</Button>);
    await fireEvent.press(screen.getByText("Tap"));
    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it("does not fire onPress when disabled", async () => {
    const onPress = jest.fn();
    await render(
      <Button disabled onPress={onPress}>
        Nope
      </Button>
    );
    await fireEvent.press(screen.getByText("Nope"));
    expect(onPress).not.toHaveBeenCalled();
  });
});
