import { cn } from "@/lib/cn";
import { colors } from "@/lib/colors";
import { forwardRef } from "react";
import { TextInput, type TextInputProps } from "react-native";

export const Textarea = forwardRef<TextInput, TextInputProps>(function Textarea(
  { className, ...props },
  ref
) {
  return (
    <TextInput
      ref={ref}
      multiline
      textAlignVertical="top"
      placeholderTextColor={colors.faint}
      keyboardAppearance="dark"
      selectionColor={colors.ring}
      className={cn(
        "min-h-[96px] w-full rounded-lg border border-input bg-card px-3 py-3 font-sans text-base leading-5 text-foreground",
        className
      )}
      {...props}
    />
  );
});
