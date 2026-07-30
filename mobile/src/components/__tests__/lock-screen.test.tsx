import { authenticateBiometric, getBiometricSupport } from "@/lib/biometrics";
import { useAppLockStore } from "@/stores/app-lock";
import { render, screen, waitFor } from "@testing-library/react-native";
import { LockScreen } from "../LockScreen";

jest.mock("@/lib/biometrics", () => ({
  getBiometricSupport: jest.fn(),
  authenticateBiometric: jest.fn()
}));

jest.mock("expo-router", () => ({
  useRouter: () => ({ replace: jest.fn() })
}));

const mockedSupport = getBiometricSupport as jest.MockedFunction<typeof getBiometricSupport>;
const mockedAuth = authenticateBiometric as jest.MockedFunction<typeof authenticateBiometric>;

beforeEach(() => {
  jest.clearAllMocks();
  mockedSupport.mockResolvedValue({ available: true, label: "Face ID" });
  useAppLockStore.setState({ ready: true, enabled: true, locked: true });
});

describe("LockScreen", () => {
  it("auto-prompts on mount and unlocks on success", async () => {
    mockedAuth.mockResolvedValue(true);
    await render(<LockScreen />);
    await waitFor(() => expect(useAppLockStore.getState().locked).toBe(false));
    expect(mockedAuth).toHaveBeenCalledWith("Unlock Junket");
  });

  it("stays locked and offers a retry when biometrics fail", async () => {
    mockedAuth.mockResolvedValue(false);
    await render(<LockScreen />);
    await waitFor(() =>
      expect(screen.getByText("Couldn’t verify it’s you. Try again.")).toBeOnTheScreen()
    );
    expect(useAppLockStore.getState().locked).toBe(true);
    expect(screen.getByText("Unlock with Face ID")).toBeOnTheScreen();
    expect(screen.getByText("Sign out")).toBeOnTheScreen();
  });
});
