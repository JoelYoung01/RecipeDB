import { fireEvent, render, screen } from "@testing-library/react-native";
import { Text } from "react-native";
import { SwipeRow } from "../SwipeRow";

async function setup() {
  const onDismiss = jest.fn();
  const onDelete = jest.fn();
  const onView = jest.fn();
  await render(
    <SwipeRow onDismiss={onDismiss} onDelete={onDelete} onView={onView}>
      <Text>2 lbs chicken thighs</Text>
    </SwipeRow>
  );
  return { onDismiss, onDelete, onView };
}

describe("SwipeRow", () => {
  it("renders its row content", async () => {
    await setup();
    expect(screen.getByText("2 lbs chicken thighs")).toBeOnTheScreen();
    expect(screen.getByText("Dismiss")).toBeOnTheScreen();
  });

  it("fires onView from the action tray", async () => {
    const { onView, onDelete } = await setup();
    await fireEvent.press(screen.getByLabelText("View recipe"));
    expect(onView).toHaveBeenCalledTimes(1);
    expect(onDelete).not.toHaveBeenCalled();
  });

  it("fires onDelete from the action tray", async () => {
    const { onDelete, onDismiss } = await setup();
    await fireEvent.press(screen.getByLabelText("Remove from list"));
    expect(onDelete).toHaveBeenCalledTimes(1);
    expect(onDismiss).not.toHaveBeenCalled();
  });
});
