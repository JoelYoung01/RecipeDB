import { loginWithApple } from "@/api/auth";
import { getErrorMessage } from "@/api/errors";
import { useSessionStore } from "@/stores/session";
import * as AppleAuthentication from "expo-apple-authentication";
import { useEffect, useRef, useState } from "react";
import { Platform } from "react-native";

interface AppleLoginButtonProps {
  onPendingChange: (pending: boolean) => void;
  onError: (message: string) => void;
}

/**
 * Native Sign in with Apple. iOS only — renders Apple's branded button (an
 * App Store requirement) once `isAvailableAsync` confirms device support,
 * and exchanges the identity token for a Julep session.
 */
export function AppleLoginButton({ onPendingChange, onError }: AppleLoginButtonProps) {
  const [available, setAvailable] = useState(false);
  const signingIn = useRef(false);

  useEffect(() => {
    if (Platform.OS !== "ios") return;
    let cancelled = false;
    AppleAuthentication.isAvailableAsync()
      .then((ok) => {
        if (!cancelled) setAvailable(ok);
      })
      .catch(() => {
        if (!cancelled) setAvailable(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!available) return null;

  const signIn = async () => {
    if (signingIn.current) return;
    signingIn.current = true;
    onPendingChange(true);
    try {
      const credential = await AppleAuthentication.signInAsync({
        requestedScopes: [
          AppleAuthentication.AppleAuthenticationScope.FULL_NAME,
          AppleAuthentication.AppleAuthenticationScope.EMAIL
        ]
      });
      if (!credential.identityToken) {
        onPendingChange(false);
        onError("Apple sign-in did not return a credential.");
        return;
      }
      // Apple shares the name only on the FIRST authorization; forward it so
      // the backend can seed the profile.
      const fullName = [credential.fullName?.givenName, credential.fullName?.familyName]
        .filter(Boolean)
        .join(" ");
      const payload = await loginWithApple({
        identity_token: credential.identityToken,
        full_name: fullName || null
      });
      await useSessionStore.getState().setSession(payload.access_token, payload.user);
    } catch (err) {
      onPendingChange(false);
      const code = (err as { code?: string }).code;
      if (code !== "ERR_REQUEST_CANCELED") {
        onError(getErrorMessage(err, "Apple sign-in failed"));
      }
    } finally {
      signingIn.current = false;
    }
  };

  return (
    <AppleAuthentication.AppleAuthenticationButton
      buttonType={AppleAuthentication.AppleAuthenticationButtonType.SIGN_IN}
      buttonStyle={AppleAuthentication.AppleAuthenticationButtonStyle.WHITE}
      cornerRadius={10}
      style={{ width: "100%", height: 44 }}
      onPress={() => void signIn()}
    />
  );
}
