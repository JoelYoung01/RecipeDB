import { API_ORIGIN } from "@/config";

export const DEFAULT_RECIPE_IMAGE = require("@/assets/images/default-recipe.jpg");

/**
 * Resolve recipe / upload image URLs for display.
 * The API returns relative `/uploads/...` paths; prefix them with the API origin.
 * Returns an expo-image compatible source.
 */
export function mediaSource(url?: string | null): number | { uri: string } {
  if (!url) return DEFAULT_RECIPE_IMAGE;
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) {
    return { uri: url };
  }
  return { uri: `${API_ORIGIN}${url.startsWith("/") ? "" : "/"}${url}` };
}
