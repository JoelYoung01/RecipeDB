import { AddMenuSheet } from "@/components/AddMenuSheet";
import { AppTabBar } from "@/components/AppTabBar";
import { colors } from "@/lib/colors";
import { Tabs } from "expo-router";
import { useState } from "react";

export default function TabsLayout() {
  const [addOpen, setAddOpen] = useState(false);

  return (
    <>
      <Tabs
        tabBar={(props) => (
          <AppTabBar {...props} addOpen={addOpen} onAddPress={() => setAddOpen((v) => !v)} />
        )}
        screenOptions={{
          headerShown: false,
          sceneStyle: { backgroundColor: colors.background }
        }}
      >
        <Tabs.Screen name="home" options={{ title: "Home" }} />
        <Tabs.Screen name="recipes" options={{ title: "Recipes" }} />
        <Tabs.Screen name="planner" options={{ title: "Planner" }} />
        <Tabs.Screen name="list" options={{ title: "Grocery" }} />
      </Tabs>
      <AddMenuSheet visible={addOpen} onClose={() => setAddOpen(false)} />
    </>
  );
}
