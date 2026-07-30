import * as LocalAuthentication from "expo-local-authentication";
import { Platform } from "react-native";

export interface BiometricSupport {
  /** Hardware present AND biometrics enrolled. */
  available: boolean;
  /** User-facing name of the strongest supported method. */
  label: "Face ID" | "Touch ID" | "Biometrics";
}

export async function getBiometricSupport(): Promise<BiometricSupport> {
  if (Platform.OS === "web") return { available: false, label: "Face ID" };
  try {
    const [hasHardware, enrolled, types] = await Promise.all([
      LocalAuthentication.hasHardwareAsync(),
      LocalAuthentication.isEnrolledAsync(),
      LocalAuthentication.supportedAuthenticationTypesAsync()
    ]);
    const label = types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)
      ? "Face ID"
      : types.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)
        ? "Touch ID"
        : "Biometrics";
    return { available: hasHardware && enrolled, label };
  } catch {
    return { available: false, label: "Face ID" };
  }
}

/** Prompt Face ID / Touch ID (with device-passcode fallback). */
export async function authenticateBiometric(promptMessage: string): Promise<boolean> {
  const result = await LocalAuthentication.authenticateAsync({ promptMessage });
  return result.success;
}
