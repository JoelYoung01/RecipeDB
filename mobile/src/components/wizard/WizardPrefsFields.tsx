import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Text } from "@/components/ui/text";
import { Textarea } from "@/components/ui/textarea";
import type { MealPlanWizardPrefs } from "@/types";
import { Pressable, View } from "react-native";

const GOAL_CHIPS = [
  "High protein",
  "Balanced macros",
  "Calorie deficit",
  "Low carb",
  "Budget friendly",
  "Quick weeknights"
];

const DIET_CHIPS = ["Vegetarian", "Gluten-free", "Dairy-free", "Nut-free", "Halal", "No pork"];

function parseNumeric(value: string): number | null {
  const digits = value.replace(/[^0-9]/g, "");
  if (!digits) return null;
  const n = Number(digits);
  return Number.isFinite(n) ? n : null;
}

/** Wizard preference editor — chips + free text, port of WizardPrefsFields.vue. */
export function WizardPrefsFields({
  prefs,
  onChange
}: {
  prefs: MealPlanWizardPrefs;
  onChange: (next: MealPlanWizardPrefs) => void;
}) {
  const chipActive = (field: "goals" | "dietary_restrictions", chip: string) =>
    (prefs[field] || "")
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .includes(chip.toLowerCase());

  const toggleChip = (field: "goals" | "dietary_restrictions", chip: string) => {
    const parts = (prefs[field] || "")
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    const exists = parts.some((p) => p.toLowerCase() === chip.toLowerCase());
    const next = exists
      ? parts.filter((p) => p.toLowerCase() !== chip.toLowerCase())
      : [...parts, chip];
    onChange({ ...prefs, [field]: next.join(", ") });
  };

  const renderChips = (field: "goals" | "dietary_restrictions", chips: string[]) => (
    <View className="mt-2 flex-row flex-wrap gap-1.5">
      {chips.map((chip) => {
        const active = chipActive(field, chip);
        return (
          <Pressable
            key={chip}
            accessibilityRole="button"
            accessibilityState={{ selected: active }}
            onPress={() => toggleChip(field, chip)}
            className={
              active
                ? "rounded-full border border-[#22c55e]/45 bg-[#22c55e]/15 px-2.5 py-1"
                : "rounded-full border border-border bg-secondary/50 px-2.5 py-1"
            }
          >
            <Text
              className={
                active
                  ? "font-sans-medium text-[11.5px] text-success-soft"
                  : "font-sans-medium text-[11.5px] text-muted-foreground"
              }
            >
              {chip}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );

  return (
    <View className="gap-5">
      <View>
        <Label className="font-sans-semibold text-sm">Goals</Label>
        <Text className="mt-0.5 text-xs text-muted-foreground">
          Optional — what should this week optimize for?
        </Text>
        {renderChips("goals", GOAL_CHIPS)}
        <Textarea
          className="mt-2 min-h-16"
          placeholder="e.g. high protein, balanced macros, calorie deficit…"
          value={prefs.goals}
          onChangeText={(v) => onChange({ ...prefs, goals: v })}
        />
      </View>

      <View>
        <Label className="font-sans-semibold text-sm">Dietary restrictions</Label>
        <Text className="mt-0.5 text-xs text-muted-foreground">
          Optional — allergies, religions, preferences
        </Text>
        {renderChips("dietary_restrictions", DIET_CHIPS)}
        <Textarea
          className="mt-2 min-h-16"
          placeholder="e.g. vegetarian, gluten-free, no shellfish…"
          value={prefs.dietary_restrictions}
          onChangeText={(v) => onChange({ ...prefs, dietary_restrictions: v })}
        />
      </View>

      <View>
        <Label className="font-sans-semibold text-sm">Preferred ingredients</Label>
        <Text className="mt-0.5 text-xs text-muted-foreground">
          Optional — what’s already in the fridge?
        </Text>
        <Textarea
          className="mt-2 min-h-16"
          placeholder="e.g. chicken thighs, broccoli, rice, tortillas…"
          value={prefs.preferred_ingredients}
          onChangeText={(v) => onChange({ ...prefs, preferred_ingredients: v })}
        />
      </View>

      <View className="flex-row gap-3">
        <View className="flex-1">
          <Label className="font-sans-semibold text-sm">Max cook time</Label>
          <Input
            className="mt-2"
            keyboardType="number-pad"
            placeholder="minutes"
            value={prefs.max_cook_minutes === null ? "" : String(prefs.max_cook_minutes)}
            onChangeText={(v) => onChange({ ...prefs, max_cook_minutes: parseNumeric(v) })}
          />
        </View>
        <View className="flex-1">
          <Label className="font-sans-semibold text-sm">Servings</Label>
          <Input
            className="mt-2"
            keyboardType="number-pad"
            placeholder="people"
            value={prefs.servings === null ? "" : String(prefs.servings)}
            onChangeText={(v) => onChange({ ...prefs, servings: parseNumeric(v) })}
          />
        </View>
      </View>

      <View>
        <Label className="font-sans-semibold text-sm">Cuisine notes</Label>
        <Input
          className="mt-2"
          placeholder="e.g. Mexican, Mediterranean, cozy comfort…"
          value={prefs.cuisine_notes}
          onChangeText={(v) => onChange({ ...prefs, cuisine_notes: v })}
        />
      </View>

      <View>
        <Label className="font-sans-semibold text-sm">Anything else?</Label>
        <Textarea
          className="mt-2 min-h-16"
          placeholder="Kids hate mushrooms, avoid repeats from last week…"
          value={prefs.extra_notes}
          onChangeText={(v) => onChange({ ...prefs, extra_notes: v })}
        />
      </View>
    </View>
  );
}
