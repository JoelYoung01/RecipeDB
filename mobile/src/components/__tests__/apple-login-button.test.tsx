import { loginWithApple } from "@/api/auth";
import { useSessionStore } from "@/stores/session";
import { act, render, waitFor } from "@testing-library/react-native";
import * as AppleAuthentication from "expo-apple-authentication";
import { AppleLoginButton } from "../AppleLoginButton";

/**
 * NativeWind's babel transform rewrites createElement calls to its interop
 * runtime, which jest.mock factories cannot reference. The mocked Apple
 * button therefore renders nothing and instead records its props here
 * (`mock` prefix keeps babel-plugin-jest-hoist happy).
 */
const mockAppleButton: { rendered: boolean; onPress?: () => void } = { rendered: false };

jest.mock("expo-apple-authentication", () => ({
  isAvailableAsync: jest.fn(),
  signInAsync: jest.fn(),
  AppleAuthenticationButton: (props: { onPress: () => void }) => {
    mockAppleButton.rendered = true;
    mockAppleButton.onPress = props.onPress;
    return null;
  },
  AppleAuthenticationButtonType: { SIGN_IN: 0 },
  AppleAuthenticationButtonStyle: { WHITE: 1 },
  AppleAuthenticationScope: { FULL_NAME: 0, EMAIL: 1 }
}));

jest.mock("@/api/auth", () => ({
  loginWithApple: jest.fn()
}));

const mockedAvailable = AppleAuthentication.isAvailableAsync as jest.MockedFunction<
  typeof AppleAuthentication.isAvailableAsync
>;
const mockedSignIn = AppleAuthentication.signInAsync as jest.MockedFunction<
  typeof AppleAuthentication.signInAsync
>;
const mockedLogin = loginWithApple as jest.MockedFunction<typeof loginWithApple>;

const user = {
  id: 1,
  username: "joel",
  email: "joel@example.com",
  display_name: "Joel",
  admin: false,
  disabled: false,
  email_verified: true
};

beforeEach(() => {
  jest.clearAllMocks();
  mockAppleButton.rendered = false;
  mockAppleButton.onPress = undefined;
});

async function pressAppleButton() {
  await waitFor(() => expect(mockAppleButton.rendered).toBe(true));
  await act(async () => {
    mockAppleButton.onPress?.();
  });
}

describe("AppleLoginButton", () => {
  it("renders nothing when Sign in with Apple is unavailable", async () => {
    mockedAvailable.mockResolvedValue(false);
    await render(<AppleLoginButton onPendingChange={jest.fn()} onError={jest.fn()} />);
    await waitFor(() => expect(mockedAvailable).toHaveBeenCalled());
    expect(mockAppleButton.rendered).toBe(false);
  });

  it("exchanges the identity token and stores the session", async () => {
    mockedAvailable.mockResolvedValue(true);
    mockedSignIn.mockResolvedValue({
      identityToken: "apple-jwt",
      fullName: { givenName: "Joel", familyName: "Young" }
    } as never);
    mockedLogin.mockResolvedValue({ access_token: "session-token", user });
    const setSession = jest.fn().mockResolvedValue(undefined);
    useSessionStore.setState({ setSession } as never);

    const onError = jest.fn();
    await render(<AppleLoginButton onPendingChange={jest.fn()} onError={onError} />);
    await pressAppleButton();

    await waitFor(() =>
      expect(mockedLogin).toHaveBeenCalledWith({
        identity_token: "apple-jwt",
        full_name: "Joel Young"
      })
    );
    await waitFor(() => expect(setSession).toHaveBeenCalledWith("session-token", user));
    expect(onError).not.toHaveBeenCalled();
  });

  it("swallows user cancellation without surfacing an error", async () => {
    mockedAvailable.mockResolvedValue(true);
    mockedSignIn.mockRejectedValue(
      Object.assign(new Error("canceled"), { code: "ERR_REQUEST_CANCELED" })
    );

    const onError = jest.fn();
    const onPendingChange = jest.fn();
    await render(<AppleLoginButton onPendingChange={onPendingChange} onError={onError} />);
    await pressAppleButton();

    await waitFor(() => expect(onPendingChange).toHaveBeenLastCalledWith(false));
    expect(onError).not.toHaveBeenCalled();
    expect(mockedLogin).not.toHaveBeenCalled();
  });
});
