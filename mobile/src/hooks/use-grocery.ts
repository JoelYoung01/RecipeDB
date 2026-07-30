import { fetchGroceryList, fetchGrocerySummary, setGroceryItemStatus } from "@/api/grocery";
import { queryClient } from "@/lib/query-client";
import { toast } from "@/stores/toast";
import type { GroceryItem, GroceryItemStatus, GroceryListResponse } from "@/types";
import { useMutation, useQuery } from "@tanstack/react-query";

const LIST_KEY = ["grocery", "list"] as const;

export function useGroceryList() {
  return useQuery({ queryKey: LIST_KEY, queryFn: fetchGroceryList });
}

export function useGrocerySummary() {
  return useQuery({
    queryKey: ["grocery", "summary"],
    queryFn: fetchGrocerySummary,
    select: (r) => r.active_count
  });
}

/** Optimistic dismiss/delete/restore of a grocery line. */
export function useSetGroceryStatus() {
  return useMutation({
    mutationFn: ({ item, status }: { item: GroceryItem; status: GroceryItemStatus }) =>
      setGroceryItemStatus(item.key, status),
    onMutate: async ({ item, status }) => {
      await queryClient.cancelQueries({ queryKey: LIST_KEY });
      const previous = queryClient.getQueryData<GroceryListResponse>(LIST_KEY);
      if (previous) {
        queryClient.setQueryData<GroceryListResponse>(LIST_KEY, {
          ...previous,
          items: previous.items.map((i) =>
            i.key === item.key
              ? { ...i, dismissed: status === "dismissed", deleted: status === "deleted" }
              : i
          )
        });
      }
      return { previous };
    },
    onError: (error, _vars, context) => {
      if (context?.previous) queryClient.setQueryData(LIST_KEY, context.previous);
      toast.fromError(error, "Could not update the item.");
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["grocery", "summary"] });
    }
  });
}
