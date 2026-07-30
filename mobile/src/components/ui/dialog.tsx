import type { ReactNode } from "react";
import { Modal, Pressable, View } from "react-native";
import { Button } from "./button";
import { Text } from "./text";

/** Centered confirmation dialog over a scrim. */
export function ConfirmDialog({
  visible,
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  destructive = false,
  loading = false,
  onConfirm,
  onCancel,
  children
}: {
  visible: boolean;
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  loading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  children?: ReactNode;
}) {
  return (
    <Modal transparent visible={visible} animationType="fade" onRequestClose={onCancel}>
      <View className="flex-1 items-center justify-center bg-black/60 px-6">
        <Pressable className="absolute inset-0" onPress={onCancel} accessibilityLabel="Close" />
        <View className="w-full max-w-sm rounded-xl border border-border bg-card p-5">
          <Text className="font-sans-semibold text-lg">{title}</Text>
          {description ? (
            <Text className="mt-2 text-sm leading-5 text-muted-foreground">{description}</Text>
          ) : null}
          {children}
          <View className="mt-5 flex-row justify-end gap-3">
            <Button variant="outline" size="sm" onPress={onCancel} disabled={loading}>
              {cancelLabel}
            </Button>
            <Button
              variant={destructive ? "destructive" : "default"}
              size="sm"
              onPress={onConfirm}
              disabled={loading}
            >
              {loading ? "Working…" : confirmLabel}
            </Button>
          </View>
        </View>
      </View>
    </Modal>
  );
}
