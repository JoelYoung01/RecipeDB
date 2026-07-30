import { colors } from "@/lib/colors";
import { tapHaptic } from "@/lib/haptics";
import { addMenuActions, type AddMenuAction, type AddMenuActionId } from "@/lib/sitemap";
import { useRouter } from "expo-router";
import {
  Camera,
  CalendarPlus,
  ChevronRight,
  Link2,
  PenLine,
  ShoppingCart,
  Sparkles
} from "lucide-react-native";
import { Pressable, View } from "react-native";
import { Sheet } from "./ui/sheet";
import { Text } from "./ui/text";

const ACTION_ICONS: Record<AddMenuActionId, typeof Link2> = {
  "import-link": Link2,
  "import-photo": Camera,
  "recipe-generate": Sparkles,
  "recipe-scratch": PenLine,
  "plan-meal": CalendarPlus,
  "shop-item": ShoppingCart
};

function ActionRow({ action, onPress }: { action: AddMenuAction; onPress: () => void }) {
  const Icon = ACTION_ICONS[action.id];
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      className={
        action.highlighted
          ? "flex-row items-center gap-3 rounded-lg border border-[#22c55e]/40 bg-[#22c55e]/10 px-3 py-3 active:opacity-80"
          : "flex-row items-center gap-3 rounded-lg px-3 py-3 active:bg-secondary/60"
      }
    >
      <View
        className={
          action.highlighted
            ? "h-10 w-10 items-center justify-center rounded-lg bg-primary"
            : "h-10 w-10 items-center justify-center rounded-lg bg-secondary"
        }
      >
        <Icon size={19} color={colors.foreground} strokeWidth={2} />
      </View>
      <View className="min-w-0 flex-1">
        <View className="flex-row items-center gap-2">
          <Text className="font-sans-medium text-sm">{action.title}</Text>
          {action.stub ? (
            <View className="rounded-full border border-border px-2 py-0.5">
              <Text className="text-[10px] text-muted-foreground">Soon</Text>
            </View>
          ) : null}
        </View>
        <Text className="mt-0.5 text-xs text-muted-foreground" numberOfLines={1}>
          {action.description}
        </Text>
      </View>
      <ChevronRight size={16} color={colors.faint} />
    </Pressable>
  );
}

/** Bottom "Add" menu opened from the raised + tab — mirrors web AddMenuSheet. */
export function AddMenuSheet({ visible, onClose }: { visible: boolean; onClose: () => void }) {
  const router = useRouter();

  const go = (action: AddMenuAction) => {
    tapHaptic();
    onClose();
    router.push(action.href as never);
  };

  const create = addMenuActions.filter((a) => a.group === "create");
  const quick = addMenuActions.filter((a) => a.group === "quick");

  return (
    <Sheet visible={visible} onClose={onClose}>
      <Text className="px-1 pb-1 text-xs uppercase tracking-wide text-faint">Create</Text>
      <View className="gap-1">
        {create.map((action) => (
          <ActionRow key={action.id} action={action} onPress={() => go(action)} />
        ))}
      </View>
      <Text className="mt-4 px-1 pb-1 text-xs uppercase tracking-wide text-faint">Quick</Text>
      <View className="gap-1">
        {quick.map((action) => (
          <ActionRow key={action.id} action={action} onPress={() => go(action)} />
        ))}
      </View>
    </Sheet>
  );
}
