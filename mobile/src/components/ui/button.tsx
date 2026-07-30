import { cn } from "@/lib/cn";
import { tapHaptic } from "@/lib/haptics";
import { cva, type VariantProps } from "class-variance-authority";
import { Children, type ReactNode } from "react";
import { Pressable, type GestureResponderEvent, type PressableProps } from "react-native";
import { Text } from "./text";

const buttonVariants = cva("flex-row items-center justify-center gap-2 rounded-lg", {
  variants: {
    variant: {
      default: "bg-primary",
      secondary: "bg-secondary",
      outline: "border border-border bg-transparent",
      ghost: "bg-transparent",
      destructive: "bg-destructive"
    },
    size: {
      default: "h-11 px-4",
      sm: "h-9 px-3",
      lg: "h-12 px-5",
      icon: "h-11 w-11",
      "icon-sm": "h-9 w-9"
    }
  },
  defaultVariants: { variant: "default", size: "default" }
});

const buttonTextVariants = cva("font-sans-semibold text-sm", {
  variants: {
    variant: {
      default: "text-primary-foreground",
      secondary: "text-secondary-foreground",
      outline: "text-foreground",
      ghost: "text-foreground",
      destructive: "text-foreground"
    }
  },
  defaultVariants: { variant: "default" }
});

export type ButtonProps = Omit<PressableProps, "children"> &
  VariantProps<typeof buttonVariants> & {
    className?: string;
    textClassName?: string;
    children?: ReactNode;
    haptic?: boolean;
  };

export function Button({
  variant,
  size,
  className,
  textClassName,
  children,
  disabled,
  onPress,
  haptic = true,
  ...props
}: ButtonProps) {
  const handlePress = (event: GestureResponderEvent) => {
    if (haptic) tapHaptic();
    onPress?.(event);
  };

  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      onPress={handlePress}
      className={cn(
        buttonVariants({ variant, size }),
        disabled && "opacity-50",
        "active:opacity-80",
        className
      )}
      {...props}
    >
      {Children.map(children, (child) =>
        typeof child === "string" || typeof child === "number" ? (
          <Text className={cn(buttonTextVariants({ variant }), textClassName)}>{child}</Text>
        ) : (
          child
        )
      )}
    </Pressable>
  );
}
