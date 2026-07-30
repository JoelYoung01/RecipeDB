import { cn } from "@/lib/cn";
import { colors } from "@/lib/colors";
import { Check } from "lucide-react-native";
import { Pressable } from "react-native";

export function Checkbox({
  checked,
  onCheckedChange,
  className
}: {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  className?: string;
}) {
  return (
    <Pressable
      accessibilityRole="checkbox"
      accessibilityState={{ checked }}
      hitSlop={8}
      onPress={() => onCheckedChange(!checked)}
      className={cn(
        "h-6 w-6 items-center justify-center rounded-md border",
        checked ? "border-primary bg-primary" : "border-border bg-secondary/40",
        className
      )}
    >
      {checked ? <Check size={15} color={colors.foreground} strokeWidth={3.5} /> : null}
    </Pressable>
  );
}
