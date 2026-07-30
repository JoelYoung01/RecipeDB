import { cn } from "@/lib/cn";
import type { ReactNode } from "react";
import { View } from "react-native";
import { Text } from "./ui/text";

export function EmptyState({
  icon,
  title,
  description,
  action,
  className
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <View
      className={cn(
        "items-center rounded-xl border border-border bg-card/50 px-6 py-10",
        className
      )}
    >
      {icon ? <View className="mb-3">{icon}</View> : null}
      <Text className="text-center font-sans-semibold text-base">{title}</Text>
      {description ? (
        <Text className="mt-1 text-center text-sm leading-5 text-muted-foreground">
          {description}
        </Text>
      ) : null}
      {action ? <View className="mt-4">{action}</View> : null}
    </View>
  );
}
