import { addDays, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/dates";
import { tapHaptic } from "@/lib/haptics";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { Animated, Easing, PanResponder, Pressable, View } from "react-native";
import { Text } from "./ui/text";

const DAY_LABELS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
const SWIPE_THRESHOLD_RATIO = 0.22;
const SWIPE_VELOCITY = 0.4;
const SNAP_MS = 280;

/**
 * Swipeable 3-panel week selector (prev / current / next) with planned-day
 * dots — port of the web HomeWeekStrip.
 */
export function HomeWeekStrip({
  plannedKeys,
  onWeekChange,
  onSelectDay
}: {
  plannedKeys: Set<string>;
  /** Fired with the center week, plus a range covering prev/current/next for dots. */
  onWeekChange: (weekStart: Date, weekDays: Date[], rangeStart: Date, rangeEnd: Date) => void;
  onSelectDay: (date: Date) => void;
}) {
  const today = useMemo(() => startOfDay(), []);
  const thisWeekStart = useMemo(() => startOfWeekMonday(today), [today]);
  const todayKey = toDateKey(today);

  const [width, setWidth] = useState(0);
  const [weekOffset, setWeekOffset] = useState(0);
  const [translateX] = useState(() => new Animated.Value(0));
  const widthRef = useRef(0);
  const animatingRef = useRef(false);
  const dragStart = useRef(0);

  const daysForOffset = useCallback(
    (offset: number): Date[] => {
      const start = addDays(thisWeekStart, offset * 7);
      return Array.from({ length: 7 }, (_, i) => addDays(start, i));
    },
    [thisWeekStart]
  );

  const panels = useMemo(
    () => [
      { offset: weekOffset - 1, days: daysForOffset(weekOffset - 1) },
      { offset: weekOffset, days: daysForOffset(weekOffset) },
      { offset: weekOffset + 1, days: daysForOffset(weekOffset + 1) }
    ],
    [weekOffset, daysForOffset]
  );

  const weekLabel = useMemo(() => {
    if (weekOffset === 0) return "This week";
    if (weekOffset === -1) return "Last week";
    if (weekOffset === 1) return "Next week";
    const start = addDays(thisWeekStart, weekOffset * 7);
    const end = addDays(start, 6);
    const opts: Intl.DateTimeFormatOptions = { month: "short", day: "numeric" };
    return `${start.toLocaleDateString(undefined, opts)} – ${end.toLocaleDateString(undefined, opts)}`;
  }, [weekOffset, thisWeekStart]);

  // Notify parent of the visible week + prefetch range (prev/current/next).
  useEffect(() => {
    const start = addDays(thisWeekStart, weekOffset * 7);
    onWeekChange(start, daysForOffset(weekOffset), addDays(start, -7), addDays(start, 13));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weekOffset, thisWeekStart]);

  // Keep the track resting on the center panel whenever layout or week changes.
  useLayoutEffect(() => {
    widthRef.current = width;
    translateX.setValue(-width);
  }, [width, weekOffset, translateX]);

  const snapTo = useCallback(
    (delta: -1 | 0 | 1) => {
      const w = widthRef.current;
      if (!w) return;
      animatingRef.current = true;
      const target = delta === 0 ? -w : delta < 0 ? 0 : -w * 2;
      Animated.timing(translateX, {
        toValue: target,
        duration: SNAP_MS,
        easing: Easing.bezier(0.22, 1, 0.36, 1),
        useNativeDriver: true
      }).start(({ finished }) => {
        animatingRef.current = false;
        if (delta !== 0 && finished) {
          setWeekOffset((w0) => w0 + delta);
        } else {
          translateX.setValue(-widthRef.current);
        }
      });
    },
    [translateX]
  );
  const snapToRef = useRef(snapTo);
  useEffect(() => {
    snapToRef.current = snapTo;
  }, [snapTo]);

  // PanResponder.create only stores these callbacks; they run on gesture
  // events, never during render, so the refs rule is a false positive here.
  const panResponder = useMemo(
    () =>
      // eslint-disable-next-line react-hooks/refs
      PanResponder.create({
        onMoveShouldSetPanResponder: (_e, g) =>
          !animatingRef.current && Math.abs(g.dx) > 8 && Math.abs(g.dx) > Math.abs(g.dy),
        onPanResponderGrant: () => {
          dragStart.current = -widthRef.current;
        },
        onPanResponderMove: (_e, g) => {
          translateX.setValue(dragStart.current + g.dx);
        },
        onPanResponderRelease: (_e, g) => {
          const w = widthRef.current || 1;
          const commit =
            Math.abs(g.dx) >= w * SWIPE_THRESHOLD_RATIO || Math.abs(g.vx) >= SWIPE_VELOCITY;
          if (commit) snapToRef.current(g.dx < 0 ? 1 : -1);
          else snapToRef.current(0);
        },
        onPanResponderTerminate: () => snapToRef.current(0)
      }),
    [translateX]
  );

  const goToThisWeek = () => {
    if (weekOffset === 0) return;
    if (Math.abs(weekOffset) === 1) {
      snapTo(weekOffset > 0 ? -1 : 1);
    } else {
      setWeekOffset(0);
    }
  };

  return (
    <View>
      <View className="mb-2 flex-row items-center justify-between gap-2">
        <Text className="font-sans-semibold text-xs text-muted-foreground">{weekLabel}</Text>
        {weekOffset !== 0 ? (
          <Pressable onPress={goToThisWeek} hitSlop={8} className="active:opacity-70">
            <Text className="font-sans-semibold text-[11.5px] text-[#22c55e]">
              Jump to this week
            </Text>
          </Pressable>
        ) : (
          <Text className="text-[11px] text-faint">Swipe for more weeks</Text>
        )}
      </View>

      <View
        className="overflow-hidden"
        onLayout={(e) => setWidth(e.nativeEvent.layout.width)}
        {...panResponder.panHandlers}
      >
        <Animated.View
          style={{
            flexDirection: "row",
            width: width ? width * 3 : "300%",
            transform: [{ translateX }]
          }}
        >
          {panels.map((panel) => (
            <View
              key={panel.offset}
              style={{ width: width || undefined }}
              className="flex-row gap-1"
            >
              {panel.days.map((day, i) => {
                const key = toDateKey(day);
                const isToday = key === todayKey;
                return (
                  <Pressable
                    key={`${panel.offset}-${key}`}
                    accessibilityRole="button"
                    accessibilityLabel={day.toDateString()}
                    onPress={() => {
                      tapHaptic();
                      onSelectDay(day);
                    }}
                    className={
                      isToday
                        ? "flex-1 items-center rounded-lg border border-[#22c55e]/35 bg-[#22c55e]/10 px-0.5 py-1.5"
                        : "flex-1 items-center rounded-lg border border-transparent px-0.5 py-1.5"
                    }
                  >
                    <Text
                      className={
                        isToday
                          ? "font-sans-bold text-[10px] tracking-wide text-[#22c55e]"
                          : "font-sans-semibold text-[10px] tracking-wide text-faint"
                      }
                    >
                      {DAY_LABELS[i]}
                    </Text>
                    <Text
                      className={
                        isToday
                          ? "mt-0.5 font-sans-bold text-[13px] text-[#22c55e]"
                          : "mt-0.5 font-sans-bold text-[13px] text-foreground"
                      }
                    >
                      {day.getDate()}
                    </Text>
                    <View
                      className={
                        plannedKeys.has(key)
                          ? "mt-1.5 h-1.5 w-1.5 rounded-full bg-[#22c55e]"
                          : "mt-1.5 h-1.5 w-1.5 rounded-full bg-gap-dot"
                      }
                    />
                  </Pressable>
                );
              })}
            </View>
          ))}
        </Animated.View>
      </View>
    </View>
  );
}
