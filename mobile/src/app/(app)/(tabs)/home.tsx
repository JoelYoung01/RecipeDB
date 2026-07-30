import { HomeWeekStrip } from "@/components/HomeWeekStrip";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Text } from "@/components/ui/text";
import { colors } from "@/lib/colors";
import { addDays, formatPrepTime, startOfDay, startOfWeekMonday, toDateKey } from "@/lib/dates";
import { tapHaptic } from "@/lib/haptics";
import { mediaSource } from "@/lib/media";
import { planDayKey, usePlansRange } from "@/hooks/use-planner";
import { useGrocerySummary } from "@/hooks/use-grocery";
import { useRecipeCount } from "@/hooks/use-recipes";
import { useSessionStore } from "@/stores/session";
import { toast } from "@/stores/toast";
import { Image } from "expo-image";
import { LinearGradient } from "expo-linear-gradient";
import { useRouter } from "expo-router";
import { Plus, Search, ShoppingCart, User } from "lucide-react-native";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Pressable, ScrollView, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

export default function HomeScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const user = useSessionStore((s) => s.user);

  const today = useMemo(() => startOfDay(), []);
  const thisWeekStart = useMemo(() => startOfWeekMonday(today), [today]);

  const [visibleDays, setVisibleDays] = useState<Date[]>(() =>
    Array.from({ length: 7 }, (_, i) => addDays(thisWeekStart, i))
  );
  const [range, setRange] = useState(() => ({
    start: addDays(thisWeekStart, -7),
    end: addDays(thisWeekStart, 13)
  }));

  const plansQuery = usePlansRange(range.start, range.end);
  const recipeCount = useRecipeCount();
  const groceryCount = useGrocerySummary();

  useEffect(() => {
    if (plansQuery.isError) toast.fromError(plansQuery.error, "Couldn’t load this week’s plan.");
  }, [plansQuery.isError, plansQuery.error]);

  const plans = useMemo(() => plansQuery.data ?? [], [plansQuery.data]);
  const plannedKeys = useMemo(() => new Set(plans.map(planDayKey)), [plans]);
  const plannedCount = visibleDays.filter((d) => plannedKeys.has(toDateKey(d))).length;
  const gapDays = visibleDays.filter((d) => !plannedKeys.has(toDateKey(d)));

  const todayKey = toDateKey(today);
  const tonight = plans.find((p) => p.planned_for.startsWith(todayKey)) ?? null;
  const tonightMeta = tonight ? formatPrepTime(tonight.recipe.prep_time) || "Tonight’s plan" : "";
  const showHeroSkeleton = plansQuery.isPending && !tonight;

  const weekdayName = today.toLocaleDateString(undefined, { weekday: "long" });

  const onWeekChange = useCallback((_start: Date, days: Date[], rangeStart: Date, rangeEnd: Date) => {
    setVisibleDays(days);
    setRange({ start: rangeStart, end: rangeEnd });
  }, []);

  const openDay = useCallback(
    (date: Date) => {
      router.push(`/planner?date=${toDateKey(date)}` as never);
    },
    [router]
  );

  const openFillGaps = () => {
    tapHaptic();
    router.push(`/planner/fill?days=${gapDays.map(toDateKey).join(",")}` as never);
  };

  const cookTonight = () => {
    if (!tonight) {
      router.push("/planner");
      return;
    }
    router.push(`/recipes/${tonight.recipe.id}` as never);
  };

  return (
    <ScrollView className="flex-1 bg-background" contentContainerClassName="pb-6">
      {/* Tonight hero */}
      <View className="h-[300px] overflow-hidden">
        {tonight ? (
          <Image
            source={mediaSource(tonight.recipe.cover_image?.url)}
            style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}
            contentFit="cover"
            transition={200}
          />
        ) : (
          <View className="absolute inset-0 bg-[#1d201d]" />
        )}
        <LinearGradient
          colors={["rgba(9,11,9,0.5)", "rgba(9,11,9,0)", "rgba(9,11,9,0.95)"]}
          locations={[0, 0.45, 1]}
          style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}
        />

        <View
          className="flex-row items-center justify-between px-5"
          style={{ paddingTop: insets.top + 8 }}
        >
          <Text className="font-sans-bold text-base tracking-tight">{weekdayName}</Text>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Account"
            onPress={() => {
              tapHaptic();
              router.push("/account");
            }}
            className="h-[34px] w-[34px] items-center justify-center overflow-hidden rounded-full bg-foreground/15 active:opacity-80"
          >
            {user?.avatar_url ? (
              <Image source={{ uri: user.avatar_url }} style={{ width: 34, height: 34 }} />
            ) : (
              <User size={16} color={colors.foreground} strokeWidth={2} />
            )}
          </Pressable>
        </View>

        <View className="absolute inset-x-0 bottom-0 flex-row items-end justify-between gap-3 px-5 pb-4">
          <View className="min-w-0 flex-1">
            <Text className="font-sans-bold text-[11px] tracking-[1px] text-success-soft">
              TONIGHT
            </Text>
            {tonight ? (
              <>
                <Text className="mt-0.5 font-sans-bold text-xl leading-tight tracking-tight">
                  {tonight.recipe.name}
                </Text>
                <Text className="mt-0.5 text-xs text-foreground/75">{tonightMeta}</Text>
              </>
            ) : showHeroSkeleton ? (
              <>
                <Skeleton className="mt-1.5 h-6 w-40 bg-foreground/20" />
                <Skeleton className="mt-2 h-3 w-28 bg-foreground/15" />
              </>
            ) : (
              <>
                <Text className="mt-0.5 font-sans-bold text-xl leading-tight tracking-tight">
                  Nothing planned
                </Text>
                <Text className="mt-0.5 text-xs text-foreground/75">
                  Pick something for tonight
                </Text>
              </>
            )}
          </View>
          <Button
            className="shrink-0 rounded-[11px] px-5"
            textClassName="text-[13px]"
            onPress={cookTonight}
          >
            {tonight ? "Cook" : "Plan"}
          </Button>
        </View>
      </View>

      {/* Week strip */}
      <View className="px-5 pt-4">
        <HomeWeekStrip
          plannedKeys={plannedKeys}
          onWeekChange={onWeekChange}
          onSelectDay={openDay}
        />
        <View className="mt-2 flex-row items-center justify-between">
          <Text className="text-xs text-muted-foreground">
            {plannedCount} of 7 dinners planned
          </Text>
          <Pressable onPress={openFillGaps} hitSlop={8} className="active:opacity-70">
            <Text className="font-sans-semibold text-[12.5px] text-[#22c55e]">
              Fill the gaps →
            </Text>
          </Pressable>
        </View>
      </View>

      {/* Action rows */}
      <View className="gap-2 px-5 pt-4">
        <Pressable
          accessibilityRole="button"
          onPress={() => {
            tapHaptic();
            router.push("/recipes/import?method=link" as never);
          }}
          className="flex-row items-center gap-3 rounded-xl border border-border bg-card px-4 py-3.5 active:opacity-80"
        >
          <Plus size={18} color="rgba(34,197,94,0.55)" strokeWidth={2} />
          <Text className="flex-1 font-sans-semibold text-sm">Import a recipe</Text>
          <Text className="text-[11.5px] text-faint">link · photo · manual</Text>
        </Pressable>

        <Pressable
          accessibilityRole="button"
          onPress={() => {
            tapHaptic();
            router.push("/recipes");
          }}
          className="flex-row items-center gap-3 rounded-xl border border-border bg-card px-4 py-3.5 active:opacity-80"
        >
          <Search size={18} color="rgba(34,197,94,0.55)" strokeWidth={2} />
          <Text className="flex-1 font-sans-semibold text-sm">Find a recipe</Text>
          {recipeCount.data === undefined ? (
            <Skeleton className="h-3 w-10" />
          ) : (
            <Text className="text-[11.5px] text-faint">{recipeCount.data} saved</Text>
          )}
        </Pressable>

        <Pressable
          accessibilityRole="button"
          onPress={() => {
            tapHaptic();
            router.push("/list");
          }}
          className="flex-row items-center gap-3 rounded-xl border border-border bg-card px-4 py-3.5 active:opacity-80"
        >
          <ShoppingCart size={18} color="rgba(34,197,94,0.55)" strokeWidth={2} />
          <Text className="flex-1 font-sans-semibold text-sm">Grocery</Text>
          <View className="rounded-full border border-[#22c55e]/35 bg-[#22c55e]/10 px-2 py-0.5">
            <Text className="font-sans-bold text-[11px] text-[#4ade80]">
              {groceryCount.data === undefined ? "·" : groceryCount.data}
            </Text>
          </View>
        </Pressable>
      </View>
    </ScrollView>
  );
}
