import { Text } from "@/components/ui/text";
import { colors } from "@/lib/colors";
import { Eye, Trash2 } from "lucide-react-native";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { Animated, PanResponder, Pressable, View } from "react-native";

const DEFAULT_ACTION_WIDTH = 128;
const DISMISS_THRESHOLD = 72;
const OPEN_THRESHOLD = 40;
const MAX_RIGHT = 180;

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

/**
 * Swipeable list row (grocery + planner). Drag right past the threshold to
 * fire onDismiss (when enabled), drag left to reveal action buttons.
 */
export function SwipeRow({
  children,
  onDismiss,
  onDelete,
  onView,
  actionWidth = DEFAULT_ACTION_WIDTH,
  canSwipeRight = true,
  dismissLabel = "Dismiss",
  deleteLabel = "Remove from list"
}: {
  children: ReactNode;
  onDismiss?: () => void;
  onDelete: () => void;
  onView?: () => void;
  actionWidth?: number;
  canSwipeRight?: boolean;
  dismissLabel?: string;
  deleteLabel?: string;
}) {
  const allowRight = Boolean(canSwipeRight && onDismiss);
  const trayWidth = onView ? actionWidth : Math.min(actionWidth, 72);
  const [offset] = useState(() => new Animated.Value(0));
  const settledOffset = useRef(0);
  const [open, setOpen] = useState(false);
  const openRef = useRef(false);

  const actions = useRef({ onDismiss, onDelete, onView, allowRight, trayWidth });
  useEffect(() => {
    actions.current = { onDismiss, onDelete, onView, allowRight, trayWidth };
  }, [onDismiss, onDelete, onView, allowRight, trayWidth]);

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

  // eslint-disable-next-line react-hooks/refs
  const [panResponder] = useState(() =>
    PanResponder.create({
      onMoveShouldSetPanResponder: (_e, g) =>
        Math.abs(g.dx) > 8 && Math.abs(g.dx) > Math.abs(g.dy) * 1.4,
      onPanResponderMove: (_e, g) => {
        const { allowRight: right, trayWidth: tray } = actions.current;
        offset.setValue(clamp(settledOffset.current + g.dx, -tray, right ? MAX_RIGHT : 0));
      },
      onPanResponderRelease: (_e, g) => {
        const { allowRight: right, trayWidth: tray, onDismiss: dismiss } = actions.current;
        const finalOffset = clamp(settledOffset.current + g.dx, -tray, right ? MAX_RIGHT : 0);
        const settle = (value: number) => {
          openRef.current = value !== 0;
          setOpen(value !== 0);
          settledOffset.current = value;
          Animated.timing(offset, { toValue: value, duration: 180, useNativeDriver: true }).start();
        };
        if (right && finalOffset >= DISMISS_THRESHOLD) {
          settle(0);
          dismiss?.();
        } else if (finalOffset <= -OPEN_THRESHOLD) {
          settle(-tray);
        } else {
          settle(0);
        }
      },
      onPanResponderTerminate: () => {
        const tray = actions.current.trayWidth;
        const value = openRef.current ? -tray : 0;
        settledOffset.current = value;
        Animated.timing(offset, { toValue: value, duration: 180, useNativeDriver: true }).start();
      }
    })
  );

  return (
    <View className="relative overflow-hidden">
      {allowRight ? (
        <View className="absolute inset-y-0 left-0 w-28 justify-center bg-[rgba(34,197,94,0.22)] pl-4">
          <Text className="font-sans-semibold text-xs text-[#4ade80]">{dismissLabel}</Text>
        </View>
      ) : null}

      <View className="absolute inset-y-0 right-0 flex-row" style={{ width: trayWidth }}>
        {onView ? (
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
        ) : null}
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={deleteLabel}
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
