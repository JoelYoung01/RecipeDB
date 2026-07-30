import { colors } from "@/lib/colors";
import { useSessionStore } from "@/stores/session";
import { Redirect, Stack } from "expo-router";

export default function AuthLayout() {
  const status = useSessionStore((s) => s.status);
  if (status === "authed") return <Redirect href="/home" />;

  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background }
      }}
    />
  );
}
