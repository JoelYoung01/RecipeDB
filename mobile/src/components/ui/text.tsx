import { cn } from "@/lib/cn";
import { Text as RNText, type TextProps } from "react-native";

/**
 * Base text — Figtree regular, light foreground.
 * Use font-sans-medium / font-sans-semibold / font-sans-bold for weights
 * (iOS custom fonts need an explicit family per weight).
 */
export function Text({ className, ...props }: TextProps) {
  return <RNText className={cn("font-sans text-base text-foreground", className)} {...props} />;
}
