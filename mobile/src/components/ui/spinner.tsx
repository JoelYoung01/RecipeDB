import { colors } from "@/lib/colors";
import { ActivityIndicator, type ActivityIndicatorProps } from "react-native";

export function Spinner(props: ActivityIndicatorProps) {
  return <ActivityIndicator color={colors.mutedForeground} {...props} />;
}
