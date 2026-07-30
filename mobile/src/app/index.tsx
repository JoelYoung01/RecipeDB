import { useSessionStore } from "@/stores/session";
import { Redirect } from "expo-router";

export default function Index() {
  const status = useSessionStore((s) => s.status);
  return <Redirect href={status === "authed" ? "/home" : "/login"} />;
}
