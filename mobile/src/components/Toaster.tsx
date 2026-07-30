import { colors } from "@/lib/colors";
import { useToastStore, type Toast } from "@/stores/toast";
import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react-native";
import { useEffect, useState } from "react";
import { Animated, Pressable, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Text } from "./ui/text";

const ICONS = {
  success: { Icon: CheckCircle2, color: colors.green400 },
  error: { Icon: XCircle, color: colors.destructive },
  warning: { Icon: AlertTriangle, color: colors.amber300 },
  info: { Icon: Info, color: colors.mutedForeground }
} as const;

function ToastRow({ toast }: { toast: Toast }) {
  const dismiss = useToastStore((s) => s.dismiss);
  const [opacity] = useState(() => new Animated.Value(0));
  const [translateY] = useState(() => new Animated.Value(8));

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, { toValue: 1, duration: 180, useNativeDriver: true }),
      Animated.spring(translateY, {
        toValue: 0,
        useNativeDriver: true,
        damping: 24,
        stiffness: 300
      })
    ]).start();
  }, [opacity, translateY]);

  const { Icon, color } = ICONS[toast.variant];

  return (
    <Animated.View style={{ opacity, transform: [{ translateY }] }}>
      <Pressable
        onPress={() => dismiss(toast.id)}
        className="mx-4 mt-2 flex-row items-center gap-3 rounded-lg border border-border bg-elevated px-4 py-3"
      >
        <Icon size={18} color={color} />
        <Text className="flex-1 text-sm leading-5">{toast.message}</Text>
      </Pressable>
    </Animated.View>
  );
}

/** Global toast overlay — rendered once above the app, under nothing. */
export function Toaster() {
  const toasts = useToastStore((s) => s.toasts);
  const insets = useSafeAreaInsets();

  if (!toasts.length) return null;

  return (
    <View
      pointerEvents="box-none"
      className="absolute inset-x-0 z-50"
      style={{ bottom: insets.bottom + 84 }}
    >
      {toasts.map((t) => (
        <ToastRow key={t.id} toast={t} />
      ))}
    </View>
  );
}
