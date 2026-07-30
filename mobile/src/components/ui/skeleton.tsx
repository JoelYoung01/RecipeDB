import { cn } from "@/lib/cn";
import { useEffect, useState } from "react";
import { Animated, View } from "react-native";

/** Pulsing placeholder block (size/shape via className on the inner view). */
export function Skeleton({ className }: { className?: string }) {
  const [opacity] = useState(() => new Animated.Value(0.55));

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 700, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.55, duration: 700, useNativeDriver: true })
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [opacity]);

  return (
    <Animated.View style={{ opacity }}>
      <View className={cn("rounded-md bg-muted", className)} />
    </Animated.View>
  );
}
