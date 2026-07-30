import type {
  GroceryItem,
  GroceryItemStatus,
  GroceryListResponse,
  GrocerySummaryResponse
} from "@/types";
import { get, put } from "./client";

export function fetchGroceryList(): Promise<GroceryListResponse> {
  return get<GroceryListResponse>("/grocery/");
}

export function fetchGrocerySummary(): Promise<GrocerySummaryResponse> {
  return get<GrocerySummaryResponse>("/grocery/summary/");
}

export function setGroceryItemStatus(
  itemKey: string,
  status: GroceryItemStatus
): Promise<GroceryItem> {
  return put<GroceryItem>("/grocery/state/", { item_key: itemKey, status });
}
