import { RecipeEditor } from "@/components/RecipeEditor";
import { useLocalSearchParams } from "expo-router";

export default function EditRecipeScreen() {
  const { recipeId } = useLocalSearchParams<{ recipeId: string }>();
  return <RecipeEditor recipeId={recipeId} />;
}
