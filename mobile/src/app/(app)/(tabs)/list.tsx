import { EmptyState } from "@/components/EmptyState";
import { SwipeRow } from "@/components/grocery/SwipeRow";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { Text } from "@/components/ui/text";
import { useGroceryList, useSetGroceryStatus } from "@/hooks/use-grocery";
import { colors } from "@/lib/colors";
import { formatShortRange } from "@/lib/dates";
import { getErrorMessage } from "@/api/errors";
import { paths } from "@/lib/sitemap";
import type { GroceryItem } from "@/types";
import { useRouter } from "expo-router";
import { EyeOff, ShoppingCart } from "lucide-react-native";
import { useMemo, useState } from "react";
import { Pressable, RefreshControl, ScrollView, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

export default function GroceryListScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [showDismissed, setShowDismissed] = useState(false);

  const list = useGroceryList();
  const setStatus = useSetGroceryStatus();

  const items = useMemo(() => list.data?.items ?? [], [list.data]);

  const visibleItems = useMemo(() => {
    if (showDismissed) return items.filter((i) => !i.deleted);
    return items.filter((i) => !i.dismissed && !i.deleted);
  }, [items, showDismissed]);

  const grouped = useMemo(() => {
    const map = new Map<string, GroceryItem[]>();
    for (const item of visibleItems) {
      const bucket = map.get(item.category) ?? [];
      bucket.push(item);
      map.set(item.category, bucket);
    }
    return Array.from(map.entries()).map(([category, categoryItems]) => ({
      category,
      items: categoryItems
    }));
  }, [visibleItems]);

  const activeCount = items.filter((i) => !i.dismissed && !i.deleted).length;
  const dismissedCount = items.filter((i) => i.dismissed && !i.deleted).length;

  const windowLabel = useMemo(() => {
    if (!list.data?.window_start || !list.data?.window_end) return "";
    return formatShortRange(new Date(list.data.window_start), new Date(list.data.window_end));
  }, [list.data]);

  const showSkeleton = list.isPending;

  function onCheck(item: GroceryItem, checked: boolean) {
    setStatus.mutate({ item, status: checked ? "dismissed" : null });
  }

  function onViewRecipe(item: GroceryItem) {
    const recipe = item.recipes[0];
    if (!recipe) return;
    router.push(paths.recipeDetail(recipe.id) as never);
  }

  return (
    <ScrollView
      className="flex-1 bg-background"
      contentContainerStyle={{
        paddingTop: insets.top + 20,
        paddingHorizontal: 16,
        paddingBottom: 24
      }}
      refreshControl={
        <RefreshControl
          refreshing={!list.isPending && list.isRefetching}
          onRefresh={() => void list.refetch()}
          tintColor={colors.mutedForeground}
        />
      }
    >
      <View className="flex-row items-start justify-between gap-3">
        <View className="min-w-0 flex-1">
          <Text className="font-sans-bold text-xl">Grocery</Text>
          <Text className="mt-1 text-sm text-muted-foreground">
            Ingredients for the next 7 days
            {windowLabel ? <Text className="text-sm text-faint"> · {windowLabel}</Text> : null}
          </Text>
        </View>
        <Button
          variant="outline"
          size="sm"
          className={showDismissed ? "border-[rgba(34,197,94,0.45)] bg-card" : "bg-card"}
          onPress={() => setShowDismissed((v) => !v)}
        >
          <EyeOff size={14} color={showDismissed ? colors.green400 : colors.foreground} />
          <Text
            className={
              showDismissed
                ? "font-sans-semibold text-xs text-[#4ade80]"
                : "font-sans-semibold text-xs"
            }
          >
            {showDismissed ? "Hide dismissed" : "Show dismissed"}
          </Text>
        </Button>
      </View>

      {!showSkeleton && dismissedCount > 0 && !showDismissed ? (
        <Text className="mt-2 text-xs text-faint">
          {dismissedCount} dismissed · {activeCount} remaining
        </Text>
      ) : null}

      {showSkeleton ? (
        <View className="mt-5 gap-5">
          {[0, 1, 2].map((section) => (
            <View key={section} className="gap-2">
              <Skeleton className="h-3 w-20" />
              <View className="gap-1.5">
                {[0, 1, 2].map((row) => (
                  <View
                    key={row}
                    className="flex-row items-start gap-3 rounded-xl border border-border bg-card px-3 py-3"
                  >
                    <Skeleton className="mt-0.5 h-4 w-4 rounded" />
                    <View className="min-w-0 flex-1 gap-2">
                      <View className="flex-row justify-between gap-2">
                        <Skeleton className="h-3.5 w-2/5" />
                        <Skeleton className="h-3 w-12" />
                      </View>
                      <Skeleton className="h-2.5 w-3/5" />
                    </View>
                  </View>
                ))}
              </View>
            </View>
          ))}
        </View>
      ) : list.isError ? (
        <View className="mt-8 items-center rounded-xl border border-border bg-card px-4 py-6">
          <Text className="text-center text-sm text-muted-foreground">
            {getErrorMessage(list.error, "Couldn’t load the grocery list.")}
          </Text>
          <Button size="sm" className="mt-4" onPress={() => void list.refetch()}>
            Retry
          </Button>
        </View>
      ) : visibleItems.length === 0 ? (
        <EmptyState
          className="mt-8"
          icon={
            <View className="h-12 w-12 items-center justify-center rounded-xl bg-[rgba(34,197,94,0.15)]">
              <ShoppingCart size={24} color={colors.green500} />
            </View>
          }
          title={items.length === 0 ? "Nothing to shop for" : "All caught up"}
          description={
            items.length === 0
              ? "Plan meals for the next week and ingredients will show up here automatically."
              : "Dismissed items are hidden."
          }
          action={
            items.length === 0 ? (
              <Button onPress={() => router.push(paths.planner as never)}>Open planner</Button>
            ) : (
              <Pressable accessibilityRole="button" onPress={() => setShowDismissed(true)}>
                <Text className="font-sans-semibold text-sm text-[#22c55e]">Show dismissed</Text>
              </Pressable>
            )
          }
        />
      ) : (
        <View className="mt-5 gap-5">
          {grouped.map((group) => (
            <View key={group.category} className="gap-2">
              <Text className="px-0.5 font-sans-bold text-[11px] uppercase tracking-[0.08em] text-faint">
                {group.category}
              </Text>
              <View className="gap-1.5">
                {group.items.map((item) => (
                  <SwipeRow
                    key={item.key}
                    onDismiss={() => setStatus.mutate({ item, status: "dismissed" })}
                    onDelete={() => setStatus.mutate({ item, status: "deleted" })}
                    onView={() => onViewRecipe(item)}
                  >
                    <View
                      className={
                        item.dismissed
                          ? "flex-row items-start gap-3 rounded-xl border border-border px-3 py-3 opacity-55"
                          : "flex-row items-start gap-3 rounded-xl border border-border px-3 py-3"
                      }
                    >
                      <Checkbox
                        className="mt-0.5 h-5 w-5"
                        checked={item.dismissed}
                        onCheckedChange={(v) => onCheck(item, v)}
                      />
                      <View className="min-w-0 flex-1">
                        <View className="flex-row items-baseline justify-between gap-2">
                          <Text
                            className={
                              item.dismissed
                                ? "flex-1 font-sans-semibold text-sm leading-snug text-muted-foreground line-through"
                                : "flex-1 font-sans-semibold text-sm leading-snug"
                            }
                          >
                            {item.name}
                          </Text>
                          {item.quantity_display ? (
                            <Text className="shrink-0 font-sans-medium text-xs text-[#86efac]">
                              {item.quantity_display}
                            </Text>
                          ) : null}
                        </View>
                        {item.recipe_titles ? (
                          <Text numberOfLines={1} className="mt-0.5 text-xs text-muted-foreground">
                            {item.recipe_titles}
                          </Text>
                        ) : null}
                      </View>
                    </View>
                  </SwipeRow>
                ))}
              </View>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}
