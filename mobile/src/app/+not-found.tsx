import { Button } from "@/components/ui/button";
import { Text } from "@/components/ui/text";
import { Link, Stack } from "expo-router";
import { View } from "react-native";

export default function NotFoundScreen() {
  return (
    <>
      <Stack.Screen options={{ headerShown: false }} />
      <View className="flex-1 items-center justify-center bg-background px-8">
        <Text className="font-sans-bold text-2xl">Page not found</Text>
        <Text className="mt-2 text-center text-sm text-muted-foreground">
          That screen doesn&apos;t exist.
        </Text>
        <Link href="/home" asChild>
          <Button className="mt-6">Go home</Button>
        </Link>
      </View>
    </>
  );
}
