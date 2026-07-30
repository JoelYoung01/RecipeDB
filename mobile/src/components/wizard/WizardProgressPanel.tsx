import { Text } from "@/components/ui/text";
import type { MealPlanWizardProgressEvent } from "@/types";
import { useEffect, useMemo, useRef } from "react";
import { ScrollView, View } from "react-native";

/** Live pipeline panel: progress bar, current message, scrolling event log. */
export function WizardProgressPanel({
  events,
  running,
  title,
  subtitle
}: {
  events: MealPlanWizardProgressEvent[];
  running: boolean;
  title: string;
  subtitle?: string;
}) {
  const logRef = useRef<ScrollView>(null);

  const progress = useMemo(() => {
    const last = [...events].reverse().find((e) => typeof e.progress === "number");
    return Math.max(0, Math.min(1, last?.progress ?? (running ? 0.05 : 0)));
  }, [events, running]);

  const pulseLabel = useMemo(() => {
    const last = events[events.length - 1];
    if (!last) return running ? "Warming up…" : "Waiting";
    return last.message;
  }, [events, running]);

  useEffect(() => {
    const t = setTimeout(() => logRef.current?.scrollToEnd({ animated: true }), 50);
    return () => clearTimeout(t);
  }, [events.length]);

  return (
    <View className="overflow-hidden rounded-2xl border border-border bg-card">
      <View className="px-4 pb-4 pt-5">
        <Text className="font-sans-bold text-[11px] uppercase tracking-[1px] text-success-soft">
          {running ? "Live" : "Pipeline"}
        </Text>
        <Text className="mt-1 font-sans-bold text-lg">{title}</Text>
        {subtitle ? <Text className="mt-1 text-sm text-muted-foreground">{subtitle}</Text> : null}

        <View className="mt-4 h-1.5 overflow-hidden rounded-full bg-secondary">
          <View
            className="h-full rounded-full bg-primary"
            style={{ width: `${progress * 100}%` }}
          />
        </View>

        <View className="mt-3 flex-row items-center gap-2">
          <View
            className={
              running ? "h-2.5 w-2.5 rounded-full bg-[#22c55e]" : "h-2.5 w-2.5 rounded-full bg-[#22c55e] opacity-40"
            }
          />
          <Text className="min-w-0 flex-1 font-sans-medium text-sm" numberOfLines={1}>
            {pulseLabel}
          </Text>
          <Text className="text-xs text-faint">{Math.round(progress * 100)}%</Text>
        </View>
      </View>

      <ScrollView
        ref={logRef}
        className="max-h-48 border-t border-border bg-elevated/80"
        contentContainerClassName="gap-2 px-4 py-3"
        nestedScrollEnabled
      >
        {events.map((event, i) => (
          <View key={`${event.stage}-${i}`} className="flex-row gap-2">
            <View
              className={
                event.status === "error"
                  ? "mt-1.5 h-1 w-1 rounded-full bg-destructive"
                  : event.status === "complete"
                    ? "mt-1.5 h-1 w-1 rounded-full bg-success-soft"
                    : "mt-1.5 h-1 w-1 rounded-full bg-muted-foreground"
              }
            />
            <Text
              className={
                event.status === "error"
                  ? "flex-1 text-[12.5px] leading-4 text-destructive"
                  : event.status === "complete"
                    ? "flex-1 text-[12.5px] leading-4 text-success-soft"
                    : "flex-1 text-[12.5px] leading-4 text-muted-foreground"
              }
            >
              {event.message}
            </Text>
          </View>
        ))}
        {!events.length ? (
          <Text className="text-sm text-faint">Waiting for the first signal…</Text>
        ) : null}
      </ScrollView>
    </View>
  );
}
