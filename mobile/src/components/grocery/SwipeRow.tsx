import { Text } from "@/components/ui/text";
import { colors } from "@/lib/colors";
import { Eye, Trash2 } from "lucide-react-native";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Animated, PanResponder, Pressable, View } from "react-native";

const ACTION_WIDTH = 128;
const DISMISS_THRESHOLD = 72;
const OPEN_THRESHOLD = 40;
const MAX_RIGHT = 180;

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

/**
 * Swipeable grocery row, mirrors the web app's SwipeRow: drag right past the
 * threshold to dismiss, drag left to reveal view/delete actions, tap the row
 * while the tray is open to close it again.
 */
export function SwipeRow({
  children,
  onDismiss,
  onDelete,
  onView
}: {
  children: ReactNode;
  onDismiss: () => void;
  onDelete: () => void;
  onView: () => void;
}) {
  const [offset] = useState(() => new Animated.Value(0));
  const settledOffset = useRef(0);
  const [open, setOpen] = useState(false);
  const openRef = useRef(false);

  // The PanResponder is created once, so route prop callbacks through a ref
  // to always invoke the latest handlers.
  const actions = useRef({ onDismiss, onDelete, onView });
  useEffect(() => {
    actions.current = { onDismiss, onDelete, onView };
  }, [onDismiss, onDelete, onView]);

  const setOpenState = (value: boolean) => {
    openRef.current = value;
    setOpen(value);
  };

  const settleTo = (value: number) => {
    settledOffset.current = value;
    Animated.timing(offset, { toValue: value, duration: 180, useNativeDriver: true }).start();
  };

  const close = () => {
    setOpenState(false);
    settleTo(0);
  };

  // PanResponder.create only stores these callbacks; they run on gesture
  // events, never during render, so the refs rule is a false positive here.
  // eslint-disable-next-line react-hooks/refs
  const [panResponder] = useState(() =>
    PanResponder.create({
      onMoveShouldSetPanResponder: (_e, g) =>
        Math.abs(g.dx) > 8 && Math.abs(g.dx) > Math.abs(g.dy) * 1.4,
      onPanResponderMove: (_e, g) => {
        offset.setValue(clamp(settledOffset.current + g.dx, -ACTION_WIDTH, MAX_RIGHT));
      },
      onPanResponderRelease: (_e, g) => {
        const finalOffset = clamp(settledOffset.current + g.dx, -ACTION_WIDTH, MAX_RIGHT);
        const settle = (value: number) => {
          openRef.current = value !== 0;
          setOpen(value !== 0);
          settledOffset.current = value;
          Animated.timing(offset, { toValue: value, duration: 180, useNativeDriver: true }).start();
        };
        if (finalOffset >= DISMISS_THRESHOLD) {
          settle(0);
          actions.current.onDismiss();
        } else if (finalOffset <= -OPEN_THRESHOLD) {
          settle(-ACTION_WIDTH);
        } else {
          settle(0);
        }
      },
      onPanResponderTerminate: () => {
        const value = openRef.current ? -ACTION_WIDTH : 0;
        settledOffset.current = value;
        Animated.timing(offset, { toValue: value, duration: 180, useNativeDriver: true }).start();
      }
    })
  );

  return (
    <View className="relative overflow-hidden rounded-xl">
      {/* Dismiss backdrop, revealed while dragging right */}
      <View className="absolute inset-y-0 left-0 w-28 justify-center bg-[rgba(34,197,94,0.22)] pl-4">
        <Text className="font-sans-semibold text-xs text-[#4ade80]">Dismiss</Text>
      </View>

      {/* Action tray, revealed while dragging left */}
      <View className="absolute inset-y-0 right-0 w-32 flex-row">
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="View recipe"
          onPress={() => {
            close();
            onView();
          }}
          className="flex-1 items-center justify-center bg-[#3f463f] active:opacity-80"
        >
          <Eye size={20} color={colors.foreground} strokeWidth={2} />
        </Pressable>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Remove from list"
          onPress={() => {
            close();
            onDelete();
          }}
          className="flex-1 items-center justify-center bg-[#dc2626] active:opacity-80"
        >
          <Trash2 size={20} color={colors.foreground} strokeWidth={2} />
        </Pressable>
      </View>

      <Animated.View
        {...panResponder.panHandlers}
        style={{ transform: [{ translateX: offset }] }}
        className="bg-card"
      >
        <Pressable disabled={!open} onPress={close} accessibilityLabel="Close actions">
          {children}
        </Pressable>
      </Animated.View>
    </View>
  );
}
