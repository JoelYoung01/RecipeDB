import { cn } from "@/lib/cn";
import type { TextProps } from "react-native";
import { Text } from "./text";

export function Label({ className, ...props }: TextProps) {
  return <Text className={cn("font-sans-medium text-sm text-foreground", className)} {...props} />;
}
