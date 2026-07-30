import { loginWithGoogle } from "@/api/auth";
import { getErrorMessage } from "@/api/errors";
import { Button } from "@/components/ui/button";
import { GOOGLE_IOS_CLIENT_ID, GOOGLE_WEB_CLIENT_ID } from "@/config";
import { colors } from "@/lib/colors";
import { useSessionStore } from "@/stores/session";
import * as Google from "expo-auth-session/providers/google";
import * as WebBrowser from "expo-web-browser";
import { LogIn } from "lucide-react-native";
import { useEffect, useRef } from "react";
import { Platform } from "react-native";

WebBrowser.maybeCompleteAuthSession();

/**
 * Native Google sign-in via expo-auth-session (system browser sheet).
 * Hidden when no client ID is configured for the current platform.
 * The resulting Google ID token is exchanged at POST /auth/login-google/.
 */
export function GoogleLoginButton({
  onPendingChange,
  onError
}: {
  onPendingChange: (pending: boolean) => void;
  onError: (message: string) => void;
}) {
  const [request, response, promptAsync] = Google.useIdTokenAuthRequest({
    iosClientId: GOOGLE_IOS_CLIENT_ID || undefined,
    webClientId: GOOGLE_WEB_CLIENT_ID || undefined,
    clientId: GOOGLE_WEB_CLIENT_ID || undefined
  });
  const exchanging = useRef(false);

  useEffect(() => {
    if (!response) return;
    if (response.type === "success") {
      const idToken = response.params.id_token;
      if (!idToken) {
        onPendingChange(false);
        onError("Google sign-in did not return a credential.");
        return;
      }
      if (exchanging.current) return;
      exchanging.current = true;
      loginWithGoogle({ credential: idToken })
        .then((payload) => useSessionStore.getState().setSession(payload.access_token, payload.user))
        .catch((err) => {
          onPendingChange(false);
          onError(getErrorMessage(err, "Google sign-in failed"));
        })
        .finally(() => {
          exchanging.current = false;
        });
    } else if (response.type === "error") {
      onPendingChange(false);
      onError(response.error?.message ?? "Google sign-in failed");
    } else if (response.type === "cancel" || response.type === "dismiss") {
      onPendingChange(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [response]);

  const available =
    Platform.OS === "web" ? Boolean(GOOGLE_WEB_CLIENT_ID) : Boolean(GOOGLE_IOS_CLIENT_ID);
  if (!available) return null;

  return (
    <Button
      variant="outline"
      className="h-11 w-full"
      disabled={!request}
      onPress={() => {
        onPendingChange(true);
        void promptAsync();
      }}
    >
      <LogIn size={16} color={colors.foreground} />
      Continue with Google
    </Button>
  );
}
