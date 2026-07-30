import { cn } from "@/lib/cn";
import { colors } from "@/lib/colors";
import { forwardRef } from "react";
import { TextInput, type TextInputProps } from "react-native";

export const Input = forwardRef<TextInput, TextInputProps>(function Input(
  { className, ...props },
  ref
) {
  return (
    <TextInput
      ref={ref}
      placeholderTextColor={colors.faint}
      keyboardAppearance="dark"
      selectionColor={colors.ring}
      className={cn(
        "h-12 w-full rounded-lg border border-input bg-card px-3 font-sans text-base leading-5 text-foreground",
        className
      )}
      {...props}
    />
  );
});
