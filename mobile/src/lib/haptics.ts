import * as Haptics from "expo-haptics";
import { Platform } from "react-native";

/** Light impact for taps on primary chrome (no-op on web). */
export function tapHaptic() {
  if (Platform.OS === "web") return;
  void Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
}

/** Success notification for completed actions (no-op on web). */
export function successHaptic() {
  if (Platform.OS === "web") return;
  void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
}
