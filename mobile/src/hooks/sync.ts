import { queryClient } from "@/lib/query-client";

/**
 * Cross-domain cache invalidation — mirrors the web app's src/stores/sync.ts.
 * The grocery window derives from planned meals; recipe edits ripple into
 * plans and grocery contents.
 */

export function syncAfterPlanMutation(options?: { recipesChanged?: boolean }) {
  void queryClient.invalidateQueries({ queryKey: ["plans"] });
  void queryClient.invalidateQueries({ queryKey: ["grocery"] });
  if (options?.recipesChanged) {
    void queryClient.invalidateQueries({ queryKey: ["recipes"] });
  }
}

export function syncAfterRecipeMutation() {
  void queryClient.invalidateQueries({ queryKey: ["recipes"] });
  void queryClient.invalidateQueries({ queryKey: ["plans"] });
  void queryClient.invalidateQueries({ queryKey: ["grocery"] });
}
