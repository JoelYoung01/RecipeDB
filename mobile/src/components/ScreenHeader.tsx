import { colors } from "@/lib/colors";
import { tapHaptic } from "@/lib/haptics";
import { useRouter } from "expo-router";
import { ChevronLeft } from "lucide-react-native";
import type { ReactNode } from "react";
import { Pressable, View } from "react-native";
import { Text } from "./ui/text";

/** Stack-screen header: back chevron, centered title, optional right slot. */
export function ScreenHeader({
  title,
  right,
  onBack
}: {
  title: string;
  right?: ReactNode;
  onBack?: () => void;
}) {
  const router = useRouter();

  const goBack = () => {
    tapHaptic();
    if (onBack) return onBack();
    if (router.canGoBack()) router.back();
    else router.replace("/home");
  };

  return (
    <View className="flex-row items-center justify-between px-2 py-2">
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Back"
        onPress={goBack}
        hitSlop={8}
        className="h-10 w-10 items-center justify-center rounded-lg active:opacity-70"
      >
        <ChevronLeft size={24} color={colors.foreground} />
      </Pressable>
      <Text className="flex-1 text-center font-sans-semibold text-base" numberOfLines={1}>
        {title}
      </Text>
      <View className="h-10 w-10 items-center justify-center">{right}</View>
    </View>
  );
}
